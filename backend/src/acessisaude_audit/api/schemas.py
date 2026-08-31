"""Esquemas de entrada e saída da API.

Separados dos modelos de domínio de propósito. O domínio existe para a
pesquisa; a API existe para o dashboard. Acoplá-los faria com que qualquer
ajuste de apresentação exigisse mexer no artefato de dados científicos — e
faria com que o formato do dataset ficasse refém das necessidades da interface.

Aqui ficam apenas: resumos (versões enxutas para listagens), envelopes de
paginação e comandos de execução.
"""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from acessisaude_audit.catalog.loader import GovernmentSphere, ServiceCategory

__all__ = [
    "CriterionOut",
    "Page",
    "ProvisionOut",
    "ScanRequest",
    "ScanSummary",
    "TargetSummary",
]

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Envelope de paginação."""

    items: list[T]
    total: int = Field(description="Total de registros disponíveis, ignorando a página.")
    limit: int
    offset: int


class TargetSummary(BaseModel):
    """Alvo do catálogo, na forma consumida pelo dashboard."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    organization: str
    sphere: GovernmentSphere
    categories: list[ServiceCategory]
    base_url: str
    territory: str
    enabled: bool
    population_served: int | None
    selection_rationale: str
    auditable_pages: int = Field(description="Sementes efetivamente varríveis.")
    declared_gaps: int = Field(
        description="Sementes excluídas por exigirem autenticação — lacunas da amostra."
    )
    tags: list[str]


class ScanSummary(BaseModel):
    """Varredura em forma de resumo, para listagens e gráficos de série."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    target_id: str
    target_name: str
    sphere: str | None
    status: str
    started_at: datetime
    finished_at: datetime | None

    page_count: int
    violation_count: int
    occurrence_count: int
    incomplete_count: int
    loss_rate: float

    # Nulos quando `observed` é falso: nenhuma página foi auditada e não há
    # veredito. O consumidor precisa distinguir isso de conformidade — ver
    # AccessibilityScore.observed.
    observed: bool
    conformance_index: float | None
    friction_index: float | None
    legal_exposure_index: float | None
    absolute_barrier: bool | None
    coverage: float

    mean_page_mb: float
    mean_cost_brl: float

    engine_version: str
    axe_version: str | None


class ScanRequest(BaseModel):
    """Comando de execução de varredura."""

    target_id: str = Field(description="Identificador do alvo no catálogo.")
    discover: bool = Field(
        default=False,
        description=(
            "Complementar as sementes com links descobertos na primeira página. "
            "Desligado por padrão: descoberta automática produz amostra não "
            "reproduzível entre execuções."
        ),
    )
    viewports: list[str] | None = Field(
        default=None,
        description=("Nomes dos perfis de dispositivo a usar. Nulo executa todos os configurados."),
    )


class CriterionOut(BaseModel):
    """Critério WCAG com seu vínculo jurídico — consumido pela tela de referência."""

    id: str
    title_pt: str
    title_en: str
    level: str
    principle: str
    rationale: str
    automatable: bool
    affects: list[str]
    url: str
    legal_risk: str | None
    legal_thesis: str | None
    remediation: str | None
    provisions: list[str]


class ProvisionOut(BaseModel):
    """Dispositivo normativo em forma de saída."""

    key: str
    source: str
    label: str
    summary: str
    strength: str
    addressee: str
    citation: str
    url: str
    routes: list[str]
