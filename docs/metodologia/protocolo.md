# Protocolo metodológico

> Documento de referência da seção de Métodos do artigo. Descreve o desenho do estudo, o
> procedimento de coleta, as variáveis e o plano de análise.

---

## 1. Desenho do estudo

**Tipo:** estudo observacional, transversal, de auditoria algorítmica, com estratificação por
esfera federativa.

**Unidade de observação:** página web × perfil de dispositivo.
**Unidade de análise principal:** achado de auditoria.
**Unidade de comparação entre instituições:** plataforma (portal).

A distinção entre as três é essencial e frequentemente colapsada na literatura da área. Ver
§ 6, sobre pseudorreplicação.

---

## 2. População e amostra

**População:** plataformas digitais de saúde pública com incidência no município e no estado
do Rio de Janeiro.

**Amostragem:** intencional, estratificada por esfera federativa (federal, estadual,
municipal) e por natureza do serviço (informacional, transacional).

Amostragem intencional é adequada aqui porque a população é pequena e conhecida, e porque o
interesse é comparar **estratos de gestão**, não estimar parâmetro populacional. A
justificativa de inclusão de cada alvo é obrigatória, registrada no catálogo
(`selection_rationale`) e verificada em teste automatizado.

**Sementes:** URLs declaradas explicitamente, não descobertas automaticamente. Descoberta
automática produz amostra não reproduzível — o conjunto de links muda a cada publicação de
conteúdo.

**Teto:** 25 páginas por plataforma, por razão ética (carga sobre servidores públicos) e
metodológica (comparabilidade entre portais de tamanhos muito diferentes).

Detalhamento em [amostragem.md](amostragem.md).

---

## 3. Perfis de dispositivo

Dois perfis, por escolha metodológica e não técnica:

| Perfil | Dimensões | Justificativa |
|---|---|---|
| `mobile-320` | 320 × 640, DPR 2, UA de aparelho de entrada | Largura mínima exigida pelo critério 1.4.10; aproxima o aparelho predominante entre usuários de baixa renda |
| `desktop-1366` | 1366 × 768 | Resolução de desktop mais comum no Brasil; ambiente em que os portais costumam ser homologados |

**O contraste entre os dois é, por si, um achado do estudo.** Interfaces homologadas em
desktop e usadas em celular produzem barreiras que só aparecem no perfil estreito — o caso
mais claro é o critério 1.4.10, verificado exclusivamente em 320 px.

---

## 4. Instrumento

| Componente | Versão | Papel |
|---|---|---|
| Navegador | Chromium (versão registrada em cada varredura) | Renderização |
| Motor de regras | axe-core 4.13.0, vendorizado | Verificação determinística sobre o DOM |
| Sondas próprias | 16 | Interação real, medição de rede, legibilidade |
| Recorte de regras | `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa` | Exclui `best-practice`: recomendações sem lastro normativo não sustentam afirmação de violação legal |

### Validação do instrumento

Executada antes de qualquer afirmação sobre portais reais, contra o conjunto de referência
(`fixtures/`), com verdade declarada em `fixtures/manifest.yaml`:

| Métrica | Resultado |
|---|---|
| **Especificidade** — falsos positivos na fixture conforme | **0** |
| **Sensibilidade** — barreiras plantadas detectadas | **18 de 20** critérios distintos |
| Barreiras fora do alcance automático | **3** (1.4.1, 2.4.2, 2.4.4) |

As três inalcançáveis exigem julgamento semântico e são reportadas como limite do método,
não como falha da implementação. Ver [limites do axe-core](limites-do-axe-core.md).

---

## 5. Variáveis

### Desfechos primários

| Variável | Tipo | Escala | Definição |
|---|---|---|---|
| `ica` | contínua | 0–100 | Índice de Conformidade, ponderado por risco jurídico |
| `ian` | contínua | 0–100 | Índice de Atrito de Navegação |
| `barreira_absoluta` | binária | — | Presença de violação de risco jurídico crítico |

### Desfechos secundários

| Variável | Tipo | Definição |
|---|---|---|
| `iej` | contínua | Índice de Exposição Jurídica |
| `peso_mb` | contínua | Bytes trafegados, em MB |
| `custo_brl` | contínua | Custo por acesso, sob preço declarado |
| `terceiros_pct` | contínua | Fração do tráfego destinada a terceiros |
| `ocorrencias` | contagem | Elementos do DOM em situação de falha |

### Variáveis de estratificação

`esfera` (federal / estadual / municipal), `viewport`, `fluxo_essencial`,
`categoria de serviço`.

### Variáveis de procedência

