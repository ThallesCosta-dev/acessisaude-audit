# Registro da série diária — 19/08 a 04/09/2026

> Diário do braço longitudinal da coleta. Complementa o
> [registro de campo de 16/08](registro-de-coleta.md), que documenta o braço transversal.
>
> **Todos os horários em UTC.** O relógio local do ambiente de coleta é UTC−3.

---

## 0. Sumário

Dezessete dias consecutivos, cinco plataformas, uma varredura por plataforma por dia, sempre
com a mesma configuração e a mesma lista de páginas. **85 varreduras, 340 tentativas de
auditoria de página, 297 bem-sucedidas.** Dezesseis dias observados (25/08 sem veredito).

Quatro desfechos:

1. **Três das cinco plataformas não variaram em nada** ao longo dos dezesseis dias observados —
   índice idêntico e conjunto de critérios violados idêntico, elemento por elemento.
2. **Duas plataformas mudaram**, em direções opostas: uma barreira crítica de teclado sumiu por
   cinco dias corridos e voltou (episódio fechado); uma violação de alternativa textual foi
   introduzida e seguia sem correção no último dia (censurada à direita).
3. **Um defeito grave do instrumento foi encontrado pelo dia 25/08**, em que a coleta falhou
   inteiramente e o instrumento reportou conformidade máxima para as cinco plataformas.
4. **Uma hipótese foi levantada e não se sustentou** com os dias adicionais — ver seção 3.5.
5. **A intermitência veio de componente de terceiro embarcado**, e não de intervenção do órgão
   — ver seção 5, que também descarta a camada de cookies como fonte de contaminação.

> **Histórico da janela.** A análise foi fechada primeiro com 13 dias (19 a 31/08) e depois
> estendida para 17 (até 04/09). O que os quatro dias extras mudaram está na seção 6.

---

## 1. Conduta e cadência

A série foi disparada por tarefa agendada (commit `78be394`), diariamente entre **12h20 e
12h25 UTC** (9h20–9h25 no horário de Brasília). **Exceção declarada:** em 01/09 a tarefa não
disparou, e a coleta foi executada manualmente às **18h07 UTC**. O dia é mantido na série: os
cinco índices são idênticos aos dos dias vizinhos, de modo que o desvio de horário não produziu
efeito detectável, e descartar uma observação por ser inconveniente seria pior do que
declará-la. Atenção à unidade ao cruzar artefatos: os
carimbos das varreduras estão em UTC, e os nomes dos arquivos em `data/logs/` estão em hora
local — `coleta-20260820-092001.log` corresponde à varredura de 12h20 UTC do dia 20. O horário fixo é decisão metodológica:
variação de horário confundiria mudança do portal com variação de carga do servidor ao longo
do dia.

A conduta é a mesma do braço transversal e não foi relaxada em nenhum dia: `robots.txt`
respeitado, intervalo mínimo de 2.000 ms entre requisições, `User-Agent` identificando a
pesquisa com endereço de contato, nenhum preenchimento de formulário, nenhuma autenticação.

**19/08 tem três execuções**, não uma. As duas primeiras (07h17–07h20 e 07h29–07h33) são
execuções manuais do dia em que a tarefa agendada foi montada; a terceira (12h20–12h24) é o
primeiro disparo da própria tarefa. **Apenas a execução das 12h20 integra a série**, pelo
critério de que a série é definida pela cadência agendada. As duas manuais permanecem
arquivadas em `data/scans/` e são recuperáveis, mas não entram na análise longitudinal:
misturá-las criaria três observações num único dia e uma só nos demais.

Critério de seleção reproduzível: `time(started_at) >= '12:00'`.

---

## 2. Cobertura obtida

Excluído o dia 25/08 (falha do coletor, seção 4):

| Plataforma | Páginas/dia | Auditadas | Tentativas | Perda |
|---|---|---|---|---|
| Secretaria municipal de saúde | 2 | 32 | 32 | 0,0% |
| Secretaria estadual de saúde | 6 | 96 | 96 | 0,0% |
| Meu SUS Digital | 2 | 32 | 32 | 0,0% |
| Portal municipal de serviços | 4 | 62 | 64 | 3,1% |
| Portal federal de saúde | 6 | 75 | 96 | 21,9% |

