# Submissão à Reciis — folha de rosto, conformidade e pendências

Documento de apoio. **Não faz parte do manuscrito** e não deve ser anexado à submissão.
Manuscrito: [`manuscrito-reciis.md`](manuscrito-reciis.md).

> **Duas versões.** O estudo existe em duas formas: a reduzida
> ([`manuscrito-reciis.md`](manuscrito-reciis.md), 59.984 caracteres do início ao fim do
> documento, referências incluídas), preparada para a Reciis, e a estendida
> ([`manuscrito-extenso.md`](manuscrito-extenso.md), 81,2 mil), para periódico de limite maior.
> A diferença é só de extensão: a estendida tem onze tabelas em vez de cinco, mantém a
> granularidade das subseções da série e traz os parágrafos da Discussão na forma anterior ao
> corte.
>
> **Toda correção de conteúdo entra nas duas.** `python scripts/conferir_manuscritos.py`
> verifica que os números, as citações e os resumos coincidem, e que a reduzida continua no
> limite, contado do início ao fim do documento. Rodar antes de qualquer submissão.
>
> **Revisão de 09/09/2026.** Os pontos da [autoavaliação](autoavaliacao-reciis.md) foram
> corrigidos nas duas versões: título, Tabela 3, hipóteses H2 e H4, comparação por portal,
> saturação do IAN, Lei 14.129/2021, diálogo com o campo da informação e comunicação em saúde
> (três referências novas), separação entre Resultados e Discussão, e extensão. As figuras foram
> regeradas a partir dos JSON do ramo `serie-temporal`.

---

## 1. Enquadramento

| Item | Decisão |
|---|---|
| Seção | **Artigos originais** (40–60 mil caracteres com espaços) |
| Extensão atual | **59.984** caracteres do início ao fim do documento, referências incluídas (corpo sem referências: 53,8 mil) — ver § 3.1 |
| Idioma | Português, com título, resumo e palavras-chave em inglês e espanhol |
| Avaliação | Duplo-cega — manuscrito sem identificação de autoria |
| Comitê de ética | Não aplicável (sem seres humanos, sem dados pessoais); declarado na subseção 2.9 |

---

## 2. Conteúdo para a Folha de Rosto

A folha de rosto é documento próprio da revista, baixado do sistema, preenchido e anexado em
formato fechado (`.pdf`). Conteúdo a transcrever:

**Autoria**
Thalles Costa — thalles.costa@ioc.fiocruz.br
Instituição: Fundação Oswaldo Cruz, Instituto Oswaldo Cruz. Rio de Janeiro, RJ, Brasil.
ORCID: ⬜ 0009-0000-3016-6640
Currículo Lattes (campo URL): http://lattes.cnpq.br/2268192231190691
Resumo da biografia (maior titulação, no formato pedido pela revista): ⬜ *preencher*
Autor correspondente: sim — indicar como contato principal na lista de coautores.

**Contribuição dos autores** (formato do periódico, ver seção *Editorial information* dos
artigos publicados)
Concepção e desenho do estudo: Thalles Costa. Coleta de dados: Thalles Costa. Análise dos
dados: Thalles Costa. Interpretação dos dados: Thalles Costa. Redação e revisão crítica do
conteúdo intelectual, aprovação da versão final e responsabilidade por todos os aspectos
legais e científicos relacionados à exatidão e à integridade do estudo: Thalles Costa.

**Declaração de conflito de interesses**
O autor declara não haver conflito de interesses.

**Fontes de financiamento**
⬜ *Declarar*. Se não houve, registrar: "A pesquisa não recebeu financiamento."

**Considerações éticas**
O estudo não envolveu seres humanos nem dados pessoais. A coleta restringiu-se ao documento
renderizado de páginas web públicas, sem autenticação, sem preenchimento de formulários e sem
transmissão de dados, não se enquadrando nas hipóteses de submissão ao sistema CEP/Conep nos
termos da Resolução CNS 510/2016.

**Apresentação prévia**
Não houve apresentação prévia.

---

## 3. Conformidade com as normas da revista

### 3.1 Contagem de caracteres — resolvida pela letra da norma

A autoavaliação da submissão publicada pela revista (atualização de 10/08/2023) diz, para
artigos originais: "entre 40 e 60 mil caracteres com espaços, **do início ao fim do
documento**". A medição de artigos publicados sugere prática mais tolerante:

| Artigo | Páginas | Corpo, com tabelas | Referências |
|---|---|---|---|
| v. 20, e3739 | 22 | 54.801 | 19.764 |
| v. 20, outro original | 18 | 50.280 | 17.041 |

