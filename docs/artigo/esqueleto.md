# Esqueleto do artigo (IMRaD)

**Título:** Auditoria Algorítmica de Acessibilidade em Plataformas Digitais de Saúde no Rio
de Janeiro: Uma Análise Interdisciplinar sob a Ótica da LBI e do Direito à Saúde

**Estado:** **coleta de campo executada em 16/08/2026.** Métodos, validação do instrumento e
Resultados sustentados por dados medidos. Falta a redação discursiva de Introdução, Discussão
e Conclusão.

Legenda: ✅ dado medido · ✍️ redação a fazer · ⬜ pendente

---

## Resumo

✍️ Escrever por último. Números já disponíveis (250 palavras):

> **Objetivo.** Avaliar a conformidade de plataformas digitais de saúde pública com incidência
> no Rio de Janeiro à WCAG 2.1 (níveis A e AA) e qualificar juridicamente as barreiras
> encontradas à luz da Lei 13.146/2015. **Métodos.** Auditoria algorítmica de **cinco
> plataformas** estratificadas por esfera federativa, em dois perfis de dispositivo, com
> instrumento validado contra conjunto de referência (nenhum falso positivo; 18 de 20
> critérios plantados detectados). Coleta em 16/08/2026. **Resultados.** Foram realizadas 20
> auditorias de página, 16 bem-sucedidas (perda de 20%), com 126 violações confirmadas.
> Mediana do índice de conformidade: **69,2** (IC 95%: 61,0–84,9). **Todas as cinco
> plataformas apresentaram barreira absoluta** — violação de risco jurídico crítico, sem rota
> alternativa. O critério 4.1.2 (Nome, função, valor) foi violado em **100% das páginas
> auditadas**. Observou-se gradiente por esfera federativa (Kruskal-Wallis, p = 0,007;
> ε² = 0,61): mediana de 87,0 no âmbito federal contra 58,9 no estadual e 61,0 no municipal.
> **Conclusões.** ✍️

**Palavras-chave:** acessibilidade digital; saúde digital; Lei Brasileira de Inclusão;
auditoria algorítmica; direito à saúde; exclusão digital.

---

## 1. Introdução

### 1.1 O deslocamento do acesso ✍️

Quando um serviço público de saúde migra para o meio digital, a acessibilidade da interface
deixa de ser questão de usabilidade e passa a ser **condição de exercício de um direito**. Se
o botão de confirmar consulta não recebe foco do teclado, a pessoa com deficiência motora não
tem uma experiência ruim: não tem consulta.

Argumentar que o art. 196 da CF/88 — acesso universal e igualitário — se aplica ao canal
digital com a mesma força com que se aplica à rampa da unidade de saúde.

### 1.2 Lacuna na literatura ✍️

Revisar e posicionar:

- **Estudos de conformidade WCAG em portais brasileiros** — em geral descritivos, contam
  violações sem qualificação jurídica e sem declarar cobertura.
- **Literatura jurídica sobre a LBI** — analisa o art. 63 doutrinariamente, sem instrumento
  de mensuração.
- **Literatura de saúde digital** — trata de adoção e usabilidade, raramente de acessibilidade
  como condição de acesso.

**A lacuna:** não há instrumento que produza, do mesmo dado, a afirmação técnica e a
proposição jurídica correspondente, com procedência auditável.

### 1.3 O usuário periférico ✍️

Fundamentar a categoria: a barreira de acesso ao serviço público de saúde não é apenas
sensorial. Plano pré-pago, aparelho de entrada, rede instável e escolaridade heterogênea
produzem exclusão com o mesmo efeito jurídico — obstrução do acesso ao direito.

Dados a levantar: penetração de planos pré-pagos, franquia média, perfil de dispositivo da
população SUS-dependente (TIC Domicílios / CETIC.br).

### 1.4 Objetivos ✍️

**Geral.** Desenvolver e aplicar instrumento de auditoria contínua que converta falhas
técnicas de acessibilidade em proposições jurídicas fundamentadas.

**Específicos.**
1. Modelar a correspondência entre os 50 critérios WCAG 2.1 A/AA e o ordenamento brasileiro.
2. Construir e validar o instrumento contra conjunto de referência.
3. Aplicá-lo a plataformas de saúde do RJ, estratificadas por esfera.
4. Quantificar o custo de acesso em dados móveis como barreira.
5. Caracterizar o perfil de exclusão por grupo afetado.

---

## 2. Métodos

