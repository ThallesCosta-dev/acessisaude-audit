# ADR 0004 — Escrever sondas próprias além do axe-core

**Estado:** aceita

---

## Contexto

O axe-core cobre bem o que se verifica por inspeção estática do DOM. A validação contra o
conjunto de referência revelou lacunas incompatíveis com o escopo declarado do projeto — e
duas delas só apareceram porque o golden set as media explicitamente.

---

## Decisão

Escrever **16 sondas próprias**, sob um contrato explícito, cobrindo quatro classes de lacuna:

### 1. Barreiras que exigem interação

`probe.focus-visible` percorre a página com **pressões reais da tecla Tab**. Necessário
porque navegadores só aplicam `:focus-visible` quando a modalidade de entrada corrente é o
teclado — `element.focus()` programático, abordagem usual de ferramentas mais simples,
produziria falso positivo em quase toda página moderna.

`probe.reflow-320` mede a página **renderizada** em 320 CSS px, ignorando elementos dentro de
contêiner rolável (técnica C37 da WCAG, que admite rolagem confinada a um bloco).

### 2. Divergências entre o axe e a norma de referência

| Lacuna | Sonda |
|---|---|
| `placeholder` aceito como nome acessível pela regra `label` | `probe.placeholder-como-rotulo` |
| Critério 4.1.1 removido na WCAG 2.2, mas no escopo aqui (ADR 0001) | `probe.id-duplicado` |

Detalhamento em [limites do axe-core](../metodologia/limites-do-axe-core.md).

### 3. Regras classificadas como boa prática, mas com lastro normativo

`tabindex` positivo (2.4.3) e salto de nível de cabeçalho (1.3.1) são `best-practice` no axe.
O projeto exclui esse conjunto — recomendações sem lastro normativo não podem sustentar
afirmação de violação legal —, mas os dois casos **têm** correspondência em critério de
sucesso, e por isso são cobertos por sonda.

### 4. Dimensões ausentes da WCAG

`probe.data-cost` e `probe.readability`, com fundamentação jurídica própria. Ver
[ADR 0006](0006-custo-de-dados-como-barreira.md).

---

## O contrato das sondas

Regra central, **verificada em teste** (`test_contrato_sondas.py`):

> Sondas declaradas `HEURISTIC` **nunca** produzem `FAIL`. O veredito máximo é `INCOMPLETE`.

A classe base rebaixa automaticamente qualquer tentativa e registra em log. É o que impede
que uma futura sonda, escrita com pressa, converta um indício de legibilidade em violação da
LBI.

Regras acessórias, também verificadas:

- toda sonda declara `id` prefixado por `probe.`, permitindo distinguir no dataset achado
  próprio de achado do axe;
- toda sonda declara descrição substantiva e critérios existentes no escopo;
- exceção em sonda é capturada, registrada e devolve lista vazia — uma sonda quebrada não
  pode derrubar a coleta nem, pior, produzir silenciosamente uma página "sem problemas".

---

## Consequências

**Positivas**

- Cobertura de 18 critérios além do que o axe alcança, mais 2 dimensões próprias.
- As lacunas do axe viram **achado metodológico documentado** do projeto, e não omissão.
- O contrato de confiança é auditável, não uma promessa.

**Negativas assumidas**

- 16 sondas a manter, com risco de divergência conforme o axe evolui. Mitigado pelo golden
  set, que falha se uma sonda passar a duplicar o axe.
- Custo de execução: `probe.focus-visible` faz uma ida e volta ao navegador por parada de
  tabulação, com teto de 40 paradas, declarado no relatório.

---

## Alternativas descartadas

**Aceitar a cobertura do axe.** Deixaria o projeto cego no formulário de agendamento — a tela
que mais importa —, por causa do padrão `placeholder` como rótulo.

**Habilitar `best-practice` do axe.** Traria as regras faltantes junto com dezenas de
recomendações sem lastro normativo, inflando a contagem de "violações legais" e enfraquecendo
o argumento jurídico.