A **SES-RJ estabilizou**. No braço transversal perdia de 50% a 67% das páginas; nos dezesseis
dias da série, perda zero. A instabilidade documentada em 16/08 era episódica. Consequência direta:
seu índice de conformidade passou de 54,1 (medido sobre o resíduo que sobrevivia às quedas)
para **49,3 sob cobertura integral** — o mais baixo da amostra.

O **gov.br concentra a perda** em dois caminhos específicos (`/saes` e `/saude-de-a-a-z`); a
página inicial falhou uma única vez em dezesseis dias. A perda caiu ao longo da série: 26,4%
no recorte de 13 dias, 21,9% no de 17, com cobertura integral em 03 e 04/09.

---

## 3. O que a série mostrou

### 3.1 Estabilidade (três plataformas)

Meu SUS Digital (5 critérios violados), SES-RJ (11) e SMS-Rio (8): **variação nula**. Mesmo
índice, mesmo conjunto de critérios, todos os dias, nos dois perfis de dispositivo. Nenhuma
barreira apareceu, sumiu ou trocou de página em dezesseis dias observados.

### 3.2 O critério 2.1.1 no portal municipal

Elemento não interativo usado como controle (`probe.non-interactive-control`), na página do
atendimento em UPA 24 horas, **nos dois perfis simultaneamente**:

```
ago                                          set
19 20 21 22 23 24 25 26 27 28 29 30 31 | 01 02 03 04
 1  1  1  1  1  .  X  .  .  .  1  1  1 |  1  1  1  1

1 = violado   . = não violado   X = sem veredito
```

Ausente em 24, 26, 27 e 28. **Não é artefato de cobertura**: em 24, 26 e 28 as quatro
auditorias de página foram bem-sucedidas. A barreira foi procurada onde estava e não foi
encontrada.

**Episódio fechado.** A janela de ausência tem cinco dias corridos (24 a 28/08) e está
delimitada por observações da barreira em 23 e em 29. Desde o retorno, presente em **sete dias
consecutivos**, todos com cobertura 4/4.

O ICA acompanha: 50,68 nos dias com a violação, 58,90 nos dias sem.

### 3.3 O critério 1.1.1 no portal federal

```
ago                                          set
19 20 21 22 23 24 25 26 27 28 29 30 31 | 01 02 03 04
 .  .  .  .  .  1  X  1  1  1  1  1  1 |  1  1  1  1
```

Introduzido entre 23 e 24/08 e **não corrigido** em nenhum dos onze dias observados seguintes.
**Censurado à direita**: persistia no último dia da série, então 11 dias é piso, não duração.

A transição está ancorada em cobertura integral dos dois lados — é o que descarta "a barreira
já existia e escapava à amostra":

| Dia | Cobertura | 1.1.1 |
|---|---|---|
| 20/08 | 6/6 | 0 de 6 |
| 21/08 | 6/6 | 0 de 6 |
| 24/08 | 6/6 | **6 de 6** |
| 27/08 | 6/6 | **6 de 6** |
| 03/09 | 6/6 | **6 de 6** |
| 04/09 | 6/6 | **6 de 6** |

É alteração de escopo do portal, não propriedade de uma página.

### 3.4 Achados que NÃO se interpretam

Os critérios 1.4.1 (29/08), 1.4.3 (30/08) e 2.4.7 (26 e 29/08), também no portal federal,
apareceram em um único dia, numa única página e num único perfil, e **não reapareceram nos
onze dias seguintes**. São compatíveis com conteúdo rotativo e ocorreram justamente no portal
de disponibilidade mais instável. **Ficam registrados e não sustentam afirmação**: não há como
separar mudança do portal de variação da amostra observada.

### 3.5 Hipótese testada e não sustentada

Com 13 dias, a ausência da barreira 2.1.1 cobria exatamente uma semana útil — segunda 24 a
sexta 28 —, com a barreira presente nos fins de semana que a cercavam. E o 1.1.1 do gov.br
apareceu na **mesma segunda-feira**. A leitura sugerida era atraente: regressão de
acessibilidade atrelada a ciclo de implantação, com deploy de segunda e reversão de fim de
semana.

**Os quatro dias adicionais não sustentam essa leitura.** Na semana útil seguinte (segunda
31/08 a sexta 04/09), a barreira 2.1.1 esteve **presente todos os dias**, com cobertura
integral. Se houvesse ciclo semanal, o episódio teria se repetido, e não se repetiu.

