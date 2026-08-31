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
sua inacessibilidade deixa de ser problema de usabilidade para tornar-se restrição de
direito. Este estudo desenvolveu, validou e aplicou um instrumento de auditoria algorítmica
que converte falhas técnicas de acessibilidade em proposições jurídicas fundamentadas na Lei
Brasileira de Inclusão. Foi aferido contra conjunto de referência com barreiras conhecidas e
aplicado a cinco plataformas de saúde do Rio de Janeiro, estratificadas por esfera
federativa, em dois perfis de dispositivo, com medições repetidas e com série diária de treze
dias consecutivos. Realizaram-se vinte auditorias de página no corte transversal, dezesseis
bem-sucedidas, com 125 violações confirmadas. Todas as páginas apresentaram ao menos uma
barreira crítica, sem rota alternativa, e o critério relativo a nome, função e valor dos
componentes de interface foi violado em todas elas. Observou-se gradiente entre esferas
federativas. Na série diária, três plataformas não apresentaram variação alguma, ao passo que
em duas houve mudança: uma barreira crítica de operação por teclado desapareceu por quatro
dias e retornou, e uma violação de alternativa textual foi introduzida e não corrigida —
evidência de que a periodicidade da verificação é parte do método. A auditoria automática
estabelece um piso de não conformidade e sustenta qualificação jurídica auditável.

**Palavras-chave:** Pessoas com Deficiência; Acesso aos Serviços de Saúde; Saúde Digital;
Direito à Saúde; Exclusão Digital.

## Abstract

Digital platforms have become the preferred channel for accessing public health services, and
their inaccessibility shifts from a usability problem to a restriction of a right. This study
developed, validated and applied an algorithmic auditing instrument that converts technical
accessibility failures into legal propositions grounded in the Brazilian Inclusion Law. It
was assessed against a reference set with known barriers and applied to five health platforms
in Rio de Janeiro, stratified by federative level, under two device profiles, with repeated
measurements and a thirteen-day daily series. Twenty page audits were carried out in the
cross-sectional block, sixteen of them successful, yielding 125 confirmed violations. Every
page presented at least one critical barrier, with no alternative route, and the criterion
concerning name, role and value of interface components was violated in all of them. A
gradient across federative levels was observed. In the daily series, three platforms showed no
variation at all, while two changed: a critical keyboard-operation barrier disappeared for
four days and returned, and a text-alternative violation was introduced and left uncorrected —
evidence that the periodicity of verification is part of the method. Automated auditing
establishes a floor of non-compliance and supports auditable legal qualification.

**Keywords:** Persons with Disabilities; Health Services Accessibility; Digital Health; Right
to Health; Digital Divide.

## Resumen

Las plataformas digitales son la vía preferente de acceso a servicios públicos de
salud, y su inaccesibilidad deja de ser un problema de usabilidad para volverse una
restricción de derecho. Este estudio desarrolló, validó y aplicó un instrumento de auditoría
algorítmica que convierte fallas técnicas de accesibilidad en proposiciones jurídicas
fundamentadas en la Ley Brasileña de Inclusión. Fue verificado con un conjunto de referencia
con barreras conocidas y aplicado a cinco plataformas de salud de Río de Janeiro,
estratificadas por esfera federativa, en dos perfiles de dispositivo, con mediciones repetidas
y una serie diaria de trece días consecutivos. Se realizaron veinte auditorías de página en el
corte transversal, dieciséis exitosas, con 125 violaciones confirmadas. Todas presentaron al
menos una barrera crítica, sin ruta alternativa, y el criterio sobre nombre, función y valor de
los componentes de interfaz fue violado en todas. Se observó gradiente entre esferas
federativas. En la serie diaria, tres plataformas no presentaron variación alguna, mientras que
dos cambiaron: una barrera crítica de operación por teclado desapareció durante cuatro días y
retornó, y una violación de alternativa textual fue introducida y no corregida — evidencia de
que la periodicidad de la verificación es parte del método. La auditoría automática establece
un piso de incumplimiento y sostiene calificación jurídica auditable.

**Palabras clave:** Personas con Discapacidad; Accesibilidad a los Servicios de Salud; Salud
Digital; Derecho a la Salud; Brecha Digital.

---

## 1 Introdução

### 1.1 O deslocamento do acesso

Quando um serviço público de saúde migra para o meio digital, a acessibilidade da interface
deixa de ser questão de usabilidade e passa a ser condição de exercício de um direito. A
formulação não é retórica. Se o botão que confirma o agendamento de uma consulta não recebe
foco do teclado, a pessoa com deficiência motora não tem uma experiência ruim: não tem
consulta. Se o controle que abre o resultado de um exame não expõe nome acessível, a pessoa
cega que usa leitor de tela não enfrenta uma dificuldade adicional: para ela, aquele controle
não existe.

O art. 196 da Constituição Federal estabelece a saúde como direito de todos e dever do
Estado, garantido mediante políticas que assegurem acesso universal e igualitário às ações e
serviços (Brasil, 1988). Quando o Estado elege o canal digital como via preferencial — ou
única — de determinado serviço, a acessibilidade desse canal incorpora-se ao conteúdo do
dever constitucional com a mesma força com que a rampa se incorpora ao dever de acesso físico
à unidade de saúde. A digitalização não cria um serviço novo, sujeito a regime próprio:
transporta um serviço existente para um meio em que as barreiras mudam de natureza, mas não
de consequência jurídica.

A Lei Brasileira de Inclusão (Brasil, 2015) fornece o elo entre o dever constitucional e o
padrão técnico. Seu art. 63, caput, torna obrigatória a acessibilidade nos sítios da internet
mantidos por órgãos de governo, "conforme as melhores práticas e diretrizes de acessibilidade
adotadas internacionalmente". O dispositivo é, tecnicamente, uma norma em branco: o
legislador não descreveu o padrão, incorporou-o por remissão. No arranjo brasileiro, essa
remissão se concretiza pelo Modelo de Acessibilidade em Governo Eletrônico (Brasil, 2014a),
construído sobre as diretrizes do World Wide Web Consortium, e pelo art. 47 do Decreto
5.296/2004 (Brasil, 2004), que já determinava acessibilidade obrigatória nos portais da
administração pública.

### 1.2 A lacuna

Três literaturas se aproximam do problema sem convergir.

A primeira, de avaliação técnica de conformidade, é a mais desenvolvida e tem no Brasil
percurso de duas décadas. Simão e Rodrigues (2005) avaliaram o portal federal de serviços e
informações e já registravam barreiras para o cidadão com deficiência. Freire, Castro e Fortes
(2009) produziram o estudo longitudinal mais consequente da série: mediram 1.232 páginas dos
27 sítios estaduais entre 1996 e 2007 e verificaram avanço modesto, ainda distante das
diretrizes internacionais, mesmo após o prazo de conformidade fixado pelo Decreto 5.296/2004.
O achado é decisivo para o presente trabalho, porque converte uma questão doutrinária em
questão empírica: a existência da norma não produziu, por si, efeito mensurável. Silva e La
Rue (2015) examinaram oito portais do Executivo estadual à luz dos direitos fundamentais das
pessoas com deficiência e concluíram que nenhum atendia integralmente aos critérios mínimos.
Mais recentemente, Barros *et al.* (2024) avaliaram a plataforma centralizada do governo
federal por três ferramentas automatizadas e concluíram que o portal não atende a requisitos
mínimos de acessibilidade. Fora do país, Alajarmeh (2021) auditou os sítios oficiais de saúde
pública de 25 países durante a pandemia e encontrou apenas três aprovados em todos os testes
aplicados, com predomínio de violações dos princípios perceptível e operável — a mesma
distribuição que este estudo encontrará.

São trabalhos descritivos, úteis e convergentes no diagnóstico, mas com três fragilidades
recorrentes. Raramente declaram a cobertura da ferramenta empregada, isto é, a fração dos
critérios normativos que ela é capaz de verificar, o que torna qualquer percentual de
conformidade um número sobre denominador oculto. Quase nunca reportam a perda de páginas na
coleta, tratando-a como incidente e não como dado. E não qualificam juridicamente o achado, de
modo que o relatório se dirige ao desenvolvedor, e não ao gestor ou ao órgão de controle.

A segunda literatura examina a validade das próprias diretrizes e a capacidade das
ferramentas de operacionalizá-las. Brajnik (2009) mostrou que critérios anunciados como
testáveis apresentam variação relevante entre avaliadores. Vigo, Brown e Conway (2013)
compararam seis ferramentas de avaliação automática e encontraram cobertura de, no máximo,
50% dos critérios de sucesso, com completude entre 14% e 38% — resultado que estabelece um
teto empírico para qualquer afirmação de conformidade baseada apenas em automação. Power
*et al.* (2012), a partir de 1.383 instâncias de problema encontradas por 32 usuários cegos
em 16 sítios, verificaram que apenas 50,4% dos problemas vividos correspondiam a algum
critério de sucesso das diretrizes. As duas conclusões, somadas, delimitam o alcance legítimo
do método automático: ele mede uma parte da norma, e a norma cobre uma parte da experiência.

A terceira literatura, situada no campo da comunicação e informação em saúde, examina a
barreira comunicacional no próprio serviço. Vieira, Caniato e Yonemotu (2017) descreveram as
percepções de pessoas com deficiência auditiva sobre o atendimento recebido e mostraram que a
barreira de comunicação opera dentro do serviço de saúde, e não apenas no acesso a ele.
Deslocada para o canal digital, essa barreira muda de forma e conserva a natureza — e é
precisamente esse deslocamento que carece de instrumento de medida.

A literatura jurídica sobre o art. 63 da Lei Brasileira de Inclusão, por fim, analisa o
dispositivo em chave doutrinária, sem instrumento de mensuração: discute-se o alcance do
dever sem produzir evidência sobre seu descumprimento.

A lacuna que este trabalho endereça está na articulação: não há instrumento que produza, do
mesmo dado e com procedência auditável, a afirmação técnica e a proposição jurídica
correspondente — indicando qual dispositivo foi violado, quem é o sujeito obrigado e por qual
via a obrigação é exigível.

### 1.3 O usuário periférico

A barreira de acesso ao serviço público digital de saúde não é apenas sensorial. Plano
pré-pago, aparelho de entrada, rede instável e escolaridade heterogênea produzem obstrução do
acesso com o mesmo efeito prático da barreira de acessibilidade clássica, e frequentemente na
mesma pessoa. O peso de uma página, medido em bytes efetivamente trafegados, é uma barreira
que as diretrizes de acessibilidade não enxergam, porque pressupõem um usuário que já chegou.

