"""Sondas de adaptação a tela pequena e a ampliação.

Cobrem dois critérios que o axe-core não verifica porque exigem observar a
página *renderizada em condição de uso*, e não apenas o DOM:

- **1.4.10 Refluxo (AA)** — conteúdo utilizável em 320 CSS px sem rolagem
  horizontal.
- **1.4.4 Redimensionar texto (AA)** — ampliação até 200% sem perda de conteúdo
  ou função.

Relevância para o objeto do estudo: o acesso a serviços públicos de saúde no
Brasil é majoritariamente móvel, e concentradamente em aparelhos de tela pequena
entre a população de menor renda. Uma página que exige rolagem lateral não é
inconveniente — ela esconde conteúdo, porque o usuário não sabe que há algo à
direita da borda.
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

__all__ = ["ReflowProbe", "ZoomLockProbe"]

#: Largura máxima, em CSS px, em que o critério 1.4.10 exige ausência de rolagem
#: horizontal. Valor fixado pela própria norma — não é parâmetro do estudo.
REFLOW_WIDTH_PX = 320

#: Tolerância em px para arredondamento de subpixel do navegador.
#:
#: Sem ela, diferenças de 0,5 px em bordas produziriam falso positivo em
#: praticamente toda página, tornando o indicador inútil.
_OVERFLOW_TOLERANCE_PX = 2


_REFLOW_SCRIPT = wrap(
    """
    const docEl = document.documentElement;
    const vw = docEl.clientWidth;
    const scrollWidth = Math.max(docEl.scrollWidth, document.body ? document.body.scrollWidth : 0);
    const overflow = scrollWidth - vw;
    const offenders = [];

    // A técnica C37/G206 da WCAG admite rolagem CONFINADA a um bloco (tabela
    // larga, bloco de código): o que o critério 1.4.10 proíbe é a rolagem do
    // DOCUMENTO. Portanto um elemento largo dentro de um contêiner rolável não
    // é violação — e ignorar isso produziria falso positivo justamente nas
    // páginas que aplicaram a técnica correta.
    const dentroDeContainerRolavel = (el) => {
      let no = el.parentElement;
      while (no && no !== document.body) {
        const cs = getComputedStyle(no);
        if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') return true;
        no = no.parentElement;
      }
      return false;
    };

    if (overflow > tolerance) {
      const all = document.querySelectorAll('body *');
      for (const el of all) {
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') continue;
        if (dentroDeContainerRolavel(el)) continue;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        if (r.right > vw + tolerance) {
          offenders.push({
            selector: cssPath(el),
            html: el.outerHTML.slice(0, 300),
            tag: el.tagName.toLowerCase(),
            right: Math.round(r.right),
            width: Math.round(r.width),
          });
          if (offenders.length >= 12) break;
        }
      }
    }
    return { viewportWidth: vw, scrollWidth, overflow, offenders };
    """,
    CSS_PATH_FN,
    args="tolerance",
)


class ReflowProbe(Probe):
    """Detecta rolagem horizontal em viewport de 320 CSS px (WCAG 1.4.10)."""

    id = "probe.reflow-320"
    criteria = ("1.4.10",)
    confidence = Confidence.DETERMINISTIC
    description = (
        "Mede a largura de rolagem do documento em 320 px e identifica os "
        "elementos que ultrapassam a borda direta do viewport."
    )

    def applies_to(self, context: ProbeContext) -> bool:
        """Só faz sentido no perfil móvel estreito."""
        return context.viewport.width <= REFLOW_WIDTH_PX

    async def _run(self, context: ProbeContext) -> list[Finding]:
        data: dict[str, Any] | None = await context.evaluate(_REFLOW_SCRIPT, _OVERFLOW_TOLERANCE_PX)
        if not data or data.get("overflow", 0) <= _OVERFLOW_TOLERANCE_PX:
            return []

        overflow = int(data["overflow"])
        offenders = data.get("offenders") or []

        nodes = [
            EvidenceNode(
                selector=str(o.get("selector", "")),
                html=str(o.get("html", "")),
                failure_summary=(
                    f"O elemento <{o.get('tag')}> estende-se até {o.get('right')} px, "
                    f"além da borda do viewport de {data.get('viewportWidth')} px."
                ),
                measured={
                    "right_px": o.get("right"),
                    "width_px": o.get("width"),
                    "viewport_width_px": data.get("viewportWidth"),
                },
            )
            for o in offenders
        ]
        if not nodes:
            # Há transbordo, mas nenhum elemento individual identificável —
            # tipicamente margem negativa ou largura fixa no próprio body.
            nodes = [
                EvidenceNode(
                    selector="html",
                    failure_summary=(
                        "O documento rola horizontalmente, mas nenhum elemento isolado "
                        "ultrapassa a borda: verificar largura fixa em html/body."
                    ),
                    measured={"overflow_px": overflow},
                )
            ]

        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.PROBE,
                outcome=Outcome.FAIL,
                impact=Impact.SERIOUS,
                criteria=list(self.criteria),
                summary=(
                    f"A página exige rolagem horizontal em tela de "
                    f"{data.get('viewportWidth')} px ({overflow} px de transbordo)."
                ),
                description=(
                    "Em viewport de 320 CSS px — largura mínima exigida pelo critério "
                    "1.4.10 e representativa dos aparelhos de entrada mais comuns entre "
                    "usuários de baixa renda — o conteúdo não se reorganiza em coluna "
                    "única. Parte da informação fica fora da área visível sem qualquer "
                    "indicação de que exista, o que difere de um simples desconforto: "
                    "o usuário não busca aquilo cuja existência desconhece."
                ),
                remediation=remediation_for("1.4.10"),
                help_url=help_url_for("1.4.10"),
                affects=affected_groups("1.4.10"),
                nodes=nodes,
            )
        ]


_ZOOM_SCRIPT = """
() => {
  const meta = document.querySelector('meta[name="viewport"]');
  if (!meta) return { present: false };
  const content = (meta.getAttribute('content') || '').toLowerCase();
  const parts = {};
  for (const chunk of content.split(',')) {
    const [k, v] = chunk.split('=').map(s => (s || '').trim());
    if (k) parts[k] = v;
  }
  const maxScale = parseFloat(parts['maximum-scale']);
  return {
    present: true,
    content,
    userScalableNo: parts['user-scalable'] === 'no' || parts['user-scalable'] === '0',
    maximumScale: Number.isFinite(maxScale) ? maxScale : null,
    html: meta.outerHTML.slice(0, 300),
  };
}
"""


class ZoomLockProbe(Probe):
    """Detecta bloqueio de ampliação via ``meta viewport`` (WCAG 1.4.4).

    Verifica dois padrões que impedem o usuário de ampliar a página:
    ``user-scalable=no`` e ``maximum-scale`` inferior a 2. Ambos são
    declarações explícitas do desenvolvedor de que o usuário não pode adaptar
    a interface à sua condição visual — o oposto do desenho universal previsto
    no art. 3º, II da LBI.
    """

    id = "probe.zoom-lock"
    criteria = ("1.4.4",)
    confidence = Confidence.DETERMINISTIC
    description = "Verifica se a meta viewport impede ampliação até 200%."

    async def _run(self, context: ProbeContext) -> list[Finding]:
        data: dict[str, Any] | None = await context.evaluate(_ZOOM_SCRIPT)
        if not data or not data.get("present"):
            return []

        reasons: list[str] = []
        if data.get("userScalableNo"):
            reasons.append("'user-scalable=no' impede totalmente a ampliação")
        max_scale = data.get("maximumScale")
        if isinstance(max_scale, (int, float)) and max_scale < 2:
            reasons.append(
                f"'maximum-scale={max_scale}' limita a ampliação abaixo dos 200% exigidos"
            )
        if not reasons:
            return []

        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.PROBE,
                outcome=Outcome.FAIL,
                impact=Impact.SERIOUS,
                criteria=list(self.criteria),
                summary="A página bloqueia a ampliação pelo usuário.",
                description=(
                    "A meta viewport declara restrições de escala: "
                    + "; ".join(reasons)
                    + ". Pessoas com baixa visão dependem da ampliação nativa do "
                    "navegador para ler conteúdo de saúde; o bloqueio equivale a "
                    "recusar adaptação razoável."
                ),
                remediation=remediation_for("1.4.4"),
                help_url=help_url_for("1.4.4"),
                affects=affected_groups("1.4.4"),
                legal_risk_override=LegalRisk.ALTO,
                nodes=[
                    EvidenceNode(
                        selector="meta[name=viewport]",
                        html=str(data.get("html", "")),
                        failure_summary="; ".join(reasons),
                        measured={
                            "content": data.get("content"),
                            "user_scalable_no": data.get("userScalableNo"),
                            "maximum_scale": max_scale,
                        },
                    )
                ],
            )
        ]
