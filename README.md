# AcessiSaúde-Audit

**Ferramenta computacional de auditoria contínua de acessibilidade web (WCAG 2.1 / LBI)
para plataformas públicas de saúde.**

Audita portais e aplicações de saúde pública contra as diretrizes WCAG 2.1 (níveis A e AA)
e converte cada falha técnica em uma proposição jurídica fundamentada na Lei Brasileira de
Inclusão (Lei 13.146/2015) e no arcabouço normativo correlato.

---

## O problema

Quando um serviço público de saúde migra para o meio digital, a acessibilidade da interface
deixa de ser questão de usabilidade e passa a ser condição de exercício de um direito. Se o
botão de confirmar consulta não recebe foco do teclado, a pessoa com deficiência motora não
tem consulta — não tem uma experiência ruim, não tem consulta.

Ferramentas de auditoria de acessibilidade existem e são boas no que fazem. Nenhuma delas,
porém, responde às três perguntas que interessam a quem discute política pública de saúde:

1. **Qual norma foi violada, e quem é o sujeito obrigado?**
   Um relatório que diz "contraste 2.9:1" não move um gestor público. Um que diz
   "violação do art. 63, caput, da LBI c/c art. 47 do Decreto 5.296/2004, exigível por ação
   civil pública" move.

2. **Quem exatamente fica de fora?**
   Contagem de defeitos mede o trabalho do desenvolvedor. O dano juridicamente relevante é
   o da pessoa excluída, não o do elemento HTML malformado.

3. **Quanto custa chegar até aqui?**
   Para o usuário periférico — plano pré-pago, aparelho de entrada, rede instável —, o peso da
   página é uma barreira que a WCAG não enxerga, porque ela pressupõe um usuário que já chegou.
   O projeto mede esse custo com parâmetros coletados e datados
   ([procedência](docs/metodologia/parametros-de-custo.md)), e reporta honestamente que o
   custo de um acesso isolado é pequeno: a força do argumento está na jornada completa, na
   tentativa frustrada por barreira de acessibilidade — as duas dimensões se agravam
   mutuamente — e no tráfego de terceiros, que o cidadão custeia sem receber serviço em troca.

---

## O que a ferramenta faz

```
┌─ coleta ────────────────────────────────────────────────────────────────┐
│  Playwright (Chromium)  →  DOM renderizado, em 2 perfis de dispositivo  │
│    ├── axe-core 4.13.0     regras determinísticas sobre o DOM estático  │
│    └── 16 sondas próprias  o que exige interação ou contexto de uso     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─ três camadas por achado ───────────────────────────────────────────────┐
│  técnica     rule_id, gravidade, seletor CSS, valores medidos           │
│  normativa   critério WCAG 2.1 violado                                  │
│  jurídica    risco, tese, dispositivos invocáveis, via de exigibilidade │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─ saídas ────────────────────────────────────────────────────────────────┐
│  JSON  artefato primário de pesquisa, reexecutável                      │
│  HTML  relatório acessível e autocontido, para o gestor público         │
│  CSV   dataset em formato longo, para pandas ou Excel                   │
│  API   consumida pelo painel React                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### Em números

| | |
|---|---|
| Critérios WCAG 2.1 modelados | **50** (30 de nível A, 20 de nível AA) |
| Com veredito automático possível | **27** (54%) — limite superior otimista |
| Sondas próprias | **16**, cobrindo 18 critérios + 2 dimensões sem correspondência WCAG |
| Dispositivos normativos registrados | **22** (12 da LBI, 3 constitucionais, 2 da Convenção da ONU) |
| Completude da matriz WCAG↔LBI | **50/50** — verificada em teste automatizado |
| Testes | 115 unitários + 18 de integração + 18 de acessibilidade do próprio painel |

---

## Três decisões que definem o projeto

### 1. Violação e indício nunca se confundem

Vereditos indeterminados (`INCOMPLETE`) jamais viram violação. Sondas declaradas heurísticas
são **impedidas por contrato**, verificado em teste, de reprovar. A diferença entre "detectei
uma falha" e "detectei algo que precisa de olhos humanos" é o que separa uma ferramenta de
auditoria de um gerador de números.

### 2. A cobertura é declarada em toda saída

Todo conjunto de índices carrega o campo `coverage`, e toda tela repete a frase:
**ausência de achado não equivale a conformidade**. A ferramenta estabelece um piso de não
conformidade, nunca um atestado de acessibilidade.

O próprio conjunto de validação mede esse limite: das 20 barreiras plantadas na fixture de
controle positivo, 18 são detectadas e **3 permanecem fora do alcance automático** — porque
exigem julgamento semântico (a cor é o *único* portador do sentido? "Documento1" é um título
*descritivo*?). É evidência empírica, produzida pelo próprio projeto, contra a leitura de
que auditoria automática atesta acessibilidade.

### 3. A ferramenta obedece às regras que aplica

O painel React e o relatório HTML são auditados pelo mesmo axe-core, com o mesmo recorte de
tags, em dois perfis de dispositivo — e a construção falha se houver qualquer violação de
nível A ou AA. Duas correções reais de acessibilidade neste código foram descobertas pela
suíte, não por revisão manual: o alerta de erro roubava o foco do link de salto, e o título
de página fazia o mesmo na carga inicial. Ambas estão documentadas no código onde ocorreram.

---

## Começando

Requisitos: Python 3.11+, Node 18+, Git.

```powershell
# Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e "backend[analysis,dev]"
playwright install chromium