> Base pronta: [`docs/metodologia/protocolo.md`](../metodologia/protocolo.md)

### 2.1 Desenho ✅

Observacional, transversal, de auditoria algorítmica, estratificado por esfera federativa.
Unidade de observação: página × perfil de dispositivo.

### 2.2 A matriz WCAG ↔ LBI ✅

**Contribuição central. Descrever em detalhe.**

- Três camadas cumulativas: geral, de saúde, específica.
- O art. 63 da LBI como norma em branco que incorpora a WCAG por remissão, via eMAG 3.1 e art.
  47 do Decreto 5.296/2004.
- Gradação de risco jurídico por três vetores: essencialidade, rota alternativa,
  reversibilidade.

**Números medidos:** 50 mapeamentos; 22 dispositivos normativos (12 da LBI, 3 constitucionais,
2 da Convenção da ONU com status de emenda constitucional); distribuição de risco: 4 críticos,
18 altos, 19 moderados, 9 baixos.

Base: [`docs/juridico/matriz-wcag-lbi.md`](../juridico/matriz-wcag-lbi.md)

### 2.3 Instrumento ✅

Chromium via Playwright; axe-core 4.13.0 vendorizado; 16 sondas próprias. Recorte de regras
restrito a `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa` — `best-practice` excluído porque
recomendações sem lastro normativo não sustentam afirmação de violação legal.

**Justificar as sondas próprias** — quatro classes de lacuna, em
[`docs/metodologia/limites-do-axe-core.md`](../metodologia/limites-do-axe-core.md).

Dois achados metodológicos merecem parágrafo próprio no artigo:

1. **O axe-core aceita `placeholder` como nome acessível** (regra `label`, check
   `non-empty-placeholder`). Como esse é o padrão mais comum nos formulários de agendamento
   dos portais públicos brasileiros, a omissão tornaria a auditoria cega na tela que mais
   importa.
2. **O critério 4.1.1 foi removido na WCAG 2.2 e o axe-core acompanhou a norma**, enquanto a
   referência normativa brasileira permanece na 2.1. Caso em que a ferramenta de referência e
   a norma de referência divergem, e o projeto opta por seguir a norma que rege o objeto.

### 2.4 Índices ✅

ICA, IAN, IEJ e o sinalizador de barreira absoluta. Apresentar as fórmulas, justificar o
amortecimento logarítmico (viés de template), a saturação exponencial e a ponderação por
risco jurídico em vez de gravidade técnica.

**Incluir a calibração de κ como resultado metodológico** — ver § 3.1.

Base: [`docs/metodologia/indices.md`](../metodologia/indices.md)

### 2.5 Validação do instrumento ✅

Conjunto de referência com cinco páginas sintéticas e verdade declarada em manifesto
versionado. Caso-controle negativo (página conforme) e positivo (20 barreiras plantadas, cada
uma anotada com o critério que deve ser detectado).

### 2.6 Ética ✅

A ferramenta lê o DOM renderizado de páginas públicas: não preenche formulário, não autentica,
não envia dados. `robots.txt` respeitado; 2000 ms entre requisições; identificação no
`User-Agent`. **Áreas autenticadas excluídas e reportadas como lacunas declaradas** — as telas
de maior risco assistencial ficam de fora, e os índices podem estar otimistas.

Base: [`docs/metodologia/etica-e-conduta-de-coleta.md`](../metodologia/etica-e-conduta-de-coleta.md)

### 2.7 Análise estatística ✅

Não paramétrica (Mann-Whitney, Kruskal-Wallis), com tamanho de efeito sempre reportado (δ de
Cliff, ε²) e intervalos por bootstrap com semente fixa. **Declarar a pseudorreplicação:**
páginas do mesmo portal não são independentes; comparações entre esferas reportadas também em
nível de portal.

### 2.8 Reprodutibilidade ✅

`config_snapshot` completo em cada varredura; axe-core em versão fixa; catálogo versionado;
material suplementar depositado com DOI.

---

## 3. Resultados

### 3.1 Validação do instrumento ✅ — **já mensurado**

| Métrica | Resultado |
|---|---|
| Especificidade (falsos positivos na página conforme) | **0** |
| Sensibilidade (critérios distintos detectados / plantados) | **18 / 20** |
| Cobertura declarada (critérios com veredito automático possível) | **27 / 50 (54%)** |

**As três barreiras fora do alcance automático** — e por que permanecem assim:

