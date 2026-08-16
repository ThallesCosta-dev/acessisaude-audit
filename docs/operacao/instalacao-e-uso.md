# Instalação e uso

---

## Requisitos

| | |
|---|---|
| Python | 3.11 ou superior |
| Node.js | 18 ou superior (apenas para o painel) |
| Espaço | ~500 MB (Chromium ocupa a maior parte) |
| Sistema | Windows, Linux ou macOS |

---

## Instalação

```powershell
git clone <repositório>
cd "AcessiSaúde-Audit ..."

python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate

pip install -e "backend[analysis,dev]"
playwright install chromium
```

O extra `analysis` traz pandas, numpy, scipy e matplotlib — necessários apenas para a análise
estatística e as figuras. A coleta funciona sem ele.

### Verificação

```powershell
acessisaude --version
acessisaude matriz          # deve reportar a matriz WCAG↔LBI íntegra
acessisaude criterios       # 50 critérios, 27 automatizáveis
```

---

## Primeira auditoria

Contra o conjunto de validação, sem tocar em nenhum servidor público:

```powershell
# Terminal 1
python scripts\servidor_fixtures.py

# Terminal 2
$env:ACESSISAUDE_REQUEST_DELAY_MS = "0"
$env:ACESSISAUDE_RESPECT_ROBOTS_TXT = "false"
$env:ACESSISAUDE_ROBOTS_OVERRIDE_REASON = "Conjunto de validacao local."
acessisaude varrer fixtures-local
```

Produz:

| Artefato | Local |
|---|---|
| JSON da varredura | `data/scans/fixtures-local__*.json` |
| Relatório HTML | `data/exports/relatorio__fixtures-local__*.html` |
| Registro no banco | `data/acessisaude.sqlite` |
| Capturas de tela | `data/screenshots/` |

---

## Comandos

| Comando | O que faz |
|---|---|
| `acessisaude alvos` | Catálogo e estado de habilitação de cada plataforma |
| `acessisaude criterios` | 50 critérios A/AA com risco jurídico e cobertura |
| `acessisaude matriz` | Verifica a integridade da matriz WCAG↔LBI |
| `acessisaude varrer ALVO` | Executa uma auditoria |
| `acessisaude relatorio ARQUIVO.json` | Gera o HTML a partir de um JSON já coletado |
| `acessisaude exportar` | Exporta CSV de todas as varreduras |
| `acessisaude servir` | Sobe a API em `127.0.0.1:8000` |

Opções úteis de `varrer`:

```powershell
acessisaude varrer sms-rio --viewport mobile-320    # um perfil só
acessisaude varrer sms-rio --sem-relatorio          # não gera HTML
acessisaude varrer sms-rio --sem-persistir          # não grava no banco
acessisaude -v varrer sms-rio                       # log em DEBUG
acessisaude --json-log varrer sms-rio               # log em JSONL, para CI
```

---

## Painel

```powershell
# Terminal 1
acessisaude servir              # http://127.0.0.1:8000/docs

# Terminal 2
cd frontend
npm install
npm run dev                     # http://127.0.0.1:5173
```

---

## Configuração

Variáveis de ambiente com prefixo `ACESSISAUDE_`, ou arquivo `.env` na raiz.

### Conduta de coleta

| Variável | Padrão | Efeito |
|---|---|---|
| `REQUEST_DELAY_MS` | `2000` | Intervalo mínimo entre requisições ao mesmo host |
| `CONCURRENCY` | `1` | Páginas em paralelo |
| `RESPECT_ROBOTS_TXT` | `true` | Desativar **exige** `ROBOTS_OVERRIDE_REASON` |
| `MAX_PAGES_PER_TARGET` | `25` | Teto de páginas por plataforma |
| `USER_AGENT_SUFFIX` | identificação da pesquisa | Anexado ao User-Agent |

### Navegador

| Variável | Padrão |
|---|---|
| `BROWSER` | `chromium` |
| `HEADLESS` | `true` |
| `NAVIGATION_TIMEOUT_MS` | `30000` |
| `SETTLE_DELAY_MS` | `1500` — espera pela hidratação de SPAs |
| `CAPTURE_SCREENSHOTS` | `true` |

