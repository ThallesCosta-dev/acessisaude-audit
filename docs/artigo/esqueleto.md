# Esqueleto do artigo (IMRaD)

**Título:** Auditoria Algorítmica de Acessibilidade em Plataformas Digitais de Saúde no Rio
de Janeiro: Uma Análise Interdisciplinar sob a Ótica da LBI e do Direito à Saúde

**Estado:** **coleta executada em 16/08/2026, com quatro medições repetidas.** Métodos,
validação do instrumento, confiabilidade teste-reteste e Resultados sustentados por dados
medidos. Falta a redação discursiva de Introdução, Discussão e Conclusão.

Legenda: ✅ dado medido · ✍️ redação a fazer · ⬜ pendente

> **Dataset primário:** as medições realizadas **após a correção do instrumento** (01h39 UTC
> em diante). As anteriores usavam um perfil desktop que anunciava `HeadlessChrome` e não
> identificava a pesquisa, o que produzia perda de páginas por bloqueio. Ver § 3.1.2 e
> [ADR 0008](../adr/0008-user-agent-em-todos-os-perfis.md).

---

## Resumo

✍️ Escrever por último. Números já disponíveis (250 palavras):

> **Objetivo.** Avaliar a conformidade de plataformas digitais de saúde pública com incidência
> no Rio de Janeiro à WCAG 2.1 (níveis A e AA) e qualificar juridicamente as barreiras
> encontradas à luz da Lei 13.146/2015. **Métodos.** Auditoria algorítmica de **cinco
> plataformas** estratificadas por esfera federativa, em dois perfis de dispositivo, com
> instrumento validado contra conjunto de referência (nenhum falso positivo; 18 de 20
> critérios plantados detectados) e submetido a quatro medições repetidas. Coleta em
> 16/08/2026. **Resultados.** Foram realizadas 20 auditorias de página, 16 bem-sucedidas, com
> 125 violações confirmadas. Mediana do índice de conformidade: **69,2** (IC 95%: 61,0–86,0),
> com **estabilidade perfeita entre medições repetidas** (Δ = 0,0 nas cinco plataformas).
> **Todas as 16 páginas auditadas apresentaram barreira absoluta** — violação de risco
> jurídico crítico, sem rota alternativa. O critério 4.1.2 (Nome, função, valor) foi violado em
> **100% das páginas**. Observou-se gradiente por esfera federativa (Kruskal-Wallis, p = 0,003;
> ε² = 0,75): mediana de 86,0 no âmbito federal contra 58,9 no estadual e 61,0 no municipal.
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

### 3.1.2 Confiabilidade teste-reteste e correção do instrumento ✅

**Quatro medições** de cada plataforma, entre 00h58 e 01h45 UTC de 16/08/2026.

O índice de conformidade foi **idêntico em todas as medições, nas cinco plataformas**
(Δ = 0,0), e o conjunto de critérios violados repetiu-se integralmente em quatro delas. É o
resultado esperado de barreiras estruturais — e a evidência de que o instrumento mede o
portal, não o momento.

**Defeito detectado e corrigido durante a coleta.** O perfil desktop não declarava
`User-Agent` explícito e herdava o padrão do Playwright, que anuncia
`HeadlessChrome/<versão>`. Isso violava a conduta declarada do projeto — identificar a
pesquisa — e produzia perda de páginas por bloqueio:

| Instrumento | Medições de `gov.br/saúde` | Perda de páginas |
|---|---|---|
| Com `HeadlessChrome` | 3 | 17% · 17% · 33% |
| Com `User-Agent` identificado | 3 | **0% · 0% · 0%** |

Teste direto confirmou que o `User-Agent` **não** explicava as falhas da SES-RJ, que têm outra
causa (§ 3.2.1). Mas explicava as do portal federal: as perdas ali eram **artefato do
instrumento**, não propriedade do portal.

Consequência metodológica: o dataset primário passou a ser o das medições posteriores à
correção. Usar as anteriores propagaria um viés do instrumento para os resultados publicados.

### 3.2 Caracterização da amostra ✅

Cinco plataformas, 20 auditorias de página (5 URLs × 2 perfis, mais sementes adicionais),
16 bem-sucedidas.

| Plataforma | Esfera | Serviço | Págs. | Perda | ICA | IAN | IEJ | Viol. | Ocorr. | Peso méd. |
|---|---|---|---|---|---|---|---|---|---|---|
| Meu SUS Digital | federal | prontuário | 2 | 0% | 72,6 | 99,9 | 58,7 | 13 | 37 | **7,17 MB** |
| gov.br/saúde | federal | informacional | 6 | 0% | **84,9** | 80,4 | 19,9 | 20 | 30 | 3,60 MB |
| SES-RJ | estadual | ouvidoria, exames | 6 | **67%** | 54,1 | 99,9 | 66,3 | 21 | 42 | 1,60 MB |
| SMS Rio (notícias) | municipal | informacional | 2 | 0% | 61,0 | 100,0 | 80,9 | 24 | 86 | 2,12 MB |
| Carioca Digital | municipal | serviços | 4 | 0% | **50,7** | 100,0 | **87,9** | 47 | **974** | 1,14 MB |

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

