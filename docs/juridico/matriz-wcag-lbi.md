# Matriz WCAG 2.1 ↔ ordenamento jurídico brasileiro

> Versão discursiva e revisável da matriz implementada em
> [`domain/mapping.py`](../../backend/src/acessisaude_audit/domain/mapping.py).
> A versão executável é a fonte da verdade; este documento existe para que a fundamentação
> possa ser lida, contestada e citada sem ler Python.
>
> Consulta interativa: rota `/referencia/criterios` da API, ou a tela **Matriz WCAG e LBI**
> do painel.

---

## 1. O problema da vinculação

Uma falha técnica não é, por si, uma violação de direito. Para que se torne, é preciso que
exista **uma norma que a proíba** e **um sujeito obrigado a cumpri-la**. Trabalhos da área
frequentemente colapsam essas camadas, citando o mesmo bloco de leis para toda e qualquer
falha — o que dilui a força argumentativa e impede graduar a gravidade.

Este projeto separa três camadas e as reúne explicitamente em cada achado:

| Camada | Pergunta | Fonte no sistema |
|---|---|---|
| **Técnica** | O que está errado? | axe-core, sondas próprias |
| **Normativa** | Qual padrão foi descumprido? | WCAG 2.1, critério identificado |
| **Jurídica** | Qual dever foi violado, por quem, exigível como? | esta matriz |

---

## 2. O elo: art. 63 da LBI

O dispositivo que juridiciza a WCAG no Brasil é o **art. 63, caput, da Lei 13.146/2015**:

> É obrigatória a acessibilidade nos sítios da internet mantidos por empresas com sede ou
> representação comercial no País ou por órgãos de governo, para uso da pessoa com
> deficiência, garantindo-lhe acesso às informações disponíveis, **conforme as melhores
> práticas e diretrizes de acessibilidade adotadas internacionalmente**.

A remissão às "melhores práticas e diretrizes adotadas internacionalmente" é uma **norma em
branco**: o legislador não descreveu o padrão técnico, incorporou-o por referência. No
contexto brasileiro, essa remissão aponta para a WCAG por dois vetores concorrentes:

1. **O eMAG 3.1** (Modelo de Acessibilidade em Governo Eletrônico), padrão oficial da
   administração pública federal, construído sobre a WCAG.
2. **O art. 47 do Decreto 5.296/2004**, que já determinava acessibilidade obrigatória nos
   portais da administração pública e foi, na prática administrativa, o veículo de adoção do
   eMAG.

O efeito é que **descumprir a WCAG em portal de órgão público brasileiro é descumprir o art.
63 da LBI** — não por analogia, mas por incorporação normativa.

---

## 3. Arquitetura da matriz

A vinculação se dá em três camadas cumulativas.

### 3.1 Camada geral — incide sobre qualquer barreira

| Dispositivo | Comando |
|---|---|
| **LBI, art. 63, caput** | Obrigatoriedade de acessibilidade em sítios de órgãos de governo |
| **LBI, art. 3º, IV, "d"** | Tipifica barreiras nas comunicações e na informação |
| **LBI, art. 4º** | Igualdade e não discriminação; recusa de adaptação razoável é discriminação |
| **Decreto 5.296/2004, art. 47** | Acessibilidade obrigatória nos portais da administração pública |
| **eMAG 3.1** | Padrão técnico oficial da administração federal |

### 3.2 Camada de saúde — incide sobre todos os alvos deste projeto

| Dispositivo | Comando |
|---|---|
| **LBI, art. 18** | Atenção integral à saúde da PcD; § 4º, IV exige comunicação e informação adequadas |
| **CF/88, art. 196** | Saúde como direito de todos e dever do Estado, com acesso universal e igualitário |
| **Convenção da ONU, art. 25** (Decreto 6.949/2009) | Direito ao mais elevado padrão de saúde, sem discriminação |

A Convenção tem **status de emenda constitucional** (art. 5º, § 3º, CF), o que a coloca acima
da legislação ordinária na hierarquia normativa — fato relevante para a gradação de gravidade.

### 3.3 Camada específica — incide conforme a natureza da barreira

