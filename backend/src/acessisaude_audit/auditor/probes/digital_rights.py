"""Sondas de direitos digitais: barreiras que a WCAG não vê.

Este módulo materializa o recorte que distingue o projeto de uma auditoria de
acessibilidade convencional. A WCAG pressupõe um usuário que *já chegou* à
página: ela pergunta se ele consegue percebê-la e operá-la. Não pergunta quanto
custou chegar, nem se o texto encontrado ali é compreensível para quem precisa
dele.

Para o usuário periférico — plano pré-pago, aparelho de entrada, rede instável,
escolaridade heterogênea — essas duas perguntas decidem o acesso ao serviço de
saúde tanto quanto o contraste de um botão. São barreiras de mesma natureza
jurídica: obstruem o acesso universal e igualitário do art. 196 da CF/88 e
frustram o dever de informação adequada do art. 18, § 4º da LBI.

Nenhuma das duas sondas produz veredito de violação da WCAG, porque não existe
critério WCAG correspondente. Elas produzem achados com fundamentação jurídica
**própria**, declarada em ``legal_thesis_override`` — e a de legibilidade,
sendo heurística, jamais reprova: apenas sinaliza.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from acessisaude_audit.auditor.probes._js import VISIBLE_TEXT_FN, wrap
from acessisaude_audit.auditor.probes.base import Confidence, Probe, ProbeContext
from acessisaude_audit.domain.mapping import LegalRisk
from acessisaude_audit.domain.models import (
    EvidenceNode,
    Finding,
    FindingSource,
    Impact,
    NetworkMetrics,
    Outcome,
)
from acessisaude_audit.domain.scoring import DEFAULT_PARAMETERS, ScoringParameters
from acessisaude_audit.domain.wcag import DeficiencyGroup

__all__ = ["DataCostProbe", "ReadabilityProbe", "count_syllables_pt", "flesch_pt_br"]


class DataCostProbe(Probe):
    """Quantifica o custo de acesso à página em dados móveis.

    Não é uma verificação de conformidade: é uma **medida de exclusão
    econômica**. Converte o peso da página em (i) reais gastos por acesso no
    plano de referência e (ii) fração da franquia mensal consumida, tornando
    comparável o que normalmente se discute em abstrato.

    O achado é emitido quando ao menos uma destas condições se verifica:

    - o peso ultrapassa o limiar de página onerosa configurado; ou
    - mais de 40% do tráfego se destina a domínios de terceiros — situação em
      que o usuário custeia, da própria franquia, recursos que não lhe prestam
      o serviço solicitado (analítica, publicidade, fontes remotas).

    A segunda condição é a mais relevante juridicamente: há transferência de
    custo ao cidadão sem contrapartida no serviço público prestado.
    """

    id = "probe.data-cost"
    criteria = ()  # Sem critério WCAG correspondente — fundamentação é própria.
    confidence = Confidence.DETERMINISTIC
    description = (
        "Converte o peso da página em custo monetário e em fração da franquia "
        "mensal de um plano de dados pré-pago de referência."
    )

    #: Fração de tráfego de terceiros a partir da qual o achado é emitido.
    THIRD_PARTY_THRESHOLD = 0.40

    def applies_to(self, context: ProbeContext) -> bool:
        """Requer métricas de rede coletadas no carregamento."""
        return isinstance(context.network, NetworkMetrics)

    async def _run(self, context: ProbeContext) -> list[Finding]:
        metrics: NetworkMetrics = context.network
        params: ScoringParameters = context.scoring or DEFAULT_PARAMETERS

        heavy = metrics.total_mb > params.heavy_page_mb
        third_party_heavy = metrics.third_party_share > self.THIRD_PARTY_THRESHOLD
        if not (heavy or third_party_heavy):
            return []

        cost = metrics.data_cost_brl(params.price_per_mb_brl)
        share = metrics.franchise_share(params.franchise_mb) * 100

        # Jornada assistencial de referência: consultar o andamento de um
        # agendamento ou o resultado de um exame não é ato único. Quatro acessos
        # por mês é a frequência mínima plausível, e a repetição é onde o custo
        # deixa de ser desprezível — motivo pelo qual o resumo reporta as duas
        # grandezas, e não apenas o custo de um acesso isolado.
        cost_journey = round(cost * 4, 6)
        share_journey = share * 4

        # Centavos, e não reais: com o preço de referência coletado
        # (R$ 3,00/GiB), o custo de um acesso fica na casa dos milésimos de
        # real, e "R$ 0,01" comunicaria menos do que "1,0 centavo". A conversão
        # é feita aqui, e não pelo formatador de `reporting`, porque a camada de
        # coleta não depende da camada de publicação.
        cents = cost * 100
        cents_journey = cost_journey * 100

        reasons: list[str] = []
        if heavy:
            reasons.append(
                f"peso de {metrics.total_mb:.2f} MB, acima do limiar de "
                f"{params.heavy_page_mb:.2f} MB"
            )
        if third_party_heavy:
            reasons.append(
                f"{metrics.third_party_share * 100:.0f}% do tráfego dirigido a "
                f"{len(metrics.third_party_domains)} domínio(s) de terceiros"
            )

        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.PROBE,
                outcome=Outcome.FAIL,
                impact=Impact.MODERATE if not third_party_heavy else Impact.SERIOUS,
                criteria=[],
                summary=(
                    f"Um único acesso a esta página consome {metrics.total_mb:.2f} MB, "
                    f"ou {share:.3f}% da franquia mensal do plano de referência "
                    f"({cents:.1f} centavo{'s' if cents >= 2 else ''})."
                ),
                description=(
                    "A página impõe custo de dados ao usuário com plano limitado: "
                    + "; ".join(reasons)
                    + ". O peso foi medido em bytes efetivamente transferidos, em "
                    "contexto sem cache — o cenário do primeiro acesso e daquele que "
                    "limpa dados do aparelho por falta de armazenamento. "
                    f"Consultada quatro vezes ao mês, frequência mínima plausível para "
                    f"acompanhar um agendamento ou um resultado de exame, esta página "
                    f"consome {share_journey:.2f}% da franquia "
                    f"({cents_journey:.1f} centavo{'s' if cents_journey >= 2 else ''}) — "
                    "e cada tentativa frustrada por barreira de acessibilidade soma-se "
                    "a essa conta, de modo que as duas dimensões se agravam mutuamente."
                ),
                remediation=(
                    "Reduzir o peso da página: comprimir e redimensionar imagens, servir "
                    "formatos modernos, remover scripts de terceiros não essenciais ao "
                    "serviço, adiar carregamento de recursos fora da área visível e "
                    "priorizar HTML semântico sobre renderização integral por JavaScript."
                ),
                affects=[DeficiencyGroup.LOW_BANDWIDTH],
                legal_risk_override=(
                    LegalRisk.ALTO if context.is_critical_path else LegalRisk.MODERADO
                ),
                legal_thesis_override=(
                    "O custo de dados exigido para acessar o serviço digital de saúde "
                    "transfere ao cidadão um ônus econômico como condição de exercício "
                    "de direito fundamental. Quando esse ônus recai desproporcionalmente "
                    "sobre a população de menor renda — a mesma que depende exclusivamente "
                    "do SUS — o acesso deixa de ser universal e igualitário, em desacordo "
                    "com o art. 196 da CF/88 e com o dever de informação adequada do art. "
                    "18, § 4º da Lei 13.146/2015. A parcela do tráfego destinada a "
                    "terceiros agrava a situação: o usuário custeia recursos que não lhe "
                    "prestam o serviço público solicitado."
                ),
                extra_provisions=["cf.art196", "lbi.art18", "lei13460.art5", "cf.art5.xiv"],
                nodes=[
                    EvidenceNode(
                        selector="document",
                        failure_summary="; ".join(reasons),
                        measured={
                            "total_mb": metrics.total_mb,
                            "total_bytes": metrics.total_bytes,
                            "request_count": metrics.request_count,
                            "third_party_share": metrics.third_party_share,
                            "third_party_domains": metrics.third_party_domains[:20],
                            "bytes_by_type": metrics.bytes_by_type,
                            "cost_brl": cost,
                            "franchise_share_pct": round(share, 4),
                            "price_per_mb_brl": params.price_per_mb_brl,
                            "franchise_mb": params.franchise_mb,
                        },
                    )
                ],
            )
        ]


# ---------------------------------------------------------------------------
# Legibilidade
# ---------------------------------------------------------------------------

_VOWELS = "aeiouáéíóúâêîôûàãõäëïöü"
_SENTENCE_SPLIT = re.compile(r"[.!?…]+(?:\s|$)")
_WORD = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]*")

#: Faixas de interpretação do Índice de Facilidade de Leitura de Flesch
#: adaptado ao português brasileiro (MARTINS et al., 1996).
_BANDS: tuple[tuple[float, str], ...] = (
    (75.0, "muito fácil (adequado às séries iniciais do ensino fundamental)"),
    (50.0, "fácil (adequado ao ensino fundamental completo)"),
    (25.0, "difícil (exige ensino médio completo)"),
    (0.0, "muito difícil (exige ensino superior)"),
)

#: Limiar abaixo do qual o texto é sinalizado.
#:
#: Fixado em 50 porque abaixo dessa faixa a compreensão passa a exigir ensino
#: médio completo — escolaridade que grande parcela da população usuária
#: exclusiva do SUS não possui. Não é um limite normativo: é um recorte
#: declarado, discutível, e por isso o achado sai como INCOMPLETE.
READABILITY_THRESHOLD = 50.0

#: Mínimo de palavras para que o índice seja estatisticamente interpretável.
MIN_WORDS = 120


def count_syllables_pt(word: str) -> int:
    """Conta sílabas de uma palavra em português, por agrupamento vocálico.

    Método: normaliza a palavra, agrupa vogais contíguas e conta os grupos.
    Ditongos e tritongos são contados como uma sílaba, o que está correto;
    hiatos (``sa-í-da``, ``co-or-de-nar``) são subcontados, o que **superestima
    levemente a facilidade de leitura**. O viés é conhecido, é conservador na
    direção certa — erra por não alarmar — e está declarado aqui e na seção de
    Métodos do artigo.

    Args:
        word: Palavra isolada.

    Returns:
        Número estimado de sílabas, no mínimo 1 para palavra não vazia.
    """
    normalized = word.lower()
    count = 0
    previous_was_vowel = False
    for char in normalized:
        base = unicodedata.normalize("NFD", char)[0]
        is_vowel = char in _VOWELS or base in "aeiou"
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    return max(count, 1 if normalized else 0)


def flesch_pt_br(text: str) -> dict[str, float | int | str]:
    """Índice de Facilidade de Leitura de Flesch adaptado ao português.

    Fórmula (MARTINS et al., 1996)::

        ILF = 248.835 − 1.015 × (palavras / frases) − 84.6 × (sílabas / palavras)

    Referência: MARTINS, T. B. F. et al. *Readability formulas applied to
    textbooks in Brazilian Portuguese*. São Carlos: ICMSC-USP, 1996.
    (Notas do ICMSC, n. 28.)

    Args:
        text: Texto corrido já extraído do conteúdo principal.

    Returns:
        Dicionário com o índice, a faixa interpretativa e as estatísticas que o
        compõem — todas expostas para que o número possa ser auditado, e não
        apenas aceito.
    """
    words = _WORD.findall(text)
    sentences = [s for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    n_words = len(words)
    n_sentences = max(len(sentences), 1)
    n_syllables = sum(count_syllables_pt(w) for w in words)

    if n_words == 0:
        return {
            "index": 0.0,
            "band": "indeterminado (sem texto)",
            "words": 0,
            "sentences": 0,
            "syllables": 0,
            "words_per_sentence": 0.0,
            "syllables_per_word": 0.0,
        }

    words_per_sentence = n_words / n_sentences
    syllables_per_word = n_syllables / n_words
    index = 248.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    index = max(0.0, min(100.0, index))

    band = next(label for threshold, label in _BANDS if index >= threshold)
    return {
        "index": round(index, 2),
        "band": band,
        "words": n_words,
        "sentences": n_sentences,
        "syllables": n_syllables,
        "words_per_sentence": round(words_per_sentence, 2),
        "syllables_per_word": round(syllables_per_word, 3),
    }


_TEXT_SCRIPT = wrap("return visibleText();", VISIBLE_TEXT_FN)


class ReadabilityProbe(Probe):
    """Mede a legibilidade do conteúdo principal (heurística, nunca reprova).

    A linguagem jurídico-administrativa é a barreira invisível dos portais
    públicos: o texto passa em todos os critérios técnicos e ainda assim não
    comunica. Um edital de convocação para exame escrito em período subordinado
    de quarenta palavras é formalmente acessível e materialmente inútil para
    boa parte de quem precisa dele.

    A sonda declara sua própria limitação: um índice de legibilidade mede
    estrutura superficial (extensão de frase, extensão de palavra), não
    compreensão. Texto simples pode ser vago; texto denso pode ser preciso e
    necessário. Por isso o resultado é sempre ``INCOMPLETE``, jamais violação —
    é um convite à revisão editorial, não uma acusação.
    """

    id = "probe.readability"
    criteria = ()
    confidence = Confidence.HEURISTIC
    description = (
        "Calcula o Índice de Facilidade de Leitura de Flesch adaptado ao "
        "português brasileiro sobre o conteúdo principal da página."
    )

    def applies_to(self, context: ProbeContext) -> bool:
        """Roda uma única vez por URL, no perfil desktop.

        O texto não muda entre viewports; medi-lo duas vezes duplicaria o
        achado no dataset e inflaria artificialmente a contagem.
        """
        return not context.viewport.is_mobile

    async def _run(self, context: ProbeContext) -> list[Finding]:
        text: str | None = await context.evaluate(_TEXT_SCRIPT)
        if not text:
            return []

        stats: dict[str, Any] = flesch_pt_br(text)
        if int(stats["words"]) < MIN_WORDS:
            # Amostra curta demais: o índice oscila muito e não é interpretável.
            return []
        if float(stats["index"]) >= READABILITY_THRESHOLD:
            return []

        return [
            Finding(
                rule_id=self.id,
                source=FindingSource.HEURISTIC,
                outcome=Outcome.INCOMPLETE,
                criteria=[],
                summary=(
                    f"Legibilidade do conteúdo principal em {stats['index']} pontos "
                    f"— faixa {stats['band']}."
                ),
                description=(
                    f"O texto principal apresenta média de {stats['words_per_sentence']} "
                    f"palavras por frase e {stats['syllables_per_word']} sílabas por "
                    "palavra. Nessa faixa, a compreensão autônoma exige escolaridade "
                    "acima da média da população que depende exclusivamente do SUS. "
                    "A informação está publicada e tecnicamente disponível, mas o "
                    "registro de linguagem opera como barreira de acesso — em especial "
                    "para pessoas com deficiência intelectual, para quem o art. 3º, IV, "
                    "'d' da LBI expressamente reconhece a barreira na comunicação. "
                    "Índices de legibilidade medem estrutura, não compreensão: este "
                    "achado sinaliza revisão editorial e não constitui, por si só, "
                    "violação de critério normativo."
                ),
                remediation=(
                    "Revisar o conteúdo em linguagem simples: frases curtas, ordem "
                    "direta, voz ativa, termos técnicos explicados na primeira "
                    "ocorrência e uma ideia por parágrafo. Manter a versão formal como "
                    "documento anexo quando houver exigência legal de redação técnica."
                ),
                affects=[DeficiencyGroup.COGNITIVE, DeficiencyGroup.LOW_BANDWIDTH],
                legal_risk_override=LegalRisk.MODERADO,
                legal_thesis_override=(
                    "A publicação de informação de saúde em registro linguístico "
                    "inacessível à população destinatária esvazia materialmente o dever "
                    "de oferta de comunicação e informação adequadas (art. 18, § 4º, IV, "
                    "LBI) e o dever de transparência ativa (art. 8º, § 3º, LAI). "
                    "A informação torna-se disponível sem se tornar acessível."
                ),
                extra_provisions=["lbi.art18", "lai.art8.par3.viii", "lei13460.art5"],
                nodes=[
                    EvidenceNode(
                        selector="main",
                        html=text[:300] + ("…" if len(text) > 300 else ""),
                        failure_summary=(f"Flesch adaptado = {stats['index']} ({stats['band']})."),
                        measured=dict(stats),
                    )
                ],
            )
        ]
