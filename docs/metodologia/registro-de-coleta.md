# Registro de coleta de campo — 16/08/2026

> Diário da coleta. Registra o que foi feito, em que ordem, o que falhou e como cada falha foi
> interpretada. Existe porque a auditoria é uma coleta de dados de pesquisa, e o campo precisa
> ter registro — inclusive do que deu errado.
>
> **Todos os horários em UTC.** O relógio local do ambiente de coleta é UTC−3.

---

## 0. Sumário

Quatro medições de cada plataforma entre 00h58 e 01h45 UTC. Dois desfechos principais:

1. **Confiabilidade teste-reteste perfeita.** O índice de conformidade não variou em nenhuma
   plataforma, em nenhuma medição.
2. **Um defeito do instrumento foi detectado e corrigido no meio da coleta.** O perfil desktop
   não se identificava e anunciava `HeadlessChrome`, causando perda de páginas por bloqueio no
   portal federal. O dataset primário passou a ser o das medições posteriores à correção.

> **O que esta coleta NÃO estabelece.** As quatro medições ocorreram em **47 minutos**. Não
> constituem janelas temporais distintas e não permitem separar instabilidade circunstancial de
> crônica, nem detectar mudança nos portais. Uma série temporal genuína — a premissa de
> "auditoria contínua" que o projeto defende — exige coletas separadas por dias ou semanas, e
> permanece pendente.

---

## 1. Conduta aplicada

Parâmetros de execução, todos no padrão do projeto (nenhuma variável de ambiente sobrescreveu
a configuração):

| Parâmetro | Valor |
|---|---|
| Intervalo entre requisições | 2 000 ms |
| Concorrência | 1 página por vez |
| `robots.txt` | respeitado |
| `User-Agent` | identificado, com contato institucional |
| Perfis | `mobile-320` e `desktop-1366` |
| Navegador | Chromium 151.0.7922.34 |
| Motor de regras | axe-core 4.13.0 (vendorizado) |
| Sondas | 16 |
| Autenticação | nenhuma; áreas autenticadas excluídas |
| Formulários | nenhum preenchido ou submetido |

---

## 2. Verificação prévia das URLs

Executada antes de habilitar qualquer alvo, com o mesmo `User-Agent` e o mesmo `RobotsGate` do
motor. Produziu **quatro correções** e **um achado sobre o instrumento**.

### 2.1 `saude.rj.gov.br` era um stub

A raiz servia 935 bytes de HTML com `window.location.replace("https://www.rj.gov.br/saude")` —
e declarava `<html lang="en">`. O portal institucional da SES-RJ migrou; os serviços ao cidadão
(ouvidoria, laudos) permaneceram no subdomínio antigo.

**Ação:** `base_url` reapontado para `www.rj.gov.br/saude`; sementes explícitas em ambos os
hosts, com a mistura declarada no catálogo.

### 2.2 `prefeitura.rio/saude` não é portal de serviços

Título da página: **"Arquivos Saúde"**. É a seção de notícias da Secretaria Municipal. Os
serviços transacionais municipais residem em `carioca.rio`.

**Ação:** categoria corrigida de transacional para informacional; `carioca.rio` acrescentado
como alvo transacional do estrato municipal, sem o qual a comparação entre esferas mediria
coisas diferentes.

### 2.3 URL morta

`prefeitura.rio/saude/clinicas-da-familia/` redirecionava para uma matéria jornalística.
**Ação:** removida.

### 2.4 `subpav.org` mudou de função

Ambas as sementes redirecionavam para `subpav.org/aps/`, hoje descrito como "repositório de
conteúdo técnico" — dirigido a profissionais de saúde, não ao cidadão.

**Ação:** desabilitado, mantido no catálogo com a justificativa. Um canal antes voltado ao
usuário deixou de sê-lo, sem substituto anunciado — informação relevante sobre o ecossistema.

### 2.5 O Meu SUS Digital é uma aplicação de página única

Serve a mesma casca de 1 418 bytes em toda rota, inclusive em `/robots.txt`. Sem renderização
por navegador, a auditoria mediria uma casca vazia.

**Consequência metodológica:** valida a opção do projeto por navegador real em vez de análise
do HTML servido. Uma auditoria por *scraping* estático reportaria zero violações para o
principal serviço digital do SUS.

### 2.6 `robots.txt` por host

| Host | Resultado |
|---|---|
| `meususdigital.saude.gov.br` | Devolve a casca da aplicação, não um arquivo de exclusão |
| `www.gov.br` | Válido, 14 diretivas; permite as sementes |
| `www.rj.gov.br` | Válido: `User-agent: *` / `Disallow:` — permissão irrestrita |
| `saude.rj.gov.br` | HTTP 404, ausente |
| `prefeitura.rio` | Válido; bloqueia apenas `/wp-admin/` |
| `carioca.rio` | Presente e vazio (0 bytes) — sem restrição |

Nenhuma semente foi bloqueada.

---

## 3. Execução

Quatro medições de cada plataforma. As de 01h39 em diante usam o **instrumento corrigido**
(ver § 6.2) e constituem o dataset primário.

| Medição | Instrumento | Horário | Observação |
|---|---|---|---|
| 1ª | com defeito de UA | 00h58 – 01h02 | coleta inicial |
| repetição | com defeito de UA | 01h03 – 01h04 | diagnóstico de falhas de rede |
| 2ª | com defeito de UA | 01h30 – 01h34 | segunda medição |
| **3ª** | **corrigido** | **01h39 – 01h45** | **dataset primário** |

