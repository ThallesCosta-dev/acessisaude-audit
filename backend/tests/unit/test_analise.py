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
    build_scans_frame,
    criterion_prevalence,
    exclusion_profile,
)
from acessisaude_audit.analysis.figures import figure_daily_series, only_audited  # noqa: E402

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
    """Duas defesas contra o mesmo erro, em camadas diferentes.

    O defeito original: uma página que não carregou não produz achado nenhum, e
    o índice lia zero violação como conformidade — atribuindo ICA 100 a um
    endereço que sequer respondeu. A defesa de raiz está no domínio, que agora
    devolve nulo sem observação; ``only_audited`` permanece como segunda linha,
    porque a análise também recebe quadros vindos de coletas antigas, gravadas
    sob o contrato anterior.
    """

    def test_pagina_em_erro_nao_recebe_indice(self, scan_com_perda: ScanResult) -> None:
        """A correção de raiz: sem carregamento, sem veredito.

        Não era bug de aritmética — uma página sem achados É conforme sob os
        critérios verificados. O erro estava em pontuar o que não foi medido.
        """
        paginas = build_pages_frame([scan_com_perda])
        falhas = paginas[~paginas["auditada"]]
        assert len(falhas) == 2
        assert falhas["ica"].isna().all()

    def test_only_audited_remove_as_paginas_em_erro(self, scan_com_perda: ScanResult) -> None:
        paginas = build_pages_frame([scan_com_perda])
        assert len(paginas) == 3
        assert len(only_audited(paginas)) == 1

    def test_nulo_nao_e_confundido_com_zero_em_agregacao(self, scan_com_perda: ScanResult) -> None:
        """O nulo tem de sobreviver ao pandas, e não virar zero na média.

        ``Series.mean`` ignora ``NaN`` por padrão, o que é o comportamento
        desejado; o risco seria um ``fillna(0)`` em algum ponto do caminho,
        que puxaria a média para baixo e trocaria uma falha de coleta por um
        portal ruim. A asserção fixa que a agregação de três páginas, das
        quais duas não carregaram, é a da única que carregou.
        """
        paginas = build_pages_frame([scan_com_perda])
        assert paginas["ica"].count() == 1
        assert paginas["ica"].mean() == pytest.approx(only_audited(paginas)["ica"].mean())

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


class TestFiguraDaSerieDiaria:
    """A figura do braço longitudinal não pode inventar continuidade.

    O risco específico: matplotlib desenha uma linha reta entre dois pontos
    válidos separados por um ``NaN`` se o valor ausente for removido antes de
    plotar. Isso emendaria visualmente os dois lados de um dia sem observação,
    desenhando exatamente a continuidade que a ADR 0010 existe para negar.
    """

    @pytest.fixture
    def serie(self, sample_page: PageAudit) -> pd.DataFrame:
        """Três dias de um alvo, o do meio sem nenhuma página auditada."""
        from datetime import datetime

        scans = []
        for i, perdido in enumerate([False, True, False]):
            paginas = (
                [PageAudit(url="http://exemplo.test/x", viewport=VP, status=PageStatus.TIMEOUT)]
                if perdido
                else [sample_page]
            )
            scans.append(
                ScanResult(
                    target_id="alvo",
                    target_name="Alvo",
                    started_at=datetime(2026, 8, 20 + i, 12, 20),
                    pages=paginas,
                )
            )
        return build_scans_frame(scans)

    def test_o_dia_sem_veredito_fica_ausente_na_serie(self, serie: pd.DataFrame) -> None:
        assert list(serie["observado"]) == [True, False, True]
        assert serie["ica"].isna().tolist() == [False, True, False]

    def test_a_linha_e_interrompida_e_nao_interpolada(self, serie: pd.DataFrame) -> None:
        fig = figure_daily_series(serie)
        try:
            (linha,) = fig.axes[0].get_lines()
            ys = linha.get_ydata()
            assert len(ys) == 3
            # O ponto do meio precisa chegar ao matplotlib como ausente: é o que
            # faz a linha quebrar em vez de atravessar a lacuna.
            assert ys[1] != ys[1]  # NaN
        finally:
            import matplotlib.pyplot as plt

            plt.close(fig)
