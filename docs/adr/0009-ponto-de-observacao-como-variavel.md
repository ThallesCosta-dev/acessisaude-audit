# ADR 0009 — O ponto de observação de rede é variável do estudo, não constante

**Estado:** aceita
**Data:** 19/08/2026

---

## Contexto

A auditoria contínua entrou em operação em 18/08/2026, executando em runner do GitHub
(`ubuntu-latest`, datacenter nos Estados Unidos), com três janelas diárias. Quatro janelas
consecutivas produziram um padrão que a coleta de campo manual não havia exibido:

| Alvo | Páginas com sucesso, em 4 janelas |
|---|---|
| `carioca.rio` | 4/4 em todas as páginas |
| `gov.br/saude` | 4/4 na inicial; 2/4 e 3/4 nas internas |
| `saude.rj.gov.br/ouvidoria/participe` | 4/4 |
| `saude.rj.gov.br/laudos` | **0/4** |
| `www.rj.gov.br/saude` | **0/4** |
| `meususdigital.saude.gov.br` | **0/4** — HTTP 403 |

Os índices agregados reportaram o Meu SUS Digital com conformidade 100,0 e exposição jurídica
0,0 — o portal mais acessível da amostra, por não ter carregado nenhuma página. Esse defeito de
leitura foi corrigido à parte; o que este ADR trata é da **causa das falhas**.

---

## Problema

De um único ponto de observação, duas explicações são indistinguíveis:

1. **o portal está indisponível** — barreira de disponibilidade, que o trabalho sustenta ser
   precondição da acessibilidade e reporta como achado;
2. **o portal recusa aquela origem de rede** — artefato do instrumento.

A distinção não é técnica, é jurídica: a primeira é resultado, a segunda é erro de medida. É
a mesma classe de confusão do [ADR 0008](0008-user-agent-em-todos-os-perfis.md), em que uma
propriedade do instrumento — o `User-Agent` anunciando `HeadlessChrome` — aparecia como
propriedade do portal.

---

## Investigação

Três hipóteses foram levantadas e testadas. Todas as medições abaixo ocorreram em 19/08/2026,
entre 05h35 e 05h50 UTC, com no máximo poucos minutos de separação entre pontos.

### Hipótese 1 — bloqueio a origem estrangeira

**Descartada para o Meu SUS Digital, sustentada para a SES-RJ.**

Uma sonda independente foi implantada no Google Apps Script
([`scripts/sonda-de-vantagem/`](../../scripts/sonda-de-vantagem/)), que executa de IPs do
Google nos Estados Unidos e faz apenas requisições HTTP — sem navegador, portanto sem auditar.

| Endereço | Azure/GitHub (EUA) | Google (EUA) | Máquina do pesquisador (BR, residencial) |
|---|---|---|---|
| `meususdigital.saude.gov.br/` | **403** | 200 | 200 |
| `www.rj.gov.br/saude/` | conexão fechada | **500** | 200 |
| `saude.rj.gov.br/laudos` | conexão fechada | **500** | 200 |
| `saude.rj.gov.br/ouvidoria/participe` | 200 | 200 | 200 |

O Meu SUS Digital responde ao Google e recusa o Azure: não é "estrangeiro", é aquela faixa de
endereços. A SES-RJ recusa as duas origens estrangeiras e atende a brasileira, em endereços
específicos — enquanto a ouvidoria, no **mesmo host**, atende todos.

### Hipótese 2 — negociação de HTTP/2

**Descartada.** O cliente HTTP foi executado com `http2=True` e `http2=False` contra os três
endereços da SES-RJ. Os seis resultados foram HTTP 200 em HTTP/1.1: o servidor não negocia
HTTP/2, e a versão do protocolo não explica a falha.

### Hipótese 3 — detecção de navegador headless

**Descartada.** Chromium foi executado a partir da máquina do pesquisador em modo headless e
em modo visível, contra `saude.rj.gov.br/laudos` e `rj.gov.br/saude/laudos`. Os quatro
resultados foram HTTP 200, com o título correto da página. A confirmação independente veio da
abertura manual em navegador comum, que exibiu a página normalmente.

### O que a investigação também corrigiu

A falha registrada em 16/08 na coleta de campo — `ERR_CONNECTION_CLOSED` em 8 de 8 tentativas
contra `/laudos`, a partir da máquina do pesquisador — **era indisponibilidade real naquela
janela**. Três dias depois, o mesmo endereço responde 200 do mesmo ponto, em todos os modos de
cliente testados.

A leitura de § 3.4 do artigo permanece válida para aquela janela e **não pode ser estendida à
série do runner**: são fenômenos distintos com a mesma aparência.

---

## Decisão

**O ponto de observação de rede passa a ser variável declarada do desenho, e não constante
implícita.**

Consequências operacionais:

1. **Toda observação declara sua origem.** As varreduras do coletor pelo ramo em que são
   publicadas; as observações da sonda pelo campo `vantagem`.

2. **Nenhuma indisponibilidade é reportada como achado a partir de um único ponto.** A
   afirmação "o serviço está fora do ar" exige convergência de pontos independentes. É a
   terceira linha da tabela de leitura documentada no
   [README da sonda](../../scripts/sonda-de-vantagem/README.md).

3. **A coleta a partir do Brasil é requisito, não preferência.** Dois dos cinco alvos — o
   prontuário federal e o resultado de exame estadual — não são auditáveis do runner do
   GitHub, e não passarão a ser: é política de origem, permanente, não instabilidade. Nuvem
   brasileira de datacenter não resolve por construção — o Google, datacenter estrangeiro,
   recebeu 500 onde a conexão residencial recebeu 200, e nada garante que uma faixa de
   datacenter brasileira seja tratada como residencial.

4. **A divergência entre pontos vira medida, e não ruído.** Que a SES-RJ sirva conteúdo a uma
   origem e erro a outra, no mesmo minuto e no mesmo host, é dado reportável sobre política de
   rede do portal — dimensão que a literatura de avaliação de acessibilidade levantada para
   este trabalho não mede.

---

## Consequências para o artigo

A subseção 3.4 afirma hoje que a falha "atinge igualmente navegador e cliente HTTP simples" e
conclui indisponibilidade. A afirmação precisa ser reescrita: a atribuição depende da origem
da requisição, e o endpoint responde normalmente do Brasil.

O achado que sobrevive é mais forte que o original, porque é reprodutível e tem três pontos de
apoio: **a SES-RJ discrimina por origem de rede em endereços específicos**, servindo conteúdo
à origem brasileira e erro às estrangeiras, no mesmo host em que outra página atende a todas.

---

## Alternativas consideradas

**Manter só o runner do GitHub e declarar a perda como limitação.** Rejeitada: produziria
série em que dois alvos aparecem permanentemente indisponíveis, e a limitação seria
indistinguível de achado — exatamente o que este ADR existe para impedir.

**Migrar a coleta para nuvem com região brasileira (Cloud Run São Paulo, Fly.io GRU).**
Rejeitada como solução, mantida como experimento futuro: exige cartão de crédito em todos os
provedores avaliados, e o resultado do Google mostra que IP brasileiro de datacenter não é
equivalente a IP residencial para efeito de política de WAF.

**Executar a sonda de controle a partir do próprio runner, em vez de terceiro ponto.**
Rejeitada como suficiente: distinguiria cliente HTTP de navegador na mesma origem, mas não
distinguiria origem de portal — que é a questão. Permanece útil como complemento.
