"""Sondas de formulário — onde o serviço público digital efetivamente acontece.

Motivação empírica, descoberta na validação do próprio motor
-----------------------------------------------------------
O axe-core **não reprova** um campo cujo único nome acessível vem do atributo
``placeholder``: sua regra ``label`` aceita ``non-empty-placeholder`` como fonte
válida de nome. A decisão é defensável do ponto de vista da especificação de
nome acessível — o ``placeholder`` de fato entra no cálculo — mas produz um
ponto cego grave na prática:

1. O ``placeholder`` **desaparece** assim que o usuário digita o primeiro
   caractere. Quem usa leitor de tela e volta ao campo para conferir o que
   preencheu ouve "caixa de edição" e o valor, sem qualquer pista do que ali se
   pedia.
2. O ``placeholder`` tem contraste tipicamente baixo, por convenção de estilo, e
   costuma falhar o critério 1.4.3 justamente para quem mais precisaria dele.
3. Ele não é anunciado de forma consistente entre combinações de navegador e
   leitor de tela.

Como esse padrão é o mais comum nos formulários de agendamento e cadastro dos
portais públicos brasileiros, aceitá-lo tornaria a auditoria cega exatamente na
tela em que o cidadão pede a consulta. Daí a sonda.

Isto é documentado como achado metodológico do projeto: ver
``docs/metodologia/limites-do-axe-core.md``.
"""

from __future__ import annotations

from typing import Any

from acessisaude_audit.auditor.probes._js import CSS_PATH_FN, wrap
from acessisaude_audit.auditor.probes.base import (
    Confidence,
    Probe,
    ProbeContext,
    affected_groups,
    help_url_for,
    remediation_for,
)
from acessisaude_audit.domain.mapping import LegalRisk
from acessisaude_audit.domain.models import (
    EvidenceNode,
    Finding,
    FindingSource,
    Impact,
    Outcome,
)

__all__ = ["ErrorIdentificationProbe", "PlaceholderAsLabelProbe"]


_FIELD_SCRIPT = wrap(
    """
    const controles = Array.from(
      document.querySelectorAll('input, select, textarea')
    ).filter(el => {
      const tipo = (el.getAttribute('type') || '').toLowerCase();
      if (['hidden', 'submit', 'reset', 'button', 'image'].includes(tipo)) return false;
      if (el.disabled) return false;
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      return true;
    });

    const textoDe = (no) => (no && no.textContent ? no.textContent.trim() : '');

    const rotuloAssociado = (el) => {
      // <label for="id">
      if (el.id) {
        const explicito = document.querySelector('label[for="' + CSS.escape(el.id) + '"]');
        if (textoDe(explicito)) return 'label-explicito';
      }
      // <label><input></label>
      const envolvente = el.closest('label');
      if (envolvente && textoDe(envolvente)) return 'label-envolvente';
      return null;
    };

    return controles.map(el => {
      const rotulo = rotuloAssociado(el);
      const ariaLabel = (el.getAttribute('aria-label') || '').trim();
      const ariaLabelledby = (el.getAttribute('aria-labelledby') || '').trim();
      let textoLabelledby = '';
      if (ariaLabelledby) {
        textoLabelledby = ariaLabelledby.split(/\\s+/)
          .map(id => textoDe(document.getElementById(id)))
          .filter(Boolean)
          .join(' ');
      }
      const placeholder = (el.getAttribute('placeholder') || '').trim();
      const title = (el.getAttribute('title') || '').trim();

      return {
        selector: cssPath(el),
        html: el.outerHTML.slice(0, 300),
        tag: el.tagName.toLowerCase(),
        type: (el.getAttribute('type') || '').toLowerCase() || null,
        name: el.getAttribute('name'),
        rotulo,
        ariaLabel,
        temLabelledby: Boolean(textoLabelledby),
        placeholder,
        title,
        ariaInvalid: (el.getAttribute('aria-invalid') || '').toLowerCase(),
        describedby: (el.getAttribute('aria-describedby') || '').trim(),
        errormessage: (el.getAttribute('aria-errormessage') || '').trim(),
        required: el.hasAttribute('required') || el.getAttribute('aria-required') === 'true',
      };
    });
    """,
    CSS_PATH_FN,
)


