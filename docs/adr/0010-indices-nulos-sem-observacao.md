# ADR 0010 — Índices nulos quando não há observação

**Estado:** aceita
**Data:** 31/08/2026

---

## Contexto

O Índice de Conformidade Acessível (ICA) é a razão entre critérios não violados e critérios
avaliados, ponderada por risco jurídico. Quando uma varredura não produz nenhum achado, o
numerador fica cheio e o índice vale 100 — o topo da escala.

Isso é correto para um portal que passou em todas as verificações. É catastrófico para um
portal que nunca respondeu: **uma página que não carregou não produz achado nenhum**.

O defeito apareceu em coleta real. Em **25/08/2026**, uma falha de resolução de nomes na
máquina coletora derrubou as 20 páginas dos cinco alvos com `net::ERR_NAME_NOT_RESOLVED`.
A ferramenta gravou, para todos eles:

```
ICA 100,0   IAN 0,0   IEJ 0,0   barreira absoluta: não
```

Cinco portais de saúde pública, entre os piores da série em todos os outros dias, registrados
como impecáveis no dia em que a rede de quem os auditava caiu. Nenhuma exceção foi levantada:
a taxa de perda de 100% ficou registrada ao lado, num campo que ninguém precisa ler para
enxergar o número grande.

O commit `fb5627d` já havia corrigido a manifestação disso no resumo da integração contínua,
mas registrou explicitamente que a correção no domínio ficava pendente. Esta ADR a executa.

---

## Problema

A ausência de observação estava sendo somada como conformidade. Três propriedades tornam isso
grave num trabalho publicável:

1. **A direção do erro é a pior possível.** Falha de coleta empurra o índice para cima, não
   para baixo. Um erro que degradasse o número seria conservador; este produz elogio.

2. **É indistinguível na saída.** ICA 100 por conformidade e ICA 100 por não observação
   ocupam a mesma célula da tabela, do CSV e do painel. Nenhum leitor consegue separá-los sem
   ir ao campo de taxa de perda — que existe, mas não é o que se lê.

3. **Contamina a série temporal.** Numa auditoria contínua, o valor do método está na
   comparação dia a dia. Um dia falso-perfeito cria uma melhora aparente e depois uma piora
   aparente, ambas artefatos da rede do observador.

Havia ainda a versão sutil do mesmo defeito em granularidade de página: `score_page` recebia a
página como veio e pontuava 100 qualquer página em erro, alimentando `paginas.csv` e os
quadros de análise com linhas falsamente perfeitas.

---

## Decisão

**Os quatro índices agregados passam a aceitar nulo, e nulo significa *sem veredito*.**

`AccessibilityScore` ganha o campo booleano `observed`. Quando ele é falso —
nenhuma página auditada com sucesso — `conformance_index`, `friction_index`,
`legal_exposure_index` e `absolute_barrier` valem `None`.

O acumulador do domínio passa a contar **páginas observadas, e não tentativas**:
`_accumulate` ignora páginas cujo `status` não seja `ok`. Isso corrige a granularidade de
página junto com a de varredura, numa única guarda.

Nulo não é zero, e a distinção é o ponto inteiro da decisão:

| Valor | Significado |
|---|---|
| ICA 100 | Nenhuma violação detectada entre os critérios verificáveis |
| ICA 0 | Todos os critérios verificáveis violados |
| ICA nulo | **Não houve observação. Não é conformidade nem não conformidade.** |

Os campos **descritivos** continuam preenchidos quando não há veredito: cobertura, contagens,
taxa de perda, procedência e o erro de cada página. Sem veredito não é sem registro — a
tentativa fracassada é justamente o que precisa ficar auditável.

---

## Consequências

### Quebra de contrato, assumida

Quatro campos que eram sempre numéricos passam a admitir nulo. Isso atravessa:

- **API** (`ScanSummary`, `Indices`): tipos passam a `float | None` e `bool | None`, com
  `observed` acompanhando. Consumidores que assumiam número recebem `null`.
- **SQL** (`scans`): as colunas correspondentes tornam-se anuláveis, mais a nova coluna
  `observed`.
- **`paginas.csv`**: nova coluna `observado`; os índices ficam **vazios**, não zerados,
  seguindo a regra de que ausência é vazio.
- **Relatório HTML, painel e CLI**: exibem travessão e um aviso `role="alert"` que precede
  qualquer número, porque o leitor precisa dessa informação antes de interpretar a tela.

### `SCHEMA_VERSION` **não** é incrementada

O documento JSON não guarda índices — ele guarda páginas e achados, e os índices são
derivados na leitura (ADR 0003). Nenhum documento gravado muda de forma, e nenhuma coleta
precisa ser refeita. As varreduras já gravadas passam a ser lidas corretamente por
`ScanRepository.reindex()`, que reconstrói o índice relacional a partir do JSON.

É a propriedade da ADR 0003 pagando dividendo: um erro de cálculo descoberto depois da coleta
custou uma reindexação, e não uma recoleta.

### O dia 25/08/2026 passa a ser explicitamente ausência

Na série analisada no artigo, o dia deixa de exibir cinco portais perfeitos e passa a exibir
cinco varreduras sem veredito. É o resultado correto, e é também o resultado que o método
precisa produzir para ser defensável: **uma auditoria contínua tem de saber dizer que não
sabe.**

### `only_audited` permanece

O filtro da camada de análise não foi removido. Ele deixa de ser a única defesa e passa a ser
a segunda, porque quadros montados a partir de coletas antigas, gravadas sob o contrato
anterior, continuam existindo em disco.

---

## Alternativas descartadas

**Zerar os índices sem observação.** Trocaria um veredito falso por outro: cinco portais
perfeitos virariam cinco portais péssimos, com o mesmo problema de fundo — afirmar sobre o que
não foi medido, agora na direção oposta.

**Levantar exceção e não gravar a varredura.** Apagaria a evidência da falha de coleta. A
janela de indisponibilidade é dado do estudo, não lixo: foi ela que permitiu distinguir a
queda de DNS do coletor (todos os alvos, simultânea) das perdas específicas do gov.br
(um alvo, recorrente).

**Corrigir apenas na apresentação.** Foi o que o commit `fb5627d` fez para o resumo da
integração contínua, e por isso o defeito sobreviveu no domínio, no CSV e no painel. Uma
correção de apresentação precisa ser repetida em cada saída nova; uma correção de tipo é
verificada pelo compilador e pelos testes.

---

## Verificação

`tests/unit/test_indices.py::TestAusenciaDeObservacao` fixa o comportamento no domínio,
incluindo a regressão específica (perda total nunca pontua 100) e a fronteira (uma única
página auditada já produz veredito).

`tests/unit/test_persistencia_e_relatorio.py::TestVarreduraSemObservacao` verifica que o nulo
sobrevive às três travessias que importam — índice relacional, CSV e relatório HTML — e que a
reindexação não fabrica veredito.

`tests/unit/test_analise.py::TestExclusaoDePaginasEmErro` cobre a granularidade de página e
fixa que o nulo não é confundido com zero na agregação em pandas.
