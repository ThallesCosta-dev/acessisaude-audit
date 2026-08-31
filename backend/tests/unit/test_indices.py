"""Comportamento dos índices agregados.

Os índices são a contribuição metodológica do projeto. Cada teste aqui fixa uma
propriedade que o artigo afirmará sobre eles — em especial as três que os
distinguem de uma contagem simples de violações.
"""

from __future__ import annotations

import pytest
from tests.conftest import make_finding

from acessisaude_audit.domain.models import (
    Impact,
    NetworkMetrics,
    Outcome,
    PageAudit,
    PageStatus,
    ScanResult,
    Viewport,
)
from acessisaude_audit.domain.scoring import (
    ScoringParameters,
    automatable_criteria_ids,
    score_page,
    score_scan,
    summarize_by_group,
)

VP = Viewport(name="desktop-1366", width=1366, height=768)


def page_with(
    *findings, critical: bool = False, network: NetworkMetrics | None = None
) -> PageAudit:
    """Página sintética com os achados informados."""
    return PageAudit(
        url="http://exemplo.test/",
        viewport=VP,
        findings=list(findings),
        is_critical_path=critical,
        network=network or NetworkMetrics(),
    )


class TestIndiceDeConformidade:
    def test_pagina_sem_violacao_pontua_100(self) -> None:
        assert score_page(page_with()).conformance_index == 100.0

    def test_violacao_derruba_o_indice(self) -> None:
        score = score_page(page_with(make_finding(criteria=["1.4.3"])))
        assert 0 < score.conformance_index < 100

    def test_criterio_critico_derruba_mais_que_criterio_de_risco_baixo(self) -> None:
        """A ponderação por risco jurídico é o que distingue o ICA de uma razão simples.

        Violar 2.1.1 (teclado, crítico) impede o uso; violar 3.1.2 (idioma de
        partes, baixo) degrada a pronúncia. Um índice que os tratasse igual
        seria inútil para priorizar correção.
        """
        critico = score_page(page_with(make_finding(criteria=["2.1.1"])))
        baixo = score_page(page_with(make_finding(criteria=["3.1.2"])))
        assert critico.conformance_index < baixo.conformance_index

    def test_denominador_usa_apenas_criterios_automatizaveis(self) -> None:
        """Reportar conformidade sobre critérios não verificáveis seria indefensável."""
        score = score_page(page_with())
        assert score.criteria_evaluated == len(automatable_criteria_ids())
        assert score.criteria_evaluated < 50

    def test_cobertura_e_reportada_junto_do_indice(self) -> None:
        score = score_page(page_with())
        assert 0 < score.coverage < 1
        assert score.coverage == pytest.approx(score.criteria_evaluated / 50)


class TestIndiceDeAtrito:
    def test_sem_achados_o_atrito_e_zero(self) -> None:
        assert score_page(page_with()).friction_index == 0.0

    def test_atrito_cresce_com_a_gravidade(self) -> None:
        leve = score_page(page_with(make_finding(impact=Impact.MINOR, criteria=["3.1.2"])))
        grave = score_page(page_with(make_finding(impact=Impact.CRITICAL, criteria=["2.1.1"])))
        assert grave.friction_index > leve.friction_index

    def test_ocorrencias_repetidas_tem_retorno_decrescente(self) -> None:
        """Correção do viés de template.

        400 links sem nome acessível são UM defeito de componente, não 400
        problemas independentes. O amortecimento logarítmico garante que o
        centésimo elemento contribua menos que o segundo.
        """
        uma = score_page(page_with(make_finding(occurrences=1))).friction_index
        dez = score_page(page_with(make_finding(occurrences=10))).friction_index
        cem = score_page(page_with(make_finding(occurrences=100))).friction_index

        assert uma < dez < cem
        # O salto de 10→100 é menor que o de 1→10, apesar de ser 10× mais elementos.
        assert (cem - dez) < (dez - uma)

    def test_indice_permanece_limitado_a_100(self) -> None:
        """Saturação exponencial: nenhuma página pode 'estourar' a escala."""
        catastrofe = page_with(
            *[
                make_finding(
                    rule_id=f"r{i}", criteria=["2.1.1"], impact=Impact.CRITICAL, occurrences=50
                )
                for i in range(40)
            ]
        )
        score = score_page(catastrofe)
        assert 90 < score.friction_index <= 100

    def test_fluxo_essencial_agrava_o_atrito(self) -> None:
        """A mesma barreira pesa mais na tela de confirmação de consulta."""
        comum = score_page(page_with(make_finding(), critical=False))
        essencial = score_page(page_with(make_finding(), critical=True))
        assert essencial.friction_index > comum.friction_index


