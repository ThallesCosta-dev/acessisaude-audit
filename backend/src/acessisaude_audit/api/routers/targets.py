"""Rotas do catálogo de alvos."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from acessisaude_audit.api.deps import get_catalog, require_target
from acessisaude_audit.api.schemas import TargetSummary
from acessisaude_audit.catalog.loader import GovernmentSphere, Target, TargetCatalog

router = APIRouter(prefix="/alvos", tags=["alvos"])


def _to_summary(target: Target) -> TargetSummary:
    return TargetSummary(
        id=target.id,
        name=target.name,
        organization=target.organization,
        sphere=target.sphere,
        categories=target.categories,
        base_url=target.base_url,
        territory=target.territory,
        enabled=target.enabled,
        population_served=target.population_served,
        selection_rationale=target.selection_rationale,
        auditable_pages=len(target.auditable_seeds),
        declared_gaps=len(target.declared_gaps),
        tags=target.tags,
    )


@router.get("", response_model=list[TargetSummary], summary="Lista os alvos do catálogo")
def list_targets(
    esfera: GovernmentSphere | None = Query(default=None, description="Filtra por esfera."),
    apenas_habilitados: bool = Query(
        default=False,
        description=(
            "Alvos de produção nascem desabilitados por conduta de coleta. "
            "Este filtro mostra apenas os que o pesquisador liberou."
        ),
    ),
    catalog: TargetCatalog = Depends(get_catalog),
) -> list[TargetSummary]:
    """Desenho amostral do estudo, tal como declarado em ``targets.yaml``."""
    items = catalog.enabled_targets if apenas_habilitados else catalog.targets
    if esfera is not None:
        items = [t for t in items if t.sphere is esfera]
    return [_to_summary(t) for t in items]


@router.get(
    "/{target_id}",
    response_model=TargetSummary,
    summary="Detalha um alvo do catálogo",
)
def get_target(target: Target = Depends(require_target)) -> TargetSummary:
    """Metadados de um alvo, incluindo a justificativa de inclusão na amostra."""
    return _to_summary(target)


@router.get(
    "/{target_id}/paginas",
    summary="Lista as páginas do alvo, separando auditáveis de lacunas declaradas",
)
def list_target_pages(target: Target = Depends(require_target)) -> dict[str, object]:
    """Sementes do alvo.

    A separação entre ``auditaveis`` e ``lacunas_declaradas`` é substantiva, não
    cosmética: as lacunas correspondem a áreas autenticadas que a ferramenta se
    recusa a varrer. Exibi-las evita que o dashboard sugira cobertura integral
    de um serviço cuja parte mais crítica não foi examinada.
    """
    return {
        "auditaveis": [
            {"url": s.url, "label": s.label, "fluxo_essencial": s.critical}
            for s in target.auditable_seeds
        ],
        "lacunas_declaradas": [
            {
                "url": s.url,
                "label": s.label,
                "motivo": s.notes or "Exige autenticação; não auditada por conduta de coleta.",
            }
            for s in target.declared_gaps
        ],
    }