Os dois excederiam 60 mil com as referências. Optou-se por **cumprir a letra da norma**, o que
elimina a dependência de consulta à secretaria. Contagem de 09/09/2026, pelo
`scripts/conferir_manuscritos.py`, descontada a sintaxe Markdown:

| Componente | Caracteres |
|---|---|
| Corpo sem referências (título, resumos, texto, tabelas, legendas) | 53.800 |
| Referências | 6.184 |
| **Documento inteiro (conta para o limite)** | **59.984** |

Chegou-se a esse número em duas rodadas: de 91,2 mil para 60 mil de corpo (troca do bloco
transversal, material de aparelho para o suplementar, treze tabelas em cinco) e, em 09/09, mais
cerca de 12 mil, cortados sobretudo na Discussão (4.2 a 4.7), nas frases interpretativas dos
Resultados e nos parágrafos descritivos de 3.3, 3.4 e 3.12. Nenhum número, citação ou achado
foi perdido; a versão estendida preserva o texto anterior ao corte. A conversão para `.docx`
precisa refazer a contagem no editor, porque a sintaxe Markdown não existe lá e a margem é de
16 caracteres.

**Já atendido no manuscrito**

- [x] Títulos em português, inglês e espanhol, sem caixa alta e sem abreviações, com termos de
      recuperação consolidados ("acessibilidade digital", "auditoria automatizada") e a série
      sinalizada por "contínua"
- [x] Resumos nos três idiomas, com **150, 146 e 146 palavras** (limite: 150)
- [x] Resumos sem abreviaturas e sem citações
- [x] Cinco palavras-chave por idioma, separadas por ponto e vírgula
- [x] Hierarquia de seções sinalizada numericamente
- [x] Sistema autor-data, com sobrenomes em maiúsculas e minúsculas (NBR 10520/2023)
- [x] Referências em NBR 6023/2025, com prenomes por extenso e DOI quando disponível
- [x] Tabelas com título **acima**, sem linhas internas, com indicação de fonte
- [x] Figuras com título **abaixo**, com indicação de fonte
- [x] Siglas descritas por extenso na primeira ocorrência
- [x] Sem identificação de autoria no corpo do texto, e sem o nome do instrumento
- [x] Resultados sem interpretação: as frases de leitura foram movidas para 4.1 e 4.7
- [x] Todas as hipóteses de 2.7 têm resultado (H1 e H3 em 3.7 e 3.8; H2 em 3.7; H4 em 3.9) e
      são retomadas nas Considerações finais

**A fazer na conversão para `.docx` / `.odt`**

- [ ] Página A4, margens de 2 cm, fonte **Arial 11**, espaçamento **1,5** em todo o texto,
      inclusive resumos e referências
- [ ] Tabelas em espaçamento simples, **tamanho 10**, construídas com a ferramenta de tabela
      do editor (não como imagem), **abertas nas laterais** e sem linhas internas
- [ ] Remover a identificação do autor das propriedades do arquivo
      (Arquivo → Informações → Inspecionar documento → Remover tudo)
- [ ] Remover a vinculação a gerenciador de referências, se houver
- [ ] Remover a nota editorial em bloco de citação do início do manuscrito
- [ ] Inserir as figuras no corpo do texto, no ponto em que são citadas, **e** anexá-las
      individualmente na submissão em formato editável — usar os arquivos `.svg` de
      [`figuras/`](figuras/), não os `.png`. As figuras não são versionadas: se a pasta estiver
      vazia, copiar os JSON de `scans-br/` do ramo `serie-temporal` para `data/scans/`, rodar
      `acessisaude reindexar` e `python scripts/gerar_figuras.py` (feito em 09/09/2026)
- [ ] Refazer a contagem de caracteres no editor depois da conversão (margem de 16 caracteres)

**Anexos da submissão**

- [ ] Folha de Rosto preenchida e salva em `.pdf`
- [ ] Declaração de responsabilidade e cessão de direitos, assinada, em `.pdf`
- [ ] Figuras 1 a 5 em arquivo editável (SVG em `docs/artigo/figuras/`, reconstruíveis por `python scripts/gerar_figuras.py`)
- [ ] **Material suplementar**, que o manuscrito cita em 2.2 e 2.4 e precisa existir: (a) uma
      linha por alvo com a justificativa de inclusão, extraída de
      `backend/src/acessisaude_audit/catalog/targets.yaml` (campo `selection_rationale`);
      (b) a matriz dos 50 critérios com os três vetores (essencialidade, rota alternativa,
      reversibilidade) e a faixa de risco resultante, extraída de `docs/juridico/`