class TestBarreiraAbsoluta:
    def test_violacao_critica_sinaliza_barreira_absoluta(self) -> None:
        score = score_page(page_with(make_finding(criteria=["2.1.1"])))
        assert score.absolute_barrier is True

    def test_violacoes_leves_nao_sinalizam_barreira_absoluta(self) -> None:
        score = score_page(page_with(make_finding(criteria=["3.1.2"], impact=Impact.MINOR)))
        assert score.absolute_barrier is False

    def test_barreira_absoluta_independe_do_indice_de_conformidade(self) -> None:
        """Um portal pode ter alta conformidade e ainda ser inutilizável.

        Esta é a razão de existir do sinalizador: nenhum índice contínuo captura
        a diferença entre 'difícil' e 'impossível'.
        """
        score = score_page(page_with(make_finding(criteria=["2.1.1"], occurrences=1)))
        assert score.conformance_index > 80
        assert score.absolute_barrier is True


class TestExposicaoJuridica:
    def test_risco_baixo_nao_gera_exposicao(self) -> None:
        """Passivo jurídico não se mede por irregularidade formal."""
        score = score_page(page_with(make_finding(criteria=["3.1.2"])))
        assert score.legal_exposure_index == 0.0

    def test_risco_alto_gera_exposicao(self) -> None:
        score = score_page(page_with(make_finding(criteria=["1.4.3"])))
        assert score.legal_exposure_index > 0


class TestSeparacaoEntreVeredito:
    def test_incompletos_nao_contam_como_violacao(self) -> None:
        """A distinção entre violação e indício é o núcleo da honestidade do método."""
        score = score_page(page_with(make_finding(outcome=Outcome.INCOMPLETE, impact=None)))
        assert score.violations == 0
        assert score.incomplete == 1
        assert score.conformance_index == 100.0
        assert score.friction_index == 0.0


class TestCustoDeDados:
    def test_converte_peso_em_custo_e_fracao_de_franquia(self) -> None:
        params = ScoringParameters(price_per_mb_brl=0.10, franchise_mb=2048.0)
        page = page_with(network=NetworkMetrics(total_bytes=5 * 1024 * 1024))
        cost = score_page(page, params).data_cost

        assert cost is not None
        assert cost.total_mb == pytest.approx(5.0)
        assert cost.cost_brl == pytest.approx(0.50)
        assert cost.franchise_share_pct == pytest.approx(0.2441, abs=1e-3)
        assert cost.is_heavy is True

    def test_pagina_leve_nao_e_marcada_como_onerosa(self) -> None:
        page = page_with(network=NetworkMetrics(total_bytes=512 * 1024))
        cost = score_page(page, ScoringParameters(heavy_page_mb=2.0)).data_cost
        assert cost is not None and cost.is_heavy is False


class TestAgregacaoDeVarredura:
    def test_paginas_em_erro_ficam_fora_do_calculo(self, sample_scan: ScanResult) -> None:
        """Página que não carregou tem zero achados — incluí-la inflaria o ICA."""
        score = score_scan(sample_scan)
        assert score.violations == len(sample_scan.pages[0].violations)
        assert sample_scan.loss_rate == pytest.approx(0.5)

    def test_atrito_e_normalizado_por_pagina(self) -> None:
        """Sem normalização, varrer mais páginas pioraria o índice do portal."""
        uma = ScanResult(target_id="t", pages=[page_with(make_finding())])
        cinco = ScanResult(target_id="t", pages=[page_with(make_finding()) for _ in range(5)])
        assert score_scan(uma).friction_index == pytest.approx(score_scan(cinco).friction_index)

    def test_perfil_de_exclusao_ordena_por_ocorrencias(self, sample_scan: ScanResult) -> None:
        perfil = summarize_by_group(score_scan(sample_scan))
        assert perfil
        contagens = [n for _, n in perfil]
        assert contagens == sorted(contagens, reverse=True)