| Critério | Barreira plantada | Julgamento exigido |
|---|---|---|
| 1.4.1 Uso de cor | Situação da consulta indicada só por círculo colorido | A cor é o **único** portador do sentido? |
| 2.4.2 Página com título | `<title>Documento1</title>` | O título existe. É **descritivo**? |
| 2.4.4 Finalidade do link | Quatro links "clique aqui" | O texto existe. **Descreve o destino**? |

> Este é um resultado, não uma limitação envergonhada. É evidência empírica, produzida pelo
> próprio instrumento, de que auditoria automática estabelece um **piso de não conformidade**
> e nunca um atestado de acessibilidade — afirmação que a literatura da área frequentemente
> não faz com esse grau de precisão.

**Calibração do índice de atrito.** O parâmetro de saturação inicialmente estimado (κ = 40)
foi rejeitado pela aferição: com ele, quatro das cinco páginas do conjunto de referência
marcavam acima de 98 e uma única falha séria já pontuava 65 — o índice não distinguia "ruim"
de "inutilizável". A recalibração empírica (κ = 150) restaurou a discriminação na faixa de
interesse. Ver [ADR 0007](../adr/0007-calibracao-empirica-de-kappa.md).

### 3.2 Caracterização da amostra ✅

Coleta em **16/08/2026**, janela única. Cinco plataformas, 20 auditorias de página
(5 URLs × 2 perfis, mais as sementes adicionais), 16 bem-sucedidas.

| Plataforma | Esfera | Serviço | Págs. | Perda | ICA | IAN | IEJ | Viol. | Ocorr. | Peso méd. |
|---|---|---|---|---|---|---|---|---|---|---|
| Meu SUS Digital | federal | prontuário | 2 | 0% | 72,6 | 99,9 | 58,7 | 13 | 37 | **7,17 MB** |
| gov.br/saúde | federal | informacional | 6 | 17% | **84,9** | 66,4 | 14,1 | 12 | 17 | 2,74 MB |
| SES-RJ | estadual | ouvidoria, exames | 6 | **50%** | 54,1 | 99,8 | 63,7 | 31 | 75 | 2,22 MB |
| SMS Rio (notícias) | municipal | informacional | 2 | 0% | 61,0 | 100,0 | 80,9 | 24 | 86 | 2,10 MB |
| Carioca Digital | municipal | serviços | 4 | 0% | **50,7** | 100,0 | **87,7** | 46 | **973** | 1,09 MB |

**Lacunas declaradas.** A área autenticada do Meu SUS Digital (resultado de exame, carteira de
vacinação) foi excluída por conduta de coleta. É a limitação mais relevante do estudo: as telas
de maior consequência assistencial ficaram fora, e os índices podem estar otimistas.

**Achados de verificação prévia** (registrados em `catalog/targets.yaml`), todos com
consequência para a leitura dos resultados:

1. `saude.rj.gov.br` era um *stub* de 935 bytes que redirecionava por JavaScript — e declarava
   `lang="en"`. O portal institucional migrou para `www.rj.gov.br/saude`, mas os serviços ao
   cidadão permaneceram no subdomínio antigo.
2. `prefeitura.rio/saude` **não é um portal de serviços**: seu título é "Arquivos Saúde", uma
   seção de notícias. Os serviços municipais residem em `carioca.rio`. O cidadão que procura
   "saúde" no portal do município encontra jornalismo institucional.
3. `subpav.org`, antigo canal da atenção primária carioca, tornou-se "repositório de conteúdo
   técnico" dirigido a profissionais. Foi excluído da amostra: um canal antes voltado ao
   usuário deixou de sê-lo, **sem substituto anunciado**.
4. O Meu SUS Digital serve a mesma casca de 1418 bytes em toda rota, inclusive em
   `/robots.txt`. É uma aplicação de página única: sem renderização por navegador, a auditoria
   mediria uma casca vazia.

### 3.2.1 Disponibilidade como precondição da acessibilidade ✅

O portal estadual perdeu **50% das páginas** na coleta primária e 67% na repetição. O
diagnóstico distinguiu duas causas:

| Alvo | Falha | Padrão | Interpretação |
|---|---|---|---|
| gov.br/saúde | `ERR_CONNECTION_RESET` | Página **diferente** a cada execução (1 de 6) | Transitória |
| SES-RJ `/laudos` | `ERR_CONNECTION_CLOSED` | **4 de 4** tentativas, nos dois perfis | Sistemática |

