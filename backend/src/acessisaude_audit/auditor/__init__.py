"""Camada de coleta: navegador, motor de regras, sondas e conduta de crawling.

Depende de ``domain`` (para os modelos e a taxonomia) e de ``catalog`` (para
saber o que auditar). **Não** depende de ``api``, ``persistence`` nem
``reporting`` — a coleta produz objetos de domínio e ignora completamente onde
eles serão guardados ou como serão exibidos.
"""

from acessisaude_audit.auditor.axe_runner import AxeResult, AxeRunner, vendored_axe_path
from acessisaude_audit.auditor.browser import BrowserPool, LoadedPage
from acessisaude_audit.auditor.crawler import HostRateLimiter, RobotsGate, normalize_url
from acessisaude_audit.auditor.engine import AuditEngine, PageTask, ScanPlan
from acessisaude_audit.auditor.probes import ALL_PROBES, Probe, ProbeContext, default_probes

__all__ = [
    "ALL_PROBES",
    "AuditEngine",
    "AxeResult",
    "AxeRunner",
    "BrowserPool",
    "HostRateLimiter",
    "LoadedPage",
    "PageTask",
    "Probe",
    "ProbeContext",
    "RobotsGate",
    "ScanPlan",
    "default_probes",
    "normalize_url",
    "vendored_axe_path",
]