### Índices — **afetam resultados publicáveis**

| Variável | Padrão | Observação |
|---|---|---|
| `FRICTION_KAPPA` | `150.0` | Calibrado empiricamente; alterar exige recalibração documentada |
| `CRITICAL_PATH_MULTIPLIER` | `1.5` | |
| `PRICE_PER_MB_BRL` | `0.0029296875` | R$ 3,00/GiB — Claro Prezão R$ 15,00/5 GB/15 dias, 10/08/2026 |
| `FRANCHISE_MB` | `10240.0` | 10 GiB/mês — duas recargas do plano de referência |
| `HEAVY_PAGE_MB` | `2.5` | Peso mediano móvel, HTTP Archive Web Almanac 2025 |

Todos viajam no `config_snapshot` de cada varredura. Procedência dos três últimos em
[parâmetros de custo](../metodologia/parametros-de-custo.md); reavaliá-los é decisão
metodológica, com registro em ADR.

---

## Auditando um portal real

1. **Conferir a URL** no catálogo — endereços de portais públicos mudam.
2. **Ler o `robots.txt`** do host.
3. **Preencher `collection_window`** no catálogo.
4. **Reconferir os parâmetros de custo** na data da coleta: preço e franquia da oferta
   pré-paga de entrada mudam com frequência. Ver
   [parâmetros de custo](../metodologia/parametros-de-custo.md) para o procedimento e a
   cadência de reavaliação.
5. **Habilitar o alvo** (`enabled: true` em `targets.yaml`) — decisão consciente, registrada
   em commit.
6. **Executar fora do horário de pico** do serviço.

Leia [ética e conduta de coleta](../metodologia/etica-e-conduta-de-coleta.md) antes.

---

## Análise

```python
from pathlib import Path
from acessisaude_audit.analysis import (
    build_findings_frame, build_pages_frame, criterion_prevalence,
    compare_groups, load_scans, save_all,
)
from acessisaude_audit.catalog.loader import load_catalog
from acessisaude_audit.config import get_settings

s = get_settings()
varreduras = load_scans(s.scans_dir)
catalogo = load_catalog(s.catalog_path)

achados = build_findings_frame(varreduras, catalog=catalogo)
paginas = build_pages_frame(varreduras, catalog=catalogo)

# Quais barreiras são estruturais no ecossistema
print(criterion_prevalence(achados).head(15))

# Comparação entre esferas, com advertência metodológica anexada
grupos = {e: g["ica"].tolist() for e, g in paginas.groupby("esfera", observed=True)}
print(compare_groups(grupos, unit="pagina").report())

# Figuras do artigo
save_all(achados, paginas, Path("docs/artigo/figuras"))
```

---

## Testes

```powershell
cd backend
pytest tests/unit              # 115 testes, ~2 s
pytest tests/integration       # 18 testes; exige Chromium e servidor de fixtures
pytest --cov=acessisaude_audit

cd ..\frontend
npm run typecheck
npm run test:a11y              # auditoria do próprio painel
```

Para incluir a tela de detalhe na auditoria do painel:

```powershell
$env:ROTA_VARREDURA = "/varreduras/<id-de-uma-varredura>"
npm run test:a11y
```

---

## Solução de problemas

**`axe.min.js não encontrado`** — rode `npm pack axe-core` em `backend/vendor/` conforme
`backend/vendor/README.md`. A rota `/saude` reporta o estado.

**`Executable doesn't exist` (Playwright)** — falta `playwright install chromium`.

**Varredura sem achados em portal que claramente tem problemas** — provavelmente SPA que não
terminou de hidratar. Aumente `ACESSISAUDE_SETTLE_DELAY_MS`.

**`respect_robots_txt=False exige ...`** — comportamento intencional: desativar a checagem
exige justificativa registrada, que fica gravada no dataset.

**Alvo desabilitado** — comportamento intencional. Ver § "Auditando um portal real".

**Peso da página medido muito abaixo do esperado** — verifique se o servidor de fixtures está
gerando os recursos sintéticos. O Chromium cancela o download de recursos declarados como
imagem cujo conteúdo não seja imagem válida.
