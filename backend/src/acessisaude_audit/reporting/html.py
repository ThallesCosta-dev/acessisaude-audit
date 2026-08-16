"""Geração do relatório HTML de auditoria.

O relatório é o produto que chega ao gestor público — quem, na prática, decide
se a barreira será corrigida. Três princípios orientam sua construção:

1. **O relatório obedece às regras que audita.** Ele declara idioma, tem
   hierarquia de cabeçalhos íntegra, marcos ARIA, link de salto, contraste
   suficiente e nenhuma informação transmitida apenas por cor. Uma ferramenta
   de acessibilidade que emitisse um relatório inacessível se desqualificaria.
2. **Nenhum número aparece sozinho.** Todo índice vem acompanhado da escala, do
   sentido (maior é melhor ou pior) e da cobertura da medição.
3. **Os limites vêm no corpo, não em nota de rodapé.** A cobertura parcial da
   verificação automática e as lacunas da amostra são exibidas na mesma seção
   dos resultados, para que não sejam lidas seletivamente.

Saída sem JavaScript e sem recursos externos: o arquivo é autocontido e pode ser
arquivado como evidência estável, aberto anos depois, ou anexado a um processo.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from acessisaude_audit.domain.lbi import provision
from acessisaude_audit.domain.mapping import LegalRisk
from acessisaude_audit.domain.models import Finding, Outcome, ScanResult
from acessisaude_audit.domain.scoring import (
    DEFAULT_PARAMETERS,
    ScoringParameters,
    score_scan,
    summarize_by_group,
)
from acessisaude_audit.domain.wcag import DeficiencyGroup, criterion
from acessisaude_audit.logging_setup import get_logger

__all__ = ["formatar_reais", "render_report", "write_report"]

logger = get_logger(__name__)

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

#: Ordem de apresentação dos achados: do mais grave ao menos grave.
_RISK_ORDER: tuple[LegalRisk, ...] = (
    LegalRisk.CRITICO,
    LegalRisk.ALTO,
    LegalRisk.MODERADO,
    LegalRisk.BAIXO,
)

#: Rótulos legíveis dos grupos afetados.
_GROUP_LABELS: dict[DeficiencyGroup, str] = {
    DeficiencyGroup.BLINDNESS: "Pessoas cegas (usuárias de leitor de tela)",
    DeficiencyGroup.LOW_VISION: "Pessoas com baixa visão",
    DeficiencyGroup.COLOR_VISION: "Pessoas com deficiência na visão de cores",
    DeficiencyGroup.DEAFNESS: "Pessoas surdas ou com deficiência auditiva",
    DeficiencyGroup.MOTOR: "Pessoas com deficiência motora (navegação sem mouse)",
    DeficiencyGroup.COGNITIVE: "Pessoas com deficiência intelectual ou neurodivergentes",
    DeficiencyGroup.SPEECH: "Pessoas usuárias de comando por voz",
    DeficiencyGroup.PHOTOSENSITIVITY: "Pessoas com epilepsia fotossensível",
    DeficiencyGroup.LOW_BANDWIDTH: "Usuários com plano de dados limitado ou aparelho antigo",
}


def _environment() -> Environment:
    """Ambiente Jinja com autoescape — o HTML recebe conteúdo de páginas reais.

    Autoescape aqui não é higiene abstrata: os trechos de HTML coletados como
    evidência vêm de portais de terceiros e serão renderizados dentro do
    relatório. Sem escape, um portal com marcação hostil injetaria conteúdo no
    documento entregue ao gestor.
    """
    env = Environment(
        loader=FileSystemLoader(_TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Dicionário posicional em vez de argumentos nomeados: a assinatura de
    # `Environment.globals.update` é inferida de forma estreita pelos stubs do
    # Jinja e rejeitaria funções passadas por palavra-chave.
    helpers: dict[str, Any] = {
        "rotulo_grupo": _group_label,
        "titulo_criterio": _criterion_title,
        "rotulo_dispositivo": _provision_label,
        "moeda": formatar_reais,
    }
    env.globals.update(helpers)
    return env


def formatar_reais(valor: float) -> str:
    """Formata um valor em reais com precisão adaptativa.

    Duas casas decimais são a convenção para preços, e são inadequadas aqui: com
    o preço de referência coletado (R$ 3,00/GiB), o custo de um único acesso fica
    na casa dos milésimos, e ``%.2f`` exibiria "R$ 0,00" para praticamente toda
    página — apagando justamente o indicador que se quer comunicar.

    A regra: abaixo de R$ 0,01, exibe-se em **centavos com uma casa**, que é a
    unidade em que a grandeza é inteligível ("0,7 centavo por acesso"). A partir
    de R$ 0,01, volta-se à convenção monetária usual.
    """
    if valor < 0.01:
        centavos = valor * 100
        # Em português, a flexão acompanha a grandeza, não a parte inteira:
        # abaixo de dois, singular ("0,7 centavo", "1,5 centavo"); de dois em
        # diante, plural.
        plural = "s" if centavos >= 2 else ""
        return f"{centavos:.1f} centavo{plural}".replace(".", ",")
    return f"R$ {valor:.2f}".replace(".", ",")


def _group_label(group: DeficiencyGroup | str) -> str:
    """Rótulo legível de um grupo afetado."""
    if isinstance(group, str):
        try:
            group = DeficiencyGroup(group)
        except ValueError:
            return group
    return _GROUP_LABELS.get(group, group.value)


def _criterion_title(criterion_id: str) -> str:
    """Título em português do critério WCAG."""
    try:
        return criterion(criterion_id).title_pt
    except KeyError:
        return "critério fora do escopo A/AA"


def _provision_label(key: str) -> str:
    """Rótulo curto do dispositivo normativo."""
    try:
        return provision(key).label
    except KeyError:
        return key


def _group_findings_by_risk(scan: ScanResult) -> list[tuple[str, list[Finding]]]:
    """Agrupa violações por risco jurídico, na ordem de gravidade decrescente.

    Achados sem risco atribuído são reunidos ao final, sob rótulo próprio, em
    vez de descartados: um achado que a matriz ainda não qualificou é uma
    lacuna do projeto, e ocultá-lo esconderia essa lacuna.
    """
    buckets: dict[str, list[Finding]] = {r.value: [] for r in _RISK_ORDER}
    buckets["nao_classificado"] = []

    for page in scan.pages:
        for finding in page.violations:
            risk = finding.legal_risk
            buckets[risk.value if risk else "nao_classificado"].append(finding)

    for items in buckets.values():
        items.sort(key=lambda f: f.occurrences, reverse=True)

    return [(name, items) for name, items in buckets.items() if items]


def _incomplete_findings(scan: ScanResult) -> list[Finding]:
    """Achados que requerem revisão humana, ordenados por volume."""
    items = [f for page in scan.pages for f in page.findings if f.outcome is Outcome.INCOMPLETE]
    items.sort(key=lambda f: f.occurrences, reverse=True)
    return items


def render_report(scan: ScanResult, *, params: ScoringParameters = DEFAULT_PARAMETERS) -> str:
    """Renderiza o relatório HTML completo de uma varredura.

    Args:
        scan: Resultado da varredura.
        params: Parâmetros de índice usados no cálculo — devem ser os mesmos da
            coleta, sob pena de o relatório exibir números que ninguém consegue
            reproduzir.

    Returns:
        HTML autocontido, pronto para gravação.
    """
    score = score_scan(scan, params)
    template = _environment().get_template("report.html.j2")
    return template.render(
        scan=scan,
        score=score,
        achados=_group_findings_by_risk(scan),
        incompletos=_incomplete_findings(scan),
        grupos=summarize_by_group(score),
        gerado_em=datetime.now(UTC),
    )


def write_report(
    scan: ScanResult,
    directory: Path,
    *,
    params: ScoringParameters = DEFAULT_PARAMETERS,
) -> Path:
    """Renderiza e grava o relatório em ``directory``.

    Returns:
        Caminho do arquivo gerado.
    """
    directory.mkdir(parents=True, exist_ok=True)
    stamp = scan.started_at.strftime("%Y%m%d-%H%M%S")
    path = directory / f"relatorio__{scan.target_id}__{stamp}.html"
    path.write_text(render_report(scan, params=params), encoding="utf-8")
    logger.info("relatório HTML gerado", extra={"arquivo": str(path)})
    return path
