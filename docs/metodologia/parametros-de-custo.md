# Parâmetros de custo de acesso: valores, fontes e datas

> Este documento existe porque um número monetário sem procedência é pior que
> nenhum número. Ele registra a origem de cada constante que converte peso de
> página em custo para o usuário, e é a referência a ser citada na seção de
> Métodos do artigo.
>
> **Data de coleta dos parâmetros: 15 de agosto de 2026.**

---

## 1. Resumo dos valores adotados

| Parâmetro | Valor | Origem |
|---|---|---|
| `price_per_mb_brl` | **0,0029296875** (R$ 3,00/GiB) | Claro Prezão R$ 15,00 / 5 GB / 15 dias, consulta em 10/08/2026 |
| `franchise_mb` | **10 240** MiB (10 GiB/mês) | Duas recargas do mesmo plano no ciclo de 30 dias |
| `heavy_page_mb` | **2,5** MiB | Peso mediano de página móvel, HTTP Archive Web Almanac 2025 (coleta de julho de 2025) |

Nenhum dos três é estimativa. Todos são valores publicados, datados e
verificáveis.

---

## 2. Preço do dado móvel

### 2.1 Plano de referência

**Claro Prezão — R$ 15,00, 5 GB, 15 dias.** É o pacote pré-pago de entrada mais
barato do mercado brasileiro na data de consulta. A tabela completa da oferta:

| Recarga | Franquia | Validade | R$/GB |
|---|---|---|---|
| **R$ 15,00** | **5 GB** | **15 dias** | **3,00** |
| R$ 20,00 | 10 GB | 20 dias | 2,00 |
| R$ 25,00 | 12 GB | 25 dias | 2,08 |
| R$ 30,00 | 15 GB | 30 dias | 2,00 |

Fonte: comparador Minha Conexão, página de planos pré-pagos da Claro, conteúdo
atualizado em 10/08/2026.

### 2.2 Por que a recarga de R$ 15,00, e não a de R$ 30,00

Porque é a que o usuário periférico efetivamente compra. Quem não consegue
comprometer R$ 30,00 de uma vez recarrega R$ 15,00 duas vezes — e paga
**R$ 3,00 por GB em vez de R$ 2,00**.

> **Achado a explorar no artigo: a penalidade da pobreza no dado móvel.**
> A mesma operadora, no mesmo mês, cobra 50% a mais por gigabyte de quem
> fraciona a recarga. O fracionamento não é escolha de conveniência: é
> consequência direta da restrição de fluxo de caixa. O usuário mais pobre paga
> mais caro pelo mesmo bem, e paga mais caro **exatamente por ser mais pobre**.
> É o mecanismo que Caplovitz descreveu em 1963 — *the poor pay more* —
> reproduzido na infraestrutura de acesso ao serviço público digital de saúde.

### 2.3 Conversão

O projeto mede tráfego em **mebibytes** (MiB, base 1024), porque é a unidade em
que o navegador reporta bytes transferidos. As operadoras anunciam "GB" sem
especificar a base; adota-se a leitura conservadora de que "5 GB" significa
5 GiB.

```
R$ 15,00 ÷ 5 GiB          = R$ 3,00 por GiB
R$ 3,00 ÷ 1024 MiB        = R$ 0,0029296875 por MiB
```

O valor é **exatamente representável em ponto flutuante binário** (3/1024 é uma
fração diádica), o que elimina erro de arredondamento acumulado ao somar
milhares de páginas.

### 2.4 Corroboração oficial: Anatel

| Indicador | 1T2026 | 1T2025 | Variação |
|---|---|---|---|
| Preço médio por GB | **R$ 5,46** | R$ 6,13 | −10,93% |
| Consumo médio por usuário | **6,51 GB/mês** | 5,37 GB/mês | +21,23% |
| ARPU pré-pago | **R$ 12,12/mês** | — | — |
| ARPU pós-pago | R$ 49,81/mês | — | — |

Fonte: ANATEL. *Panorama Econômico-Financeiro do Setor de Telecomunicações*,
1º trimestre de 2026.

**Duas leituras importantes.**

O preço médio da Anatel (R$ 5,46/GB) é **82% superior** ao valor adotado
(R$ 3,00/GB). A diferença não é contradição: a Anatel computa receita total
dividida por dado efetivamente consumido, e os usuários não consomem a franquia
inteira — o preço *efetivo* por GB usado é maior que o preço *anunciado* por GB
de franquia. Para estimar o custo de carregar uma página, a taxa marginal
anunciada é a métrica correta.

A consequência metodológica é que **a estimativa deste projeto é conservadora**:
adota-se a menor das duas taxas defensáveis, de modo que o custo reportado erra
para menos, nunca para mais. Uma auditoria que quisesse exagerar o problema
usaria o número da Anatel.

---

## 3. Franquia de referência

**10 240 MiB (10 GiB) por mês**, correspondente a duas recargas de R$ 15,00 no
ciclo de 30 dias.

### Também conservador

A Anatel reporta ARPU pré-pago de **R$ 12,12 por mês** — menos da metade dos
R$ 30,00 pressupostos aqui, e esse valor ainda inclui voz e SMS, não apenas
dados. O usuário pré-pago médio, portanto, dispõe de franquia **substancialmente
menor** que a de referência.

A escolha de uma franquia maior que a média real desloca a estimativa na direção
segura: os percentuais de consumo reportados pelo projeto são **pisos**. Um
usuário com 5 GiB mensais sofre o dobro do impacto percentual calculado aqui.

### O que a franquia de referência não captura

Uma parcela relevante da população não tem franquia alguma em sentido próprio:
depende de aplicativos com **tráfego zero-rated**. A oferta consultada é
explícita — "WhatsApp e Claro Música sem descontar do pacote de dados".

