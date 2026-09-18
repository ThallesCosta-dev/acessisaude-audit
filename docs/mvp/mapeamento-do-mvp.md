# Mapeamento do MVP: AcessiSaúde-Audit

**Escopo essencial, arquitetura tecnológica e plano de entregas da ferramenta computacional de auditoria contínua de acessibilidade web (WCAG 2.1 / LBI) para plataformas públicas de saúde**

| | |
|---|---|
| Disciplina | 5-PJS 2026.2_Noturno |
| Professor | Ricardo Marciano |
| Grupo | Thalles Ferreira Costa (thalles.costa@ioc.fiocruz.br); Bruno de Araujo de Jesus; Jonathas Batista |
| Tema | Tema 6 — Avaliador Automático de Acessibilidade e Direitos Digitais em Saúde |
| Artigo associado | Acessibilidade digital em plataformas públicas de saúde no Rio de Janeiro: auditoria automatizada contínua e qualificação jurídica das barreiras (submissão à Reciis) |
| Versão do documento | 1.0, de 15/09/2026 |
| Prazo da entrega | 20/10/2026 |
| Repositório | AGPL-3.0; endereço público informado após a avaliação duplo-cega do artigo |


## 1. Visão do produto

### 1.1 O problema

Quando um serviço público de saúde migra para o meio digital, a acessibilidade da interface deixa de ser questão de usabilidade e passa a ser condição de exercício de um direito. O art. 63 da Lei Brasileira de Inclusão (Lei 13.146/2015) obriga os órgãos de governo a manter sítios acessíveis "conforme as melhores práticas e diretrizes de acessibilidade adotadas internacionalmente", e a Lei 14.129/2021 inclui a acessibilidade entre os princípios do governo digital. A norma existe há dez anos e a literatura brasileira mostra, desde 2005, que sua existência não produziu, por si, efeito mensurável.

Ferramentas automáticas de avaliação de acessibilidade existem e são boas no que fazem. Nenhuma delas responde às três perguntas que interessam a quem discute política pública de saúde:

1. **Qual norma foi violada e quem é o sujeito obrigado?** Um relatório que diz "contraste 2,9:1" não move um gestor. Um que diz "violação do art. 63, caput, da LBI, exigível por ação civil pública" move.
2. **Quem exatamente fica de fora?** A contagem de defeitos mede o trabalho do desenvolvedor; o dano juridicamente relevante é o da pessoa excluída.
3. **Quanto custa chegar até aqui?** Para o usuário periférico, com plano pré-pago, aparelho de entrada e rede instável, o peso da página em bytes é barreira que as diretrizes não enxergam.

### 1.2 A solução

O AcessiSaúde-Audit é uma aplicação que realiza varreduras automáticas em portais públicos de saúde, avalia a conformidade com as diretrizes WCAG 2.1 (níveis A e AA) e com a Lei Brasileira de Inclusão, e produz, a partir do mesmo dado e com procedência auditável, três camadas por achado: a **técnica** (regra, gravidade, seletor, valores medidos), a **normativa** (critério WCAG violado) e a **jurídica** (dispositivo invocável, sujeito obrigado, via de exigibilidade). Complementa a auditoria com a medição do custo de acesso em dados móveis e com um perfil de exclusão por grupo afetado, e repete a varredura diariamente, porque a barreira de hoje pode não ser a de amanhã.

### 1.3 Usuários e valor entregue

| Usuário | O que recebe do MVP |
|---|---|
| Pesquisador (autor do artigo) | Dataset primário reexecutável (JSON), índices calibrados, série temporal e figuras do artigo |
| Gestor público de saúde | Relatório HTML autocontido e acessível, com a conduta corretiva de cada achado em linguagem de gestor |
| Órgão de controle (Ministério Público, Defensoria, Controladoria) | Qualificação jurídica de cada barreira: dispositivo, tese, sujeito obrigado e via de exigibilidade |
| Equipe de desenvolvimento do portal | Achado técnico com seletor CSS, valores medidos e regra do axe-core, reproduzível |
| Sociedade civil e imprensa | Painel público com índices por plataforma e por esfera federativa, com cobertura declarada |

### 1.4 Princípios que definem o produto

