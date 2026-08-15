"""Sondas de estrutura semântica — a infraestrutura do leitor de tela.

O leitor de tela não "vê" a página: ele a percorre por meio de duas estruturas
que o desenvolvedor precisa ter construído deliberadamente — os **marcos**
(``main``, ``nav``, ``header``) e a **hierarquia de cabeçalhos**. Quando ambas
faltam, o usuário cego não tem outra opção senão ouvir a página inteira,
linearmente, do início ao fim, a cada navegação.

É exatamente o que o item "falta de leitores de tela" do escopo do projeto
designa: não a ausência do software leitor — que o usuário traz consigo — mas a
ausência, no portal, da estrutura sem a qual esse software é inútil.

Critérios cobertos: 2.4.1 (Ignorar blocos), 1.3.1 (Informações e relações),
2.4.6 (Cabeçalhos e rótulos) e 3.1.1 (Idioma da página).
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

__all__ = [
    "DuplicateIdProbe",
    "HeadingStructureProbe",
    "LandmarkProbe",
    "PageLanguageProbe",
]


_LANDMARK_SCRIPT = wrap(
    """
    const q = (sel) => Array.from(document.querySelectorAll(sel));
    const main = q('main, [role="main"]');
    const nav = q('nav, [role="navigation"]');
    const banner = q('header, [role="banner"]');
    const contentinfo = q('footer, [role="contentinfo"]');

    // Link de salto: primeiro link âncora do documento cujo destino existe.
    const anchors = q('a[href^="#"]').slice(0, 8);
    let skipLink = null;
    for (const a of anchors) {
      const id = decodeURIComponent(a.getAttribute('href').slice(1));
      if (!id) continue;
      const target =
        document.getElementById(id) ||
        document.querySelector('[name="' + CSS.escape(id) + '"]');
      if (target) {
        skipLink = {
          text: (a.textContent || '').trim().slice(0, 120),
          selector: cssPath(a),
          targetId: id,
        };
        break;
      }
    }
    return {
      mainCount: main.length,
      navCount: nav.length,
      bannerCount: banner.length,
      contentinfoCount: contentinfo.length,
      skipLink,
      bodyHtml: document.body ? document.body.outerHTML.slice(0, 200) : '',
    };
    """,
    CSS_PATH_FN,
)


class LandmarkProbe(Probe):
    """Verifica marcos de navegação e mecanismo de salto (WCAG 2.4.1, 1.3.1).

    Duas verificações independentes:

    - **Marco principal.** Ausência de ``main`` (ou ``role="main"``) impede o
      leitor de tela de pular direto ao conteúdo. Veredito determinístico.
    - **Link de salto.** Ausência de âncora funcional para o conteúdo, quando
      *também* não há marco principal, caracteriza violação de 2.4.1: não existe
      nenhum mecanismo de bypass. Quando há marco mas não há link, o achado sai
      como ``INCOMPLETE`` — o marco já constitui mecanismo suficiente segundo a
      técnica ARIA11 do W3C.
    """

    id = "probe.landmarks"
    criteria = ("2.4.1", "1.3.1")
    confidence = Confidence.DETERMINISTIC
    description = "Verifica presença de marcos ARIA e de mecanismo de salto de blocos."

    async def _run(self, context: ProbeContext) -> list[Finding]:
        data: dict[str, Any] | None = await context.evaluate(_LANDMARK_SCRIPT)
        if data is None:
            return []

        has_main = int(data.get("mainCount", 0)) > 0
        skip_link = data.get("skipLink")
        findings: list[Finding] = []

        if not has_main:
            findings.append(
                Finding(
                    rule_id="probe.landmarks.no-main",
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.SERIOUS,
                    criteria=["1.3.1"],
                    summary="A página não declara marco de conteúdo principal (<main>).",
                    description=(
                        'Sem <main> ou role="main", o leitor de tela não distingue o '
                        "conteúdo da moldura de navegação. O usuário cego precisa ouvir "
                        "todo o cabeçalho e todo o menu a cada página que abre — em um "
                        "portal com sessenta itens de menu, isso são minutos de áudio "
                        "antes da primeira informação útil sobre a consulta."
                    ),
                    remediation=(
                        "Envolver o conteúdo específico da página em <main> e reservar "
                        "<header>, <nav> e <footer> para as regiões repetidas."
                    ),
                    help_url=help_url_for("1.3.1"),
                    affects=affected_groups("1.3.1"),
                    nodes=[
                        EvidenceNode(
                            selector="body",
                            html=str(data.get("bodyHtml", "")),
                            failure_summary='Nenhum elemento <main> ou role="main" no documento.',
                            measured={
                                "main": data.get("mainCount"),
                                "nav": data.get("navCount"),
                                "banner": data.get("bannerCount"),
                                "contentinfo": data.get("contentinfoCount"),
                            },
                        )
                    ],
                )
            )

        if not skip_link:
            outcome = Outcome.FAIL if not has_main else Outcome.INCOMPLETE
            findings.append(
                Finding(
                    rule_id="probe.landmarks.no-skip-link",
                    source=FindingSource.PROBE,
                    outcome=outcome,
                    impact=Impact.MODERATE if outcome is Outcome.FAIL else None,
                    criteria=["2.4.1"],
                    summary="Nenhum link de salto para o conteúdo principal foi encontrado.",
                    description=(
                        "Não há âncora funcional no início do documento que permita "
                        "ignorar os blocos repetidos de navegação."
                        + (
                            " Como a página também não declara marco principal, não "
                            "existe mecanismo algum de bypass: o critério 2.4.1 está "
                            "violado."
                            if outcome is Outcome.FAIL
                            else " A página declara marco principal, o que já satisfaz "
                            "o critério pela técnica ARIA11; o link de salto permanece "
                            "recomendável e a verificação fica registrada para revisão."
                        )
                    ),
                    remediation=remediation_for("2.4.1"),
                    help_url=help_url_for("2.4.1"),
                    affects=affected_groups("2.4.1"),
                    nodes=[
                        EvidenceNode(
                            selector="body",
                            failure_summary="Nenhuma âncora interna com destino existente.",
                            measured={"has_main": has_main},
                        )
                    ],
                )
            )

        return findings


_HEADING_SCRIPT = wrap(
    """
    const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6,[role="heading"]'))
      .filter(el => {
        const cs = getComputedStyle(el);
        return cs.display !== 'none' && cs.visibility !== 'hidden';
      })
      .map(el => {
        const aria = el.getAttribute('aria-level');
        const level = aria ? parseInt(aria, 10) : parseInt(el.tagName.slice(1), 10);
        return {
          level: Number.isFinite(level) ? level : null,
          text: (el.textContent || '').trim().slice(0, 120),
          selector: cssPath(el),
          html: el.outerHTML.slice(0, 200),
        };
      })
      .filter(h => h.level !== null);

    const skips = [];
    let previous = null;
    for (const h of headings) {
      if (previous !== null && h.level > previous + 1) {
        skips.push({ ...h, previousLevel: previous });
      }
      previous = h.level;
    }
    const empty = headings.filter(h => h.text.length === 0);
    const h1 = headings.filter(h => h.level === 1);
    return { total: headings.length, h1Count: h1.length, skips, empty, first: headings[0] || null };
    """,
    CSS_PATH_FN,
)


class HeadingStructureProbe(Probe):
    """Avalia a hierarquia de cabeçalhos (WCAG 1.3.1, 2.4.6).

    Três defeitos são distinguidos, porque têm gravidades diferentes:

    - **Cabeçalho vazio** — o leitor de tela anuncia "título nível 2" e nada
      mais. Falha determinística de 2.4.6.
    - **Ausência de H1** — a página não declara do que trata. Falha de 1.3.1.
    - **Salto de nível** (h2 → h4) — quebra o sumário mental que o usuário
      constrói. É defeito real, mas o axe-core o classifica como boa prática e
      há casos legítimos em conteúdo fragmentado; sai como ``INCOMPLETE``.
    """

    id = "probe.heading-structure"
    criteria = ("1.3.1", "2.4.6")
    confidence = Confidence.DETERMINISTIC
    description = "Verifica presença de H1, cabeçalhos vazios e saltos de nível."

    async def _run(self, context: ProbeContext) -> list[Finding]:
        data: dict[str, Any] | None = await context.evaluate(_HEADING_SCRIPT)
        if data is None:
            return []

        findings: list[Finding] = []
        total = int(data.get("total", 0))
        h1_count = int(data.get("h1Count", 0))
        empty = data.get("empty") or []
        skips = data.get("skips") or []

        if total == 0:
            findings.append(
                Finding(
                    rule_id="probe.heading-structure.none",
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.SERIOUS,
                    criteria=["1.3.1", "2.4.6"],
                    summary="A página não possui nenhum cabeçalho.",
                    description=(
                        "Sem cabeçalhos, o principal atalho de navegação do leitor de "
                        "tela — a lista de títulos — fica vazio. A página só pode ser "
                        "percorrida linearmente, do começo ao fim."
                    ),
                    remediation=remediation_for("2.4.6"),
                    help_url=help_url_for("1.3.1"),
                    affects=affected_groups("1.3.1"),
                    nodes=[EvidenceNode(selector="body", failure_summary="Zero cabeçalhos.")],
                )
            )
            return findings

        if h1_count == 0:
            findings.append(
                Finding(
                    rule_id="probe.heading-structure.no-h1",
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.MODERATE,
                    criteria=["1.3.1"],
                    summary="A página não declara um cabeçalho de primeiro nível (H1).",
                    description=(
                        "O H1 é o que informa ao usuário de leitor de tela do que trata a "
                        "página. Sem ele, a hierarquia começa no meio e o assunto "
                        "principal precisa ser inferido."
                    ),
                    remediation=(
                        "Declarar exatamente um H1 por página, descrevendo o serviço ou "
                        "a informação ali oferecida."
                    ),
                    help_url=help_url_for("1.3.1"),
                    affects=affected_groups("1.3.1"),
                    nodes=[
                        EvidenceNode(
                            selector=str((data.get("first") or {}).get("selector", "body")),
                            html=str((data.get("first") or {}).get("html", "")),
                            failure_summary=(
                                f"Primeiro cabeçalho da página é de nível "
                                f"{(data.get('first') or {}).get('level')}."
                            ),
                            measured={"headings_total": total, "h1_count": h1_count},
                        )
                    ],
                )
            )

        if empty:
            findings.append(
                Finding(
                    rule_id="probe.heading-structure.empty",
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.SERIOUS,
                    criteria=["2.4.6"],
                    summary=f"{len(empty)} cabeçalho(s) sem texto acessível.",
                    description=(
                        "Cabeçalhos vazios são anunciados pelo leitor de tela como itens "
                        "de estrutura sem conteúdo, poluindo a lista de títulos e "
                        "quebrando a expectativa de que cada entrada leve a algum lugar."
                    ),
                    remediation=remediation_for("2.4.6"),
                    help_url=help_url_for("2.4.6"),
                    affects=affected_groups("2.4.6"),
                    nodes=[
                        EvidenceNode(
                            selector=str(h.get("selector", "")),
                            html=str(h.get("html", "")),
                            failure_summary=f"Cabeçalho de nível {h.get('level')} sem texto.",
                            measured={"level": h.get("level")},
                        )
                        for h in empty[:10]
                    ],
                )
            )

        if skips:
            findings.append(
                Finding(
                    rule_id="probe.heading-structure.level-skip",
                    source=FindingSource.PROBE,
                    outcome=Outcome.INCOMPLETE,
                    criteria=["1.3.1"],
                    summary=f"{len(skips)} salto(s) de nível na hierarquia de cabeçalhos.",
                    description=(
                        "A sequência de níveis pula degraus (por exemplo, de H2 para H4). "
                        "Isso sugere que os cabeçalhos foram escolhidos pelo tamanho da "
                        "fonte, e não pela estrutura do conteúdo. Há casos legítimos em "
                        "páginas com blocos independentes, razão pela qual o achado fica "
                        "registrado para revisão humana em vez de reprovado."
                    ),
                    remediation=(
                        "Escolher o nível pelo lugar na hierarquia do conteúdo e ajustar "
                        "o tamanho visual por CSS."
                    ),
                    help_url=help_url_for("1.3.1"),
                    affects=affected_groups("1.3.1"),
                    nodes=[
                        EvidenceNode(
                            selector=str(s.get("selector", "")),
                            html=str(s.get("html", "")),
                            failure_summary=(
                                f"Nível {s.get('previousLevel')} seguido diretamente de "
                                f"nível {s.get('level')} ({s.get('text')!r})."
                            ),
                            measured={
                                "from_level": s.get("previousLevel"),
                                "to_level": s.get("level"),
                            },
                        )
                        for s in skips[:10]
                    ],
                )
            )

        return findings


_LANG_SCRIPT = """
() => {
  const html = document.documentElement;
  return {
    lang: html.getAttribute('lang'),
    xmlLang: html.getAttribute('xml:lang'),
    html: html.outerHTML.slice(0, 160),
  };
}
"""


class PageLanguageProbe(Probe):
    """Verifica a declaração de idioma do documento (WCAG 3.1.1).

    O impacto é frequentemente subestimado por quem enxerga: sem ``lang``, o
    sintetizador de voz aplica a fonética do idioma padrão do sistema. "Cartão
    Nacional de Saúde" lido com fonemas ingleses não é uma leitura com sotaque —
    é ruído. A informação foi publicada e não foi comunicada.

    Distingue três situações:

    - Atributo ausente → ``FAIL``.
    - Atributo presente e português → conforme.
    - Atributo presente e não português → ``INCOMPLETE``. A página pode ser
      legitimamente estrangeira, ainda que improvável em portal público
      brasileiro; cabe verificação humana.
    """

    id = "probe.page-language"
    criteria = ("3.1.1",)
    confidence = Confidence.DETERMINISTIC
    description = "Verifica o atributo lang do elemento html."

    async def _run(self, context: ProbeContext) -> list[Finding]:
        data: dict[str, Any] | None = await context.evaluate(_LANG_SCRIPT)
        if data is None:
            return []

        lang = (data.get("lang") or data.get("xmlLang") or "").strip()
        if not lang:
            return [
                Finding(
                    rule_id="probe.page-language.missing",
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.SERIOUS,
                    criteria=list(self.criteria),
                    summary="O documento não declara o idioma (atributo lang ausente).",
                    description=(
                        "Sem declaração de idioma, o leitor de tela aplica a fonética do "
                        "idioma configurado no sistema do usuário. Termos de saúde em "
                        "português pronunciados com fonemas de outro idioma tornam-se "
                        "ininteligíveis: a informação pública existe, mas não chega."
                    ),
                    remediation=remediation_for("3.1.1"),
                    help_url=help_url_for("3.1.1"),
                    affects=affected_groups("3.1.1"),
                    legal_risk_override=LegalRisk.ALTO,
                    nodes=[
                        EvidenceNode(
                            selector="html",
                            html=str(data.get("html", "")),
                            failure_summary="Elemento <html> sem atributo lang.",
                            measured={"lang": None},
                        )
                    ],
                )
            ]

        if not lang.lower().startswith("pt"):
            return [
                Finding(
                    rule_id="probe.page-language.unexpected",
                    source=FindingSource.PROBE,
                    outcome=Outcome.INCOMPLETE,
                    criteria=list(self.criteria),
                    summary=f"O documento declara idioma {lang!r}, não português.",
                    description=(
                        "Portais públicos brasileiros devem declarar 'pt-BR'. Um idioma "
                        "diverso pode ser legítimo em versão internacional da página, ou "
                        "pode ser resíduo de template estrangeiro — caso em que a "
                        "pronúncia sintética fica comprometida. Requer verificação."
                    ),
                    remediation=remediation_for("3.1.1"),
                    help_url=help_url_for("3.1.1"),
                    affects=affected_groups("3.1.1"),
                    nodes=[
                        EvidenceNode(
                            selector="html",
                            html=str(data.get("html", "")),
                            failure_summary=f"lang={lang!r}.",
                            measured={"lang": lang},
                        )
                    ],
                )
            ]

        return []


_DUPLICATE_ID_SCRIPT = wrap(
    """
    const porId = new Map();
    for (const el of document.querySelectorAll('[id]')) {
      const id = el.getAttribute('id');
      if (!id) continue;
      if (!porId.has(id)) porId.set(id, []);
      porId.get(id).push(el);
    }

    // Referências que dependem de unicidade do id para funcionar.
    const referencias = new Set();
    for (const el of document.querySelectorAll('label[for]')) {
      referencias.add(el.getAttribute('for'));
    }
    for (const attr of ['aria-labelledby', 'aria-describedby', 'aria-controls',
                        'aria-owns', 'aria-errormessage', 'aria-activedescendant']) {
      for (const el of document.querySelectorAll('[' + attr + ']')) {
        for (const id of (el.getAttribute(attr) || '').split(/\\s+/)) {
          if (id) referencias.add(id);
        }
      }
    }

    const duplicados = [];
    for (const [id, elementos] of porId) {
      if (elementos.length < 2) continue;
      duplicados.push({
        id,
        ocorrencias: elementos.length,
        referenciado: referencias.has(id),
        selector: cssPath(elementos[1]),
        html: elementos[1].outerHTML.slice(0, 300),
        tags: elementos.map(e => e.tagName.toLowerCase()).slice(0, 6),
      });
      if (duplicados.length >= 15) break;
    }
    return duplicados;
    """,
    CSS_PATH_FN,
)


class DuplicateIdProbe(Probe):
    """Detecta identificadores duplicados no documento (WCAG 2.1, critério 4.1.1).

    Por que esta sonda existe
    -------------------------
    O critério 4.1.1 (Análise) foi **removido na WCAG 2.2**, e o axe-core
    acompanhou a norma: desde a versão 4.x, a regra ``duplicate-id`` deixou de
    integrar os conjuntos ``wcag2a``/``wcag21a`` e passou a boa prática. Como a
    referência normativa deste projeto é a **WCAG 2.1** — que é o que o Decreto
    5.296/2004 e o eMAG 3.1 incorporam na prática administrativa brasileira —,
    aceitar essa omissão deixaria um critério do escopo declarado sem qualquer
    verificação, contradizendo a cobertura reportada.

    A situação é registrada em ``docs/metodologia/limites-do-axe-core.md``: é um
    caso em que a ferramenta de referência e a norma de referência divergem, e o
    projeto opta por seguir a norma que rege o objeto auditado.

    Gradação do veredito, por consequência prática:

    - ``id`` duplicado **e referenciado** por ``label[for]`` ou por atributo
      ARIA → ``FAIL``. A associação é ambígua: o navegador resolve para o
      primeiro elemento, e o rótulo do segundo campo simplesmente não existe
      para a tecnologia assistiva.
    - ``id`` duplicado e **não referenciado** → ``INCOMPLETE``. É marcação
      malformada e fonte de defeito futuro, mas não produz, no estado atual da
      página, barreira demonstrável.
    """

    id = "probe.id-duplicado"
    criteria = ("4.1.1",)
    confidence = Confidence.DETERMINISTIC
    description = (
        "Identifica atributos id repetidos, distinguindo os que quebram "
        "associações de rótulo dos que apenas violam a boa formação do HTML."
    )

    async def _run(self, context: ProbeContext) -> list[Finding]:
        duplicados: list[dict[str, Any]] | None = await context.evaluate(_DUPLICATE_ID_SCRIPT)
        if not duplicados:
            return []

        criticos = [d for d in duplicados if d.get("referenciado")]
        inertes = [d for d in duplicados if not d.get("referenciado")]
        achados: list[Finding] = []

        def _nos(itens: list[dict[str, Any]]) -> list[EvidenceNode]:
            return [
                EvidenceNode(
                    selector=str(d.get("selector", "")),
                    html=str(d.get("html", "")),
                    failure_summary=(
                        f"id={d.get('id')!r} aparece {d.get('ocorrencias')} vezes "
                        f"(elementos: {', '.join(d.get('tags') or [])})."
                    ),
                    measured={
                        "id": d.get("id"),
                        "ocorrencias": d.get("ocorrencias"),
                        "referenciado": d.get("referenciado"),
                    },
                )
                for d in itens[:10]
            ]

        if criticos:
            achados.append(
                Finding(
                    rule_id=self.id,
                    source=FindingSource.PROBE,
                    outcome=Outcome.FAIL,
                    impact=Impact.SERIOUS,
                    criteria=list(self.criteria),
                    summary=(
                        f"{len(criticos)} identificador(es) duplicado(s) quebram "
                        "associações de rótulo ou de descrição."
                    ),
                    description=(
                        "Os identificadores abaixo se repetem no documento e são alvo "
                        "de label[for] ou de atributo ARIA. Como o navegador resolve a "
                        "referência para o primeiro elemento encontrado, os demais "
                        "ficam sem rótulo acessível: o leitor de tela anuncia um campo "
                        "de formulário sem dizer que dado ele pede."
                    ),
                    remediation=(
                        "Tornar cada id único no documento. Em páginas montadas a "
                        "partir de componentes repetidos, gerar sufixo por instância."
                    ),
                    help_url=help_url_for("4.1.1"),
                    affects=affected_groups("4.1.1"),
                    legal_risk_override=LegalRisk.ALTO,
                    nodes=_nos(criticos),
                )
            )

        if inertes:
            achados.append(
                Finding(
                    rule_id="probe.id-duplicado.inerte",
                    source=FindingSource.PROBE,
                    outcome=Outcome.INCOMPLETE,
                    criteria=list(self.criteria),
                    summary=(
                        f"{len(inertes)} identificador(es) duplicado(s) sem referência associada."
                    ),
                    description=(
                        "Marcação malformada que ainda não produz barreira demonstrável, "
                        "por nenhum atributo apontar para estes identificadores. "
                        "Permanece como risco: qualquer script ou rótulo futuro que os "
                        "referencie passará a resolver para o elemento errado."
                    ),
                    remediation=remediation_for("4.1.1"),
                    help_url=help_url_for("4.1.1"),
                    affects=affected_groups("4.1.1"),
                    nodes=_nos(inertes),
                )
            )

        return achados