Os dados disponíveis sustentam a sobreposição. O Censo 2022 identificou 14,4 milhões de
pessoas com deficiência no país, 7,3% da população de dois anos ou mais; entre elas, a taxa de
analfabetismo era de 21,3%, quatro vezes a das pessoas sem deficiência, e apenas 7,4% haviam
concluído o ensino superior, contra 19,5% (IBGE, 2025). A pesquisa TIC Domicílios 2024, por
sua vez, mostra que a internet está presente em 68% dos domicílios das classes D e E, contra a
totalidade dos da classe A, e que apenas 3% das pessoas dessas classes reúnem as condições do
indicador de conectividade significativa — que combina custo, velocidade, banda larga fixa e
acesso por mais de um dispositivo —, contra 73% na classe A; entre quem tem telefone celular
nas classes D e E, 86% acessam a rede exclusivamente por esse aparelho (CGI.br, 2025).

Escolaridade mais baixa, conectividade precária e dependência exclusiva do aparelho móvel
não são variáveis de contexto: são as condições concretas em que a interface do serviço
público de saúde é efetivamente usada — e são, também, exatamente as condições que a
homologação em desktop, com banda larga e alta escolaridade presumida, deixa de simular.

Este estudo adota a expressão *usuário periférico* para designar essa posição composta —
quem depende exclusivamente do sistema público de saúde e acede a ele por meio de
infraestrutura de conectividade precária. A categoria não substitui a de pessoa com
deficiência: sobrepõe-se a ela, e o trabalho mede as duas dimensões separadamente, porque têm
fundamentos jurídicos distintos e correções distintas.

### 1.4 Objetivos

**Objetivo geral.** Desenvolver, validar e aplicar um instrumento de auditoria contínua que
converta falhas técnicas de acessibilidade em proposições jurídicas fundamentadas.

**Objetivos específicos.** (1) Modelar a correspondência entre os 50 critérios de sucesso de
níveis A e AA das diretrizes de acessibilidade para conteúdo web, versão 2.1 (W3C, 2018), e
o ordenamento jurídico brasileiro; (2) construir e aferir o instrumento contra um conjunto de referência com
barreiras conhecidas; (3) aplicá-lo a plataformas de saúde com incidência no Rio de Janeiro,
estratificadas por esfera federativa; (4) quantificar o custo de acesso em dados móveis como
barreira; (5) caracterizar o perfil de exclusão por grupo de pessoas afetado.

---

## 2 Metodologia

### 2.1 Desenho do estudo

Estudo observacional de auditoria algorítmica, estratificado por esfera federativa, com dois
componentes. O componente **transversal** compara plataformas entre si em uma janela de
medição. O componente **longitudinal** repete a mesma auditoria, com a mesma configuração, em
dias sucessivos, e é o que permite distinguir barreira persistente de barreira transitória —
distinção que a auditoria pontual, por construção, não pode fazer, e sem a qual a proposta de
auditoria *contínua* seria apenas uma promessa de arquitetura.

A unidade de observação é a página web em um perfil de dispositivo, em um dia; a unidade de
análise é o achado de auditoria; a unidade de comparação entre instituições é a plataforma.
A distinção entre as três é necessária e é frequentemente colapsada na literatura da área,
com consequências que a subseção 2.7 detalha.

### 2.2 População, amostra e conduta de coleta

A população é o conjunto de plataformas digitais de saúde pública com incidência no município
e no estado do Rio de Janeiro. A amostragem foi intencional, estratificada por esfera
federativa (federal, estadual, municipal) e por natureza do serviço (informacional,
transacional). A escolha se justifica porque a população é pequena e conhecida e porque o
interesse é comparar estratos de gestão, não estimar parâmetro populacional. A justificativa
de inclusão de cada alvo consta do catálogo versionado do instrumento.

As páginas auditadas foram declaradas explicitamente, e não descobertas por rastreamento
automático: a descoberta automática produz amostra não reproduzível, porque o conjunto de
links muda a cada publicação de conteúdo. Fixou-se teto de 25 páginas por plataforma, por
razão ética — carga sobre servidores públicos — e metodológica — comparabilidade entre
portais de tamanhos distintos.

A conduta de coleta observou o arquivo `robots.txt` de cada origem, intervalo mínimo de 2.000
milissegundos entre requisições e identificação da pesquisa no campo `User-Agent`. O
instrumento lê o documento renderizado de páginas públicas: não preenche formulários, não
autentica e não transmite dados. Áreas autenticadas foram excluídas e reportadas como lacunas
declaradas da amostra.

A **janela de coleta** compreendeu dois blocos, declarados aqui porque o segundo é condição
do componente longitudinal. O bloco transversal ocorreu em 16 e 19 de agosto de 2026, com
medições repetidas em intervalo de minutos, e sustenta os resultados das subseções 3.1 a 3.11.
O bloco longitudinal ocorreu entre **19 e 31 de agosto de 2026**, em treze dias consecutivos,
por tarefa agendada disparada diariamente entre 12h20 e 12h25 em tempo universal coordenado
(9h20 a 9h25 no horário de Brasília), sempre com a mesma configuração e a mesma lista de
páginas. O horário fixo é decisão metodológica: variação de horário confundiria mudança do
portal com variação de carga do servidor ao longo do dia. Produziram-se 65 varreduras e 260
tentativas de auditoria de página, das quais 219 foram bem-sucedidas.

### 2.3 Perfis de dispositivo

Adotaram-se dois perfis, por decisão metodológica e não técnica. O perfil `mobile-320` (320 ×
640 pixels, densidade 2, agente de aparelho de entrada) corresponde à largura mínima exigida
pelo critério 1.4.10 e aproxima o aparelho predominante entre usuários de menor renda. O
perfil `desktop-1366` (1366 × 768) corresponde à resolução de desktop mais comum no país e ao
ambiente em que os portais costumam ser homologados. O contraste entre os dois é, por si, um
resultado do estudo.

### 2.4 A matriz de correspondência normativa

A contribuição central do instrumento é a matriz que vincula cada critério de sucesso a
dispositivos do ordenamento brasileiro, em três camadas cumulativas.

A **camada geral** incide sobre qualquer barreira e reúne o art. 63, caput, da Lei Brasileira
de Inclusão; o art. 3º, IV, "d", que tipifica as barreiras nas comunicações e na informação;
o art. 4º, sobre igualdade e não discriminação; o art. 47 do Decreto 5.296/2004; e o Modelo
de Acessibilidade em Governo Eletrônico.

A **camada de saúde** incide sobre todos os alvos deste estudo e acrescenta o art. 18 da Lei
Brasileira de Inclusão, sobre atenção integral à saúde da pessoa com deficiência; o art. 196
da Constituição; e o art. 25 da Convenção Internacional sobre os Direitos das Pessoas com
Deficiência, promulgada pelo Decreto 6.949/2009 (Brasil, 2009) com status de emenda
constitucional.

A **camada específica** varia conforme a natureza da barreira e acrescenta, por exemplo, o
art. 74 da Lei Brasileira de Inclusão quando há dependência de tecnologia assistiva; o art.
8º, § 3º, VIII, da Lei de Acesso à Informação (Brasil, 2011) quando se trata de transparência
ativa; e o art. 9 da Convenção quando a barreira é absoluta, isto é, quando não há rota
alternativa acessível. Essa terceira camada evita o vício, comum na literatura, de invocar o
mesmo bloco de dispositivos para toda e qualquer falha, o que dilui a força argumentativa e
impede graduar a gravidade.

O risco jurídico de cada critério foi graduado pela combinação de três vetores —
essencialidade do serviço obstruído, existência de rota alternativa e reversibilidade do dano
— em quatro faixas, com os pesos empregados nos índices: crítico (peso 12; 4 critérios), alto
(peso 7; 18), moderado (peso 3; 19) e baixo (peso 1; 9). A escala é independente da gravidade
técnica atribuída pelo motor de regras, e ambas são reportadas. A matriz cobre os 50 de 50
critérios do escopo, e a completude é verificada por teste automatizado.

### 2.5 Instrumento

O instrumento executa o navegador Chromium por automação, aplica sobre o documento
renderizado o motor de regras `axe-core` na versão 4.13.0, vendorizada para garantir
reprodutibilidade, e acrescenta 16 sondas próprias que cobrem 18 critérios e duas dimensões
sem correspondência normativa. O recorte de regras restringiu-se às marcações `wcag2a`,
`wcag2aa`, `wcag21a` e `wcag21aa`; a categoria de boas práticas foi excluída, porque
recomendação sem lastro normativo não sustenta afirmação de violação legal.

Dois achados metodológicos emergiram da construção das sondas e merecem registro, por
afetarem qualquer estudo que empregue o mesmo motor. O primeiro: o `axe-core` aceita o
atributo `placeholder` como nome acessível válido. Como esse é o padrão mais comum nos
formulários de agendamento dos portais públicos brasileiros, a omissão tornaria a auditoria
cega precisamente na tela de maior consequência assistencial. O segundo: o critério 4.1.1 foi
removido na versão 2.2 das diretrizes, e o motor acompanhou a norma técnica, enquanto a
referência normativa brasileira permanece na versão 2.1. Trata-se de caso em que a ferramenta
de referência e a norma de referência divergem, e a opção adotada foi seguir a norma que rege
o objeto.

### 2.6 Índices

Contar violações produz três vieses, cada um suficiente para invalidar comparações entre
portais. O **viés de template**: uma página com 400 links sem nome acessível recebe 400
ocorrências, mas tem um defeito — o componente de link do sistema de design. O **viés de
equivalência**: somar uma falha de declaração de idioma com uma armadilha de teclado supõe que
ambas pesam igual. E o **viés de cobertura**, já discutido na subseção 1.2. Construíram-se,
por isso, quatro indicadores.

O **Índice de Conformidade de Acessibilidade** (ICA) é dado por
ICA = 100 × (1 − Σ*w*(*c*) para *c* violado ⁄ Σ*w*(*c*) para *c* verificável), em que *w*(*c*)
é o peso do risco jurídico do critério. O denominador contém apenas os critérios com veredito
automático possível, e a razão entre eles e o total (27/50 = 0,54) acompanha todo índice
publicado, sob o rótulo de cobertura.

O **Índice de Atrito de Navegação** (IAN) agrega, por achado, o produto do peso técnico, do
peso jurídico e de log₂(1 + ocorrências), multiplicado por 1,5 nas páginas de fluxo essencial
declarado, e satura por IAN = 100 × (1 − *e*^(−atrito⁄κ)). O amortecimento logarítmico corrige
o viés de template: cem elementos com o mesmo defeito pesam 6,7 vezes um, e não cem vezes. A
saturação exponencial mantém o índice limitado e comparável entre portais de tamanhos
distintos.