- **Ausência de achado não é conformidade.** Dos 50 critérios modelados, 27 admitem veredito automático, e só para alguns modos de falha. O instrumento estabelece um piso de não conformidade, nunca um atestado.
- **Violação e indício não se confundem.** Vereditos indeterminados jamais viram violação, e sondas heurísticas são impedidas por contrato, verificado em teste, de reprovar.
- **Nenhum número circula sem seus parâmetros.** Todo índice viaja com as constantes que o produziram; todo achado, com a versão do motor que o detectou.
- **A ferramenta obedece às regras que aplica.** O painel e o relatório são auditados pelo mesmo motor, e a construção falha diante de qualquer violação de nível A ou AA.


## 2. Escopo essencial do MVP

### 2.1 Objetivo do MVP

Entregar, até 20/10/2026, um instrumento funcional, aferido e documentado que (a) audite plataformas públicas de saúde contra a WCAG 2.1 A/AA, (b) qualifique juridicamente cada achado pela matriz WCAG↔LBI, (c) produza índices com cobertura declarada, (d) opere em série diária sem intervenção manual e (e) sustente os resultados do artigo científico submetido à Reciis.

### 2.2 Funcionalidades essenciais (dentro do escopo)

| # | Funcionalidade | Critério de aceitação | Situação em 15/09 |
|---|---|---|---|
| F1 | Catálogo de alvos com desenho amostral declarado | Cada alvo tem justificativa de inclusão obrigatória; alvos nascem desabilitados | Concluída: 5 plataformas habilitadas em 3 esferas federativas |
| F2 | Varredura com navegador real em dois perfis de dispositivo | Chromium via Playwright, contexto isolado por página, perfis desktop e móvel 320 px | Concluída |
| F3 | Regras determinísticas do axe-core 4.13.0, vendorizado | Injeção em todos os quadros; recorte às tags WCAG 2.x A/AA; falha na injeção nunca vira aprovação | Concluída |
| F4 | Sondas próprias para o que o axe não alcança | 16 sondas cobrindo 18 critérios e 2 dimensões sem correspondência WCAG; sondas heurísticas não reprovam | Concluída |
| F5 | Matriz WCAG↔LBI | 50 critérios mapeados a 22 dispositivos normativos, com risco jurídico, tese e conduta corretiva; integridade 50/50 verificada em teste | Concluída |
| F6 | Índices com cobertura declarada | ICA, IAN, IEJ, barreira absoluta e custo de acesso; campo `coverage` em toda saída; índices nulos quando não há observação | Concluída (ADR 0005, 0007, 0010) |
| F7 | Medição do custo de acesso em dados móveis | Bytes efetivamente trafegados por página, com parâmetros de preço e franquia datados e registrados no `config_snapshot` | Concluída (ADR 0006) |
| F8 | Persistência com documento JSON como fonte da verdade | JSON íntegro gravado em disco e no banco; índice relacional reconstruível por `reindexar` | Concluída (ADR 0003) |
| F9 | Relatório HTML autocontido e acessível | Sem JavaScript nem recursos externos; conforme WCAG 2.1 AA; auditado pelo próprio motor | Concluída |
| F10 | Exportação em CSV formato longo | Achados e páginas exportáveis para pandas ou Excel | Concluída |
| F11 | API REST | Rotas de referência normativa, alvos, varreduras, índices, relatório e CSV; documentação OpenAPI em `/docs` | Concluída |
| F12 | Painel web | Visão geral, lista de alvos, detalhe da varredura e referência normativa; consome a matriz pela API em vez de duplicá-la | Concluída; refinamento visual em andamento |
| F13 | Auditoria contínua agendada com portão de aferição | Execução diária; nada toca portal público se o instrumento reprovar no conjunto de validação | Concluída; série de 22 dias (19/08 a 09/09) e em curso |
| F14 | Conjunto de validação sintético | 20 barreiras plantadas cobrindo 21 critérios; página de controle conforme sem violação | Concluída: 18 detectadas, 3 fora do alcance automático, declaradas |
| F15 | Conduta ética de coleta implementada como falha, não recomendação | Identificação obrigatória no User-Agent; respeito a `robots.txt`; intervalo mínimo de 2 s; alvos desabilitados por padrão | Concluída |
| F16 | Instalação em um clique no Windows | `iniciar.bat` cria o ambiente, instala dependências, roda a primeira auditoria e sobe API e painel | Concluída |
| F17 | Depósito público de código e dados com identificador persistente | Repositório público e DOI dos dados primários e do material suplementar | **Pendente**, prevista para a entrega E6 |

