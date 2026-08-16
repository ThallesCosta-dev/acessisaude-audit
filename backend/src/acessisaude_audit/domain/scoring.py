"""Índices agregados: da contagem de falhas à medida interpretável.

Contar violações é a métrica ingênua da área e produz três vieses conhecidos:

1. **Viés de template.** Uma página com 400 links sem nome acessível recebe 400
   ocorrências, mas trata-se de *um* defeito de componente. Contagem bruta
   superestima portais grandes.
2. **Viés de equivalência.** Somar uma falha de ``lang`` ausente com uma
   armadilha de teclado supõe que ambas pesam igual — a primeira degrada, a
   segunda impede.
3. **Viés de cobertura.** Ferramentas automáticas cobrem cerca de um terço dos
   critérios; relatar "97% de conformidade" sobre esse subconjunto é
   metodologicamente indefensável.

Este módulo enfrenta os três: amortecimento logarítmico das ocorrências,
ponderação por gravidade técnica **e** jurídica, e denominador restrito aos
critérios efetivamente automatizáveis, com a cobertura sempre reportada junto
ao índice.

Todas as constantes de calibração são explícitas em :class:`ScoringParameters`
e viajam no ``config_snapshot`` de cada varredura, de modo que qualquer número
publicado no artigo seja reexecutável. Ver ``docs/metodologia/indices.md``.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field

from acessisaude_audit.domain.mapping import LegalRisk, mapping_for
from acessisaude_audit.domain.models import (
    Finding,
    NetworkMetrics,
    Outcome,
    PageAudit,
    ScanResult,
)
from acessisaude_audit.domain.wcag import (
    WCAG_CRITERIA,
    ConformanceLevel,
    DeficiencyGroup,
    Principle,
    criterion,
)

__all__ = [
    "AccessibilityScore",
    "DataCostScore",
    "ScoringParameters",
    "automatable_criteria_ids",
    "score_page",
    "score_scan",
]


@dataclass(frozen=True, slots=True)
class ScoringParameters:
    """Constantes de calibração dos índices.

    Attributes:
        friction_kappa: Constante de saturação do Índice de Atrito de Navegação.
            Define quanto "atrito bruto" corresponde a ~63% do índice.

            **Calibração empírica.** O valor 150.0 foi obtido medindo o atrito
            bruto de cada página do conjunto de validação e escolhendo κ de modo
            que a escala discrimine na faixa de interesse. Valores menores
            saturam: com κ=40, uma única falha séria de risco alto já pontuava
            65, e quatro das cinco fixtures marcavam acima de 98 — o índice
            deixava de distinguir "ruim" de "inutilizável", que é justamente a
            distinção que ele precisa fazer.

            Comportamento resultante, medido (axe-core 4.13.0 + 15 sondas)::

                atrito bruto   IAN     caso de referência
                ------------   -----   ----------------------------------------
                        0,0      0,0   página conforme (caso-controle negativo)
                        9,0      5,8   uma falha leve isolada
                       42,0     24,4   uma falha séria de risco jurídico alto
                       84,0     42,9   duas falhas sérias
                      306,0     87,0   formulário sem rótulos programáticos
                     1810,8    100,0   caso-controle positivo (20 barreiras)

            Ver ``docs/metodologia/indices.md`` para a tabela completa e o
            procedimento de recalibração quando o conjunto de sondas mudar.
        critical_path_multiplier: Fator aplicado ao atrito de páginas
            pertencentes a fluxo essencial declarado no catálogo. Justificativa
            jurídica: a mesma barreira tem consequência distinta na página
            institucional e na tela de confirmação de consulta.
        price_per_mb_brl: Preço de referência do mebibyte de dados móveis, em
            reais.

            **Valor coletado, não estimado.** Plano de referência: *Claro Prezão
            R$ 15,00 / 5 GB / 15 dias*, o pacote pré-pago de entrada mais barato
            do mercado brasileiro na data de consulta (10/08/2026). Equivalente
            mensal: R$ 30,00 por 10 GiB, isto é **R$ 3,00 por GiB** ou
            R$ 0,0029296875 por MiB — valor exatamente representável em ponto
            flutuante (3/1024), o que evita erro de arredondamento acumulado.

            Fontes e valores corroborantes em
            ``docs/metodologia/parametros-de-custo.md``. Em síntese: a Anatel
            reporta preço médio efetivo de R$ 5,46/GB no 1T2026, superior ao
            valor aqui adotado, de modo que a estimativa de custo do projeto é
            **conservadora** — erra para menos, nunca para mais.

        franchise_mb: Franquia mensal do plano de referência, em MiB.
            10 GiB = 10 240 MiB, correspondente a duas recargas de R$ 15,00 no
            ciclo de 15 dias.

            A Anatel reporta receita média mensal de **R$ 12,12** por usuário
            pré-pago (1T2026) — menos da metade dos R$ 30,00 pressupostos aqui.
            O usuário pré-pago médio dispõe, portanto, de franquia **menor** que
            a de referência, o que reforça o caráter conservador da medida.

        heavy_page_mb: Limiar acima do qual a página é classificada como onerosa.

            **Valor coletado:** 2,5 MiB, o peso mediano de uma página inicial em
            dispositivo móvel segundo o *Web Almanac 2025* do HTTP Archive
            (coleta de julho de 2025: mediana de 2 559 KiB; percentil 90 de
            8 337 KiB).

            A escolha é deliberadamente descritiva, e não normativa: o limiar não
            é um ideal de engenharia, é a mediana da web comercial — notoriamente
            inchada. Uma página de serviço público de saúde acima dela é pesada
            mesmo para o padrão do que se critica.
    """

    friction_kappa: float = 150.0
    critical_path_multiplier: float = 1.5
    #: R$ 3,00 por GiB — ver docstring. 3/1024 é exato em ponto flutuante.
    price_per_mb_brl: float = 0.0029296875
    franchise_mb: float = 10240.0
    heavy_page_mb: float = 2.5

    def as_dict(self) -> dict[str, float]:
        """Serialização para o ``config_snapshot`` da varredura."""
        return {
            "friction_kappa": self.friction_kappa,
            "critical_path_multiplier": self.critical_path_multiplier,
            "price_per_mb_brl": self.price_per_mb_brl,
            "franchise_mb": self.franchise_mb,
            "heavy_page_mb": self.heavy_page_mb,
        }


DEFAULT_PARAMETERS = ScoringParameters()


def automatable_criteria_ids() -> frozenset[str]:
    """Critérios A/AA para os quais a ferramenta emite veredito determinístico.

    É o **denominador honesto** do índice de conformidade. Critérios sem
    verificação automática possível não entram no cálculo — e a razão entre
    este conjunto e o total de critérios é reportada como ``coverage``.
    """
    return frozenset(c.id for c in WCAG_CRITERIA if c.automatable)


class DataCostScore(BaseModel):
    """Custo de acesso para o usuário com plano de dados limitado."""

    model_config = ConfigDict(frozen=True)

    total_mb: float = Field(description="Peso médio da página em MB.")
    cost_brl: float = Field(description="Custo estimado por acesso, em reais.")
    franchise_share_pct: float = Field(
        description="Percentual da franquia mensal consumido em um acesso."
    )
    third_party_share_pct: float = Field(
        description="Percentual do tráfego destinado a domínios de terceiros."
    )
    is_heavy: bool = Field(description="Excede o limiar de página onerosa.")
    monthly_cost_brl_at_4_visits: float = Field(
        description=(
            "Custo mensal estimado para quatro acessos — frequência de referência "
            "para acompanhamento de agendamento e resultado de exame."
        )
    )


class AccessibilityScore(BaseModel):
    """Conjunto de índices de uma página ou de uma varredura completa.

    Nenhum índice deve ser lido isoladamente: ``conformance_index`` responde
    "quanto do exigível foi cumprido", ``friction_index`` responde "quanto custa
    usar mesmo assim", e ``absolute_barrier`` responde "é possível usar?".
    Um portal pode ter conformidade de 85% e ainda assim ser inutilizável por
    uma única armadilha de teclado.
    """

    model_config = ConfigDict(frozen=True)

    conformance_index: float = Field(
        ge=0,
        le=100,
        description=(
            "ICA — Índice de Conformidade de Acessibilidade, em [0,100]. "
            "Fração ponderada, por risco jurídico, dos critérios automatizáveis "
            "não violados."
        ),
    )
    friction_index: float = Field(
        ge=0,
        le=100,
        description=(
            "IAN — Índice de Atrito de Navegação, em [0,100]. Cresce com a "
            "gravidade técnica, o risco jurídico e (de forma amortecida) o "
            "número de ocorrências. 0 = sem atrito detectado."
        ),
    )
    legal_exposure_index: float = Field(
        ge=0,
        le=100,
        description=(
            "IEJ — Índice de Exposição Jurídica, em [0,100]. Concentra-se na "
            "gravidade das violações, ignorando as de risco baixo, e responde "
            "à pergunta do gestor: 'qual o tamanho do meu passivo?'"
        ),
    )
    absolute_barrier: bool = Field(
        description=(
            "Há ao menos uma violação de risco jurídico CRÍTICO — barreira sem "
            "rota alternativa. Torna o serviço inacessível de fato, "
            "independentemente do valor dos demais índices."
        )
    )
    coverage: float = Field(
        ge=0,
        le=1,
        description=(
            "Fração dos 50 critérios A/AA em que a ferramenta consegue emitir "
            "veredito determinístico para ao menos um modo de falha. É um "
            "LIMITE SUPERIOR OTIMISTA da cobertura real: mede sobre quantos "
            "critérios a ferramenta pode dizer algo, não quantas barreiras ela "
            "encontra. Um portal com todos os 'alt' preenchidos com 'imagem' "
            "passa em 1.1.1 e permanece inacessível."
        ),
    )
    criteria_evaluated: int = Field(description="Critérios no denominador do ICA.")
    criteria_violated: int = Field(description="Critérios distintos violados.")
    violations: int = Field(description="Achados com veredito de falha.")
    occurrences: int = Field(description="Elementos do DOM em situação de falha.")
    incomplete: int = Field(description="Achados que exigem revisão humana.")
    violations_by_impact: dict[str, int] = Field(default_factory=dict)
    violations_by_legal_risk: dict[str, int] = Field(default_factory=dict)
    violations_by_principle: dict[str, int] = Field(default_factory=dict)
    violations_by_level: dict[str, int] = Field(default_factory=dict)
    excluded_groups: dict[str, int] = Field(
        default_factory=dict,
        description=(
            "Ocorrências de barreira por grupo de pessoas afetado. Responde "
            "'quem é excluído', e não apenas 'quantas falhas há'."
        ),
    )
    violated_criteria: list[str] = Field(default_factory=list)
    data_cost: DataCostScore | None = None


@dataclass(slots=True)
class _Accumulator:
    """Estado intermediário do cálculo, compartilhado entre página e varredura."""

    raw_friction: float = 0.0
    raw_legal: float = 0.0
    violations: int = 0
    occurrences: int = 0
    incomplete: int = 0
    violated_criteria: set[str] = field(default_factory=set)
    by_impact: Counter[str] = field(default_factory=Counter)
    by_legal_risk: Counter[str] = field(default_factory=Counter)
    by_principle: Counter[str] = field(default_factory=Counter)
    by_level: Counter[str] = field(default_factory=Counter)
    by_group: Counter[str] = field(default_factory=Counter)
    absolute_barrier: bool = False
    pages: int = 0


def _finding_weight(finding: Finding) -> tuple[float, float]:
    """Peso técnico e peso jurídico de um achado.

    O peso técnico vem do ``impact`` do axe-core (ou da sonda); o jurídico, do
    maior :class:`LegalRisk` entre os critérios violados. Achados sem impacto
    declarado recebem peso técnico neutro 1.0 — nunca 0, para não desaparecerem
    silenciosamente do índice.
    """
    technical = finding.impact.weight if finding.impact else 1.0
    legal = finding.legal_risk.weight if finding.legal_risk else 1.0
    return technical, legal


def _accumulate(acc: _Accumulator, page: PageAudit, params: ScoringParameters) -> None:
    """Incorpora uma página ao acumulador."""
    acc.pages += 1
    path_factor = params.critical_path_multiplier if page.is_critical_path else 1.0

    for finding in page.findings:
        if finding.outcome is Outcome.INCOMPLETE:
            acc.incomplete += 1
            continue
        if finding.outcome is not Outcome.FAIL:
            continue

        acc.violations += 1
        occ = max(finding.occurrences, 1)
        acc.occurrences += occ

        technical, legal = _finding_weight(finding)

        # Amortecimento logarítmico: a segunda ocorrência do mesmo defeito
        # informa muito menos que a primeira (viés de template).
        damped = math.log2(1 + occ)
        acc.raw_friction += technical * legal * damped * path_factor

        risk = finding.legal_risk
        if risk is not None:
            acc.by_legal_risk[risk.value] += 1
            if risk is LegalRisk.CRITICO:
                acc.absolute_barrier = True
            # O IEJ ignora risco baixo: passivo jurídico não se mede por
            # irregularidade formal, e sim por obstrução efetiva de direito.
            if risk is not LegalRisk.BAIXO:
                acc.raw_legal += risk.weight * damped * path_factor

        if finding.impact is not None:
            acc.by_impact[finding.impact.value] += 1

        for group in finding.affects:
            acc.by_group[group.value] += occ

        for crit_id in finding.criteria:
            acc.violated_criteria.add(crit_id)
            try:
                sc = criterion(crit_id)
            except KeyError:
                continue
            acc.by_principle[sc.principle.value] += 1
            acc.by_level[sc.level.value] += 1


def _saturate(raw: float, kappa: float) -> float:
    """Mapeia atrito bruto em [0, ∞) para índice em [0, 100).

    Usa saturação exponencial ``100·(1 − e^{−x/κ})``. A escolha é deliberada:
    uma soma linear tornaria o índice ilimitado e incomparável entre portais de
    tamanhos diferentes; um simples corte em 100 achataria toda a faixa alta,
    impedindo distinguir "ruim" de "inutilizável".
    """
    if raw <= 0:
        return 0.0
    return round(100.0 * (1.0 - math.exp(-raw / kappa)), 2)


def _conformance(violated: set[str], evaluated: frozenset[str]) -> float:
    """ICA: fração ponderada por risco jurídico dos critérios não violados.

    Fórmula::

        ICA = 100 · (1 − Σ_{c ∈ V} w(c) / Σ_{c ∈ A} w(c))

    onde ``A`` é o conjunto de critérios automatizáveis, ``V ⊆ A`` o conjunto
    dos violados e ``w(c)`` o peso do risco jurídico do critério. A ponderação
    faz com que violar 2.1.1 (teclado, risco crítico) derrube o índice muito
    mais do que violar 3.1.2 (idioma de partes, risco baixo).
    """

    def weight(crit_id: str) -> float:
        m = mapping_for(crit_id)
        return m.legal_risk.weight if m else LegalRisk.MODERADO.weight

    denominator = sum(weight(c) for c in evaluated)
    if denominator == 0:
        return 100.0
    numerator = sum(weight(c) for c in violated if c in evaluated)
    return round(max(0.0, 100.0 * (1.0 - numerator / denominator)), 2)


def _data_cost(metrics: NetworkMetrics, params: ScoringParameters) -> DataCostScore:
    """Converte métricas de rede em custo monetário para o usuário periférico."""
    cost = metrics.data_cost_brl(params.price_per_mb_brl)
    return DataCostScore(
        total_mb=metrics.total_mb,
        cost_brl=cost,
        franchise_share_pct=round(metrics.franchise_share(params.franchise_mb) * 100, 4),
        third_party_share_pct=round(metrics.third_party_share * 100, 2),
        is_heavy=metrics.total_mb > params.heavy_page_mb,
        monthly_cost_brl_at_4_visits=round(cost * 4, 4),
    )


def _build(
    acc: _Accumulator,
    evaluated: frozenset[str],
    params: ScoringParameters,
    data_cost: DataCostScore | None,
) -> AccessibilityScore:
    """Materializa o resultado a partir do acumulador."""
    # O atrito é normalizado por página para permitir comparar portais de
    # tamanhos diferentes — sem isso, varrer mais páginas pioraria o índice.
    pages = max(acc.pages, 1)
    return AccessibilityScore(
        conformance_index=_conformance(acc.violated_criteria, evaluated),
        friction_index=_saturate(acc.raw_friction / pages, params.friction_kappa),
        legal_exposure_index=_saturate(acc.raw_legal / pages, params.friction_kappa),
        absolute_barrier=acc.absolute_barrier,
        coverage=round(len(evaluated) / len(WCAG_CRITERIA), 4),
        criteria_evaluated=len(evaluated),
        criteria_violated=len(acc.violated_criteria & evaluated),
        violations=acc.violations,
        occurrences=acc.occurrences,
        incomplete=acc.incomplete,
        violations_by_impact=dict(acc.by_impact),
        violations_by_legal_risk=dict(acc.by_legal_risk),
        violations_by_principle=dict(acc.by_principle),
        violations_by_level=dict(acc.by_level),
        excluded_groups=dict(acc.by_group),
        violated_criteria=sorted(acc.violated_criteria),
        data_cost=data_cost,
    )


def score_page(
    page: PageAudit, params: ScoringParameters = DEFAULT_PARAMETERS
) -> AccessibilityScore:
    """Calcula os índices de uma única auditoria de página."""
    acc = _Accumulator()
    _accumulate(acc, page, params)
    return _build(acc, automatable_criteria_ids(), params, _data_cost(page.network, params))


def score_scan(
    scan: ScanResult, params: ScoringParameters = DEFAULT_PARAMETERS
) -> AccessibilityScore:
    """Calcula os índices agregados de uma varredura completa.

    Apenas páginas com carregamento bem-sucedido entram no cálculo; páginas em
    erro distorceriam o índice para baixo (menos falhas detectadas por não haver
    conteúdo). A taxa de perda fica registrada em
    :attr:`~acessisaude_audit.domain.models.ScanResult.loss_rate`.
    """
    acc = _Accumulator()
    pages = scan.successful_pages
    for page in pages:
        _accumulate(acc, page, params)

    aggregate_cost: DataCostScore | None = None
    if pages:
        # Peso médio por página: a métrica que o usuário efetivamente paga a
        # cada navegação, e não o somatório do portal inteiro.
        mean = NetworkMetrics(
            total_bytes=round(sum(p.network.total_bytes for p in pages) / len(pages)),
            third_party_bytes=round(sum(p.network.third_party_bytes for p in pages) / len(pages)),
            request_count=round(sum(p.network.request_count for p in pages) / len(pages)),
        )
        aggregate_cost = _data_cost(mean, params)

    return _build(acc, automatable_criteria_ids(), params, aggregate_cost)


def summarize_by_group(score: AccessibilityScore) -> list[tuple[DeficiencyGroup, int]]:
    """Ordena os grupos afetados por número de ocorrências, do maior ao menor.

    Alimenta a figura "perfil de exclusão" do artigo — a visualização que traduz
    contagem de defeitos em população impactada.
    """
    out: list[tuple[DeficiencyGroup, int]] = []
    for raw, count in score.excluded_groups.items():
        try:
            out.append((DeficiencyGroup(raw), count))
        except ValueError:  # pragma: no cover - grupo desconhecido em dado legado
            continue
    return sorted(out, key=lambda item: item[1], reverse=True)


def summarize_by_principle(score: AccessibilityScore) -> list[tuple[Principle, int]]:
    """Violações por princípio POUR, em ordem canônica."""
    return [(p, score.violations_by_principle.get(p.value, 0)) for p in Principle]


def summarize_by_level(score: AccessibilityScore) -> list[tuple[ConformanceLevel, int]]:
    """Violações por nível de conformidade (A antes de AA)."""
    return [
        (lvl, score.violations_by_level.get(lvl.value, 0))
        for lvl in (ConformanceLevel.A, ConformanceLevel.AA)
    ]
