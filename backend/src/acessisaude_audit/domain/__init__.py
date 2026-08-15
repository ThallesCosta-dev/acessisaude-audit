"""Camada de domínio: normas, direito, modelos e índices.

Esta camada é **pura** — não conhece navegador, banco de dados, HTTP nem
sistema de arquivos. A regra é verificável: nenhum módulo em ``domain/``
importa de ``auditor/``, ``persistence/``, ``api/`` ou ``reporting/``. O teste
``tests/unit/test_domain_purity.py`` falha se essa direção de dependência for
invertida.

Motivo: o domínio codifica a contribuição científica do projeto (a matriz
WCAG↔LBI e os índices). Mantê-lo isolado permite citá-lo, testá-lo e reusá-lo
independentemente da implementação de coleta.
"""

from acessisaude_audit.domain.lbi import LEGAL_PROVISIONS, LegalProvision, provision
from acessisaude_audit.domain.mapping import (
    CRITERION_MAPPINGS,
    CriterionMapping,
    LegalRisk,
    mapping_for,
    provisions_for,
)
from acessisaude_audit.domain.models import (
    SCHEMA_VERSION,
    EvidenceNode,
    Finding,
    FindingSource,
    Impact,
    NetworkMetrics,
    Outcome,
    PageAudit,
    PageStatus,
    ScanResult,
    ScanStatus,
    Viewport,
)
from acessisaude_audit.domain.scoring import (
    AccessibilityScore,
    DataCostScore,
    ScoringParameters,
    score_page,
    score_scan,
)
from acessisaude_audit.domain.wcag import (
    WCAG_CRITERIA,
    ConformanceLevel,
    DeficiencyGroup,
    Principle,
    SuccessCriterion,
    criterion,
    criterion_from_axe_tag,
)

__all__ = [
    "CRITERION_MAPPINGS",
    "LEGAL_PROVISIONS",
    "SCHEMA_VERSION",
    "WCAG_CRITERIA",
    "AccessibilityScore",
    "ConformanceLevel",
    "CriterionMapping",
    "DataCostScore",
    "DeficiencyGroup",
    "EvidenceNode",
    "Finding",
    "FindingSource",
    "Impact",
    "LegalProvision",
    "LegalRisk",
    "NetworkMetrics",
    "Outcome",
    "PageAudit",
    "PageStatus",
    "Principle",
    "ScanResult",
    "ScanStatus",
    "ScoringParameters",
    "SuccessCriterion",
    "Viewport",
    "criterion",
    "criterion_from_axe_tag",
    "mapping_for",
    "provision",
    "provisions_for",
    "score_page",
    "score_scan",
]
