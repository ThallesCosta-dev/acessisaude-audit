# AcessiSaúde-Audit — backend

Motor de auditoria, domínio normativo-jurídico, persistência, API e CLI.

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e "backend[analysis,dev]"
playwright install chromium
```

O `playwright install chromium` baixa o navegador (~150 MB). Sem ele, nenhuma
varredura roda — a API sobe, mas `/saude` reporta estado degradado.

## Arquitetura em uma tela

```
domain/        normas WCAG, dispositivos legais, matriz, modelos, índices
               └─ camada PURA: nenhum import de navegador, banco ou HTTP
catalog/       desenho amostral em YAML (targets.yaml)
auditor/       Playwright + axe-core + 13 sondas próprias + conduta de coleta
persistence/   JSON (verdade) + SQLite (índice de consulta)
reporting/     relatório HTML acessível, exportações CSV
analysis/      pandas, estatística, figuras do artigo
api/           FastAPI consumida pelo dashboard React
cli.py         interface principal da coleta
```

A direção das dependências é sempre para dentro, em direção a `domain`. O teste
`tests/unit/test_arquitetura.py` falha se essa regra for quebrada.

## Uso da CLI

```powershell
acessisaude alvos                       # catálogo e estado de habilitação
acessisaude criterios                   # 50 critérios A/AA e risco jurídico
acessisaude matriz                      # integridade da matriz WCAG↔LBI
acessisaude varrer fixtures-local       # auditoria completa
acessisaude relatorio data\scans\x.json # HTML a partir de um JSON coletado
acessisaude exportar                    # CSV de todas as varreduras
acessisaude servir                      # sobe a API em 127.0.0.1:8000
```

Antes de varrer as fixtures, suba o servidor do conjunto de validação:

```powershell
python scripts\servidor_fixtures.py
```

## Conceitos que o código materializa

**Três camadas por achado.** Todo `Finding` carrega simultaneamente a camada
técnica (`rule_id`, `impact`), a normativa (`criteria`) e a jurídica
(`legal_risk`, `legal_thesis`, `legal_provisions`). Nenhuma análise precisa
reconstruir esse vínculo depois.

**Violação ≠ indício.** Vereditos `INCOMPLETE` nunca viram violação. Sondas
declaradas heurísticas são impedidas, por contrato verificado em teste, de
reprovar.

**Cobertura declarada.** `AccessibilityScore.coverage` acompanha todo índice.
Ausência de achado não é conformidade, e o código diz isso em toda saída.

**Conduta de coleta no código, não no manual.** `robots.txt`, intervalo entre
requisições e identificação no User-Agent estão em `auditor/crawler.py`.
Desativar o respeito ao robots exige justificativa registrada, validada em
`config.py`.

**Custo de acesso como barreira.** `probes/digital_rights.py` mede o peso da
página em reais e em fração de franquia mensal — a exclusão econômica que a
WCAG não enxerga.

## Configuração

Variáveis com prefixo `ACESSISAUDE_`, em ambiente ou `.env`. Ver
`src/acessisaude_audit/config.py`: cada campo documenta o que altera e por quê.

Os parâmetros que afetam resultados publicáveis — preço do MB, franquia,
constante de saturação dos índices — viajam no `config_snapshot` de cada
varredura. Nenhum número do artigo circula dissociado das constantes que o
produziram.

## Testes

```powershell
pytest                              # unitários (rápidos)
pytest -m integration               # exige navegador e servidor de fixtures
pytest --cov=acessisaude_audit      # cobertura
```

O conjunto de validação (`fixtures/`) mede sensibilidade e especificidade do
motor. `fixtures/manifest.yaml` declara a verdade de referência.

## Qualidade

```powershell
ruff check backend\src
ruff format --check backend\src
mypy backend\src
```
