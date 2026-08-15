# O motor de auditoria

> Como uma página vira achados. Implementação em
> [`auditor/`](../../backend/src/acessisaude_audit/auditor/).

---

## Composição

```
                       página carregada
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
        axe-core 4.13.0                  16 sondas
   regras determinísticas          interação real, rede,
    sobre o DOM estático            legibilidade, custo
              │                               │
              └───────────────┬───────────────┘
                              ▼
                      Finding[] com três camadas
              técnica · normativa · jurídica
```

Nenhum dos dois decide o que é ilegal. A camada jurídica é anexada por
`domain/mapping.py` no momento da construção do achado, e o motor apenas transporta.

---

## O carregamento

### Contexto isolado por página

Cada página é auditada em um contexto de navegação novo. É decisão **metodológica**, não
técnica: contextos compartilhados acumulam cache e cookies, o que subestimaria o custo de
dados e mascararia banners de consentimento que só aparecem no primeiro acesso.

### Parâmetros fixados

`locale=pt-BR`, `timezone=America/Sao_Paulo`, `color_scheme=light`,
`reduced_motion=no-preference`. O esquema de cores é fixado porque o axe avalia as cores
**computadas**: um esquema indeterminado tornaria o veredito de contraste não reproduzível
entre máquinas.

### Espera pela renderização

```
domcontentloaded  →  networkidle (tolerante a timeout)  →  settle_delay (1500 ms)
```

O `networkidle` é intencionalmente tolerante a falha: portais com polling permanente nunca
ficam ociosos, e esperar até o timeout desperdiça tempo sem melhorar a medição. O
`settle_delay` cobre a hidratação de SPAs — sem ele, aplicações React seriam auditadas antes
de renderizar, e o resultado **subestimaria** as falhas.

### Contabilidade de rede

Handler em `requestfinished` acumulando `request.sizes()` — bytes efetivamente trafegados
(corpo comprimido + cabeçalhos), que é a medida correspondente ao consumo de franquia do
usuário. Recursos servidos do cache não são contabilizados; por isso o contexto é novo.

Domínio registrável aproximado por heurística com correção para sufixos compostos brasileiros
(`gov.br`, `com.br`), suficiente e auditável para um estudo que trabalha majoritariamente com
`.gov.br`.

> **Armadilha registrada.** `NetworkRecorder` **não** usa `slots=True`, ao contrário das
> demais dataclasses do módulo: o Playwright memoiza o handler embrulhado gravando um atributo
> no objeto que o expõe, e com `__slots__` isso levanta `AttributeError` — silenciando o
> registro de tráfego em toda página. O comentário está no código, onde importa.

---

## O axe-core

### Injeção em todos os quadros

Portais públicos embutem mapas, players e formulários de terceiros em `iframe`. Sem injetar em
subquadros, essas regiões ficariam fora da auditoria e o índice sairia otimista.

Quadros cross-origin sem CORS não são inspecionáveis — limitação do navegador, não defeito.
São registrados em log, e a sonda de legendas emite achado `INCOMPLETE` declarando a região
como opaca à auditoria: **declarar o ponto cego é parte do método**.

### Recorte de regras

```python
axe_tags = ("wcag2a", "wcag2aa", "wcag21a", "wcag21aa")
```

`best-practice` é excluído deliberadamente: são recomendações da Deque, não requisitos de
conformidade, e usá-las inflaria a contagem de "violações legais".

### Tradução para o domínio

Regras cujas tags não correspondem a nenhum critério A/AA modelado são **descartadas**: sem
vínculo normativo não há afirmação jurídica possível, e o projeto não reporta o que não
consegue fundamentar.

De cada nó extraem-se os valores medidos das verificações que reprovaram — é o que transforma
"contraste insuficiente" em "2,91:1 onde se exigem 4,5:1, texto `#8a8a8a` sobre `#ffffff`".
A diferença entre uma alegação e uma prova.

### Falha na injeção não vira aprovação