Verificação complementar às 01h06: **ambos os hosts da SES-RJ ficaram inacessíveis também para
um cliente HTTP comum**, com o mesmo User-Agent — inclusive `www.rj.gov.br/saude`, que
respondera HTTP 200 quarenta minutos antes. Trata-se de **instabilidade de infraestrutura**, e
não de bloqueio a automação.

> **Ponto para a Discussão.** A disponibilidade é precondição da acessibilidade. Um serviço de
> resultado de exame que não responde não é um serviço difícil de usar: é um serviço
> indisponível. Nenhum índice de conformidade WCAG captura isso, e o estudo só o registrou
> porque o motor trata falha como **dado** — e não como interrupção.

### 3.3 Conformidade geral ✅

Mediana do ICA por página: **69,2** (IC 95% por bootstrap: 61,0–84,9; n = 16; Q1 = 60,4;
Q3 = 85,4; mín. 50,7; máx. 95,2).

**126 violações confirmadas** e 47 achados indeterminados, em 173 achados.

| Princípio POUR | Violações | | Nível | Violações | | Risco jurídico | Violações |
|---|---|---|---|---|---|---|---|
| Perceptível | **69** | | A | **85** | | Alto | **90** |
| Operável | 19 | | AA | 32 | | Crítico | **27** |
| Compreensível | 15 | | | | | Moderado | 9 |
| Robusto | 14 | | | | | Baixo | **0** |

Duas leituras merecem destaque na redação:

- **73% das violações são de nível A**, o patamar mínimo de conformidade. Não se trata de
  refinamento: é o piso que não foi alcançado.
- **Nenhuma violação de risco baixo.** Todas as barreiras detectadas obstruem tarefa ou exigem
  esforço desproporcional. O instrumento não está reportando irregularidade formal.

**Figura 1** — prevalência por critério (fração das páginas em que cada critério é violado):

| Critério | Prevalência | Nível |
|---|---|---|
| **4.1.2 Nome, função, valor** | **100%** | A |
| 1.1.1 Conteúdo não textual | 66,7% | A |
| 2.4.4 Finalidade do link | 66,7% | A |
| 1.3.1 Informações e relações | 66,7% | A |
| 3.3.2 Rótulos ou instruções | 66,7% | A |
| 1.4.4 Redimensionar texto | 55,6% | AA |
| 1.4.3 Contraste (mínimo) | 44,4% | AA |
| 1.4.10 Refluxo | 44,4% | AA |
| 2.4.1 Ignorar blocos | 33,3% | A |

> **O achado central do estudo.** O critério 4.1.2 foi violado em **todas** as páginas
> auditadas, das cinco plataformas, nas três esferas de governo. Significa que, em toda
> plataforma examinada, existe ao menos um controle que a tecnologia assistiva **não consegue
> anunciar**: para o usuário de leitor de tela, aquele botão ou link simplesmente não existe.
> Prevalência de 100% em uma amostra estratificada por esfera indica falha **estrutural** do
> ecossistema, não deficiência de um órgão.

### 3.4 Barreiras absolutas ✅

**Todas as cinco plataformas** apresentam violação de risco jurídico crítico. Em **14 das 16
páginas auditadas** (87,5%) há barreira sem rota alternativa.

Regras que produziram as 27 violações críticas:

| Regra | Achados | O que significa para o usuário |
|---|---|---|
| `link-name` | 10 | Link sem texto acessível: o leitor de tela anuncia "link" e nada mais |
| `button-name` | 7 | Botão sem nome: a ação é inominada |
| `input-button-name` | 4 | Botão de formulário sem rótulo |
| `label` | 2 | Campo sem rótulo programático |
| `probe.non-interactive-control` | 2 | `div` com clique, inalcançável por teclado |
| `nested-interactive` | 1 | Controle aninhado em controle: foco imprevisível |
| `input-image-alt` | 1 | Botão-imagem sem alternativa textual |

Todas se reduzem à mesma privação: **o controle existe visualmente e não existe para quem não
enxerga**. É a forma mais severa da barreira do art. 3º, IV, "d" da LBI.

### 3.5 Gradiente por esfera federativa ✅ (H1 — sustentada, com ressalvas)

| Esfera | n (páginas) | ICA mediana | IAN mediana | IEJ mediana |
|---|---|---|---|---|
| Federal | 7 | **87,0** | 69,9 | **13,6** |
| Estadual | 3 | 58,9 | 99,8 | 65,9 |
| Municipal | 6 | 61,0 | **100,0** | **84,2** |

