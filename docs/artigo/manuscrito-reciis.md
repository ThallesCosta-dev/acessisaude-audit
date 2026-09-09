# Auditoria algorítmica de acessibilidade em plataformas digitais de saúde pública: desenvolvimento de instrumento e qualificação jurídica de barreiras no Rio de Janeiro

# Algorithmic accessibility auditing in public health digital platforms: instrument development and legal qualification of barriers in Rio de Janeiro

# Auditoría algorítmica de accesibilidad en plataformas digitales de salud pública: desarrollo de un instrumento y calificación jurídica de barreras en Río de Janeiro

> **Seção pretendida:** Artigos originais (entre 40 e 60 mil caracteres com espaços).
> **Documento sem identificação de autoria**, conforme a política de avaliação duplo-cega da
> Reciis. Os dados de autoria constam exclusivamente da Folha de Rosto e dos metadados da
> submissão.


---

## Resumo

Plataformas digitais tornaram-se via preferencial de acesso a serviços públicos de saúde, e
sua inacessibilidade restringe um direito. Desenvolveu-se um instrumento de auditoria
algorítmica que converte falhas técnicas de acessibilidade em proposições jurídicas
fundamentadas na Lei Brasileira de Inclusão. Aferido contra conjunto de referência com
barreiras conhecidas, foi aplicado a cinco plataformas de saúde do Rio de Janeiro,
estratificadas por esfera federativa, em série diária de dezessete dias. No corte transversal, vinte auditorias de página produziram 168 violações confirmadas. Todas
apresentaram ao menos uma barreira crítica, sem rota alternativa, e o critério de nome, função
e valor dos componentes foi violado em todas. Observou-se gradiente entre esferas federativas.
Na série, três plataformas não variaram em dezesseis dias observados e duas mudaram, o que
indica que a periodicidade da verificação integra o método. A auditoria automática estabelece
um piso de não conformidade e sustenta qualificação jurídica auditável.

**Palavras-chave:** Pessoas com Deficiência; Acesso aos Serviços de Saúde; Saúde Digital;
Direito à Saúde; Exclusão Digital.

## Abstract

Digital platforms have become the preferred channel for public health services, and their
inaccessibility restricts a right. An algorithmic auditing instrument converts technical
accessibility failures into legal propositions grounded in the Brazilian Inclusion Law.
Assessed against a reference set with known barriers, it was applied to five health platforms
in Rio de Janeiro, stratified by federative level, and in a seventeen-day series. In the cross-sectional block, twenty page audits yielded 168 confirmed violations. Every page presented at least one critical barrier, with no alternative route, and
the criterion on name, role and value of interface components was violated in all. A gradient
across federative levels was observed. In the series, three platforms showed no variation
across sixteen observed days and two changed, which indicates that the periodicity of
verification is part of the method. Automated auditing establishes a floor of non-compliance
and supports auditable legal qualification.

**Keywords:** Persons with Disabilities; Health Services Accessibility; Digital Health; Right
to Health; Digital Divide.

## Resumen

Las plataformas digitales son la vía preferente de acceso a la salud pública, y su
inaccesibilidad restringe un derecho. Se desarrolló un instrumento de auditoría algorítmica
que convierte fallas de accesibilidad en proposiciones jurídicas fundamentadas en la Ley
Brasileña de Inclusión. Verificado con un conjunto de referencia con barreras conocidas, se
aplicó a cinco plataformas de salud de Río de Janeiro, estratificadas por esfera federativa,
en serie diaria de diecisiete días. Veinte auditorías del corte transversal produjeron 168 violaciones confirmadas. Todas presentaron al menos una
barrera crítica, sin ruta alternativa, y el criterio sobre nombre, función y valor de los
componentes fue violado en todas. Se observó gradiente entre esferas. En la serie, tres
plataformas no variaron en dieciséis días observados y dos cambiaron, lo que muestra que la
periodicidad integra el método. La auditoría automática establece un piso de incumplimiento y
sostiene calificación jurídica auditable.

**Palabras clave:** Personas con Discapacidad; Accesibilidad a los Servicios de Salud; Salud
Digital; Derecho a la Salud; Brecha Digital.

---

## 1 Introdução

### 1.1 O deslocamento do acesso

Quando um serviço público de saúde migra para o meio digital, a acessibilidade da interface
deixa de ser questão de usabilidade e passa a ser condição de exercício de um direito. Um
botão de confirmação de agendamento que não recebe foco do teclado não entrega à pessoa com
deficiência motora uma experiência ruim: entrega-lhe a ausência da consulta. Já o controle que
abre o resultado de um exame sem expor nome acessível sequer chega a existir para quem navega
por leitor de tela.

O art. 196 da Constituição Federal estabelece a saúde como direito de todos e dever do Estado,
garantido mediante políticas de acesso universal e igualitário (Brasil, 1988). Quando o Estado
elege o canal digital como via preferencial de um serviço, às vezes como via única, a
acessibilidade desse canal incorpora-se ao dever constitucional com a mesma força com que a
rampa se incorpora ao dever de acesso físico à unidade de saúde. Digitalizar não cria serviço
novo nem inaugura regime próprio; transporta um serviço existente para um meio em que as
barreiras mudam de natureza e conservam a consequência jurídica.

A Lei Brasileira de Inclusão (Brasil, 2015) fornece o elo entre o dever constitucional e o
padrão técnico. Seu art. 63, caput, torna obrigatória a acessibilidade nos sítios da internet
mantidos por órgãos de governo, "conforme as melhores práticas e diretrizes de acessibilidade
adotadas internacionalmente". O dispositivo é, tecnicamente, uma norma em branco: o legislador
incorporou o padrão por remissão em vez de descrevê-lo. No arranjo brasileiro, essa remissão
se concretiza pelo Modelo de Acessibilidade em Governo Eletrônico (Brasil, 2014a),
construído sobre as diretrizes do World Wide Web Consortium, e pelo art. 47 do Decreto
5.296/2004 (Brasil, 2004), que já determinava acessibilidade obrigatória nos portais da
administração pública.

### 1.2 A lacuna

Três literaturas se aproximam do problema sem convergir.

A primeira, de avaliação técnica de conformidade, tem no Brasil percurso de duas décadas.
Simão e Rodrigues (2005) avaliaram o portal federal de serviços e informações e já registravam
barreiras para o cidadão com deficiência. Freire, Castro e Fortes (2009) produziram o estudo
longitudinal mais consequente da série: mediram 1.232 páginas dos 27 sítios estaduais entre
1996 e 2007 e verificaram avanço modesto, ainda distante das diretrizes internacionais, mesmo
após o prazo fixado pelo Decreto 5.296/2004. O achado é decisivo aqui, porque converte questão
doutrinária em questão empírica: a existência da norma não produziu, por si, efeito mensurável.
Silva e La Rue (2015) examinaram oito portais do Executivo estadual e concluíram que nenhum
atendia integralmente aos critérios mínimos, e Barros *et al.* (2024) chegaram a conclusão
equivalente sobre a plataforma centralizada do governo federal. Fora do país, Alajarmeh (2021)
auditou os sítios oficiais de saúde pública de 25 países durante a pandemia e encontrou apenas
três aprovados em todos os testes, com predomínio de violações dos princípios perceptível e
operável, a mesma distribuição que este estudo encontrará.

São trabalhos convergentes no diagnóstico, com três fragilidades recorrentes: raramente declaram
a cobertura da ferramenta, o que torna qualquer percentual um número sobre denominador oculto;
quase nunca reportam a perda de páginas na coleta, tratando-a como incidente e não como dado; e
não qualificam juridicamente o achado, de modo que o relatório se dirige ao desenvolvedor, e não
ao gestor ou ao órgão de controle.

A segunda literatura examina a validade das diretrizes e a capacidade das ferramentas de
operacionalizá-las. Brajnik (2009) mostrou que critérios anunciados como testáveis variam entre
avaliadores. Vigo, Brown e Conway (2013) compararam seis ferramentas e encontraram cobertura de,
no máximo, 50% dos critérios de sucesso, com completude entre 14% e 38%. E Power *et al.* (2012),
a partir de 1.383 instâncias encontradas por 32 usuários cegos em 16 sítios, verificaram que
apenas 50,4% dos problemas vividos correspondiam a algum critério de sucesso. Somadas, as
conclusões delimitam o alcance do método automático: ele mede uma parte da norma, e a norma cobre
uma parte da experiência.