O **Índice de Exposição Jurídica** (IEJ) tem a mesma forma funcional, ignora o peso técnico e
descarta os achados de risco baixo — passivo jurídico não se mede por irregularidade formal,
e sim por obstrução efetiva de direito.

O **sinalizador de barreira absoluta** é booleano e indica a presença de violação de risco
crítico. Não é um índice, e é o mais importante: um portal pode ter conformidade alta e ser
inutilizável por uma única armadilha de teclado. Nenhum índice contínuo distingue "difícil" de
"impossível", razão pela qual o sinalizador precede qualquer número em todas as saídas.

O custo de acesso foi calculado como o produto do peso da página, em mebibytes efetivamente
trafegados, pelo preço do dado móvel, e expresso também como fração da franquia mensal. Os
parâmetros foram coletados e datados: R$ 3,00 por gibibyte (oferta pré-paga de R$ 15,00 por
5 GB em 15 dias, consultada em 10 de agosto de 2026); franquia de 10 gibibytes mensais; e
limiar de página onerosa de 2,5 mebibytes, correspondente ao peso mediano móvel reportado
pelo *Web Almanac* (HTTP Archive, 2025). Os três parâmetros são conservadores frente aos
dados setoriais oficiais, que apontam preço efetivo médio superior e receita média por usuário
pré-pago inferior à franquia adotada (Anatel, 2026): a estimativa erra para menos.

Todos os parâmetros que afetam número publicável são serializados junto de cada varredura, de
modo que nenhum resultado dependa de constante implícita no código.

### 2.7 Análise estatística

Empregou-se estatística não paramétrica, por assimetria conhecida das distribuições de
índices de acessibilidade: teste de Mann-Whitney para dois grupos, com δ de Cliff como
tamanho de efeito, e teste de Kruskal-Wallis para três ou mais, com ε². Intervalos de
confiança por *bootstrap* percentílico, com 10.000 reamostragens e semente fixa. O tamanho de
efeito é reportado sempre, ao lado do valor-p: com poucas instituições por estrato, um p
pequeno pode acompanhar diferença irrelevante e um p grande pode esconder diferença
substantiva por falta de potência.

Duas ameaças à validade foram declaradas no desenho e não apenas na discussão. A
**pseudorreplicação**: páginas do mesmo portal compartilham template, equipe e decisões de
projeto, e não são observações independentes; tratá-las como tal infla o *n* e produz
significância espúria. A mitigação adotada foi reportar as comparações entre esferas também
em nível de portal, com uma observação por plataforma, e apresentar a análise por página como
descritiva. A **potência insuficiente**: os resultados são formulados como ausência de
diferença detectável, nunca como igualdade entre grupos.

As hipóteses são exploratórias e assim devem ser lidas — o desenho não comporta confirmação.
Formularam-se quatro: gradiente de conformidade entre esferas federativas (H1); maior atrito
em serviços transacionais que em informacionais (H2); barreiras reveladas exclusivamente pelo
perfil móvel (H3); e associação positiva entre peso da página e participação de tráfego de
terceiros (H4).

### 2.8 Validação do instrumento

Antes de qualquer afirmação sobre portais reais, o instrumento foi aferido contra um conjunto
de referência composto por cinco páginas sintéticas, servidas localmente, com verdade
declarada em manifesto versionado. O conjunto inclui um controle negativo — página construída
em conformidade — e um controle positivo com 20 barreiras plantadas, cada uma anotada com o
critério que deveria ser detectado.

O parâmetro de saturação κ do índice de atrito foi determinado empiricamente por esse
conjunto, e não escolhido *a priori*. O valor inicialmente estimado (κ = 40) foi rejeitado
pela aferição: com ele, quatro das cinco páginas de referência pontuavam acima de 98 e uma
única falha séria já marcava 65, de modo que o índice deixava de distinguir "ruim" de
"inutilizável" — exatamente a distinção que ele existe para fazer. A recalibração fixou
κ = 150.

### 2.9 Reprodutibilidade e ética

Cada varredura carrega o registro completo de configuração, incluindo versões do navegador,
do motor de regras e do próprio instrumento, além da data e hora da coleta. O motor de regras
está vendorizado em versão fixa e o catálogo de alvos é versionado. O código e os dados
primários estão depositados em repositório público sob licença livre, cujo endereço será
informado após a avaliação por pares, em razão da política de avaliação cega.

O estudo não envolveu seres humanos nem dados pessoais: a coleta se restringiu ao documento
renderizado de páginas públicas, sem autenticação, sem preenchimento de formulário e sem
transmissão de dados. Não houve, portanto, submissão a comitê de ética em pesquisa, nos
termos da Resolução 510/2016 do Conselho Nacional de Saúde. A conduta de coleta observou os
limites descritos na subseção 2.2.

---

## 3 Resultados

### 3.1 Aferição do instrumento

Contra o conjunto de referência, o instrumento não produziu nenhum falso positivo na página
construída em conformidade e detectou 18 dos 20 critérios distintos plantados no controle
positivo. A cobertura declarada — critérios com veredito automático possível — é de 27 dos 50
critérios do escopo, ou 54%.

As três barreiras que permaneceram fora do alcance automático estão descritas na Tabela 1.

**Tabela 1** – Barreiras plantadas não detectáveis por verificação automática e julgamento
exigido

| Critério | Barreira plantada | Julgamento exigido |
|---|---|---|
| 1.4.1 Uso de cor | Situação da consulta indicada apenas por círculo colorido | A cor é o único portador do sentido? |
| 2.4.2 Página com título | Título da página definido como "Documento1" | O título existe; é descritivo? |
| 2.4.4 Finalidade do link | Quatro links com o texto "clique aqui" | O texto existe; descreve o destino? |

Fonte: elaboração própria.

O resultado não é uma limitação envergonhada: é evidência empírica, produzida pelo próprio
instrumento, de que a auditoria automática estabelece um piso de não conformidade e nunca um
atestado de acessibilidade. As três barreiras exigem julgamento semântico, e nenhuma delas
seria resolvida por refinamento da implementação.

### 3.2 Confiabilidade teste-reteste e correção do instrumento durante a coleta

Cada plataforma foi medida quatro vezes, entre 00h58 e 01h45 (tempo universal coordenado) de
16 de agosto de 2026. O índice de conformidade foi idêntico em todas as medições, nas cinco
plataformas, com variação nula, e o conjunto de critérios violados repetiu-se integralmente
em quatro delas. É o resultado esperado de barreiras estruturais, e evidência de que o
instrumento mede o portal, e não o momento.

A repetição revelou um defeito do próprio instrumento. O perfil de desktop não declarava
agente explícito e herdava o padrão da biblioteca de automação, que anuncia navegador em modo
headless. Isso violava a conduta declarada de identificar a pesquisa e produzia perda de
páginas por bloqueio, conforme a Tabela 2.

**Tabela 2** – Perda de páginas no portal federal informacional antes e depois da correção do
agente de usuário

| Configuração do instrumento | Medições | Perda de páginas |
|---|---|---|
| Agente herdado, em modo headless | 3 | 17% · 17% · 33% |
| Agente identificando a pesquisa | 3 | 0% · 0% · 0% |

Fonte: elaboração própria.

Teste direto confirmou que o agente de usuário não explicava as falhas do portal estadual,
que têm outra causa (subseção 3.4), mas explicava as do portal federal: as perdas ali eram
artefato do instrumento, e não propriedade do portal. Em consequência, o conjunto de dados
primário passou a ser o das medições posteriores à correção; usar as anteriores propagaria um
viés do instrumento para os resultados publicados.

A série diária revelou um segundo defeito, de natureza distinta e mais grave, porque afetava a
interpretação e não a coleta. Em 25 de agosto de 2026, uma falha de resolução de nomes na
máquina coletora impediu o carregamento das 20 páginas das cinco plataformas. O índice de
conformidade é a razão entre critérios não violados e critérios avaliados: sem página
carregada não há achado, o numerador fica cheio, e o instrumento registrou **100 pontos —
o máximo da escala — para as cinco plataformas**, no único dia em que nada foi observado.
Nenhuma exceção foi levantada; a taxa de perda de 100% ficou registrada num campo ao lado.

O defeito é da classe que interessa a um trabalho metodológico, por três razões. A direção do
erro é a mais desfavorável possível: falha de coleta empurra o índice para cima, produzindo
elogio onde deveria haver silêncio. O resultado é indistinguível na saída, porque conformidade
perfeita e ausência de observação ocupam a mesma célula. E o efeito sobre uma série temporal é
específico: um dia falsamente perfeito cria uma melhora aparente seguida de uma piora
aparente, ambas artefatos da rede de quem observa.

A correção foi de tipo, e não de apresentação. Os quatro índices passaram a admitir valor
nulo, e nulo passou a significar *sem veredito* — nem conformidade, nem não conformidade. O
acumulador do instrumento passou a contar páginas observadas, e não tentativas. Os campos
descritivos — cobertura, contagens, taxa de perda, estado de cada tentativa — continuam
preenchidos, porque a tentativa fracassada é justamente o que precisa permanecer auditável.
Como o documento primário de cada varredura armazena páginas e achados, e não índices, as
coletas anteriores foram reprocessadas sem que nenhum portal precisasse ser varrido de novo:
o erro de método custou uma reindexação, e não um retorno a campo.

O episódio é reportado, e não apagado, porque **uma auditoria contínua precisa saber dizer que
não sabe**. Um instrumento que converte silêncio em aprovação é, num domínio de exigibilidade
jurídica, pior do que instrumento nenhum: produz atestado de conformidade sobre o vazio.

### 3.3 Caracterização da amostra

Auditaram-se cinco plataformas, em 20 auditorias de página, das quais 16 foram bem-sucedidas
— perda global de 20%, concentrada no portal estadual. A Tabela 3 apresenta a caracterização.

**Tabela 3** – Plataformas auditadas, perda de páginas e indicadores por plataforma, Rio de
Janeiro, 16 de agosto de 2026

| Plataforma | Esfera | Serviço | Páginas | Perda | ICA | IAN | IEJ | Violações | Ocorrências | Peso médio (MB) |
|---|---|---|---|---|---|---|---|---|---|---|
| Meu SUS Digital | Federal | Prontuário | 2 | 0% | 72,6 | 99,9 | 58,7 | 13 | 37 | 7,17 |
| Portal federal de saúde | Federal | Informacional | 6 | 0% | 84,9 | 80,4 | 19,9 | 20 | 30 | 3,60 |
| Secretaria estadual de saúde | Estadual | Ouvidoria, exames | 6 | 67% | 54,1 | 99,9 | 66,3 | 21 | 42 | 1,60 |
| Secretaria municipal de saúde | Municipal | Informacional | 2 | 0% | 61,0 | 100,0 | 80,9 | 24 | 86 | 2,12 |
| Portal municipal de serviços | Municipal | Serviços | 4 | 0% | 50,7 | 100,0 | 87,9 | 47 | 974 | 1,14 |

