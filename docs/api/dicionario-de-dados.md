# Dicionário de dados

> Documenta os artefatos de dados do projeto: o JSON de varredura (fonte da verdade), as
> tabelas SQL (índice) e os CSV de análise.
>
> Esquema corrente: **1.0.0** (`domain.models.SCHEMA_VERSION`).

---

## 1. `achados.csv` — uma linha por achado

Unidade de análise principal. Codificação **UTF-8 com BOM**, separador **`;`** — o público
inclui gestores públicos que abrirão o arquivo no Excel em configuração regional brasileira.

Listas são serializadas com **`|`**, nunca vírgula (que colidiria com o CSV).

| Coluna | Tipo | Descrição |
|---|---|---|
| `scan_id` | UUID | Identificador da varredura |
| `target_id` | texto | Identificador do alvo no catálogo |
| `target_name` | texto | Nome da plataforma |
| `coletado_em` | ISO 8601 UTC | Início da varredura |
| `pagina_url` | URL | Página em que o achado ocorreu |
| `fluxo_essencial` | 0/1 | Página pertence a fluxo essencial declarado |
| `viewport` | texto | `mobile-320` ou `desktop-1366` |
| `regra_id` | texto | Regra do axe (`color-contrast`) ou sonda (`probe.reflow-320`) |
| `origem` | enum | `axe-core`, `probe`, `heuristic`, `manual` |
| `veredito` | enum | `fail`, `incomplete`, `pass`, `inapplicable` |
| `gravidade_tecnica` | enum | `minor`, `moderate`, `serious`, `critical`; **vazio** se não for `fail` |
| `risco_juridico` | enum | `baixo`, `moderado`, `alto`, `critico` |
| `criterios_wcag` | lista `\|` | Critérios violados, ex. `1.4.3` |
| `criterio_principal` | texto | Primeiro da lista; facilita agregação |
| `principio` | enum | `perceptivel`, `operavel`, `compreensivel`, `robusto` |
| `nivel` | enum | `A` ou `AA` |
| `ocorrencias` | inteiro | Elementos distintos do DOM em falha |
| `grupos_afetados` | lista `\|` | Ver § 4 |
| `dispositivos_normativos` | lista `\|` | Chaves, ex. `lbi.art63.caput` |
| `resumo` | texto | Uma frase: o que está errado |
| `tese_juridica` | texto | Proposição que liga a falha à norma |

### Convenções

**Veredito ≠ violação.** Filtrar por `veredito == 'fail'` para violações confirmadas. Linhas
com `incomplete` são indícios que exigem revisão humana e **nunca** devem ser somadas às
violações.

**`ocorrencias` ≠ número de achados.** Um achado com 400 ocorrências é *um* defeito de
template com 400 manifestações. Reportar as duas grandezas em separado evita o viés de
template — ver [índices](../metodologia/indices.md).

---

## 2. `paginas.csv` — uma linha por página × viewport

| Coluna | Tipo | Descrição |
|---|---|---|
| `scan_id`, `target_id`, `target_name`, `coletado_em` | | Identificação |
| `pagina_url` | URL | URL final, após redirecionamentos |
| `titulo` | texto | `document.title` |
| `idioma_declarado` | texto | Atributo `lang` do `<html>`; **vazio** se ausente |
| `fluxo_essencial` | 0/1 | |
| `viewport` | texto | |
| `situacao` | enum | `ok`, `http_error`, `timeout`, `blocked_by_robots`, `navigation_error` |
| `http_status` | inteiro | **Vazio** se a navegação falhou antes da resposta |
| `observado` | 0/1 | A página foi auditada com sucesso. Quando `0`, as quatro colunas abaixo ficam **vazias** |
| `indice_conformidade` | 0–100 | ICA da página; **vazio** se `observado = 0` |
| `indice_atrito` | 0–100 | IAN da página; **vazio** se `observado = 0` |
| `indice_exposicao_juridica` | 0–100 | IEJ da página; **vazio** se `observado = 0` |
| `barreira_absoluta` | 0/1 | Há violação de risco crítico; **vazio** se `observado = 0` |
| `violacoes` | inteiro | Achados com veredito `fail` |
| `ocorrencias` | inteiro | Elementos em falha |
| `incompletos` | inteiro | Achados pendentes de revisão |
| `criterios_violados` | lista `\|` | |
| `peso_mb` | decimal | Bytes trafegados |
| `requisicoes` | inteiro | |
| `terceiros_pct` | decimal | % do tráfego a domínios de terceiros |
| `custo_brl` | decimal | Sob `price_per_mb_brl` declarado |
| `franquia_pct` | decimal | % da franquia mensal por acesso |
| `lcp_ms` | decimal | Largest Contentful Paint; **vazio** se não medido |
| `duracao_auditoria_ms` | inteiro | Tempo de auditoria da página |

### Ausência é vazio, nunca zero

Regra que atravessa os dois arquivos. `lcp_ms` vazio significa "não medido"; `lcp_ms = 0`
significaria "carregamento instantâneo". Confundi-los inventaria observações e distorceria
qualquer média.

A regra vale com força particular para os índices. Uma página que não carregou não produz
achado nenhum, e um índice de conformidade calculado sobre zero achado vale **100** — o topo
da escala — sem que nada tenha sido verificado. Por isso `observado` existe e por isso as
quatro colunas de índice ficam vazias quando ele é `0`:

