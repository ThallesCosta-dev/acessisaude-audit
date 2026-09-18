# Entrega de 09 a 11/09/2026: grupo, revista escolhida e introdução do artigo

**Identificação do grupo, revista escolhida e introdução do artigo científico, conforme a atividade proposta na disciplina 5-PJS 2026.2_Noturno (professor Ricardo Marciano)**

## 1. Identificação do grupo e tema escolhido

Conforme solicitado na atividade, o grupo escolheu uma revista científica e um dos temas propostos para o desenvolvimento do projeto em forma de artigo. A identificação completa do trabalho é apresentada a seguir.

| | |
|---|---|
| Componentes do grupo | Thalles Ferreira Costa; Bruno de Araujo de Jesus; Jonathas Batista |
| Tema escolhido | Tema 6 — Avaliador Automático de Acessibilidade e Direitos Digitais em Saúde |
| Título do projeto (MVP de software) | AcessiSaúde-Audit: Ferramenta Computacional de Auditoria Contínua de Acessibilidade Web (WCAG/LBI) para Plataformas Públicas de Saúde |
| Título do artigo científico | Auditoria Algorítmica de Acessibilidade em Plataformas Digitais de Saúde no Rio de Janeiro: Uma Análise Interdisciplinar sob a Ótica da LBI e do Direito à Saúde |
| Título ajustado às normas da revista | Acessibilidade digital em plataformas públicas de saúde no Rio de Janeiro: auditoria automatizada contínua e qualificação jurídica das barreiras |
| Áreas interdisciplinares | Ciência da Computação / Tecnologia da Informação (TI); Saúde Coletiva / Saúde Pública |
| Revista escolhida | RECIIS — Revista Eletrônica de Comunicação, Informação & Inovação em Saúde (Icict/Fiocruz) |
| Data da entrega | 15/09/2026 |

## 2. Revista escolhida e normas incorporadas

**Reciis — Revista Eletrônica de Comunicação, Informação e Inovação em Saúde** (Fiocruz/Icict, Rio de Janeiro). ISSN 1981-6278. Periódico de acesso aberto, avaliação duplo-cega, sem taxa de publicação.

Seção pretendida: **Artigos originais**.

Normas da revista já incorporadas ao manuscrito:

| Exigência da Reciis | Situação no manuscrito |
|---|---|
| 40 a 60 mil caracteres com espaços, do início ao fim do documento | 59.984 caracteres, conferidos por script |
| Título, resumo e palavras-chave em português, inglês e espanhol | Atendido; resumos com 150, 146 e 146 palavras (limite: 150) |
| Cinco palavras-chave por idioma, separadas por ponto e vírgula | Atendido |
| Seções numeradas: introdução, metodologia, resultados, discussão, considerações finais | Atendido |
| Citação autor-data (NBR 10520/2023) e referências NBR 6023/2025 | Atendido, 25 referências, todas citadas no corpo |
| Página A4, margens de 2 cm, Arial 11, espaçamento 1,5 | A aplicar na conversão do manuscrito para `.docx` |
| Manuscrito sem identificação de autoria (avaliação duplo-cega) | Atendido; folha de rosto em documento separado |

Justificativa da escolha: a revista cobre, entre suas temáticas, tecnologias de informação e comunicação aplicadas à saúde, indicadores e monitoramento de políticas de saúde, e políticas de comunicação, informação e saúde. O artigo dialoga com trabalho publicado na própria Reciis (Vieira; Caniato; Yonemotu, 2017) e com o campo da informação em saúde (Torres; Mazzoni; Alves, 2002; Moraes; González de Gómez, 2007).

## 3. Artigo iniciado: introdução

O texto abaixo é a seção 1 do manuscrito, já redigida no formato da revista (sistema autor-data, NBR 10520/2023). No manuscrito, as subseções correspondem a 1.1 a 1.4.

**Palavras-chave:** Pessoas com Deficiência; Acesso aos Serviços de Saúde; Saúde Digital; Direito à Saúde; Exclusão Digital.

### 3.1 O deslocamento do acesso

Quando um serviço público de saúde migra para o meio digital, a acessibilidade da interface deixa de ser questão de usabilidade e passa a ser condição de exercício de um direito. Um botão de confirmação de agendamento que não recebe foco do teclado não entrega à pessoa com deficiência motora uma experiência ruim: entrega-lhe a ausência da consulta.

O art. 196 da Constituição Federal estabelece a saúde como direito de todos e dever do Estado, garantido mediante políticas de acesso universal e igualitário (Brasil, 1988). Quando o Estado elege o canal digital como via preferencial de um serviço, às vezes como via única, a acessibilidade desse canal incorpora-se ao dever constitucional com a mesma força com que a rampa se incorpora ao dever de acesso físico à unidade de saúde. Digitalizar não cria serviço novo: transporta um serviço existente para um meio em que as barreiras mudam de natureza e conservam a consequência jurídica.

