"""Sondas de operabilidade por teclado.

Este é o grupo de sondas com maior peso jurídico do projeto. A navegação por
teclado é a via de acesso de duas populações distintas — pessoas com deficiência
motora e pessoas cegas usuárias de leitor de tela — e, ao contrário de quase
toda outra barreira, **não admite rota alternativa**: se o botão de confirmar
consulta não recebe foco, não existe outro caminho até ele.

Por isso as violações aqui detectadas recebem
:class:`~acessisaude_audit.domain.mapping.LegalRisk.CRITICO` e alimentam a
sinalização de *barreira absoluta* nos índices.

Diferencial em relação ao axe-core
----------------------------------
O axe verifica o DOM em repouso. Estas sondas **interagem**: emitem pressões
reais da tecla Tab através do protocolo do navegador. A diferença é decisiva
para o indicador de foco visível, porque os navegadores só aplicam a
pseudoclasse ``:focus-visible`` quando a modalidade de entrada corrente é o
teclado. Uma chamada programática a ``element.focus()`` — abordagem usual de
ferramentas mais simples — não ativa essa modalidade e produziria falsos
positivos em massa em qualquer página moderna.
"""

from __future__ import annotations

from typing import Any

from acessisaude_audit.auditor.probes._js import CSS_PATH_FN, FOCUSABLE_SELECTOR, wrap
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

__all__ = ["FocusVisibilityProbe", "InteractiveElementProbe", "TabOrderProbe"]

#: Teto de elementos percorridos por tabulação.
#:
#: A verificação custa uma ida e volta ao navegador por elemento; em portais com
#: menus extensos, percorrer tudo multiplicaria o tempo de varredura sem
#: acrescentar informação — defeitos de indicador de foco são sistêmicos (vêm do
#: CSS global), não pontuais. O teto é declarado no relatório para que a
#: cobertura parcial não seja lida como cobertura total.
MAX_TAB_STOPS = 40


_PREPARE_SCRIPT = wrap(
    """
    const els = Array.from(document.querySelectorAll(selector)).filter(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 || r.height > 0;
    });
    const styleOf = (el) => {
      const cs = getComputedStyle(el);
      return [
        cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.outlineOffset,
        cs.boxShadow, cs.borderColor, cs.borderWidth, cs.borderStyle,
        cs.backgroundColor, cs.color, cs.textDecorationLine, cs.transform, cs.filter
      ].join('|');
    };
    els.forEach((el, i) => {
      el.setAttribute('data-a11y-probe-idx', String(i));
      el.setAttribute('data-a11y-probe-base', styleOf(el));
    });
    return {
      count: els.length,
      items: els.slice(0, 200).map((el, i) => ({
        index: i,
        selector: cssPath(el),
        tag: el.tagName.toLowerCase(),
        html: el.outerHTML.slice(0, 300),
      })),
    };
    """,
    CSS_PATH_FN,
    args="selector",
)

#: Lê o elemento atualmente focado e compara seu estilo com a linha de base.
_ACTIVE_SCRIPT = """
() => {
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return null;
  const cs = getComputedStyle(el);
  const now = [
    cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.outlineOffset,
    cs.boxShadow, cs.borderColor, cs.borderWidth, cs.borderStyle,
    cs.backgroundColor, cs.color, cs.textDecorationLine, cs.transform, cs.filter
  ].join('|');
  const base = el.getAttribute('data-a11y-probe-base');
  const idx = el.getAttribute('data-a11y-probe-idx');
  return {
    index: idx === null ? null : Number(idx),
    changed: base === null ? null : base !== now,
    outlineStyle: cs.outlineStyle,
    outlineWidth: cs.outlineWidth,
    boxShadow: cs.boxShadow,
    tag: el.tagName.toLowerCase(),
    tabindex: el.getAttribute('tabindex'),
    tracked: base !== null,
  };
}
"""

_CLEANUP_SCRIPT = """
() => {
  for (const el of document.querySelectorAll('[data-a11y-probe-idx]')) {
    el.removeAttribute('data-a11y-probe-idx');
    el.removeAttribute('data-a11y-probe-base');
  }
  return true;
}
"""