A terceira, no campo da comunicação e informação em saúde, examina a barreira comunicacional
dentro do serviço. Vieira, Caniato e Yonemotu (2017) mostraram, a partir das percepções de
pessoas com deficiência auditiva, que a barreira opera dentro do serviço, e não apenas no acesso
a ele; deslocada para o canal digital, ela muda de forma e conserva a natureza. A literatura
jurídica sobre o art. 63, por fim, analisa o dispositivo em chave doutrinária, sem instrumento
de mensuração.

A lacuna de que este trabalho trata está na articulação. Não há instrumento que produza, do
mesmo dado e com procedência auditável, a afirmação técnica e a proposição jurídica
correspondente, indicando qual dispositivo foi violado, quem é o sujeito obrigado e por qual
via a obrigação é exigível.

### 1.3 O usuário periférico

A barreira de acesso ao serviço público digital de saúde não é apenas sensorial. Plano pré-pago,
aparelho de entrada, rede instável e escolaridade heterogênea obstruem o acesso com o mesmo
efeito prático da barreira clássica, e frequentemente na mesma pessoa. O peso de uma página,
medido em bytes efetivamente trafegados, é barreira que as diretrizes não enxergam, porque
pressupõem um usuário que já chegou.

Os dados disponíveis sustentam a sobreposição. O Censo 2022 identificou 14,4 milhões de pessoas
com deficiência no país, 7,3% da população de dois anos ou mais; entre elas, a taxa de
analfabetismo era de 21,3%, quatro vezes a das pessoas sem deficiência, e apenas 7,4% haviam
concluído o ensino superior, contra 19,5% (IBGE, 2025). A TIC Domicílios 2024 mostra que apenas
3% das pessoas das classes D e E reúnem as condições do indicador de conectividade
significativa, contra 73% na classe A, e que 86% de quem tem celular nessas classes acessa a
rede exclusivamente por esse aparelho (CGI.br, 2025).

Escolaridade mais baixa, conectividade precária e dependência exclusiva do aparelho móvel são
as condições concretas em que a interface do serviço público de saúde é usada, e não variáveis
de contexto. São também as condições que a homologação em desktop, com banda larga e alta
escolaridade presumida, deixa de simular.

Este estudo adota a expressão *usuário periférico* para designar essa posição composta: quem
depende exclusivamente do sistema público de saúde e o acessa por infraestrutura de
conectividade precária. A categoria se sobrepõe à de pessoa com deficiência sem substituí-la.
O trabalho mede as duas dimensões separadamente, porque têm fundamentos jurídicos distintos e
correções distintas.

### 1.4 Objetivos

**Objetivo geral.** Desenvolver, validar e aplicar um instrumento de auditoria contínua que
converta falhas técnicas de acessibilidade em proposições jurídicas fundamentadas.

**Objetivos específicos.** (1) Modelar a correspondência entre os 50 critérios de sucesso de
níveis A e AA das diretrizes de acessibilidade para conteúdo web, versão 2.1 (W3C, 2018), e o
ordenamento jurídico brasileiro; (2) aferir o instrumento contra conjunto de referência com
barreiras conhecidas; (3) aplicá-lo a plataformas de saúde do Rio de Janeiro, estratificadas por
esfera federativa; (4) quantificar o custo de acesso em dados móveis como barreira; (5)
caracterizar o perfil de exclusão por grupo afetado.

---

## 2 Metodologia

### 2.1 Desenho do estudo

Estudo observacional de auditoria algorítmica, estratificado por esfera federativa, com dois
componentes. O transversal compara plataformas entre si em uma janela de medição; o longitudinal
repete a mesma auditoria, com a mesma configuração, em dias sucessivos, e é o que permite
distinguir barreira persistente de barreira transitória, distinção que a auditoria pontual, por
construção, não pode fazer.

A unidade de observação é a página web em um perfil de dispositivo, em um dia; a de análise é o
achado; a de comparação entre instituições é a plataforma. A distinção entre as três é
frequentemente colapsada na literatura da área, com consequências que a subseção 2.7 detalha.

### 2.2 População, amostra e conduta de coleta

A população é o conjunto de plataformas digitais de saúde pública com incidência no município e
no estado do Rio de Janeiro. A amostragem foi intencional, estratificada por esfera federativa e
por natureza do serviço, porque a população é pequena e conhecida e o interesse é comparar
estratos de gestão, não estimar parâmetro populacional. A justificativa de inclusão de cada alvo
consta do catálogo versionado do instrumento.

As páginas auditadas foram declaradas explicitamente, e não descobertas por rastreamento
automático, que produz amostra não reproduzível. Fixou-se teto de 25 páginas por plataforma, por
razão ética e metodológica. A conduta observou o `robots.txt` de cada origem, intervalo mínimo
de 2.000 milissegundos entre requisições e identificação da pesquisa no campo `User-Agent`. O
instrumento lê o documento renderizado de páginas públicas: não preenche formulários, não
autentica e não transmite dados. Áreas autenticadas foram excluídas e reportadas como lacunas
declaradas.

A coleta ocorreu entre 16 de agosto e 4 de setembro de 2026. Um primeiro bloco, em 16 e 19 de
agosto, com medições repetidas em intervalo de minutos, sustenta a análise de confiabilidade e
o exame de disponibilidade das subseções 3.2 e 3.4. A partir de 19 de agosto, tarefa agendada
passou a executar a mesma configuração diariamente, entre 12h20 e 12h25 em tempo universal
coordenado, sobre a mesma lista de páginas, por dezessete dias consecutivos. O horário fixo é
decisão metodológica: variação de horário confundiria mudança do portal com variação de carga
do servidor ao longo do dia. Produziram-se 85 varreduras e 340 tentativas de auditoria de
página, das quais 297 foram bem-sucedidas.

O **bloco transversal** das subseções 3.3 e 3.5 a 3.11 corresponde a 4 de setembro, único
critério de escolha sendo a cobertura: é dia em que as cinco plataformas responderam
integralmente, o que impede que a comparação entre esferas seja contaminada por
indisponibilidade de infraestrutura.

Registram-se dois desvios da cadência, mantidos na análise por serem menos danosos declarados
que suprimidos. Em 1º de setembro a tarefa não disparou e a coleta saiu manualmente às 18h07,
com os cinco índices idênticos aos dos dias vizinhos, sem efeito detectável. Em 25 de agosto,
falha de resolução de nomes na máquina coletora impediu qualquer observação, e o dia integra a
série sem veredito (subseções 3.2 e 3.12).

### 2.3 Perfis de dispositivo

Adotaram-se dois perfis, por decisão metodológica e não técnica. O `mobile-320` (320 × 640
pixels, densidade 2, agente de aparelho de entrada) corresponde à largura mínima exigida pelo
critério 1.4.10 e aproxima o aparelho predominante entre usuários de menor renda; o
`desktop-1366` (1366 × 768), à resolução mais comum no país e ao ambiente em que os portais
costumam ser homologados. O contraste entre os dois é, por si, um resultado do estudo.

### 2.4 A matriz de correspondência normativa

A contribuição central do instrumento é a matriz que vincula cada critério de sucesso a
dispositivos do ordenamento brasileiro, em três camadas cumulativas.

A camada geral incide sobre qualquer barreira; a de saúde, sobre todos os alvos deste estudo, e
acrescenta a Convenção Internacional sobre os Direitos das Pessoas com Deficiência, promulgada
pelo Decreto 6.949/2009 (Brasil, 2009) com status de emenda constitucional; a específica varia
com a natureza da barreira e acrescenta, por exemplo, o art. 74 da Lei Brasileira de Inclusão
quando há dependência de tecnologia assistiva e o art. 9 da Convenção quando a barreira é
absoluta. A terceira camada evita o vício, comum na literatura, de invocar o mesmo bloco de
dispositivos para qualquer falha, o que dilui a força argumentativa e impede graduar a
gravidade.

O risco jurídico de cada critério foi graduado pela combinação de três vetores (essencialidade
do serviço obstruído, existência de rota alternativa e reversibilidade do dano) em quatro
faixas, com os pesos empregados nos índices: crítico (peso 12; 4 critérios), alto (peso 7; 18),
moderado (peso 3; 19) e baixo (peso 1; 9). A escala é independente da gravidade técnica
atribuída pelo motor de regras, e ambas são reportadas. A matriz cobre os 50 critérios do
escopo, e a completude é verificada por teste automatizado.

### 2.5 Instrumento