### 2.3 Fora do escopo do MVP

Declarado para evitar expansão silenciosa:

- Critérios de nível AAA da WCAG 2.1 e critérios novos da WCAG 2.2 (ADR 0001).
- Avaliação de aplicativos móveis nativos (Android/iOS). O MVP audita a versão web das plataformas.
- Áreas autenticadas dos portais. A coleta restringe-se a páginas públicas, sem preenchimento de formulários nem transmissão de dados, o que dispensa submissão ao sistema CEP/Conep.
- Teste com usuários reais. O instrumento mede uma parte da norma; a experiência da pessoa com deficiência é objeto de trabalho futuro.
- Emissão automática de peças jurídicas (notificações, representações). O MVP fornece a fundamentação; a peça é do operador do direito.
- Integração com o eMAG como validador independente. O eMAG é referência normativa, não motor de regras do MVP.
- Correção automática das barreiras nos portais auditados.

### 2.4 Requisitos não funcionais

| Requisito | Meta | Verificação |
|---|---|---|
| Reprodutibilidade | Toda varredura carrega versão do motor, do axe-core e o `config_snapshot` completo | Teste de persistência |
| Robustez | Falha em uma página não interrompe a varredura; vira `PageAudit` com status de erro e entra na taxa de perda | Teste de integração |
| Acessibilidade do próprio produto | Painel e relatório sem violação A/AA | 18 testes de acessibilidade com `@axe-core/playwright`, na construção |
| Qualidade de código | Tipagem estrita (mypy strict), lint (ruff), arquitetura verificada por teste estático | 115 testes unitários, ~2 s |
| Conduta de coleta | Cerca de 10 páginas por plataforma por execução; carga inferior à de um rastreador de busca comum | Parâmetros no catálogo e no ambiente |
| Portabilidade | Windows, Linux e macOS; imagem Docker única para coleta e API | Dockerfile e `iniciar.bat` |
| Licença | AGPL-3.0-or-later | `pyproject.toml` e `package.json` |


## 3. Arquitetura tecnológica

### 3.1 Visão geral

O sistema tem quatro blocos: o **motor de auditoria** (Python, Playwright, axe-core e sondas próprias), o **domínio normativo** (matriz WCAG↔LBI e índices, em Python puro), a **persistência e publicação** (JSON, SQLite ou PostgreSQL, relatório HTML, CSV) e a **interface** (API FastAPI e painel React). A regra única de arquitetura é que **as dependências apontam para dentro, em direção ao domínio**, e ela é verificada por análise estática do código-fonte em teste automatizado, não prometida em documento.

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

A pureza do domínio importa porque ele codifica a contribuição científica do projeto: um revisor avalia a matriz sem instalar Chromium, os índices são recalculados sobre dados já coletados sem revarrer portais, e a matriz é citável independentemente da implementação de coleta.

### 3.2 Pilha tecnológica

| Camada | Tecnologia | Versão mínima | Papel |
|---|---|---|---|
| Linguagem do backend | Python | 3.11 (3.12 na imagem Docker) | Motor, domínio, API, análise |
| Navegador de coleta | Playwright + Chromium | 1.47 | DOM renderizado, interação real (Tab), contabilidade de bytes |
| Regras de acessibilidade | axe-core, vendorizado | 4.13.0 | Regras determinísticas sobre o DOM (ADR 0002) |
| Modelagem de dados | Pydantic | 2.8 | Contratos `Finding`, `PageAudit`, `ScanResult`; validação do JSON |
| Persistência | SQLAlchemy + Alembic; SQLite (local) ou PostgreSQL (nuvem) | 2.0 / 1.13 | Índice relacional derivado do documento JSON |
| API | FastAPI + Uvicorn | 0.115 / 0.30 | Casca fina sobre o domínio; OpenAPI |
| Linha de comando | Typer + Rich | 0.12 / 13.7 | `acessisaude alvos | criterios | matriz | varrer | relatorio | exportar | servir | reindexar` |
| Relatório | Jinja2 | 3.1 | HTML autocontido, sem JavaScript |
| Análise estatística | pandas, numpy, scipy, statsmodels, matplotlib | extra `analysis` | Dataset, testes, figuras do artigo |
| Painel | React 18, React Router 6, TypeScript 5.6, Vite 5 | | Interface para gestor e público |
| Qualidade | pytest, pytest-asyncio, ruff, mypy strict, eslint + jsx-a11y, @axe-core/playwright | | Testes, lint, tipagem, acessibilidade do painel |
| Implantação | Docker (python:3.12-slim), GitHub Actions, Render (cron + Postgres + web + static) | | Coleta agendada e painel público |
| Ponto de observação alternativo | Google Apps Script (sonda de vantagem) e contêiner mínimo (Cloud Run) | | Controle de rede: distingue portal indisponível de portal que recusa o IP (ADR 0009) |

