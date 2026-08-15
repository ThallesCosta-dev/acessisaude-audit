"""Sondas próprias do AcessiSaúde-Audit.

O registro :data:`ALL_PROBES` é a lista canônica executada pelo motor. A ordem
importa apenas para a legibilidade do relatório — as sondas são independentes
entre si e nenhuma depende do resultado de outra.

Cobertura por origem (ver ``docs/arquitetura/motor-de-auditoria.md``):

===============================  ==========================================
Origem                           Papel
===============================  ==========================================
``axe-core``                     Regras determinísticas sobre o DOM estático
``probes/viewport.py``           Adaptação a tela pequena e ampliação
``probes/keyboard.py``           Operabilidade sem mouse
``probes/structure.py``          Estrutura semântica para leitor de tela
``probes/forms.py``              Rotulagem e identificação de erro
``probes/media.py``              Mídia temporal e conteúdo em movimento
``probes/digital_rights.py``     Custo de acesso e legibilidade
===============================  ==========================================
"""

from acessisaude_audit.auditor.probes.base import (
    Confidence,
    Probe,
    ProbeContext,
    affected_groups,
    help_url_for,
    remediation_for,
)
from acessisaude_audit.auditor.probes.digital_rights import (
    DataCostProbe,
    ReadabilityProbe,
    flesch_pt_br,
)
from acessisaude_audit.auditor.probes.forms import (
    ErrorIdentificationProbe,
    PlaceholderAsLabelProbe,
)
from acessisaude_audit.auditor.probes.keyboard import (
    FocusVisibilityProbe,
    InteractiveElementProbe,
    TabOrderProbe,
)
from acessisaude_audit.auditor.probes.media import (
    AutoplayProbe,
    CaptionsProbe,
    MetaRefreshProbe,
)
from acessisaude_audit.auditor.probes.structure import (
    DuplicateIdProbe,
    HeadingStructureProbe,
    LandmarkProbe,
    PageLanguageProbe,
)
from acessisaude_audit.auditor.probes.viewport import ReflowProbe, ZoomLockProbe

__all__ = [
    "ALL_PROBES",
    "AutoplayProbe",
    "CaptionsProbe",
    "Confidence",
    "DataCostProbe",
    "DuplicateIdProbe",
    "ErrorIdentificationProbe",
    "FocusVisibilityProbe",
    "HeadingStructureProbe",
    "InteractiveElementProbe",
    "LandmarkProbe",
    "MetaRefreshProbe",
    "PageLanguageProbe",
    "PlaceholderAsLabelProbe",
    "Probe",
    "ProbeContext",
    "ReadabilityProbe",
    "ReflowProbe",
    "TabOrderProbe",
    "ZoomLockProbe",
    "affected_groups",
    "default_probes",
    "flesch_pt_br",
    "help_url_for",
    "remediation_for",
]

#: Classes de sonda executadas por padrão em toda auditoria de página.
ALL_PROBES: tuple[type[Probe], ...] = (
    # Estrutura primeiro: define se o leitor de tela sequer consegue navegar.
    PageLanguageProbe,
    LandmarkProbe,
    HeadingStructureProbe,
    DuplicateIdProbe,
    # Operabilidade: barreiras sem rota alternativa.
    InteractiveElementProbe,
    TabOrderProbe,
    FocusVisibilityProbe,
    # Formulários: onde o serviço público efetivamente se realiza.
    PlaceholderAsLabelProbe,
    ErrorIdentificationProbe,
    # Adaptação ao dispositivo do usuário.
    ReflowProbe,
    ZoomLockProbe,
    # Mídia temporal.
    CaptionsProbe,
    AutoplayProbe,
    MetaRefreshProbe,
    # Direitos digitais: custo e compreensão.
    DataCostProbe,
    ReadabilityProbe,
)


def default_probes() -> list[Probe]:
    """Instancia o conjunto padrão de sondas.

    Cada varredura recebe instâncias novas para que sondas com estado interno
    (nenhuma tem hoje, mas o contrato não o proíbe) não vazem informação de uma
    página para outra.
    """
    return [cls() for cls in ALL_PROBES]
