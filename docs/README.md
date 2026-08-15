# Documentação

Índice completo. Comece pelo [README do repositório](../README.md) se ainda não o leu.

---

## Por objetivo

### Quero rodar a ferramenta
→ [Instalação e uso](operacao/instalacao-e-uso.md)

### Quero entender como funciona
→ [Visão geral da arquitetura](arquitetura/visao-geral.md)
→ [O motor de auditoria](arquitetura/motor-de-auditoria.md)
→ [Decisões de arquitetura](adr/)

### Quero avaliar se o método se sustenta
→ [Protocolo metodológico](metodologia/protocolo.md)
→ [Índices: construção e calibração](metodologia/indices.md)
→ [Limites conhecidos do axe-core](metodologia/limites-do-axe-core.md)
→ [Desenho amostral](metodologia/amostragem.md)
→ [Reprodutibilidade](metodologia/reprodutibilidade.md)

### Quero avaliar a fundamentação jurídica
→ [Matriz WCAG ↔ LBI](juridico/matriz-wcag-lbi.md)
→ [Limites e ressalvas](juridico/limites-e-ressalvas.md)

### Quero usar os dados
→ [Dicionário de dados](api/dicionario-de-dados.md)
→ [Referência da API](api/referencia.md)

### Quero coletar em portais reais
→ [Ética e conduta de coleta](metodologia/etica-e-conduta-de-coleta.md) — **leitura obrigatória**
→ [Desenho amostral](metodologia/amostragem.md)

### Quero escrever o artigo
→ [Esqueleto IMRaD](artigo/esqueleto.md)

---

## Decisões de arquitetura

| # | Decisão |
|---|---|
| [0001](adr/0001-escopo-wcag-a-aa.md) | Escopo restrito aos níveis A e AA da WCAG 2.1 |
| [0002](adr/0002-axe-core-vendorizado.md) | Vendorizar o axe-core |
| [0003](adr/0003-documento-json-como-fonte-da-verdade.md) | JSON como fonte da verdade, SQL como índice |
| [0004](adr/0004-sondas-proprias.md) | Escrever sondas próprias |
| [0005](adr/0005-indices-ponderados-por-risco-juridico.md) | Ponderar por risco jurídico |
| [0006](adr/0006-custo-de-dados-como-barreira.md) | Custo de acesso como barreira auditável |
| [0007](adr/0007-calibracao-empirica-de-kappa.md) | Recalibração empírica de κ |

---

## Três coisas que a documentação insiste em repetir

**Ausência de achado não é conformidade.** 27 dos 50 critérios admitem veredito automático, e
apenas para alguns modos de falha. A ferramenta produz um piso de não conformidade.

**Violação e indício não se confundem.** Vereditos `INCOMPLETE` nunca viram violação, e sondas
heurísticas são impedidas por contrato de reprovar.

**Nenhum número circula sem seus parâmetros.** Todo índice viaja com as constantes que o
produziram, e todo achado com a versão do motor que o detectou.

---

## Documentação que vive no código

Parte substantiva das decisões está documentada onde importa — ao lado da implementação:

| Assunto | Onde |
|---|---|
| Justificativa de cada critério WCAG, em linguagem de gestor | `domain/wcag.py` |
| Texto, citação e vias de exigibilidade de cada dispositivo | `domain/lbi.py` |
| Tese jurídica e conduta corretiva de cada critério | `domain/mapping.py` |
| Fórmulas dos índices e tabela de calibração | `domain/scoring.py` |
| O que cada sonda verifica e qual lacuna ela cobre | `auditor/probes/*.py` |
| Armadilhas de implementação já encontradas | comentários no ponto exato do código |

O último item merece nota: quando um defeito custou tempo para ser diagnosticado — o
`slots=True` que silenciava o registro de tráfego, o `logger.exception` que engolia o
traceback, o foco roubado do link de salto —, a explicação ficou no código, e não em um
documento que ninguém consultaria no momento certo.