| Natureza | Dispositivo acrescido |
|---|---|
| Dependência de tecnologia assistiva | LBI, art. 74 |
| Acesso à informação pública | CF/88, art. 5º, XIV; LAI, art. 8º, § 3º, VIII |
| Conteúdo audiovisual / pessoa surda | Decreto 5.626/2005, art. 26 |
| Qualidade do serviço público | Lei 13.460/2017, art. 5º |
| Autonomia no uso | LBI, art. 3º, I |
| Atendimento prioritário | LBI, art. 9º, V |
| Barreira absoluta, sem rota alternativa | Convenção da ONU, art. 9 |

Essa terceira camada é o que evita o vício de citar o mesmo bloco de leis para tudo.

---

## 4. Gradação do risco jurídico

A escala **não** é a do `impact` do axe-core, que mede gravidade técnica. São dimensões
independentes, e ambas são reportadas. Um defeito tecnicamente "menor" pode ser
juridicamente crítico se ocorrer no botão de confirmação de uma consulta.

A graduação combina três vetores:

1. **Essencialidade** do serviço obstruído;
2. **Existência de rota alternativa** acessível;
3. **Reversibilidade** do dano.

| Risco | Peso | Definição | Critérios |
|---|---|---|---|
| **Crítico** | 12 | Impede o acesso a serviço de saúde essencial, sem rota alternativa; risco de dano à saúde ou perda de prazo/vaga irrecuperável | **4** |
| **Alto** | 7 | Impede a conclusão da tarefa por um grupo identificável | **18** |
| **Moderado** | 3 | Exige esforço desproporcional ou auxílio de terceiro, ferindo a autonomia do art. 3º, I | **19** |
| **Baixo** | 1 | Dificulta o uso, mas há rota alternativa | **9** |

### Os quatro critérios de risco crítico

| Critério | Barreira | Fundamento da gradação |
|---|---|---|
| **2.1.1** Teclado | Controle inoperável sem mouse | Não há rota alternativa: para a pessoa com deficiência motora ou usuária de leitor de tela, a função inexiste |
| **2.1.2** Sem bloqueio do teclado | Armadilha de foco | Aprisiona: impede tanto concluir quanto abandonar a tarefa |
| **2.3.1** Três flashes | Conteúdo intermitente | Dano à **integridade física** (crise epiléptica), não apenas ao acesso |
| **4.1.2** Nome, função, valor | Widget sem exposição ARIA | O controle não existe para a tecnologia assistiva — forma mais severa da barreira do art. 3º, IV, "d" |

---

## 5. Vias de exigibilidade

Cada dispositivo declara as vias típicas de exigência em caso de descumprimento. A informação
é operacional: muda o destinatário do relatório.

| Via | Quando é a mais adequada |
|---|---|
| **Ministério Público** | Descumprimento continuado, com dever claro e sujeito determinado |
| **Ação civil pública** | Interesse difuso de toda a população com deficiência atendida |
| **Controle externo (TCU/TCE)** | Art. 64 da LBI permite atacar pela via orçamentária: acessibilidade como requisito de aprovação de projetos e de financiamento com recursos públicos |
| **Ouvidoria do SUS** | Primeira via, menos onerosa, com prazo de resposta |
| **Conselho de direitos da PcD** | Articulação política e acompanhamento |
| **Ação individual** | Dano concreto a pessoa determinada |

A via do **art. 64** é frequentemente subutilizada e merece destaque no artigo: ela permite
condicionar financiamento à conformidade, o que é instrumento de indução mais rápido que a
via judicial.

---

## 6. Barreiras sem correspondência na WCAG

Duas dimensões medidas pelo projeto não correspondem a nenhum critério de sucesso, e por isso
recebem fundamentação jurídica própria, declarada em `legal_thesis_override`.

### 6.1 Custo de acesso em dados móveis

> O custo de dados exigido para acessar o serviço digital de saúde transfere ao cidadão um
> ônus econômico como condição de exercício de direito fundamental. Quando esse ônus recai
> desproporcionalmente sobre a população de menor renda — a mesma que depende exclusivamente
> do SUS —, o acesso deixa de ser universal e igualitário, em desacordo com o art. 196 da
> CF/88 e com o dever de informação adequada do art. 18, § 4º da LBI. A parcela do tráfego
> destinada a terceiros agrava a situação: o usuário custeia recursos que não lhe prestam o
> serviço público solicitado.