Se o axe não puder ser injetado ou executado, a página é registrada **sem achados do axe** —
nunca com zero violações. "Não medido" não é "conforme".

---

## As sondas

16 sondas, organizadas por classe de barreira. Contrato completo em
[ADR 0004](../adr/0004-sondas-proprias.md); lacunas que motivaram cada uma em
[limites do axe-core](../metodologia/limites-do-axe-core.md).

### Ordem de execução

Estrutura → operabilidade → formulários → dispositivo → mídia → direitos digitais. A ordem
importa apenas para a legibilidade do relatório: as sondas são independentes e nenhuma depende
do resultado de outra.

### A sonda mais elaborada: `probe.focus-visible`

Método em três passos:

1. **Marcar.** JavaScript percorre os elementos focáveis, atribui um índice a cada um e grava
   a assinatura de estilo em repouso (13 propriedades computadas).
2. **Tabular.** Playwright emite pressões **reais** da tecla Tab, através do protocolo do
   navegador. Necessário porque navegadores só aplicam `:focus-visible` quando a modalidade de
   entrada corrente é o teclado — um `element.focus()` programático produziria falso positivo
   em quase toda página moderna.
3. **Comparar.** A cada parada, a assinatura corrente é comparada com a linha de base.

Gradação do veredito, por honestidade sobre o alcance do método:

| Situação | Veredito |
|---|---|
| Sem mudança **e** `outline` explicitamente suprimido | `FAIL` |
| Sem mudança, mas sem supressão explícita | `INCOMPLETE` |

O segundo caso existe porque indicadores desenhados em pseudoelementos `::before`/`::after`
ou em elemento irmão não são captados pela comparação — limitação declarada na docstring da
sonda e no relatório.

Teto: 40 paradas de tabulação, **reportado no achado**, para que a cobertura parcial não seja
lida como cobertura total.

### As duas sondas sem critério WCAG

`probe.data-cost` e `probe.readability` produzem achados com fundamentação jurídica própria,
ancorada no art. 196 da CF/88 e no art. 18, § 4º da LBI. A segunda é declarada **heurística** e
jamais reprova.

---

## Orquestração

### O plano vem antes do navegador

```python
plano = engine.plan(alvo, viewports=...)
# → tarefas conhecidas, total conhecido, lacunas declaradas registradas
```

Materializar o plano antes da execução torna o total conhecido (progresso, estimativa) e,
sobretudo, torna a coleta **reproduzível**: o plano pode ser inspecionado, registrado e
reexecutado.

### Conduta antes de cada requisição

```
robots.txt permite?  →  Crawl-delay do host (se maior que o nosso)  →  intervalo de cortesia
```

Detalhes em [ética e conduta de coleta](../metodologia/etica-e-conduta-de-coleta.md).

### Falhas viram dado

`asyncio.gather(..., return_exceptions=True)`: uma exceção não prevista em uma página é
registrada com traceback completo e vira `PageAudit` com `NAVIGATION_ERROR`. A varredura segue,
o status vira `PARTIAL` e a `loss_rate` aparece em toda saída.

> **Armadilha registrada.** O log usa `logger.error(..., exc_info=excecao)` e **não**
> `logger.exception`: aqui não há exceção ativa — ela foi capturada por `gather` —, e
> `logger.exception` gravaria `NoneType: None` no lugar do traceback, escondendo exatamente o
> defeito que precisa ser diagnosticado. Foi o que aconteceu durante o desenvolvimento, e a
> correção está comentada no código.

---

## O que o motor deliberadamente não faz

| Decisão | Onde mora |
|---|---|
| O que é violação | axe-core e sondas |
| O que é ilegal | `domain/mapping.py` |
| Como pontuar | `domain/scoring.py` |
| O que auditar | `catalog/targets.yaml` |

Essa modéstia é arquitetural. As quatro decisões que o motor não toma são exatamente as que
precisam ser defendidas no artigo — e mantê-las fora do código de coleta permite discuti-las,
testá-las e alterá-las sem tocar no navegador.
