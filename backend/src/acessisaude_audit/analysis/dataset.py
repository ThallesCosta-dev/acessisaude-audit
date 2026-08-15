"""Construção dos data frames de análise a partir das varreduras.

Fronteira entre a ferramenta e a pesquisa. Tudo daqui para a frente é análise
estatística; tudo antes é coleta. A separação permite que o artigo descreva a
coleta e a análise como etapas independentes — e permite reanalisar dados já
coletados sem revarrer portal algum.

Três data frames, em formato longo (*tidy*):

``achados``
    Uma linha por achado. Unidade de análise principal.
``paginas``
    Uma linha por página × viewport, com índices e custo de dados.
``varreduras``
    Uma linha por varredura, com os índices agregados.

Convenção sobre ausência: colunas numéricas usam ``NaN`` para "não medido" e
nunca ``0``. Confundir os dois inventaria observações — um LCP ausente viraria
"carregamento instantâneo" em qualquer média.

O import de pandas é opcional (extra ``analysis``): a ferramenta de coleta roda
sem ele, e só quem for analisar precisa instalá-lo.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from acessisaude_audit.catalog.loader import TargetCatalog
from acessisaude_audit.domain.models import Outcome, ScanResult
from acessisaude_audit.domain.scoring import (
    DEFAULT_PARAMETERS,
    ScoringParameters,
    score_page,
    score_scan,
)
from acessisaude_audit.domain.wcag import criterion
from acessisaude_audit.logging_setup import get_logger

if TYPE_CHECKING:  # pragma: no cover
    import pandas as pd

__all__ = [
    "build_findings_frame",
    "build_pages_frame",
    "build_scans_frame",
    "load_scans",
]

logger = get_logger(__name__)


def _pandas() -> Any:
    """Importa pandas com mensagem útil se o extra não estiver instalado."""
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "A análise exige o extra 'analysis'. Instale com: pip install -e \"backend[analysis]\""
        ) from exc
    return pd


def load_scans(directory: Path, *, pattern: str = "*.json") -> list[ScanResult]:
    """Carrega todas as varreduras de um diretório.

    Arquivos que não validam contra o esquema corrente são **registrados e
    pulados**, não silenciosamente ignorados nem fatais: um dataset de versão
    anterior não deve impedir a análise dos demais, mas sua exclusão precisa
    aparecer no log e ser reportada como perda.
    """
    scans: list[ScanResult] = []
    skipped: list[str] = []
    for path in sorted(directory.glob(pattern)):
        try:
            scans.append(ScanResult.model_validate_json(path.read_text(encoding="utf-8")))
        except Exception as exc:
            skipped.append(path.name)
            logger.warning(
                "varredura ignorada por incompatibilidade de esquema",
                extra={"arquivo": path.name, "erro": str(exc)},
            )
    logger.info(
        "varreduras carregadas",
        extra={"carregadas": len(scans), "ignoradas": len(skipped)},
    )
    return scans


def _target_metadata(catalog: TargetCatalog | None) -> dict[str, dict[str, Any]]:
    """Índice de metadados do catálogo, por ``target_id``."""
    if catalog is None:
        return {}
    return {
        t.id: {
            "esfera": t.sphere.value,
            "organizacao": t.organization,
            "territorio": t.territory,
            "populacao_atendida": t.population_served,
            "categorias": "|".join(c.value for c in t.categories),
        }
        for t in catalog.targets
    }


def build_findings_frame(
    scans: Sequence[ScanResult],
    *,
    catalog: TargetCatalog | None = None,
) -> pd.DataFrame:
    """Data frame de achados, uma linha por achado.

    Args:
        scans: Varreduras a incluir.
        catalog: Catálogo, para enriquecer com esfera federativa e população.
            Opcional, mas necessário para qualquer análise estratificada.

    Returns:
        ``DataFrame`` com colunas tipadas e categorias ordenadas.
    """
    pd = _pandas()
    meta = _target_metadata(catalog)
    rows: list[dict[str, Any]] = []

    for scan in scans:
        extra = meta.get(scan.target_id, {})
        for page in scan.pages:
            for f in page.findings:
                primary = f.criteria[0] if f.criteria else None
                principle = level = None
                if primary:
                    try:
                        sc = criterion(primary)
                        principle, level = sc.principle.value, sc.level.value
                    except KeyError:
                        pass
                risk = f.legal_risk
                rows.append(
                    {
                        "scan_id": str(scan.id),
                        "target_id": scan.target_id,
                        "coletado_em": scan.started_at,
                        "pagina_url": f.page_url or page.url,
                        "viewport": f.viewport or page.viewport.name,
                        "fluxo_essencial": page.is_critical_path,
                        "regra_id": f.rule_id,
                        "origem": f.source.value,
                        "veredito": f.outcome.value,
                        "violacao": f.outcome is Outcome.FAIL,
                        "gravidade_tecnica": f.impact.value if f.impact else None,
                        "risco_juridico": risk.value if risk else None,
                        "peso_juridico": risk.weight if risk else None,
                        "criterio_principal": primary,
                        "n_criterios": len(f.criteria),
                        "principio": principle,
                        "nivel": level,
                        "ocorrencias": f.occurrences,
                        "n_grupos_afetados": len(f.affects),
                        "grupos_afetados": "|".join(g.value for g in f.affects),
                        "n_dispositivos": len(f.legal_provisions),
                        **extra,
                    }
                )

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    for column in ("origem", "veredito", "gravidade_tecnica", "principio", "nivel", "esfera"):
        if column in frame:
            frame[column] = frame[column].astype("category")

    # Ordem natural do risco: permite ordenar e plotar sem reespecificar toda vez.
    if "risco_juridico" in frame:
        frame["risco_juridico"] = pd.Categorical(
            frame["risco_juridico"],
            categories=["baixo", "moderado", "alto", "critico"],
            ordered=True,
        )
    return frame


def build_pages_frame(
    scans: Sequence[ScanResult],
    *,
    catalog: TargetCatalog | None = None,
    params: ScoringParameters = DEFAULT_PARAMETERS,
) -> pd.DataFrame:
    """Data frame de páginas, uma linha por página × viewport."""
    pd = _pandas()
    meta = _target_metadata(catalog)
    rows: list[dict[str, Any]] = []

    for scan in scans:
        extra = meta.get(scan.target_id, {})
        for page in scan.pages:
            score = score_page(page, params)
            cost = score.data_cost
            net = page.network
            rows.append(
                {
                    "scan_id": str(scan.id),
                    "target_id": scan.target_id,
                    "coletado_em": scan.started_at,
                    "pagina_url": page.final_url or page.url,
                    "titulo": page.title,
                    "idioma_declarado": page.lang,
                    "viewport": page.viewport.name,
                    "movel": page.viewport.is_mobile,
                    "fluxo_essencial": page.is_critical_path,
                    "situacao": page.status.value,
                    "auditada": page.status.value == "ok",
                    "http_status": page.http_status,
                    "ica": score.conformance_index,
                    "ian": score.friction_index,
                    "iej": score.legal_exposure_index,
                    "barreira_absoluta": score.absolute_barrier,
                    "violacoes": score.violations,
                    "ocorrencias": score.occurrences,
                    "incompletos": score.incomplete,
                    "criterios_violados": score.criteria_violated,
                    "peso_mb": net.total_mb,
                    "requisicoes": net.request_count,
                    "terceiros_pct": cost.third_party_share_pct if cost else float("nan"),
                    "custo_brl": cost.cost_brl if cost else float("nan"),
                    "franquia_pct": cost.franchise_share_pct if cost else float("nan"),
                    # NaN, não 0: medição ausente não é medição de valor zero.
                    "lcp_ms": net.largest_contentful_paint_ms
                    if net.largest_contentful_paint_ms is not None
                    else float("nan"),
                    "duracao_ms": page.duration_ms if page.duration_ms else float("nan"),
                    **extra,
                }
            )

    frame = pd.DataFrame(rows)
    if not frame.empty and "esfera" in frame:
        frame["esfera"] = frame["esfera"].astype("category")
    return frame


def build_scans_frame(
    scans: Sequence[ScanResult],
    *,
    catalog: TargetCatalog | None = None,
    params: ScoringParameters = DEFAULT_PARAMETERS,
) -> pd.DataFrame:
    """Data frame de varreduras, uma linha por varredura."""
    pd = _pandas()
    meta = _target_metadata(catalog)
    rows: list[dict[str, Any]] = []

    for scan in scans:
        score = score_scan(scan, params)
        cost = score.data_cost
        rows.append(
            {
                "scan_id": str(scan.id),
                "target_id": scan.target_id,
                "target_name": scan.target_name,
                "coletado_em": scan.started_at,
                "situacao": scan.status.value,
                "paginas": scan.page_count,
                "taxa_de_perda": scan.loss_rate,
                "ica": score.conformance_index,
                "ian": score.friction_index,
                "iej": score.legal_exposure_index,
                "barreira_absoluta": score.absolute_barrier,
                "cobertura": score.coverage,
                "violacoes": score.violations,
                "ocorrencias": score.occurrences,
                "incompletos": score.incomplete,
                "criterios_violados": score.criteria_violated,
                "peso_medio_mb": cost.total_mb if cost else float("nan"),
                "custo_medio_brl": cost.cost_brl if cost else float("nan"),
                "versao_motor": scan.engine_version,
                "versao_axe": scan.axe_version,
                **meta.get(scan.target_id, {}),
            }
        )

    frame = pd.DataFrame(rows)
    if not frame.empty and "esfera" in frame:
        frame["esfera"] = frame["esfera"].astype("category")
    return frame


def criterion_prevalence(findings: pd.DataFrame, *, only_violations: bool = True) -> pd.DataFrame:
    """Prevalência de cada critério: em que fração das páginas ele é violado.

    Prevalência é preferível a contagem bruta para a figura principal do artigo.
    Contagem responde "quantos defeitos há" e é dominada pelo portal maior;
    prevalência responde "esta barreira é estrutural no ecossistema?", que é a
    pergunta da pesquisa.
    """
    pd = _pandas()
    if findings.empty:
        return pd.DataFrame(columns=["criterio", "titulo", "nivel", "paginas", "prevalencia"])

    base = findings[findings["violacao"]] if only_violations else findings
    total_pages = findings["pagina_url"].nunique()
    if total_pages == 0:
        return pd.DataFrame(columns=["criterio", "titulo", "nivel", "paginas", "prevalencia"])

    grouped = (
        base.dropna(subset=["criterio_principal"])
        .groupby("criterio_principal", observed=True)["pagina_url"]
        .nunique()
        .reset_index(name="paginas")
    )
    grouped["prevalencia"] = grouped["paginas"] / total_pages
    grouped["titulo"] = grouped["criterio_principal"].map(_criterion_title)
    grouped["nivel"] = grouped["criterio_principal"].map(_criterion_level)
    grouped = grouped.rename(columns={"criterio_principal": "criterio"})
    return grouped.sort_values("prevalencia", ascending=False).reset_index(drop=True)


def _criterion_title(criterion_id: str) -> str:
    try:
        return criterion(criterion_id).title_pt
    except KeyError:
        return "—"


def _criterion_level(criterion_id: str) -> str:
    try:
        return criterion(criterion_id).level.value
    except KeyError:
        return "—"


def exclusion_profile(findings: pd.DataFrame) -> pd.DataFrame:
    """Ocorrências de barreira por grupo de pessoas afetado.

    Converte contagem de defeitos em população impactada — a leitura que
    sustenta o argumento jurídico, já que o dano juridicamente relevante é o
    da pessoa excluída, não o do elemento HTML malformado.
    """
    pd = _pandas()
    if findings.empty:
        return pd.DataFrame(columns=["grupo", "ocorrencias", "achados"])

    base = findings[findings["violacao"]]
    registros: list[dict[str, Any]] = []
    for _, row in base.iterrows():
        grupos: Iterable[str] = (row["grupos_afetados"] or "").split("|")
        for grupo in grupos:
            if grupo:
                registros.append({"grupo": grupo, "ocorrencias": row["ocorrencias"]})

    if not registros:
        return pd.DataFrame(columns=["grupo", "ocorrencias", "achados"])

    frame = pd.DataFrame(registros)
    return (
        frame.groupby("grupo", observed=True)
        .agg(ocorrencias=("ocorrencias", "sum"), achados=("ocorrencias", "size"))
        .reset_index()
        .sort_values("ocorrencias", ascending=False)
        .reset_index(drop=True)
    )