### Índice de conformidade por medição

| Alvo | 1ª | repetição | 2ª | 3ª | Δ |
|---|---|---|---|---|---|
| `conecte-sus-web` | 72,6 | — | 72,6 | 72,6 | **0,0** |
| `gov-br-saude` | 84,9 | 84,9 | 84,9 | 84,9 | **0,0** |
| `ses-rj` | 54,1 | 54,1 | 54,1 | 54,1 | **0,0** |
| `sms-rio` | 61,0 | — | 61,0 | 61,0 | **0,0** |
| `carioca-rio-saude` | 50,7 | — | 50,7 | 50,7 | **0,0** |

O conjunto de critérios violados repetiu-se integralmente em quatro das cinco plataformas; em
`gov-br-saude` variou conforme quais páginas conseguiram carregar.

---

## 4. Diagnóstico das falhas

### 4.1 `gov.br/saúde` — artefato do instrumento

Inicialmente interpretada como falha transitória de rede: `ERR_CONNECTION_RESET`, uma página em
seis, mudando de página entre execuções.

**A interpretação estava errada.** Com o `User-Agent` corrigido, a perda caiu a zero:

| Instrumento | Medições | Perda |
|---|---|---|
| Com `HeadlessChrome` | 3 | 17% · 17% · 33% |
| Com UA identificado | 3 | **0% · 0% · 0%** |

As perdas eram bloqueio da assinatura de automação, não instabilidade do portal.

### 4.2 SES-RJ — instabilidade de infraestrutura

`/laudos` falhou em **8 de 8** tentativas de navegador. Observação direta da disponibilidade:

| Instante | Instrumento | Resultado |
|---|---|---|
| 00h47 | cliente HTTP | HTTP 200 nos três endereços |
| 01h06 | cliente HTTP | **falha nos dois hosts** |
| 01h29 | cliente HTTP | HTTP 200 nos três endereços |
| 01h37 | cliente HTTP **e** navegador | **falha em ambos, simultaneamente** |

**Conclusão:** a infraestrutura oscila em escala de minutos e a falha atinge igualmente
navegador e cliente HTTP simples. Teste direto com dois `User-Agent` distintos confirmou que a
assinatura não influencia o resultado neste host.

> Nenhuma tentativa foi feita de falsear o `User-Agent` para simular navegador comum e testar
> bloqueio. Fazê-lo violaria a regra de identificação declarada na conduta do projeto.

### 4.3 Interpretação para o artigo

A disponibilidade é precondição da acessibilidade. Um serviço de resultado de exame que
responde de forma intermitente não é difícil de usar: para quem tenta no minuto errado, não
existe. Nenhum índice de conformidade WCAG captura isso, e o estudo só o registrou porque o
motor trata falha de carregamento como **dado**, com taxa de perda reportada em toda saída.

---

## 5. Composição final da amostra (dataset primário)

| Alvo | Esfera | Natureza | Págs. válidas |
|---|---|---|---|
| Meu SUS Digital | federal | prontuário, resultado de exame | 2 |
| gov.br/saúde | federal | informacional, transparência | 6 |
| SES-RJ | estadual | ouvidoria, resultado de exame | **2** |
| SMS Rio | municipal | informacional (notícias) | 2 |
| Carioca Digital | municipal | catálogo de serviços | 4 |

**16 auditorias de página válidas** de 20 realizadas.

Lacuna declarada: área autenticada do Meu SUS Digital, que concentra as telas de maior
consequência assistencial.

---

## 6. Dois defeitos do instrumento encontrados pela coleta

### 6.1 Figuras incluíam páginas que não carregaram

Como uma página sem achados tem, por construção, índice de conformidade 100, o estrato estadual
— com 50% de perda — aparecia com mediana 86 na figura contra 58,9 na análise numérica do
mesmo dado.

`score_scan` já excluía páginas em erro ao agregar; as figuras não. Corrigido em
`analysis/figures.only_audited`, com testes em `tests/unit/test_analise.py`.

### 6.2 Perfil desktop não se identificava

O perfil `desktop-1366` não declarava `user_agent` e herdava o padrão do Playwright, que
anuncia `HeadlessChrome`. Consequências: violação da conduta declarada do projeto, confusão
metodológica na comparação entre perfis, e perda de páginas por bloqueio (§ 4.1).

Corrigido; ver [ADR 0008](../adr/0008-user-agent-em-todos-os-perfis.md).

### 6.3 Por que ambos escaparam

Nenhum dos dois podia ser detectado pelo conjunto de validação sintético: fixtures locais nunca
falham ao carregar e nunca bloqueiam por `User-Agent`. Atravessaram a construção do
instrumento, sua validação, mais de 130 testes e duas revisões da documentação de ética.

É o argumento mais direto a favor de **executar a coleta de campo antes de considerar um
instrumento pronto**.

---

## 7. Reprodução

```powershell
# Verificação prévia
acessisaude alvos

# Coleta (conduta padrão; nenhuma variável de ambiente)
acessisaude varrer conecte-sus-web
acessisaude varrer gov-br-saude
acessisaude varrer ses-rj
acessisaude varrer sms-rio
acessisaude varrer carioca-rio-saude

# Exportação e figuras
acessisaude exportar
```

Os JSON de cada varredura estão em `data/scans/`, com `config_snapshot` completo. Portais
mudam: reexecutar verifica o **procedimento**, não reproduz o dado. Para reprocessar o dado
original, use os arquivos arquivados.