Fica registrado como hipótese descartada, e não apagada: é a diferença entre um diário de campo
e um relatório de resultados. Com um episódio só, qualquer regularidade de calendário é
indistinguível de coincidência — e por isso nenhuma foi levada ao manuscrito.

---

## 4. O defeito encontrado pelo dia 25/08

Em 25/08, todas as 20 páginas das cinco plataformas falharam com
`net::ERR_NAME_NOT_RESOLVED`. Falha simultânea em cinco domínios distintos, de operadores
distintos, no mesmo minuto: é resolução de nomes na máquina coletora, não indisponibilidade
dos portais. O diagnóstico é independente do log, mas coincide com ele: o arquivo do dia foi
arquivado pelo operador como `coleta-20260825-092002-TIVE PROBLEMA DE REDE.log`.

O instrumento gravou, para as cinco plataformas:

```
ICA 100,0   IAN 0,0   IEJ 0,0   barreira absoluta: não
```

**Conformidade máxima no único dia, em dezessete, em que nada foi observado.** O ICA é a razão entre critérios
não violados e critérios avaliados; sem página carregada não há achado, e o numerador fica
cheio. Nenhuma exceção foi levantada — a taxa de perda de 100% ficou registrada num campo ao
lado, que ninguém precisa ler para enxergar o número grande.

A correção está na [ADR 0010](../adr/0010-indices-nulos-sem-observacao.md): os quatro índices
passaram a admitir nulo, e nulo significa **sem veredito**. O acumulador do domínio passou a
contar páginas observadas, e não tentativas — o que corrigiu junto a mesma falha em
granularidade de página, que vinha contaminando `paginas.csv` com 59 linhas de ICA 100 sobre
páginas que nunca carregaram.

Como o documento JSON guarda páginas e achados, e não índices (ADR 0003), **nenhum portal
precisou ser varrido de novo**: `acessisaude reindexar` reconstruiu as varreduras arquivadas
(115 na primeira aplicação, 139 depois da extensão da janela), das quais 5 passaram a constar
sem veredito. Após a reindexação, nenhuma varredura
de portal real pontua ICA 100 — as únicas linhas que restam nesse valor são do conjunto de
validação local, em que a página deliberadamente acessível *deve* pontuar 100.

---

## 5. Sobreposições na tela: o que contamina e o que não contamina

Investigação motivada por uma observação simples: **as capturas de tela dos portais reais têm
banner de cookies na frente**. A pergunta era se isso contamina a auditoria. A resposta é não
para a camada de consentimento e sim, de outra forma, para os componentes embarcados — e o
caminho até a segunda parte revelou a causa do episódio da seção 3.2.

### Camada de consentimento: não contamina o ICA

O instrumento percorre o documento renderizado, não a imagem. Um banner sobreposto **acrescenta
nós ao documento; não subtrai**. Três verificações:

| Verificação | Resultado |
|---|---|
| Critérios exclusivos do banner | **nenhum**, nas cinco plataformas |
| Ocorrências vindas do banner | 4,5% (SMS-Rio), 0,2% (gov.br), 0% nas demais |
| Supressão de detecção fora do banner | **não ocorre** — mais de 95% das ocorrências são de fora |

A terceira é a que importava mais. Gerenciadores de consentimento costumam marcar o restante
do documento como oculto para tecnologia assistiva enquanto o banner está aberto; se isso
acontecesse, a análise ficaria confinada ao banner e o portal pareceria **melhor** do que é —
a direção perigosa de erro. Não é o caso: o volume de achados fora da camada descarta a
hipótese empiricamente.

Conclusão: o **ICA é insensível** por construção, já que opera sobre critérios e nenhum
critério é exclusivo do banner. IAN e IEJ operam sobre ocorrências e admitem influência
pequena, concentrada em um portal.

Achados que de fato vêm da camada de consentimento do SMS-Rio, para registro: `image-alt` em
`.logo-lgpd` e `link-name` no vínculo para `lgpd.prefeitura.rio`. Ambos os critérios também são
violados no conteúdo próprio do portal, e por isso não alteram o conjunto.

### Componente embarcado: contamina, e explicou o episódio

Ao inspecionar o elemento por trás do achado de 2.1.1 no Carioca Digital, a evidência gravada
mostrou:

```html
<span onclick="LikeBtn.vote(1, 0, event);" class="lb-a" data-lb_index="0">
```

É um **botão de curtida de um fornecedor externo**, não um controle do serviço de atendimento.
Daí duas consequências.

