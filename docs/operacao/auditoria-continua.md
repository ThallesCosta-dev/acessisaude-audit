# Auditoria contínua

> Como transformar a promessa do título — auditoria **contínua** — em resultado.

---

## 1. Por que isto existe

A coleta de referência produziu quatro medições em 47 minutos. Isso atesta a
**confiabilidade do instrumento**: o índice de conformidade não variou, e o conjunto de
critérios violados repetiu-se. Não atesta a **persistência das barreiras no tempo**, que é
afirmação diferente e exige janelas separadas por dias.

Enquanto a série não existir, o trabalho descreve um instrumento de auditoria contínua sem
exibir a continuidade. É a lacuna mais visível do artigo, e a única que não se resolve
escrevendo melhor.

Há um segundo motivo, que a própria coleta revelou. O portal estadual oscilou em escala de
**minutos**, com falha igual em navegador e em cliente HTTP simples. Uma coleta em horário
fixo não distingue indisponibilidade circunstancial de crônica; três janelas diárias em
horários dispersos, ao longo de semanas, distinguem.

---

## 2. O que uma execução faz

```
1. varre o conjunto de validação sintético
2. AFERE o instrumento contra essa varredura ──── reprovou? aborta aqui
3. varre os alvos habilitados no catálogo
4. exporta o dataset acumulado em CSV
```

A ordem é a decisão de projeto que mais importa. Se o passo 2 falhar, nada toca portal
público. Um instrumento não aferido produz número, não resultado — e ainda impõe carga a
servidor de terceiro sem contrapartida.

O portão está em [`scripts/aferir_instrumento.py`](../../scripts/aferir_instrumento.py) e
verifica duas propriedades:

| Propriedade | Verificação | Por quê |
|---|---|---|
| Especificidade | A página conforme não produz **nenhuma** violação | Um falso positivo aqui invalida a coleta inteira: o motor passou a reprovar o que é correto |
| Sensibilidade | O controle positivo detecta ao menos **15** critérios distintos | Detecta regressão do motor — uma atualização que deixe de reportar uma classe inteira de falha |

O piso de 15 é deliberadamente inferior aos 18 aferidos no estudo. O portão existe para
detectar **regressão**, não para reproduzir a validação, que é feita contra o manifesto e
revisada por humano. Os dois perfis não são equivalentes: o perfil móvel detecta 18 critérios
e o de desktop, 17 — um piso de 18 reprovaria o desktop em toda execução.

O comportamento está travado em
[`backend/tests/unit/test_afericao_continua.py`](../../backend/tests/unit/test_afericao_continua.py).

---

## 3. Conduta de coleta

Antes de habilitar qualquer agendamento, leia
[ética e conduta de coleta](../metodologia/etica-e-conduta-de-coleta.md). Três pontos são
inegociáveis e estão implementados como falha, não como recomendação:

1. **Identificação obrigatória.** Sem `ACESSISAUDE_USER_AGENT_SUFFIX`, o script de coleta
   recusa executar. Um portal público precisa poder saber quem o acessa e a quem reclamar.
2. **Alvos nascem desabilitados.** O agendamento varre apenas o que está `enabled: true` no
   catálogo. Habilitar continua sendo decisão consciente do pesquisador.
3. **Intervalo mínimo entre requisições.** Padrão de 2.000 ms, elevável, e a redução exige
   decisão explícita registrada.

Carga real de uma execução: cerca de 10 páginas por plataforma, três vezes ao dia. É tráfego
desprezível para qualquer portal em produção, e é menos do que um rastreador de busca comum.

---

## 4. Caminho A — GitHub Actions (recomendado para a pesquisa)

[`.github/workflows/coleta.yml`](../../.github/workflows/coleta.yml)

> O arquivo se chama `coleta.yml`, e não `auditoria-continua.yml`, por um motivo
> operacional: o GitHub não registrou o workflow quando ele chegou no push inicial do
> repositório — a página respondia "This workflow does not exist" com o arquivo presente no
> ramo padrão, sem erro de sintaxe e com o Actions habilitado. Um push adicional não resolveu;
> renomear o arquivo resolveu, porque o GitHub passou a tratá-lo como workflow novo em vez de
> reprocessar um que já havia classificado. Registrado aqui para poupar o diagnóstico a quem
> reimplantar o projeto.

**Por que este é o caminho padrão:** é gratuito, versiona os artefatos, e o dataset ganha um
endereço estável e citável. Para produzir a série temporal que o artigo precisa, é o
suficiente.

### Habilitar

1. **Settings → Secrets and variables → Actions → Variables**, criar
   `CONTATO_PESQUISA`:

   ```
   AcessiSaude-Audit/pesquisa (+fulano@instituicao.br)
   ```

   Sem essa variável o fluxo falha de propósito, com mensagem explicando por quê.