Fonte: elaboração própria.
Notas: ICA — Índice de Conformidade de Acessibilidade (0–100, maior é melhor); IAN — Índice
de Atrito de Navegação (0–100, menor é melhor); IEJ — Índice de Exposição Jurídica (0–100,
menor é melhor).

A verificação prévia dos alvos, realizada na data da coleta, produziu quatro achados com
consequência para a leitura dos resultados, todos registrados no catálogo.

O endereço institucional da secretaria estadual havia sido reduzido a um documento de 935
bytes que redirecionava por script e declarava idioma inglês: o portal migrou de domínio, mas
os serviços ao cidadão permaneceram no subdomínio antigo. A seção de saúde do portal da
prefeitura não é um portal de serviços — seu título é "Arquivos Saúde" e seu conteúdo é
jornalismo institucional, enquanto os serviços residem em endereço distinto. O antigo canal da
atenção primária municipal converteu-se em repositório técnico dirigido a profissionais e foi
excluído da amostra: um canal antes voltado ao usuário deixou de sê-lo, sem substituto
anunciado. Por fim, a plataforma federal de prontuário serve a mesma casca de 1.418 bytes em
toda rota, inclusive no `robots.txt`, por ser aplicação de página única — sem renderização por
navegador, a auditoria mediria uma casca vazia.

A limitação mais relevante da amostra é declarada: a área autenticada da plataforma federal
de prontuário, onde residem resultado de exame e carteira de vacinação, foi excluída por
conduta de coleta. As telas de maior consequência assistencial ficaram fora, e os índices
podem estar otimistas.

### 3.4 Disponibilidade como precondição da acessibilidade

O portal estadual perdeu entre 50% e 67% das páginas em todas as quatro medições. Descartado
o agente de usuário como causa, o diagnóstico prosseguiu por observação direta da
disponibilidade dos dois hospedeiros envolvidos, sintetizada na Tabela 4.

**Tabela 4** – Observação direta da disponibilidade dos hospedeiros do portal estadual, 16 de
agosto de 2026

| Instante (tempo universal coordenado) | Instrumento | Resultado |
|---|---|---|
| 00h47 | Cliente HTTP | Resposta 200 nos três endereços |
| 01h00 · 01h04 · 01h31 · 01h40 | Navegador | Falha em 50% a 67% das páginas |
| 01h06 | Cliente HTTP | Falha nos dois hospedeiros |
| 01h29 | Cliente HTTP | Resposta 200 nos três endereços |
| 01h37 | Cliente HTTP e navegador | Falha em ambos, simultaneamente |

Fonte: elaboração própria.

Na janela de coleta, portanto, a infraestrutura oscilou em escala de minutos, com falha
atingindo navegador e cliente HTTP simples. A página de resultado de exame não foi auditada
com sucesso nenhuma vez — falhou em oito de oito tentativas por navegador —, embora o cliente
HTTP a tenha alcançado duas vezes, nos intervalos entre quedas.

#### 3.4.1 Verificação por múltiplos pontos de observação

A conclusão de que se tratava de indisponibilidade repousava sobre um único ponto de
observação — uma conexão residencial no Rio de Janeiro. Verificação posterior, em 19 de agosto
de 2026, mostrou que essa atribuição era insuficiente, e o resultado corrige a leitura.

O instrumento foi executado a partir de três posições de rede distintas, com medições
separadas por poucos minutos: um servidor em nuvem nos Estados Unidos, um segundo serviço em
nuvem também nos Estados Unidos, e a conexão residencial brasileira da coleta original.

**Tabela 5** – Resposta dos hospedeiros do portal estadual por posição de rede, 19 de agosto de
2026, entre 05h35 e 05h50 (tempo universal coordenado)

| Endereço | Nuvem A (EUA) | Nuvem B (EUA) | Conexão residencial (Brasil) |
|---|---|---|---|
| Portal institucional | conexão encerrada | 500 | **200** |
| Resultado de exame | conexão encerrada | 500 | **200** |
| Ouvidoria | 200 | 200 | 200 |

Fonte: elaboração própria.

O padrão é consistente e não é de indisponibilidade: **o mesmo hospedeiro atende a ouvidoria a
todas as posições e recusa dois endereços específicos às posições estrangeiras**, servindo-os
normalmente à posição brasileira, no mesmo intervalo de minutos.

Três hipóteses alternativas foram testadas e descartadas. A negociação do protocolo HTTP/2 não
explica o comportamento — o servidor não a oferece, e as requisições ocorrem em HTTP/1.1 em
todos os casos. A detecção de navegador automatizado também não: execuções em modo visível e
em modo automatizado, a partir da posição brasileira, obtiveram resposta 200 nos dois
endereços, e a abertura manual em navegador comum confirmou. E não se trata de recusa
indiscriminada a origem estrangeira, porque as duas nuvens receberam respostas distintas entre
si em um dos alvos federais examinados em paralelo.

O achado que sobrevive é mais específico, e mais forte, que o original: **o portal estadual
diferencia a resposta conforme a origem de rede da requisição**, em endereços determinados. A
indisponibilidade observada em 16 de agosto foi real naquela janela — a posição brasileira
também falhou —, mas não pode ser inferida a partir de observação estrangeira, e as duas
situações têm a mesma aparência para um instrumento com um único ponto de vista.

A consequência metodológica é imediata e está incorporada ao desenho: **a posição de rede
passa a ser variável declarada do estudo, e nenhuma afirmação de indisponibilidade é
sustentada a partir de um ponto único.** A alternativa — tratar a origem como constante
implícita — produziria, em auditoria continuada a partir de infraestrutura em nuvem, uma série
em que dois dos cinco alvos apareceriam permanentemente fora do ar, com a limitação
indistinguível do achado.

### 3.5 Conformidade geral

A mediana do índice de conformidade por página foi de 69,2 (intervalo de confiança de 95% por
*bootstrap*: 61,0–84,9; *n* = 16; primeiro quartil 60,4; terceiro quartil 85,4; mínimo 50,7;
máximo 87,0).

Registraram-se 174 achados, dos quais 125 violações confirmadas e 49 vereditos indeterminados.
Vereditos indeterminados jamais foram convertidos em violação, e as sondas declaradas
heurísticas estão impedidas, por contrato verificado em teste, de produzir reprovação.

Das 125 violações, 113 correspondem a um critério de sucesso das diretrizes; as 12 restantes
decorrem de sondas que medem dimensões sem correspondência normativa — custo de acesso —, e
por isso não figuram nas distribuições por princípio e por nível de conformidade da Tabela 6.

**Tabela 6** – Distribuição das violações por princípio, por nível de conformidade e por
faixa de risco jurídico

| Princípio | Violações | Nível | Violações | Risco jurídico | Violações |
|---|---|---|---|---|---|
| Perceptível | 64 | A | 82 | Crítico | 28 |
| Operável | 18 | AA | 31 | Alto | 87 |
| Compreensível | 16 | — | — | Moderado | 10 |
| Robusto | 15 | — | — | Baixo | 0 |
| **Total** | **113** | **Total** | **113** | **Total** | **125** |

Fonte: elaboração própria.

Duas leituras merecem destaque. Primeira: 73% das violações vinculadas a critério são de
nível A, o patamar mínimo de conformidade — não se trata de refinamento, mas do piso que não
foi alcançado. Segunda: nenhuma violação de risco baixo. Todas as barreiras detectadas
obstruem tarefa ou exigem esforço desproporcional; o instrumento não está reportando
irregularidade formal.

A Figura 1 apresenta a prevalência por critério, isto é, a fração dos oito endereços distintos
auditados com sucesso — as 16 auditorias correspondem a esses oito endereços em dois perfis —
em que cada critério foi violado. O critério 4.1.2 (Nome, função, valor) foi violado em 100%
dos endereços; seguem-se 3.3.2 (Rótulos ou instruções), com 75,0%; e 1.1.1 (Conteúdo não
textual), 1.3.1 (Informações e relações), 1.4.4 (Redimensionar texto) e 2.4.4 (Finalidade do
link), com 62,5% cada. O critério 1.4.3 (Contraste mínimo) aparece em 50,0%, 1.4.10 (Refluxo)
em 37,5% e 2.4.1 (Ignorar blocos) em 25,0%. Com 12,5% cada, fecham a distribuição os critérios
2.1.1 (Teclado), 2.4.3 (Ordem de foco) e 3.1.1 (Idioma da página).

**Figura 1** – Prevalência de violação por critério de sucesso, em fração das páginas
auditadas
Fonte: elaboração própria.

O achado central do estudo é a prevalência total do critério 4.1.2. Em todas as páginas, das
cinco plataformas, nas três esferas de governo, existe ao menos um controle que a tecnologia
assistiva não consegue anunciar: para o usuário de leitor de tela, aquele botão ou aquele
link simplesmente não existe. Prevalência de 100% em amostra estratificada por esfera aponta
falha estrutural do ecossistema, e não deficiência de um órgão.

### 3.6 Barreiras absolutas

Todas as cinco plataformas e todas as 16 páginas auditadas apresentam violação de risco
jurídico crítico, isto é, barreira sem rota alternativa. Não há, no conjunto examinado, uma
única página de serviço público digital de saúde plenamente utilizável por pessoa cega ou com
deficiência motora. A Tabela 7 decompõe as 28 violações críticas.

**Tabela 7** – Regras que produziram violações de risco jurídico crítico e privação
correspondente

| Regra | Achados | Consequência para o usuário |
|---|---|---|
| Nome de botão ausente | 10 | A ação é inominada |
| Nome de link ausente | 10 | O leitor de tela anuncia "link" e nada mais |
| Nome de botão de formulário ausente | 4 | Controle de envio sem rótulo |
| Controle não interativo com manipulador de clique | 2 | Elemento clicável inalcançável por teclado |
| Alternativa textual de botão-imagem ausente | 1 | Botão sem descrição |
| Rótulo programático de campo ausente | 1 | Campo sem identificação para tecnologia assistiva |

Fonte: elaboração própria.

Todas se reduzem à mesma privação: o controle existe visualmente e não existe para quem não
enxerga. É a forma mais severa da barreira tipificada no art. 3º, IV, "d", da Lei Brasileira
de Inclusão.