class TestCalibracaoDoAtrito:
    """A escala do IAN precisa discriminar na faixa que interessa.

    Um índice que satura cedo deixa de distinguir "ruim" de "inutilizável" —
    exatamente a distinção que sustenta a priorização de correções e a
    comparação entre portais no artigo. Estes testes travam a calibração
    documentada em :class:`ScoringParameters`, de modo que alterá-la exija
    alterar o teste, e portanto assumir a mudança.
    """

    def test_uma_falha_seria_de_risco_alto_fica_na_faixa_intermediaria(self) -> None:
        """Caso de referência da docstring: deve pontuar próximo de 25."""
        score = score_page(
            page_with(make_finding(criteria=["1.4.3"], impact=Impact.SERIOUS, occurrences=1))
        )
        assert 20 <= score.friction_index <= 30

    def test_falha_leve_isolada_pontua_baixo(self) -> None:
        score = score_page(
            page_with(make_finding(criteria=["3.1.2"], impact=Impact.MINOR, occurrences=1))
        )
        assert 0 < score.friction_index < 10

    def test_barreira_absoluta_multipla_pontua_alto(self) -> None:
        score = score_page(
            page_with(
                *[
                    make_finding(
                        rule_id=f"r{i}",
                        criteria=["2.1.1"],
                        impact=Impact.CRITICAL,
                        occurrences=5,
                    )
                    for i in range(3)
                ]
            )
        )
        assert score.friction_index > 80

    def test_escala_discrimina_entre_os_casos_de_referencia(self) -> None:
        """Os três casos precisam ficar bem separados, e não colados no teto."""
        leve = score_page(
            page_with(make_finding(criteria=["3.1.2"], impact=Impact.MINOR))
        ).friction_index
        serio = score_page(
            page_with(make_finding(criteria=["1.4.3"], impact=Impact.SERIOUS))
        ).friction_index
        critico = score_page(
            page_with(
                *[
                    make_finding(
                        rule_id=f"r{i}", criteria=["2.1.1"], impact=Impact.CRITICAL, occurrences=5
                    )
                    for i in range(3)
                ]
            )
        ).friction_index

        assert serio - leve > 10, "leve e sério devem ficar claramente distintos"
        assert critico - serio > 40, "sério e crítico devem ficar claramente distintos"


class TestParametrosDeCustoColetados:
    """Trava os valores coletados de preço, franquia e limiar de peso.

    Os três deixaram de ser ilustrativos e passaram a ser dados publicados,
    datados e citados no artigo (ver ``docs/metodologia/parametros-de-custo.md``).
    Alterá-los muda todo número monetário publicado, e por isso precisa exigir a
    alteração deste teste — e portanto a assunção consciente da mudança.
    """

    def test_preco_e_o_do_plano_pre_pago_de_entrada(self) -> None:
        """R$ 3,00 por GiB — Claro Prezão R$ 15,00 / 5 GB / 15 dias."""
        params = ScoringParameters()
        assert params.price_per_mb_brl * 1024 == pytest.approx(3.00)

    def test_preco_e_exatamente_representavel(self) -> None:
        """3/1024 é fração diádica: sem erro de arredondamento na agregação.

        Somar milhares de páginas com um preço não representável acumularia
        deriva numérica em um valor que vai para o artigo.
        """
        params = ScoringParameters()
        assert params.price_per_mb_brl == 3.0 / 1024
        assert params.price_per_mb_brl * 1024 * 1024 == 3.0 * 1024

    def test_franquia_corresponde_a_duas_recargas(self) -> None:
        """10 GiB/mês = 2 × 5 GiB do ciclo de 15 dias."""
        assert ScoringParameters().franchise_mb == 2 * 5 * 1024

    def test_limiar_de_peso_e_a_mediana_movel_publicada(self) -> None:
        """2,5 MiB — HTTP Archive Web Almanac 2025, coleta de julho de 2025."""
        assert ScoringParameters().heavy_page_mb == pytest.approx(2.5, abs=0.05)

    def test_parametros_sao_conservadores_frente_a_anatel(self) -> None:
        """O preço adotado fica abaixo do preço efetivo oficial.

        A Anatel reporta R$ 5,46/GB no 1T2026 (receita ÷ dado consumido). Adotar
        a taxa marginal anunciada, menor, faz a estimativa de custo errar para
        menos — direção segura para uma afirmação publicável.
        """
        preco_anatel_por_gib = 5.46
        preco_adotado_por_gib = ScoringParameters().price_per_mb_brl * 1024
        assert preco_adotado_por_gib < preco_anatel_por_gib

    def test_custo_de_pagina_tipica_permanece_legivel(self) -> None:
        """O custo precisa sobreviver ao arredondamento da persistência.

        Com o preço real, uma página mediana custa milésimos de real. Se o
        arredondamento colapsasse o valor em zero, o indicador se tornaria
        inútil — foi o motivo de elevar a precisão de 4 para 6 casas.
        """
        pagina = page_with(network=NetworkMetrics(total_bytes=int(2.5 * 1024 * 1024)))
        cost = score_page(pagina).data_cost
        assert cost is not None
        assert cost.cost_brl > 0
        assert cost.cost_brl == pytest.approx(0.007324, abs=1e-6)