- **ICA:** Kruskal-Wallis, p = 0,0068; ε² = 0,614 (efeito grande).
- **IAN:** Kruskal-Wallis, p = 0,0020; ε² = 0,804 (efeito grande).

Agregado em nível de portal (uma observação por plataforma), para contornar a
pseudorreplicação:

| Esfera | ICA por portal |
|---|---|
| Federal | 72,6 · 84,9 |
| Estadual | 54,1 |
| Municipal | 50,7 · 61,0 |

**Ressalvas obrigatórias na redação.** O n é pequeno (5 portais, 3 no estrato estadual) e as
páginas de um mesmo portal não são independentes. Os testes são **descritivos**, não
confirmatórios. O que a amostra sustenta é a direção — federal acima de estadual e municipal —
e a magnitude do efeito, não a generalização para o universo de portais brasileiros.

Note-se também que o índice de exposição jurídica separa os estratos com mais nitidez que o de
conformidade (13,6 contra 84,2, uma razão de mais de seis), sugerindo que a diferença entre
esferas está menos no **número** de falhas e mais na **gravidade** delas.

### 3.6 Efeito do perfil de dispositivo ✅ (H3 — parcialmente sustentada)

| Perfil | n | ICA mediana | IAN mediana | Peso mediano |
|---|---|---|---|---|
| desktop-1366 | 7 | 65,8 | 99,9 | 1,44 MB |
| mobile-320 | 9 | 72,6 | 99,8 | **2,44 MB** |

Mann-Whitney U: **não houve diferença detectável** no atrito (p = 0,957; δ de Cliff = 0,032,
efeito desprezível).

Mas a comparação de índices agregados esconde o achado relevante:

> **O critério 1.4.10 (Refluxo) apareceu exclusivamente no perfil móvel**, e nenhum critério
> apareceu exclusivamente no desktop. A barreira existe apenas onde o usuário está.

Auditar somente em desktop — prática comum na literatura e nas homologações — teria produzido
um relatório sem essa classe inteira de barreira. O achado justifica a exigência metodológica
de dois perfis, e é o argumento empírico mais direto contra a auditoria de perfil único.

Registre-se ainda que o peso mediano é **70% maior** no perfil móvel (2,44 MB contra 1,44 MB):
o dispositivo com menos recursos recebe mais bytes.

### 3.7 Custo de acesso ⬜ (H4) — parâmetros ✅

Parâmetros já coletados e documentados em
[parâmetros de custo](../metodologia/parametros-de-custo.md):

| Parâmetro | Valor | Fonte |
|---|---|---|
| Preço do dado | R$ 3,00/GiB | Claro Prezão R$ 15,00 / 5 GB / 15 dias, 10/08/2026 |
| Franquia | 10 GiB/mês | Duas recargas do mesmo plano |
| Limiar de peso | 2,5 MiB | Mediana móvel, HTTP Archive Web Almanac 2025 |

Corroboração oficial (ANATEL, *Panorama Econômico-Financeiro*, 1T2026): preço médio efetivo
R$ 5,46/GB; consumo médio 6,51 GB/mês; ARPU pré-pago R$ 12,12/mês. Os parâmetros adotados são
conservadores frente a esses números.

#### Resultados medidos ✅

Peso mediano por página: **1,82 MB** (IC 95%: 1,36–2,94; n = 16). **4 de 16 páginas (25%)**
excedem o limiar de 2,5 MiB — a mediana da web comercial.

| Plataforma | Peso mediano | Custo/acesso | % franquia | Terceiros |
|---|---|---|---|---|
| Meu SUS Digital | **7,17 MB** | R$ 0,0210 | 0,070% | 2,2% |
| gov.br/saúde | 2,44 MB | R$ 0,0072 | 0,024% | 17,8% |
| SMS Rio | 2,10 MB | R$ 0,0062 | 0,021% | **69,3%** |
| SES-RJ | 1,55 MB | R$ 0,0045 | 0,015% | 16,1% |
| Carioca Digital | 1,05 MB | R$ 0,0031 | 0,010% | 36,3% |

**H4 não foi sustentada.** A correlação entre peso e fração de terceiros é **negativa**
(Spearman ρ = −0,256), o oposto do previsto. O caso extremo explica: o Meu SUS Digital é a
página mais pesada (7,17 MB) e a que **menos** depende de terceiros (2,2%) — seu peso vem da
própria aplicação. Já a seção de notícias da SMS Rio, com 2,10 MB, tem **69,3% do tráfego
dirigido a terceiros**.