### 3.7 Gradiente por esfera federativa

A Tabela 8 apresenta as medianas dos três índices por esfera.

**Tabela 8** – Medianas dos índices por esfera federativa

| Esfera | Páginas | ICA | IAN | IEJ |
|---|---|---|---|---|
| Federal | 8 | 86,0 | 80,8 | 22,3 |
| Estadual | 2 | 58,9 | 99,9 | 66,3 |
| Municipal | 6 | 61,0 | 100,0 | 84,2 |

Fonte: elaboração própria.

Para o índice de conformidade, o teste de Kruskal-Wallis resultou em p = 0,0029, com
ε² = 0,746; para o índice de atrito, p = 0,0017, com ε² = 0,831 — efeitos grandes em ambos os
casos. Agregando em nível de portal, para contornar a pseudorreplicação, os valores de
conformidade são 72,6 e 84,9 na esfera federal, 54,1 na estadual e 50,7 e 61,0 na municipal,
preservando a direção observada. A Figura 2 representa a distribuição.

**Figura 2** – Distribuição do índice de conformidade por esfera federativa
Fonte: elaboração própria.

As ressalvas são obrigatórias, e uma delas é de composição, não de tamanho. O *n* é pequeno —
cinco portais, e apenas duas páginas válidas no estrato estadual, em razão do descrito na
subseção 3.4 — e as páginas de um mesmo portal não são independentes.

Além disso, **os estratos não comparam objetos equivalentes**. Das três páginas amostradas no
estrato estadual, apenas a ouvidoria é transacional: apresenta cinco formulários e sete campos
preenchíveis, contra um único campo, o da busca, nas outras duas. O estrato estadual entra na
comparação representado, na prática, por uma página de manifestação do cidadão, enquanto o
federal é representado por um prontuário eletrônico e o municipal por um catálogo de serviços.
Como páginas transacionais concentram mais controles interativos — e é sobre controles que
recaem os critérios de risco crítico —, a heterogeneidade tende a **atenuar** o gradiente
observado, e não a produzi-lo. Ainda assim, ela precisa ser declarada: o que a amostra compara
é o que cada esfera oferece sob o rótulo de saúde, e não a mesma tarefa em três esferas. Os testes são descritivos, não confirmatórios. O que a
amostra sustenta é a direção do gradiente e a magnitude do efeito, não a generalização para o
universo de portais brasileiros.

Note-se que o índice de exposição jurídica separa os estratos com mais nitidez que o de
conformidade — 22,3 contra 84,2, quase o quádruplo —, o que sugere que a distância entre
esferas está menos no número de falhas e mais na gravidade delas.

### 3.8 Efeito do perfil de dispositivo

A comparação entre perfis não revelou diferença nos índices agregados: mediana de conformidade
de 69,2 no perfil de desktop e 66,8 no perfil móvel; mediana de atrito de 99,8 em ambos; peso
mediano de 2,29 e 2,26 mebibytes, respectivamente. O teste de Mann-Whitney para o atrito
resultou em p = 1,000, com δ de Cliff igual a 0,000.

A comparação de agregados, porém, esconde o achado relevante: o critério 1.4.10 (Refluxo)
apareceu exclusivamente no perfil móvel, e nenhum critério apareceu exclusivamente no perfil
de desktop. A barreira existe apenas onde o usuário está. Auditar somente em desktop — prática
comum na literatura e nas homologações — teria produzido um relatório sem essa classe inteira
de barreira.

Registre-se uma correção relativa à leitura preliminar. Com o instrumento defeituoso descrito
na subseção 3.2, o peso mediano parecia 70% maior no perfil móvel (2,44 contra 1,44
mebibytes). Com o instrumento corrigido, os pesos são equivalentes: a assimetria era artefato
de quais páginas conseguiam carregar em cada perfil, e não característica dos portais. O caso
ilustra por que perda diferencial de dados não pode ser tratada como ruído aleatório.

### 3.9 Custo de acesso

O peso mediano por página foi de 2,29 mebibytes (intervalo de confiança de 95%: 1,59–4,17;
*n* = 16), e 4 das 16 páginas (25%) excedem o limiar de 2,5 mebibytes. A Tabela 9 apresenta os
resultados por plataforma.

**Tabela 9** – Peso mediano, custo por acesso, fração da franquia mensal e participação de
tráfego de terceiros, por plataforma

| Plataforma | Peso mediano (MB) | Custo por acesso (R$) | Fração da franquia | Tráfego de terceiros |
|---|---|---|---|---|
| Meu SUS Digital | 7,17 | 0,0210 | 0,070% | 2,2% |
| Portal federal de saúde | 2,49 | 0,0073 | 0,024% | 41,9% |
| Secretaria municipal de saúde | 2,11 | 0,0062 | 0,021% | 69,4% |
| Secretaria estadual de saúde | 1,60 | 0,0047 | 0,016% | 16,6% |
| Portal municipal de serviços | 1,14 | 0,0033 | 0,011% | 40,8% |

Fonte: elaboração própria.

A hipótese H4 não foi sustentada. A correlação entre peso da página e participação de
terceiros é fraca e de sinal contrário ao previsto (ρ de Spearman = −0,200; p = 0,747),
calculada sobre apenas cinco plataformas: o coeficiente não sustenta afirmação sobre direção
alguma, e o que se pode dizer com honestidade é que **não há associação detectável** entre as
duas grandezas.

O que sustenta a leitura é a dissociação qualitativa, visível na Tabela 9 e na Figura 3. A
plataforma federal de prontuário é a página mais pesada do conjunto (7,17 mebibytes) e a que
menos depende de terceiros (2,2%) — seu peso vem da própria aplicação. Já a seção de notícias
municipal, com menos de um terço daquele peso (2,11 mebibytes), dirige 69,4% do tráfego a
domínios de terceiros. Uma grandeza varia sem a outra, e três das cinco plataformas dirigem
mais de 40% do tráfego a terceiros.

**Figura 3** – Peso da página decomposto em tráfego próprio e de terceiros, por plataforma
Fonte: elaboração própria.

O custo monetário de um acesso isolado é pequeno — de R$ 0,003 a R$ 0,021 —, e o texto o
afirma explicitamente. A relevância do achado não está no valor unitário, e a subseção 4.5
desenvolve por quê.

Dois elementos de contexto, colhidos na mesma consulta às ofertas comerciais, qualificam a
leitura. A mesma operadora cobra R$ 3,00 por gibibyte de quem recarrega R$ 15,00 a cada 15
dias e R$ 2,00 por gibibyte de quem recarrega R$ 30,00 por 30 dias: 50% a mais para quem não
consegue comprometer o valor cheio. E a oferta de entrada consultada isenta explicitamente um
aplicativo de mensageria do consumo de franquia, ao passo que o portal público de saúde não é
isento.

### 3.10 Perfil de exclusão

A Figura 4 e a Tabela 10 convertem contagem de defeitos em população impactada, agregando
ocorrências por grupo de pessoas afetado.

**Tabela 10** – Ocorrências de barreira e achados distintos, por grupo de pessoas afetado

| Grupo afetado | Ocorrências | Achados |
|---|---|---|
| Deficiência intelectual ou neurodivergência | 1.126 | 96 |
| Baixa visão | 1.060 | 76 |
| Deficiência na visão de cores | 636 | 8 |
| Cegueira, com uso de leitor de tela | 479 | 82 |
| Deficiência motora | 116 | 37 |
| Plano de dados limitado | 106 | 22 |
| Uso de comando por voz | 84 | 26 |

Fonte: elaboração própria.

**Figura 4** – Ocorrências de barreira por grupo de pessoas afetado
Fonte: elaboração própria.

Um achado é contraintuitivo: deficiência intelectual e neurodivergência encabeçam a lista, com
mais ocorrências que cegueira. Outro é diagnóstico: a deficiência na visão de cores reúne 636
ocorrências em apenas 8 achados distintos — razão de 79 ocorrências por achado, retrato do
defeito de sistema de design, em que uma decisão de paleta se replica por centenas de
elementos.

### 3.11 Qualificação jurídica

A Tabela 11 apresenta os dispositivos invocados pelas 125 violações, segundo a matriz descrita
na subseção 2.4.

**Tabela 11** – Dispositivos normativos invocados pelas violações confirmadas

| Dispositivo | Invocações |
|---|---|
| Lei 13.146/2015, art. 18 — atenção integral à saúde da pessoa com deficiência | 125 |
| Constituição Federal, art. 196 — acesso universal e igualitário | 125 |
| Lei 13.146/2015, art. 63, caput — acessibilidade em sítios de órgãos de governo | 113 |
| Lei 13.146/2015, art. 3º, IV, "d" — barreiras nas comunicações e na informação | 113 |
| Lei 13.146/2015, art. 4º — igualdade e não discriminação | 113 |
| Decreto 5.296/2004, art. 47 | 113 |
| Modelo de Acessibilidade em Governo Eletrônico | 113 |
| Convenção sobre os Direitos das Pessoas com Deficiência, art. 25 | 113 |
| Lei 13.146/2015, art. 74 — tecnologia assistiva | 76 |
| Constituição Federal, art. 5º, XIV — acesso à informação | 38 |
| Convenção sobre os Direitos das Pessoas com Deficiência, art. 9 | 28 |
| Lei 12.527/2011, art. 8º, § 3º, VIII — transparência ativa | 26 |

Fonte: elaboração própria.

As 28 invocações do art. 9 da Convenção correspondem exatamente às 28 violações de risco
crítico — as barreiras sem rota alternativa. É o dado de maior densidade normativa do estudo:
em todas as cinco plataformas, e em todas as páginas auditadas, há descumprimento de norma com
hierarquia constitucional.

As vias de exigibilidade variam com a esfera. Na federal, o controle externo cabe ao Tribunal
de Contas da União, somando-se o Ministério Público Federal, a ação civil pública e a via
orçamentária do art. 64 da Lei Brasileira de Inclusão. Na estadual e na municipal, o controle
externo cabe aos respectivos tribunais de contas, com o Ministério Público estadual e as
ouvidorias como vias complementares.

### 3.12 Série temporal diária

A série de treze dias (19 a 31 de agosto de 2026) produziu 65 varreduras e 260 tentativas de
auditoria de página. Em 25 de agosto, a falha do coletor descrita na subseção 3.2 impediu
qualquer observação, e o dia consta da série **sem veredito**: não entra como conformidade
nem como não conformidade. Restam doze dias observados. A Tabela 12 apresenta o índice de
conformidade por plataforma e por dia.

**Tabela 12** – Índice de conformidade acessível por plataforma, em série diária, 19 a 31 de
agosto de 2026

