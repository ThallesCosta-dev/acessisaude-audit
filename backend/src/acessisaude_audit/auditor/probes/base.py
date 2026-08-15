"""Contrato das sondas de auditoria.

Uma **sonda** é uma verificação própria do projeto, executada sobre a página já
carregada, que investiga algo que o axe-core não cobre ou cobre de forma
insuficiente para o recorte deste estudo.

Por que sondas existem
----------------------
O axe-core é excelente no que faz — verificação estática do DOM contra regras
determinísticas — e deliberadamente conservador: ele só reprova quando tem
certeza. Isso o torna cego a três classes de barreira que são centrais aqui:

1. **Barreiras que só aparecem em condição de uso.** Refluxo em 320 px, foco
   visível, armadilha de teclado — exigem interagir com a página, não apenas
   lê-la.
2. **Barreiras de custo.** O peso em dados móveis não viola critério WCAG
   algum, mas exclui materialmente o usuário periférico do serviço de saúde.
3. **Barreiras de compreensão.** Texto oficial em registro jurídico-burocrático
   é tecnicamente acessível e praticamente inútil para grande parte da
   população usuária do SUS.

Disciplina metodológica
-----------------------
Toda sonda declara em qual :class:`Confidence` opera. Sondas ``HEURISTIC``
**nunca** produzem :attr:`Outcome.FAIL` — apenas ``INCOMPLETE``, sinalizando
revisão humana. Essa regra é verificada em teste
(``tests/unit/test_probe_contract.py``) e é o que impede a ferramenta de
transformar suspeita em acusação.
"""

from __future__ import annotations

import abc
from enum import StrEnum
from typing import Any

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page

from acessisaude_audit.domain.mapping import mapping_for
from acessisaude_audit.domain.models import Finding, Outcome, Viewport
from acessisaude_audit.domain.wcag import DeficiencyGroup, criterion
from acessisaude_audit.logging_setup import get_logger

__all__ = [
    "Confidence",
    "Probe",
    "ProbeContext",
    "affected_groups",
    "help_url_for",
    "remediation_for",
]

logger = get_logger(__name__)


def remediation_for(criterion_id: str) -> str:
    """Conduta corretiva registrada na matriz jurídica para o critério.

    Sondas usam este acesso em vez de escreverem a própria recomendação, para
    que a orientação entregue ao gestor seja idêntica venha ela do axe-core ou
    de uma verificação própria.
    """
    m = mapping_for(criterion_id)
    return m.remediation if m else ""


def affected_groups(criterion_id: str) -> list[DeficiencyGroup]:
    """Grupos impactados pela violação do critério, em ordem estável."""
    try:
        return sorted(criterion(criterion_id).affects, key=lambda g: g.value)
    except KeyError:  # pragma: no cover
        return []


def help_url_for(criterion_id: str) -> str | None:
    """URL do *Understanding WCAG* para o critério."""
    try:
        return criterion(criterion_id).url
    except KeyError:  # pragma: no cover
        return None


class Confidence(StrEnum):
    """Grau de certeza que a sonda é capaz de oferecer."""

    DETERMINISTIC = "deterministic"
    """A verificação é objetiva e reprodutível: o veredito pode ser FAIL."""

    HEURISTIC = "heuristic"
    """A verificação é indiciária: o veredito máximo é INCOMPLETE."""