> **Hipótese revista, a explorar na Discussão.** Peso próprio e dependência de terceiros são
> **duas patologias distintas**, e não manifestações de uma só. A primeira é dívida técnica de
> aplicação; a segunda é transferência de custo ao cidadão em favor de serviços que não lhe
> prestam nada. Exigem correções diferentes e têm fundamentos jurídicos diferentes — e o motor
> as separa desde o desenho, o que permitiu detectar a divergência.
>
> Que **quase 70% do tráfego** da seção de saúde do portal municipal vá a domínios de terceiros
> é o dado isolado mais forte desta seção: o cidadão custeia, da própria franquia, recursos
> alheios ao serviço público que foi buscar.

**Redação obrigatória.** O custo monetário de um acesso isolado é pequeno — de R$ 0,003 a
R$ 0,021 — e o texto precisa afirmá-lo. A força do argumento está na jornada completa, na
tentativa frustrada por barreira de acessibilidade (as duas dimensões se agravam mutuamente) e
no tráfego de terceiros. Inflar o número seria fabricar evidência.

### 3.7.1 Dois achados a desenvolver ✅

**A penalidade da pobreza no dado móvel.** A mesma operadora cobra R$ 3,00/GB de quem recarrega
R$ 15,00 a cada 15 dias e R$ 2,00/GB de quem recarrega R$ 30,00 por 30 dias — 50% a mais para
quem não consegue comprometer o valor cheio. Fracionar não é conveniência, é restrição de
fluxo de caixa. É o mecanismo de Caplovitz (*The Poor Pay More*, 1963) reproduzido na
infraestrutura de acesso ao serviço público digital.

**A assimetria do zero-rating.** A oferta de entrada consultada isenta explicitamente o
WhatsApp do consumo de franquia; o portal público de saúde não é isento. Para o usuário de
menor renda, o Estado é o único serviço que cobra pelo acesso. Sugere via de correção
**regulatória** — inclusão de serviços públicos essenciais no tráfego não tarifado —, e não
apenas técnica.

### 3.8 Perfil de exclusão ✅

**Figura 2** — ocorrências de barreira por grupo de pessoas afetado. Converte contagem de
defeitos em população impactada.

| Grupo afetado | Ocorrências | Achados |
|---|---|---|
| Deficiência intelectual / neurodivergência | **1 149** | 101 |
| Baixa visão | 1 075 | 80 |
| Deficiência na visão de cores | 636 | 8 |
| Cegueira (leitor de tela) | 489 | 85 |
| Deficiência motora | 135 | 38 |
| Plano de dados limitado | 104 | 20 |
| Comando por voz | 90 | 25 |

Dois pontos para a redação:

- **Deficiência intelectual e neurodivergência encabeçam a lista**, com mais ocorrências que
  cegueira. É contraintuitivo e importante: o debate público sobre acessibilidade digital
  costuma se organizar em torno do leitor de tela, e a medida mostra que a maior carga recai
  sobre quem depende de estrutura, rotulagem e linguagem previsíveis.
- **Visão de cores tem 636 ocorrências em apenas 8 achados** — razão de 79 ocorrências por
  achado. É o retrato do defeito de *design system*: uma decisão de paleta, replicada em
  centenas de elementos. Corrigi-la em um lugar resolveria todas, e é exatamente o tipo de
  achado que o amortecimento logarítmico do IAN evita superponderar.

### 3.9 Qualificação jurídica ✅

Dispositivos invocados pelas 126 violações:

| Dispositivo | Invocações |
|---|---|
| LBI, art. 18 (atenção integral à saúde da PcD) | 126 |
| CF/88, art. 196 (acesso universal e igualitário) | 126 |
| LBI, art. 63, caput (acessibilidade obrigatória em sítios de governo) | 117 |
| LBI, art. 3º, IV, "d" (barreiras nas comunicações e na informação) | 117 |
| LBI, art. 4º (igualdade e não discriminação) | 117 |
| Decreto 5.296/2004, art. 47 | 117 |
| eMAG 3.1 | 117 |
| Convenção da ONU, art. 25 (Decreto 6.949/2009) | 117 |
| LBI, art. 74 (tecnologia assistiva) | 78 |
| CF/88, art. 5º, XIV (acesso à informação) | 36 |
| Convenção da ONU, art. 9 — **status de emenda constitucional** | 27 |
| LAI, art. 8º, § 3º, VIII (transparência ativa) | 27 |

