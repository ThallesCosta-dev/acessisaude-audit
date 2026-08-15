# Visão geral da arquitetura

---

## Regra única

**As dependências apontam para dentro, em direção a `domain`.**

```
                        ┌──────────────────────────┐
   api ──────────────►  │                          │
   cli ──────────────►  │         domain           │
   auditor ──────────►  │                          │
   persistence ──────►  │  wcag.py    normas       │
   reporting ────────►  │  lbi.py     direito      │
   analysis ─────────►  │  mapping.py matriz       │
                        │  models.py  dados        │
   catalog ──────────►  │  scoring.py índices      │
                        │                          │
                        │  PURO: sem navegador,    │
                        │  banco, HTTP ou pandas   │
                        └──────────────────────────┘
```

A regra é **verificada por análise estática do código-fonte**
([`tests/unit/test_arquitetura.py`](../../backend/tests/unit/test_arquitetura.py)), não
prometida em documento. Três testes a sustentam:

- `test_direcao_das_dependencias` — cada camada só importa as camadas permitidas;
- `test_dominio_nao_toca_infraestrutura` — o domínio não importa Playwright, SQLAlchemy,
  FastAPI, pandas nem YAML;
- `test_dominio_nao_faz_io_de_arquivo` — nenhum `open()` no domínio.

### Por que a pureza importa aqui

Não é preferência estética. O domínio codifica **a contribuição científica do projeto**: a
matriz WCAG↔LBI e a construção dos índices. Mantê-lo isolado permite que:

- um revisor avalie a matriz sem instalar Chromium;
- os índices sejam recalculados sobre dados já coletados, sem revarrer portais;
- a contribuição seja citável e reusável independentemente da implementação de coleta.

---

## As camadas

### `domain/` — normas, direito, modelos, índices

| Módulo | Conteúdo |
|---|---|
| `wcag.py` | Os 50 critérios A/AA, com grupos afetados e justificativa em linguagem de gestor |
| `lbi.py` | 22 dispositivos normativos, com citação ABNT, sujeito obrigado e via de exigibilidade |
| `mapping.py` | A matriz: 50 mapeamentos, com risco jurídico, tese e conduta corretiva |
| `models.py` | `Finding`, `PageAudit`, `ScanResult` — o contrato de dados da pesquisa |
| `scoring.py` | ICA, IAN, IEJ, barreira absoluta, custo de acesso |

### `catalog/` — desenho amostral

O catálogo YAML **não é configuração, é desenho amostral**. Cada alvo declara por que integra
a amostra (`selection_rationale`, obrigatório e verificado em teste) e quais páginas ficaram
de fora e por quê (lacunas declaradas).

### `auditor/` — coleta

| Módulo | Responsabilidade |
|---|---|
| `browser.py` | Playwright, contextos isolados, contabilidade de bytes trafegados |
| `axe_runner.py` | Injeção do axe-core em todos os quadros; tradução para o domínio |
| `probes/` | 16 sondas próprias: o que o axe não alcança |
| `crawler.py` | `robots.txt`, intervalo entre requisições, descoberta de links |
| `engine.py` | Orquestração: o que visitar, em que ordem, sob quais restrições |

**O motor é deliberadamente burro.** Ele não decide o que é violação (isso é do axe e das
sondas), não decide o que é ilegal (isso é de `mapping.py`) e não decide como pontuar (isso é
de `scoring.py`). Essa modéstia é arquitetural: as três decisões que ele não toma são
exatamente as que precisam ser defendidas no artigo, e mantê-las fora do código de coleta
permite discuti-las e alterá-las sem tocar no navegador.

### `persistence/` — documento + índice

Estratégia deliberada de duplicação, com direção da verdade explícita:

| Artefato | Papel |
|---|---|
| **JSON** em `data/scans/` e na coluna `document` | **Fonte da verdade.** Dado primário da pesquisa |
| Tabelas `scans` e `findings` | Índice achatado, para consulta rápida |