O portal estadual perdeu entre 50% e 67% das páginas em **todas** as quatro medições. Como o
`User-Agent` foi descartado como causa (§ 3.1.2), o diagnóstico prosseguiu por observação
direta da disponibilidade dos dois hosts da SES-RJ:

| Instante (UTC) | Instrumento | Resultado |
|---|---|---|
| 00h47 | cliente HTTP | HTTP 200 nos três endereços |
| 01h00 · 01h04 · 01h31 · 01h40 | navegador | falha em 50–67% das páginas |
| 01h06 | cliente HTTP | **falha nos dois hosts** |
| 01h29 | cliente HTTP | HTTP 200 nos três endereços |
| 01h37 | cliente HTTP **e** navegador | **falha em ambos, simultaneamente** |

**Conclusão:** a infraestrutura da SES-RJ oscila em escala de **minutos**, e a falha atinge
igualmente navegador e cliente HTTP simples. Não é bloqueio a automação — é indisponibilidade.

A página de **resultado de exame** (`/laudos`) nunca foi auditada com sucesso: falhou em
8 de 8 tentativas de navegador, embora o cliente HTTP a tenha alcançado duas vezes nos
intervalos entre quedas.

> **Ponto para a Discussão.** A disponibilidade é precondição da acessibilidade. Um serviço de
> resultado de exame que responde de forma intermitente não é um serviço difícil de usar: é um
> serviço que, para quem tenta no minuto errado, não existe. Nenhum índice de conformidade
> WCAG captura isso, e o estudo só o registrou porque o motor trata falha de carregamento como
> **dado** — com taxa de perda reportada em toda saída — e não como interrupção da coleta.
>
> Note-se a assimetria: o cidadão que encontra a página fora do ar não sabe se o problema é
> dele, do aparelho ou do Estado. A indisponibilidade intermitente é, do ponto de vista da
> experiência, pior que a queda franca.

### 3.3 Conformidade geral ✅

Mediana do ICA por página: **69,2** (IC 95% por bootstrap: 61,0–86,0; n = 16; Q1 = 60,4;
Q3 = 85,4; mín. 50,7; máx. 87,0).

**125 violações confirmadas** e 49 achados indeterminados, em 174 achados.

| Princípio POUR | Violações | | Nível | Violações | | Risco jurídico | Violações |
|---|---|---|---|---|---|---|---|
| Perceptível | **64** | | A | **82** | | Alto | **87** |
| Operável | 18 | | AA | 31 | | Crítico | **28** |
| Compreensível | 16 | | | | | Moderado | 10 |
| Robusto | 15 | | | | | Baixo | **0** |

Duas leituras merecem destaque na redação:

- **73% das violações são de nível A**, o patamar mínimo de conformidade. Não se trata de
  refinamento: é o piso que não foi alcançado.
- **Nenhuma violação de risco baixo.** Todas as barreiras detectadas obstruem tarefa ou exigem
  esforço desproporcional. O instrumento não está reportando irregularidade formal.

**Figura 1** — prevalência por critério (fração das páginas em que cada critério é violado):

| Critério | Prevalência | Nível |
|---|---|---|
| **4.1.2 Nome, função, valor** | **100%** | A |
| 3.3.2 Rótulos ou instruções | 75,0% | A |
| 1.1.1 Conteúdo não textual | 62,5% | A |
| 1.3.1 Informações e relações | 62,5% | A |
| 1.4.4 Redimensionar texto | 62,5% | AA |
| 2.4.4 Finalidade do link | 62,5% | A |
| 1.4.3 Contraste (mínimo) | 50,0% | AA |
| 1.4.10 Refluxo | 37,5% | AA |
| 2.4.1 Ignorar blocos | 25,0% | A |

> **O achado central do estudo.** O critério 4.1.2 foi violado em **todas** as páginas
> auditadas, das cinco plataformas, nas três esferas de governo. Significa que, em toda
> plataforma examinada, existe ao menos um controle que a tecnologia assistiva **não consegue
> anunciar**: para o usuário de leitor de tela, aquele botão ou link simplesmente não existe.
> Prevalência de 100% em uma amostra estratificada por esfera indica falha **estrutural** do
> ecossistema, não deficiência de um órgão.

### 3.4 Barreiras absolutas ✅

**Todas as cinco plataformas** e **todas as 16 páginas auditadas** apresentam violação de
risco jurídico crítico — barreira sem rota alternativa. Não há, no conjunto examinado, uma
única página de serviço público de saúde plenamente utilizável por pessoa cega ou com
deficiência motora.