As 27 invocações do art. 9 da Convenção correspondem exatamente às 27 violações de risco
crítico — as barreiras sem rota alternativa. É o dado com maior densidade normativa do estudo:
**em todas as cinco plataformas há descumprimento de norma com hierarquia constitucional.**

Vias de exigibilidade cabíveis, por esfera:

| Esfera | Plataformas | Controle externo | Demais vias |
|---|---|---|---|
| Federal | Meu SUS Digital, gov.br/saúde | TCU | MPF, ACP, art. 64 da LBI |
| Estadual | SES-RJ | TCE-RJ | MPRJ, ouvidoria estadual |
| Municipal | SMS Rio, Carioca Digital | TCM-RJ | MPRJ, ouvidoria municipal, 1746 |

---

## 4. Discussão

### 4.1 Principais achados ✍️ — material medido disponível

Seis achados a desenvolver, todos sustentados por dado:

1. **O critério 4.1.2 foi violado em 100% das páginas auditadas.** Em toda plataforma, nas três
   esferas, existe controle que a tecnologia assistiva não consegue anunciar. Prevalência total
   em amostra estratificada indica falha estrutural do ecossistema, não deficiência de um órgão.
2. **As cinco plataformas apresentam barreira absoluta.** Não há, no conjunto examinado, um
   único serviço digital de saúde plenamente utilizável por pessoa cega ou com deficiência
   motora.
3. **Gradiente por esfera, com efeito grande** (ε² = 0,61 para conformidade; 0,80 para atrito).
   A distância é maior na *gravidade* das falhas que no número delas.
4. **A barreira de refluxo só existe onde o usuário está.** O critério 1.4.10 apareceu
   exclusivamente no perfil de 320 px — auditoria de perfil único não a veria.
5. **Peso próprio e dependência de terceiros são patologias distintas** (ρ = −0,256). A página
   mais pesada é a que menos depende de terceiros; a seção de notícias municipal dirige 69% do
   tráfego a domínios alheios ao serviço.
6. **Indisponibilidade como barreira.** O serviço estadual de resultado de exame não respondeu
   em nenhuma das quatro tentativas, e ambos os hosts da SES-RJ ficaram inacessíveis durante a
   janela. Nenhum índice WCAG captura isso.

### 4.1.1 O achado contraintuitivo do perfil de exclusão ✍️

Deficiência intelectual e neurodivergência lideram as ocorrências (1 149), acima de cegueira
(489). O debate público e a prática de mercado organizam-se em torno do leitor de tela; a
medida sugere que a maior carga recai sobre quem depende de estrutura semântica, rotulagem
consistente e linguagem previsível — precisamente o que se degrada primeiro quando a
acessibilidade é tratada como conformidade formal.

Vale contrastar com a razão ocorrências/achado do grupo de visão de cores (79:1), que revela o
defeito de sistema de design: uma decisão de paleta replicada centenas de vezes.

### 4.2 O art. 63 como norma em branco ✍️

Desenvolver: a remissão às "melhores práticas adotadas internacionalmente" transforma um
padrão técnico privado (W3C) em conteúdo de dever jurídico. Consequências: (a) atualização do
padrão altera o dever sem alteração legislativa; (b) o eMAG funciona como vetor de
concretização; (c) a divergência entre WCAG 2.1 e 2.2 cria zona de indeterminação — de que o
critério 4.1.1 é exemplo concreto e documentado neste trabalho.

### 4.3 Acessibilidade como condição do acesso universal ✍️

Articular art. 196 da CF/88 com art. 63 da LBI e art. 9 da Convenção da ONU (status de emenda
constitucional). Tese: quando o canal digital é a via preferencial ou única de acesso ao
serviço, sua inacessibilidade **restringe o próprio direito à saúde**, e não apenas o direito
à informação.

### 4.4 Exclusão digital e exclusão por deficiência ✍️

Sustentar que são barreiras de mesma natureza jurídica, ambas obstruindo o acesso ao direito.
O custo de dados como transferência de ônus econômico ao cidadão — agravada pela parcela do
tráfego destinada a terceiros, que não presta serviço público algum.

### 4.5 Limites do método ✍️ ✅