class FocusVisibilityProbe(Probe):
    """Verifica se cada parada de tabulação exibe indicador de foco (WCAG 2.4.7).

    Método: marca os elementos focáveis com sua assinatura de estilo em repouso,
    percorre a página com pressões reais de Tab e, a cada parada, compara a
    assinatura corrente com a linha de base. Ausência de qualquer diferença
    visual significa que o usuário de teclado não tem como saber onde está.

    Limitações declaradas:

    - A comparação é de estilo computado do próprio elemento; indicadores
      desenhados exclusivamente em pseudoelementos ``::before``/``::after`` ou
      em um elemento irmão não são captados e podem gerar falso positivo. Por
      isso o veredito é ``FAIL`` apenas quando, além de não haver mudança, o
      ``outline`` está explicitamente suprimido; nos demais casos o achado sai
      como ``INCOMPLETE``.
    - Percorre no máximo :data:`MAX_TAB_STOPS` paradas.
    """

    id = "probe.focus-visible"
    criteria = ("2.4.7",)
    confidence = Confidence.DETERMINISTIC
    description = (
        "Percorre a página por tabulação real e verifica se cada parada de foco "
        "produz mudança visual perceptível."
    )

    async def _run(self, context: ProbeContext) -> list[Finding]:
        prepared: dict[str, Any] | None = await context.evaluate(
            _PREPARE_SCRIPT, FOCUSABLE_SELECTOR
        )
        if not prepared or not prepared.get("count"):
            return []

        items = {int(i["index"]): i for i in prepared.get("items", [])}
        total = int(prepared["count"])
        limit = min(total, MAX_TAB_STOPS)

        no_indicator: list[dict[str, Any]] = []
        suppressed: list[dict[str, Any]] = []
        seen_indices: set[int] = set()

        # Começa do topo do documento para que a ordem de tabulação observada
        # corresponda à que o usuário encontraria ao abrir a página.
        await context.page.evaluate("() => window.scrollTo(0, 0)")
        for _ in range(limit):
            await context.page.keyboard.press("Tab")
            active: dict[str, Any] | None = await context.evaluate(_ACTIVE_SCRIPT)
            if not active or not active.get("tracked"):
                continue
            idx = active.get("index")
            if idx is None or idx in seen_indices:
                continue
            seen_indices.add(int(idx))

            if active.get("changed") is False:
                record = {**items.get(int(idx), {}), **active}
                outline_off = (
                    active.get("outlineStyle") == "none"
                    or str(active.get("outlineWidth", "")).startswith("0")
                ) and active.get("boxShadow") in (None, "none")
                (suppressed if outline_off else no_indicator).append(record)

        await context.evaluate(_CLEANUP_SCRIPT)

        findings: list[Finding] = []
        if suppressed:
            findings.append(
                self._finding(
                    outcome=Outcome.FAIL,
                    impact=Impact.SERIOUS,
                    records=suppressed,
                    total=total,
                    inspected=limit,
                    summary=(
                        f"{len(suppressed)} controle(s) não exibem indicador de foco: "
                        "o contorno está suprimido e nenhuma outra mudança visual ocorre."
                    ),
                    description=(
                        "Ao percorrer a página com a tecla Tab, estes controles recebem "
                        "o foco sem qualquer alteração perceptível — o contorno padrão do "
                        "navegador foi removido e não houve substituto. Para quem navega "
                        "sem mouse, a página passa a exigir adivinhação: pressiona-se "
                        "Enter sem saber qual ação será disparada. Em um fluxo de "
                        "agendamento, isso significa confirmar ou cancelar às cegas."
                    ),
                )
            )
        if no_indicator:
            findings.append(
                self._finding(
                    outcome=Outcome.INCOMPLETE,
                    impact=None,
                    records=no_indicator,
                    total=total,
                    inspected=limit,
                    summary=(
                        f"{len(no_indicator)} controle(s) sem mudança de estilo detectável "
                        "ao receber foco — requer confirmação visual."
                    ),
                    description=(
                        "Nenhuma diferença foi observada no estilo computado do próprio "
                        "elemento ao recebê-lo. O indicador pode existir em pseudoelemento "
                        "ou em elemento irmão, casos que esta verificação não alcança. "
                        "Confirmar visualmente antes de reportar como violação."
                    ),
                )
            )
        return findings

    def _finding(
        self,
        *,
        outcome: Outcome,
        impact: Impact | None,
        records: list[dict[str, Any]],
        total: int,
        inspected: int,
        summary: str,
        description: str,
    ) -> Finding:
        return Finding(
            rule_id=self.id,
            source=FindingSource.PROBE,
            outcome=outcome,
            impact=impact,
            criteria=list(self.criteria),
            summary=summary,
            description=(
                f"{description} Foram inspecionadas {inspected} das {total} paradas de "
                "tabulação da página."
            ),
            remediation=remediation_for("2.4.7"),
            help_url=help_url_for("2.4.7"),
            affects=affected_groups("2.4.7"),
            nodes=[
                EvidenceNode(
                    selector=str(r.get("selector", "")),
                    html=str(r.get("html", "")),
                    failure_summary=(
                        f"<{r.get('tag')}> recebe foco sem alteração visual "
                        f"(outline: {r.get('outlineStyle')} {r.get('outlineWidth')}; "
                        f"box-shadow: {r.get('boxShadow')})."
                    ),
                    measured={
                        "outline_style": r.get("outlineStyle"),
                        "outline_width": r.get("outlineWidth"),
                        "box_shadow": r.get("boxShadow"),
                    },
                )
                for r in records[:12]
            ],
        )