def _tem_rotulo_persistente(campo: dict[str, Any]) -> bool:
    """Se o campo tem nome acessível que **permanece** após o preenchimento."""
    return bool(campo.get("rotulo") or campo.get("ariaLabel") or campo.get("temLabelledby"))


class PlaceholderAsLabelProbe(Probe):
    """Detecta campos rotulados apenas por ``placeholder`` ou ``title`` (WCAG 3.3.2).

    Emite dois vereditos distintos, porque a gravidade difere:

    - **``placeholder`` como único rótulo** → ``FAIL``. O texto some ao digitar:
      o rótulo existe antes do uso e deixa de existir durante o uso, que é
      justamente quando o usuário precisa conferi-lo.
    - **``title`` como único rótulo** → ``FAIL``. O ``title`` só aparece com o
      cursor parado sobre o campo, gesto indisponível em toque e em navegação
      por teclado.

    Campos sem **nenhuma** fonte de nome ficam fora desta sonda: o axe-core já
    os reprova pela regra ``label``, e reportá-los aqui duplicaria o mesmo
    defeito sob dois identificadores, inflando a contagem de violações.
    """

    id = "probe.placeholder-como-rotulo"
    criteria = ("3.3.2",)
    confidence = Confidence.DETERMINISTIC
    description = (
        "Identifica campos de formulário cujo único nome acessível provém de "
        "placeholder ou title — fontes que não persistem durante o uso."
    )

    async def _run(self, context: ProbeContext) -> list[Finding]:
        campos: list[dict[str, Any]] | None = await context.evaluate(_FIELD_SCRIPT)
        if not campos:
            return []

        so_placeholder = [
            c for c in campos if not _tem_rotulo_persistente(c) and c.get("placeholder")
        ]
        so_title = [
            c
            for c in campos
            if not _tem_rotulo_persistente(c) and not c.get("placeholder") and c.get("title")
        ]

        achados: list[Finding] = []

        if so_placeholder:
            achados.append(
                Finding(
                    rule_id=self.id,
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.SERIOUS,
                    criteria=list(self.criteria),
                    summary=(
                        f"{len(so_placeholder)} campo(s) de formulário são identificados "
                        "apenas pelo texto de placeholder."
                    ),
                    description=(
                        "Estes campos não possuem <label>, aria-label nem "
                        "aria-labelledby: sua única identificação é o placeholder, que "
                        "desaparece assim que o usuário digita o primeiro caractere. "
                        "Quem usa leitor de tela e retorna ao campo para conferir o que "
                        "preencheu ouve apenas 'caixa de edição' e o valor digitado, sem "
                        "saber se ali se pedia o CPF ou o Cartão Nacional de Saúde. "
                        "O padrão também falha para pessoas com deficiência intelectual, "
                        "que perdem a instrução ao começar a responder. "
                        "Registre-se que a verificação automática do axe-core aceita o "
                        "placeholder como nome acessível válido; esta sonda existe "
                        "precisamente para cobrir essa lacuna."
                    ),
                    remediation=remediation_for("3.3.2"),
                    help_url=help_url_for("3.3.2"),
                    affects=affected_groups("3.3.2"),
                    legal_risk_override=LegalRisk.ALTO,
                    nodes=[
                        EvidenceNode(
                            selector=str(c.get("selector", "")),
                            html=str(c.get("html", "")),
                            failure_summary=(
                                f"<{c.get('tag')}> identificado apenas por "
                                f"placeholder={c.get('placeholder')!r}."
                            ),
                            measured={
                                "placeholder": c.get("placeholder"),
                                "name": c.get("name"),
                                "type": c.get("type"),
                                "obrigatorio": c.get("required"),
                            },
                        )
                        for c in so_placeholder[:12]
                    ],
                )
            )

        if so_title:
            achados.append(
                Finding(
                    rule_id="probe.title-como-rotulo",
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.MODERATE,
                    criteria=list(self.criteria),
                    summary=(
                        f"{len(so_title)} campo(s) são identificados apenas pelo atributo title."
                    ),
                    description=(
                        "O atributo title só é exibido quando o cursor do mouse "
                        "permanece sobre o elemento — gesto indisponível em telas de "
                        "toque e na navegação por teclado. Como identificação única de "
                        "campo, ele exclui a maior parte dos usuários móveis."
                    ),
                    remediation=remediation_for("3.3.2"),
                    help_url=help_url_for("3.3.2"),
                    affects=affected_groups("3.3.2"),
                    nodes=[
                        EvidenceNode(
                            selector=str(c.get("selector", "")),
                            html=str(c.get("html", "")),
                            failure_summary=f"Identificado apenas por title={c.get('title')!r}.",
                            measured={"title": c.get("title"), "name": c.get("name")},
                        )
                        for c in so_title[:12]
                    ],
                )
            )

        return achados