1. Cobertura parcial (27/50 critérios, e apenas para alguns modos de falha).
2. Áreas autenticadas não auditadas — índices possivelmente otimistas.
3. **Amostra pequena:** 5 portais, 16 auditorias de página válidas, 3 no estrato estadual.
   Amostragem intencional, sem inferência para o universo nacional. Os testes são descritivos.
4. **Perda de 20% das páginas**, concentrada no portal estadual (50%). A perda não é ruído:
   é informação sobre disponibilidade, mas reduz a base de comparação do estrato estadual a
   três observações.
5. **Janela única.** A coleta ocorreu em um só dia; a instabilidade da SES-RJ pode ser
   circunstancial. A proposta é de auditoria contínua, e este é o primeiro ponto da série.
6. **Pseudorreplicação.** Páginas do mesmo portal compartilham template e equipe; os testes
   por página são descritivos, e a agregação por portal é reportada em paralelo.
7. **Preço do dado como parâmetro externo:** coletado e datado, mas é oferta comercial que
   muda, e o valor de uma operadora não representa todo o mercado.
8. **Critérios da WCAG 2.2 fora do escopo**, notadamente 2.5.8 (tamanho do alvo de toque),
   relevante para o uso móvel que os próprios dados mostram ser predominante.
9. **Viés conhecido e medido na sonda de legibilidade** (subcontagem de hiatos), que
   superestima a facilidade de leitura — erro na direção conservadora.

### 4.6 Implicações para a política pública ✍️

- **Art. 64 da LBI** como instrumento subutilizado: condicionar financiamento e aprovação de
  projetos à conformidade é indução mais rápida que a via judicial.
- Auditoria **contínua** e pública como mecanismo de accountability — a ferramenta produz
  relatórios acessíveis, prontos para encaminhamento.
- Selo de acessibilidade digital (art. 63, § 1º), nunca regulamentado.

### 4.7 Trabalhos futuros ✍️

- Avaliação com usuários reais de tecnologia assistiva (o que nenhuma auditoria automática
  substitui).
- Série temporal: a proposta é contínua, e este trabalho é o primeiro ponto.
- Extensão a aplicativos móveis nativos.
- Modelo de efeitos mistos, com portal como efeito aleatório, para tratar a
  pseudorreplicação.

---

## 5. Conclusão ✍️ ⬜

---

## Materiais suplementares ✅

| Artefato | Conteúdo |
|---|---|
| Repositório | Código completo, sob AGPL-3.0 |
| `data/scans/*.json` | Varreduras com evidência e procedência |
| `data/acessisaude.sqlite` | Banco pronto para consulta |
| `achados.csv`, `paginas.csv` | Datasets em formato longo |
| `fixtures/` + manifesto | Conjunto de validação e verdade de referência |
| Hash do commit | Estado do código na coleta |

---

## Checklist antes da submissão

**Concluído**

- [x] Preço do dado, franquia e limiar de peso coletados, com fonte e data
      (`docs/metodologia/parametros-de-custo.md`)
- [x] Janela de coleta declarada em `collection_window` (16/08/2026)
- [x] URLs do catálogo conferidas na data da coleta, com quatro correções registradas
- [x] `robots.txt` verificado na origem de cada host, com o resultado em `robots_note`
- [x] Coleta executada; 5 plataformas, 20 auditorias de página
- [x] Lacunas declaradas listadas (área autenticada do Meu SUS Digital)
- [x] Cobertura (27/50) declarada em Métodos e em Resultados
- [x] Tamanho de efeito reportado em todo teste (ε², δ de Cliff)
- [x] Pseudorreplicação declarada, com agregação por portal em paralelo
- [x] Figuras verificadas em escala de cinza, com hachura distinguindo séries
- [x] Perda de páginas reportada e diagnosticada (transitória × sistemática)

**Pendente**

- [ ] Redigir Introdução, Discussão e Conclusão
- [ ] Levantar dados de contexto: penetração de pré-pago e perfil de dispositivo da população
      SUS-dependente (TIC Domicílios / CETIC.br)
- [ ] Revisão de literatura e posicionamento da lacuna
- [ ] Citação da Anatel substituída pelo relatório primário, não pelo veículo especializado
- [ ] Parâmetros de custo reconferidos nos sítios das operadoras, com captura arquivada
- [ ] Considerar ampliar a amostra: 3 observações no estrato estadual é pouco
- [ ] Repetir a coleta em segunda janela, para separar instabilidade circunstancial de crônica
- [ ] Órgãos auditados previamente comunicados, com relatório HTML encaminhado
- [ ] Material suplementar depositado com DOI
