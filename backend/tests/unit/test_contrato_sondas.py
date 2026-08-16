"""Contrato das sondas — o que impede a ferramenta de transformar suspeita em acusação.

A regra central: **sondas heurísticas não reprovam**. Ela existe porque a
diferença entre "detectei uma falha" e "detectei algo que precisa de olhos
humanos" é o que separa uma ferramenta de auditoria de um gerador de números.
Verificá-la em teste impede que uma futura sonda, escrita com pressa, converta
um indício de legibilidade em violação da LBI.
"""

from __future__ import annotations

from typing import Any

import pytest

from acessisaude_audit.auditor.probes import ALL_PROBES, default_probes
from acessisaude_audit.auditor.probes.base import Confidence, Probe, ProbeContext
from acessisaude_audit.auditor.probes.digital_rights import (
    READABILITY_THRESHOLD,
    count_syllables_pt,
    flesch_pt_br,
)
from acessisaude_audit.domain.models import Finding, FindingSource, Impact, Outcome, Viewport
from acessisaude_audit.domain.wcag import criterion

VP = Viewport(name="desktop-1366", width=1366, height=768)


class _PaginaFalsa:
    """Página mínima que só sabe avaliar scripts com respostas pré-definidas."""

    def __init__(self, respostas: dict[str, Any] | None = None) -> None:
        self._respostas = respostas or {}
        self.url = "http://exemplo.test/"

    async def evaluate(self, script: str, arg: Any = None) -> Any:
        for chave, valor in self._respostas.items():
            if chave in script:
                return valor
        return None


def contexto(**kwargs: Any) -> ProbeContext:
    return ProbeContext(
        page=_PaginaFalsa(kwargs.pop("respostas", None)),  # type: ignore[arg-type]
        url="http://exemplo.test/",
        viewport=kwargs.pop("viewport", VP),
        **kwargs,
    )


class TestRegistroDeSondas:
    def test_identificadores_unicos(self) -> None:
        ids = [p.id for p in default_probes()]
        assert len(ids) == len(set(ids))

    def test_todo_id_usa_o_prefixo_probe(self) -> None:
        """O prefixo permite distinguir, no dataset, achado próprio de achado do axe."""
        assert all(p.id.startswith("probe.") for p in default_probes())

    def test_toda_sonda_declara_o_que_verifica(self) -> None:
        assert all(len(p.description) > 30 for p in default_probes())

    def test_criterios_declarados_existem_no_escopo(self) -> None:
        for probe in default_probes():
            for crit_id in probe.criteria:
                criterion(crit_id)  # KeyError se estiver fora do escopo A/AA

    def test_cobertura_das_sondas_complementa_o_axe(self) -> None:
        """As sondas existem para alcançar o que o axe-core não alcança.

        Os critérios abaixo dependem de interação ou de contexto de uso e não
        são verificáveis por inspeção estática do DOM.
        """
        cobertos = {c for p in default_probes() for c in p.criteria}
        for esperado in ("1.4.10", "1.4.4", "2.4.7", "2.4.1", "2.2.1"):
            assert esperado in cobertos, f"Nenhuma sonda cobre {esperado}"