Dispositivos: CF/88 art. 196; LBI art. 18; Lei 13.460/2017 art. 5º; CF/88 art. 5º, XIV.

### 6.2 Legibilidade do conteúdo

> A publicação de informação de saúde em registro linguístico inacessível à população
> destinatária esvazia materialmente o dever de oferta de comunicação e informação adequadas
> (art. 18, § 4º, IV, LBI) e o dever de transparência ativa (art. 8º, § 3º, LAI). A informação
> torna-se disponível sem se tornar acessível.

Dispositivos: LBI art. 18; LAI art. 8º, § 3º, VIII; Lei 13.460/2017 art. 5º.

⚠️ Esta sonda é **heurística** e, por contrato verificado em teste, jamais produz veredito
de violação — apenas sinaliza para revisão editorial. Índices de legibilidade medem estrutura
superficial, não compreensão: texto simples pode ser vago, texto denso pode ser preciso e
necessário.

---

## 7. Completude

A matriz cobre **50 de 50** critérios do escopo. A completude é verificada em teste
automatizado (`test_matriz_e_completa`) e exposta na rota
`/referencia/integridade-da-matriz`, de modo que um revisor possa conferi-la sem ler código.

A exigência não é formal. Um critério sem mapeamento produziria um achado juridicamente mudo:
a ferramenta detectaria a falha e não conseguiria dizer que dever foi violado — que é
precisamente o que ela existe para fazer.

Dois testes adicionais protegem a qualidade, e não apenas a existência, do mapeamento:

- toda tese jurídica tem ao menos 80 caracteres (ela vai literalmente para o relatório e para
  o artigo);
- toda conduta corretiva tem ao menos 30 caracteres e descreve ação concreta.

---

## 8. Como contestar esta matriz

A matriz é uma **proposta interpretativa**, não uma verdade estabelecida. Discordâncias
legítimas são esperadas, sobretudo na gradação de risco, que envolve juízo de valor sobre
essencialidade de serviço.

Para propor alteração:

1. Editar `CRITERION_MAPPINGS` em `domain/mapping.py`, com a tese revisada.
2. Registrar a mudança em `docs/adr/`, com a justificativa doutrinária.
3. Verificar que a suíte continua passando (`pytest tests/unit/test_dominio_normativo.py`).
4. Reindexar as varreduras já coletadas (`ScanRepository.reindex`) — o risco jurídico é
   derivado, e o documento JSON permanece intacto.

O passo 4 é possível porque o JSON é a fonte da verdade e o índice relacional é integralmente
derivável dele: mudar a interpretação jurídica **não exige revarrer portal algum**.

---

## Referências normativas

BRASIL. **Constituição da República Federativa do Brasil de 1988**. Brasília, DF: Senado Federal, 1988.

BRASIL. **Decreto nº 5.296, de 2 de dezembro de 2004**. Regulamenta as Leis nº 10.048/2000 e nº 10.098/2000. Diário Oficial da União, Brasília, DF, 3 dez. 2004.

BRASIL. **Decreto nº 5.626, de 22 de dezembro de 2005**. Regulamenta a Lei nº 10.436/2002. Diário Oficial da União, Brasília, DF, 23 dez. 2005.

BRASIL. **Decreto nº 6.949, de 25 de agosto de 2009**. Promulga a Convenção Internacional sobre os Direitos das Pessoas com Deficiência. Diário Oficial da União, Brasília, DF, 26 ago. 2009.

BRASIL. **Lei nº 12.527, de 18 de novembro de 2011**. Regula o acesso a informações. Diário Oficial da União, Brasília, DF, 18 nov. 2011.

BRASIL. **Lei nº 13.146, de 6 de julho de 2015**. Institui a Lei Brasileira de Inclusão da Pessoa com Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.

BRASIL. **Lei nº 13.460, de 26 de junho de 2017**. Dispõe sobre participação, proteção e defesa dos direitos do usuário dos serviços públicos. Diário Oficial da União, Brasília, DF, 27 jun. 2017.

BRASIL. Ministério do Planejamento. **eMAG — Modelo de Acessibilidade em Governo Eletrônico**. Versão 3.1. Brasília, DF, 2014.

W3C. **Web Content Accessibility Guidelines (WCAG) 2.1**. W3C Recommendation, 5 jun. 2018.