| Dia | Meu SUS Digital | Portal federal de saúde | Secretaria estadual | Secretaria municipal | Portal municipal de serviços |
|---|---|---|---|---|---|
| 19/08 | 72,6 | 84,9 | 49,3 | 61,0 | 50,7 |
| 20/08 | 72,6 | 84,9 | 49,3 | 61,0 | 50,7 |
| 21/08 | 72,6 | 84,9 | 49,3 | 61,0 | 50,7 |
| 22/08 | 72,6 | 84,9 | 49,3 | 61,0 | 50,7 |
| 23/08 | 72,6 | 84,9 | 49,3 | 61,0 | 50,7 |
| 24/08 | 72,6 | 80,1 | 49,3 | 61,0 | 58,9 |
| 25/08 | — | — | — | — | — |
| 26/08 | 72,6 | 75,3 | 49,3 | 61,0 | 58,9 |
| 27/08 | 72,6 | 80,1 | 49,3 | 61,0 | 58,9 |
| 28/08 | 72,6 | 80,1 | 49,3 | 61,0 | 58,9 |
| 29/08 | 72,6 | 75,3 | 49,3 | 61,0 | 50,7 |
| 30/08 | 72,6 | 75,3 | 49,3 | 61,0 | 50,7 |
| 31/08 | 72,6 | 80,1 | 49,3 | 61,0 | 50,7 |

Nota: o travessão indica ausência de observação — nenhuma página carregou, por falha do
coletor, e não há veredito a reportar. Fonte: elaboração própria.

A Figura 5 representa a mesma série. O dia sem veredito aparece como interrupção das linhas,
e não como interpolação entre os dias vizinhos: ligar os pontos por cima da lacuna desenharia
uma continuidade que não foi observada.

**Figura 5** – Índice de conformidade acessível em série diária, por plataforma, 19 a 31 de
agosto de 2026
Fonte: elaboração própria.

#### 3.12.1 Estabilidade: a barreira típica é estrutural

Três das cinco plataformas — o Meu SUS Digital, a secretaria estadual e a secretaria municipal —
apresentaram **variação nula** ao longo dos doze dias observados: índice idêntico e, mais
significativo, **conjunto de critérios violados idêntico**, respectivamente 5, 11 e 8
critérios, em todos os dias e nos dois perfis de dispositivo. Nenhuma barreira apareceu,
desapareceu ou se deslocou de página.

O resultado é de interpretação direta: a barreira típica destes portais não é acidente de
publicação, é propriedade do sistema que os produz. Ela sobrevive a doze ciclos de publicação
de conteúdo porque não está no conteúdo — está no *template*, no componente reaproveitado, na
ausência de verificação na homologação. É o mesmo diagnóstico que a prevalência de 100% do
critério 4.1.2 sugeria no corte transversal, agora sustentado por evidência de persistência,
e não apenas de disseminação.

#### 3.12.2 Mudança: duas barreiras que se moveram

Duas plataformas variaram, e as duas variações são qualitativamente distintas. A Tabela 13
sintetiza os critérios cuja violação mudou de estado ao longo da série.

**Tabela 13** – Critérios de sucesso cuja violação mudou de estado na série diária

| Plataforma | Critério | Risco jurídico | 19 a 23/08 | 24 a 28/08 | 29 a 31/08 |
|---|---|---|---|---|---|
| Portal municipal de serviços | 2.1.1 Teclado | Crítico | Violado | Não violado | Violado |
| Portal federal de saúde | 1.1.1 Conteúdo não textual | Alto | Não violado | Violado | Violado |

Fonte: elaboração própria.

A **violação do critério 2.1.1** no portal municipal de serviços é o achado de maior
consequência da série. Trata-se de elemento não interativo empregado como controle, detectado
pela sonda própria do instrumento, na página do serviço de atendimento em unidades de pronto
atendimento, **nos dois perfis de dispositivo simultaneamente**. Ela esteve presente em 19,
20, 21, 22 e 23 de agosto; ausente em 24, 26, 27 e 28; e presente novamente em 29, 30 e 31.
A ausência não é artefato de cobertura: em 24, 26 e 28 as quatro auditorias de página foram
bem-sucedidas, de modo que a barreira foi procurada onde estava e não foi encontrada.

Um controle inoperável por teclado impede a conclusão da tarefa por quem não usa mouse, sem
rota alternativa, na página que informa como obter atendimento de urgência. A consequência
metodológica é imediata: **uma auditoria pontual realizada em 26 de agosto teria declarado
essa página livre da barreira; a mesma auditoria, em 22 ou em 30, a teria encontrado.** As
duas auditorias seriam corretas quanto ao instante e erradas quanto ao portal. É a
demonstração empírica, e não meramente argumentativa, de que a periodicidade da verificação é
parte do método, e não detalhe operacional.

A **violação do critério 1.1.1** no portal federal de saúde tem o sinal oposto: é uma
regressão introduzida e não corrigida. Ausente nos cinco primeiros dias, apareceu em 24 de
agosto e permaneceu em todos os oito dias observados subsequentes. Nos dois dias de cobertura
integral do período (24 e 27 de agosto), a violação foi detectada em **todas as páginas
auditadas e nos dois perfis**, o que a caracteriza como alteração de escopo do portal, e não
como propriedade de uma página. Conteúdo não textual sem alternativa equivalente exclui o
usuário de leitor de tela do acesso à informação veiculada.

Três outros critérios da mesma plataforma — 1.4.1, 1.4.3 e 2.4.7 — apareceram de forma
esporádica, em um ou dois dias, sempre em uma única página e em um único perfil. Reporta-se a
ocorrência, mas não se extrai dela interpretação: são compatíveis com conteúdo rotativo e
ocorreram justamente no portal de disponibilidade mais instável, o que impede separar mudança
do portal de variação de amostra observada.

#### 3.12.3 Disponibilidade ao longo da série

Excluído o dia sem veredito, a série confirma e quantifica o achado da subseção 3.4. A perda
de páginas concentra-se em uma única plataforma: **26,4% no portal federal de saúde**, contra
**0% no Meu SUS Digital, na secretaria estadual e na secretaria municipal** e 4,2% no portal
municipal de serviços, ao longo dos mesmos doze dias, do mesmo ponto de rede e no mesmo
horário. As falhas do portal federal de saúde recaíram sobre dois caminhos
específicos — a página de secretaria finalística e o índice temático de saúde —, enquanto a
página inicial falhou uma única vez em doze dias.

Registre-se ainda a mudança na secretaria estadual, cuja perda passou de 50% a 67% nas
medições de 16 de agosto para **0% nos doze dias da série**, com cobertura integral das seis
auditorias de página diárias. A instabilidade de infraestrutura documentada na subseção 3.4
foi, portanto, episódica, e o índice de conformidade do portal sob cobertura integral — 49,3
pontos, o mais baixo da amostra — é agora medido sobre a amostra completa de páginas, e não
sobre o resíduo que sobrevivia às quedas.

---

## 4 Discussão

### 4.1 Principais achados

Oito resultados sustentam a discussão, todos ancorados em dado medido, e cada um é
desenvolvido adiante. **O critério 4.1.2 foi violado em 100% das páginas**, nas três esferas:
prevalência total em amostra estratificada indica falha estrutural do ecossistema de
desenvolvimento — padrões de componente, ausência de verificação na homologação, contratação
que não exige acessibilidade — e não deficiência isolada de um órgão, do que segue que a
correção órgão a órgão tende a ser menos eficiente que a atuação sobre padrões e requisitos de
compra. **Todas as 16 páginas apresentam barreira absoluta**, o que separa este estudo dos que
reportam percentuais: um portal com conformidade de 86 pontos e uma barreira absoluta não é
"majoritariamente acessível", é um portal que impede o uso por um grupo determinado. **O
gradiente por esfera** tem efeito grande e distância maior na gravidade que no número das
falhas. **A barreira de refluxo só existe onde o usuário está**, no perfil de 320 pixels — o
argumento empírico mais direto contra a auditoria de perfil único. **Peso próprio e
dependência de terceiros variam de forma independente**, e o instrumento só pôde exibir a
dissociação por separá-los desde o desenho. **A disponibilidade depende da posição de rede do
observador** (subseção 4.3). **O serviço raramente está onde o portal oficial o anuncia**
(subseção 4.4). E, na série de treze dias, **três das cinco plataformas não variaram em nada,
enquanto duas mudaram** — uma barreira crítica de teclado desapareceu por quatro dias e
retornou, e uma violação de alternativa textual foi introduzida e não corrigida (subseção
4.7). Os dois fatos, juntos, sustentam a tese do trabalho: a barreira típica é estrutural e
persistente, mas não *todas* são, e distinguir umas das outras exige repetição.

### 4.2 O art. 63 como norma em branco

A remissão do art. 63 da Lei Brasileira de Inclusão às "melhores práticas e diretrizes de
acessibilidade adotadas internacionalmente" transforma um padrão técnico produzido por
consórcio privado em conteúdo de dever jurídico estatal. A construção tem três consequências
que este trabalho pôde observar empiricamente.

A primeira é que a atualização do padrão altera o conteúdo do dever sem alteração
legislativa. A segunda é que o Modelo de Acessibilidade em Governo Eletrônico funciona como
vetor de concretização — mas é norma administrativa, e a última versão de referência data de
2014, o que abre distância crescente em relação ao padrão internacional que pretende
incorporar. A terceira é a zona de indeterminação criada pela divergência entre versões, de
que o critério 4.1.1 é exemplo concreto e documentado neste estudo: o critério foi removido na
versão 2.2 das diretrizes, e o motor de regras acompanhou a norma técnica, enquanto a
referência normativa brasileira permanece na versão 2.1. Descumprir hoje um critério que a
versão mais recente da norma técnica abandonou é, ou não é, violação de dever jurídico? A
pergunta não é acadêmica: dela depende a exigibilidade concreta.

Há, além disso, uma questão empírica embutida na construção, e a literatura brasileira já a
formulou. Freire, Castro e Fortes (2009) mediram os sítios estaduais ao longo de doze anos
para verificar se o prazo de conformidade do Decreto 5.296/2004 produziria efeito observável,
e encontraram avanço modesto. Quase duas décadas depois, com a Lei Brasileira de Inclusão em
vigor há mais de dez anos, os resultados aqui obtidos — nível A violado em 73% dos casos,
barreira absoluta em todas as páginas — sugerem que a resposta continua a mesma. A norma
existe; o efeito mensurável, não. É argumento a favor de deslocar a atenção da produção
normativa para os mecanismos de verificação e indução, tema da subseção 4.9.