Regras que produziram as 28 violações críticas:

| Regra | Achados | O que significa para o usuário |
|---|---|---|
| `button-name` | 10 | Botão sem nome: a ação é inominada |
| `link-name` | 10 | Link sem texto acessível: o leitor de tela anuncia "link" e nada mais |
| `input-button-name` | 4 | Botão de formulário sem rótulo |
| `probe.non-interactive-control` | 2 | `div` com clique, inalcançável por teclado |
| `input-image-alt` | 1 | Botão-imagem sem alternativa textual |
| `label` | 1 | Campo sem rótulo programático |

Todas se reduzem à mesma privação: **o controle existe visualmente e não existe para quem não
enxerga**. É a forma mais severa da barreira do art. 3º, IV, "d" da LBI.

### 3.5 Gradiente por esfera federativa ✅ (H1 — sustentada, com ressalvas)

| Esfera | n (páginas) | ICA mediana | IAN mediana | IEJ mediana |
|---|---|---|---|---|
| Federal | 8 | **86,0** | 80,8 | **22,3** |
| Estadual | 2 | 58,9 | 99,9 | 66,3 |
| Municipal | 6 | 61,0 | **100,0** | **84,2** |

- **ICA:** Kruskal-Wallis, p = 0,0029; ε² = 0,746 (efeito grande).
- **IAN:** Kruskal-Wallis, p = 0,0017; ε² = 0,831 (efeito grande).

Agregado em nível de portal (uma observação por plataforma), para contornar a
pseudorreplicação:

| Esfera | ICA por portal |
|---|---|
| Federal | 72,6 · 84,9 |
| Estadual | 54,1 |
| Municipal | 50,7 · 61,0 |

**Ressalvas obrigatórias na redação.** O n é pequeno (5 portais, e apenas **2 páginas válidas**
no estrato estadual, por causa da indisponibilidade), e as páginas de um mesmo portal não são
independentes. Os testes são **descritivos**, não confirmatórios. O que a amostra sustenta é a
direção — federal acima de estadual e municipal — e a magnitude do efeito, não a generalização
para o universo de portais brasileiros.

Note-se também que o índice de exposição jurídica separa os estratos com mais nitidez que o de
conformidade (22,3 contra 84,2, quase o quádruplo), sugerindo que a diferença entre esferas
está menos no **número** de falhas e mais na **gravidade** delas.

### 3.6 Efeito do perfil de dispositivo ✅ (H3 — parcialmente sustentada)

| Perfil | n | ICA mediana | IAN mediana | Peso mediano |
|---|---|---|---|---|
| desktop-1366 | 8 | 69,2 | 99,8 | 2,29 MB |
| mobile-320 | 8 | 66,8 | 99,8 | 2,26 MB |

Mann-Whitney U: **nenhuma diferença** no atrito (p = 1,000; δ de Cliff = 0,000).

A comparação de índices agregados esconde o achado relevante:

> **O critério 1.4.10 (Refluxo) apareceu exclusivamente no perfil móvel**, e nenhum critério
> apareceu exclusivamente no desktop. A barreira existe apenas onde o usuário está.

Auditar somente em desktop — prática comum na literatura e nas homologações — teria produzido
um relatório sem essa classe inteira de barreira. O achado justifica a exigência metodológica
de dois perfis, e é o argumento empírico mais direto contra a auditoria de perfil único.

> **Correção em relação à leitura preliminar.** Com o instrumento defeituoso, o peso mediano
> parecia 70% maior no perfil móvel (2,44 contra 1,44 MB). Com o instrumento corrigido, os
> pesos são equivalentes (2,26 contra 2,29 MB): a assimetria era artefato de quais páginas
> conseguiam carregar em cada perfil, e não característica dos portais. O caso ilustra por que
> perda diferencial de dados não pode ser tratada como ruído aleatório.

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

Peso mediano por página: **2,29 MB** (IC 95%: 1,59–4,15; n = 16). **4 de 16 páginas (25%)**
excedem o limiar de 2,5 MiB — a mediana da web comercial.

| Plataforma | Peso mediano | Custo/acesso | % franquia | Terceiros |
|---|---|---|---|---|
| Meu SUS Digital | **7,17 MB** | R$ 0,0210 | 0,070% | 2,2% |
| gov.br/saúde | 2,49 MB | R$ 0,0073 | 0,024% | 41,9% |
| SMS Rio | 2,11 MB | R$ 0,0062 | 0,021% | **69,4%** |
| SES-RJ | 1,60 MB | R$ 0,0047 | 0,016% | 16,6% |
| Carioca Digital | 1,14 MB | R$ 0,0033 | 0,011% | 40,8% |