| Valor de `indice_conformidade` | Significado |
|---|---|
| `100` | Nenhuma violação detectada entre os critérios verificáveis |
| `0` | Todos os critérios verificáveis violados |
| *(vazio)* | **Não houve observação.** Não é conformidade nem não conformidade |

Ao carregar o arquivo em pandas, as colunas vazias chegam como `NaN`, e as agregações
(`mean`, `median`) as ignoram por padrão — que é o comportamento desejado. **Não aplique
`fillna(0)`**: isso converteria falha de coleta em portal ruim. A decisão está registrada em
[ADR 0010](../adr/0010-indices-nulos-sem-observacao.md), com o caso de campo que a motivou.

---

## 3. Tabelas SQL

Índice achatado do JSON, reconstruível por `ScanRepository.reindex()`.

### `scans`

Uma linha por varredura, com índices pré-calculados: `conformance_index`, `friction_index`,
`legal_exposure_index`, `absolute_barrier`, `coverage`, `mean_page_mb`, `mean_cost_brl`,
`loss_rate`, além de procedência (`engine_version`, `axe_version`, `browser`).

A coluna **`observed`** indica se alguma página foi auditada com sucesso. Quando é falsa, os
quatro índices são **`NULL`** — não zero. Consultas que agregam índices devem filtrar por
`observed = 1` ou confiar em que `AVG`/`MIN`/`MAX` do SQL ignoram `NULL`; `COALESCE(..., 0)`
sobre essas colunas reintroduz o erro que a coluna existe para impedir.

A coluna **`document`** guarda o `ScanResult` completo em JSON — a fonte da verdade.

A coluna **`sphere`** é desnormalizada de propósito: o catálogo é versionado e pode mudar, mas
a análise precisa saber a que esfera o alvo pertencia **quando o dado foi coletado**.

### `findings`

Uma linha por achado, sem os nós de evidência — volumosos, ausentes de qualquer agregação e
disponíveis no documento JSON. Guarda apenas `occurrences`, o que mantém a tabela ágil sem
perder informação analítica.

Índices compostos: `(scan_id, primary_criterion)` e `(outcome, legal_risk)`.

---

## 4. Vocabulários controlados

### `grupos_afetados`

| Valor | Significado |
|---|---|
| `cegueira` | Pessoas cegas, usuárias de leitor de tela |
| `baixa_visao` | Pessoas com baixa visão |
| `visao_de_cores` | Deficiência na visão de cores |
| `surdez` | Pessoas surdas ou com deficiência auditiva |
| `motora` | Deficiência motora; navegação sem mouse |
| `cognitiva_neurodivergencia` | Deficiência intelectual, neurodivergência |
| `fala` | Usuários de comando por voz |
| `fotossensibilidade` | Epilepsia fotossensível |
| `baixa_conectividade` | **Não é deficiência.** O usuário periférico: plano de dados limitado, aparelho antigo, rede instável |

O último está no mesmo vocabulário deliberadamente: o projeto trata exclusão digital e
exclusão por deficiência como barreiras de mesma natureza jurídica, porque ambas obstruem o
acesso ao direito à saúde. Ver
[ADR 0006](../adr/0006-custo-de-dados-como-barreira.md).

### `risco_juridico`

| Valor | Peso | Definição |
|---|---|---|
| `critico` | 12 | Impede acesso a serviço essencial, sem rota alternativa |
| `alto` | 7 | Impede a conclusão da tarefa por grupo identificável |
| `moderado` | 3 | Exige esforço desproporcional ou auxílio de terceiro |
| `baixo` | 1 | Dificulta, mas há rota alternativa |

### `dispositivos_normativos`

Chaves estáveis. Resolução completa (rótulo, citação ABNT, sujeito obrigado, vias de
exigibilidade) na rota `/referencia/dispositivos`.

Exemplos: `lbi.art63.caput`, `lbi.art3.iv.d`, `cf.art196`, `onu.art9`, `dec5296.art47`,
`lai.art8.par3.viii`, `emag.3.1`.

---

## 5. Carregando em pandas

```python
import pandas as pd

achados = pd.read_csv("data/exports/achados.csv", sep=";", encoding="utf-8-sig")
paginas = pd.read_csv("data/exports/paginas.csv", sep=";", encoding="utf-8-sig")

# Ordem natural do risco — permite ordenar e plotar sem reespecificar
achados["risco_juridico"] = pd.Categorical(
    achados["risco_juridico"],
    categories=["baixo", "moderado", "alto", "critico"],
    ordered=True,
)

violacoes = achados[achados["veredito"] == "fail"]
```

Ou, direto do JSON, com metadados do catálogo já anexados:

```python
from acessisaude_audit.analysis import build_findings_frame, load_scans
from acessisaude_audit.catalog.loader import load_catalog
from acessisaude_audit.config import get_settings

s = get_settings()
achados = build_findings_frame(load_scans(s.scans_dir), catalog=load_catalog(s.catalog_path))
```

---

## 6. Evolução do esquema

`SCHEMA_VERSION` é incrementada em toda mudança incompatível, com entrada em `docs/adr/`.

A leitura de um JSON de versão anterior **falha explicitamente**. Leitura tolerante produziria
dados silenciosamente errados — o pior resultado possível em um artefato de pesquisa.
