"""Rotas de varredura: execução, consulta, relatório e exportação."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, PlainTextResponse

from acessisaude_audit.api.deps import get_catalog, get_repository, get_settings_dep
from acessisaude_audit.api.schemas import Page, ScanRequest, ScanSummary
from acessisaude_audit.auditor.engine import AuditEngine
from acessisaude_audit.catalog.loader import Target, TargetCatalog
from acessisaude_audit.config import Settings
from acessisaude_audit.domain.models import ScanResult
from acessisaude_audit.domain.scoring import score_scan, summarize_by_group
from acessisaude_audit.logging_setup import get_logger
from acessisaude_audit.persistence.database import (
    create_database_engine,
    init_database,
    make_session_factory,
    session_scope,
)
from acessisaude_audit.persistence.repositories import JsonScanStore, ScanRepository
from acessisaude_audit.reporting.html import render_report

router = APIRouter(prefix="/varreduras", tags=["varreduras"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Registro de execuções em andamento
# ---------------------------------------------------------------------------
# Registro em memória, deliberadamente simples. Uma varredura é uma operação de
# pesquisa iniciada manualmente por um operador que acompanha o resultado — não
# há requisito de fila durável, retomada após queda ou execução distribuída.
# Introduzir Celery/Redis aqui adicionaria infraestrutura que ninguém precisa
# manter e que dificultaria a reprodução do estudo por terceiros.
#
# A consequência é explícita e documentada: reiniciar o processo perde o estado
# das execuções em curso. As varreduras já concluídas estão em disco e no banco.
# ---------------------------------------------------------------------------
_JOBS: dict[str, dict[str, Any]] = {}


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Inicia uma varredura em segundo plano",
)
async def start_scan(
    request: ScanRequest,
    background: BackgroundTasks,
    catalog: TargetCatalog = Depends(get_catalog),
    settings: Settings = Depends(get_settings_dep),
) -> dict[str, Any]:
    """Enfileira a execução de uma varredura e devolve o identificador do trabalho.

    Retorna 202: a varredura leva de segundos a minutos por página, e manter a
    requisição HTTP aberta durante a coleta produziria timeouts no cliente e
    interromperia a coleta ao menor soluço de rede.
    """
    try:
        target = catalog.get(request.target_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alvo não encontrado: {request.target_id}",
        ) from exc

    if not target.enabled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"O alvo {target.id!r} está desabilitado no catálogo. Alvos de produção "
                "nascem desabilitados por conduta de coleta: habilite-o explicitamente "
                "em targets.yaml, assumindo o respeito ao robots.txt e ao intervalo "
                "entre requisições."
            ),
        )

    viewports = settings.viewports()
    if request.viewports:
        wanted = set(request.viewports)
        viewports = tuple(v for v in viewports if v.name in wanted)
        if not viewports:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nenhum perfil de dispositivo conhecido em {request.viewports}.",
            )

    job_id = str(uuid4())
    _JOBS[job_id] = {
        "id": job_id,
        "target_id": target.id,
        "status": "pendente",
        "concluidas": 0,
        "total": len(target.auditable_seeds) * len(viewports),
        "url_corrente": None,
        "scan_id": None,
        "erro": None,
    }

    background.add_task(_run_scan, job_id, target, settings, list(viewports), request.discover)
    logger.info("varredura enfileirada", extra={"job": job_id, "alvo": target.id})
    return {"job_id": job_id, "status": "pendente", "alvo": target.id}


async def _run_scan(
    job_id: str,
    target: Target,
    settings: Settings,
    viewports: list[Any],
    discover: bool,
) -> None:
    """Executa a varredura e persiste o resultado.

    Roda fora do ciclo da requisição. Toda exceção é capturada e registrada no
    trabalho: uma falha aqui não pode derrubar o servidor da API.
    """
    job = _JOBS[job_id]
    job["status"] = "executando"

    def progress(done: int, total: int, url: str) -> None:
        job.update(concluidas=done, total=total, url_corrente=url)

    try:
        engine = AuditEngine(settings)
        scan = await engine.run(
            target, viewports=viewports, discover=discover, on_progress=progress
        )

        store = JsonScanStore(settings.scans_dir)
        json_path = store.save(scan)

        # Sessão própria: a do request já foi encerrada quando a tarefa começa.
        db = create_database_engine(settings.resolved_database_url())
        init_database(db)
        with session_scope(make_session_factory(db)) as session:
            ScanRepository(session, params=settings.scoring_parameters()).save(
                scan, json_path=json_path, sphere=target.sphere.value
            )

        job.update(status="concluida", scan_id=str(scan.id), url_corrente=None)
        logger.info(
            "varredura persistida",
            extra={"job": job_id, "scan": str(scan.id), "status": scan.status.value},
        )
    except asyncio.CancelledError:  # pragma: no cover - encerramento do servidor
        job.update(status="cancelada")
        raise
    except Exception as exc:
        job.update(status="falhou", erro=repr(exc))
        logger.exception("varredura falhou", extra={"job": job_id, "alvo": target.id})


@router.get("/trabalhos/{job_id}", summary="Consulta o andamento de uma varredura")
def get_job(job_id: str) -> dict[str, Any]:
    """Progresso de uma execução em segundo plano."""
    job = _JOBS.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Trabalho desconhecido. O registro de execuções é mantido em memória "
                "e se perde ao reiniciar o servidor."
            ),
        )
    return job


@router.get("", response_model=Page[ScanSummary], summary="Lista varreduras registradas")
def list_scans(
    target_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    repo: ScanRepository = Depends(get_repository),
) -> Page[ScanSummary]:
    """Varreduras persistidas, da mais recente à mais antiga."""
    rows = repo.list_rows(target_id=target_id, limit=limit, offset=offset)
    return Page[ScanSummary](
        items=[ScanSummary.model_validate(r) for r in rows],
        total=repo.count(target_id=target_id),
        limit=limit,
        offset=offset,
    )


@router.get("/{scan_id}", response_model=ScanResult, summary="Recupera a varredura completa")
def get_scan(scan_id: str, repo: ScanRepository = Depends(get_repository)) -> ScanResult:
    """Documento integral da varredura — o artefato primário de pesquisa."""
    scan = repo.get(scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Varredura não encontrada."
        )
    return scan


@router.get("/{scan_id}/indices", summary="Índices agregados da varredura")
def get_scan_scores(
    scan_id: str,
    repo: ScanRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings_dep),
) -> dict[str, Any]:
    """Índices, distribuições e perfil de exclusão.

    Inclui ``parametros`` na resposta: nenhum índice deste projeto deve
    circular dissociado das constantes que o produziram.
    """
    scan = repo.get(scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Varredura não encontrada."
        )

    params = settings.scoring_parameters()
    score = score_scan(scan, params)
    return {
        "indices": score.model_dump(),
        "grupos_excluidos": [
            {"grupo": g.value, "ocorrencias": n} for g, n in summarize_by_group(score)
        ],
        "parametros": params.as_dict(),
        "taxa_de_perda": scan.loss_rate,
        "lacunas_declaradas": scan.config_snapshot.get("plan", {}).get("declared_gaps", []),
    }


@router.get(
    "/{scan_id}/relatorio",
    response_class=HTMLResponse,
    summary="Relatório HTML acessível da varredura",
)
def get_scan_report(
    scan_id: str,
    repo: ScanRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings_dep),
) -> HTMLResponse:
    """Relatório completo, autocontido e conforme WCAG 2.1 AA."""
    scan = repo.get(scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Varredura não encontrada."
        )
    return HTMLResponse(render_report(scan, params=settings.scoring_parameters()))


@router.get(
    "/{scan_id}/achados.csv",
    response_class=PlainTextResponse,
    summary="Exporta os achados da varredura em CSV",
)
def export_scan_findings(
    scan_id: str,
    incluir_incompletos: bool = Query(default=True),
    repo: ScanRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings_dep),
) -> PlainTextResponse:
    """CSV em formato longo, pronto para pandas ou Excel."""
    from acessisaude_audit.reporting.exports import export_findings_csv

    scan = repo.get(scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Varredura não encontrada."
        )

    path = settings.exports_dir / f"achados__{scan_id}.csv"
    export_findings_csv([scan], path, include_incomplete=incluir_incompletos)
    return PlainTextResponse(
        path.read_text(encoding="utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="achados__{scan_id}.csv"'},
    )


@router.get(
    "/agregados/criterios",
    summary="Frequência de critérios violados em todas as varreduras",
)
def criterion_frequency(
    apenas_violacoes: bool = Query(default=True),
    repo: ScanRepository = Depends(get_repository),
) -> list[dict[str, Any]]:
    """Quais barreiras são estruturais no ecossistema, e não acidentes isolados.

    É a consulta que alimenta a figura principal do artigo.
    """
    from acessisaude_audit.domain.wcag import criterion

    out: list[dict[str, Any]] = []
    for crit_id, total in repo.criterion_frequency(only_violations=apenas_violacoes):
        try:
            sc = criterion(crit_id)
            out.append(
                {
                    "criterio": crit_id,
                    "titulo": sc.title_pt,
                    "nivel": sc.level.value,
                    "principio": sc.principle.value,
                    "achados": total,
                }
            )
        except KeyError:
            out.append({"criterio": crit_id, "titulo": None, "achados": total})
    return out


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove uma varredura")
def delete_scan(scan_id: str, repo: ScanRepository = Depends(get_repository)) -> None:
    """Exclui a varredura do índice relacional.

    O arquivo JSON em ``data/scans/`` **não** é removido: ele é o registro
    primário da pesquisa e sua exclusão precisa ser um ato deliberado no sistema
    de arquivos, nunca efeito colateral de uma chamada de API.
    """
    if not repo.delete(scan_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Varredura não encontrada."
        )