A Lei Brasileira de Inclusão (Brasil, 2015) fornece o elo entre o dever constitucional e o padrão técnico. Seu art. 63, caput, torna obrigatória a acessibilidade nos sítios da internet mantidos por órgãos de governo, "conforme as melhores práticas e diretrizes de acessibilidade adotadas internacionalmente". O dispositivo é, tecnicamente, uma norma em branco: o legislador incorporou o padrão por remissão em vez de descrevê-lo. No arranjo brasileiro, essa remissão se concretiza pelo Modelo de Acessibilidade em Governo Eletrônico (Brasil, 2014a), construído sobre as diretrizes do World Wide Web Consortium, e pelo art. 47 do Decreto 5.296/2004 (Brasil, 2004), que já determinava acessibilidade obrigatória nos portais da administração pública. A Lei 14.129/2021 (Brasil, 2021), que rege a prestação digital de serviços públicos, fecha o circuito: seu art. 3º, XIX, inclui entre os princípios do governo digital a acessibilidade da pessoa com deficiência, nos termos da Lei Brasileira de Inclusão.

### 3.2 A lacuna

Três literaturas se aproximam do problema sem convergir.

A primeira, de avaliação técnica de conformidade, tem no Brasil percurso de duas décadas. Simão e Rodrigues (2005) já registravam barreiras no portal federal de serviços. Freire, Castro e Fortes (2009) mediram 1.232 páginas dos 27 sítios estaduais entre 1996 e 2007 e verificaram avanço modesto, mesmo após o prazo fixado pelo Decreto 5.296/2004: a existência da norma não produziu, por si, efeito mensurável. Silva e La Rue (2015) concluíram que nenhum de oito portais do Executivo estadual atendia integralmente aos critérios mínimos, e Barros *et al.* (2024) chegaram a conclusão equivalente sobre a plataforma centralizada do governo federal. Fora do país, Alajarmeh (2021) auditou os sítios oficiais de saúde pública de 25 países durante a pandemia e encontrou apenas três aprovados em todos os testes, com predomínio de violações dos princípios perceptível e operável, a mesma distribuição que este estudo encontrará.

São trabalhos convergentes no diagnóstico, com três fragilidades recorrentes: raramente declaram a cobertura da ferramenta, o que torna qualquer percentual um número sobre denominador oculto; quase nunca reportam a perda de páginas na coleta; e não qualificam juridicamente o achado, de modo que o relatório se dirige ao desenvolvedor, e não ao gestor ou ao órgão de controle.

A segunda literatura examina a validade das diretrizes e a capacidade das ferramentas de operacionalizá-las. Brajnik (2009) mostrou que critérios anunciados como testáveis variam entre avaliadores. Vigo, Brown e Conway (2013) compararam seis ferramentas e encontraram cobertura de, no máximo, 50% dos critérios de sucesso, com completude entre 14% e 38%. E Power *et al.* (2012), a partir de 1.383 instâncias encontradas por 32 usuários cegos em 16 sítios, verificaram que apenas 50,4% dos problemas vividos correspondiam a algum critério de sucesso. Somadas, as conclusões delimitam o alcance do método automático: ele mede uma parte da norma, e a norma cobre uma parte da experiência.

A terceira literatura, do campo da informação e comunicação em saúde, oferece ao problema o enquadramento mais antigo e menos usado. Torres, Mazzoni e Alves (2002) já formulavam a acessibilidade à informação no espaço digital como condição de acesso, e não como atributo de interface, e Moraes e González de Gómez (2007) mostraram que a informação em saúde é dimensão constitutiva do cuidado e da capacidade de resposta do Estado, e não seu suporte. Vieira, Caniato e Yonemotu (2017) mostraram, a partir das percepções de pessoas com deficiência auditiva, que a barreira comunicacional opera dentro do serviço, e não apenas no acesso a ele; deslocada para o canal digital, ela muda de forma e conserva a natureza. Nessa chave, a barreira de acessibilidade em um portal de saúde é também violação do direito à informação pública, que a Lei de Acesso à Informação (Brasil, 2011) torna explícito ao exigir, no art. 8º, § 3º, VIII, conteúdo acessível às pessoas com deficiência. A literatura jurídica sobre o art. 63, por fim, analisa o dispositivo em chave doutrinária, sem instrumento de mensuração.

A lacuna de que este trabalho trata está na articulação. Não há instrumento que produza, do mesmo dado e com procedência auditável, a afirmação técnica e a proposição jurídica correspondente, indicando qual dispositivo foi violado, quem é o sujeito obrigado e por qual via a obrigação é exigível.