O achado tem, por fim, uma implicação metodológica que extrapola este trabalho. Se o conteúdo
do dever é definido por remissão a um padrão que evolui, então a ferramenta de auditoria
precisa declarar a versão do padrão que aplica, e não apenas a sua própria — do contrário,
dois relatórios sobre o mesmo portal, produzidos em datas distintas, tornam-se incomparáveis
sem que se saiba por quê.

### 4.3 Disponibilidade como precondição da acessibilidade

A disponibilidade é precondição da acessibilidade, e nenhum índice de conformidade a captura.
Um serviço de resultado de exame que responde de forma intermitente não é um serviço difícil
de usar: é um serviço que, para quem tenta no minuto errado, não existe. O estudo só registrou
o fenômeno porque o instrumento trata falha de carregamento como dado — com taxa de perda
reportada em toda saída — e não como interrupção da coleta.

Registre-se a assimetria informacional que a situação produz. O cidadão que encontra a página
fora do ar não sabe se o problema é do seu aparelho, da sua conexão ou do Estado. Do ponto de
vista da experiência, a indisponibilidade intermitente é pior que a queda franca: convida à
repetição da tentativa, e cada tentativa consome franquia de dados.

O caso sugere que a taxa de perda de páginas deveria ser desfecho reportado nos estudos de
acessibilidade, e não incidente de coleta silenciosamente descartado: excluir as páginas que
não carregaram produz retrato sistematicamente mais favorável que a realidade do serviço. A
verificação por múltiplos pontos (subseção 3.4.1) acrescenta uma exigência a isso, e é a
contribuição metodológica mais transferível deste trabalho. **Reportar perda de páginas só é
informativo se a posição de rede do observador for declarada.** Uma mesma taxa de perda significa indisponibilidade do serviço, se medida da
posição em que o cidadão está, ou política de rede do portal, se medida de outra — e as duas
são indistinguíveis sem um segundo ponto de observação.

A consequência prática atinge diretamente a proposta de auditoria continuada. Executada em
infraestrutura de nuvem, como é natural para um monitoramento automatizado, ela reportaria
indefinidamente como indisponíveis dois dos cinco alvos, entre eles o serviço de resultado de
exame — produzindo um falso achado estável, robusto à repetição e indistinguível de um
resultado verdadeiro justamente por não variar. É a forma mais perigosa de erro em série
temporal: a que a consistência confirma.

Registre-se, por fim, o que a diferenciação por origem significa do ponto de vista do direito
de acesso. Ela não é, em si, barreira de acessibilidade — o cidadão brasileiro alcança o
serviço. Mas revela que a camada de rede aplica ao serviço público de saúde políticas de
discriminação que não constam de norma alguma, não são publicadas e não são recorríveis: o
usuário a quem a resposta for negada não recebe explicação nem via de contestação.

### 4.4 A arquitetura de encaminhamento

Um padrão atravessa a verificação prévia dos alvos e a caracterização das páginas, e não estava
previsto no desenho: **o cidadão que procura um serviço de saúde no portal oficial encontra,
na maior parte das vezes, um índice que aponta para outro lugar.**

A seção de saúde do portal municipal é um arquivo de notícias. O antigo canal da atenção
primária tornou-se repositório técnico dirigido a profissionais. O portal institucional
estadual organiza-se por público — cidadão, servidor, gestor, pesquisador, imprensa — e não
oferece transação. E a página de resultado de exame não entrega resultado algum: apresenta
cinco cartões que encaminham a sistemas distintos, com autenticação própria, entre os quais
duas plataformas de empresas privadas.

A caracterização é qualitativa, e assim deve ser reportada: tentativas de quantificá-la por
contagem de elementos de formulário mostraram-se inúteis, porque filtros de listagem, campos
de busca e avisos de consentimento inflam a contagem em páginas que não oferecem transação
alguma. O que sustenta o padrão é a inspeção de cada alvo, registrada no catálogo do estudo.

O achado tem três consequências, e a terceira é jurídica.

**Metodológica.** Auditar o portal oficial não é auditar o serviço. A conformidade medida
descreve a camada de encaminhamento, e o ponto em que a tarefa é efetivamente concluída
permanece fora do alcance — atrás de autenticação, e frequentemente em outro domínio. Os
índices aqui reportados descrevem, portanto, o que o cidadão encontra antes de chegar ao
serviço, o que reforça a leitura de que constituem piso e não retrato.

**Sobre a experiência.** Cada salto acrescenta uma superfície de acessibilidade que ninguém
audita, e o custo se acumula sobre quem menos pode absorvê-lo: mais páginas carregadas, mais
franquia de dados consumida, mais oportunidades de encontrar a barreira que interrompe a
tarefa. Para o usuário de leitor de tela, cada camada é um novo conjunto de controles a
reconhecer; e o critério mais violado neste estudo, com prevalência total, é justamente o que
governa o reconhecimento de controles.

**Jurídica.** Que a etapa final ocorra em plataforma privada não afasta o dever de
acessibilidade — desloca o sujeito obrigado. O art. 63 da Lei Brasileira de Inclusão alcança
os sítios mantidos por empresas com sede ou representação comercial no País, de modo que o
prestador privado que entrega o resultado do exame está tão vinculado quanto a secretaria que
o contratou. **O dever segue o serviço, e não o domínio.** A consequência prática interessa ao
controle externo: a via do art. 64, que condiciona financiamento e aprovação de projetos à
acessibilidade, alcança o arranjo contratual inteiro, e não apenas a página que ostenta o
brasão.

### 4.5 Exclusão digital e exclusão por deficiência

O custo monetário de um acesso isolado é pequeno, e inflá-lo seria fabricar evidência. A força
do argumento está em três lugares, todos mensurados.

O primeiro é a jornada completa: acompanhar um agendamento não é ato único, e o consumo se
acumula sobre acessos repetidos. O segundo é a tentativa frustrada: cada barreira de
acessibilidade que obriga a repetir o fluxo soma-se à conta, de modo que as duas dimensões
auditadas se agravam mutuamente — e essa interação é a contribuição original da medida. O
terceiro é o tráfego de terceiros: que quase 70% do tráfego da seção de saúde do portal
municipal se dirija a domínios de terceiros significa que o cidadão custeia, da própria
franquia, recursos alheios ao serviço público que foi buscar. É a métrica com fundamento
jurídico mais direto, porque ali há transferência de custo sem contrapartida.

Dois mecanismos observados nas ofertas comerciais reforçam a leitura. O primeiro reproduz, na
infraestrutura de acesso ao serviço público digital, o mecanismo que Caplovitz (1963) descreveu
no consumo de bens duráveis por famílias de baixa renda: fracionar a recarga não é
conveniência, é restrição de fluxo de caixa, e custa 50% mais por unidade de dado — o mais
pobre paga mais caro pelo mesmo bem, e paga mais caro precisamente por ser mais pobre. O
segundo é a assimetria do tratamento tarifário: a oferta de entrada isenta um aplicativo
privado de mensageria do consumo de franquia, e não isenta o portal público de saúde. Para o
usuário de menor renda, o Estado é o único serviço que cobra pelo acesso.

A assimetria merece leitura à luz do art. 9º da Lei 12.965/2014 (Brasil, 2014b), que impõe ao
responsável pela transmissão o dever de tratar de forma isonômica os pacotes de dados, sem
distinção por conteúdo, origem, destino, serviço ou aplicação. Não cabe a este trabalho
qualificar a licitude da prática, que depende de análise regulatória própria e não foi objeto
do estudo. Cabe registrar o efeito medido: sob as ofertas consultadas, o serviço público de
saúde ocupa posição tarifária desfavorável frente a aplicações privadas de mensageria. Se
confirmada em levantamento dirigido ao mercado, a assimetria sugere via de correção
regulatória — inclusão de serviços públicos de saúde no tráfego não tarifado — e não apenas
técnica.

Os dois mecanismos incidem sobre uma população cuja conectividade já é precária por outras
razões: nas classes D e E, apenas 3% reúnem as condições do indicador de conectividade
significativa e 86% de quem tem celular acessa a rede exclusivamente por ele (CGI.br, 2025).
Somar a essa base uma página de vários mebibytes, com parcela relevante do tráfego destinada
a terceiros, é agravar uma restrição preexistente — e é sobre esse agravamento, não sobre o
centavo isolado, que a discussão jurídica deve incidir.

Sustenta-se, com isso, que exclusão digital e exclusão por deficiência são barreiras de mesma
natureza jurídica: ambas obstruem o acesso ao direito, ambas incidem sobre a mesma população
dependente do sistema público, e ambas encontram fundamento no art. 196 da Constituição
combinado com o dever de comunicação e informação adequadas do art. 18 da Lei Brasileira de
Inclusão. Reconheça-se, porém, que a tese sobre custo de dados é de princípio, e não de
regra: não há norma que fixe limite de peso de página, e o argumento é, por isso, mais frágil
que o ancorado em critério de sucesso — diferença que este trabalho declara em vez de
dissimular.

### 4.6 O perfil de exclusão e o que ele desloca

O debate público sobre acessibilidade digital, e boa parte da prática de mercado,
organiza-se em torno do leitor de tela. A medida de perfil de exclusão sugere outro arranjo:
deficiência intelectual e neurodivergência lideram as ocorrências, acima de cegueira. A maior
carga recai sobre quem depende de estrutura semântica, rotulagem consistente e linguagem
previsível — precisamente o que se degrada primeiro quando a acessibilidade é tratada como
conformidade formal, verificada por lista de checagem ao fim do desenvolvimento.

A leitura precisa de uma ressalva metodológica: o número de ocorrências depende da atribuição
de grupos afetados a cada critério, que é uma modelagem do instrumento e não um dado
observado, e um mesmo achado pode afetar mais de um grupo. O que o resultado sustenta é a
ordem de grandeza relativa, não uma estimativa populacional.

A razão entre ocorrências e achados distintos, por sua vez, é diagnóstica de outro modo. As
79 ocorrências por achado no grupo de visão de cores revelam o defeito de sistema de design:
corrigi-lo em um lugar resolveria centenas de elementos. É exatamente o tipo de achado que o
amortecimento logarítmico do índice de atrito evita superponderar, e é também o tipo de achado
que sugere onde a correção tem melhor relação entre custo e efeito.

### 4.7 A periodicidade como parte do método

A série de treze dias permite responder a uma objeção que a auditoria pontual não consegue
sequer formular: as barreiras medidas são propriedade do portal ou do dia em que ele foi
medido?

