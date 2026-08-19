# Sonda de vantagem

Controle de rede para a auditoria contínua, executado no Google Apps Script.

**Não audita acessibilidade.** Pergunta apenas "este endereço responde?", a partir de uma
posição de rede diferente da do coletor.

---

## 1. O problema que ela resolve

Em quatro janelas consecutivas de coleta pelo runner do GitHub (IP de datacenter nos Estados
Unidos), o resultado foi:

| Endereço | Do runner | Da máquina do pesquisador (IP residencial, Brasil) |
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

Com **três posições de observação** — runner nos EUA, máquina do pesquisador no Brasil, e
Google via Apps Script — a divergência deixa de ser ruído e passa a ser medida da política de
rede do portal.

## 2. O que ela não faz — e por que não pode fazer

**Não move a auditoria para o Apps Script.** A limitação não é de cota nem de linguagem: é de
arquitetura. O `UrlFetchApp` devolve o HTML que o servidor mandou, e a auditoria opera sobre o
documento **renderizado**. Três critérios do estudo tornam isso concreto:

| Critério | O que exige | Existe no HTML servido? |
|---|---|---|
| 1.4.3 Contraste mínimo | cor computada após a cascata de CSS | não |
| 4.1.2 Nome, função, valor | árvore de acessibilidade do navegador | não |
| 1.4.10 Refluxo | layout real a 320 px | não |

E o caso extremo: o Meu SUS Digital serve 1.418 bytes de casca vazia. A sonda receberia esses
1.418 bytes e teria zero a auditar.

**Repassar o HTML ao coletor também não resolveria.** Para renderizar a página, o navegador
precisa buscar CSS, JavaScript, fontes e imagens no mesmo portal, do mesmo IP que leva 403. A
sonda move o primeiro pedido, não os cinquenta de que a renderização depende.

**E ela não substitui um ponto brasileiro.** O Apps Script executa de IPs do Google,
majoritariamente nos EUA. Acrescenta um segundo ponto estrangeiro, independente do primeiro.
A leitura dos resultados possíveis:

| Runner (EUA) | Apps Script (EUA) | Máquina (BR) | Leitura |
|---|---|---|---|
| falha | falha | sucesso | política de rede contra origem estrangeira |
| falha | **sucesso** | sucesso | específico daquele IP, ou falha de renderização |
| falha | falha | falha | **indisponibilidade real do portal** |

Só a terceira linha sustenta a afirmação de que o serviço está fora do ar.

## 3. Implantação

Cerca de cinco minutos. Não exige cartão de crédito nem projeto no Google Cloud.

1. Crie uma planilha em [sheets.new](https://sheets.new) e dê um nome a ela — por exemplo
   *AcessiSaúde — sonda de vantagem*.

2. Na planilha: **Extensões → Apps Script**.

3. Apague o conteúdo do editor e cole o [`Codigo.gs`](Codigo.gs) desta pasta.

4. **Preencha a constante `CONTATO`**, no topo, com a identificação da pesquisa e um e-mail de
   contato. A sonda lança erro e recusa executar enquanto o marcador `PREENCHA` estiver lá —
   coleta automatizada não identificada é conduta que este projeto recusa.

5. Salve (Ctrl+S).

6. Selecione a função **`observar`** na barra superior e clique em **Executar**. Na primeira
   vez o Google pede autorização: *Revisar permissões* → sua conta → *Avançado* → *Acessar
   (não seguro)* → *Permitir*. O aviso é o padrão para scripts não verificados; as permissões
   pedidas são acesso à própria planilha e requisições externas.

7. Confira a aba `observacoes`, que deve ter dez linhas.

Neste ponto a sonda já funciona, gravando na planilha. A publicação automática no repositório
é a etapa seguinte e é opcional.

## 4. Publicação automática no repositório

Sem isso, a comparação com a série do coletor exige baixar CSV e cruzar à mão. Com isso, cada
observação vira um arquivo no ramo `serie-temporal`, ao lado das varreduras.

### 4.1 Criar o token

Em **github.com → Settings (da conta) → Developer settings → Personal access tokens →
Fine-grained tokens → Generate new token**:

| Campo | Valor |
|---|---|
| Token name | `sonda-de-vantagem` |
| Expiration | o horizonte da coleta — 90 dias cobre a maioria dos casos |
| Repository access | **Only select repositories** → `acessisaude-audit` |
| Permissions → Repository permissions → **Contents** | **Read and write** |

Nenhuma outra permissão. Escopo restrito a um repositório e a uma capacidade é o que torna
aceitável guardar o token num projeto do Apps Script.

Copie o valor — o GitHub o exibe uma única vez.

### 4.2 Cadastrar o token no script

No editor do Apps Script: **Configurações do projeto** (ícone de engrenagem, à esquerda) →
role até **Propriedades do script** → **Adicionar propriedade do script**:

| Propriedade | Valor |
|---|---|
| `GITHUB_TOKEN` | o token copiado |

**Não cole o token no `Codigo.gs`.** Propriedades do script não vão para o repositório e não
aparecem em compartilhamento do arquivo.

### 4.3 Conferir

Execute a função **`conferirAcessoAoGitHub`** e veja o registro (*Execuções*, à esquerda).
Deve dizer `Acesso confirmado`.

Se der **404**: em repositório privado, token sem permissão devolve 404 e não 403 — confira se
o repositório foi selecionado e se `Contents` está em *Read and write*. Confira também se o
ramo `serie-temporal` já existe; ele nasce na primeira coleta do workflow.

### 4.4 Instalar o gatilho

Execute **`instalarGatilho`** uma vez. Passa a rodar a cada 6 horas, gravando na planilha e
publicando em `observacoes/` no ramo `serie-temporal`.

Para interromper: execute `removerGatilhos`.

## 5. Analisando junto com a série

```powershell
git fetch origin serie-temporal:serie-temporal
git worktree add C:\Temp\serie serie-temporal
```

```
serie-temporal/
  scans/         varreduras do coletor — auditoria, com navegador
  observacoes/   observações da sonda — controle, sem navegador
  exports/       dataset consolidado do coletor
```

O que interessa é comparar `status_http` por URL entre as duas fontes, em janelas próximas. A
sonda grava `vantagem` em cada observação justamente para que a origem de cada ponto seja
explícita no dado, e não inferida pelo horário.

Uma divergência sistemática, no mesmo endereço e na mesma hora, é medida de política de rede —
e é reportável como resultado, não como limitação.

## 6. Cotas

As dez requisições a cada seis horas somam 40 por dia, mais 4 chamadas à API do GitHub. É uma
fração pequena dos limites de conta gratuita do Apps Script, tanto em chamadas de
`UrlFetchApp` quanto em tempo diário de gatilho.

## 7. Manutenção

A lista `ALVOS` **duplica as sementes do catálogo**
([`targets.yaml`](../../backend/src/acessisaude_audit/catalog/targets.yaml)), porque o Apps
Script não tem como ler o YAML do repositório. Se o catálogo mudar e esta lista não, a sonda
passa a observar endereços diferentes dos auditados e deixa de servir como controle.

Ao alterar o catálogo, rode o verificador — ele existe para que a divergência apareça, em vez
de a sonda passar a medir outra coisa em silêncio:

```powershell
python scripts\sonda-de-vantagem\conferir_alvos.py
```