### 3.3 Componentes do backend

| Pacote | Responsabilidade |
|---|---|
| `domain/wcag.py` | Os 50 critérios A/AA, com grupos afetados e justificativa em linguagem de gestor |
| `domain/lbi.py` | 22 dispositivos normativos (12 da LBI, 3 constitucionais, 2 da Convenção da ONU e correlatos), com citação, sujeito obrigado e via de exigibilidade |
| `domain/mapping.py` | A matriz: 50 mapeamentos com risco jurídico, tese e conduta corretiva |
| `domain/models.py` | Contrato de dados da pesquisa |
| `domain/scoring.py` | ICA, IAN, IEJ, barreira absoluta e custo de acesso; tabela de calibração |
| `catalog/` | Catálogo YAML dos alvos: desenho amostral, não configuração |
| `auditor/browser.py` | Contextos isolados, parâmetros fixados (locale, fuso, esquema de cores), contabilidade de rede |
| `auditor/axe_runner.py` | Injeção do axe-core em todos os quadros e tradução para o domínio |
| `auditor/probes/` | 16 sondas: estrutura, teclado, formulários, viewport, mídia, direitos digitais |
| `auditor/crawler.py` | `robots.txt`, intervalo entre requisições, descoberta de links |
| `auditor/engine.py` | Planejamento antes do navegador; falhas viram dado |
| `persistence/` | Repositório, ORM, reindexação a partir do JSON |
| `reporting/` | Relatório HTML e exportação CSV |
| `analysis/` | Dataset, estatística e figuras |
| `api/` | Roteadores de referência, alvos e varreduras |
| `cli.py` | Interface de linha de comando |

### 3.4 Fluxo de uma varredura

```
1. catálogo          →  alvo + sementes (exclui as que exigem autenticação)
2. plan()            →  lista de tarefas (URL × perfil), conhecida antes de abrir o navegador
3. por tarefa:
     robots.txt      →  permitido?
     intervalo       →  aguarda a cortesia devida ao host
     browser.open()  →  contexto novo, sem cache, com contabilidade de bytes
     axe-core        →  regras determinísticas sobre o DOM
     16 sondas       →  interação real, medição de rede, legibilidade
4. ScanResult        →  JSON + banco + relatório HTML
```

Cada achado sai com três camadas: técnica (regra, gravidade, seletor CSS, valores medidos), normativa (critério WCAG 2.1) e jurídica (risco, tese, dispositivos invocáveis, via de exigibilidade). O motor não decide o que é violação (axe e sondas), o que é ilegal (`mapping.py`) nem como pontuar (`scoring.py`): as três decisões que precisam ser defendidas no artigo ficam fora do código de coleta.

### 3.5 Modelo de dados

O **documento JSON de cada varredura é a fonte da verdade** e o dado primário da pesquisa. As tabelas `scans` e `findings` são índice achatado, para consulta rápida, e podem ser reconstruídas a qualquer momento por `acessisaude reindexar`. Isso torna operacional a promessa de que mudar o cálculo de um índice, ou a interpretação jurídica de um critério, não exige revarrer portal algum.

Cada varredura carrega: identificação do alvo, data e hora, perfis de dispositivo, versão do motor e do axe-core, `config_snapshot` com todos os parâmetros de pontuação e custo, lista de páginas com status (`OK`, `TIMEOUT`, `HTTP_ERROR`, `BLOCKED_BY_ROBOTS`, `NAVIGATION_ERROR`), bytes trafegados por domínio, achados, índices com campo `coverage` e taxa de perda. O dicionário de dados completo está em `docs/api/dicionario-de-dados.md`.

