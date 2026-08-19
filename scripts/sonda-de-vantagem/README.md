# Sonda de vantagem

Controle de rede para a auditoria contínua, executado no Google Apps Script.

**Não audita acessibilidade.** Pergunta apenas "este endereço responde?", a partir de uma
posição de rede diferente da do coletor.

---

## 1. O problema que ela resolve

Em quatro janelas consecutivas de coleta pelo runner do GitHub (IP de datacenter nos Estados
Unidos), o resultado foi:

| Endereço | Do runner | Desta máquina (IP residencial, Brasil) |
|---|---|---|
| `meususdigital.saude.gov.br` | HTTP 403 · 8 de 8 tentativas | HTTP 200 |
| `saude.rj.gov.br/laudos` | falha · 4 de 4 janelas | HTTP 200, 37 KB |
| `www.rj.gov.br/saude` | falha · 4 de 4 janelas | HTTP 200, 98 KB |

De um único ponto de observação, duas explicações são indistinguíveis:

1. **o portal está indisponível** — barreira de disponibilidade, que o trabalho sustenta ser
   precondição da acessibilidade;
2. **o portal recusa aquele IP** — artefato do instrumento, da mesma classe do User-Agent
   `HeadlessChrome` registrado no [ADR 0008](../../docs/adr/).

A diferença não é técnica, é jurídica: a primeira é achado, a segunda é erro de medida.
Confundi-las contamina o resultado.

Com **três posições de observação** — runner nos EUA, máquina do pesquisador no Brasil, e
Google via Apps Script — a divergência deixa de ser ruído e passa a ser medida da política de
rede do portal.

## 2. O que ela não resolve

O Apps Script executa de IPs do Google, majoritariamente nos Estados Unidos. **Não substitui
um ponto de observação brasileiro**: acrescenta um segundo ponto estrangeiro, independente do
primeiro.

A leitura dos resultados possíveis:

| Runner (EUA) | Apps Script (EUA) | Máquina (BR) | Leitura |
|---|---|---|---|
| falha | falha | sucesso | Política de rede contra origem estrangeira |
| falha | sucesso | sucesso | Específico daquele IP, ou falha de renderização |
| falha | falha | falha | Indisponibilidade real do portal |

Só a terceira linha sustenta a afirmação de que o serviço está fora do ar.

E há um limite que nenhuma das três posições remove: o Apps Script não roda navegador. O
`UrlFetchApp` devolve o HTML servido, e a auditoria depende do documento **renderizado** —
razão pela qual o Meu SUS Digital, aplicação de página única, serve 1.418 bytes de casca vazia
a qualquer cliente sem JavaScript. Uma resposta 200 aqui significa "o servidor respondeu", não
"a página existe para o usuário".

## 3. Implantação

Cerca de cinco minutos. Não exige cartão de crédito nem projeto no Google Cloud.

1. Crie uma planilha em [sheets.new](https://sheets.new) e dê um nome a ela — por exemplo
   *AcessiSaúde — sonda de vantagem*.

2. Na planilha: **Extensões → Apps Script**. Abre o editor, com um `Código.gs` vazio.

3. Apague o conteúdo e cole o [`Codigo.gs`](Codigo.gs) desta pasta.

4. **Preencha a constante `CONTATO`**, no topo, com a identificação da pesquisa e um e-mail de
   contato. A sonda lança erro e recusa executar enquanto o marcador `PREENCHA` estiver lá —
   coleta automatizada não identificada é conduta que este projeto recusa.

5. Salve (Ctrl+S).

6. Selecione a função **`observar`** na barra superior e clique em **Executar**. Na primeira
   vez o Google pede autorização: *Revisar permissões* → sua conta → *Avançado* → *Acessar
   (não seguro)* → *Permitir*. O aviso é o padrão para scripts não verificados; as permissões
   pedidas são acesso à própria planilha e requisições externas.

7. Confira a aba `observacoes`, que deve ter dez linhas.

8. Selecione a função **`instalarGatilho`** e execute uma vez. Passa a rodar a cada 6 horas.

Para interromper: execute `removerGatilhos`.

## 4. Analisando junto com a série

Baixe a aba como CSV (**Arquivo → Fazer download → CSV**) e compare com a série do coletor,
que está no ramo `serie-temporal`:

```powershell
git fetch origin serie-temporal:serie-temporal
git worktree add C:\Temp\serie serie-temporal
```

A coluna que interessa é `status_http` por `url`, no mesmo intervalo de tempo das janelas do
coletor. Uma divergência sistemática entre as duas fontes, no mesmo endereço e na mesma hora,
é medida de política de rede — e é reportável como resultado, não como limitação.

## 5. Cotas

Amplamente suficientes para este uso: as dez requisições a cada seis horas somam 40 por dia,
contra um limite de 20.000 chamadas diárias de `UrlFetchApp` em conta gratuita. O tempo de
execução por disparo fica em torno de 20 segundos, contra 90 minutos diários de gatilhos.

## 6. Manutenção

A lista `ALVOS` **duplica as sementes do catálogo**
([`targets.yaml`](../../backend/src/acessisaude_audit/catalog/targets.yaml)), porque o Apps
Script não tem como ler o YAML do repositório. A duplicação é deliberada e frágil: se o
catálogo mudar e esta lista não, a sonda passa a observar endereços diferentes dos auditados e
deixa de servir como controle.

Ao alterar o catálogo, rode o verificador — ele existe para que a divergência apareça, em vez
de a sonda passar a medir outra coisa em silêncio:

```powershell
python scripts\sonda-de-vantagem\conferir_alvos.py
```
