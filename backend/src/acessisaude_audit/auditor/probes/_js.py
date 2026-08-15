"""Fragmentos JavaScript compartilhados entre sondas.

Mantidos em um módulo próprio por duas razões: evitar divergência entre cópias
do mesmo helper (um seletor CSS gerado de formas diferentes tornaria as
evidências incomparáveis entre sondas) e permitir testar o JavaScript
isoladamente contra as fixtures.

Todos os fragmentos são expressões de função autocontidas, prontas para
``page.evaluate``. Nenhum deles modifica o documento de forma persistente — o
único que marca elementos (:data:`MARK_FOCUSABLES`) remove suas marcas ao final.
"""

from __future__ import annotations

__all__ = [
    "CSS_PATH_FN",
    "FOCUSABLE_SELECTOR",
    "VISIBLE_TEXT_FN",
    "wrap",
]

#: Seletor dos elementos naturalmente alcançáveis por tabulação.
#:
#: Não inclui ``[tabindex="-1"]``: elementos com tabindex negativo são
#: focáveis por script, mas propositalmente fora da ordem de tabulação, e
#: cobrá-los produziria falso positivo.
FOCUSABLE_SELECTOR = (
    "a[href], area[href], button:not([disabled]), input:not([disabled]):not([type='hidden']), "
    "select:not([disabled]), textarea:not([disabled]), summary, "
    "[contenteditable='true'], [tabindex]:not([tabindex='-1'])"
)

#: Gera um seletor CSS curto e estável até um elemento.
#:
#: Estratégia: usa ``id`` quando existir (é único por definição), senão
#: reconstrói o caminho com ``nth-of-type`` limitado a cinco níveis. Caminhos
#: mais longos que isso são ilegíveis no relatório e não ajudam o desenvolvedor
#: a localizar o defeito.
CSS_PATH_FN = """
const cssPath = (el) => {
  if (!el || el.nodeType !== 1) return '';
  if (el.id) return '#' + CSS.escape(el.id);
  const parts = [];
  let node = el;
  let depth = 0;
  while (node && node.nodeType === 1 && depth < 5) {
    let part = node.tagName.toLowerCase();
    if (node.id) { parts.unshift('#' + CSS.escape(node.id)); break; }
    const parent = node.parentElement;
    if (parent) {
      const siblings = Array.from(parent.children).filter(c => c.tagName === node.tagName);
      if (siblings.length > 1) part += ':nth-of-type(' + (siblings.indexOf(node) + 1) + ')';
    }
    parts.unshift(part);
    node = node.parentElement;
    depth++;
  }
  return parts.join(' > ');
};
"""

#: Extrai o texto visível do conteúdo principal da página.
#:
#: Prefere ``main`` / ``[role=main]`` / ``article``; cai para ``body`` quando
#: nenhum marco existir. Descarta ``script``, ``style``, ``nav``, ``header``,
#: ``footer`` e elementos ocultos, para que a métrica de legibilidade meça o
#: conteúdo informativo e não o menu de navegação.
VISIBLE_TEXT_FN = """
const visibleText = () => {
  const root = document.querySelector('main, [role="main"], article') || document.body;
  if (!root) return '';
  const skip = new Set([
    'SCRIPT', 'STYLE', 'NOSCRIPT', 'NAV', 'HEADER', 'FOOTER', 'ASIDE', 'SVG', 'TEMPLATE',
  ]);
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = node.parentElement;
      if (!parent || skip.has(parent.tagName)) return NodeFilter.FILTER_REJECT;
      const cs = getComputedStyle(parent);
      if (cs.display === 'none' || cs.visibility === 'hidden') return NodeFilter.FILTER_REJECT;
      return node.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    }
  });
  const chunks = [];
  let n;
  while ((n = walker.nextNode())) chunks.push(n.textContent.trim());
  return chunks.join(' ').replace(/\\s+/g, ' ').trim();
};
"""


def wrap(body: str, *helpers: str, args: str = "") -> str:
    """Monta uma expressão de função para ``page.evaluate``.

    Args:
        body: Corpo da função, incluindo o ``return``.
        helpers: Fragmentos a inserir antes do corpo (ex. :data:`CSS_PATH_FN`).
        args: Lista de parâmetros da função, ex. ``"limit"``.

    Returns:
        Uma expressão ``(args) => { ... }`` pronta para avaliação.
    """
    prelude = "\n".join(helpers)
    return f"({args}) => {{\n{prelude}\n{body}\n}}"