### 3.6 API

| Grupo | Rotas |
|---|---|
| Operação | `GET /saude` |
| Referência normativa | `GET /referencia/criterios`, `GET /referencia/criterios/{id}`, `GET /referencia/dispositivos`, `GET /referencia/dispositivos/{chave}`, `GET /referencia/integridade-da-matriz` |
| Alvos | `GET /alvos`, `GET /alvos/{id}`, `GET /alvos/{id}/paginas` |
| Varreduras | `POST /varreduras` (202), `GET /varreduras/trabalhos/{job_id}`, `GET /varreduras`, `GET /varreduras/{id}`, `GET /varreduras/{id}/indices`, `GET /varreduras/{id}/relatorio` (HTML), `GET /varreduras/{id}/achados.csv`, `GET /varreduras/agregados/criterios`, `DELETE /varreduras/{id}` |

O painel consome a rota de referência em vez de reimplementar a matriz em TypeScript; do contrário ela existiria em duas versões, e elas divergiriam.

### 3.7 Painel

Quatro telas: **Visão geral** (índices por plataforma e por esfera, série diária), **Alvos** (catálogo, estado de habilitação, justificativa de inclusão), **Detalhe da varredura** (achados por página, três camadas, relatório e CSV) e **Referência** (50 critérios, 22 dispositivos, integridade da matriz). Toda tela repete a advertência de que ausência de achado não equivale a conformidade. O painel é auditado pelo mesmo axe-core que ele exibe, em dois perfis de dispositivo, e a construção falha diante de qualquer violação de nível A ou AA; duas correções reais de acessibilidade no próprio painel foram descobertas por essa suíte.

### 3.8 Implantação

| Cenário | Composição | Uso |
|---|---|---|
| Local, um clique | `iniciar.bat`: venv, backend, Chromium, painel, primeira auditoria contra o conjunto de validação, API em :8000 e painel em :5173 | Demonstração e desenvolvimento |
| GitHub Actions (recomendado para a pesquisa) | Workflow `coleta.yml`: aferição, coleta dos alvos habilitados, exportação; dados no ramo órfão `serie-temporal`, versionados e citáveis por commit | Produção da série do artigo; custo zero |
| Tarefa agendada em máquina brasileira | `scripts/coleta-diaria.ps1`, uma vez por dia, com IP residencial nacional | Braço brasileiro da série (o runner do GitHub recebeu HTTP 403 de uma plataforma) |
| Render (painel público) | `render.yaml`: cron de coleta (3 janelas diárias), PostgreSQL, API e painel estático; imagem Docker única | Monitoramento visível a gestor; o cron não tem disco persistente, e o JSON sobrevive na coluna `document` do Postgres |

Ordem de uma execução agendada: (1) varre o conjunto de validação sintético; (2) **afere** o instrumento contra essa varredura e aborta se reprovar; (3) varre os alvos habilitados; (4) exporta o dataset acumulado. Um instrumento não aferido não toca portal público.

### 3.9 Decisões de arquitetura registradas

| ADR | Decisão |
|---|---|
| 0001 | Escopo restrito aos níveis A e AA da WCAG 2.1 |
| 0002 | Vendorizar o axe-core em vez de baixá-lo em execução |
| 0003 | JSON como fonte da verdade, SQL como índice |
| 0004 | Escrever sondas próprias além do axe-core |
| 0005 | Ponderar os índices por risco jurídico, não por gravidade técnica |
| 0006 | Tratar o custo de acesso como barreira auditável |
| 0007 | Recalibrar κ empiricamente (40 → 150) |
| 0008 | User-Agent explícito em todos os perfis |
| 0009 | O ponto de observação de rede é variável do estudo |
| 0010 | Índices nulos quando não há observação: nulo não é zero |

### 3.10 Segurança, ética e conformidade

- A coleta restringe-se ao documento renderizado de páginas públicas, sem autenticação, sem preenchimento de formulários e sem transmissão de dados pessoais; não se enquadra nas hipóteses de submissão ao CEP/Conep (Resolução CNS 510/2016).
- Identificação obrigatória do pesquisador no User-Agent; sem ela o script de coleta recusa executar.
- Respeito a `robots.txt` por padrão; desativar exige justificativa registrada, que fica gravada no dataset.
- Alvos nascem desabilitados; habilitar é decisão consciente, registrada em commit.
- Segredos (contato da pesquisa, URL do banco, origens CORS) ficam fora do repositório, em variáveis de ambiente marcadas `sync: false`.
- Comunicação prévia aos órgãos auditados, com o relatório HTML encaminhado, integra a conduta declarada do projeto.


