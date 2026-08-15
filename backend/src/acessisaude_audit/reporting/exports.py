"""Exportação tabular: o dataset que vai para a análise e para o artigo.

Duas tabelas, em formato longo (*tidy data*), porque é a forma que pandas, R e
qualquer software estatístico consomem sem transformação prévia:

- ``achados.csv`` — uma linha por achado. Unidade de análise principal.
- ``paginas.csv`` — uma linha por página × viewport, com os índices e o custo
  de dados. Unidade de análise para comparações entre portais.

Decisões de formato, todas voltadas à interoperabilidade e à honestidade do dado:

- Codificação **UTF-8 com BOM**. O Excel em português abre UTF-8 puro com
  acentuação corrompida, e o público desta ferramenta inclui gestores públicos
  que abrirão o arquivo no Excel.
- Separador **ponto e vírgula** e decimal **vírgula** opcionais, pelo mesmo motivo.
- Listas (critérios, dispositivos) serializadas com ``|`` como separador — nunca
  vírgula, que colidiria com o CSV.
- Valores ausentes ficam **vazios**, jamais zero. Zero é uma medição; vazio é a
  ausência dela, e confundir os dois inventa dado.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from acessisaude_audit.domain.models import PageAudit, ScanResult
from acessisaude_audit.domain.scoring import (
    DEFAULT_PARAMETERS,
    ScoringParameters,
    score_page,
)
from acessisaude_audit.domain.wcag import criterion
from acessisaude_audit.logging_setup import get_logger

__all__ = ["FINDING_COLUMNS", "PAGE_COLUMNS", "export_findings_csv", "export_pages_csv"]

logger = get_logger(__name__)

#: Colunas de ``achados.csv``, documentadas em ``docs/api/dicionario-de-dados.md``.
FINDING_COLUMNS: tuple[str, ...] = (
    "scan_id",
    "target_id",
    "target_name",
    "coletado_em",
    "pagina_url",
    "fluxo_essencial",
    "viewport",
    "regra_id",
    "origem",
    "veredito",
    "gravidade_tecnica",
    "risco_juridico",
    "criterios_wcag",
    "criterio_principal",
    "principio",
    "nivel",
    "ocorrencias",
    "grupos_afetados",
    "dispositivos_normativos",
    "resumo",
    "tese_juridica",
)

#: Colunas de ``paginas.csv``.
PAGE_COLUMNS: tuple[str, ...] = (
    "scan_id",
    "target_id",
    "target_name",
    "coletado_em",
    "pagina_url",
    "titulo",
    "idioma_declarado",
    "fluxo_essencial",
    "viewport",
    "situacao",
    "http_status",
    "indice_conformidade",
    "indice_atrito",
    "indice_exposicao_juridica",
    "barreira_absoluta",
    "violacoes",
    "ocorrencias",
    "incompletos",
    "criterios_violados",
    "peso_mb",
    "requisicoes",
    "terceiros_pct",
    "custo_brl",
    "franquia_pct",
    "lcp_ms",
    "duracao_auditoria_ms",
)


def _join(values: Iterable[Any]) -> str:
    """Serializa lista para célula CSV com ``|`` como separador."""
    return "|".join(str(v) for v in values)


def _writer(path: Path, columns: Sequence[str], *, delimiter: str) -> tuple[Any, Any]:
    handle = path.open("w", encoding="utf-8-sig", newline="")
    writer = csv.DictWriter(
        handle, fieldnames=list(columns), delimiter=delimiter, quoting=csv.QUOTE_MINIMAL
    )
    writer.writeheader()
    return handle, writer


def export_findings_csv(
    scans: Sequence[ScanResult],
    path: Path,
    *,
    delimiter: str = ";",
    include_incomplete: bool = True,
) -> Path:
    """Exporta todos os achados de um conjunto de varreduras.

    Args:
        scans: Varreduras a exportar.
        path: Arquivo de destino.
        delimiter: Separador de campos (``";"`` para compatibilidade com Excel
            em configuração regional brasileira).
        include_incomplete: Se ``False``, exporta apenas violações confirmadas.
            O padrão é incluir: separar violação de indício é responsabilidade
            da análise, e filtrar na exportação esconderia a distinção.

    Returns:
        O caminho gravado.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, writer = _writer(path, FINDING_COLUMNS, delimiter=delimiter)
    rows = 0
    try:
        for scan in scans:
            collected = scan.started_at.isoformat()
            for page in scan.pages:
                findings = page.findings if include_incomplete else page.violations
                for f in findings:
                    primary = f.criteria[0] if f.criteria else ""
                    principle = level = ""
                    if primary:
                        try:
                            sc = criterion(primary)
                            principle, level = sc.principle.value, sc.level.value
                        except KeyError:
                            pass
                    risk = f.legal_risk
                    writer.writerow(
                        {
                            "scan_id": str(scan.id),
                            "target_id": scan.target_id,
                            "target_name": scan.target_name,
                            "coletado_em": collected,
                            "pagina_url": f.page_url or page.url,
                            "fluxo_essencial": int(page.is_critical_path),
                            "viewport": f.viewport or page.viewport.name,
                            "regra_id": f.rule_id,
                            "origem": f.source.value,
                            "veredito": f.outcome.value,
                            "gravidade_tecnica": f.impact.value if f.impact else "",
                            "risco_juridico": risk.value if risk else "",
                            "criterios_wcag": _join(f.criteria),
                            "criterio_principal": primary,
                            "principio": principle,
                            "nivel": level,
                            "ocorrencias": f.occurrences,
                            "grupos_afetados": _join(g.value for g in f.affects),
                            "dispositivos_normativos": _join(f.legal_provisions),
                            "resumo": f.summary,
                            "tese_juridica": f.legal_thesis or "",
                        }
                    )
                    rows += 1
    finally:
        handle.close()

    logger.info("achados exportados", extra={"arquivo": str(path), "linhas": rows})
    return path