_INTERACTIVE_SCRIPT = wrap(
    """
    // Elementos nativamente interativos: já são focáveis e anunciados.
    const interactive = new Set([
      'A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'SUMMARY', 'DETAILS', 'LABEL', 'OPTION',
    ]);
    // Papéis ARIA que declaram um widget acionável.
    const widgetRoles = new Set([
      'button', 'link', 'checkbox', 'radio', 'tab', 'menuitem', 'switch',
      'option', 'treeitem', 'slider', 'combobox', 'textbox',
    ]);
    const offenders = [];
    for (const el of document.querySelectorAll('[onclick], [onkeydown], [onmousedown]')) {
      if (interactive.has(el.tagName)) continue;
      const role = (el.getAttribute('role') || '').toLowerCase();
      const tabindex = el.getAttribute('tabindex');
      const focusable = tabindex !== null && tabindex !== '-1';
      const hasWidgetRole = widgetRoles.has(role);
      if (focusable && hasWidgetRole) continue;
      offenders.push({
        selector: cssPath(el),
        html: el.outerHTML.slice(0, 300),
        tag: el.tagName.toLowerCase(),
        role: role || null,
        tabindex,
        focusable,
        hasWidgetRole,
      });
      if (offenders.length >= 15) break;
    }
    return offenders;
    """,
    CSS_PATH_FN,
)


