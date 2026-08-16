# Reprodutibilidade

> Um resultado que não pode ser reexecutado não é um resultado.

---

## O que precisa ser fixado

Uma auditoria de acessibilidade tem mais fontes de variação do que parece. Cada uma foi
tratada explicitamente:

| Fonte de variação | Tratamento |
|---|---|
| Versão do motor de regras | axe-core **vendorizado** em versão fixa (4.13.0); versão gravada em cada varredura |
| Versão do navegador | Registrada em `ScanResult.browser` |
| Perfil de dispositivo | Fixado em `DEFAULT_VIEWPORTS`, serializado no `config_snapshot` |
| Locale e fuso horário | `pt-BR` e `America/Sao_Paulo`, fixados no contexto de navegação |
| Esquema de cores | `color_scheme="light"` fixado — o axe avalia cores computadas, e um esquema indeterminado tornaria o veredito de contraste não reproduzível |
| Cache do navegador | Contexto **novo por página**: toda medição é do primeiro acesso |
| Conjunto de páginas | Sementes explícitas no catálogo, não descoberta automática |
| Constantes de índice | `ScoringParameters` serializado no `config_snapshot` |
| Aleatoriedade | Semente única em `Settings.random_seed`, usada em bootstrap e em qualquer amostragem |
| Esquema de dados | `SCHEMA_VERSION`; leitura de versão incompatível falha explicitamente |

---

## O `config_snapshot`

Toda varredura carrega os parâmetros que a produziram:

```json
{
  "browser": "chromium",
  "headless": true,
  "navigation_timeout_ms": 30000,
  "settle_delay_ms": 1500,
  "locale": "pt-BR",
  "timezone_id": "America/Sao_Paulo",
  "max_pages_per_target": 25,
  "request_delay_ms": 2000,
  "concurrency": 1,
  "respect_robots_txt": true,
  "robots_override_reason": "",
  "axe_tags": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
  "viewports": [ ... ],
  "scoring": {
    "friction_kappa": 150.0,
    "critical_path_multiplier": 1.5,
    "price_per_mb_brl": 0.0029296875,
    "franchise_mb": 10240.0,
    "heavy_page_mb": 2.5
  },
  "random_seed": 42,
  "probes": ["probe.page-language", "probe.landmarks", ...],
  "plan": {
    "total_tasks": 10,
    "unique_urls": 5,
    "discover_enabled": false,
    "declared_gaps": [ ... ]
  }
}
```

Deliberadamente **não** inclui caminhos locais nem host/porta da API: não alteram nenhum
número e só poluiriam o dataset com dados do ambiente do pesquisador.

---

## Reexecutar um resultado publicado

```powershell
# 1. Restaurar o commit da coleta
git checkout <hash-do-commit-da-coleta>

# 2. Recriar o ambiente
pip install -e "backend[analysis,dev]"
playwright install chromium

# 3. Conferir a versão do axe vendorizado
#    (deve corresponder ao campo axe_version do JSON)

# 4. Reexecutar
acessisaude varrer <alvo>
```

Portais reais mudam entre coletas — a reexecução verifica o **procedimento**, não reproduz o
dado. Para verificar o dado, use o JSON arquivado:

```powershell
# Reprocessar índices e relatório a partir do dado original
acessisaude relatorio data\scans\<arquivo>.json
acessisaude exportar
```

---

## Reprocessar sem recoletar

Consequência de o JSON ser a fonte da verdade
([ADR 0003](../adr/0003-documento-json-como-fonte-da-verdade.md)):

| Mudança | Exige recoleta? |
|---|---|
| Recalibrar κ | **Não** — reindexar |
| Alterar a matriz jurídica | **Não** — reindexar |
| Alterar a fórmula de um índice | **Não** — reindexar |
| Acrescentar coluna ao índice relacional | **Não** — reindexar |
| Alterar a tradução do axe para o domínio | **Não** — o resultado bruto está no JSON |
| Atualizar o axe-core | **Sim** — o motor produziu o dado |
| Acrescentar sonda | **Sim** — a sonda precisa observar a página |

```python
from acessisaude_audit.persistence import ScanRepository, session_scope
with session_scope(factory) as sessao:
    ScanRepository(sessao).reindex(scan_id)
```

---

## Material suplementar do artigo

Recomenda-se depositar, com DOI (Zenodo ou repositório institucional):

| Artefato | Conteúdo |
|---|---|
| `data/scans/*.json` | Varreduras completas, com evidência e procedência |
| `data/acessisaude.sqlite` | Banco pronto para consulta — arquivo único |
| `data/exports/achados.csv` | Dataset em formato longo |
| `data/exports/paginas.csv` | Uma linha por página × viewport |
| `fixtures/` + `manifest.yaml` | Conjunto de validação e verdade de referência |
| `backend/vendor/axe.min.js` | Motor exato usado |
| Hash do commit | Estado do código na coleta |

Antes de depositar, revisar as capturas em `data/screenshots/` — portais podem exibir dado de
exemplo que pareça real.

---

## O que ainda não é reproduzível

Declarado por honestidade:

1. **O estado dos portais.** Nenhuma auditoria de site em produção reproduz o objeto. Mitigado
   pelo arquivamento do JSON com data e pela proposta de auditoria contínua.
2. **Renderização entre versões de Chromium.** Mudanças no motor de layout podem alterar
   medições de contraste e transbordo. Mitigado pelo registro da versão; não eliminado.
3. **Conteúdo dinâmico e testes A/B.** Portais que servem variantes diferentes produzem
   resultados diferentes na mesma URL. Não há mitigação técnica; cabe declarar como limitação.
4. **Ordem de execução das sondas.** As sondas são independentes, mas `probe.focus-visible`
   pressiona Tab e altera o elemento focado. Sondas posteriores não dependem de foco, o que
   torna o efeito inócuo — mas é uma invariante mantida por convenção, não por verificação.