## 4. Plano de entregas

### 4.1 Entregas já realizadas

| Entrega | Data | Conteúdo |
|---|---|---|
| E0 — Núcleo do instrumento | 15/08/2026 | Domínio normativo, motor de auditoria, 16 sondas, persistência, relatório, API, painel, testes |
| E1 — Coleta de campo | 15/08/2026 | Parâmetros de custo coletados e datados; primeira coleta em 5 plataformas; segunda e terceira medições; correção de defeito de identificação do instrumento |
| E2 — Auditoria contínua | 17 a 19/08/2026 | Workflow agendado com portão de aferição; braço brasileiro da série; sonda de vantagem em terceiro ponto de observação; ADR 0009 |
| E3 — Série diária e correção do instrumento | 31/08/2026 | 13 dias de série; índices nulos sem observação (ADR 0010); série entra no artigo |
| E4 — Manuscrito em duas versões | 04 a 05/09/2026 | Versão reduzida (59.984 caracteres) para a Reciis e versão estendida; bloco transversal de 04/09 com 20/20 auditorias; verificação automática de divergência entre as versões |
| E5 — Revisão pela autoavaliação da revista | 09/09/2026 | Todos os pontos do roteiro da Reciis corrigidos nas duas versões; figuras regeradas; janela da série em 22 dias |

### 4.2 Cronograma até 20/10/2026

| Semana | Período | Entrega | Atividades | Resultado verificável |
|---|---|---|---|---|
| S1 | 15 a 20/09 | E6a — Fechamento da série | Fixar a data de corte da série diária no registro de campo; reprocessar (`reindexar`, `gerar_figuras.py`); refazer a contagem de caracteres | Data de corte registrada; figuras e tabelas coerentes com o corte; contagem dentro do limite |
| S1 | 15 a 20/09 | Entrega da disciplina (09 a 11/09) | PDF compilado dos artigos; introdução no formato da revista; documento com membros, revista e introdução | Três arquivos enviados ao professor |
| S2 | 21 a 27/09 | E6b — Depósito com identificador persistente | Depositar dados primários (JSON da série) e material suplementar (justificativa por alvo; matriz dos 50 critérios com os três vetores de risco) em repositório com DOI; publicar o código | DOI dos dados e do material suplementar; repositório público |
| S2 | 21 a 27/09 | E6c — Conferência de referências | Substituir a citação da Anatel pelo relatório primário; confirmar paginação e DOI das seis referências pendentes; reconferir parâmetros de custo com captura arquivada | Tabela de conferência da folha de submissão sem itens abertos |
| S3 | 28/09 a 04/10 | E7 — Submissão à Reciis | Converter o manuscrito para `.docx` no formato da revista (Arial 11, 1,5, A4, 2 cm; tabelas em 10 pt e abertas nas laterais); remover identificação de autoria das propriedades do arquivo; preencher folha de rosto e declaração de responsabilidade; anexar as cinco figuras em SVG; comunicar previamente os órgãos auditados com o relatório | Protocolo de submissão emitido pelo sistema da revista |
| S4 | 05 a 11/10 | E8 — Consolidação do MVP | Refinamento visual do painel já em andamento (App, Dashboard, Alvos, Detalhe, Referência); rodar a suíte completa (115 unitários, 18 de integração, 18 de acessibilidade); revisar documentação de instalação e uso; validar o `iniciar.bat` em máquina limpa | Suíte verde; instalação em um clique validada; documentação atualizada |
| S5 | 12 a 18/10 | E9 — Documento final do MVP | Atualizar este documento com o estado real de cada funcionalidade e entrega; incluir capturas do painel e do relatório; preparar apresentação de 10 minutos com demonstração ao vivo contra o conjunto de validação | Versão 2.0 deste documento em `.docx` e `.pdf` |
| S6 | 19 a 20/10 | Entrega final | Revisão final e envio | Documento entregue em 20/10/2026 |

### 4.3 Marcos

