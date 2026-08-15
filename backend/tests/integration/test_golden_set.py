"""Validação do motor contra o conjunto de referência.

Este é o teste que autoriza o projeto a fazer afirmações sobre portais reais.
Sem ele, um resultado ruim seria ambíguo entre "o portal está ruim" e "o
detector está errado".

O que se mede:

**Sensibilidade** — o motor encontra o que está plantado? Cada critério em
``deve_detectar`` (``fixtures/manifest.yaml``) que não aparecer é um falso
negativo e falha o teste.

**Especificidade** — o motor deixa em paz o que está correto? Cada critério em
``nao_deve_detectar`` que aparecer é um falso positivo e falha o teste.

Exige Chromium (``playwright install chromium``) e sobe o servidor de fixtures
automaticamente. Marcado como ``integration``: fica fora do ciclo rápido.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from acessisaude_audit.auditor.engine import AuditEngine
from acessisaude_audit.catalog.loader import GovernmentSphere, SeedPage, Target
from acessisaude_audit.config import Settings
from acessisaude_audit.domain.models import Outcome, PageStatus, ScanResult, Viewport
from acessisaude_audit.domain.scoring import score_scan

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

VP_MOBILE = Viewport(name="mobile-320", width=320, height=640, is_mobile=True)
VP_DESKTOP = Viewport(name="desktop-1366", width=1366, height=768)


def _target_for(base_url: str, arquivo: str, *, critical: bool = False) -> Target:
    """Alvo sintético de página única, para isolar cada fixture."""
    return Target(
        id="golden",
        name="Conjunto de validação",
        organization="AcessiSaúde-Audit",
        sphere=GovernmentSphere.FEDERAL,
        base_url=base_url,
        selection_rationale="Página do conjunto de validação sintético do projeto.",
        seeds=[SeedPage(url=f"{base_url}/{arquivo}", label=arquivo, critical=critical)],
    )


def _page_spec(manifest: dict[str, Any], arquivo: str) -> dict[str, Any]:
    for pagina in manifest["paginas"]:
        if pagina["arquivo"] == arquivo:
            return pagina
    raise KeyError(f"Fixture ausente do manifesto: {arquivo}")


async def _scan(
    settings: Settings, base_url: str, arquivo: str, viewports: tuple[Viewport, ...]
) -> ScanResult:
    engine = AuditEngine(settings)
    target = _target_for(base_url, arquivo, critical=True)
    return await engine.run(target, viewports=viewports)


def _criterios_detectados(scan: ScanResult) -> set[str]:
    """Critérios com veredito de FALHA. Indícios não contam."""
    return {c for page in scan.pages for f in page.violations for c in f.criteria}


def _regras_detectadas(scan: ScanResult) -> set[str]:
    return {f.rule_id for page in scan.pages for f in page.violations}


class TestCasoControleNegativo:
    """A página conforme não pode gerar violação alguma."""

    async def test_pagina_acessivel_nao_gera_falsos_positivos(
        self, settings: Settings, fixture_server: str, golden_manifest: dict[str, Any]
    ) -> None:
        arquivo = "pages/acessivel-agendamento.html"
        spec = _page_spec(golden_manifest, arquivo)
        scan = await _scan(settings, fixture_server, arquivo, (VP_MOBILE, VP_DESKTOP))

        assert scan.successful_pages, f"Nenhuma página carregou: {scan.errors}"

        detectados = _criterios_detectados(scan)
        proibidos = set(spec["nao_deve_detectar"])
        falsos_positivos = detectados & proibidos

        assert not falsos_positivos, (
            "Falsos positivos na página conforme: "
            f"{sorted(falsos_positivos)}.\nAchados: "
            + "\n".join(
                f"  {f.rule_id} {f.criteria} — {f.summary}"
                for p in scan.pages
                for f in p.violations
            )
        )

    async def test_pagina_acessivel_nao_tem_barreira_absoluta(
        self, settings: Settings, fixture_server: str
    ) -> None:
        scan = await _scan(
            settings, fixture_server, "pages/acessivel-agendamento.html", (VP_DESKTOP,)
        )
        score = score_scan(scan)
        assert score.absolute_barrier is False
        assert score.conformance_index == 100.0


class TestCasoControlePositivo:
    """A página com barreiras plantadas precisa acusar cada uma delas."""

    async def test_detecta_todas_as_barreiras_esperadas(
        self, settings: Settings, fixture_server: str, golden_manifest: dict[str, Any]
    ) -> None:
        arquivo = "pages/inacessivel-agendamento.html"
        spec = _page_spec(golden_manifest, arquivo)
        scan = await _scan(settings, fixture_server, arquivo, (VP_MOBILE, VP_DESKTOP))

        assert scan.successful_pages, f"Nenhuma página carregou: {scan.errors}"

        detectados = _criterios_detectados(scan)
        esperados = set(spec["deve_detectar"])
        falsos_negativos = esperados - detectados

        assert not falsos_negativos, (
            f"Barreiras plantadas não detectadas: {sorted(falsos_negativos)}.\n"
            f"Detectados: {sorted(detectados)}"
        )

    async def test_sinaliza_barreira_absoluta(
        self, settings: Settings, fixture_server: str
    ) -> None:
        """Controles em <div onclick> não têm rota alternativa: risco crítico."""
        scan = await _scan(
            settings, fixture_server, "pages/inacessivel-agendamento.html", (VP_DESKTOP,)
        )
        assert score_scan(scan).absolute_barrier is True

    async def test_sondas_proprias_detectam_o_que_o_axe_nao_ve(
        self, settings: Settings, fixture_server: str
    ) -> None:
        """Justificativa empírica da existência das sondas.

        Estas quatro barreiras não são detectáveis por inspeção estática do DOM:
        exigem interação real ou avaliação em condição de uso.
        """
        scan = await _scan(
            settings,
            fixture_server,
            "pages/inacessivel-agendamento.html",
            (VP_MOBILE, VP_DESKTOP),
        )
        regras = _regras_detectadas(scan)
        for esperada in (
            "probe.zoom-lock",  # bloqueio de ampliação
            "probe.meta-refresh",  # recarregamento automático
            "probe.positive-tabindex",  # ordem de foco alterada
            "probe.non-interactive-control",  # div com onclick
        ):
            assert esperada in regras, f"Sonda {esperada} não acusou. Regras: {sorted(regras)}"

    async def test_refluxo_so_e_acusado_no_perfil_movel(
        self, settings: Settings, fixture_server: str
    ) -> None:
        """A tabela de 900 px transborda em 320 px, mas não em 1366 px."""
        arquivo = "pages/inacessivel-agendamento.html"
        movel = await _scan(settings, fixture_server, arquivo, (VP_MOBILE,))
        desktop = await _scan(settings, fixture_server, arquivo, (VP_DESKTOP,))

        assert "probe.reflow-320" in _regras_detectadas(movel)
        assert "probe.reflow-320" not in _regras_detectadas(desktop)

    async def test_volume_minimo_de_violacoes(
        self, settings: Settings, fixture_server: str, golden_manifest: dict[str, Any]
    ) -> None:
        spec = _page_spec(golden_manifest, "pages/inacessivel-agendamento.html")
        scan = await _scan(
            settings,
            fixture_server,
            "pages/inacessivel-agendamento.html",
            (VP_MOBILE, VP_DESKTOP),
        )
        assert scan.violation_count >= spec["min_violacoes"]


class TestIsolamentoPorTema:
    """Fixtures temáticas verificam a atribuição correta de critério."""

    @pytest.mark.parametrize(
        "arquivo",
        ["pages/contraste-e-cor.html", "pages/formulario-sem-rotulos.html"],
    )
    async def test_detecta_o_esperado_e_nada_alem(
        self,
        settings: Settings,
        fixture_server: str,
        golden_manifest: dict[str, Any],
        arquivo: str,
    ) -> None:
        spec = _page_spec(golden_manifest, arquivo)
        scan = await _scan(settings, fixture_server, arquivo, (VP_DESKTOP,))
        assert scan.successful_pages, f"Página não carregou: {scan.errors}"

        detectados = _criterios_detectados(scan)

        faltando = set(spec.get("deve_detectar", [])) - detectados
        assert not faltando, f"{arquivo}: não detectou {sorted(faltando)}"

        indevidos = detectados & set(spec.get("nao_deve_detectar", []))
        assert not indevidos, f"{arquivo}: detectou indevidamente {sorted(indevidos)}"


class TestCustoDeAcesso:
    """A dimensão que nenhuma ferramenta convencional de acessibilidade mede."""

    async def test_mede_peso_e_emite_achado_de_custo(
        self, settings: Settings, fixture_server: str, golden_manifest: dict[str, Any]
    ) -> None:
        arquivo = "pages/pagina-pesada.html"
        spec = _page_spec(golden_manifest, arquivo)
        scan = await _scan(settings, fixture_server, arquivo, (VP_DESKTOP,))

        pagina = scan.successful_pages[0]
        assert pagina.network.total_mb >= spec["peso_minimo_mb"], (
            f"Peso medido {pagina.network.total_mb} MB, abaixo do mínimo esperado. "
            "O servidor de fixtures gerou os recursos sintéticos?"
        )
        assert "probe.data-cost" in _regras_detectadas(scan)

    async def test_custo_e_convertido_em_reais_e_fracao_de_franquia(
        self, settings: Settings, fixture_server: str
    ) -> None:
        scan = await _scan(settings, fixture_server, "pages/pagina-pesada.html", (VP_DESKTOP,))
        cost = score_scan(scan, settings.scoring_parameters()).data_cost

        assert cost is not None
        assert cost.cost_brl > 0
        assert cost.franchise_share_pct > 0
        assert cost.is_heavy is True

    async def test_distingue_peso_proprio_de_tracking_de_terceiros(
        self, settings: Settings, fixture_server: str, golden_manifest: dict[str, Any]
    ) -> None:
        """O achado decorre do peso, não da fração de terceiros (~23%).

        Verifica que o motor separa as duas causas em vez de somá-las: são
        problemas distintos, com correções e fundamentos jurídicos distintos.
        """
        spec = _page_spec(golden_manifest, "pages/pagina-pesada.html")
        scan = await _scan(settings, fixture_server, "pages/pagina-pesada.html", (VP_DESKTOP,))

        rede = scan.successful_pages[0].network
        assert rede.third_party_bytes > 0, "Os recursos de 'localhost' não foram contabilizados."
        assert rede.third_party_share < spec["fracao_terceiros_maxima"]

    async def test_pagina_pesada_e_conforme_em_wcag(
        self, settings: Settings, fixture_server: str, golden_manifest: dict[str, Any]
    ) -> None:
        """A barreira é econômica, não técnica — e o motor não as confunde."""
        spec = _page_spec(golden_manifest, "pages/pagina-pesada.html")
        scan = await _scan(settings, fixture_server, "pages/pagina-pesada.html", (VP_DESKTOP,))

        indevidos = _criterios_detectados(scan) & set(spec["nao_deve_detectar"])
        assert not indevidos, f"Falsos positivos de WCAG: {sorted(indevidos)}"


class TestIntegridadeDaColeta:
    """Propriedades do resultado, independentes de qual página foi auditada."""

    async def test_registra_procedencia_completa(
        self, settings: Settings, fixture_server: str
    ) -> None:
        """Todo número precisa ser rastreável até o motor que o produziu."""
        scan = await _scan(settings, fixture_server, "pages/contraste-e-cor.html", (VP_DESKTOP,))
        assert scan.axe_version, "Versão do axe-core não registrada."
        assert scan.browser, "Navegador não registrado."
        assert scan.engine_version
        assert scan.config_snapshot["probes"]
        assert scan.config_snapshot["viewports"]
        assert "scoring" in scan.config_snapshot

    async def test_indicios_nunca_viram_violacao(
        self, settings: Settings, fixture_server: str
    ) -> None:
        scan = await _scan(
            settings, fixture_server, "pages/formulario-sem-rotulos.html", (VP_DESKTOP,)
        )
        incompletos = [f for p in scan.pages for f in p.findings if f.outcome is Outcome.INCOMPLETE]
        assert all(f.impact is None for f in incompletos), (
            "Achado indeterminado com gravidade técnica atribuída."
        )

    async def test_url_inexistente_vira_erro_registrado_e_nao_excecao(
        self, settings: Settings, fixture_server: str
    ) -> None:
        """Uma página fora do ar não pode interromper a varredura das demais."""
        scan = await _scan(settings, fixture_server, "pages/nao-existe.html", (VP_DESKTOP,))
        assert scan.pages
        assert scan.pages[0].status is PageStatus.HTTP_ERROR
        assert scan.loss_rate == 1.0

    async def test_achados_carregam_as_tres_camadas(
        self, settings: Settings, fixture_server: str
    ) -> None:
        """Técnica, normativa e jurídica — o vínculo é montado na coleta."""
        scan = await _scan(
            settings, fixture_server, "pages/inacessivel-agendamento.html", (VP_DESKTOP,)
        )
        violacoes = [f for p in scan.pages for f in p.violations if f.criteria]
        assert violacoes

        for f in violacoes:
            assert f.rule_id
            assert f.criteria
            assert f.legal_risk is not None, f"{f.rule_id} sem risco jurídico"
            assert f.legal_provisions, f"{f.rule_id} sem dispositivos normativos"
            assert f.legal_thesis, f"{f.rule_id} sem tese jurídica"

    async def test_relatorio_e_gerado_a_partir_da_varredura_real(
        self, settings: Settings, fixture_server: str, tmp_path: Path
    ) -> None:
        from acessisaude_audit.reporting.html import write_report

        scan = await _scan(
            settings, fixture_server, "pages/inacessivel-agendamento.html", (VP_DESKTOP,)
        )
        path = write_report(scan, tmp_path)
        html = path.read_text(encoding="utf-8")

        assert 'lang="pt-BR"' in html
        assert "Barreira absoluta" in html
        assert "LBI, art. 63, caput" in html
