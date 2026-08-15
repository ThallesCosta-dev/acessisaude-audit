"""Execução do axe-core e tradução de seus resultados para o domínio.

O axe-core é o motor de regras determinístico do projeto. Este módulo faz três
coisas e nenhuma a mais:

1. **Injeta** a cópia vendorizada em todos os quadros da página (incluindo
   ``iframe``, comuns em portais públicos que embutem widgets de terceiros).
2. **Executa** apenas os conjuntos de regras com lastro normativo — as tags
   ``wcag2a``, ``wcag2aa``, ``wcag21a`` e ``wcag21aa``. As regras
   ``best-practice`` são deliberadamente excluídas: são recomendações da Deque,
   não requisitos de conformidade, e usá-las inflaria artificialmente a
   contagem de "violações legais".
3. **Traduz** o JSON do axe para :class:`~acessisaude_audit.domain.models.Finding`,
   acoplando a cada achado seu mapeamento jurídico.

O que este módulo *não* faz: julgar. Resultados ``incomplete`` do axe são
preservados como :attr:`~acessisaude_audit.domain.models.Outcome.INCOMPLETE` e
jamais convertidos em violação — a diferença entre "detectei uma falha" e
"detectei algo que precisa de olhos humanos" é o que separa esta ferramenta de
um gerador de números.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page

from acessisaude_audit.domain.mapping import mapping_for
from acessisaude_audit.domain.models import (
    EvidenceNode,
    Finding,
    FindingSource,
    Impact,
    Outcome,
)
from acessisaude_audit.domain.wcag import DeficiencyGroup, criterion_from_axe_tag
from acessisaude_audit.logging_setup import get_logger

__all__ = ["AxeResult", "AxeRunner", "vendored_axe_path"]

logger = get_logger(__name__)

#: Chaves de ``check.data`` que carregam medições úteis como evidência.
#:
#: O axe devolve dicionários heterogêneos por tipo de regra; extrair só o que é
#: interpretável evita despejar ruído no dataset de pesquisa.
_MEASURED_KEYS = frozenset(
    {
        "contrastRatio",
        "expectedContrastRatio",
        "fgColor",
        "bgColor",
        "fontSize",
        "fontWeight",
        "messageKey",
        "missingAttr",
        "role",
        "name",
        "values",
    }
)


@cache
def vendored_axe_path() -> Path:
    """Caminho da cópia vendorizada do ``axe.min.js``.

    Procura primeiro ao lado do pacote instalado (cenário de wheel) e depois no
    diretório ``vendor/`` do repositório (cenário de desenvolvimento).

    Raises:
        FileNotFoundError: Se nenhuma cópia for encontrada — situação que
            invalidaria toda a auditoria e por isso falha alto e cedo.
    """
    here = Path(__file__).resolve()
    candidates = (
        here.parents[1] / "vendor" / "axe.min.js",  # instalado no pacote
        here.parents[3] / "vendor" / "axe.min.js",  # backend/vendor no repo
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "axe.min.js não encontrado. Rode `npm pack axe-core` em backend/vendor "
        "conforme backend/vendor/README.md."
    )


class AxeResult:
    """Resultado bruto de uma execução do axe, com acesso tipado.

    Guardar o bruto além do traduzido permite reprocessar datasets antigos se a
    tradução para o domínio mudar, sem precisar revarrer os portais.
    """

    __slots__ = ("raw",)

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw

    @property
    def engine_version(self) -> str | None:
        """Versão do axe-core que produziu o resultado."""
        engine = self.raw.get("testEngine") or {}
        version = engine.get("version")
        return str(version) if version else None

    @property
    def violations(self) -> list[dict[str, Any]]:
        """Regras com falha confirmada."""
        return list(self.raw.get("violations") or [])

    @property
    def incomplete(self) -> list[dict[str, Any]]:
        """Regras cujo veredito depende de revisão humana."""
        return list(self.raw.get("incomplete") or [])

    @property
    def passes(self) -> list[dict[str, Any]]:
        """Regras aprovadas — usadas para aferir cobertura efetiva."""
        return list(self.raw.get("passes") or [])

    @property
    def inapplicable(self) -> list[dict[str, Any]]:
        """Regras sem elemento correspondente na página."""
        return list(self.raw.get("inapplicable") or [])


class AxeRunner:
    """Injeta e executa o axe-core em uma página do Playwright."""

    def __init__(
        self,
        tags: tuple[str, ...],
        *,
        script_path: Path | None = None,
        max_html_chars: int = 400,
    ) -> None:
        """
        Args:
            tags: Conjuntos de regras a executar, ex. ``("wcag2a", "wcag2aa")``.
            script_path: Caminho alternativo para ``axe.min.js``. ``None`` usa a
                cópia vendorizada.
            max_html_chars: Truncamento do HTML de evidência.
        """
        self._tags = tags
        self._script_path = script_path or vendored_axe_path()
        self._max_html = max_html_chars
        self._source: str | None = None

    @property
    def source(self) -> str:
        """Código-fonte do axe-core, lido uma única vez por processo."""
        if self._source is None:
            self._source = self._script_path.read_text(encoding="utf-8")
        return self._source

    async def run(self, page: Page) -> AxeResult | None:
        """Executa o axe-core na página e devolve o resultado bruto.

        Returns:
            :class:`AxeResult`, ou ``None`` se a injeção ou a execução falharem
            — caso em que a página é registrada sem achados do axe, e não com
            zero violações. A distinção é essencial: "não medido" não é
            "conforme".
        """
        if not await self._inject(page):
            return None

        options = {
            "runOnly": {"type": "tag", "values": list(self._tags)},
            "resultTypes": ["violations", "incomplete"],
            # Nós relacionados inflam o JSON sem acrescentar evidência acionável.
            "elementRef": False,
            "reporter": "v1",
        }
        script = (
            "async (options) => {"
            "  if (typeof window.axe === 'undefined') { return null; }"
            "  try { return await window.axe.run(document, options); }"
            "  catch (e) { return { __error: String(e && e.message || e) }; }"
            "}"
        )
        try:
            raw = await page.evaluate(script, options)
        except PlaywrightError as exc:
            logger.warning("axe.run falhou", extra={"url": page.url, "erro": str(exc)})
            return None

        if not isinstance(raw, dict):
            logger.warning("axe.run não retornou objeto", extra={"url": page.url})
            return None
        if "__error" in raw:
            logger.warning(
                "axe.run lançou exceção na página",
                extra={"url": page.url, "erro": raw["__error"]},
            )
            return None
        return AxeResult(raw)

    async def _inject(self, page: Page) -> bool:
        """Injeta o axe-core no quadro principal e nos subquadros.

        A injeção em subquadros é necessária porque portais públicos embutem
        mapas, players e formulários de terceiros em ``iframe``; sem ela, essas
        regiões ficariam fora da auditoria e o índice sairia otimista.
        """
        injected_main = False
        for frame in page.frames:
            try:
                await frame.evaluate(self.source)
                if frame is page.main_frame:
                    injected_main = True
            except PlaywrightError as exc:
                # Quadros cross-origin sem CORS não são inspecionáveis. É uma
                # limitação do navegador, não um defeito: registramos e seguimos.
                logger.debug(
                    "quadro não inspecionável",
                    extra={"frame_url": frame.url, "erro": str(exc)},
                )
        if not injected_main:
            logger.warning("não foi possível injetar o axe-core", extra={"url": page.url})
        return injected_main

    # ------------------------------------------------------------------ tradução

    def to_findings(
        self,
        result: AxeResult,
        *,
        page_url: str,
        viewport_name: str,
    ) -> list[Finding]:
        """Traduz o resultado do axe em achados do domínio.

        Regras cujas tags não correspondem a nenhum critério WCAG A/AA modelado
        são descartadas: sem vínculo normativo, não há afirmação jurídica
        possível — e este projeto não reporta o que não consegue fundamentar.
        """
        findings: list[Finding] = []
        for rule in result.violations:
            finding = self._rule_to_finding(
                rule, Outcome.FAIL, page_url=page_url, viewport_name=viewport_name
            )
            if finding is not None:
                findings.append(finding)
        for rule in result.incomplete:
            finding = self._rule_to_finding(
                rule, Outcome.INCOMPLETE, page_url=page_url, viewport_name=viewport_name
            )
            if finding is not None:
                findings.append(finding)
        return findings

    def _rule_to_finding(
        self,
        rule: dict[str, Any],
        outcome: Outcome,
        *,
        page_url: str,
        viewport_name: str,
    ) -> Finding | None:
        criteria = _criteria_from_tags(rule.get("tags") or [])
        if not criteria:
            return None

        impact = _impact(rule.get("impact"))
        affects = _affected_groups(criteria)
        remediation = _remediation(criteria)

        return Finding(
            rule_id=str(rule.get("id", "desconhecida")),
            source=FindingSource.AXE_CORE,
            outcome=outcome,
            impact=impact if outcome is Outcome.FAIL else None,
            criteria=criteria,
            summary=str(rule.get("help") or rule.get("description") or "").strip(),
            description=str(rule.get("description") or "").strip(),
            remediation=remediation,
            help_url=rule.get("helpUrl"),
            affects=affects,
            nodes=[self._node(n) for n in (rule.get("nodes") or [])],
            page_url=page_url,
            viewport=viewport_name,
        )

    def _node(self, node: dict[str, Any]) -> EvidenceNode:
        target = node.get("target") or []
        selector = " ".join(str(t) for t in target) if target else ""
        html = str(node.get("html") or "")
        if len(html) > self._max_html:
            html = html[: self._max_html] + "…"
        return EvidenceNode(
            selector=selector,
            html=html,
            failure_summary=str(node.get("failureSummary") or "").strip(),
            target_frame=[str(t) for t in target[:-1]] if len(target) > 1 else [],
            measured=_measured(node),
        )


def _criteria_from_tags(tags: list[Any]) -> list[str]:
    """Extrai os identificadores WCAG das tags do axe, sem duplicatas."""
    seen: dict[str, None] = {}
    for tag in tags:
        sc = criterion_from_axe_tag(str(tag))
        if sc is not None:
            seen.setdefault(sc.id, None)
    return list(seen)


def _impact(raw: Any) -> Impact | None:
    """Converte o ``impact`` textual do axe no enum do domínio."""
    if not raw:
        return None
    try:
        return Impact(str(raw))
    except ValueError:  # pragma: no cover - vocabulário novo do axe
        logger.debug("impacto desconhecido reportado pelo axe", extra={"impacto": raw})
        return None


def _affected_groups(criteria: list[str]) -> list[DeficiencyGroup]:
    """União dos grupos afetados pelos critérios violados, em ordem estável."""
    from acessisaude_audit.domain.wcag import criterion

    seen: dict[DeficiencyGroup, None] = {}
    for crit_id in criteria:
        try:
            for group in criterion(crit_id).affects:
                seen.setdefault(group, None)
        except KeyError:  # pragma: no cover
            continue
    return sorted(seen, key=lambda g: g.value)


def _remediation(criteria: list[str]) -> str:
    """Concatena as condutas corretivas dos critérios violados."""
    parts: list[str] = []
    for crit_id in criteria:
        m = mapping_for(crit_id)
        if m and m.remediation not in parts:
            parts.append(m.remediation)
    return " ".join(parts)


def _measured(node: dict[str, Any]) -> dict[str, Any]:
    """Coleta os valores medidos pelas verificações que reprovaram o nó.

    Percorre os três grupos de checagem do axe (``any``, ``all``, ``none``) e
    retém apenas as chaves de :data:`_MEASURED_KEYS`. É o que transforma
    "contraste insuficiente" em "2.91:1 onde se exigem 4.5:1, texto #8a8a8a
    sobre #ffffff" — a diferença entre uma alegação e uma prova.
    """
    out: dict[str, Any] = {}
    for group in ("any", "all", "none"):
        for check in node.get(group) or []:
            data = check.get("data")
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in _MEASURED_KEYS and _is_jsonable(value):
                        out.setdefault(key, value)
            elif data is not None and _is_jsonable(data):
                out.setdefault(str(check.get("id", "data")), data)
    return out


def _is_jsonable(value: Any) -> bool:
    """Evita que estruturas exóticas do axe quebrem a serialização do dataset."""
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return False
    return True
