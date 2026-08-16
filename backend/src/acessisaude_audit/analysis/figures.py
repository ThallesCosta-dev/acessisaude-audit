"""Figuras do artigo.

Geradas por código, a partir do dataset, e não montadas à mão — de modo que
qualquer figura publicada possa ser reproduzida com um comando e refeita quando
a coleta for ampliada.

Decisões de apresentação, todas com justificativa:

**Escala de cinza por padrão.** Muitos periódicos brasileiros da área de saúde
coletiva ainda imprimem em preto e branco. Uma figura que só se lê em cores
perde informação exatamente no meio pelo qual será mais lida.

**Nenhuma informação apenas por cor.** Séries recebem também padrão de hachura
ou marcador. Seria contraditório publicar, em um artigo sobre acessibilidade,
uma figura que viola o critério 1.4.1.

**Sem eixo truncado.** Eixos de índice começam em zero. Truncar amplifica
visualmente diferenças pequenas — prática comum e enganosa em comparações
entre instituições.

**Legenda descreve o achado, não o gráfico.** "Contraste insuficiente ocorre em
83% das páginas auditadas", não "Gráfico de barras de prevalência".
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from acessisaude_audit.domain.wcag import criterion
from acessisaude_audit.logging_setup import get_logger

if TYPE_CHECKING:  # pragma: no cover
    import pandas as pd
    from matplotlib.figure import Figure

__all__ = [
    "apply_style",
    "figure_criterion_prevalence",
    "figure_data_cost",
    "figure_exclusion_profile",
    "figure_index_by_sphere",
    "save_all",
]

logger = get_logger(__name__)

#: Padrões de hachura para distinguir séries sem depender de cor.
_HATCHES = ("", "///", "...", "xxx", "\\\\\\", "+++")

#: Tons de cinza com contraste suficiente entre si e sobre branco.
_GRAYS = ("#2b2b2b", "#5a5a5a", "#828282", "#a8a8a8", "#c9c9c9")


def _plt() -> Any:
    try:
        import matplotlib

        matplotlib.use("Agg")  # sem servidor gráfico: gera arquivo, não janela
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            'As figuras exigem o extra "analysis": pip install -e "backend[analysis]"'
        ) from exc
    return plt


def apply_style() -> None:
    """Aplica o estilo tipográfico usado em todas as figuras."""
    plt = _plt()
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "font.family": "sans-serif",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linestyle": ":",
            "legend.frameon": False,
        }
    )


def figure_criterion_prevalence(prevalence: pd.DataFrame, *, top: int = 15) -> Figure:
    """Prevalência dos critérios mais violados.

    Barras horizontais ordenadas — a leitura correta é comparar comprimentos, e
    o rótulo de cada critério é longo demais para caber no eixo x.

    Args:
        prevalence: Saída de
            :func:`~acessisaude_audit.analysis.dataset.criterion_prevalence`.
        top: Quantos critérios exibir.
    """
    plt = _plt()
    apply_style()

    data = prevalence.head(top).iloc[::-1]  # invertido: maior no topo
    fig, ax = plt.subplots(figsize=(7.0, max(3.0, 0.32 * len(data) + 1.2)))

    rotulos = [f"{row.criterio} {row.titulo}" for row in data.itertuples()]
    valores = data["prevalencia"] * 100

    # Nível A recebe hachura distinta de AA: a distinção é normativa e
    # relevante, e não pode depender de cor.
    hatches = ["" if lvl == "A" else "///" for lvl in data["nivel"]]
    bars = ax.barh(rotulos, valores, color=_GRAYS[1], edgecolor="black", linewidth=0.6)
    for bar, hatch in zip(bars, hatches, strict=True):
        bar.set_hatch(hatch)

    for bar, valor in zip(bars, valores, strict=True):
        ax.text(
            valor + 1.2,
            bar.get_y() + bar.get_height() / 2,
            f"{valor:.0f}%",
            va="center",
            fontsize=8,
        )

    ax.set_xlim(0, 100)  # sem truncamento
    ax.set_xlabel("Páginas em que o critério é violado (%)")
    ax.set_title("Prevalência de violação por critério de sucesso WCAG 2.1")

    from matplotlib.patches import Patch

    ax.legend(
        handles=[
            Patch(facecolor=_GRAYS[1], edgecolor="black", label="Nível A"),
            Patch(facecolor=_GRAYS[1], edgecolor="black", hatch="///", label="Nível AA"),
        ],
        loc="lower right",
    )
    return fig


def figure_exclusion_profile(profile: pd.DataFrame) -> Figure:
    """Ocorrências de barreira por grupo de pessoas afetado.

    A figura que traduz "quantos defeitos" em "quem fica de fora" — a leitura
    que sustenta o argumento jurídico do artigo.
    """
    plt = _plt()
    apply_style()

    rotulos = {
        "cegueira": "Pessoas cegas",
        "baixa_visao": "Baixa visão",
        "visao_de_cores": "Visão de cores",
        "surdez": "Surdez",
        "motora": "Deficiência motora",
        "cognitiva_neurodivergencia": "Def. intelectual / neurodivergência",
        "fala": "Comando por voz",
        "fotossensibilidade": "Fotossensibilidade",
        "baixa_conectividade": "Plano de dados limitado",
    }

    data = profile.iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.0, max(3.0, 0.36 * len(data) + 1.2)))

    nomes = [rotulos.get(g, g) for g in data["grupo"]]
    bars = ax.barh(nomes, data["ocorrencias"], color=_GRAYS[2], edgecolor="black", linewidth=0.6)
    for bar, hatch in zip(bars, _HATCHES * 4, strict=False):
        bar.set_hatch(hatch)

    ax.set_xlabel("Ocorrências de barreira")
    ax.set_title("Perfil de exclusão: quem é afetado pelas barreiras detectadas")
    return fig


def figure_index_by_sphere(pages: pd.DataFrame, *, index: str = "ica") -> Figure:
    """Distribuição de um índice por esfera federativa.

    Diagrama de caixa com os pontos sobrepostos. Exibir os pontos não é
    ornamento: com poucos portais por estrato, a caixa sozinha sugere uma
    densidade de dados que não existe.
    """
    plt = _plt()
    apply_style()

    titulos = {
        "ica": "Índice de Conformidade (ICA)",
        "ian": "Índice de Atrito de Navegação (IAN)",
        "iej": "Índice de Exposição Jurídica (IEJ)",
    }
    fig, ax = plt.subplots(figsize=(6.0, 4.0))

    esferas = [e for e in ("federal", "estadual", "municipal") if e in set(pages["esfera"])]
    dados = [pages.loc[pages["esfera"] == e, index].dropna().tolist() for e in esferas]

    bp = ax.boxplot(dados, labels=esferas, patch_artist=True, widths=0.55, showfliers=False)
    for patch, hatch in zip(bp["boxes"], _HATCHES, strict=False):
        patch.set_facecolor(_GRAYS[3])
        patch.set_edgecolor("black")
        patch.set_hatch(hatch)
    for element in ("medians", "whiskers", "caps"):
        for line in bp[element]:
            line.set_color("black")

    import numpy as np

    rng = np.random.default_rng(42)  # jitter reproduzível
    for i, valores in enumerate(dados, start=1):
        if not valores:
            continue
        x = rng.normal(i, 0.045, size=len(valores))
        ax.plot(x, valores, "o", color="black", markersize=3, alpha=0.55)

    ax.set_ylim(0, 100)  # sem truncamento
    ax.set_ylabel(titulos.get(index, index.upper()))
    ax.set_xlabel("Esfera federativa")
    ax.set_title(f"{titulos.get(index, index.upper())} por esfera de governo")
    return fig


def figure_data_cost(pages: pd.DataFrame, *, franchise_mb: float = 10240.0) -> Figure:
    """Custo de acesso por página, em fração da franquia mensal de dados.

    Eixo em escala logarítmica: os pesos variam por ordens de grandeza entre
    páginas institucionais leves e telas de sistema carregadas de scripts, e a
    escala linear achataria toda a faixa baixa em uma única coluna.
    """
    plt = _plt()
    apply_style()

    data = pages.dropna(subset=["peso_mb"])
    data = data[data["peso_mb"] > 0]
    fig, ax = plt.subplots(figsize=(6.5, 4.0))

    if data.empty:
        ax.text(0.5, 0.5, "Sem medições de peso disponíveis", ha="center", va="center")
        return fig

    ax.hist(data["peso_mb"], bins=20, color=_GRAYS[3], edgecolor="black", linewidth=0.6)
    ax.set_xscale("log")
    ax.set_xlabel("Peso da página (MB, escala logarítmica)")
    ax.set_ylabel("Número de páginas")
    ax.set_title("Custo de acesso: peso das páginas auditadas")

    mediana = float(data["peso_mb"].median())
    ax.axvline(mediana, color="black", linestyle="--", linewidth=1.2)
    ax.text(
        mediana,
        ax.get_ylim()[1] * 0.92,
        # Três casas na fração: com a franquia de referência (10 GiB), páginas
        # de peso comum ficam abaixo de 0,1%, e duas casas colapsariam a
        # anotação em "0,00%".
        f"  mediana {mediana:.2f} MB\n  ({mediana / franchise_mb * 100:.3f}% da franquia)",
        fontsize=8,
        va="top",
    )
    return fig


def save_all(
    findings: pd.DataFrame,
    pages: pd.DataFrame,
    directory: Path,
    *,
    franchise_mb: float = 10240.0,
) -> list[Path]:
    """Gera e grava todas as figuras do artigo.

    Cada figura é salva em PNG (300 dpi, para submissão) e em SVG (vetorial,
    para edição). Figuras que não têm dado suficiente são **puladas com
    registro no log**, nunca geradas vazias: uma figura em branco em um artigo
    é pior que a ausência dela.

    Returns:
        Caminhos dos arquivos gravados.
    """
    from acessisaude_audit.analysis.dataset import criterion_prevalence, exclusion_profile

    plt = _plt()
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    def _save(fig: Figure, nome: str) -> None:
        for ext in ("png", "svg"):
            path = directory / f"{nome}.{ext}"
            fig.savefig(path)
            written.append(path)
        plt.close(fig)
        logger.info("figura gerada", extra={"figura": nome})

    if not findings.empty:
        prevalence = criterion_prevalence(findings)
        if not prevalence.empty:
            _save(figure_criterion_prevalence(prevalence), "fig1-prevalencia-criterios")

        profile = exclusion_profile(findings)
        if not profile.empty:
            _save(figure_exclusion_profile(profile), "fig2-perfil-de-exclusao")
    else:
        logger.warning("sem achados: figuras 1 e 2 não geradas")

    if not pages.empty and "esfera" in pages and pages["esfera"].nunique() > 1:
        _save(figure_index_by_sphere(pages, index="ica"), "fig3-ica-por-esfera")
    else:
        logger.warning("esfera federativa ausente ou com um único valor: figura 3 não gerada")

    if not pages.empty:
        _save(figure_data_cost(pages, franchise_mb=franchise_mb), "fig4-custo-de-acesso")

    return written


def criterion_label(criterion_id: str) -> str:
    """Rótulo curto do critério para uso em eixos."""
    try:
        sc = criterion(criterion_id)
        return f"{sc.id} {sc.title_pt}"
    except KeyError:
        return criterion_id
