# ADR 0005 — Ponderar os índices por risco jurídico, não por gravidade técnica

**Estado:** aceita

---

## Contexto

O axe-core classifica cada violação em `minor`, `moderate`, `serious` ou `critical`. É uma
escala de **gravidade técnica**: quão severamente a implementação está errada.

Um índice de conformidade precisa de pesos. A escolha óbvia seria usar essa escala. Ela é
inadequada para o objeto deste estudo.

---

## Decisão

Ponderar por **risco jurídico** (`LegalRisk`), escala própria com quatro faixas, definida em
`domain/mapping.py` e graduada por três vetores combinados: essencialidade do serviço
obstruído, existência de rota alternativa e reversibilidade do dano.

| Faixa | Peso | Critérios |
|---|---|---|
| Crítico | 12 | 4 |
| Alto | 7 | 18 |
| Moderado | 3 | 19 |
| Baixo | 1 | 9 |

A gravidade técnica **não é descartada**: entra no cálculo do IAN, multiplicada pelo peso
jurídico, e é reportada separadamente em cada achado. São dimensões independentes.

---

## Justificativa

As duas escalas divergem sistematicamente, e a divergência é informativa:

| Situação | Gravidade técnica | Risco jurídico |
|---|---|---|
| `lang` ausente no `<html>` | `serious` | **Alto** — a informação de saúde é publicada e não é comunicada |
| Contraste 4,4:1 em rodapé institucional | `serious` | **Alto**, mas em página não essencial (φ = 1) |
| `div[onclick]` no botão de confirmar consulta | `critical` | **Crítico** — não há rota alternativa |
| `tabindex="3"` em formulário | `moderate` | **Alto** — induz submissão de dados de saúde incompletos |
| Trecho em inglês sem `lang` | `minor` | **Baixo** |

O caso decisivo é o quarto: uma falha tecnicamente moderada que, no contexto de um formulário
de agendamento, produz erro de dado clínico. A escala técnica não tem como saber disso,
porque não conhece o contexto do serviço.

Um índice ponderado por gravidade técnica responderia "quão mal implementado está o portal".
O ponderado por risco jurídico responde **"quanto isso impede o cidadão de ser atendido"** —
que é a pergunta da pesquisa.

---

## Consequências

**Positivas**

- Violar 2.1.1 (teclado) derruba o ICA doze vezes mais que violar 3.1.2 (idioma de partes),
  o que corresponde à realidade da exclusão produzida.
- A priorização de correção que o relatório sugere é a priorização que um gestor público
  deveria adotar.
- O IEJ pode ignorar risco baixo, afirmando que passivo jurídico não se mede por
  irregularidade formal.

**Negativas assumidas**

- A gradação envolve **juízo de valor** e é contestável. Mitigado por: cada mapeamento
  declara a tese que sustenta sua classificação; a matriz é consultável pela API; e alterar a
  gradação não exige recoletar dados, apenas reindexar (ADR 0003).
- Os índices não são diretamente comparáveis com os de outras ferramentas. Aceitável: o
  projeto reporta também a contagem bruta de violações e de ocorrências.

---

## Alternativa descartada

**Publicar os dois índices, um por escala.** Duplicaria toda a saída e transferiria ao leitor
a decisão de qual usar — que é exatamente a decisão metodológica que o projeto precisa tomar
e defender.