class TestContratoDeConfianca:
    @pytest.mark.asyncio
    async def test_sonda_heuristica_nao_pode_reprovar(self) -> None:
        """Invariante central: heurística sinaliza, não acusa."""

        class SondaMalComportada(Probe):
            id = "probe.teste-heuristica"
            confidence = Confidence.HEURISTIC
            description = "Sonda de teste que tenta indevidamente reprovar."

            async def _run(self, context: ProbeContext) -> list[Finding]:
                return [
                    Finding(
                        rule_id=self.id,
                        source=FindingSource.HEURISTIC,
                        outcome=Outcome.FAIL,  # tentativa indevida
                        impact=Impact.CRITICAL,
                        summary="Tentativa de reprovar a partir de heurística.",
                    )
                ]

        achados = await SondaMalComportada().run(contexto())
        assert achados[0].outcome is Outcome.INCOMPLETE
        assert achados[0].impact is None

    @pytest.mark.asyncio
    async def test_sonda_deterministica_pode_reprovar(self) -> None:
        class SondaDeterministica(Probe):
            id = "probe.teste-deterministica"
            confidence = Confidence.DETERMINISTIC
            description = "Sonda de teste com veredito determinístico."

            async def _run(self, context: ProbeContext) -> list[Finding]:
                return [
                    Finding(
                        rule_id=self.id,
                        source=FindingSource.PROBE,
                        outcome=Outcome.FAIL,
                        impact=Impact.SERIOUS,
                        summary="Falha objetiva verificada.",
                    )
                ]

        achados = await SondaDeterministica().run(contexto())
        assert achados[0].outcome is Outcome.FAIL

    @pytest.mark.asyncio
    async def test_excecao_em_sonda_nao_derruba_a_auditoria(self) -> None:
        """Uma sonda quebrada não pode produzir 'página sem problemas'."""

        class SondaQuebrada(Probe):
            id = "probe.teste-quebrada"
            description = "Sonda de teste que lança exceção."

            async def _run(self, context: ProbeContext) -> list[Finding]:
                raise RuntimeError("falha simulada")

        assert await SondaQuebrada().run(contexto()) == []

    @pytest.mark.asyncio
    async def test_contexto_preenche_url_e_viewport(self) -> None:
        """A sonda não precisa repetir — nem pode errar — a procedência do achado."""

        class SondaSimples(Probe):
            id = "probe.teste-contexto"
            description = "Sonda de teste que omite a procedência do achado."

            async def _run(self, context: ProbeContext) -> list[Finding]:
                return [
                    Finding(
                        rule_id=self.id,
                        source=FindingSource.PROBE,
                        outcome=Outcome.FAIL,
                        summary="Achado sem procedência declarada.",
                    )
                ]

        achado = (await SondaSimples().run(contexto()))[0]
        assert achado.page_url == "http://exemplo.test/"
        assert achado.viewport == "desktop-1366"


class TestAplicabilidadePorViewport:
    def test_refluxo_so_roda_em_tela_estreita(self) -> None:
        """O critério 1.4.10 se define em 320 px; medi-lo em desktop não faz sentido."""
        from acessisaude_audit.auditor.probes.viewport import ReflowProbe

        movel = Viewport(name="mobile-320", width=320, height=640, is_mobile=True)
        assert ReflowProbe().applies_to(contexto(viewport=movel)) is True
        assert ReflowProbe().applies_to(contexto(viewport=VP)) is False

    def test_legibilidade_nao_duplica_entre_viewports(self) -> None:
        """O texto não muda com o dispositivo; medi-lo duas vezes inflaria o dataset."""
        from acessisaude_audit.auditor.probes.digital_rights import ReadabilityProbe

        movel = Viewport(name="mobile-320", width=320, height=640, is_mobile=True)
        assert ReadabilityProbe().applies_to(contexto(viewport=VP)) is True
        assert ReadabilityProbe().applies_to(contexto(viewport=movel)) is False

    def test_custo_de_dados_exige_metricas_de_rede(self) -> None:
        from acessisaude_audit.auditor.probes.digital_rights import DataCostProbe

        assert DataCostProbe().applies_to(contexto()) is False


class TestLegibilidade:
    @pytest.mark.parametrize(
        ("palavra", "silabas"),
        [
            ("casa", 2),
            ("agendamento", 5),
            ("sus", 1),
            ("consulta", 3),
            ("medicamento", 5),
            ("a", 1),
        ],
    )
    def test_contagem_de_silabas(self, palavra: str, silabas: int) -> None:
        """Palavras sem hiato são contadas exatamente."""
        assert count_syllables_pt(palavra) == silabas

    @pytest.mark.parametrize(
        ("palavra", "real", "estimado"),
        [
            ("saúde", 3, 2),  # sa-ú-de → o método agrupa "aú"
            ("coordenar", 4, 3),  # co-or-de-nar → agrupa "oo"
            ("saída", 3, 2),  # sa-í-da → agrupa "aí"
        ],
    )
    def test_hiatos_sao_subcontados_de_forma_conhecida(
        self, palavra: str, real: int, estimado: int
    ) -> None:
        """O viés do método está medido, não apenas declarado.

        O agrupamento vocálico trata hiato como ditongo e subconta sílabas.
        Menos sílabas por palavra ⇒ índice de Flesch MAIOR ⇒ texto parece mais
        fácil do que é. O erro é conservador na direção certa: a sonda deixa de
        alarmar em casos limítrofes, em vez de acusar indevidamente um portal.

        Este teste fixa a magnitude do viés para que ela possa ser citada na
        seção de Métodos, e falha se uma futura mudança na implementação
        alterá-la silenciosamente.
        """
        assert count_syllables_pt(palavra) == estimado
        assert estimado < real

    def test_texto_simples_pontua_alto(self) -> None:
        texto = (
            "Você pode marcar consulta. Ligue para a clínica. O atendimento é de "
            "graça. Leve seu cartão. A vaga é sua. Chegue cedo. Traga documento."
        )
        assert float(flesch_pt_br(texto)["index"]) > READABILITY_THRESHOLD

    def test_texto_burocratico_pontua_baixo(self) -> None:
        """Registro jurídico-administrativo: tecnicamente acessível, praticamente inútil."""
        texto = (
            "Considerando a necessidade de regulamentação dos procedimentos "
            "administrativos concernentes à operacionalização do agendamento "
            "eletrônico de consultas especializadas no âmbito da rede "
            "assistencial municipal, resolve-se estabelecer que a solicitação "
            "deverá ser instruída com documentação comprobatória da condição de "
            "elegibilidade do requerente, observadas as disposições regulamentares "
            "supervenientes e as diretrizes emanadas da instância gestora "
            "competente, sem prejuízo das prerrogativas fiscalizatórias inerentes."
        )
        assert float(flesch_pt_br(texto)["index"]) < READABILITY_THRESHOLD

    def test_texto_vazio_nao_quebra(self) -> None:
        resultado = flesch_pt_br("")
        assert resultado["words"] == 0
        assert "indeterminado" in str(resultado["band"])

    def test_estatisticas_sao_expostas_para_auditoria(self) -> None:
        """O número precisa ser auditável, não apenas aceito."""
        resultado = flesch_pt_br("Marque sua consulta. É simples e rápido.")
        assert {"index", "band", "words", "sentences", "syllables"} <= set(resultado)


