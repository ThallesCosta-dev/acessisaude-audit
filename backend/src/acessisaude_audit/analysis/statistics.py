"""Testes e estimativas para a seção de Resultados.

Escolhas metodológicas, todas com consequência sobre o que o artigo pode
afirmar:

**Não paramétrico por padrão.** Índices de acessibilidade não são normalmente
distribuídos — concentram-se em faixas e têm caudas longas. Usam-se
Kruskal-Wallis e Mann-Whitney, e não ANOVA ou teste t.

**Tamanho de efeito sempre.** Todo teste devolve, junto do valor-p, uma medida
de efeito (δ de Cliff ou ε²). Com amostras de portais — tipicamente dezenas de
páginas — um p pequeno pode acompanhar diferença irrelevante, e um p grande
pode esconder diferença substantiva por falta de potência.

**Intervalos por bootstrap.** Sem suposição de forma, e com semente fixa vinda
da configuração, para que o mesmo dado produza o mesmo intervalo.

**A unidade de análise é declarada.** Páginas do mesmo portal não são
observações independentes: compartilham template, equipe e decisões de design.
Toda função aqui exige que o chamador informe se está agregando por página ou
por portal, e :func:`design_warning` emite o alerta correspondente para que a
limitação apareça no texto.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from acessisaude_audit.logging_setup import get_logger

__all__ = [
    "TestResult",
    "bootstrap_ci",
    "cliffs_delta",
    "compare_groups",
    "describe",
    "design_warning",
]

logger = get_logger(__name__)


def _numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            'A análise exige o extra "analysis": pip install -e "backend[analysis]"'
        ) from exc
    return np


def _scipy() -> Any:
    try:
        from scipy import stats
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            'A análise exige o extra "analysis": pip install -e "backend[analysis]"'
        ) from exc
    return stats


@dataclass(frozen=True, slots=True)
class TestResult:
    """Resultado de um teste de hipótese, com tudo que o relato exige.

    Attributes:
        test: Nome do teste aplicado.
        statistic: Estatística de teste.
        p_value: Valor-p bilateral.
        effect_size: Tamanho de efeito.
        effect_name: Qual medida de efeito foi usada.
        effect_interpretation: Faixa qualitativa do efeito.
        n_by_group: Tamanho de cada grupo.
        note: Advertência metodológica aplicável.
    """

    test: str
    statistic: float
    p_value: float
    effect_size: float
    effect_name: str
    effect_interpretation: str
    n_by_group: dict[str, int]
    note: str = ""

    def report(self, alpha: float = 0.05) -> str:
        """Frase pronta para a seção de Resultados, em português.

        Formulada para não induzir a leitura errada: "não houve diferença
        detectável" em vez de "os grupos são iguais". Ausência de evidência de
        diferença não é evidência de ausência de diferença, e com amostras de
        portais essa distinção é frequentemente decisiva.
        """
        ns = ", ".join(f"n({g})={n}" for g, n in self.n_by_group.items())
        veredito = (
            "diferença estatisticamente significativa"
            if self.p_value < alpha
            else "não houve diferença detectável"
        )
        return (
            f"{self.test}: {veredito} (p = {self.p_value:.4f}; "
            f"{self.effect_name} = {self.effect_size:.3f}, efeito "
            f"{self.effect_interpretation}; {ns})." + (f" {self.note}" if self.note else "")
        )


def describe(values: list[float]) -> dict[str, float]:
    """Estatísticas descritivas robustas.

    Reporta mediana e amplitude interquartil ao lado de média e desvio: em
    distribuições assimétricas, a média sozinha desloca a leitura, e é
    exatamente o caso dos índices de acessibilidade.
    """
    np = _numpy()
    arr = np.asarray([v for v in values if v == v], dtype=float)  # descarta NaN
    if arr.size == 0:
        return {"n": 0}
    q1, q3 = np.percentile(arr, [25, 75])
    return {
        "n": int(arr.size),
        "media": float(np.mean(arr)),
        "desvio": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "mediana": float(np.median(arr)),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


def cliffs_delta(a: list[float], b: list[float]) -> tuple[float, str]:
    """δ de Cliff: probabilidade de um valor de ``a`` exceder um de ``b``.

    Medida não paramétrica de tamanho de efeito, em [-1, 1]. Preferida ao d de
    Cohen aqui porque não pressupõe normalidade nem variâncias homogêneas.

    Faixas (ROMANO et al., 2006): |δ| < 0,147 desprezível; < 0,33 pequeno;
    < 0,474 médio; caso contrário grande.

    Returns:
        Par ``(delta, interpretação)``.
    """
    np = _numpy()
    x = np.asarray([v for v in a if v == v], dtype=float)
    y = np.asarray([v for v in b if v == v], dtype=float)
    if x.size == 0 or y.size == 0:
        return 0.0, "indeterminado"

    # Comparação vetorizada de todos os pares.
    diff = np.sign(x[:, None] - y[None, :])
    delta = float(diff.sum() / (x.size * y.size))

    magnitude = abs(delta)
    if magnitude < 0.147:
        label = "desprezível"
    elif magnitude < 0.33:
        label = "pequeno"
    elif magnitude < 0.474:
        label = "médio"
    else:
        label = "grande"
    return delta, label


def bootstrap_ci(
    values: list[float],
    *,
    statistic: Literal["mediana", "media"] = "mediana",
    confidence: float = 0.95,
    resamples: int = 10_000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Intervalo de confiança por bootstrap percentílico.

    Args:
        values: Observações.
        statistic: Estatística a estimar.
        confidence: Nível de confiança.
        resamples: Número de reamostragens.
        seed: Semente — deve vir de ``Settings.random_seed`` para que o
            intervalo publicado seja reproduzível.

    Returns:
        Tripla ``(estimativa, limite_inferior, limite_superior)``.
    """
    np = _numpy()
    arr = np.asarray([v for v in values if v == v], dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan"), float("nan")
    if arr.size == 1:
        return float(arr[0]), float(arr[0]), float(arr[0])

    fn = np.median if statistic == "mediana" else np.mean
    rng = np.random.default_rng(seed)
    samples = rng.choice(arr, size=(resamples, arr.size), replace=True)
    estimates = fn(samples, axis=1)

    tail = (1 - confidence) / 2 * 100
    lower, upper = np.percentile(estimates, [tail, 100 - tail])
    return float(fn(arr)), float(lower), float(upper)


def compare_groups(
    groups: dict[str, list[float]],
    *,
    unit: Literal["pagina", "portal"] = "pagina",
) -> TestResult:
    """Compara a distribuição de uma métrica entre grupos.

    Aplica Mann-Whitney U para dois grupos e Kruskal-Wallis para três ou mais.

    Args:
        groups: Mapa nome do grupo → observações.
        unit: Unidade de análise. Determina a advertência metodológica anexada
            ao resultado — ver :func:`design_warning`.

    Raises:
        ValueError: Se houver menos de dois grupos com dados.
    """
    stats = _scipy()
    clean = {name: [v for v in vals if v == v] for name, vals in groups.items()}
    clean = {name: vals for name, vals in clean.items() if vals}
    if len(clean) < 2:
        raise ValueError("São necessários ao menos dois grupos com observações.")

    sizes = {name: len(vals) for name, vals in clean.items()}
    note = design_warning(unit, sizes)

    if len(clean) == 2:
        (name_a, a), (name_b, b) = clean.items()
        result = stats.mannwhitneyu(a, b, alternative="two-sided")
        delta, label = cliffs_delta(a, b)
        return TestResult(
            test=f"Mann-Whitney U ({name_a} vs. {name_b})",
            statistic=float(result.statistic),
            p_value=float(result.pvalue),
            effect_size=delta,
            effect_name="δ de Cliff",
            effect_interpretation=label,
            n_by_group=sizes,
            note=note,
        )

    result = stats.kruskal(*clean.values())
    # ε² = (H − k + 1) / (n − k): tamanho de efeito do Kruskal-Wallis.
    n = sum(sizes.values())
    k = len(clean)
    epsilon_sq = max(0.0, (float(result.statistic) - k + 1) / (n - k)) if n > k else 0.0
    if epsilon_sq < 0.01:
        label = "desprezível"
    elif epsilon_sq < 0.06:
        label = "pequeno"
    elif epsilon_sq < 0.14:
        label = "médio"
    else:
        label = "grande"

    return TestResult(
        test=f"Kruskal-Wallis ({k} grupos)",
        statistic=float(result.statistic),
        p_value=float(result.pvalue),
        effect_size=epsilon_sq,
        effect_name="ε²",
        effect_interpretation=label,
        n_by_group=sizes,
        note=note,
    )


def design_warning(unit: str, sizes: dict[str, int]) -> str:
    """Advertência metodológica correspondente ao desenho da comparação.

    Existe para que a limitação apareça no texto do artigo em vez de ficar
    implícita. As duas ameaças cobertas são as que mais frequentemente invalidam
    conclusões nesta área:

    - **Pseudorreplicação.** Páginas de um mesmo portal compartilham template e
      equipe: não são observações independentes. Tratá-las como tal infla o n e
      produz significância espúria.
    - **Potência insuficiente.** Com poucos portais por estrato, a ausência de
      significância não distingue "não há diferença" de "não houve como
      detectá-la".
    """
    avisos: list[str] = []
    if unit == "pagina":
        avisos.append(
            "Unidade de análise = página. Páginas de um mesmo portal não são "
            "independentes (mesmo template e mesma equipe): o resultado é "
            "suscetível a pseudorreplicação e deve ser lido como descritivo, "
            "com confirmação por modelo de efeitos mistos ou por agregação em "
            "nível de portal."
        )
    if any(n < 5 for n in sizes.values()):
        pequenos = [g for g, n in sizes.items() if n < 5]
        avisos.append(
            f"Grupos com menos de 5 observações ({', '.join(pequenos)}): potência "
            "insuficiente; a ausência de significância não sustenta afirmação de "
            "equivalência."
        )
    return " ".join(avisos)
