# ADR 0007 — Recalibrar κ empiricamente (40 → 150)

**Estado:** aceita

---

## Contexto

O Índice de Atrito de Navegação satura exponencialmente:

```
IAN = 100 · ( 1 − e^{ −atrito_bruto / κ } )
```

O valor inicial, `κ = 40`, foi escolhido por estimativa, **antes** de qualquer medição. A
docstring afirmava que ele fora calibrado de modo que "uma página com uma falha séria de
risco jurídico alto em um único elemento pontue próximo de 25 e uma página com barreira
absoluta em vários controles ultrapasse 80".

A primeira execução completa contra o conjunto de validação mostrou que **a afirmação era
falsa**.

---

## Medição

| Atrito bruto | Caso de referência | IAN com κ=40 |
|---|---|---|
| 9,0 | uma falha leve isolada | 20,1 |
| 42,0 | uma falha séria de risco alto | **65,0** (afirmado: ~25) |
| 84,0 | duas falhas sérias | 87,8 |
| 306,0 | formulário sem rótulos | 100,0 |
| 1810,8 | caso-controle positivo | 100,0 |

Quatro das cinco fixtures marcavam acima de 98. O índice deixava de distinguir "ruim" de
"inutilizável" — exatamente a distinção que ele existe para fazer, e que sustenta a
comparação entre portais no artigo.

---

## Decisão

`κ = 150`, obtido por aferição sobre o conjunto de validação.

| Atrito bruto | IAN com κ=150 |
|---|---|
| 0,0 | 0,0 |
| 9,0 | 5,8 |
| 42,0 | **24,4** — corresponde ao comportamento declarado |
| 84,0 | 42,9 |
| 306,0 | 87,0 |
| 1810,8 | 100,0 |

Efeito medido na varredura de referência do conjunto de validação:

| | κ = 40 | κ = 150 |
|---|---|---|
| IAN agregado | 100,0 | **96,6** |
| IEJ agregado | 85,2 | **40,0** |

O IEJ era o mais distorcido: saturado em 85 quando o conjunto contém uma página inteiramente
conforme e três com poucas violações.

---

## Consequências

**Positivas**

- A escala discrimina na faixa de interesse.
- O comportamento está travado em teste (`TestCalibracaoDoAtrito`), com quatro asserções que
  fixam os casos de referência e as distâncias entre eles. Alterar κ exige alterar o teste, e
  portanto assumir a mudança.
- O procedimento de recalibração está documentado em
  [`metodologia/indices.md`](../metodologia/indices.md#calibracao).

**Negativas assumidas**

- Nenhum dado precisou ser descartado: a única varredura anterior era de validação, e foi
  reexecutada. Se houvesse coleta de campo, a mudança exigiria reindexar (possível, ADR 0003)
  e declarar descontinuidade em qualquer série temporal.

---

## Nota metodológica

Esta ADR registra um **erro corrigido**, não uma decisão de projeto. Fica no registro porque
é instrutivo: a constante fora escolhida por estimativa, a docstring afirmava uma calibração
que os dados não sustentavam, e o problema só apareceu porque o conjunto de validação existia
e foi efetivamente executado.

É o argumento a favor de golden sets em ferramentas de medição: sem ele, o índice teria sido
publicado saturado, e a conclusão do artigo — "os portais municipais apresentam atrito
significativamente maior" — poderia refletir apenas o teto da escala.
