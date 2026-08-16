"""Camada de análise: montagem do dataset e exclusão de páginas em erro.

O teste central deste módulo protege contra um defeito real, encontrado apenas
quando a coleta de campo produziu perda de páginas: uma página que **não
carregou** tem zero achados e, por construção, índice de conformidade 100.
Incluí-la em uma agregação faz um portal instável parecer conforme.

``score_scan`` já aplicava essa exclusão; as figuras não aplicavam. O resultado
era uma figura que contradizia a análise numérica do mesmo dado — a esfera
estadual, com 50% de perda, aparecia com mediana de ICA 86 no gráfico contra
58,9 na tabela.
"""

from __future__ import annotations

import pytest

from acessisaude_audit.domain.models import PageAudit, PageStatus, ScanResult, Viewport

pd = pytest.importorskip("pandas", reason="requer o extra 'analysis'")

from acessisaude_audit.analysis.dataset import (  # noqa: E402
    build_findings_frame,
    build_pages_frame,
    criterion_prevalence,
    exclusion_profile,
)
from acessisaude_audit.analysis.figures import only_audited  # noqa: E402

VP = Viewport(name="desktop-1366", width=1366, height=768)


@pytest.fixture
def scan_com_perda(sample_page: PageAudit) -> ScanResult:
    """Varredura com uma página auditada e duas que não carregaram."""
    falhas = [
        PageAudit(
            url="http://exemplo.test/indisponivel",
            viewport=VP,
            status=PageStatus.NAVIGATION_ERROR,
            error="net::ERR_CONNECTION_CLOSED",
        ),
        PageAudit(
            url="http://exemplo.test/erro-500",
            viewport=VP,
            status=PageStatus.HTTP_ERROR,
            http_status=500,
            error="HTTP 500",
        ),
    ]
    return ScanResult(
        target_id="alvo-instavel",
        target_name="Portal Instável",
        pages=[sample_page, *falhas],
    )


class TestExclusaoDePaginasEmErro:
    def test_pagina_em_erro_recebe_ica_100(self, scan_com_perda: ScanResult) -> None:
        """Demonstra o mecanismo do defeito, para que ele não seja esquecido.

        Não é bug do índice: uma página sem achados É conforme sob os critérios
        verificados. O erro está em agregar o que não foi medido.
        """
        paginas = build_pages_frame([scan_com_perda])
        falhas = paginas[~paginas["auditada"]]
        assert len(falhas) == 2
        assert (falhas["ica"] == 100.0).all()

    def test_only_audited_remove_as_paginas_em_erro(self, scan_com_perda: ScanResult) -> None:
        paginas = build_pages_frame([scan_com_perda])
        assert len(paginas) == 3
        assert len(only_audited(paginas)) == 1

    def test_exclusao_altera_materialmente_a_mediana(self, scan_com_perda: ScanResult) -> None:
        """A diferença não é cosmética: muda a conclusão sobre o portal."""
        paginas = build_pages_frame([scan_com_perda])
        com_falhas = paginas["ica"].median()
        so_auditadas = only_audited(paginas)["ica"].median()
        assert com_falhas > so_auditadas
        assert com_falhas == 100.0

    def test_only_audited_tolera_quadro_sem_a_coluna(self) -> None:
        """Robustez: quadros de outra origem não devem quebrar a figura."""
        outro = pd.DataFrame({"ica": [50.0, 70.0]})
        assert len(only_audited(outro)) == 2

    def test_taxa_de_perda_e_preservada_no_dataset(self, scan_com_perda: ScanResult) -> None:
        """A perda precisa continuar visível: é limitação a declarar no artigo."""
        # abs, e não rel: loss_rate é arredondada a 4 casas na origem.
        assert scan_com_perda.loss_rate == pytest.approx(2 / 3, abs=1e-4)


class TestMontagemDoDataset:
    def test_quadro_de_achados_tem_as_tres_camadas(self, scan_com_perda: ScanResult) -> None:
        achados = build_findings_frame([scan_com_perda])
        for coluna in ("regra_id", "criterio_principal", "risco_juridico", "peso_juridico"):
            assert coluna in achados.columns

    def test_violacao_distingue_veredito(self, scan_com_perda: ScanResult) -> None:
        achados = build_findings_frame([scan_com_perda])
        assert achados["violacao"].sum() < len(achados)
        assert (achados.loc[achados["veredito"] == "incomplete", "violacao"] == False).all()  # noqa: E712

    def test_risco_juridico_tem_ordem_natural(self, scan_com_perda: ScanResult) -> None:
        """Permite ordenar e plotar sem reespecificar a ordem a cada uso."""
        achados = build_findings_frame([scan_com_perda])
        categorias = list(achados["risco_juridico"].cat.categories)
        assert categorias == ["baixo", "moderado", "alto", "critico"]

    def test_prevalencia_usa_paginas_como_denominador(self, scan_com_perda: ScanResult) -> None:
        """Prevalência responde 'a barreira é estrutural?', não 'quantas há?'."""
        achados = build_findings_frame([scan_com_perda])
        prev = criterion_prevalence(achados)
        assert not prev.empty
        assert (prev["prevalencia"] <= 1.0).all()

    def test_perfil_de_exclusao_agrega_por_grupo(self, scan_com_perda: ScanResult) -> None:
        perfil = exclusion_profile(build_findings_frame([scan_com_perda]))
        assert not perfil.empty
        assert list(perfil.columns) == ["grupo", "ocorrencias", "achados"]
        assert perfil["ocorrencias"].is_monotonic_decreasing

    def test_quadro_vazio_nao_quebra(self) -> None:
        assert build_findings_frame([]).empty
        assert criterion_prevalence(pd.DataFrame()).empty
