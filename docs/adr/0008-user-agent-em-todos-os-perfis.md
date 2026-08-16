# ADR 0008 — User-Agent explícito em todos os perfis de dispositivo

**Estado:** aceita
**Data:** 16/08/2026

---

## Contexto

O perfil `mobile-320` declarava `user_agent` explícito; o `desktop-1366` não. Sem declaração,
o Playwright usa o padrão do Chromium, que anuncia:

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
HeadlessChrome/151.0.7922.34 Safari/537.36
```

O código compensava com um cabeçalho `X-Audit-Agent` quando não havia UA declarado. A
compensação era insuficiente.

O defeito foi detectado na **segunda medição de campo**, ao investigar por que o perfil desktop
falhava sistematicamente em um host onde o móvel funcionava.

---

## Problema

### 1. Violação da conduta declarada do projeto

`docs/metodologia/etica-e-conduta-de-coleta.md` afirma:

> Auditar sem se identificar seria conduta de coleta inaceitável em pesquisa. Toda requisição
> carrega: `AcessiSaudeAudit/0.1 (+pesquisa academica; contato: ...)`

**Não era verdade para metade das requisições.** O cabeçalho `X-Audit-Agent` não aparece nos
registros de servidor padrão, que gravam o `User-Agent`. Na prática, metade da coleta era
anônima — e a documentação afirmava o contrário.

### 2. Confusão metodológica

`HeadlessChrome` é assinatura de automação bloqueada por muitos firewalls de aplicação. Com um
perfil identificável como robô e outro não, qualquer diferença observada entre perfis passava
a ser **confundida com diferença de bloqueio**, e não de renderização — comprometendo a
hipótese H3 do estudo.

### 3. Perda de dados por artefato do instrumento

Medido diretamente, no portal federal:

| Instrumento | Medições | Perda de páginas |
|---|---|---|
| Com `HeadlessChrome` | 3 | 17% · 17% · 33% |
| Com `User-Agent` identificado | 3 | **0% · 0% · 0%** |

As perdas eram **propriedade do instrumento**, não do portal. Propagá-las aos resultados teria
produzido uma taxa de indisponibilidade inventada para o gov.br.

---

## Decisão

**Todo perfil de dispositivo declara `user_agent` explícito**, sobre o qual o sufixo de
identificação da pesquisa é anexado.

O perfil desktop passa a declarar um Chrome comum de área de trabalho. O ramo de compensação
por cabeçalho permanece no código apenas como rede de segurança, mas agora **emite aviso alto
em log**, para que um perfil personalizado sem UA não passe despercebido.

Quatro testes travam a decisão (`TestCondutaDosPerfisDeDispositivo`):

- todo perfil padrão declara `user_agent`;
- nenhum perfil anuncia automação (`headless` no UA);
- o sufixo de identificação traz endereço de contato;
- os perfis diferem apenas no que devem diferir.

---

## Consequências

**Positivas**

- A conduta declarada passa a ser verdadeira para todas as requisições.
- A comparação entre perfis deixa de ser confundida com bloqueio.
- Perda de páginas volta a significar indisponibilidade do portal.

**Negativas assumidas**

- **Os dados coletados antes de 01h39 UTC de 16/08/2026 têm viés conhecido** no perfil desktop.
  Foram descartados como dataset primário e mantidos apenas como evidência de confiabilidade
  teste-reteste e de disponibilidade. Ver `docs/metodologia/registro-de-coleta.md`.
- O UA declarado precisará ser atualizado periodicamente para não destoar das versões correntes
  do navegador — anotado na cadência de manutenção.

---

## Alternativa descartada

**Manter o `HeadlessChrome` e declarar a limitação.** Descartada porque não é limitação, é
defeito: contradiz uma regra de conduta que o próprio projeto publica, e o custo da correção é
uma linha de configuração.

---

## Nota metodológica

O defeito atravessou a construção inteira do instrumento, a validação contra o conjunto
sintético, 137 testes e duas revisões da documentação de ética — **sem ser detectado**. Só
apareceu quando a coleta de campo produziu falhas assimétricas entre perfis que exigiram
explicação.

É o argumento mais direto a favor de executar a coleta antes de considerar um instrumento
pronto: o conjunto de validação local nunca bloqueia por User-Agent, e portanto nunca poderia
revelar essa classe de defeito.