- [ ] Metadados de autoria completos no sistema (nome, e-mail, ORCID, Lattes, afiliação por
      extenso na língua original com cidade, estado e país, país, biografia)

---

## 4. Pendências de conteúdo antes de submeter

Em ordem de risco para o parecer.

1. **Decidir onde fechar a série.** A janela está em vinte e dois dias (19/08 a 09/09/2026) e a
   tarefa agendada continua rodando. O que já está garantido: episódio de barreira intermitente
   **fechado** e mensurável, regressão do portal federal com piso de quinze dias observados e
   transição ancorada em cobertura integral dos dois lados, três portais com vinte e um dias de
   variação nula, e um dia em que uma única plataforma ficou sem veredito (06/09), que exercita
   o requisito do § 4.7. O que ainda falta e só o tempo dá: **um segundo episódio de
   intermitência**, sem o qual não se pode dizer com que frequência barreiras mudam, e o
   fechamento da regressão do gov.br, que converteria "≥ 15 dias" em uma duração. Reprocessar custa dois comandos:
   `acessisaude reindexar` e `python scripts/gerar_figuras.py`. Fixar a data de corte no
   [registro da série](../metodologia/registro-da-serie-diaria.md) antes de submeter, e refazer
   a contagem de caracteres depois, porque a série cresce dentro do texto.

3. **Citação da Anatel pelo relatório primário**, e não por veículo especializado.
   Reconferir também os parâmetros de custo nos sítios das operadoras, com captura arquivada.

4. **Anonimato do repositório — resolvido.** O nome do instrumento não aparece em nenhuma das
   duas versões; a subseção 2.9 informa que o endereço será fornecido após a avaliação.

5. **Depósito dos dados primários e do material suplementar com DOI**, e comunicação prévia
   aos órgãos auditados, com o relatório encaminhado. Atenção: `data/scans/` é ignorado pelo
   git, e as 110 varreduras da série existem apenas no ramo remoto `serie-temporal`
   (`scans-br/`). A afirmação de 2.9, de que código e dados estão "depositados em repositório
   público", só é verdadeira depois do depósito. É a única pendência de conteúdo que não pode
   ser resolvida dentro do repositório.

**Resolvidos em 09/09/2026** (detalhe na [autoavaliação](autoavaliacao-reciis.md)): extensão
dentro do limite contado do início ao fim; Tabela 3; H2, H4 e comparação por portal; IAN
saturado retirado do teste; Lei 14.129/2021 em 1.1; terceiro parágrafo de 1.2 reescrito na
chave do direito à informação, com Torres, Mazzoni e Alves (2002) e Moraes e González de Gómez
(2007); interpretação retirada dos Resultados; título novo; material suplementar citado em 2.2
e 2.4; figuras regeradas.

**Resolvidos na revisão anterior.** A revisão de literatura passou de 4 para 9 referências externas
verificadas, com precedente brasileiro direto (Freire; Castro; Fortes, 2009), e a subseção 1.3
deixou de argumentar a categoria de usuário periférico para quantificá-la, com o Censo 2022 e a
TIC Domicílios 2024.

**Resolvido na revisão da série.** A pendência da janela única deixou de existir: o manuscrito
passou a ter componente longitudinal declarado (§ 2.1 e § 2.2), seção de resultados (§ 3.12,
Tabelas 12 e 13, Figura 5), discussão (§ 4.7) e limites reescritos (§ 4.8). A série também
expôs um defeito do instrumento — índice de conformidade máximo em dia sem observação —
corrigido pela [ADR 0010](../adr/0010-indices-nulos-sem-observacao.md) e reportado no próprio
artigo (§ 3.2), por ser contribuição metodológica e não detalhe de implementação.

**Bloco transversal trocado para 04/09/2026.** O corte de 16/08 tinha 16 de 20 auditorias
válidas e reduzia o estrato estadual a duas páginas, por indisponibilidade do portal naquela
janela. A série ofereceu cinco dias de cobertura integral, e o manuscrito passou a usar
04/09: **20 de 20 auditorias, perda nula, estrato estadual com seis páginas**. As duas
afirmações centrais sobreviveram ao *n* maior — barreira absoluta em 20/20 e prevalência total
do critério 4.1.2, agora acompanhado do 1.1.1 —, e as 125 violações passaram a 168. Sumiram, com
a troca, a inconsistência entre o ICA da secretaria estadual nos dois blocos e a limitação mais
citada do estudo, a de duas observações no estrato estadual. Tabelas e figuras foram regeradas
por `python scripts/gerar_figuras.py`, que fixa qual bloco alimenta cada uma.

