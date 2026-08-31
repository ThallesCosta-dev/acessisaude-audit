# Registro da série diária — 19 a 31/08/2026

> Diário do braço longitudinal da coleta. Complementa o
> [registro de campo de 16/08](registro-de-coleta.md), que documenta o braço transversal.
>
> **Todos os horários em UTC.** O relógio local do ambiente de coleta é UTC−3.

---

## 0. Sumário

Treze dias consecutivos, cinco plataformas, uma varredura por plataforma por dia, sempre com a
mesma configuração e a mesma lista de páginas. **65 varreduras, 260 tentativas de auditoria de
página, 219 bem-sucedidas.**

Três desfechos:

1. **Três das cinco plataformas não variaram em nada** ao longo dos doze dias observados —
   índice idêntico e conjunto de critérios violados idêntico, elemento por elemento.
2. **Duas plataformas mudaram**, em direções opostas: uma barreira crítica de teclado sumiu por
   quatro dias e voltou; uma violação de alternativa textual foi introduzida e não corrigida.
3. **Um defeito grave do instrumento foi encontrado pelo dia 25/08**, em que a coleta falhou
   inteiramente e o instrumento reportou conformidade máxima para as cinco plataformas.

---

## 1. Conduta e cadência

A série foi disparada por tarefa agendada (commit `78be394`), diariamente entre **12h20 e
12h25 UTC** (9h20–9h25 no horário de Brasília). Atenção à unidade ao cruzar artefatos: os
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
| Secretaria municipal de saúde | 2 | 24 | 24 | 0,0% |
| Secretaria estadual de saúde | 6 | 72 | 72 | 0,0% |
| Meu SUS Digital | 2 | 24 | 24 | 0,0% |
| Portal municipal de serviços | 4 | 46 | 48 | 4,2% |
| Portal federal de saúde | 6 | 53 | 72 | 26,4% |

A **SES-RJ estabilizou**. No braço transversal perdia de 50% a 67% das páginas; nos doze dias
da série, perda zero. A instabilidade documentada em 16/08 era episódica. Consequência direta:
seu índice de conformidade passou de 54,1 (medido sobre o resíduo que sobrevivia às quedas)
para **49,3 sob cobertura integral** — o mais baixo da amostra.

O **gov.br concentra a perda** em dois caminhos específicos (`/saes` e `/saude-de-a-a-z`); a
página inicial falhou uma única vez em doze dias.

---

## 3. O que a série mostrou

### 3.1 Estabilidade (três plataformas)

Meu SUS Digital (5 critérios violados), SES-RJ (11) e SMS-Rio (8): **variação nula**. Mesmo
índice, mesmo conjunto de critérios, todos os dias, nos dois perfis de dispositivo. Nenhuma
barreira apareceu, sumiu ou trocou de página em doze dias.

### 3.2 O critério 2.1.1 no portal municipal

Elemento não interativo usado como controle (`probe.non-interactive-control`), na página do
atendimento em UPA 24 horas, **nos dois perfis simultaneamente**:

```
19 20 21 22 23 24 25 26 27 28 29 30 31
 1  1  1  1  1  .  X  .  .  .  1  1  1     1 = violado   . = não violado   X = sem veredito
```

Ausente em 24, 26, 27 e 28. **Não é artefato de cobertura**: em 24, 26 e 28 as quatro
auditorias de página foram bem-sucedidas. A barreira foi procurada onde estava e não foi
encontrada.

O ICA acompanha: 50,68 nos dias com a violação, 58,90 nos dias sem.

### 3.3 O critério 1.1.1 no portal federal

```
19 20 21 22 23 24 25 26 27 28 29 30 31
 .  .  .  .  .  1  X  1  1  1  1  1  1
```

Introduzido entre 23 e 24/08 e **não corrigido** em nenhum dos oito dias observados seguintes.
Nos dois dias de cobertura integral do período (24 e 27), detectado em **todas as páginas e
nos dois perfis** — é alteração de escopo do portal, não propriedade de uma página.

### 3.4 Achados que NÃO se interpretam

Os critérios 1.4.1 (29/08), 1.4.3 (30/08) e 2.4.7 (26 e 29/08), também no portal federal,
apareceram em um único dia, numa única página e num único perfil. São compatíveis com conteúdo
rotativo e ocorreram justamente no portal de disponibilidade mais instável. **Ficam
registrados e não sustentam afirmação**: não há como separar mudança do portal de variação da
amostra observada.

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

**Conformidade máxima no único dia em que nada foi observado.** O ICA é a razão entre critérios
não violados e critérios avaliados; sem página carregada não há achado, e o numerador fica
cheio. Nenhuma exceção foi levantada — a taxa de perda de 100% ficou registrada num campo ao
lado, que ninguém precisa ler para enxergar o número grande.

A correção está na [ADR 0010](../adr/0010-indices-nulos-sem-observacao.md): os quatro índices
passaram a admitir nulo, e nulo significa **sem veredito**. O acumulador do domínio passou a
contar páginas observadas, e não tentativas — o que corrigiu junto a mesma falha em
granularidade de página, que vinha contaminando `paginas.csv` com 59 linhas de ICA 100 sobre
páginas que nunca carregaram.

Como o documento JSON guarda páginas e achados, e não índices (ADR 0003), **nenhum portal
precisou ser varrido de novo**: `acessisaude reindexar` reconstruiu as 115 varreduras
arquivadas, das quais 5 passaram a constar sem veredito. Após a reindexação, nenhuma varredura
de portal real pontua ICA 100 — as únicas linhas que restam nesse valor são do conjunto de
validação local, em que a página deliberadamente acessível *deve* pontuar 100.

---

## 5. Reprodução

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