### 3.3 O usuário periférico

A barreira de acesso ao serviço público digital de saúde não é apenas sensorial. Plano pré-pago, aparelho de entrada, rede instável e escolaridade heterogênea obstruem o acesso com o mesmo efeito prático, e frequentemente na mesma pessoa. O peso de uma página, em bytes trafegados, é barreira que as diretrizes não enxergam, porque pressupõem um usuário que já chegou.

Os dados sustentam a sobreposição. O Censo 2022 identificou 14,4 milhões de pessoas com deficiência, 7,3% da população de dois anos ou mais; entre elas, a taxa de analfabetismo era de 21,3%, quatro vezes a das pessoas sem deficiência, e apenas 7,4% haviam concluído o ensino superior, contra 19,5% (IBGE, 2025). A TIC Domicílios 2024 mostra que apenas 3% das pessoas das classes D e E reúnem as condições do indicador de conectividade significativa, contra 73% na classe A, e que 86% de quem tem celular nessas classes acessa a rede exclusivamente por esse aparelho (CGI.br, 2025). São as condições concretas de uso da interface, e as que a homologação em desktop, com banda larga, deixa de simular.

Este estudo adota a expressão *usuário periférico* para designar essa posição composta: quem depende exclusivamente do sistema público de saúde e o acessa por infraestrutura de conectividade precária. A categoria se sobrepõe à de pessoa com deficiência sem substituí-la, e o trabalho mede as duas dimensões separadamente, porque têm fundamentos jurídicos e correções distintos.

### 3.4 Objetivos

**Objetivo geral.** Desenvolver, validar e aplicar um instrumento de auditoria contínua que converta falhas técnicas de acessibilidade em proposições jurídicas fundamentadas.

**Objetivos específicos.** (1) Modelar a correspondência entre os 50 critérios de sucesso de níveis A e AA das diretrizes de acessibilidade para conteúdo web, versão 2.1 (W3C, 2018), e o ordenamento jurídico brasileiro; (2) aferir o instrumento contra conjunto de referência com barreiras conhecidas; (3) aplicá-lo a plataformas de saúde do Rio de Janeiro, estratificadas por esfera federativa; (4) quantificar o custo de acesso em dados móveis como barreira; (5) caracterizar o perfil de exclusão por grupo afetado.

## 4. Referências citadas na introdução

ALAJARMEH, Nancy. Evaluating the accessibility of public health websites: an exploratory cross-country study. **Universal Access in the Information Society**, Berlin, v. 21, n. 3, p. 771-789, 2021. DOI: https://doi.org/10.1007/s10209-020-00788-7.

BARROS, Ygor Santos; OUTÃO, Juliana Carvalho Silva do; SACRAMENTO, Carolina; FERREIRA, Simone Bacellar Leal; PIMENTEL, Mariano Gomes; SANTOS, Rodrigo Pereira dos. Avaliação de acessibilidade da plataforma Gov.br por ferramentas automatizadas. In: LATIN AMERICAN SYMPOSIUM ON DIGITAL GOVERNMENT, 12., 2024. **Anais** [...]. Porto Alegre: Sociedade Brasileira de Computação, 2024. p. 50-61. DOI: https://doi.org/10.5753/wcge.2024.2282.

BRAJNIK, Giorgio. Validity and reliability of web accessibility guidelines. In: INTERNATIONAL ACM SIGACCESS CONFERENCE ON COMPUTERS AND ACCESSIBILITY, 11., 2009, Pittsburgh. **Proceedings** [...]. New York: ACM, 2009. p. 131-138. DOI: https://doi.org/10.1145/1639642.1639666.

BRASIL. [Constituição (1988)]. **Constituição da República Federativa do Brasil de 1988**. Brasília, DF: Presidência da República, [2024]. Disponível em: http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao.htm. Acesso em: 16 ago. 2026.

BRASIL. **Decreto nº 5.296, de 2 de dezembro de 2004**. Regulamenta as Leis nº 10.048, de 8 de novembro de 2000, e nº 10.098, de 19 de dezembro de 2000. **Diário Oficial da União**: seção 1, Brasília, DF, 3 dez. 2004.

BRASIL. **Lei nº 12.527, de 18 de novembro de 2011**. Regula o acesso a informações previsto no inciso XXXIII do art. 5º, no inciso II do § 3º do art. 37 e no § 2º do art. 216 da Constituição Federal. **Diário Oficial da União**: seção 1, edição extra, Brasília, DF, 18 nov. 2011.

BRASIL. Ministério do Planejamento, Orçamento e Gestão. **eMAG**: Modelo de Acessibilidade em Governo Eletrônico. Versão 3.1. Brasília, DF: MPOG, 2014a. Disponível em: https://emag.governoeletronico.gov.br/. Acesso em: 16 ago. 2026.