def export_pages_csv(
    scans: Sequence[ScanResult],
    path: Path,
    *,
    delimiter: str = ";",
    params: ScoringParameters = DEFAULT_PARAMETERS,
) -> Path:
    """Exporta uma linha por página auditada, com índices e custo de dados."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, writer = _writer(path, PAGE_COLUMNS, delimiter=delimiter)
    rows = 0
    try:
        for scan in scans:
            collected = scan.started_at.isoformat()
            for page in scan.pages:
                writer.writerow(_page_row(scan, page, collected, params))
                rows += 1
    finally:
        handle.close()

    logger.info("páginas exportadas", extra={"arquivo": str(path), "linhas": rows})
    return path


def _page_row(
    scan: ScanResult, page: PageAudit, collected: str, params: ScoringParameters
) -> dict[str, Any]:
    """Monta a linha de ``paginas.csv`` para uma auditoria de página."""
    score = score_page(page, params)
    cost = score.data_cost
    net = page.network
    return {
        "scan_id": str(scan.id),
        "target_id": scan.target_id,
        "target_name": scan.target_name,
        "coletado_em": collected,
        "pagina_url": page.final_url or page.url,
        "titulo": page.title or "",
        "idioma_declarado": page.lang or "",
        "fluxo_essencial": int(page.is_critical_path),
        "viewport": page.viewport.name,
        "situacao": page.status.value,
        "http_status": page.http_status if page.http_status is not None else "",
        "indice_conformidade": score.conformance_index,
        "indice_atrito": score.friction_index,
        "indice_exposicao_juridica": score.legal_exposure_index,
        "barreira_absoluta": int(score.absolute_barrier),
        "violacoes": score.violations,
        "ocorrencias": score.occurrences,
        "incompletos": score.incomplete,
        "criterios_violados": _join(score.violated_criteria),
        "peso_mb": net.total_mb,
        "requisicoes": net.request_count,
        "terceiros_pct": cost.third_party_share_pct if cost else "",
        "custo_brl": cost.cost_brl if cost else "",
        "franquia_pct": cost.franchise_share_pct if cost else "",
        # Vazio, e não zero: LCP indisponível é ausência de medição.
        "lcp_ms": net.largest_contentful_paint_ms
        if net.largest_contentful_paint_ms is not None
        else "",
        "duracao_auditoria_ms": round(page.duration_ms) if page.duration_ms else "",
    }
