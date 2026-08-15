# Limites conhecidos do axe-core e o que as sondas próprias cobrem

> Este documento registra **achados metodológicos do próprio projeto**: pontos em que a
> ferramenta de referência da área não cobre o que o escopo declarado exige. Cada um foi
> descoberto pela suíte de validação, não presumido, e cada um motivou uma sonda própria.

---

## Por que o axe-core, e por que ele não basta

O axe-core (Deque Systems, versão 4.13.0 vendorizada) é o motor de regras de acessibilidade
mais usado e mais bem mantido do mercado. Ele é a base determinística deste projeto por três
razões: cobertura ampla das regras verificáveis por inspeção do DOM, taxa de falso positivo
baixíssima por decisão de projeto da Deque, e vocabulário de resultados alinhado ao EARL.

Sua virtude central — só reprovar quando há certeza — é também o que o torna cego a três
classes de barreira que são centrais no recorte deste estudo:

1. **Barreiras que só existem em condição de uso.** Refluxo em 320 px, foco visível,
   armadilha de teclado: exigem *interagir* com a página, não apenas lê-la.
2. **Barreiras de custo.** O peso da página não viola critério WCAG algum, e ainda assim
   exclui materialmente o usuário periférico do serviço de saúde.
3. **Barreiras de compreensão.** Texto oficial em registro jurídico-burocrático passa em
   todos os critérios técnicos e não comunica.

Além dessas, a validação revelou duas divergências específicas, tratadas em detalhe abaixo.

---

## Divergência 1 — `placeholder` aceito como nome acessível

### O achado

A regra `label` do axe-core inclui `non-empty-placeholder` entre as fontes válidas de nome
acessível. Um campo assim **não é reprovado**:

```html
<input type="text" placeholder="Cartão Nacional de Saúde" name="cns">
```

A decisão é defensável do ponto de vista da especificação de nome acessível — o `placeholder`
de fato entra no cálculo. Na prática, produz um ponto cego grave.

### Por que importa

1. **O `placeholder` desaparece ao digitar.** Quem usa leitor de tela e volta ao campo para
   conferir o que preencheu ouve "caixa de edição" e o valor, sem nenhuma pista do que ali
   se pedia. O rótulo existe antes do uso e deixa de existir *durante* o uso — que é
   exatamente quando é necessário.
2. **Seu contraste é tipicamente baixo**, por convenção de estilo, falhando o critério 1.4.3
   justamente para quem mais precisaria dele.
3. **É o padrão mais comum** nos formulários de agendamento e cadastro dos portais públicos
   brasileiros.

Aceitar essa omissão tornaria a auditoria cega precisamente na tela em que o cidadão pede a
consulta.

### Como foi descoberto

A fixture `formulario-sem-rotulos.html` declara `deve_detectar: ["3.3.2"]` no manifesto do
conjunto de validação. O teste de integração falhou: o axe não reportou nada. A investigação
levou à regra `label` e ao check `non-empty-placeholder`.

### Cobertura

`PlaceholderAsLabelProbe` ([`probes/forms.py`](../../backend/src/acessisaude_audit/auditor/probes/forms.py)).

Reprova campos cujo único nome acessível vem de `placeholder` ou de `title`. Campos **sem
nenhuma** fonte de nome ficam fora da sonda: o axe já os reprova, e reportá-los duas vezes
sob identificadores distintos inflaria a contagem de violações.

---

## Divergência 2 — critério 4.1.1 abandonado pela norma, mas não pelo Brasil

### O achado

O critério **4.1.1 (Análise / *Parsing*)** foi **removido na WCAG 2.2**. O axe-core acompanhou
a norma: desde a versão 4.x, a regra `duplicate-id` deixou de integrar os conjuntos `wcag2a`
e `wcag21a` e passou a boa prática (`best-practice`).

Como este projeto exclui `best-practice` do recorte — recomendações sem lastro normativo não
podem sustentar afirmação de violação legal —, o critério ficava sem qualquer verificação.

### Por que importa

A referência normativa deste projeto é a **WCAG 2.1**, e não por conservadorismo: é o que o
Decreto 5.296/2004 e o eMAG 3.1 incorporam na prática administrativa brasileira, e é a versão
para a qual a remissão do art. 63 da LBI às "melhores práticas" aponta no contexto nacional.

Trata-se de um caso em que **a ferramenta de referência e a norma de referência divergem**.
O projeto opta por seguir a norma que rege o objeto auditado. Aceitar a omissão deixaria um
critério do escopo declarado sem verificação, contradizendo a cobertura reportada.

### Cobertura

`DuplicateIdProbe` ([`probes/structure.py`](../../backend/src/acessisaude_audit/auditor/probes/structure.py)),
com gradação por consequência prática:

| Situação | Veredito | Razão |
|---|---|---|
| `id` duplicado **e referenciado** por `label[for]` ou atributo ARIA | `FAIL` | O navegador resolve para o primeiro elemento; o rótulo do segundo campo não existe para a tecnologia assistiva |
| `id` duplicado e **não referenciado** | `INCOMPLETE` | Marcação malformada e risco futuro, mas sem barreira demonstrável no estado atual da página |

A gradação obrigou a corrigir a própria fixture: a duplicação plantada originalmente não era
referenciada, e portanto não produzia barreira. Foi refeita para o padrão realista de
componente repetido em template, em que dois campos apontam `aria-describedby` para o mesmo
`id` duplicado.

---

## O que continua fora do alcance automático

Medido no conjunto de validação: das **20 barreiras** plantadas na fixture de controle
positivo, **18 critérios distintos são detectados**. Três permanecem inalcançáveis, e é
importante que permaneçam:

| Critério | Barreira plantada | Por que exige julgamento humano |
|---|---|---|
| **1.4.1** Uso de cor | Situação da consulta indicada só por um círculo colorido | Exige decidir se a cor é o **único** portador do sentido. Um algoritmo não sabe se o texto adjacente já transmite a informação |
| **2.4.2** Página com título | `<title>Documento1</title>` | O título **existe**. Julgar se é *descritivo* exige entender do que a página trata |
| **2.4.4** Finalidade do link | Quatro links "clique aqui" | Os links **têm** texto acessível. Julgar se ele descreve o destino é semântica, não sintaxe |

Estes três casos são a evidência empírica, produzida pelo próprio projeto, de que **auditoria
automática estabelece um piso de não conformidade e nunca um atestado de acessibilidade**.
O número é citado na seção de Métodos do artigo.

---

## Cobertura das sondas próprias

16 sondas, cobrindo 18 critérios WCAG e 2 dimensões sem correspondência normativa.

| Sonda | Critérios | O que o axe não faz |
|---|---|---|
| `probe.page-language` | 3.1.1 | — (complementa com distinção pt-BR / outro idioma) |
| `probe.landmarks` | 2.4.1, 1.3.1 | Bypass de blocos exige avaliar marco **e** link de salto em conjunto |
| `probe.heading-structure` | 1.3.1, 2.4.6 | Salto de nível é `best-practice` no axe |
| `probe.id-duplicado` | 4.1.1 | Critério removido na WCAG 2.2 — ver divergência 2 |
| `probe.non-interactive-control` | 2.1.1, 4.1.2 | `div[onclick]` sem role não é reprovado por inspeção estática |
| `probe.positive-tabindex` | 2.4.3 | `best-practice` no axe |
| `probe.focus-visible` | 2.4.7 | Exige **tabulação real**: `:focus-visible` só ativa com modalidade de teclado |
| `probe.placeholder-como-rotulo` | 3.3.2 | Ver divergência 1 |
| `probe.erro-sem-mensagem` | 3.3.1 | Exige correlacionar `aria-invalid` com descrição associada |
| `probe.reflow-320` | 1.4.10 | Exige medir a página **renderizada** em 320 px |
| `probe.zoom-lock` | 1.4.4 | Exige interpretar a meta viewport |
| `probe.captions` | 1.2.2, 1.2.3 | — (declara também os players de terceiros como região opaca) |
| `probe.autoplay` | 1.4.2, 2.2.2 | Exige inspecionar estado de mídia em tempo de execução |
| `probe.meta-refresh` | 2.2.1 | — |
| `probe.data-cost` | *(nenhum)* | Dimensão econômica, ausente da WCAG |
| `probe.readability` | *(nenhum)* | Dimensão de compreensão, ausente da WCAG A/AA |

As duas últimas produzem achados com **fundamentação jurídica própria**, declarada em
`legal_thesis_override`, ancorada no art. 196 da CF/88 e no art. 18, § 4º da LBI.

---

## Disciplina de manutenção

Atualizar o axe-core é uma **mudança metodológica**, não uma atualização de dependência.
Entre versões menores, o motor altera limiares, adiciona regras e reclassifica impactos — e
uma variação no índice passaria a refletir mudança no detector, não no portal auditado.

O procedimento obrigatório está em
[`backend/vendor/README.md`](../../backend/vendor/README.md):

1. Registro em `docs/adr/` justificando a troca.
2. Reexecução da suíte contra `fixtures/pages/`, verificando se o golden set ainda produz os
   mesmos vereditos.
3. Reaferição de κ, se o conjunto de achados mudar (ver [índices](indices.md#calibracao)).
4. Nota na seção de Métodos, se a coleta atravessar as duas versões.

A versão do motor fica registrada em cada `ScanResult` (`axe_version`), de modo que qualquer
número publicado seja rastreável até o detector que o produziu.