BRASIL. **Lei nº 13.146, de 6 de julho de 2015**. Institui a Lei Brasileira de Inclusão da Pessoa com Deficiência (Estatuto da Pessoa com Deficiência). **Diário Oficial da União**: seção 1, Brasília, DF, 7 jul. 2015.

BRASIL. **Lei nº 14.129, de 29 de março de 2021**. Dispõe sobre princípios, regras e instrumentos para o Governo Digital e para o aumento da eficiência pública. **Diário Oficial da União**: seção 1, Brasília, DF, 30 mar. 2021.

CGI.BR — COMITÊ GESTOR DA INTERNET NO BRASIL. **Pesquisa sobre o uso das tecnologias de informação e comunicação nos domicílios brasileiros**: TIC Domicílios 2024. São Paulo: CGI.br; NIC.br; Cetic.br, 2025. Disponível em: https://cetic.br/pt/pesquisa/domicilios/. Acesso em: 16 ago. 2026.

FREIRE, André Pimenta; CASTRO, Mário de; FORTES, Renata Pontin de Mattos. Acessibilidade dos sítios web dos governos estaduais brasileiros: uma análise quantitativa entre 1996 e 2007. **Revista de Administração Pública**, Rio de Janeiro, v. 43, n. 2, p. 395-414, 2009. DOI: https://doi.org/10.1590/S0034-76122009000200006.

IBGE — INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA. **Censo demográfico 2022**: pessoas com deficiência — resultados preliminares da amostra. Rio de Janeiro: IBGE, 2025. Disponível em: https://www.ibge.gov.br/. Acesso em: 16 ago. 2026.

MORAES, Ilara Hämmerli Sozzi de; GONZÁLEZ DE GÓMEZ, Maria Nélida. Informação e informática em saúde: caleidoscópio contemporâneo da saúde. **Ciência & Saúde Coletiva**, Rio de Janeiro, v. 12, n. 3, p. 553-565, 2007. DOI: https://doi.org/10.1590/S1413-81232007000300002.

POWER, Christopher; FREIRE, André; PETRIE, Helen; SWALLOW, David. Guidelines are only half of the story: accessibility problems encountered by blind users on the web. In: SIGCHI CONFERENCE ON HUMAN FACTORS IN COMPUTING SYSTEMS, 2012, Austin. **Proceedings** [...]. New York: ACM, 2012. p. 433-442.

SILVA, Rosane Leal da; LA RUE, Letícia Almeida de. A acessibilidade nos sites do Poder Executivo estadual à luz dos direitos fundamentais das pessoas com deficiência. **Revista de Administração Pública**, Rio de Janeiro, v. 49, n. 2, p. 315-339, 2015. DOI: https://doi.org/10.1590/0034-7612130130.

SIMÃO, João Batista; RODRIGUES, Georgete. Acessibilidade às informações públicas: uma avaliação do portal de serviços e informações do governo federal. **Ciência da Informação**, Brasília, DF, v. 34, n. 2, p. 234-245, 2005. DOI: https://doi.org/10.1590/S0100-19652005000200009.

TORRES, Elisabeth Fátima; MAZZONI, Alberto Angel; ALVES, João Bosco da Mota. A acessibilidade à informação no espaço digital. **Ciência da Informação**, Brasília, DF, v. 31, n. 3, p. 83-91, 2002. DOI: https://doi.org/10.1590/S0100-19652002000300009.

VIEIRA, Camila Mugnai; CANIATO, Daniela Godoi; YONEMOTU, Bruna Prado Ribeiro. Comunicação e acessibilidade: percepções de pessoas com deficiência auditiva sobre seu atendimento nos serviços de saúde. **Reciis – Revista Eletrônica de Comunicação, Informação e Inovação em Saúde**, Rio de Janeiro, v. 11, n. 2, 2017. DOI: https://doi.org/10.29397/reciis.v11i2.1139.

VIGO, Markel; BROWN, Justin; CONWAY, Vivienne. Benchmarking web accessibility evaluation tools: measuring the harm of sole reliance on automated tests. In: INTERNATIONAL CROSS-DISCIPLINARY CONFERENCE ON WEB ACCESSIBILITY, 10., 2013, Rio de Janeiro. **Proceedings** [...]. New York: ACM, 2013. DOI: https://doi.org/10.1145/2461121.2461124.

W3C — WORLD WIDE WEB CONSORTIUM. **Web Content Accessibility Guidelines (WCAG) 2.1**. W3C Recommendation, 5 jun. 2018. Disponível em: https://www.w3.org/TR/WCAG21/. Acesso em: 16 ago. 2026.
