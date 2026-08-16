# Registro de coleta de campo — 16/08/2026

> Diário da coleta. Registra o que foi feito, em que ordem, o que falhou e como cada falha foi
> interpretada. Existe porque a auditoria é uma coleta de dados de pesquisa, e o campo precisa
> ter registro — inclusive do que deu errado.

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

| Ordem | Alvo | Início | Situação | Perda |
|---|---|---|---|---|
| 1 | `conecte-sus-web` | 00h58 | concluída | 0% |
| 2 | `gov-br-saude` | 00h59 | parcial | 17% |
| 3 | `ses-rj` | 01h00 | parcial | **50%** |
| 4 | `sms-rio` | 01h00 | concluída | 0% |
| 5 | `carioca-rio-saude` | 01h02 | concluída | 0% |

Repetições de verificação (não integram o dataset): `gov-br-saude` às 01h04 e `ses-rj` às
01h04, ambas destinadas a distinguir falha transitória de sistemática.

---

## 4. Diagnóstico das falhas

### 4.1 `gov.br/saúde` — transitória

`ERR_CONNECTION_RESET`, uma página em seis, em ambas as execuções. **A página afetada mudou**
entre as execuções (`/saude/pt-br` na primeira, `/composicao/saes` na segunda). Falha de rede,
não propriedade de uma página específica.

### 4.2 SES-RJ — instabilidade de infraestrutura

`/laudos` falhou nas **quatro** tentativas (duas execuções × dois perfis), com
`ERR_CONNECTION_CLOSED` e `ERR_SOCKET_NOT_CONNECTED`. Na segunda execução, também
`www.rj.gov.br/saude` falhou nos dois perfis.

**Verificação complementar às 01h06**, com cliente HTTP comum e o mesmo `User-Agent`: três
tentativas em cada host, **todas falharam** — incluindo `www.rj.gov.br/saude`, que respondera
HTTP 200 às 00h47.

**Conclusão:** instabilidade de infraestrutura, não bloqueio a automação. A hipótese de
bloqueio foi descartada porque a falha atinge igualmente um cliente que não executa JavaScript
e não se apresenta como navegador.

> Nenhuma tentativa foi feita de falsear o `User-Agent` para testar bloqueio. Fazê-lo violaria
> a regra de identificação declarada na conduta de coleta do projeto.

### 4.3 Interpretação para o artigo

A disponibilidade é precondição da acessibilidade. Um serviço de resultado de exame que não
responde não é difícil de usar: é indisponível. Nenhum índice de conformidade WCAG captura
isso, e o estudo só o registrou porque o motor trata falha de carregamento como **dado**, com
taxa de perda reportada em toda saída.

---

## 5. Composição final da amostra

| Alvo | Esfera | Natureza | Págs. válidas |
|---|---|---|---|
| Meu SUS Digital | federal | prontuário, resultado de exame | 2 |
| gov.br/saúde | federal | informacional, transparência | 5 |
| SES-RJ | estadual | ouvidoria, resultado de exame | 3 |
| SMS Rio | municipal | informacional (notícias) | 2 |
| Carioca Digital | municipal | catálogo de serviços | 4 |

**16 auditorias de página válidas** de 20 realizadas (perda de 20%).

Lacuna declarada: área autenticada do Meu SUS Digital, que concentra as telas de maior
consequência assistencial.

---

## 6. Defeito do instrumento encontrado durante a análise

A figura de índice por esfera incluía páginas que **não carregaram**. Como uma página sem
achados tem, por construção, índice de conformidade 100, o estrato estadual — com 50% de perda
— aparecia com mediana 86 na figura contra 58,9 na análise numérica do mesmo dado.

`score_scan` já excluía páginas em erro ao agregar; as figuras não. Corrigido em
`analysis/figures.only_audited`, com teste em `tests/unit/test_analise.py` que trava a
propriedade.

O defeito só se manifestou com dados de campo: o conjunto de validação sintético nunca produz
falha de carregamento. É argumento a favor de executar a coleta antes de considerar o
instrumento pronto.

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