**A primeira é a causa do episódio.** Nos cinco dias de ausência, sumiram juntos os *três*
achados que tocavam esse componente — 2.1.1, alternativa textual e contraste — e os três
voltaram juntos em 29/08. Enquanto isso, o domínio do fornecedor permaneceu entre os terceiros
requisitados **todos os dias, inclusive nos do episódio**: o script foi buscado, mas o
componente não se materializou no documento.

| Dia | Domínio do fornecedor requisitado | Componente no documento |
|---|---|---|
| 19 a 23/08 | sim | sim |
| 24 a 28/08 | **sim** | **não** |
| 29/08 a 04/09 | sim | sim |

Isso **descarta a leitura de correção e regressão pelo órgão municipal**. O que oscilou foi a
renderização de um componente de terceiro.

**A segunda é um limite do modelo de risco.** O risco jurídico é atribuído por critério: 2.1.1
é crítico esteja o elemento no botão que agenda a consulta ou num botão de curtida. Para este
achado, a classificação é desproporcional à consequência assistencial. O limite passou a estar
declarado em § 4.8 do manuscrito.

Verificou-se, por isso, o que sustenta a afirmação central do artigo. As violações de risco
crítico do conjunto vêm majoritariamente de **elementos do caminho do serviço**: campo de busca
sem rótulo (`#edit-busca`), botão de busca sem nome (`#searchsubmit`), botão de autenticação
sem nome (`.br-sign-in` na barra gov.br), vínculos sem nome. O componente de terceiro responde
por 24 dos 148 achados críticos do Carioca Digital, e por nenhum nos demais portais. **A
afirmação de barreira absoluta em todas as páginas não repousa sobre widgets.**

Registre-se ainda que o portal manteve barreira absoluta **em todos os cinco dias do episódio**,
por outras violações críticas. Nenhum dia da série teve o Carioca Digital sem barreira absoluta.

### O que ficou de correção no manuscrito

A redação anterior de § 3.12.2 e § 4.7 dizia "um controle inoperável por teclado impede a
conclusão da tarefa (...) na página que informa como obter atendimento de urgência". A frase é
verdadeira sobre o critério e enganosa sobre o elemento: sugere que o serviço de urgência ficou
inoperável por teclado, quando o elemento é acessório. Corrigida.

---

## 6. O que os quatro dias extras mudaram

A análise foi fechada com 13 dias e reaberta com 17. Vale registrar o que a extensão produziu,
porque é o argumento operacional a favor de deixar a coleta rodando:

| | 13 dias (até 31/08) | 17 dias (até 04/09) |
|---|---|---|
| Estabilidade dos três portais | 12 dias observados | **16 dias observados** |
| Episódio 2.1.1 | aberto à direita | **fechado**, 5 dias corridos |
| Regressão 1.1.1 | ≥ 8 dias observados | **≥ 11 dias observados** |
| Transição do 1.1.1 | 2 dias de cobertura 6/6 depois | **4 dias**, 2 antes e 2 depois |
| Hipótese do ciclo semanal | plausível, n = 1 | **não replicou** |
| Critérios esporádicos do gov.br | possivelmente ativos | **sem reincidência em 11 dias** |

Nenhuma conclusão do artigo foi invertida. O que mudou foi a **força** de cada afirmação: o
episódio virou mensurável, a regressão ganhou piso maior, a transição ganhou controle dos dois
lados, e uma hipótese sedutora foi eliminada antes de chegar ao texto. Custo: zero — a tarefa
agendada já rodava.

---

## 7. Reprodução

```powershell
# A tarefa agendada executa, uma vez por dia:
acessisaude varrer conecte-sus-web
acessisaude varrer gov-br-saude
acessisaude varrer ses-rj
acessisaude varrer sms-rio
acessisaude varrer carioca-rio-saude

# Reconstrução do índice relacional a partir dos JSON arquivados:
acessisaude reindexar

# Exportação do dataset da análise:
acessisaude exportar
```

Recorte da série no índice relacional:

```sql
SELECT date(started_at) AS dia, target_id, observed, conformance_index, loss_rate
  FROM scans
 WHERE target_id <> 'fixtures-local'
   AND time(started_at) >= '12:00'
 ORDER BY started_at;
```

Portais mudam — e esta série é justamente a evidência disso. Reexecutar verifica o
**procedimento**; o dado original está em `data/scans/`, com `config_snapshot` completo em cada
arquivo.