2. Opcionalmente, `REQUEST_DELAY_MS` para elevar o intervalo entre requisições.

3. **Actions → Auditoria contínua → Run workflow**, marcando *apenas_afericao*, para uma
   primeira execução que não toca em nenhum portal público. Serve para validar o ambiente.

4. Removida a marcação, o agendamento passa a rodar às 03h17, 14h43 e 21h29 UTC.

### Onde os dados ficam

Ramo órfão **`serie-temporal`**, com apenas dados e sem histórico de código:

```
serie-temporal/
  scans/     todos os JSON, acumulados
  exports/   achados.csv e paginas.csv, reexportados sobre a série INTEIRA
```

Cada execução também guarda os artefatos por 90 dias, redundância deliberada: os JSON são a
fonte da verdade da pesquisa, e o *push* para o ramo pode falhar.

Para analisar localmente:

```powershell
git fetch origin serie-temporal
git worktree add ..\serie serie-temporal
python -c "from acessisaude_audit.analysis import dataset; print(len(dataset.load_scans(r'..\serie\scans')))"
```

---

## 5. Caminho B — Render (recomendado se o painel deve ficar no ar)

[`render.yaml`](../../render.yaml) + [`Dockerfile`](../../Dockerfile)

Define quatro peças: um **cron** de coleta, um **Postgres**, a **API** e o **painel** estático.

### A restrição que precisa ser entendida antes

O cron do Render **não tem disco persistente**: o que for gravado em `/app/data` desaparece ao
fim da execução. A procedência sobrevive por uma razão de arquitetura — o repositório grava o
documento JSON íntegro na coluna `document` da tabela de varreduras, e o índice relacional é
inteiramente derivável dele.

Consequência prática: **com Postgres anexado, nada se perde; sem ele, perde-se tudo.** Não
remova o banco do blueprint.

### Habilitar

1. Conectar o repositório no Render e aplicar o blueprint.
2. Definir `ACESSISAUDE_USER_AGENT_SUFFIX` no serviço de coleta (marcado `sync: false`,
   portanto não versionado).
3. Após o primeiro *deploy*, ajustar `ACESSISAUDE_CORS_ORIGINS` na API para o endereço
   publicado do painel.

### Extrair a série do Postgres

```python
from acessisaude_audit.domain.models import ScanResult
from acessisaude_audit.persistence import ...  # sessão apontando para o Postgres

# O documento é a fonte da verdade; o índice é derivado.
scans = [ScanResult.model_validate(row.document) for row in session.query(ScanRow).all()]
```

---

## 5.1 Sonda de vantagem — controle de rede

A coleta a partir de um único ponto de observação não distingue **portal indisponível** de
**portal que recusa aquele IP**. A distinção é decisiva: a primeira é achado — disponibilidade
como precondição da acessibilidade —, a segunda é artefato do instrumento, da mesma classe do
User-Agent `HeadlessChrome` do ADR 0008.

A primeira semana de coleta pelo runner do GitHub produziu o caso concreto: o Meu SUS Digital
devolveu HTTP 403 em 8 de 8 tentativas e duas páginas da SES-RJ nunca carregaram, enquanto os
mesmos endereços respondem HTTP 200 de um IP residencial brasileiro.

A [sonda de vantagem](../../scripts/sonda-de-vantagem/) acrescenta um terceiro ponto de
observação, no Google Apps Script. Não audita acessibilidade — apenas pergunta "este endereço
responde?" — e por isso não precisa de navegador, o que a torna implantável em cinco minutos e
sem custo. Ver [o README da sonda](../../scripts/sonda-de-vantagem/README.md).

---

## 6. Comparação

| | GitHub Actions | Render |
|---|---|---|
| Custo | Gratuito | Pago acima do plano gratuito |
| Persistência dos JSON | Ramo git, versionado | Coluna `document` no Postgres |
| Dataset citável | Sim, por *commit* | Requer exportação |
| Painel público | Não | Sim |
| Melhor para | Produzir a série do artigo | Monitoramento visível a gestor |

Os dois podem coexistir: o Actions produz o dado da pesquisa, o Render exibe o resultado.

---

## 7. Antes de publicar a série

Três cuidados, todos derivados de decisões já tomadas no projeto:

1. **Declarar o κ vigente.** Séries coletadas com parâmetros de pontuação distintos não são
   comparáveis. Se `ScoringParameters` mudar, registrar em `docs/adr/` e tratar como série
   nova — ver [índices](../metodologia/indices.md#calibracao).
2. **Declarar a versão do axe-core.** Cada varredura já carrega a sua; uma atualização do
   motor muda o que é detectável e cria degrau na série.
3. **Comunicar os órgãos auditados.** Monitoramento contínuo de portal público é atividade
   legítima de pesquisa, e comunicá-la previamente — com o relatório HTML encaminhado — é
   parte da conduta que este projeto declara.
