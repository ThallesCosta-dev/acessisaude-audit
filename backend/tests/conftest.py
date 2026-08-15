"""Fixtures compartilhadas da suíte.

Convenções da suíte:

- Testes **unitários** não tocam rede, disco de produção nem navegador.
- Testes de **integração** (marcador ``integration``) sobem Chromium e o
  servidor do conjunto de validação. Rodam sob demanda, não no ciclo rápido.
- Nenhum teste depende de portal real. Depender de rede externa tornaria a
  suíte um detector de instabilidade da internet, não do código.
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from acessisaude_audit.auditor.probes.base import affected_groups
from acessisaude_audit.config import Settings
from acessisaude_audit.domain.models import (
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

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "fixtures"
FIXTURE_HOST = "127.0.0.1"
FIXTURE_PORT = 8080
FIXTURE_BASE = f"http://{FIXTURE_HOST}:{FIXTURE_PORT}"


# ---------------------------------------------------------------------------
# Objetos de domínio
# ---------------------------------------------------------------------------


@pytest.fixture
def viewport_mobile() -> Viewport:
    return Viewport(name="mobile-320", width=320, height=640, is_mobile=True)


@pytest.fixture
def viewport_desktop() -> Viewport:
    return Viewport(name="desktop-1366", width=1366, height=768)


def make_finding(
    *,
    rule_id: str = "regra-teste",
    criteria: list[str] | None = None,
    outcome: Outcome = Outcome.FAIL,
    impact: Impact | None = Impact.SERIOUS,
    occurrences: int = 1,
    source: FindingSource = FindingSource.AXE_CORE,
) -> Finding:
    """Constrói um achado com valores previsíveis.

    Fábrica em vez de fixture: vários testes precisam de achados com parâmetros
    diferentes na mesma função, o que a injeção de fixture não permite.
    """
    crits = criteria if criteria is not None else ["1.4.3"]
    # Deriva os grupos afetados dos critérios, como faz o pipeline real: um
    # achado sem grupo afetado não conseguiria alimentar o perfil de exclusão.
    grupos: dict[Any, None] = {}
    for crit_id in crits:
        for grupo in affected_groups(crit_id):
            grupos.setdefault(grupo, None)

    return Finding(
        rule_id=rule_id,
        source=source,
        outcome=outcome,
        impact=impact if outcome is Outcome.FAIL else None,
        criteria=crits,
        affects=list(grupos),
        summary=f"Achado de teste para {rule_id}",
        nodes=[
            EvidenceNode(selector=f"#elemento-{i}", html=f"<div id='elemento-{i}'></div>")
            for i in range(occurrences)
        ],
        page_url="http://exemplo.test/pagina",
        viewport="desktop-1366",
    )


@pytest.fixture
def sample_page(viewport_desktop: Viewport) -> PageAudit:
    """Página auditada com um conjunto variado de achados."""
    return PageAudit(
        url="http://exemplo.test/agendamento",
        final_url="http://exemplo.test/agendamento",
        status=PageStatus.OK,
        http_status=200,
        title="Agendamento",
        lang="pt-BR",
        viewport=viewport_desktop,
        findings=[
            make_finding(rule_id="color-contrast", criteria=["1.4.3"], occurrences=4),
            make_finding(
                rule_id="probe.non-interactive-control",
                criteria=["2.1.1", "4.1.2"],
                impact=Impact.CRITICAL,
                occurrences=2,
                source=FindingSource.PROBE,
            ),
            make_finding(
                rule_id="probe.readability",
                criteria=[],
                outcome=Outcome.INCOMPLETE,
                impact=None,
                source=FindingSource.HEURISTIC,
            ),
        ],
        network=NetworkMetrics(
            total_bytes=3_145_728,  # 3 MiB
            request_count=42,
            third_party_bytes=1_048_576,  # 1 MiB
            third_party_domains=["analytics.example"],
            bytes_by_type={"document": 51_200, "script": 2_097_152, "image": 996_376},
        ),
        is_critical_path=True,
    )


@pytest.fixture
def sample_scan(sample_page: PageAudit) -> ScanResult:
    """Varredura completa com uma página bem-sucedida e uma em erro."""
    failed = PageAudit(
        url="http://exemplo.test/indisponivel",
        viewport=sample_page.viewport,
        status=PageStatus.TIMEOUT,
        error="Timeout de navegação",
    )
    return ScanResult(
        id=uuid4(),
        target_id="alvo-teste",
        target_name="Portal de Teste",
        base_url="http://exemplo.test",
        status=ScanStatus.PARTIAL,
        pages=[sample_page, failed],
        engine_version="0.1.0",
        axe_version="4.13.0",
        browser="chromium 140.0",
        config_snapshot={"probes": ["probe.data-cost"], "plan": {"declared_gaps": []}},
    )


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Configuração isolada em diretório temporário.

    Nunca reutiliza ``data/``: um teste que gravasse ali contaminaria o dataset
    de pesquisa com varreduras sintéticas.
    """
    return Settings(
        data_dir=tmp_path / "data",
        database_url=f"sqlite:///{(tmp_path / 'teste.sqlite').as_posix()}",
        headless=True,
        request_delay_ms=0,
        navigation_timeout_ms=20_000,
        settle_delay_ms=300,
        capture_screenshots=False,
        respect_robots_txt=False,
        robots_override_reason="Conjunto de validação local, sem servidor público envolvido.",
        max_pages_per_target=10,
    )


# ---------------------------------------------------------------------------
# Servidor do conjunto de validação (integração)
# ---------------------------------------------------------------------------


def _port_open(host: str, port: int, timeout: float = 0.25) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


@pytest.fixture(scope="session")
def fixture_server() -> Iterator[str]:
    """Sobe o servidor de fixtures, ou reaproveita um já em execução.

    Reaproveitar é intencional: durante o desenvolvimento é comum manter o
    servidor rodando em outro terminal, e derrubá-lo a cada sessão de teste
    seria hostil.
    """
    if _port_open(FIXTURE_HOST, FIXTURE_PORT):
        yield FIXTURE_BASE
        return

    script = REPO_ROOT / "scripts" / "servidor_fixtures.py"
    process = subprocess.Popen(
        [sys.executable, str(script), "--porta", str(FIXTURE_PORT), "--host", FIXTURE_HOST],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if _port_open(FIXTURE_HOST, FIXTURE_PORT):
            break
        time.sleep(0.2)
    else:  # pragma: no cover
        process.terminate()
        pytest.fail("Servidor de fixtures não subiu em 15 segundos.")

    try:
        yield FIXTURE_BASE
    finally:
        process.terminate()
        process.wait(timeout=5)


@pytest.fixture(scope="session")
def golden_manifest() -> dict[str, Any]:
    """Verdade de referência do conjunto de validação."""
    import yaml

    data = yaml.safe_load((FIXTURES_DIR / "manifest.yaml").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data