O instrumento executa o navegador Chromium por automação, aplica sobre o documento renderizado
o motor de regras `axe-core` na versão 4.13.0, vendorizada para garantir reprodutibilidade, e
acrescenta 16 sondas próprias que cobrem 18 critérios e duas dimensões sem correspondência
normativa. O recorte restringiu-se às marcações `wcag2a`, `wcag2aa`, `wcag21a` e `wcag21aa`, com exclusão
da categoria de boas práticas, porque recomendação sem lastro normativo não sustenta afirmação
de violação legal.

Dois achados da construção das sondas afetam qualquer estudo que empregue o mesmo motor. O
`axe-core` aceita `placeholder` como nome acessível válido, e como esse é o padrão mais comum
nos formulários de agendamento dos portais públicos brasileiros, a omissão tornaria a auditoria
cega na tela de maior consequência assistencial. E o critério 4.1.1, removido na versão 2.2 das
diretrizes e acompanhado pelo motor, permanece na referência normativa brasileira: adotou-se a
norma que rege o objeto.

### 2.6 Índices

Contar violações produz três vieses, cada um suficiente para invalidar comparações entre
portais. O **viés de template**: uma página com 400 links sem nome acessível recebe 400
ocorrências, mas tem um defeito, o componente de link do sistema de design. O **viés de
equivalência**: somar uma falha de declaração de idioma com uma armadilha de teclado supõe que
ambas pesam igual. E o **viés de cobertura**, discutido na subseção 1.2. Daí quatro
indicadores.

O **Índice de Conformidade de Acessibilidade** (ICA) é dado por
ICA = 100 × (1 − Σ*w*(*c*) para *c* violado ⁄ Σ*w*(*c*) para *c* verificável), em que *w*(*c*) é
o peso do risco jurídico do critério. O denominador contém apenas os critérios com veredito
automático possível, e a razão entre eles e o total (27/50) acompanha todo índice publicado, sob
o rótulo de cobertura.

O **Índice de Atrito de Navegação** (IAN) agrega, por achado, o produto do peso técnico, do peso
jurídico e de log₂(1 + ocorrências), multiplicado por 1,5 nas páginas de fluxo essencial
declarado, e satura por IAN = 100 × (1 − *e*^(−atrito⁄κ)). O amortecimento logarítmico corrige o
viés de template, fazendo cem elementos com o mesmo defeito pesarem 6,7 vezes um, e a saturação
mantém o índice comparável entre portais de tamanhos distintos. O **Índice de Exposição
Jurídica** (IEJ) tem a mesma forma funcional, ignora o peso técnico e descarta os achados de
risco baixo, porque passivo jurídico não se mede por irregularidade formal, e sim por obstrução
efetiva de direito.

O **sinalizador de barreira absoluta** é booleano e indica a presença de violação de risco
crítico. Não é um índice, e é o mais importante: um portal pode ter conformidade alta e ser
inutilizável por uma única armadilha de teclado. Nenhum índice contínuo distingue "difícil" de
"impossível", razão pela qual o sinalizador precede qualquer número em todas as saídas.

O custo de acesso é o produto do peso da página, em mebibytes efetivamente trafegados, pelo preço
do dado móvel, expresso também como fração da franquia mensal. Os parâmetros foram coletados e
datados: R$ 3,00 por gibibyte (oferta pré-paga consultada em 10 de agosto de 2026), franquia de
10 gibibytes mensais e limiar de página onerosa de 2,5 mebibytes, peso mediano móvel do *Web
Almanac* (HTTP Archive, 2025). Os três são conservadores frente aos dados oficiais (Anatel,
2026): a estimativa erra para menos. Todos os parâmetros que afetam número publicável são
serializados junto de cada varredura.

### 2.7 Análise estatística

Empregou-se estatística não paramétrica, por assimetria conhecida das distribuições de índices
de acessibilidade: Kruskal-Wallis com ε² para três grupos, e Mann-Whitney com δ de Cliff para
dois. O tamanho de efeito é reportado sempre, ao lado do valor-p: com poucas instituições por
estrato, um p pequeno pode acompanhar diferença irrelevante e um p grande pode esconder
diferença substantiva por falta de potência.

Duas ameaças à validade foram declaradas no desenho, e não apenas na discussão. A
**pseudorreplicação**: páginas do mesmo portal compartilham template e equipe, e não são
observações independentes, de modo que tratá-las como tal infla o *n*; a mitigação foi reportar
as comparações entre esferas também em nível de portal e apresentar a análise por página como
descritiva. A **potência insuficiente**: os resultados são formulados como ausência de diferença
detectável, nunca como igualdade entre grupos.

As hipóteses são exploratórias e assim devem ser lidas: o desenho não comporta confirmação.
Formularam-se quatro: gradiente de conformidade entre esferas federativas (H1); maior atrito em
serviços transacionais que em informacionais (H2); barreiras reveladas exclusivamente pelo
perfil móvel (H3); e associação positiva entre peso da página e participação de tráfego de
terceiros (H4).

### 2.8 Validação do instrumento

Antes de qualquer afirmação sobre portais reais, o instrumento foi aferido contra um conjunto de
referência de cinco páginas sintéticas com verdade declarada em manifesto versionado: um
controle negativo, construído em conformidade, e um controle positivo com 20 barreiras
plantadas, cada uma anotada com o critério que deveria ser detectado. O parâmetro de saturação κ
do índice de atrito foi determinado empiricamente por esse conjunto, e não escolhido *a priori*:
o valor estimado inicialmente (κ = 40) fazia quatro das cinco páginas pontuarem acima de 98, de
modo que o índice deixava de distinguir "ruim" de "inutilizável", e a recalibração fixou
κ = 150.

### 2.9 Reprodutibilidade e ética

Cada varredura carrega o registro completo de configuração, incluindo versões do navegador, do
motor de regras e do próprio instrumento, além da data e hora da coleta. O motor está
vendorizado em versão fixa e o catálogo de alvos é versionado. O código e os dados primários
estão depositados em repositório público sob licença livre, cujo endereço será informado após a
avaliação por pares. O estudo não envolveu seres humanos nem dados pessoais, e não houve, por
isso, submissão a comitê de ética, nos termos da Resolução 510/2016 do Conselho Nacional de
Saúde.

---

## 3 Resultados

### 3.1 Aferição do instrumento

Contra o conjunto de referência, o instrumento não produziu falso positivo na página construída
em conformidade e detectou 18 dos 20 critérios plantados no controle positivo. A cobertura
declarada, isto é, os critérios com veredito automático possível, é de 27 dos 50 do escopo.

As três barreiras fora do alcance automático têm a mesma natureza: exigem julgamento semântico
que nenhuma ferramenta emite. A situação da consulta indicada só por círculo colorido (1.4.1)
requer decidir se a cor é o único portador do sentido; o título "Documento1" (2.4.2) existe, e a
pergunta é se descreve a página; os links "clique aqui" (2.4.4) têm texto, e a pergunta é se ele
descreve o destino. O resultado não é limitação envergonhada: é evidência, produzida pelo próprio
instrumento, de que a auditoria automática estabelece um piso de não conformidade e nunca um
atestado de acessibilidade.

### 3.2 Confiabilidade e correções do instrumento durante a coleta

Cada plataforma foi medida quatro vezes, entre 00h58 e 01h45 de 16 de agosto de 2026, com índice
de conformidade idêntico em todas as medições e variação nula, e conjunto de critérios violados
repetido integralmente em quatro das cinco. É o resultado esperado de barreiras estruturais, e
evidência de que o instrumento mede o portal, e não o momento.

A repetição revelou um defeito do próprio instrumento: o perfil de desktop não declarava agente
explícito e herdava o padrão da biblioteca de automação, que anuncia navegador em modo headless,
o que violava a conduta declarada de identificar a pesquisa e produzia perda de páginas por
bloqueio. Três medições com o agente herdado perderam 17%, 17% e 33% das páginas do portal
federal informacional, e três posteriores à correção não perderam nenhuma. Todas as medições
reportadas neste trabalho são posteriores à correção.

A série diária revelou um segundo defeito, mais grave, porque afetava a interpretação e não a
coleta. Em 25 de agosto, uma falha de resolução de nomes na máquina coletora impediu o
carregamento das 20 páginas das cinco plataformas. O índice de conformidade é a razão entre
critérios não violados e critérios avaliados: sem página carregada não há achado, o numerador
fica cheio, e o instrumento registrou 100 pontos, o máximo da escala, para as cinco plataformas,
no único dia em que nada foi observado.