> **Segundo achado a explorar no artigo: a assimetria do zero-rating.**
> O aplicativo de mensagens privado não consome franquia; o portal público de
> saúde consome. Para o usuário na faixa de menor renda, o Estado é o único
> serviço que cobra pelo acesso. A prática, autorizada no arcabouço regulatório
> brasileiro de neutralidade de rede, produz o efeito de **desvantagem econômica
> do serviço público frente ao privado** — e sugere que a via de correção não é
> apenas técnica (reduzir o peso das páginas), mas também regulatória (incluir
> serviços públicos essenciais no tráfego não tarifado).

---

## 4. Limiar de página onerosa

**2,5 MiB.** Peso mediano de uma página inicial em dispositivo móvel:

| Percentil | Peso |
|---|---|
| Mediana | **2 559 KiB** (≈ 2,50 MiB) |
| Percentil 90 | 8 337 KiB (≈ 8,14 MiB) |

Fonte: HTTP ARCHIVE. *Web Almanac 2025 — Page Weight*. Coleta de julho de 2025.
A mediana cresceu 8,4% em relação a 2024 (2,4 MB) e 202,8% em relação a 2015
(845 KB).

### Por que a mediana, e não um ideal de engenharia

A escolha é **descritiva, não normativa**, e isso é deliberado. Um limiar
derivado de boas práticas de desempenho (por exemplo, 500 KB) seria facilmente
descartado como perfeccionismo por um gestor público.

A mediana da web comercial — notoriamente inchada, e crescendo — é uma régua que
não admite essa objeção: uma página de serviço público de saúde acima dela é
pesada **mesmo pelo padrão daquilo que se critica**.

---

## 5. Efeito da correção sobre os valores anteriores

Os valores anteriores eram declaradamente ilustrativos. A substituição os altera
em ordens de grandeza:

| Parâmetro | Antes (ilustrativo) | Agora (coletado) | Razão |
|---|---|---|---|
| Preço por MiB | R$ 0,10 | R$ 0,0029296875 | **34× menor** |
| Franquia | 2 048 MiB | 10 240 MiB | 5× maior |
| Limiar de peso | 2,0 MiB | 2,5 MiB | 1,25× maior |

O preço ilustrativo superestimava o custo em **trinta e quatro vezes**. Uma
página de 3 MiB aparecia como custando R$ 0,30 por acesso; custa, de fato,
R$ 0,0088.

### Consequência honesta para o argumento

**O custo monetário de um acesso isolado é pequeno, e o artigo precisa dizer
isso.** Inflá-lo seria fabricar evidência.

A força do argumento econômico está em outros três lugares, todos mensurados
pelo projeto:

1. **A jornada completa.** Acompanhar um agendamento ou um resultado de exame
   não é ato único. O achado da sonda reporta o consumo em quatro acessos
   mensais, frequência mínima plausível.
2. **A tentativa frustrada.** Cada falha de acessibilidade que obriga a repetir
   o fluxo soma-se à conta. As duas dimensões auditadas pelo projeto — barreira
   sensorial e barreira econômica — **agravam-se mutuamente**, e essa interação
   é a contribuição original da medida.
3. **O tráfego de terceiros.** A parcela que não presta serviço algum ao usuário
   é onde há transferência de custo sem contrapartida — e é a métrica com
   fundamento jurídico mais direto.

A apresentação foi ajustada para não colapsar a grandeza: valores abaixo de
R$ 0,01 são exibidos em centavos ("0,9 centavo por acesso"), e o dado é
persistido com seis casas decimais para que a agregação não perca precisão.

---

## 6. Quando reavaliar

| Parâmetro | Cadência | Gatilho |
|---|---|---|
| Preço e franquia | Trimestral | Publicação do *Panorama* da Anatel; mudança na oferta de entrada das operadoras |
| Limiar de peso | Anual | Publicação do *Web Almanac* |

Toda alteração exige registro em `docs/adr/` e **declaração de descontinuidade**
em qualquer série temporal que atravesse a mudança. Como os parâmetros viajam no
`config_snapshot` de cada varredura, dados já coletados permanecem
reinterpretáveis: basta reindexar
([ADR 0003](../adr/0003-documento-json-como-fonte-da-verdade.md)).

---

## 7. Referências

ANATEL. **Panorama Econômico-Financeiro do Setor de Telecomunicações**:
1º trimestre de 2026. Brasília, DF: Agência Nacional de Telecomunicações, 2026.

CAPLOVITZ, David. **The Poor Pay More**: consumer practices of low-income
families. New York: Free Press, 1963.

HTTP ARCHIVE. **Web Almanac 2025**: Page Weight. Disponível em:
https://almanac.httparchive.org/en/2025/page-weight. Coleta de julho de 2025.

MINHA CONEXÃO. **Claro Pré-Pago 2026**: planos e preços. Disponível em:
https://www.minhaconexao.com.br/planos/claro/planos-claro/claro-pre-pago.
Conteúdo atualizado em 10 ago. 2026. Acesso em: 15 ago. 2026.

TELETIME. **Preço médio do GB na telefonia móvel diminui no primeiro
trimestre**. 3 jul. 2026. Disponível em:
https://teletime.com.br/03/07/2026/preco-medio-gb-telefonia-movel-diminui/.
Acesso em: 15 ago. 2026.

> **Nota para a redação final do artigo.** Os dados da Anatel foram obtidos por
> intermédio de veículo especializado. Antes da submissão, substituir a citação
> pelo relatório primário, disponível no portal de dados abertos da Agência, e
> conferir os valores na fonte oficial. Do mesmo modo, os preços das operadoras
> devem ser reconferidos diretamente nos sítios oficiais na data da coleta de
> campo, com captura de tela arquivada como evidência.