class TestParametrosSaoExplicitos:
    def test_parametros_sao_serializaveis_para_o_snapshot(self) -> None:
        """Nenhum número publicável pode depender de constante não declarada."""
        params = ScoringParameters()
        dump = params.as_dict()
        assert set(dump) == {
            "friction_kappa",
            "critical_path_multiplier",
            "price_per_mb_brl",
            "franchise_mb",
            "heavy_page_mb",
        }
        assert all(isinstance(v, float) for v in dump.values())


class TestAusenciaDeObservacao:
    """Perda total de páginas não pode ser lida como conformidade.

    Este é o defeito que motivou o contrato nulo, e ele apareceu em coleta
    real: em 25/08/2026 uma falha de DNS do coletor derrubou as 20 páginas dos
    cinco alvos, e a versão anterior reportou ICA 100,0 para todos — o número
    máximo da escala, indistinguível de um portal impecável. Como o ICA é a
    razão entre critérios não violados e critérios avaliados, zero violação
    sobre zero observação produzia o numerador cheio.

    A correção é de tipo, não de apresentação: os quatro índices passam a
    aceitar nulo, e nulo significa *sem veredito* — nem conformidade, nem não
    conformidade. Os campos descritivos (cobertura, contagens, taxa de perda)
    continuam preenchidos, porque descrevem a tentativa, e é a tentativa que
    ficou registrada.
    """

    def _scan_totalmente_perdido(self) -> ScanResult:
        return ScanResult(
            target_id="t",
            pages=[
                PageAudit(
                    url=f"http://exemplo.test/{i}",
                    viewport=VP,
                    status=PageStatus.NAVIGATION_ERROR,
                    error="net::ERR_NAME_NOT_RESOLVED",
                )
                for i in range(4)
            ],
        )

    def test_sem_pagina_auditada_nao_ha_observacao(self) -> None:
        score = score_scan(self._scan_totalmente_perdido())
        assert score.observed is False

    def test_sem_observacao_os_quatro_indices_sao_nulos(self) -> None:
        """Nulo, e não zero: zero é um veredito, e não há veredito a dar."""
        score = score_scan(self._scan_totalmente_perdido())
        assert score.conformance_index is None
        assert score.friction_index is None
        assert score.legal_exposure_index is None
        assert score.absolute_barrier is None

    def test_perda_total_nunca_pontua_como_conformidade_perfeita(self) -> None:
        """A regressão específica: 20 páginas em erro reportavam ICA 100,0."""
        assert score_scan(self._scan_totalmente_perdido()).conformance_index != 100.0

    def test_a_tentativa_permanece_descrita(self) -> None:
        """Sem veredito não é sem registro — a perda precisa ser auditável."""
        scan = self._scan_totalmente_perdido()
        score = score_scan(scan)
        assert scan.loss_rate == 1.0
        assert score.violations == 0
        assert score.coverage > 0

    def test_uma_unica_pagina_auditada_ja_produz_veredito(self) -> None:
        """A fronteira é a existência de observação, não a sua quantidade.

        Uma varredura com perda parcial continua pontuando: o que ela mede é
        parcial, e a taxa de perda — reportada ao lado — é o que qualifica a
        leitura.
        """
        scan = ScanResult(
            target_id="t",
            pages=[
                page_with(make_finding(criteria=["1.4.3"])),
                PageAudit(
                    url="http://exemplo.test/x", viewport=VP, status=PageStatus.NAVIGATION_ERROR
                ),
            ],
        )
        score = score_scan(scan)
        assert score.observed is True
        assert score.conformance_index is not None
        assert scan.loss_rate == 0.5