# Conjunto de validação e primeira auditoria
python scripts\servidor_fixtures.py          # em outro terminal
acessisaude varrer fixtures-local

# API e painel
acessisaude servir                            # http://127.0.0.1:8000/docs
cd frontend && npm install && npm run dev     # http://127.0.0.1:5173
```

A varredura contra o conjunto de validação produz um JSON em `data/scans/`, um relatório
HTML em `data/exports/` e um registro no banco SQLite — sem tocar em nenhum servidor público.

### Auditando um portal real

Plataformas em produção nascem **desabilitadas** em
[`backend/src/acessisaude_audit/catalog/targets.yaml`](backend/src/acessisaude_audit/catalog/targets.yaml).
Habilitar uma delas é decisão consciente do pesquisador, que assume respeito ao `robots.txt`,
intervalo mínimo entre requisições e identificação no `User-Agent`. Leia
[a conduta de coleta](docs/metodologia/etica-e-conduta-de-coleta.md) antes.

A ferramenta nunca preenche formulários, nunca autentica e nunca envia dados. Lê o DOM
renderizado de páginas públicas — nada além disso.

---

## Documentação

### Para entender o sistema
- [Visão geral da arquitetura](docs/arquitetura/visao-geral.md)
- [O motor de auditoria](docs/arquitetura/motor-de-auditoria.md)
- [Decisões de arquitetura (ADRs)](docs/adr/)

### Para avaliar o método
- [Protocolo metodológico](docs/metodologia/protocolo.md)
- [Índices: construção e calibração](docs/metodologia/indices.md)
- [Parâmetros de custo: valores, fontes e datas](docs/metodologia/parametros-de-custo.md)
- [Desenho amostral](docs/metodologia/amostragem.md)
- [Limites conhecidos do axe-core](docs/metodologia/limites-do-axe-core.md)
- [Ética e conduta de coleta](docs/metodologia/etica-e-conduta-de-coleta.md)
- [Reprodutibilidade](docs/metodologia/reprodutibilidade.md)

### Para avaliar a fundamentação jurídica
- [Matriz WCAG ↔ LBI](docs/juridico/matriz-wcag-lbi.md)
- [Limites e ressalvas](docs/juridico/limites-e-ressalvas.md)

### Para usar os dados
- [Dicionário de dados](docs/api/dicionario-de-dados.md)
- [Referência da API](docs/api/referencia.md)
- [Instalação e operação](docs/operacao/instalacao-e-uso.md)

### Para escrever o artigo
- [Esqueleto IMRaD](docs/artigo/esqueleto.md)

---

## Estrutura do repositório

```
backend/
  src/acessisaude_audit/
    domain/       normas WCAG, dispositivos legais, matriz, modelos, índices   [puro]
    catalog/      desenho amostral em YAML
    auditor/      Playwright + axe-core + 16 sondas + conduta de coleta
    persistence/  JSON (fonte da verdade) + SQLite (índice de consulta)
    reporting/    relatório HTML acessível, exportações CSV
    analysis/     pandas, estatística não paramétrica, figuras do artigo
    api/          FastAPI
    cli.py        interface principal da coleta
  tests/          unitários e integração contra o conjunto de validação
  vendor/         axe-core 4.13.0 vendorizado (reprodutibilidade)
frontend/         painel React + Vite, auditado por si mesmo
fixtures/         conjunto de validação com barreiras conhecidas + manifesto
docs/             arquitetura, ADRs, metodologia, jurídico, artigo
scripts/          servidor do conjunto de validação
data/             artefatos gerados (não versionado)
```

A direção das dependências é sempre para dentro, em direção a `domain` — e isso é verificado
por análise estática em `tests/unit/test_arquitetura.py`, não apenas prometido em documento.

---

## Publicação associada

**Título do artigo em preparação:** *Auditoria Algorítmica de Acessibilidade em Plataformas
Digitais de Saúde no Rio de Janeiro: Uma Análise Interdisciplinar sob a Ótica da LBI e do
Direito à Saúde.*

O esqueleto IMRaD, com os resultados já mensurados e as lacunas a preencher, está em
[`docs/artigo/esqueleto.md`](docs/artigo/esqueleto.md).

---

## Aviso

Esta ferramenta é instrumento de auditoria técnica e de pesquisa acadêmica. Os relatórios
que produz **não constituem parecer jurídico nem prova pericial**. As proposições jurídicas
apresentadas indicam fundamentos normativos aplicáveis segundo a matriz documentada do
projeto, e sua adequação ao caso concreto depende de análise profissional. Ver
[limites e ressalvas](docs/juridico/limites-e-ressalvas.md).

---

## Licença

AGPL-3.0-or-later. O axe-core, vendorizado em `backend/vendor/`, é da Deque Systems e está
sob Mozilla Public License 2.0.

## Autoria

Thalles Costa — thalles.costa@ioc.fiocruz.br