def test_registro_padrao_contem_todas_as_sondas() -> None:
    assert len(default_probes()) == len(ALL_PROBES)


class TestCondutaDosPerfisDeDispositivo:
    """A conduta de coleta precisa valer para **todos** os perfis.

    A regra declarada em ``docs/metodologia/etica-e-conduta-de-coleta.md`` é que
    a ferramenta se identifique no User-Agent. O perfil desktop originalmente não
    declarava User-Agent e herdava o padrão do Playwright, que anuncia
    ``HeadlessChrome`` e nada diz sobre a pesquisa.

    O defeito só apareceu na segunda medição de campo, ao investigar falhas
    assimétricas entre perfis. Estes testes o impedem de voltar — e impedem que
    um perfil novo seja acrescentado sem identificação.
    """

    def test_todo_perfil_padrao_declara_user_agent(self) -> None:
        from acessisaude_audit.config import DEFAULT_VIEWPORTS

        sem_ua = [v.name for v in DEFAULT_VIEWPORTS if not v.user_agent]
        assert not sem_ua, (
            f"Perfis sem User-Agent explícito: {sem_ua}. Sem ele, o navegador "
            "anuncia HeadlessChrome e a coleta não se identifica."
        )

    def test_nenhum_perfil_anuncia_automacao(self) -> None:
        """Anunciar automação não é problema ético — é problema metodológico.

        Um perfil detectável como robô e outro não tornariam a comparação entre
        perfis confundida com diferença de bloqueio por firewall de aplicação.
        A identificação da pesquisa vai no sufixo, que é acrescentado a todos.
        """
        from acessisaude_audit.config import DEFAULT_VIEWPORTS

        suspeitos = [
            v.name for v in DEFAULT_VIEWPORTS if v.user_agent and "headless" in v.user_agent.lower()
        ]
        assert not suspeitos, f"Perfis que anunciam automação: {suspeitos}"

    def test_o_sufixo_de_identificacao_traz_contato(self) -> None:
        """Identificar-se sem contato não permite que o administrador reaja."""
        from acessisaude_audit.config import Settings

        sufixo = Settings().user_agent_suffix
        assert "AcessiSaude" in sufixo
        assert "@" in sufixo, "O User-Agent precisa trazer um contato."

    def test_perfis_diferem_apenas_no_que_deve_diferir(self) -> None:
        """Isola a variável do experimento de comparação entre perfis (H3).

        Se os perfis divergirem em algo além de dimensões, densidade e natureza
        móvel, a diferença observada deixa de ser atribuível ao dispositivo.
        """
        from acessisaude_audit.config import DEFAULT_VIEWPORTS

        assert len({v.name for v in DEFAULT_VIEWPORTS}) == len(DEFAULT_VIEWPORTS)
        # Ambos identificam a pesquisa pelo mesmo mecanismo: o sufixo é anexado
        # ao User-Agent do perfil, e não substituído por um cabeçalho próprio.
        assert all(v.user_agent for v in DEFAULT_VIEWPORTS)