**Ampliação da janela para 22 dias.** Os cinco dias de 05 a 09/09 não inverteram nada e
acrescentaram um evento novo: em 06/09 só o portal municipal de serviços não respondeu, e a
varredura consta sem veredito para ele apenas, com as demais plataformas observadas. A regressão
do gov.br segue aberta (piso de quinze dias) e nenhum segundo episódio de intermitência ocorreu.
Registro na seção 7 do [registro da série](../metodologia/registro-da-serie-diaria.md).

**Ampliação da janela para 17 dias.** Nenhuma conclusão foi invertida; o que mudou foi a força
das afirmações. O episódio de intermitência fechou e passou a ter duração; a regressão do
portal federal ganhou piso maior e controle de cobertura integral dos dois lados; e uma
hipótese de ciclo semanal de implantação, plausível com treze dias, **não replicou** na semana
seguinte e por isso não chegou ao manuscrito. O registro dessa hipótese descartada está na
seção 3.5 do [registro da série](../metodologia/registro-da-serie-diaria.md) — é diário de
campo, não resultado.

---

## 5. Referências a conferir antes de submeter

Elementos que não foram verificados na fonte primária e precisam ser confirmados para
fechar a NBR 6023/2025:

| Referência | Situação |
|---|---|
| Alajarmeh, 2021 | ✅ Conferido: autoria, periódico, v. 21, n. 3, p. 771-789, DOI |
| Barros *et al.*, 2024 | ✅ Conferido: seis autores, p. 50-61, DOI |
| Brajnik, 2009 | ✅ Conferido: anais, p. 131-138, DOI |
| Freire; Castro; Fortes, 2009 | ✅ Conferido: autoria, RAP v. 43, n. 2, DOI · ⬜ confirmar paginação |
| Silva; La Rue, 2015 | ✅ Conferido: RAP v. 49, n. 2, p. 315-339, DOI |
| Simão; Rodrigues, 2005 | ✅ Conferido: Ci. Inf. v. 34, n. 2, p. 234-245, DOI |
| Vieira; Caniato; Yonemotu, 2017 | ✅ Conferido: Reciis v. 11, n. 2, DOI · nome do periódico agora por extenso |
| Torres; Mazzoni; Alves, 2002 | ✅ Conferido na SciELO: autoria, Ci. Inf. v. 31, n. 3, DOI · ⬜ confirmar paginação (p. 83-91) |
| Moraes; González de Gómez, 2007 | ✅ Conferido: Ciênc. Saúde Coletiva v. 12, n. 3, p. 553-565, DOI |
| Brasil, 2021 (Lei 14.129) | ✅ Conferido no portal da Câmara: art. 3º, XIX, DOU de 30 mar. 2021 |
| Power *et al.*, 2012 | ⬜ DOI e paginação exata nos anais da CHI '12 |
| Vigo; Brown; Conway, 2013 | ⬜ Paginação e local do evento (W4A '13) |
| IBGE, 2025 | ⬜ Trocar pela referência do documento, não pela notícia de divulgação |
| CGI.br, 2025 | ⬜ Conferir título e ano de publicação do relatório da TIC Domicílios 2024 |
| Anatel, 2026 | ⬜ Substituir pelo relatório primário; conferir título exato e data |
| HTTP Archive, 2025 | ⬜ Conferir capítulo específico do *Web Almanac* e a data de acesso |
| Caplovitz, 1963 | ⬜ Conferir editora e paginação na 1ª edição (Free Press of Glencoe) |
| Brasil, 2014b | ✅ Conferido: Lei 12.965/2014, art. 9º, DOU de 24 abr. 2014 |

**Correspondência entre citações e lista** — verificada em 09/09/2026: **25 referências**, todas
citadas no corpo, e nenhuma citação no corpo sem entrada na lista. A Lei de Acesso à Informação
(Brasil, 2011) constava da lista e não era citada com autor-data no corpo; a citação entrou no
terceiro parágrafo de 1.2.

Três correções desta rodada:

- a referência do W3C constava na lista e **não era citada** no texto, porque o corpo escreve
  "diretrizes de acessibilidade para conteúdo web, versão 2.1" por extenso, sem a sigla.
  Acrescentada a citação `(W3C, 2018)` nos objetivos específicos;
- a expressão "penalidade da pobreza", usada na seção 4.5, é conceito de Caplovitz (1963) e
  estava sem atribuição. A passagem foi reescrita para dar a lineagem;
- a proposta de "correção regulatória" da seção 4.5 estava sem âncora normativa. Ancorada no
  art. 9º da Lei 12.965/2014, que impõe tratamento isonômico de pacotes de dados. As entradas
  de 2014 passaram a `2014a` (eMAG) e `2014b` (Marco Civil).

---

## 6. Divergências numéricas corrigidas

**Rodada de 09/09/2026**, recalculada a partir dos cinco JSON de 04/09 (`scans-br/`, ramo
`serie-temporal`) com `analysis.dataset.build_pages_frame`:

| Onde | Antes | Agora | Origem |
|---|---|---|---|
| Tabela 3, coluna de risco | 110 / 42 / 16 (soma 168) | **104 / 42 / 8** (soma 154) | A coluna incluía as 14 violações da sonda de custo (6 altas, 8 moderadas), que o título exclui. O "art. 74 invocado 110 vezes" de 3.11 está certo: a sonda de custo não invoca o art. 74 |
| 3.1 | "18 dos 20 critérios plantados" e "três barreiras fora" | 20 barreiras cobrem **21 critérios**; 18 detectados, 3 fora | Manifesto `fixtures/manifest.yaml` |
| 3.1 × 3.5 | 2.4.4 "fora do alcance" e "violado em 70%" | Cobertura é por modo de falha: as 14 violações de 2.4.4 vêm da regra `link-name` | Verificado nos JSON |
| 3.7 (novo) | H2 sem resultado | Fluxo essencial (12) × informacional (8): ICA 61,0 × 81,2, p = 0,0003, δ = −0,98; IEJ 78,9 × 27,9, δ = 0,98; **confundido com H1** (6 das 8 informacionais são do gov.br) | IAN excluído do teste por incorporar o fluxo essencial (× 1,5) |
| 3.9 (novo) | H4 cortada | ρ = −0,41, p = 0,07, n = 20; por plataforma ρ = −0,80, p = 0,10, n = 5 | O −0,200 anterior era do bloco de 16/08 |
| 3.7 | IAN testado (ε² = 0,798) | **IAN não testado**: ≥ 99 em 13 de 20 auditorias | Saturação declarada em 3.7 e 4.8 |
| 3.7 (novo) | Comparação por portal prometida em 2.7 | Medianas por portal reportadas: IEJ 19,8 / 58,7 / 66,3 / 81,2 / 87,6; ICA 82,2 / 72,6 / 73,3 / 61,0 / 58,2 | Descritivo, sem teste |

**Rodada anterior.** Todos os números do manuscrito foram **recalculados a partir dos JSON do conjunto primário**
(última varredura de cada alvo, posterior à correção do instrumento), usando o próprio módulo
`analysis.dataset` do projeto. Quatro divergências apareceram, e o esqueleto já foi corrigido:

| Onde | Antes | Agora | Origem do erro |
|---|---|---|---|
| IC 95% do índice de conformidade | 61,0–**86,0** | 61,0–**84,9** | Valor calculado sobre o dataset anterior à correção do instrumento |
| Correlação peso × terceiros | ρ = **−0,386** | ρ = **−0,200** (p = 0,747) | Idem. Muda a leitura: não é "correlação negativa", é **ausência de associação detectável** — a Discussão foi reescrita para se apoiar na dissociação qualitativa, que os dados sustentam |
| Estrato estadual | "três observações" | **duas** | 6 páginas com 67% de perda → 2 válidas; a soma por esfera (8+2+6) fecha em 16 |
| Perfil de exclusão | 1 149 e 489 no texto | **1 126 e 479** | O texto de § 4.1.1 divergia da tabela de § 3.8; a tabela estava certa |

Confirmado pelos dados, e mantido: 125 violações, 16/16 páginas com barreira absoluta,
prevalência de 100% do critério 4.1.2, ε² = 0,746 e 0,831, δ de Cliff = 0,000, peso mediano de
2,292 MB, 4 de 16 páginas acima de 2,5 MiB, 1.4.10 exclusivo do perfil móvel.

**A conciliação 113 × 125** deixou de ser dedução e passou a ser verificação: as 12 violações
sem critério WCAG são todas da sonda `probe.data-cost`. É por isso que as distribuições por
princípio e por nível somam 113, e é o mesmo 113 das invocações do art. 63. A nota está na
subseção 3.5 do manuscrito.

Para reexecutar a conferência, o dataset primário é a última varredura de cada alvo em
`data/scans/` — note que `data/exports/*.csv` estava **defasado**, gerado antes da correção do
instrumento. Rodar `acessisaude exportar` antes de qualquer análise.
