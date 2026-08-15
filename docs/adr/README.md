# Decisões de arquitetura (ADR)

Registro das decisões estruturais do projeto, com o contexto que as motivou e as
consequências assumidas. Existem porque, meses depois, a pergunta "por que isto está assim?"
tem resposta — e porque um artigo que descreve o software precisa poder justificar suas
escolhas.

Formato: contexto → decisão → consequências → alternativas descartadas.

| # | Decisão | Estado |
|---|---|---|
| [0001](0001-escopo-wcag-a-aa.md) | Escopo restrito aos níveis A e AA da WCAG 2.1 | Aceita |
| [0002](0002-axe-core-vendorizado.md) | Vendorizar o axe-core em vez de baixá-lo em execução | Aceita |
| [0003](0003-documento-json-como-fonte-da-verdade.md) | JSON como fonte da verdade, SQL como índice | Aceita |
| [0004](0004-sondas-proprias.md) | Escrever sondas próprias além do axe-core | Aceita |
| [0005](0005-indices-ponderados-por-risco-juridico.md) | Ponderar os índices por risco jurídico, não por gravidade técnica | Aceita |
| [0006](0006-custo-de-dados-como-barreira.md) | Tratar o custo de acesso como barreira auditável | Aceita |
| [0007](0007-calibracao-empirica-de-kappa.md) | Recalibrar κ empiricamente (40 → 150) | Aceita |

## Quando escrever uma nova ADR

Sempre que a decisão:

- alterar números já publicados ou publicáveis (troca do axe-core, recalibração de κ,
  mudança na matriz jurídica);
- quebrar a compatibilidade do esquema de dados;
- alterar a direção das dependências entre camadas;
- ampliar ou reduzir o escopo normativo auditado.

Atualizações de dependência que não afetem resultado não exigem ADR.