A direção do erro é a mais desfavorável possível, porque falha de coleta empurra o índice para
cima e produz elogio onde deveria haver silêncio, e o resultado é indistinguível na saída, já
que conformidade perfeita e ausência de observação ocupam a mesma célula. A correção foi de
tipo, e não de apresentação: os quatro índices passaram a admitir valor nulo, significando *sem
veredito*, e o acumulador passou a contar páginas observadas, e não tentativas. Como o documento
primário armazena páginas e achados, e não índices, as coletas anteriores foram reprocessadas
sem que nenhum portal precisasse ser varrido de novo.

O episódio é reportado, e não apagado, porque **uma auditoria contínua precisa saber dizer que
não sabe**. Um instrumento que converte silêncio em aprovação produz atestado de conformidade
sobre o vazio.

### 3.3 Caracterização da amostra

O bloco transversal corresponde a 4 de setembro de 2026, dia em que as cinco plataformas
responderam integralmente: 20 auditorias de página, 20 bem-sucedidas, perda nula. A cobertura
completa evita que a comparação entre esferas seja contaminada por indisponibilidade de
infraestrutura (subseção 3.4).

**Tabela 1** – Plataformas auditadas: indicadores, peso e custo de acesso por plataforma, Rio de
Janeiro, 4 de setembro de 2026

