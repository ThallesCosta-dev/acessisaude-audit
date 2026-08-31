"""Esquema relacional para consulta e agregação.

Estratégia de persistência — **documento + índice**:

- O :class:`~acessisaude_audit.domain.models.ScanResult` completo é gravado
  como JSON, tanto em arquivo (``data/scans/``) quanto na coluna
  :attr:`ScanRow.document`. Esse JSON é o **dado primário da pesquisa**: nada
  se perde, e qualquer análise futura pode ser refeita sobre ele, inclusive se
  a modelagem relacional mudar.
- As tabelas :class:`ScanRow` e :class:`FindingRow` são um **índice achatado**
  do mesmo conteúdo, existente apenas para responder rápido às consultas do
  dashboard e das análises ("quantas violações de 1.4.3 por esfera de
  governo?").

A duplicação é deliberada e a direção da verdade é explícita: em qualquer
divergência, o documento JSON prevalece e o índice é reconstruído a partir dele
(:func:`~acessisaude_audit.persistence.repositories.ScanRepository.reindex`).
Isso evita o problema clássico de normalizar dados de pesquisa cedo demais e
descobrir, na análise, que um campo descartado era essencial.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

__all__ = ["Base", "FindingRow", "ScanRow"]


class Base(DeclarativeBase):
    """Base declarativa do esquema."""


class ScanRow(Base):
    """Uma varredura, com seus índices agregados pré-calculados."""

    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    schema_version: Mapped[str] = mapped_column(String(16), nullable=False)

    target_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    target_name: Mapped[str] = mapped_column(String(255), default="")
    base_url: Mapped[str] = mapped_column(String(1024), default="")
    sphere: Mapped[str | None] = mapped_column(String(40), index=True)
    """Esfera federativa, copiada do catálogo no momento da varredura.

    Desnormalizado de propósito: o catálogo é versionado e pode mudar, mas a
    análise precisa saber a que esfera o alvo pertencia **quando o dado foi
    coletado**."""

    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    engine_version: Mapped[str] = mapped_column(String(40), default="")
    axe_version: Mapped[str | None] = mapped_column(String(40))
    browser: Mapped[str] = mapped_column(String(120), default="")

    page_count: Mapped[int] = mapped_column(Integer, default=0)
    violation_count: Mapped[int] = mapped_column(Integer, default=0)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    incomplete_count: Mapped[int] = mapped_column(Integer, default=0)
    loss_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Índices anuláveis: nulo significa "não observado", e é distinto de zero.
    # Uma varredura em que nenhuma página carregou não tem veredito — ver
    # AccessibilityScore.observed. Filtrar por `observed.is_(True)` antes de
    # agregar é obrigatório; sem isso, a ausência de observação entra na média
    # como se fosse conformidade perfeita.
    observed: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    conformance_index: Mapped[float | None] = mapped_column(Float)
    friction_index: Mapped[float | None] = mapped_column(Float)
    legal_exposure_index: Mapped[float | None] = mapped_column(Float)
    absolute_barrier: Mapped[bool | None] = mapped_column(Boolean, index=True)
    coverage: Mapped[float] = mapped_column(Float, default=0.0)

    mean_page_mb: Mapped[float] = mapped_column(Float, default=0.0)
    mean_cost_brl: Mapped[float] = mapped_column(Float, default=0.0)

    document: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    """O ScanResult completo em JSON — a fonte da verdade."""

    json_path: Mapped[str | None] = mapped_column(String(1024))
    """Caminho do arquivo JSON correspondente, quando gravado em disco."""

    findings: Mapped[list[FindingRow]] = relationship(
        back_populates="scan", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (Index("ix_scans_target_started", "target_id", "started_at"),)

    def __repr__(self) -> str:  # pragma: no cover - conveniência de depuração
        ica = self.conformance_index if self.observed else "sem veredito"
        return f"<ScanRow {self.target_id} {self.started_at:%Y-%m-%d} ICA={ica}>"


class FindingRow(Base):
    """Um achado achatado, pronto para agregação.

    Não guarda os nós de evidência: eles são volumosos, não entram em nenhuma
    agregação e permanecem disponíveis no documento JSON da varredura. Guardar
    apenas a contagem (``occurrences``) mantém a tabela ágil sem perder
    informação analítica.
    """

    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True
    )

    rule_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    impact: Mapped[str | None] = mapped_column(String(20), index=True)
    legal_risk: Mapped[str | None] = mapped_column(String(20), index=True)

    criteria: Mapped[list[str]] = mapped_column(JSON, default=list)
    primary_criterion: Mapped[str | None] = mapped_column(String(12), index=True)
    """Primeiro critério da lista — permite agregar por critério sem abrir o JSON."""

    principle: Mapped[str | None] = mapped_column(String(20), index=True)
    level: Mapped[str | None] = mapped_column(String(4), index=True)

    affects: Mapped[list[str]] = mapped_column(JSON, default=list)
    legal_provisions: Mapped[list[str]] = mapped_column(JSON, default=list)

    occurrences: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text, default="")
    legal_thesis: Mapped[str | None] = mapped_column(Text)

    page_url: Mapped[str] = mapped_column(String(1024), default="", index=True)
    viewport: Mapped[str] = mapped_column(String(40), default="", index=True)
    is_critical_path: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    scan: Mapped[ScanRow] = relationship(back_populates="findings")

    __table_args__ = (
        Index("ix_findings_scan_criterion", "scan_id", "primary_criterion"),
        Index("ix_findings_outcome_risk", "outcome", "legal_risk"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FindingRow {self.rule_id} {self.outcome} x{self.occurrences}>"