**H4 não foi sustentada.** A correlação entre peso e fração de terceiros é **negativa**
(Spearman ρ = −0,386), o oposto do previsto. O caso extremo explica: o Meu SUS Digital é a
página mais pesada (7,17 MB) e a que **menos** depende de terceiros (2,2%) — seu peso vem da
própria aplicação. Já a seção de notícias da SMS Rio, com 2,11 MB, tem **69,4% do tráfego
dirigido a terceiros**.

Registre-se que **três das cinco plataformas dirigem mais de 40% do tráfego a terceiros** —
proporção que, com o instrumento defeituoso, aparecia subestimada no portal federal (17,8%
contra os 41,9% medidos).

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
| Deficiência intelectual / neurodivergência | **1 126** | 96 |
| Baixa visão | 1 060 | 76 |
| Deficiência na visão de cores | 636 | 8 |
| Cegueira (leitor de tela) | 479 | 82 |
| Deficiência motora | 116 | 37 |
| Plano de dados limitado | 106 | 22 |
| Comando por voz | 84 | 26 |

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

Dispositivos invocados pelas 125 violações:

| Dispositivo | Invocações |
|---|---|
| LBI, art. 18 (atenção integral à saúde da PcD) | 125 |
| CF/88, art. 196 (acesso universal e igualitário) | 125 |
| LBI, art. 63, caput (acessibilidade obrigatória em sítios de governo) | 113 |
| LBI, art. 3º, IV, "d" (barreiras nas comunicações e na informação) | 113 |
| LBI, art. 4º (igualdade e não discriminação) | 113 |
| Decreto 5.296/2004, art. 47 | 113 |
| eMAG 3.1 | 113 |
| Convenção da ONU, art. 25 (Decreto 6.949/2009) | 113 |
| LBI, art. 74 (tecnologia assistiva) | 76 |
| CF/88, art. 5º, XIV (acesso à informação) | 38 |
| Convenção da ONU, art. 9 — **status de emenda constitucional** | 28 |
| LAI, art. 8º, § 3º, VIII (transparência ativa) | 26 |

As 28 invocações do art. 9 da Convenção correspondem exatamente às 28 violações de risco
crítico — as barreiras sem rota alternativa. É o dado com maior densidade normativa do estudo:
**em todas as cinco plataformas, e em todas as páginas auditadas, há descumprimento de norma
com hierarquia constitucional.**

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
2. **Todas as 16 páginas apresentam barreira absoluta.** Não há, no conjunto examinado, uma
   única página de serviço digital de saúde plenamente utilizável por pessoa cega ou com
   deficiência motora.
3. **Gradiente por esfera, com efeito grande** (ε² = 0,75 para conformidade; 0,83 para atrito).
   A distância é maior na *gravidade* das falhas que no número delas.
4. **A barreira de refluxo só existe onde o usuário está.** O critério 1.4.10 apareceu
   exclusivamente no perfil de 320 px — auditoria de perfil único não a veria.
5. **Peso próprio e dependência de terceiros são patologias distintas** (ρ = −0,386). A página
   mais pesada é a que menos depende de terceiros; a seção de notícias municipal dirige 69% do
   tráfego a domínios alheios ao serviço, e três das cinco plataformas passam de 40%.
6. **Indisponibilidade como barreira.** O serviço estadual de resultado de exame não respondeu
   em nenhuma das oito tentativas de navegador. Observou-se oscilação da infraestrutura em
   escala de minutos, afetando igualmente navegador e cliente HTTP. Nenhum índice WCAG
   captura isso.
7. **Estabilidade perfeita entre medições repetidas.** O índice de conformidade não variou
   (Δ = 0,0) em quatro medições de cada plataforma ao longo de 47 minutos, e o conjunto de
   critérios violados repetiu-se integralmente em quatro das cinco. As barreiras são
   estruturais, não circunstanciais — e o instrumento mede o portal, não o momento.

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
5. **Janela única.** As quatro medições ocorreram em 47 minutos. **Não são janelas temporais
   distintas** e não permitem separar instabilidade circunstancial de crônica, nem detectar
   mudança nos portais. A estabilidade observada atesta a confiabilidade do instrumento, não a
   persistência das barreiras no tempo. Uma série temporal genuína — a premissa de auditoria
   contínua que o trabalho defende — exige coletas separadas por dias, e permanece pendente.
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
- [ ] **Coletar em janelas separadas por dias** — as quatro medições atuais cobrem 47 minutos
      e atestam confiabilidade do instrumento, não persistência das barreiras
- [ ] Ampliar a amostra: 2 páginas válidas no estrato estadual é pouco, e a causa é a
      indisponibilidade do próprio portal — o que sugere coletar em horários distintos
- [ ] Órgãos auditados previamente comunicados, com relatório HTML encaminhado
- [ ] Material suplementar depositado com DOI