| Plataforma | Esfera | Págs. | ICA | IAN | IEJ | Viol. | Ocorr. | Peso (MB) | Custo (R$) | Terceiros (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| Meu SUS Digital | Federal | 2 | 72,6 | 99,8 | 58,7 | 13 | 37 | 7,29 | 0,0214 | 3,9 |
| Portal federal de saúde | Federal | 6 | 80,1 | 90,6 | 25,6 | 26 | 42 | 3,55 | 0,0104 | 29,4 |
| Secretaria estadual de saúde | Estadual | 6 | 49,3 | 99,9 | 67,1 | 60 | 142 | 3,07 | 0,0090 | 26,8 |
| Secretaria municipal de saúde | Municipal | 2 | 61,0 | 100,0 | 81,2 | 24 | 90 | 2,12 | 0,0062 | 69,9 |
| Portal municipal de serviços | Municipal | 4 | 50,7 | 100,0 | 87,5 | 45 | 976 | 1,06 | 0,0031 | 37,1 |

Fonte: elaboração própria. ICA, Índice de Conformidade de Acessibilidade (0–100, maior é melhor); IAN, Índice de
Atrito de Navegação, e IEJ, Índice de Exposição Jurídica (0–100, menor é melhor).

A verificação prévia dos alvos produziu quatro achados registrados no catálogo: o endereço
institucional da secretaria estadual havia sido reduzido a um redirecionamento por script, porque
o portal migrou de domínio e os serviços ao cidadão permaneceram no subdomínio antigo; a seção de
saúde do portal da prefeitura não é portal de serviços, e sim jornalismo institucional; o antigo
canal da atenção primária municipal converteu-se em repositório dirigido a profissionais e foi
excluído da amostra, sem substituto anunciado ao usuário; e a plataforma federal de prontuário é
aplicação de página única, de modo que, sem renderização por navegador, a auditoria mediria uma
casca vazia.

A limitação mais relevante é declarada: a área autenticada da plataforma federal de prontuário,
onde residem resultado de exame e carteira de vacinação, foi excluída por conduta de coleta. As
telas de maior consequência assistencial ficaram fora, e os índices podem estar otimistas.

### 3.4 Disponibilidade e posição de rede do observador

A cobertura integral de 4 de setembro é recente. Em 16 de agosto, o portal estadual perdia entre
50% e 67% das páginas em todas as quatro medições, e o diagnóstico dessa perda produziu
resultado metodológico que sobrevive à normalização posterior. Descartado o agente de usuário
como causa, a observação direta mostrou oscilação em escala de minutos: a página de resultado de
exame falhou em oito de oito tentativas por navegador. A conclusão de indisponibilidade
repousava, porém, sobre um único ponto de observação, e a verificação em 19 de agosto a partir
de três posições de rede mostrou que a atribuição era insuficiente (Tabela 2).

**Tabela 2** – Resposta dos hospedeiros do portal estadual por posição de rede, 19 de agosto de
2026

| Endereço | Nuvem A (EUA) | Nuvem B (EUA) | Conexão residencial (Brasil) |
|---|---|---|---|
| Portal institucional | conexão encerrada | 500 | 200 |
| Resultado de exame | conexão encerrada | 500 | 200 |
| Ouvidoria | 200 | 200 | 200 |

Fonte: elaboração própria.

O padrão não é de indisponibilidade: o mesmo hospedeiro atende a ouvidoria a todas as posições e
recusa dois endereços específicos às estrangeiras, servindo-os normalmente à brasileira, no
mesmo intervalo de minutos. Negociação de HTTP/2, detecção de navegador automatizado e recusa
indiscriminada a origem estrangeira foram testadas e descartadas. O achado que sobrevive é mais
específico que o original: **o portal estadual diferencia a resposta conforme a origem de rede da
requisição**. A indisponibilidade de 16 de agosto foi real naquela janela, já que a posição
brasileira também falhou, mas não pode ser inferida de observação estrangeira. A consequência
está incorporada ao desenho: a posição de rede passa a ser variável declarada do estudo, e
nenhuma afirmação de indisponibilidade é sustentada a partir de um ponto único.

### 3.5 Conformidade geral

As 20 auditorias produziram **168 violações confirmadas**, 1.287 ocorrências e 66 achados
pendentes de revisão humana. Das 168, 154 correspondem a um critério de sucesso das diretrizes;
as 14 restantes decorrem da sonda de custo de acesso, que mede dimensão sem correspondência
normativa direta, e por isso não figuram na Tabela 3.

**Tabela 3** – Distribuição das 154 violações vinculadas a critério, por princípio, por nível
de conformidade e por risco jurídico

| Princípio | Violações | Nível | Violações | Risco jurídico | Violações |
|---|---|---|---|---|---|
| Perceptível | 85 | A | 120 | Alto | 110 |
| Operável | 28 | AA | 34 | Crítico | 42 |
| Robusto | 25 | | | Moderado | 16 |
| Compreensível | 16 | | | | |

Fonte: elaboração própria.

Duas leituras se impõem. A primeira é que 78% das violações vinculadas a critério são de nível A,
o patamar mínimo: não se trata de refinamento, mas do piso que não foi alcançado. A segunda é
que a concentração no princípio perceptível reproduz o padrão de Alajarmeh (2021) e é, em parte,
propriedade do método.

A Figura 1 apresenta a prevalência por critério, a fração dos dez endereços distintos auditados
em que cada um foi violado. **Dois critérios foram violados em 100% dos endereços**: 4.1.2
(Nome, função, valor) e 1.1.1 (Conteúdo não textual). Seguem-se 1.3.1 e 2.4.4 em 70%, e 3.3.2
em 60%.

**Figura 1** – Prevalência de violação por critério de sucesso, em fração dos endereços
auditados
Fonte: elaboração própria.

Prevalência total de 4.1.2 em amostra estratificada significa que nenhum dos três níveis de
governo produz interface cujos componentes anunciem corretamente nome, função e valor à
tecnologia assistiva. Um controle que a tecnologia assistiva não consegue anunciar não é um
controle difícil: para o usuário de leitor de tela, aquele botão não existe.

### 3.6 Barreiras absolutas

**As 20 páginas auditadas apresentam ao menos uma violação de risco jurídico crítico**, isto é,
barreira que impede o uso do serviço por um grupo identificável, sem rota alternativa. São 42
achados, e a origem deles é monótona: 14 vínculos e 10 botões sem nome acessível, que deixam
navegação e ação sem anúncio para o leitor de tela; 5 campos sem rótulo associado e 4 botões de
formulário sem nome, que tornam o formulário não preenchível; 4 elementos interativos
aninhados, que produzem foco e anúncio ambíguos; 2 elementos não interativos usados como
controle, inoperáveis por teclado; 2 resumos de bloco expansível sem nome; e 1 imagem-botão sem
alternativa textual.

A composição importa mais que o total: as barreiras críticas recaem sobre campos e botões de
busca, botões de autenticação e vínculos de navegação, elementos do caminho do serviço.

### 3.7 Gradiente por esfera federativa

A Tabela 4 apresenta as medianas dos três índices por esfera, em nível de página.

**Tabela 4** – Medianas dos índices por esfera federativa

| Esfera | Páginas | ICA | IAN | IEJ |
|---|---|---|---|---|
| Federal | 8 | 81,2 | 90,8 | 27,9 |
| Estadual | 6 | 73,3 | 99,9 | 66,3 |
| Municipal | 6 | 61,0 | 100,0 | 83,5 |

Fonte: elaboração própria.

O teste de Kruskal-Wallis resultou em p = 0,0031 e ε² = 0,563 para o índice de conformidade,
p = 0,0004 e ε² = 0,798 para o de atrito e p = 0,0004 e ε² = 0,813 para o de exposição jurídica:
efeitos grandes nos três casos. O índice de exposição jurídica separa os estratos com mais
nitidez que o de conformidade (27,9 contra 83,5, três vezes mais), o que sugere que a distância
entre esferas está menos no número de falhas e mais na gravidade delas (Figura 2).

**Figura 2** – Distribuição do índice de conformidade por esfera federativa
Fonte: elaboração própria.

Duas ressalvas são obrigatórias. O *n* é pequeno, e as páginas de um mesmo portal não são
independentes, o que expõe o resultado à pseudorreplicação declarada na subseção 2.7. E os
estratos não comparam objetos equivalentes: das seis páginas do estrato estadual, apenas a
ouvidoria é transacional, ao passo que o municipal concentra páginas de serviço. Como páginas
transacionais têm mais controles interativos, e é sobre controles que recaem os critérios
críticos, a heterogeneidade tende a atenuar o gradiente, e não a produzi-lo.

### 3.8 Efeito do perfil de dispositivo

A comparação entre perfis não revelou diferença nos índices agregados: a mediana de conformidade
é 72,9 nos dois, e a de atrito, 99,8. O agregado, porém, esconde o achado. **O critério 1.4.10
(Refluxo) foi violado exclusivamente no perfil de 320 pixels**, em quatro dos dez endereços, e
nenhum critério foi exclusivo do desktop.

A barreira de refluxo obriga a rolar horizontalmente para ler uma linha de texto, e existe apenas
na largura em que a maior parte da população de interesse acessa o serviço. Auditar somente em
desktop, prática comum na literatura e nas homologações, teria produzido relatório sem essa
classe inteira de barreira.

### 3.9 Custo de acesso

O peso, o custo por acesso e a participação de terceiros por plataforma constam da Tabela 1,
sob os parâmetros declarados na subseção 2.6. Nenhum acesso consome mais de 0,07% da franquia
mensal, e seis das vinte auditorias excedem 2,5 mebibytes. O custo de um acesso isolado é pequeno, de
R$ 0,003 a R$ 0,021: a relevância do achado não está no valor unitário, e a subseção 4.5
desenvolve por quê.

A decomposição revela dissociação que a média esconde: a plataforma federal de prontuário é a
página mais pesada e a que menos depende de terceiros, porque seu peso vem da própria
aplicação, enquanto a secretaria municipal é leve e dirige 69,9% do tráfego a domínios de
terceiros. **Peso próprio e dependência de terceiros são dimensões independentes**, e o
instrumento só pôde exibir a dissociação por separá-las desde o desenho, como mostra a Figura 3.

**Figura 3** – Peso da página decomposto em tráfego próprio e de terceiros, por plataforma
Fonte: elaboração própria.

### 3.10 Perfil de exclusão

A Figura 4 agrega as ocorrências por grupo de pessoas afetado, o que desloca a leitura da
contagem de defeitos para a identificação de quem fica de fora. A ordem é encabeçada por
deficiência intelectual e neurodivergência (1.218 ocorrências em 127 achados distintos) e baixa
visão (1.112 em 99), seguidas de deficiência na visão de cores (638 em 8) e cegueira (575 em
120); deficiência motora, comando por voz e plano de dados limitado completam a lista.

Dois padrões merecem leitura. O primeiro é de política: a maior carga não recai sobre o grupo que
a discussão pública associa à acessibilidade digital, e sim sobre quem depende de estrutura
semântica e linguagem previsível. O segundo é diagnóstico: a deficiência na visão de cores reúne
638 ocorrências em apenas 8 achados, razão de 80 por achado e retrato do defeito de sistema de
design, em que uma decisão de paleta se replica por centenas de elementos (Figura 4).

**Figura 4** – Ocorrências de barreira por grupo de pessoas afetado
Fonte: elaboração própria.

### 3.11 Qualificação jurídica

A matriz da subseção 2.4 vinculou as 168 violações a dispositivos determinados. A camada de
saúde, com o art. 18 da Lei Brasileira de Inclusão e o art. 196 da Constituição, foi invocada
pelas 168; a camada geral, pelas 154 vinculadas a critério. Na camada específica, o art. 74 da
Lei Brasileira de Inclusão foi invocado 110 vezes; o art. 5º, XIV, da Constituição, 50; o art. 9
da Convenção, 42; o art. 8º, § 3º, VIII, da Lei de Acesso à Informação, 36; e o art. 5º da Lei
13.460/2017, outras 18.

As 42 invocações do art. 9 da Convenção correspondem exatamente às 42 violações de risco
crítico. É o dado de maior densidade normativa do estudo: em todas as cinco plataformas, e em
todas as páginas auditadas, há descumprimento de norma com hierarquia constitucional.

As vias de exigibilidade variam com a esfera: na federal, o controle externo cabe ao Tribunal de
Contas da União, somando-se o Ministério Público Federal, a ação civil pública e a via
orçamentária do art. 64 da Lei Brasileira de Inclusão; na estadual e na municipal, cabe aos
respectivos tribunais de contas, com o Ministério Público estadual e as ouvidorias como vias
complementares.

### 3.12 Série temporal diária

A série de dezessete dias produziu 85 varreduras e 340 tentativas de auditoria de página, das
quais 297 foram bem-sucedidas. Em 25 de agosto a falha do coletor descrita na subseção 3.2
impediu qualquer observação, e o dia consta sem veredito; restam dezesseis dias observados. Na
Figura 5, esse dia aparece como interrupção das linhas, e não como interpolação, porque ligar os
pontos por cima da lacuna desenharia continuidade que não foi observada.

**Figura 5** – Índice de conformidade acessível em série diária, por plataforma, 19 de agosto
a 4 de setembro de 2026
Fonte: elaboração própria.

**Três das cinco plataformas apresentaram variação nula** ao longo dos dezesseis dias
observados: índice idêntico e, mais significativo, conjunto de critérios violados idêntico,
respectivamente 5, 11 e 8 critérios, em todos os dias e nos dois perfis. Nenhuma barreira
apareceu, desapareceu ou se deslocou de página em duas semanas e meia, o que indica que a
barreira típica não está no conteúdo, e sim no *template*, no componente reaproveitado e na
ausência de verificação na homologação. As outras duas variaram, em direções opostas, conforme
a Tabela 5.

**Tabela 5** – Critérios de sucesso cuja violação mudou de estado na série diária

| Plataforma | Critério | Risco jurídico | 19 a 23/08 | 24 a 28/08 | 29/08 a 04/09 |
|---|---|---|---|---|---|
| Portal municipal de serviços | 2.1.1 Teclado | Crítico | Violado | Não violado | Violado |
| Portal federal de saúde | 1.1.1 Conteúdo não textual | Alto | Não violado | Violado | Violado |

Fonte: elaboração própria.

O episódio do critério 2.1.1 é delimitado nos dois extremos, e a ausência não é artefato de
amostragem: em 24, 26 e 28 as quatro auditorias diárias foram bem-sucedidas, de modo que a
barreira foi procurada onde estava e não foi encontrada. A evidência armazenada permite atribuir causa, e a atribuição é o ponto de maior interesse
metodológico. O elemento pertence a componente de engajamento fornecido por terceiro, um botão
de curtida embarcado na página, e nos cinco dias do episódio desapareceram juntos os três
achados que o tocavam, retornando juntos em 29 de agosto, enquanto o domínio do fornecedor
permaneceu entre os terceiros requisitados todos os dias: o script foi buscado, mas o componente
não se materializou no documento. A leitura consistente com a evidência é a de falha de renderização de
componente de terceiro, e não a de correção e regressão promovidas pelo órgão. O portal manteve
barreira absoluta em todos os dias do episódio, por outras violações críticas.

A violação do critério 1.1.1 no portal federal tem o sinal oposto: apareceu em 24 de agosto e
permaneceu nos onze dias observados subsequentes. A transição está ancorada em cobertura
integral dos dois lados, com o critério não violado em nenhuma das seis auditorias nos dias 6/6
anteriores e violado em todas as seis nos posteriores, o que descarta barreira que já existisse
e escapasse à amostra. Outros três critérios da mesma plataforma apareceram de forma esporádica
no fim de agosto e não reapareceram: reporta-se a ocorrência sem extrair dela interpretação.

#### 3.12.1 Disponibilidade ao longo da série

Excluído o dia sem veredito, a perda de páginas concentra-se em uma única plataforma: 21,9% no
portal federal de saúde, contra 0% no Meu SUS Digital, na secretaria estadual e na secretaria
municipal, e 3,1% no portal municipal de serviços, ao longo dos mesmos dezesseis dias e do
mesmo ponto de rede. As falhas do portal federal recaíram sobre dois caminhos específicos, a
página de secretaria finalística e o índice temático de saúde, enquanto a página inicial
falhou uma única vez em dezesseis dias.

A instabilidade da secretaria estadual documentada na subseção 3.4 foi episódica: sua perda
passou de 50% a 67% em 16 de agosto para 0% nos dezesseis dias da série, o que torna legítimo
adotar um dia de cobertura completa como bloco transversal.

---

## 4 Discussão

### 4.1 Principais achados

Dois achados organizam a discussão. O primeiro é de escala: dois critérios violados em 100% dos
endereços, nas três esferas, e barreira absoluta nas 20 páginas indicam falha estrutural do
ecossistema de desenvolvimento, e não deficiência isolada de um órgão; segue daí que corrigir
órgão a órgão tende a ser menos eficiente que atuar sobre padrões de componente e requisitos de
compra. O segundo é de tempo: três das cinco plataformas não variaram em nada ao longo de
dezesseis dias observados, enquanto duas mudaram. Juntos, sustentam a tese do trabalho, de que
a barreira típica é estrutural e persistente, mas não *todas* são, e distinguir umas das outras
exige repetição.

Um portal com conformidade de 80 pontos e uma barreira absoluta não é majoritariamente
acessível; é um portal que impede o uso por um grupo determinado. É o que separa este estudo dos
que reportam percentuais, e o que motiva as subseções seguintes.

### 4.2 O art. 63 como norma em branco

A remissão do art. 63 da Lei Brasileira de Inclusão às "melhores práticas e diretrizes de
acessibilidade adotadas internacionalmente" transforma um padrão técnico produzido por
consórcio privado em conteúdo de dever jurídico estatal. A construção tem três consequências
observáveis.

A atualização do padrão altera o conteúdo do dever sem alteração legislativa. O Modelo de
Acessibilidade em Governo Eletrônico funciona como vetor de concretização, mas é norma
administrativa cuja última versão de referência data de 2014, o que abre distância crescente em
relação ao padrão que pretende incorporar. E a divergência entre versões cria zona de
indeterminação, de que o critério 4.1.1 é exemplo documentado neste estudo: removido na versão
2.2 das diretrizes e acompanhado pelo motor de regras, permanece na referência normativa
brasileira. Descumpri-lo hoje é, ou não é, violação de dever jurídico? Da resposta depende a
exigibilidade concreta.

Há uma questão empírica embutida na construção, e a literatura brasileira já a formulou. Freire,
Castro e Fortes (2009) mediram os sítios estaduais ao longo de doze anos para verificar se o
prazo do Decreto 5.296/2004 produziria efeito observável, e encontraram avanço modesto. Quase
duas décadas depois, os resultados aqui obtidos (nível A violado em 78% dos casos, barreira
absoluta em todas as páginas) sugerem que a resposta continua a mesma: a norma existe, o efeito
mensurável não. É argumento a favor de deslocar a atenção da produção normativa para os
mecanismos de verificação e indução, tema da subseção 4.9. Segue daí, ainda, uma exigência que
extrapola este trabalho: se o conteúdo do dever é definido por remissão a padrão que evolui, a
ferramenta precisa declarar a versão do padrão que aplica, sob pena de tornar incomparáveis dois
relatórios sobre o mesmo portal.

### 4.3 Disponibilidade como precondição da acessibilidade

A disponibilidade é precondição da acessibilidade, e nenhum índice de conformidade a captura.
Um serviço de resultado de exame que responde de forma intermitente não é difícil de usar: para
quem tenta no minuto errado, é um serviço que não existe. Daí que a taxa de perda deva ser
desfecho reportado, e não incidente descartado em silêncio.

A verificação por múltiplos pontos acrescenta a exigência que é a contribuição metodológica mais
transferível deste trabalho. **Reportar perda de páginas só é informativo se a posição de rede do
observador for declarada**, porque uma mesma taxa significa indisponibilidade do serviço, se
medida de onde o cidadão está, ou política de rede do portal, se medida de outra posição. A
consequência atinge a proposta de auditoria continuada: executada em nuvem, como é natural para
monitoramento automatizado, ela reportaria indefinidamente como indisponíveis dois dos cinco
alvos, produzindo falso achado estável, robusto à repetição e indistinguível de um resultado
verdadeiro justamente por não variar. É a forma mais perigosa de erro em série temporal: a que a
consistência confirma.

### 4.4 O alcance do dever e a arquitetura de encaminhamento

Um padrão atravessa a verificação prévia dos alvos e não estava previsto no desenho: **o
cidadão que procura um serviço de saúde no portal oficial encontra, na maior parte das vezes,
um índice que aponta para outro lugar.** A seção de saúde do portal municipal é um arquivo de
notícias; o portal institucional estadual organiza-se por público e não oferece transação; e a
página de resultado de exame apresenta cinco cartões que encaminham a sistemas distintos, com
autenticação própria, entre os quais duas plataformas privadas. A caracterização é qualitativa,
e assim deve ser reportada.

Seguem daí duas consequências. A metodológica é que auditar o portal oficial não é auditar o
serviço: a conformidade medida descreve a camada de encaminhamento, e o ponto em que a tarefa é
concluída permanece atrás de autenticação e frequentemente em outro domínio, o que reforça a
leitura de que os índices constituem piso e não retrato. A jurídica é que a etapa final ocorrer
em plataforma privada não afasta o dever; desloca o sujeito obrigado. O art. 63 alcança os
sítios mantidos por empresas com sede ou representação comercial no País, de modo que o
prestador privado que entrega o resultado do exame está tão vinculado quanto a secretaria que o
contratou. **O dever segue o serviço, e não o domínio**, e a via do art. 64 alcança por isso o
arranjo contratual inteiro, e não apenas a página que ostenta o brasão.

### 4.5 Exclusão digital e exclusão por deficiência

O custo monetário de um acesso isolado é pequeno, e inflá-lo seria fabricar evidência. A força
do argumento está em três lugares, todos mensurados: a jornada completa, já que acompanhar um
agendamento não é ato único; a tentativa frustrada, porque cada barreira que obriga a repetir o
fluxo soma-se à conta, de modo que as duas dimensões auditadas se agravam mutuamente, e essa
interação é a contribuição original da medida; e o tráfego de terceiros, porque que quase 70% do
tráfego da seção de saúde do portal municipal se dirija a domínios alheios significa que o
cidadão custeia, da própria franquia, recursos estranhos ao serviço que foi buscar.

Dois mecanismos das ofertas comerciais reforçam a leitura. O primeiro reproduz, na infraestrutura
de acesso ao serviço público digital, o que Caplovitz (1963) descreveu no consumo de bens
duráveis por famílias de baixa renda: fracionar a recarga não é conveniência, é restrição de
fluxo de caixa, e custa 50% mais por unidade de dado. O segundo é a assimetria tarifária: a
oferta de entrada isenta um aplicativo privado de mensageria do consumo de franquia, e não
isenta o portal público de saúde.

A assimetria merece leitura à luz do art. 9º da Lei 12.965/2014 (Brasil, 2014b), que impõe ao
responsável pela transmissão o dever de tratar de forma isonômica os pacotes de dados, sem
distinção por conteúdo, serviço ou aplicação. Não cabe a este trabalho qualificar a licitude da
prática, que depende de análise regulatória própria; cabe registrar o efeito medido e a via de
correção que ele sugere, regulatória e não apenas técnica. Os dois mecanismos incidem sobre
população cuja conectividade já é precária por outras razões: nas classes D e E, apenas 3%
reúnem as condições do indicador de conectividade significativa (CGI.br, 2025). Somar a essa
base uma página de vários mebibytes é agravar restrição preexistente, e é sobre esse
agravamento, e não sobre o centavo isolado, que a discussão jurídica deve incidir.

Sustenta-se, com isso, que exclusão digital e exclusão por deficiência são barreiras de mesma
natureza jurídica: ambas obstruem o acesso ao direito, incidem sobre a mesma população
dependente do sistema público e encontram fundamento no art. 196 da Constituição combinado com
o art. 18 da Lei Brasileira de Inclusão. Reconheça-se, porém, que a tese sobre custo de dados é
de princípio, e não de regra, porque não há norma que fixe limite de peso de página: o argumento
é mais frágil que o ancorado em critério de sucesso, diferença que este trabalho declara em vez
de dissimular.

### 4.6 O perfil de exclusão e o que ele desloca

O debate público sobre acessibilidade digital organiza-se em torno do leitor de tela, e o perfil
de exclusão sugere outro arranjo: a maior carga recai sobre quem depende de estrutura semântica,
rotulagem consistente e linguagem previsível, que é o que se degrada primeiro quando a
acessibilidade é tratada como conformidade formal. A ressalva é que a atribuição de grupos a
cada critério é modelagem do instrumento, e não dado observado, de modo que o resultado sustenta
ordem de grandeza relativa, não estimativa populacional. Já a razão entre ocorrências e achados
distintos é diagnóstica de outro modo: as 80 ocorrências por achado no grupo de visão de cores
revelam defeito de sistema de design, cuja correção em um lugar resolveria centenas de
elementos, e é o tipo de achado que sugere onde a correção tem melhor relação entre custo e
efeito.

### 4.7 A periodicidade como parte do método

A série responde a uma objeção que a auditoria pontual não consegue formular: as barreiras
medidas são propriedade do portal ou do dia em que ele foi medido?

Para a maior parte do que se mediu, a resposta é inequívoca. Barreiras que sobrevivem a
dezesseis ciclos de publicação não são falha de conteúdo; estão no componente reutilizado e no
processo que o homologa sem verificar acessibilidade. Isso desloca o alvo da recomendação:
corrigir página é enxugar gelo, e o ponto de intervenção eficiente é o padrão de componente e o
requisito de contratação, argumento que a subseção 4.9 desenvolve.

Mas a resposta não é uniforme, e é aí que está a contribuição da série. Uma auditoria do portal
municipal em 26 de agosto não teria registrado a violação que uma auditoria de 30 de agosto
teria registrado; nenhuma das duas estaria errada sobre o instante, e ambas descreveriam mal o
portal. No portal federal o movimento foi o inverso, e a auditoria anterior a 24 de agosto teria
produzido retrato favorável de um portal que estava a um dia de piorar.

O episódio municipal traz um deslocamento de responsabilidade. O elemento pertencia a componente
de terceiro, e sua intermitência acompanhou a renderização do componente, não uma intervenção do
órgão: a acessibilidade do serviço variou por cinco dias sem que nada mudasse na conduta de quem
responde juridicamente por ela. O art. 63 não distingue código próprio de código embarcado, e
nem deveria, porque quem escolhe embarcar responde pelo que embarcou. Mas o órgão não pode
assegurar conformidade continuada por inspeção do próprio código, o que é argumento para
verificação contínua e contra auditoria de entrega. As duas trajetórias diferem, ainda, no que
se pode afirmar sobre duração: o episódio municipal está fechado e é mensurável, ao passo que a
regressão federal está censurada à direita, e o estudo estabelece um piso de onze dias
observados, não a duração.

A consequência interessa mais ao regime jurídico do que ao método. O dever do art. 63 é
continuado: o portal precisa ser acessível enquanto for oferecido, e não no dia da vistoria. Um
regime que produz um laudo por exercício mede uma amostra de tamanho um de um processo que
varia e cria o incentivo previsível de conformidade concentrada na data conhecida. A auditoria
contínua não é uma versão mais frequente da auditoria pontual; é o único desenho cuja unidade
de observação corresponde à estrutura temporal do dever que pretende verificar. Ela impõe, em
contrapartida, um requisito ao instrumento: como acumula dias em que a coleta falha, **"não
sei" precisa ser um valor representável**, distinto de "está conforme" e de "não está
conforme".

### 4.8 Limites do estudo

A **cobertura é parcial**: 27 dos 50 critérios admitem veredito automático, e apenas para alguns
modos de falha, valor coerente com o teto empírico da literatura (Vigo; Brown; Conway, 2013). As
**áreas autenticadas não foram auditadas**, o que deixa fora da amostra as telas de maior
consequência assistencial e torna os índices possivelmente otimistas.

A **amostra é pequena**: cinco portais em três estratos, com amostragem intencional que não
comporta inferência para o universo nacional. Os testes são descritivos, e a
**pseudorreplicação** (páginas do mesmo portal compartilham template e equipe) é mitigada pela
agregação por portal, não eliminada. A série não amplia a amostra de portais, e responde a
pergunta diferente, a de persistência.

A **série é curta e tem um único ponto no dia**. Dezessete dias detectam mudança, mas não
caracterizam sazonalidade nem alcançam variações intradiárias. Observou-se um único episódio de
barreira intermitente, o que basta para estabelecer que barreiras mudam, mas não com que
frequência. A atribuição de causa também fica fora do alcance do método, que constata a mudança
de estado sem distinguir correção revertida, variante servida por cache ou implantação parcial.
Verificou-se, por outro lado, que as camadas de consentimento de cookies não contaminam os
índices, já que nenhum critério é exclusivo do banner.

O **risco jurídico é atribuído por critério, e não por elemento**. Uma violação de operação por
teclado recebe classificação crítica esteja no botão que agenda a consulta ou em componente
periférico, e a série produziu esse segundo caso. A escolha é conservadora, porque decidir
automaticamente o que é periférico exigiria julgamento sobre a tarefa do usuário, mas sobrestima
a consequência assistencial de parte dos achados críticos; no conjunto da amostra o efeito é
limitado, porque as violações críticas são majoritariamente de campos e botões do caminho do
serviço.

Três limites menores completam a lista: o **preço do dado é parâmetro externo**, oferta
comercial que muda; os **critérios da versão 2.2 estão fora do escopo**, notadamente o de
tamanho do alvo de toque; e há **viés medido na sonda de legibilidade**, que superestima a
facilidade de leitura, erro na direção conservadora.

Acima de todos, permanece o limite estrutural do método: a auditoria automática não substitui a
avaliação com usuários reais de tecnologia assistiva. A evidência de que apenas metade dos
problemas efetivamente vividos por usuários cegos corresponde a critério de sucesso das
diretrizes (Power *et al.*, 2012) delimita o alcance de qualquer instrumento desta natureza,
inclusive deste. O que se propõe não é substituto da avaliação com usuários, e sim um mecanismo
de monitoramento contínuo, de baixo custo marginal, capaz de estabelecer um piso e de dirigi-lo
a quem tem competência para exigir correção.

### 4.9 Implicações para a política pública

Três implicações decorrem dos achados. A primeira é o subaproveitamento do art. 64 da Lei
Brasileira de Inclusão, que permite condicionar a aprovação de projetos e o financiamento
público à observância das regras de acessibilidade: a via orçamentária induz mais rápido que a
judicial e incide sobre o momento em que a barreira é criada, a contratação. A segunda é o valor
da auditoria contínua e pública como mecanismo de responsabilização, porque relatórios
acessíveis e endereçados ao gestor e ao órgão de controle mudam o destinatário da informação. A
terceira é a ausência de regulamentação do selo de acessibilidade digital previsto no art. 63,
§ 1º, que priva o sistema de mecanismo oficial de aferição e transfere a órgãos de controle uma
função que a lei previu como administrativa.

Cabe a ressalva que o próprio instrumento reproduz em todas as suas saídas: as proposições
jurídicas indicam fundamentos normativos aplicáveis segundo matriz documentada e contestável, e
não constituem parecer jurídico nem prova pericial. Sua adequação ao caso concreto depende de
análise profissional, que envolve elementos que nenhuma ferramenta verifica.

### 4.10 Trabalhos futuros

Quatro desdobramentos são prioritários: avaliação com usuários reais de tecnologia assistiva,
que nenhuma auditoria automática substitui; extensão da série diária, que dezessete dias apenas
inauguram, já que uma janela de meses permitiria estimar o tempo de permanência de uma barreira;
extensão a aplicativos móveis nativos; e modelo de efeitos mistos, com portal como efeito
aleatório e dia como medida repetida, para tratar formalmente a pseudorreplicação.

---

## 5 Considerações finais

Este trabalho desenvolveu, aferiu e aplicou um instrumento que produz, do mesmo dado, a
afirmação técnica e a proposição jurídica correspondente, com procedência auditável. A aferição
não produziu falsos positivos e detectou 18 das 20 barreiras plantadas, deixando fora do alcance
automático as que exigem julgamento semântico — evidência, produzida pelo próprio instrumento,
contra a leitura de que auditoria automática atesta acessibilidade.

Aplicado a cinco plataformas de saúde com incidência no Rio de Janeiro, encontrou 168 violações
confirmadas em 20 auditorias de página. Todas apresentaram barreira sem rota alternativa, e dois
critérios foram violados em todos os endereços, nas três esferas. Essa prevalência total, em
amostra estratificada, aponta falha estrutural do ecossistema e desloca a resposta adequada da
correção pontual para os padrões de desenvolvimento e os requisitos de contratação.

A série de dezessete dias converteu a auditoria contínua de desenho em resultado. Três
plataformas repetiram, dia após dia, o mesmo conjunto de critérios violados, o que caracteriza a
barreira típica como estrutural, e não circunstancial; duas mudaram, uma delas por componente de
terceiro embarcado, sem que nada mudasse na conduta do órgão. A conclusão não é sobre esses
portais, e sim sobre o método: como o dever do art. 63 é continuado, uma verificação que produz
um laudo por exercício mede uma amostra de tamanho um de um processo que varia.

A contribuição metodológica que se pretende oferecer é menos o valor de qualquer índice do que
quatro exigências que o instrumento incorpora e que a literatura frequentemente dispensa:
declarar a cobertura em toda saída; jamais converter veredito indeterminado em violação; jamais
converter ausência de observação em conformidade, mantendo o "não sei" como valor
representável; e vincular cada achado a um dispositivo determinado, com sujeito obrigado e via
de exigibilidade.

Permanece intransponível, por construção, o limite de que nenhum instrumento automático
substitui a avaliação com as pessoas que a barreira exclui.

---

## Referências

ALAJARMEH, Nancy. Evaluating the accessibility of public health websites: an exploratory
cross-country study. **Universal Access in the Information Society**, Berlin, v. 21, n. 3,
p. 771-789, 2021. DOI: https://doi.org/10.1007/s10209-020-00788-7.

ANATEL — AGÊNCIA NACIONAL DE TELECOMUNICAÇÕES. **Panorama econômico-financeiro do setor de
telecomunicações**: 1º trimestre de 2026. Brasília, DF: Anatel, 2026.

BARROS, Ygor Santos; OUTÃO, Juliana Carvalho Silva do; SACRAMENTO, Carolina; FERREIRA, Simone
Bacellar Leal; PIMENTEL, Mariano Gomes; SANTOS, Rodrigo Pereira dos. Avaliação de
acessibilidade da plataforma Gov.br por ferramentas automatizadas. In: LATIN AMERICAN
SYMPOSIUM ON DIGITAL GOVERNMENT, 12., 2024. **Anais** [...]. Porto Alegre: Sociedade
Brasileira de Computação, 2024. p. 50-61. DOI: https://doi.org/10.5753/wcge.2024.2282.

BRAJNIK, Giorgio. Validity and reliability of web accessibility guidelines. In: INTERNATIONAL
ACM SIGACCESS CONFERENCE ON COMPUTERS AND ACCESSIBILITY, 11., 2009, Pittsburgh.
**Proceedings** [...]. New York: ACM, 2009. p. 131-138. DOI:
https://doi.org/10.1145/1639642.1639666.

BRASIL. [Constituição (1988)]. **Constituição da República Federativa do Brasil de 1988**.
Brasília, DF: Presidência da República, [2024]. Disponível em:
http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao.htm. Acesso em: 16 ago. 2026.

BRASIL. **Decreto nº 5.296, de 2 de dezembro de 2004**. Regulamenta as Leis nº 10.048, de 8
de novembro de 2000, e nº 10.098, de 19 de dezembro de 2000. **Diário Oficial da União**:
seção 1, Brasília, DF, 3 dez. 2004.

BRASIL. **Decreto nº 6.949, de 25 de agosto de 2009**. Promulga a Convenção Internacional
sobre os Direitos das Pessoas com Deficiência e seu Protocolo Facultativo. **Diário Oficial da
União**: seção 1, Brasília, DF, 26 ago. 2009.

BRASIL. **Lei nº 12.527, de 18 de novembro de 2011**. Regula o acesso a informações previsto
no inciso XXXIII do art. 5º, no inciso II do § 3º do art. 37 e no § 2º do art. 216 da
Constituição Federal. **Diário Oficial da União**: seção 1, edição extra, Brasília, DF, 18
nov. 2011.

BRASIL. **Lei nº 12.965, de 23 de abril de 2014**. Estabelece princípios, garantias, direitos
e deveres para o uso da internet no Brasil. **Diário Oficial da União**: seção 1, Brasília,
DF, 24 abr. 2014b.

BRASIL. Ministério do Planejamento, Orçamento e Gestão. **eMAG**: Modelo de Acessibilidade em
Governo Eletrônico. Versão 3.1. Brasília, DF: MPOG, 2014a. Disponível em:
https://emag.governoeletronico.gov.br/. Acesso em: 16 ago. 2026.

BRASIL. **Lei nº 13.146, de 6 de julho de 2015**. Institui a Lei Brasileira de Inclusão da
Pessoa com Deficiência (Estatuto da Pessoa com Deficiência). **Diário Oficial da União**:
seção 1, Brasília, DF, 7 jul. 2015.

CAPLOVITZ, David. **The poor pay more**: consumer practices of low-income families. New York:
The Free Press of Glencoe, 1963.

CGI.BR — COMITÊ GESTOR DA INTERNET NO BRASIL. **Pesquisa sobre o uso das tecnologias de
informação e comunicação nos domicílios brasileiros**: TIC Domicílios 2024. São Paulo:
CGI.br; NIC.br; Cetic.br, 2025. Disponível em: https://cetic.br/pt/pesquisa/domicilios/.
Acesso em: 16 ago. 2026.

FREIRE, André Pimenta; CASTRO, Mário de; FORTES, Renata Pontin de Mattos. Acessibilidade dos
sítios web dos governos estaduais brasileiros: uma análise quantitativa entre 1996 e 2007.
**Revista de Administração Pública**, Rio de Janeiro, v. 43, n. 2, p. 395-414, 2009. DOI:
https://doi.org/10.1590/S0034-76122009000200006.

HTTP ARCHIVE. **Web Almanac**: HTTP Archive's annual state of the web report. [S. l.]: HTTP
Archive, 2025. Disponível em: https://almanac.httparchive.org/. Acesso em: 10 ago. 2026.

IBGE — INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA. **Censo demográfico 2022**: pessoas
com deficiência — resultados preliminares da amostra. Rio de Janeiro: IBGE, 2025. Disponível
em: https://www.ibge.gov.br/. Acesso em: 16 ago. 2026.

POWER, Christopher; FREIRE, André; PETRIE, Helen; SWALLOW, David. Guidelines are only half of
the story: accessibility problems encountered by blind users on the web. In: SIGCHI CONFERENCE
ON HUMAN FACTORS IN COMPUTING SYSTEMS, 2012, Austin. **Proceedings** [...]. New York: ACM,
2012. p. 433-442.

SILVA, Rosane Leal da; LA RUE, Letícia Almeida de. A acessibilidade nos sites do Poder
Executivo estadual à luz dos direitos fundamentais das pessoas com deficiência. **Revista de
Administração Pública**, Rio de Janeiro, v. 49, n. 2, p. 315-339, 2015. DOI:
https://doi.org/10.1590/0034-7612130130.

SIMÃO, João Batista; RODRIGUES, Georgete. Acessibilidade às informações públicas: uma
avaliação do portal de serviços e informações do governo federal. **Ciência da Informação**,
Brasília, DF, v. 34, n. 2, p. 234-245, 2005. DOI:
https://doi.org/10.1590/S0100-19652005000200009.

VIEIRA, Camila Mugnai; CANIATO, Daniela Godoi; YONEMOTU, Bruna Prado Ribeiro. Comunicação e
acessibilidade: percepções de pessoas com deficiência auditiva sobre seu atendimento nos
serviços de saúde. **RECIIS**, Rio de Janeiro, v. 11, n. 2, 2017. DOI:
https://doi.org/10.29397/reciis.v11i2.1139.

VIGO, Markel; BROWN, Justin; CONWAY, Vivienne. Benchmarking web accessibility evaluation
tools: measuring the harm of sole reliance on automated tests. In: INTERNATIONAL
CROSS-DISCIPLINARY CONFERENCE ON WEB ACCESSIBILITY, 10., 2013, Rio de Janeiro.
**Proceedings** [...]. New York: ACM, 2013. DOI: https://doi.org/10.1145/2461121.2461124.

W3C — WORLD WIDE WEB CONSORTIUM. **Web Content Accessibility Guidelines (WCAG) 2.1**. W3C
Recommendation, 5 jun. 2018. Disponível em: https://www.w3.org/TR/WCAG21/. Acesso em: 16 ago.
2026.