class ProbeContext:
    """Tudo o que uma sonda precisa saber sobre a página em exame.

    Attributes:
        page: A página carregada, para consulta e interação.
        url: URL efetiva da página.
        viewport: Perfil de dispositivo em uso — várias sondas só fazem sentido
            em um dos perfis (refluxo em 320 px, por exemplo).
        is_critical_path: Se a página integra fluxo essencial declarado.
        network: Métricas de tráfego já coletadas no carregamento. Disponíveis
            para as sondas de direitos digitais, que avaliam custo de acesso —
            informação que existe fora do DOM e que, por isso, nenhuma
            ferramenta de acessibilidade convencional considera.
        scoring: Parâmetros de índice (preço do MB, franquia, limiares), para
            que as sondas não embutam constantes não declaradas.
    """

    __slots__ = ("is_critical_path", "network", "page", "scoring", "url", "viewport")

    def __init__(
        self,
        page: Page,
        url: str,
        viewport: Viewport,
        *,
        is_critical_path: bool = False,
        network: Any = None,
        scoring: Any = None,
    ) -> None:
        self.page = page
        self.url = url
        self.viewport = viewport
        self.is_critical_path = is_critical_path
        self.network = network
        self.scoring = scoring

    async def evaluate(self, script: str, arg: Any = None) -> Any:
        """Avalia JavaScript na página, devolvendo ``None`` em caso de erro.

        Sondas usam este método em vez de ``page.evaluate`` para que uma falha
        isolada de script não interrompa a auditoria da página.
        """
        try:
            return await self.page.evaluate(script, arg)
        except PlaywrightError as exc:
            logger.warning("script de sonda falhou", extra={"url": self.url, "erro": str(exc)})
            return None


class Probe(abc.ABC):
    """Classe base de todas as sondas.

    Subclasses implementam :meth:`_run` e declaram :attr:`id`, :attr:`criteria`
    e :attr:`confidence`. A execução passa por :meth:`run`, que aplica o
    contrato de confiança e captura exceções.
    """

    #: Identificador estável da sonda, prefixado por ``probe.``.
    id: str = "probe.base"

    #: Critérios WCAG que a sonda avalia. Pode ser vazio para sondas de
    #: direitos digitais que não correspondem a critério técnico.
    criteria: tuple[str, ...] = ()

    #: Grau de certeza — determina o veredito máximo admissível.
    confidence: Confidence = Confidence.DETERMINISTIC

    #: Descrição do que a sonda verifica, exibida na documentação da API.
    description: str = ""

    def applies_to(self, context: ProbeContext) -> bool:
        """Se a sonda deve rodar neste contexto.

        O padrão é rodar sempre. Sondas específicas de viewport sobrescrevem.
        """
        return True

    async def run(self, context: ProbeContext) -> list[Finding]:
        """Executa a sonda com as garantias do contrato.

        Returns:
            Lista de achados, possivelmente vazia. Nunca levanta exceção: uma
            sonda quebrada não pode interromper a coleta nem, pior, produzir
            silenciosamente uma página "sem problemas".
        """
        if not self.applies_to(context):
            return []
        try:
            findings = await self._run(context)
        except PlaywrightError as exc:
            logger.warning(
                "sonda falhou", extra={"sonda": self.id, "url": context.url, "erro": str(exc)}
            )
            return []
        except Exception:
            logger.exception(
                "erro inesperado em sonda", extra={"sonda": self.id, "url": context.url}
            )
            return []

        return [self._enforce_contract(f, context) for f in findings]

    def _enforce_contract(self, finding: Finding, context: ProbeContext) -> Finding:
        """Aplica as invariantes do contrato de sondas a um achado.

        - Sondas heurísticas não podem reprovar: ``FAIL`` vira ``INCOMPLETE``.
        - ``page_url`` e ``viewport`` são preenchidos a partir do contexto, para
          que a sonda não precise (nem possa errar em) repeti-los.
        """
        if self.confidence is Confidence.HEURISTIC and finding.outcome is Outcome.FAIL:
            logger.debug(
                "veredito rebaixado para INCOMPLETE por contrato heurístico",
                extra={"sonda": self.id, "regra": finding.rule_id},
            )
            finding = finding.model_copy(update={"outcome": Outcome.INCOMPLETE, "impact": None})
        return finding.model_copy(
            update={"page_url": context.url, "viewport": context.viewport.name}
        )

    @abc.abstractmethod
    async def _run(self, context: ProbeContext) -> list[Finding]:
        """Implementação concreta da verificação."""
        raise NotImplementedError
