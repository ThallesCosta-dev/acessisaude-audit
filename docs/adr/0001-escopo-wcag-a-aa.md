# ADR 0001 — Escopo restrito aos níveis A e AA da WCAG 2.1

**Estado:** aceita

---

## Contexto

A WCAG 2.1 define 78 critérios de sucesso em três níveis de conformidade (A, AA, AAA). É
preciso decidir quais integram o escopo auditado, e a decisão determina o denominador de todo
índice de conformidade que o projeto publicar.

Duas questões independentes:

1. **Quais níveis?** A, AA, AAA?
2. **Qual versão?** 2.0, 2.1 ou 2.2?

---

## Decisão

**Níveis A e AA da WCAG 2.1** — 50 critérios (30 de nível A, 20 de nível AA).

### Quanto aos níveis

O nível AAA é excluído porque:

- O próprio W3C afirma que **não é possível satisfazer todos os critérios AAA para todo tipo
  de conteúdo**, e não recomenda exigi-lo como política geral.
- O Decreto 5.296/2004, o eMAG 3.1 e a prática administrativa brasileira tomam A/AA como
  patamar exigível para sítios da administração pública.
- Incluir AAA inflaria artificialmente a contagem de violações e enfraqueceria o argumento
  jurídico: seria fácil ao gestor responder que se exige o inexigível.

### Quanto à versão

A WCAG 2.2 é mais recente, mas a **2.1 é a referência normativa brasileira efetiva**:

- O eMAG 3.1 (2014) e o Decreto 5.296/2004 são anteriores à 2.2 e não a incorporam.
- A remissão do art. 63 da LBI às "melhores práticas adotadas internacionalmente" aponta,
  no contexto administrativo brasileiro, para o que o eMAG materializa.

A escolha tem consequência concreta: o critério **4.1.1 (Análise)** foi removido na 2.2 e
permanece no escopo aqui — o que exigiu escrever uma sonda própria, porque o axe-core seguiu
a 2.2 e deixou de verificá-lo. Ver
[ADR 0004](0004-sondas-proprias.md) e
[limites do axe-core](../metodologia/limites-do-axe-core.md).

---

## Consequências

**Positivas**

- Denominador estável e defensável: 50 critérios, dos quais 27 admitem veredito automático.
- Alinhamento com o patamar juridicamente exigível no Brasil, o que dá força ao argumento.
- Contagem de violações que o gestor não pode descartar como perfeccionismo.

**Negativas assumidas**

- Barreiras reais cobertas apenas por critérios AAA não são reportadas — notadamente 1.4.6
  (contraste reforçado, 7:1) e 3.1.5 (nível de leitura). A segunda é parcialmente compensada
  pela sonda de legibilidade, que opera com fundamentação jurídica própria em vez de critério
  WCAG.
- Critérios novos da 2.2 ficam fora: 2.4.11 (foco não obscurecido), 2.5.8 (tamanho do alvo de
  toque), 3.3.7 (entrada redundante). O 2.5.8 é particularmente relevante para uso móvel e
  merece nota como limitação no artigo.

---

## Alternativas descartadas

**Incluir AAA como camada informativa separada.** Descartada por complexidade
desproporcional: exigiria um segundo denominador, um segundo índice e uma explicação
adicional em toda saída, para ganho marginal.

**Adotar a WCAG 2.2.** Descartada porque desalinharia o escopo técnico da referência
normativa brasileira, enfraquecendo a vinculação jurídica que é a contribuição central do
projeto.

**Adotar a EN 301 549** (norma europeia de contratação pública). Descartada por não ter
vigência no Brasil; permanece como referência comparativa possível na discussão do artigo.

---

## Revisão

Reavaliar quando o eMAG for atualizado para a WCAG 2.2, ou quando norma federal brasileira
passar a referenciá-la expressamente. A migração exigirá nova ADR, reaferição de κ e nota de
descontinuidade em qualquer série temporal que atravesse a mudança.