Em qualquer divergência, o JSON prevalece e o índice é reconstruído por
`ScanRepository.reindex()`. Isso torna operacional a promessa de que mudar o cálculo de um
índice — ou a interpretação jurídica de um critério — **não exige revarrer portal algum**.

### `reporting/` — publicação

Relatório HTML autocontido, sem JavaScript e sem recursos externos: pode ser arquivado como
evidência estável, aberto anos depois ou anexado a um processo. Ele próprio conforme WCAG 2.1
AA — uma ferramenta que emitisse relatório inacessível se desqualificaria.

### `analysis/` — pesquisa

Fronteira entre a ferramenta e a análise estatística. Exige o extra `analysis`; a coleta
funciona sem ele, separação deliberada para que rodar auditorias não imponha a pilha
científica a quem só quer o relatório.

### `api/` + `frontend/`

A API é casca fina sobre o domínio. O painel React consome a rota `/referencia` em vez de
reimplementar a matriz em TypeScript — do contrário ela existiria em duas versões, e elas
divergiriam.

---

## Fluxo de uma varredura

```
1. catálogo          →  alvo + sementes (exclui as que exigem autenticação)
2. plan()            →  lista de tarefas (URL × viewport), conhecida antes de abrir o navegador
3. por tarefa:
     robots.txt      →  permitido?
     intervalo       →  aguarda a cortesia devida ao host
     browser.open()  →  contexto novo, sem cache, com contabilidade de bytes
     axe-core        →  regras determinísticas sobre o DOM
     16 sondas       →  interação real, medição de rede, legibilidade
4. ScanResult        →  JSON + SQLite + relatório HTML
```

Materializar o plano **antes** da execução torna o total conhecido (barra de progresso,
estimativa) e, sobretudo, torna a coleta reproduzível: o plano pode ser inspecionado,
registrado e reexecutado.

### Isolamento por página

Cada página é auditada em **contexto de navegação novo**. O isolamento é metodológico, não
técnico: contextos compartilhados acumulam cache e cookies, o que subestimaria o custo de
dados e mascararia banners de consentimento que só aparecem no primeiro acesso.

---

## Robustez: falhas viram dado, não interrupção

| Falha | Tratamento |
|---|---|
| Página não carrega | `PageStatus.TIMEOUT` / `HTTP_ERROR`; entra na taxa de perda |
| Bloqueada por `robots.txt` | `PageStatus.BLOCKED_BY_ROBOTS`, registrada |
| Sonda lança exceção | Capturada, registrada em log, devolve lista vazia |
| axe-core falha na injeção | Página registrada **sem achados do axe**, não com zero violações |
| Quadro cross-origin | Registrado como região opaca à auditoria |

A última linha da tabela é a mais importante: **"não medido" nunca é convertido em
"conforme"**. Uma varredura que morre na página 12 de 40 perde as 28 seguintes; uma que
registra o erro mantém o dataset utilizável com perda mensurável — e a `loss_rate` aparece em
toda saída.

---

## Onde as decisões estão registradas

| Assunto | Documento |
|---|---|
| Decisões de arquitetura | [`docs/adr/`](../adr/) |
| Construção e calibração dos índices | [`docs/metodologia/indices.md`](../metodologia/indices.md) |
| Limites do axe-core e por que existem sondas | [`docs/metodologia/limites-do-axe-core.md`](../metodologia/limites-do-axe-core.md) |
| Conduta de coleta | [`docs/metodologia/etica-e-conduta-de-coleta.md`](../metodologia/etica-e-conduta-de-coleta.md) |
| Fundamentação jurídica | [`docs/juridico/matriz-wcag-lbi.md`](../juridico/matriz-wcag-lbi.md) |
| Formato do dado | [`docs/api/dicionario-de-dados.md`](../api/dicionario-de-dados.md) |
