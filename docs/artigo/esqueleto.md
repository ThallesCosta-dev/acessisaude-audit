# Esqueleto do artigo (IMRaD)

**Título:** Auditoria Algorítmica de Acessibilidade em Plataformas Digitais de Saúde no Rio
de Janeiro: Uma Análise Interdisciplinar sob a Ótica da LBI e do Direito à Saúde

**Estado:** estrutura definida, seções de Métodos e de validação do instrumento já
sustentadas por resultados medidos. Aguarda a coleta de campo para Resultados e Discussão.

Legenda: ✅ dado já medido · ⬜ depende da coleta · ✍️ redação a fazer

---

## Resumo

⬜ Escrever por último. Estrutura sugerida (250 palavras):

> **Objetivo.** Avaliar a conformidade de plataformas digitais de saúde pública do Rio de
> Janeiro à WCAG 2.1 (A/AA) e qualificar juridicamente as barreiras encontradas à luz da Lei
> 13.146/2015. **Métodos.** Auditoria algorítmica de N plataformas, estratificadas por esfera
> federativa, em dois perfis de dispositivo, com instrumento validado contra conjunto de
> referência (especificidade 100%, sensibilidade 18/20 critérios). **Resultados.** ⬜
> **Conclusões.** ⬜

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

### 3.2 Caracterização da amostra ⬜

Tabela: plataforma, esfera, categoria de serviço, páginas auditadas, lacunas declaradas,
população de referência. Declarar a janela de coleta.

### 3.3 Conformidade geral ⬜

- ICA por plataforma, com intervalo por bootstrap.
- Distribuição de violações por princípio POUR e por nível (A / AA).
- **Figura 1:** prevalência por critério — em que fração das páginas cada critério é violado.
  Prevalência, e não contagem: contagem é dominada pelo portal maior, prevalência responde se
  a barreira é estrutural no ecossistema.

### 3.4 Barreiras absolutas ⬜

Quantas plataformas apresentam violação de risco crítico. **Reportar antes de qualquer índice
contínuo:** um portal pode ter ICA alto e ser inutilizável.

Detalhar cada ocorrência: critério, página, fluxo em que se encontra.

### 3.5 Gradiente por esfera federativa ⬜ (H1)

Kruskal-Wallis do ICA por esfera, com ε² e intervalos. **Figura 3:** diagrama de caixa com
pontos sobrepostos — com poucos portais por estrato, a caixa sozinha sugere densidade de dados
que não existe.

Reportar em nível de página **e** em nível de portal, explicitando a pseudorreplicação.

### 3.6 Efeito do perfil de dispositivo ⬜ (H3)

Comparação pareada, mesma URL nos dois perfis. Espera-se que o critério 1.4.10 apareça
exclusivamente no perfil de 320 px — o que já ocorre no conjunto de validação e é verificado
em teste.

### 3.7 Custo de acesso ⬜ (H4)

- Peso mediano por página, custo em reais, fração da franquia.
- Fração destinada a terceiros — a métrica juridicamente mais relevante.
- **Figura 4:** distribuição de peso em escala logarítmica.

⚠️ **Substituir o preço de referência pelo valor coletado, com fonte e data, antes de
publicar.** O valor padrão do código é ilustrativo.

### 3.8 Perfil de exclusão ⬜

**Figura 2:** ocorrências de barreira por grupo afetado. Converte contagem de defeitos em
população impactada — a leitura que sustenta o argumento jurídico.

### 3.9 Qualificação jurídica ⬜

- Dispositivos mais frequentemente invocados.
- Distribuição de risco jurídico das violações encontradas.
- Vias de exigibilidade cabíveis por esfera (TCU para federal, TCE para estadual/municipal).

---

## 4. Discussão

### 4.1 Principais achados ✍️ ⬜

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
3. Amostragem intencional — sem inferência para o universo nacional.
4. Pseudorreplicação.
5. Preço do MB como premissa declarada, não medida.
6. Corte temporal.
7. Critérios da WCAG 2.2 fora do escopo, notadamente 2.5.8 (alvo de toque).
8. Viés conhecido e medido na sonda de legibilidade (subcontagem de hiatos).

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

- [ ] Preço do MB e franquia substituídos por valores coletados, com fonte e data
- [ ] Janela de coleta declarada em `collection_window`
- [ ] URLs do catálogo conferidas na data da coleta
- [ ] Lacunas declaradas listadas na seção de Métodos
- [ ] Cobertura (27/50) declarada em Métodos **e** em Resultados
- [ ] Tamanho de efeito reportado em todo teste
- [ ] Pseudorreplicação declarada
- [ ] Órgãos auditados previamente comunicados, com relatório encaminhado
- [ ] Material suplementar depositado com DOI
- [ ] Figuras verificadas em escala de cinza (nenhuma informação só por cor)