class ErrorIdentificationProbe(Probe):
    """Detecta erro de campo sem mensagem associada programaticamente (WCAG 3.3.1).

    Alvo: campos marcados com ``aria-invalid="true"`` que não apontam para
    nenhuma descrição do erro (``aria-describedby`` ou ``aria-errormessage``).

    O sistema *sabe* que o campo está errado — declarou-o na marcação — e não
    informa **qual** é o erro por via acessível. Para quem usa leitor de tela, o
    formulário falha em silêncio: o envio não completa e nada explica por quê.
    Em um agendamento de consulta, isso não é inconveniência, é negativa de
    atendimento por meio técnico.
    """

    id = "probe.erro-sem-mensagem"
    criteria = ("3.3.1",)
    confidence = Confidence.DETERMINISTIC
    description = (
        "Identifica campos com aria-invalid=true sem descrição de erro associada programaticamente."
    )

    async def _run(self, context: ProbeContext) -> list[Finding]:
        campos: list[dict[str, Any]] | None = await context.evaluate(_FIELD_SCRIPT)
        if not campos:
            return []

        invalidos_mudos = [
            c
            for c in campos
            if c.get("ariaInvalid") == "true"
            and not c.get("describedby")
            and not c.get("errormessage")
        ]
        if not invalidos_mudos:
            return []

        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.PROBE,
                outcome=Outcome.FAIL,
                impact=Impact.SERIOUS,
                criteria=list(self.criteria),
                summary=(
                    f"{len(invalidos_mudos)} campo(s) em erro não informam qual é o erro "
                    "por via acessível."
                ),
                description=(
                    'Os campos declaram aria-invalid="true", mas não apontam para '
                    "nenhuma descrição do problema. O sistema reconhece o erro e não o "
                    "comunica: para quem usa leitor de tela, o formulário simplesmente "
                    "não é enviado, sem explicação. O usuário repete a tentativa "
                    "indefinidamente ou desiste do serviço."
                ),
                remediation=remediation_for("3.3.1"),
                help_url=help_url_for("3.3.1"),
                affects=affected_groups("3.3.1"),
                legal_risk_override=LegalRisk.ALTO,
                nodes=[
                    EvidenceNode(
                        selector=str(c.get("selector", "")),
                        html=str(c.get("html", "")),
                        failure_summary=(
                            'aria-invalid="true" sem aria-describedby nem aria-errormessage.'
                        ),
                        measured={"name": c.get("name"), "type": c.get("type")},
                    )
                    for c in invalidos_mudos[:12]
                ],
            )
        ]