class InteractiveElementProbe(Probe):
    """Detecta controles construídos sobre elementos não interativos (WCAG 2.1.1, 4.1.2).

    Padrão alvo: ``<div onclick="...">`` sem ``tabindex`` nem ``role``. Para o
    mouse, funciona. Para o teclado, o elemento é inalcançável; para o leitor de
    tela, ele sequer é anunciado como controle. É a forma mais comum e mais
    severa de exclusão em interfaces construídas sem preocupação com
    acessibilidade — e a que melhor ilustra, no artigo, que a barreira decorre
    de decisão de implementação, não de limitação tecnológica.
    """

    id = "probe.non-interactive-control"
    criteria = ("2.1.1", "4.1.2")
    confidence = Confidence.DETERMINISTIC
    description = (
        "Identifica elementos com manipulador de clique que não são focáveis "
        "por teclado nem expõem papel de widget."
    )

    async def _run(self, context: ProbeContext) -> list[Finding]:
        offenders: list[dict[str, Any]] | None = await context.evaluate(_INTERACTIVE_SCRIPT)
        if not offenders:
            return []

        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.PROBE,
                outcome=Outcome.FAIL,
                impact=Impact.CRITICAL,
                criteria=list(self.criteria),
                summary=(
                    f"{len(offenders)} elemento(s) respondem ao clique do mouse mas não "
                    "são alcançáveis por teclado."
                ),
                description=(
                    "Elementos genéricos (div, span) receberam manipuladores de clique "
                    "sem tabindex nem papel ARIA correspondente. O controle funciona "
                    "apenas para quem usa mouse: não recebe foco por tabulação e não é "
                    "anunciado como acionável por leitores de tela. Não há rota "
                    "alternativa — para a pessoa com deficiência motora ou visual, a "
                    "função simplesmente não existe."
                ),
                remediation=(
                    "Usar <button> ou <a href> nativos. Quando inevitável manter o "
                    'elemento genérico, acrescentar role de widget, tabindex="0" e '
                    "manipulador de teclado (Enter e Espaço) equivalente ao de clique."
                ),
                help_url=help_url_for("2.1.1"),
                affects=affected_groups("2.1.1"),
                legal_risk_override=LegalRisk.CRITICO,
                legal_thesis_override=(
                    "A construção de controles inacessíveis por teclado impede "
                    "integralmente o uso do serviço por pessoas com deficiência motora "
                    "e por usuários de leitor de tela, sem qualquer rota alternativa. "
                    "Configura barreira absoluta na comunicação e na informação (art. "
                    "3º, IV, 'd', LBI), violação direta do dever de acessibilidade dos "
                    "sítios de órgãos de governo (art. 63, caput, LBI) e descumprimento "
                    "do art. 9 da Convenção sobre os Direitos das Pessoas com "
                    "Deficiência, que tem hierarquia de emenda constitucional."
                ),
                extra_provisions=["onu.art9", "lbi.art74", "lbi.art3.i"],
                nodes=[
                    EvidenceNode(
                        selector=str(o.get("selector", "")),
                        html=str(o.get("html", "")),
                        failure_summary=(
                            f"<{o.get('tag')}> possui manipulador de clique, "
                            f"tabindex={o.get('tabindex')!r} e role={o.get('role')!r}."
                        ),
                        measured={
                            "tag": o.get("tag"),
                            "role": o.get("role"),
                            "tabindex": o.get("tabindex"),
                            "focusable": o.get("focusable"),
                        },
                    )
                    for o in offenders
                ],
            )
        ]


_TABORDER_SCRIPT = wrap(
    """
    const offenders = [];
    for (const el of document.querySelectorAll('[tabindex]')) {
      const value = parseInt(el.getAttribute('tabindex'), 10);
      if (Number.isFinite(value) && value > 0) {
        offenders.push({
          selector: cssPath(el),
          html: el.outerHTML.slice(0, 300),
          tag: el.tagName.toLowerCase(),
          tabindex: value,
        });
        if (offenders.length >= 15) break;
      }
    }
    return offenders;
    """,
    CSS_PATH_FN,
)


class TabOrderProbe(Probe):
    """Detecta ``tabindex`` positivo, que desalinha a ordem de foco (WCAG 2.4.3).

    ``tabindex`` maior que zero retira o elemento da ordem natural do documento
    e o promove para a frente de *toda* a página. Em formulários de saúde, o
    efeito prático é o usuário de teclado chegar ao botão de enviar antes de
    preencher os campos — e submeter dados incompletos sem perceber.
    """

    id = "probe.positive-tabindex"
    criteria = ("2.4.3",)
    confidence = Confidence.DETERMINISTIC
    description = "Identifica elementos com tabindex positivo."

    async def _run(self, context: ProbeContext) -> list[Finding]:
        offenders: list[dict[str, Any]] | None = await context.evaluate(_TABORDER_SCRIPT)
        if not offenders:
            return []

        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.PROBE,
                outcome=Outcome.FAIL,
                impact=Impact.MODERATE,
                criteria=list(self.criteria),
                summary=(
                    f"{len(offenders)} elemento(s) usam tabindex positivo, alterando a "
                    "ordem natural de tabulação."
                ),
                description=(
                    "Valores de tabindex maiores que zero criam uma ordem de foco "
                    "paralela à ordem visual do documento. O usuário de teclado passa a "
                    "percorrer a página em sequência imprevisível, o que em um formulário "
                    "de agendamento produz preenchimento fora de ordem e submissão "
                    "prematura."
                ),
                remediation=remediation_for("2.4.3"),
                help_url=help_url_for("2.4.3"),
                affects=affected_groups("2.4.3"),
                nodes=[
                    EvidenceNode(
                        selector=str(o.get("selector", "")),
                        html=str(o.get("html", "")),
                        failure_summary=(f"<{o.get('tag')}> declara tabindex={o.get('tabindex')}."),
                        measured={"tabindex": o.get("tabindex")},
                    )
                    for o in offenders
                ],
            )
        ]