`versao_axe`, `versao_motor`, `navegador`, `coletado_em`, `config_snapshot` completo. Sem
elas, nenhum número é reexecutável.

---

## 6. Plano de análise

### Estatística descritiva

Mediana e amplitude interquartil ao lado de média e desvio. Distribuições de índices de
acessibilidade são assimétricas e a média sozinha desloca a leitura.

### Comparação entre estratos

- **Dois grupos:** Mann-Whitney U, com δ de Cliff como tamanho de efeito.
- **Três ou mais:** Kruskal-Wallis, com ε².
- **Intervalos:** bootstrap percentílico, 10 000 reamostragens, semente fixa.

Testes não paramétricos por padrão: os índices não são normalmente distribuídos, concentram-se
em faixas e têm caudas longas.

**Tamanho de efeito é reportado sempre**, junto do valor-p. Com amostras de portais —
tipicamente dezenas de páginas e poucas instituições —, um p pequeno pode acompanhar diferença
irrelevante, e um p grande pode esconder diferença substantiva por falta de potência.

### Duas ameaças declaradas

**Pseudorreplicação.** Páginas do mesmo portal compartilham template, equipe e decisões de
design: **não são observações independentes**. Tratá-las como tal infla o n e produz
significância espúria. O módulo `analysis.statistics` exige que o chamador declare a unidade
de análise e anexa a advertência correspondente ao resultado
(`design_warning`), para que a limitação apareça no texto do artigo.

Mitigação: comparações entre esferas são reportadas **também** em nível de portal (uma
observação por plataforma), e a análise por página é apresentada como descritiva.

**Potência insuficiente.** Com poucos portais por estrato, a ausência de significância não
distingue "não há diferença" de "não houve como detectá-la". A função `report()` formula os
resultados como "não houve diferença detectável", nunca "os grupos são iguais".

---

## 7. Hipóteses

| # | Hipótese | Teste |
|---|---|---|
| H1 | Há gradiente de conformidade entre esferas federativas, com portais municipais apresentando menor ICA | Kruskal-Wallis, ICA por esfera |
| H2 | Serviços transacionais (agendamento, cadastro) apresentam maior atrito que informacionais | Mann-Whitney, IAN por categoria |
| H3 | O perfil móvel revela barreiras ausentes no desktop | Comparação pareada, mesmo URL nos dois perfis |
| H4 | O custo de acesso é maior em plataformas com maior participação de tráfego de terceiros | Correlação de Spearman entre `terceiros_pct` e `peso_mb` |

As hipóteses são **exploratórias** e devem ser declaradas como tais: o desenho não comporta
confirmação, e H1 em particular pressupõe capacidade técnica desigual entre níveis de gestão
— presunção que o estudo testa, e não adota.

---

## 8. Reprodutibilidade

Ver [reprodutibilidade.md](reprodutibilidade.md). Em síntese: o JSON de cada varredura carrega
o `config_snapshot` completo; o axe-core é vendorizado em versão fixa; o catálogo é
versionado; toda semente aleatória vem da configuração.

---

## 9. Ética

Ver [ética e conduta de coleta](etica-e-conduta-de-coleta.md). A ferramenta lê o DOM
renderizado de páginas públicas: não preenche formulário, não autentica, não envia dados.
Áreas autenticadas são excluídas e reportadas como lacunas declaradas da amostra.

---

## 10. Limitações a declarar no artigo

1. **Cobertura parcial.** 27 dos 50 critérios admitem veredito automático, e apenas para
   alguns modos de falha. Ausência de achado não é conformidade.
2. **Áreas autenticadas não auditadas.** Concentram as telas de maior risco; os índices podem
   estar otimistas.
3. **Amostragem intencional.** Não permite inferência para o universo de portais públicos
   brasileiros.
4. **Pseudorreplicação.** Páginas do mesmo portal não são independentes.
5. **Preço do dado como parâmetro externo.** Coletado e datado
   ([parâmetros de custo](parametros-de-custo.md)), mas é uma oferta comercial que muda, e o
   valor de uma operadora não representa todo o mercado. Os parâmetros adotados são
   conservadores frente aos dados da Anatel: a estimativa de custo erra para menos.
6. **Corte temporal.** Portais mudam; a janela de coleta precisa ser declarada e o desenho é
   de auditoria contínua, não de fotografia única.
7. **Critérios da WCAG 2.2 fora do escopo.** Notadamente 2.5.8 (tamanho do alvo de toque),
   relevante para uso móvel.
8. **Viés conhecido na sonda de legibilidade.** O agrupamento vocálico subconta hiatos e
   superestima a facilidade de leitura — erro conservador, medido e declarado.