Para a maior parte do que se mediu, a resposta é inequívoca. Três plataformas repetiram, por
doze dias, o mesmo conjunto de critérios violados, elemento por elemento. Barreiras que
sobrevivem a doze ciclos de publicação não são falha de conteúdo; estão no componente
reutilizado e no processo que o homologa sem verificar acessibilidade. Isso desloca o alvo da
recomendação: corrigir página é enxugar gelo, e o ponto de intervenção eficiente é o padrão de
componente e o requisito de contratação — argumento que a subseção 4.9 desenvolve.

Mas a resposta não é uniforme, e é aí que está a contribuição da série. Duas barreiras se
moveram, em direções opostas e com significados opostos. No portal municipal de serviços, um
controle inoperável por teclado — risco crítico, sem rota alternativa, na página do
atendimento de urgência — esteve presente em cinco dias, ausente em quatro e presente
novamente em três. Uma auditoria realizada em 26 de agosto teria certificado a ausência da
barreira que uma auditoria de 30 de agosto teria encontrado. Nenhuma das duas estaria errada
sobre o instante; ambas estariam erradas sobre o portal.

No portal federal de saúde, o movimento foi o inverso: uma violação de alternativa textual
introduzida entre 23 e 24 de agosto, presente em todas as páginas e nos dois perfis, e não
corrigida em nenhum dos oito dias observados seguintes. Nesse caso, a auditoria pontual
anterior à data teria produzido um retrato favorável de um portal que estava a um dia de
piorar — e nada, no relatório, indicaria a possibilidade.

A consequência prática interessa mais ao regime jurídico do que ao método. O dever do art. 63
da Lei Brasileira de Inclusão é continuado: o portal precisa ser acessível enquanto for
oferecido, e não no dia da vistoria. Um regime de verificação que produz um laudo por exercício
mede uma amostra de tamanho um de um processo que varia — e, pior, cria o incentivo previsível
de conformidade concentrada na data conhecida. A auditoria contínua não é uma versão mais
frequente da auditoria pontual; é o único desenho cuja unidade de observação corresponde à
estrutura temporal do dever que pretende verificar.

A série também expôs o requisito que o instrumento precisou incorporar para sustentar essa
afirmação. Uma verificação contínua acumula, necessariamente, dias em que a coleta falha — e um
instrumento que converte ausência de observação em conformidade transforma sua própria
instabilidade em elogio ao objeto auditado. A correção descrita na subseção 3.2 é, por isso,
menos um detalhe de implementação do que uma condição de validade: **em auditoria contínua,
"não sei" precisa ser um valor representável**, distinto de "está conforme" e de "não está
conforme". Ferramentas que reportam percentuais de acessibilidade sem representar esse terceiro
estado publicam, em cada falha de rede, um atestado de conformidade sobre o vazio.

### 4.8 Limites do estudo

Os limites a seguir devem acompanhar qualquer leitura dos resultados.

A **cobertura é parcial**: 27 dos 50 critérios admitem veredito automático, e apenas para
alguns modos de falha. O valor é coerente com o teto empírico reportado na literatura (Vigo;
Brown; Conway, 2013) e reforça que ausência de achado não equivale a conformidade. A
concentração das violações nos princípios perceptível e operável, aqui como em Alajarmeh
(2021), é em parte propriedade do objeto e em parte propriedade do método: são os princípios
que a verificação automática alcança melhor, e a leitura precisa considerar as duas causas.

As **áreas autenticadas não foram auditadas**, o que deixa fora da amostra as telas de maior
consequência assistencial e torna os índices possivelmente otimistas.

A **amostra é pequena**: cinco portais, com apenas um no estrato estadual. A amostragem foi
intencional e não comporta inferência para o universo nacional; os testes são descritivos, e a
**pseudorreplicação** — páginas do mesmo portal compartilham template e equipe — é mitigada
pela agregação por portal reportada em paralelo, não eliminada. A série diária **não amplia a
amostra de portais**: doze observações do mesmo portal são doze observações de um portal, e
tratá-las como doze unidades independentes inflaria o *n* de forma ainda mais grave que a
pseudorreplicação entre páginas. Ela responde a uma pergunta diferente — a de persistência —,
não à de generalização.

A **série é curta e tem um único ponto no dia**. Treze dias detectam mudança, mas não
caracterizam sazonalidade, não distinguem manutenção programada de regressão, e não alcançam
variações intradiárias: a coleta ocorre uma vez por dia, sempre no mesmo horário, e uma
barreira que existisse apenas fora dessa janela seria invisível ao estudo. A escolha de
horário fixo, necessária para não confundir mudança do portal com carga do servidor, tem esse
custo declarado. A atribuição de causa às mudanças observadas também permanece fora do
alcance do método: o instrumento constata que o critério 2.1.1 deixou de ser violado em 24 de
agosto e voltou a sê-lo em 29, mas não distingue correção revertida, variante de página
servida por infraestrutura de cache ou implantação parcial — a distinção exigiria informação
que só o órgão responsável possui.

Os **dias sem observação são parte da série, e não ruído removido**. Dos treze dias, um não
produziu veredito, e a série é reportada com essa lacuna explícita. O procedimento evita o
viés que o descarte silencioso produziria, mas não elimina o fato de que doze dias observados
são menos do que treze.

Três limites menores completam a lista. O **preço do dado é parâmetro externo**, coletado e
datado, mas é oferta comercial que muda, e o valor de uma operadora não representa o mercado.
Os **critérios da versão 2.2 estão fora do escopo**, notadamente o de tamanho do alvo de
toque, relevante para o uso móvel que os próprios dados sugerem ser predominante. E há **viés
conhecido e medido na sonda de legibilidade**, que subconta hiatos e superestima a facilidade
de leitura — erro na direção conservadora.

Acima de todos, permanece o limite estrutural do método: a auditoria automática não substitui
a avaliação com usuários reais de tecnologia assistiva. A evidência de que apenas metade dos
problemas efetivamente vividos por usuários cegos corresponde a critério de sucesso das
diretrizes (Power *et al.*, 2012) delimita o alcance de qualquer instrumento desta natureza,
inclusive deste. O que se propõe não é substituto da avaliação com usuários, e sim um
mecanismo de monitoramento contínuo, de baixo custo marginal, capaz de estabelecer um piso e
de dirigi-lo a quem tem competência para exigir correção.

### 4.9 Implicações para a política pública

Três implicações decorrem dos achados.

A primeira é o subaproveitamento do art. 64 da Lei Brasileira de Inclusão, que permite
condicionar a aprovação de projetos e o financiamento com recursos públicos à observância das
regras de acessibilidade. A via orçamentária é instrumento de indução mais rápido que a
judicial, e incide sobre o momento em que a barreira é criada — a contratação — e não sobre o
momento em que ela é constatada.

A segunda é o valor da auditoria contínua e pública como mecanismo de responsabilização.
Relatórios acessíveis, reexecutáveis e endereçados ao gestor e ao órgão de controle mudam o
destinatário da informação: o dado deixa de circular apenas entre desenvolvedores.

A terceira é a ausência de regulamentação do selo de acessibilidade digital previsto no art.
63, § 1º, da Lei Brasileira de Inclusão, que priva o sistema de um mecanismo oficial de
aferição — e, na prática, transfere a órgãos de controle e ao Ministério Público uma função
que a lei previu como administrativa.

Cabe, por fim, a ressalva que o próprio instrumento reproduz em todas as suas saídas: as
proposições jurídicas aqui apresentadas indicam fundamentos normativos aplicáveis segundo uma
matriz documentada e contestável, e não constituem parecer jurídico nem prova pericial. Sua
adequação ao caso concreto depende de análise profissional, que envolve elementos que nenhuma
ferramenta verifica — a identificação do sujeito obrigado em arranjos de contratação
complexos e a eventual incidência de excludentes, entre outros.

### 4.10 Trabalhos futuros

Quatro desdobramentos são prioritários: avaliação com usuários reais de tecnologia assistiva,
que nenhuma auditoria automática substitui; **extensão da série diária**, que treze dias
apenas inauguram — uma janela de meses permitiria caracterizar sazonalidade, associar mudanças
a ciclos de publicação e estimar o tempo de permanência de uma barreira, que é a grandeza de
interesse para a exigibilidade; extensão a aplicativos móveis nativos, onde reside parte
relevante do acesso; e modelo de efeitos mistos, com portal como efeito aleatório e dia como
medida repetida, para tratar formalmente a pseudorreplicação que este desenho apenas declara e
mitiga.

---

## 5 Considerações finais

Este trabalho desenvolveu, aferiu e aplicou um instrumento que produz, do mesmo dado, a
afirmação técnica e a proposição jurídica correspondente, com procedência auditável. A
aferição não produziu falsos positivos e detectou 18 das 20 barreiras plantadas, deixando três
fora do alcance automático por exigirem julgamento semântico — evidência, produzida pelo
próprio instrumento, contra a leitura de que auditoria automática atesta acessibilidade.

Aplicado a cinco plataformas de saúde com incidência no Rio de Janeiro, encontrou 125
violações confirmadas em 16 auditorias de página. Todas apresentaram barreira sem rota
alternativa, e o critério relativo a nome, função e valor dos componentes foi violado em todas
elas, nas três esferas. Essa prevalência total, em amostra estratificada, aponta falha
estrutural do ecossistema e desloca a resposta adequada da correção pontual para os padrões de
desenvolvimento e os requisitos de contratação.

A série de treze dias converteu a auditoria contínua de desenho em resultado. Três plataformas
repetiram, dia após dia, exatamente o mesmo conjunto de critérios violados — o que caracteriza
a barreira típica como estrutural, e não circunstancial. Duas mudaram: em uma, uma barreira
crítica de operação por teclado, na página do atendimento de urgência, esteve ausente por
quatro dias e voltou; em outra, uma violação de alternativa textual foi introduzida e
permaneceu. A conclusão que daí se extrai não é sobre esses portais, e sim sobre o método:
como o dever do art. 63 é continuado, uma verificação que produz um laudo por exercício mede
uma amostra de tamanho um de um processo que varia.

A contribuição metodológica que se pretende oferecer é menos o valor de qualquer índice do que
quatro exigências que o instrumento incorpora e que a literatura da área frequentemente
dispensa: declarar a cobertura em toda saída, de modo que nenhum percentual seja lido sobre
denominador oculto; jamais converter veredito indeterminado em violação, mantendo separadas a
detecção de falha e a indicação de revisão humana; **jamais converter ausência de observação em
conformidade**, mantendo o "não sei" como valor representável, distinto de "conforme" e de "não
conforme"; e vincular cada achado a um dispositivo determinado, com sujeito obrigado e via de
exigibilidade, para que o relatório encontre quem tem competência para agir sobre ele.

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
