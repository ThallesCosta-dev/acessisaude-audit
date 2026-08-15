"""Rotas de referência normativa: WCAG, dispositivos legais e a matriz que os une.

Não dependem de nenhuma varredura. Existem para que o dashboard consiga
explicar um achado sem duplicar, em TypeScript, a matriz jurídica que já está
modelada em Python — evitando que as duas divirjam com o tempo, problema
clássico em sistemas com regra de negócio replicada no cliente.

São também o modo mais direto de tornar a contribuição do projeto inspecionável:
a matriz WCAG↔LBI fica disponível como dado, não apenas como texto de artigo.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from acessisaude_audit.api.schemas import CriterionOut, ProvisionOut
from acessisaude_audit.domain.lbi import LEGAL_PROVISIONS, provision
from acessisaude_audit.domain.mapping import mapping_for, unmapped_criteria
from acessisaude_audit.domain.wcag import WCAG_CRITERIA, ConformanceLevel, criterion

router = APIRouter(prefix="/referencia", tags=["referência normativa"])


def _to_out(criterion_id: str) -> CriterionOut:
    sc = criterion(criterion_id)
    m = mapping_for(criterion_id)
    return CriterionOut(
        id=sc.id,
        title_pt=sc.title_pt,
        title_en=sc.title_en,
        level=sc.level.value,
        principle=sc.principle.value,
        rationale=sc.rationale,
        automatable=sc.automatable,
        affects=sorted(g.value for g in sc.affects),
        url=sc.url,
        legal_risk=m.legal_risk.value if m else None,
        legal_thesis=m.thesis if m else None,
        remediation=m.remediation if m else None,
        provisions=list(m.provision_keys) if m else [],
    )


@router.get(
    "/criterios",
    response_model=list[CriterionOut],
    summary="Lista os critérios WCAG 2.1 A/AA com seu vínculo jurídico",
)
def list_criteria(
    nivel: ConformanceLevel | None = Query(default=None, description="Filtra por nível."),
    apenas_automatizaveis: bool = Query(
        default=False,
        description=(
            "Restringe aos critérios com veredito automático — o denominador "
            "honesto do índice de conformidade."
        ),
    ),
) -> list[CriterionOut]:
    """Universo normativo auditado, com risco jurídico e conduta corretiva."""
    items = WCAG_CRITERIA
    if nivel is not None:
        items = tuple(c for c in items if c.level is nivel)
    if apenas_automatizaveis:
        items = tuple(c for c in items if c.automatable)
    return [_to_out(c.id) for c in items]


@router.get(
    "/criterios/{criterion_id}",
    response_model=CriterionOut,
    summary="Detalha um critério e sua fundamentação jurídica",
)
def get_criterion(criterion_id: str) -> CriterionOut:
    """Um critério com seu risco jurídico, tese e dispositivos invocáveis."""
    try:
        return _to_out(criterion_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Critério fora do escopo A/AA modelado: {criterion_id}",
        ) from exc


@router.get(
    "/dispositivos",
    response_model=list[ProvisionOut],
    summary="Lista os dispositivos normativos invocáveis",
)
def list_provisions() -> list[ProvisionOut]:
    """Constituição, Convenção da ONU, LBI, LAI, decretos e eMAG."""
    return [
        ProvisionOut(
            key=p.key,
            source=p.source.value,
            label=p.label,
            summary=p.summary,
            strength=p.strength.value,
            addressee=p.addressee,
            citation=p.citation,
            url=p.url,
            routes=sorted(r.value for r in p.routes),
        )
        for p in LEGAL_PROVISIONS
    ]


@router.get(
    "/dispositivos/{key}",
    response_model=ProvisionOut,
    summary="Detalha um dispositivo normativo",
)
def get_provision(key: str) -> ProvisionOut:
    """Um dispositivo normativo com citação ABNT e vias de exigibilidade."""
    try:
        p = provision(key)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo não registrado: {key}",
        ) from exc
    return ProvisionOut(
        key=p.key,
        source=p.source.value,
        label=p.label,
        summary=p.summary,
        strength=p.strength.value,
        addressee=p.addressee,
        citation=p.citation,
        url=p.url,
        routes=sorted(r.value for r in p.routes),
    )


@router.get(
    "/integridade-da-matriz",
    summary="Verifica se todo critério do escopo tem fundamentação jurídica",
)
def matrix_integrity() -> dict[str, object]:
    """Diagnóstico de completude da matriz WCAG↔LBI.

    Exposto como rota — e não apenas como teste — porque a completude é uma
    afirmação do artigo. Um revisor pode conferi-la sem ler o código.
    """
    orphans = unmapped_criteria()
    return {
        "criterios_no_escopo": len(WCAG_CRITERIA),
        "criterios_sem_mapeamento": list(orphans),
        "matriz_completa": not orphans,
        "dispositivos_registrados": len(LEGAL_PROVISIONS),
    }