| Marco | Data | Critério |
|---|---|---|
| M1 — Série fechada | 20/09/2026 | Data de corte registrada e figuras regeradas |
| M2 — Dados depositados | 27/09/2026 | DOI emitido |
| M3 — Artigo submetido | 04/10/2026 | Protocolo da Reciis |
| M4 — MVP consolidado | 11/10/2026 | Suíte verde e instalação validada |
| M5 — Documento do MVP entregue | 20/10/2026 | Envio ao professor |

### 4.4 Definição de pronto

Uma entrega está pronta quando: (a) os testes automatizados passam; (b) toda decisão que altere números publicáveis tem ADR; (c) o `scripts/conferir_manuscritos.py` não acusa divergência entre as versões do manuscrito; (d) a documentação em `docs/` reflete o comportamento do código; (e) o resultado verificável da tabela 4.2 existe e pode ser mostrado.

### 4.5 Papéis

| Papel | Responsável | Atribuições |
|---|---|---|
| Concepção, desenvolvimento, coleta, análise e redação | Thalles Ferreira Costa | Entregas E0 a E9 |
| Revisão do manuscrito e das entregas da disciplina | Bruno de Araujo de Jesus | Atribuição a confirmar com o grupo |
| Revisão do manuscrito e das entregas da disciplina | Jonathas Batista | Atribuição a confirmar com o grupo |


## 5. Riscos e mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Portal auditado bloqueia o ponto de observação (HTTP 403 ao runner do GitHub) | Ocorreu | Perda de série para uma plataforma | Braço brasileiro da coleta em IP residencial e sonda de vantagem em terceiro ponto (ADR 0009); "sem veredito" é valor representável, nunca convertido em conformidade |
| Atualização do axe-core muda o que é detectável e cria degrau na série | Média | Comparabilidade | axe-core vendorizado e fixado em 4.13.0; versão gravada em cada varredura; troca exige ADR e série nova |
| Mudança de parâmetros de custo (preço e franquia da oferta pré-paga) | Alta | Custo de acesso não comparável | Parâmetros datados no `config_snapshot`; reavaliação registrada em ADR |
| Manuscrito ultrapassa 60 mil caracteres após a conversão para `.docx` | Média | Recusa na triagem | Margem de 16 caracteres; recontagem no editor prevista na E7; versão estendida disponível para periódico de limite maior |
| Depósito dos dados atrasa (repositório, DOI) | Média | Afirmação do artigo sobre depósito público fica falsa | Entrega E6b antes da submissão; a submissão (E7) depende de M2 |
| Indisponibilidade prolongada de plataforma na janela final | Baixa | Perda mensurável | Falhas viram dado com `loss_rate`; o método já trata o caso (§ 4.7 do manuscrito) |
| Dependência de uma única pessoa para todas as entregas | Alta | Atraso em caso de indisponibilidade | Documentação completa em `docs/`, ADR, `iniciar.bat` e suíte de testes permitem que outro membro reproduza e continue |


## 6. Glossário

| Termo | Significado |
|---|---|
| WCAG 2.1 | Web Content Accessibility Guidelines, versão 2.1, do W3C; níveis A, AA e AAA |
| LBI | Lei Brasileira de Inclusão da Pessoa com Deficiência, Lei 13.146/2015 |
| eMAG | Modelo de Acessibilidade em Governo Eletrônico, versão 3.1 |
| axe-core | Motor de regras de acessibilidade da Deque, de código aberto |
| Sonda | Verificação própria do projeto para o que o axe-core não alcança (interação, rede, legibilidade) |
| ICA | Índice de conformidade de acessibilidade |
| IAN | Índice de atrito de navegação |
| IEJ | Índice de exposição jurídica |
| Barreira absoluta | Violação crítica sem rota alternativa, que impede o uso do serviço |
| Custo de acesso | Bytes trafegados convertidos em fração da franquia e em reais, com parâmetros datados |
| Usuário periférico | Quem depende exclusivamente do sistema público de saúde e o acessa por conectividade precária |
| Cobertura | Fração dos critérios que o instrumento é capaz de verificar automaticamente; declarada em toda saída |
| ADR | Registro de decisão de arquitetura (Architecture Decision Record) |
| Série diária | Varredura repetida uma vez por dia das cinco plataformas, de 19/08/2026 em diante |
