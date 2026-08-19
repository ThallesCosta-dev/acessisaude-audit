# Sonda de vantagem em posição brasileira — Cloud Run

Contêiner mínimo que observa os endereços do catálogo a partir de
`southamerica-east1`. **Não audita acessibilidade** — não há navegador aqui.

---

## 1. A pergunta que este contêiner responde

A coleta contínua roda em runner do GitHub e não consegue auditar dois dos cinco alvos. As
medições até agora:

| Endereço | GitHub (EUA) | Apps Script (EUA) | Residencial (Brasil) |
|---|---|---|---|
| `meususdigital.saude.gov.br/` | **403** | 200 | 200 |
| `www.rj.gov.br/saude/` | conexão encerrada | **500** | 200 |
| `saude.rj.gov.br/laudos` | conexão encerrada | **500** | 200 |
| demais sete endereços | 200 | 200 | 200 |

Falta uma célula, e ela decide onde a coleta contínua vai morar:

> **Um IP brasileiro de datacenter é tratado como o residencial, ou como as nuvens
> estrangeiras?**

- **200 nos dez** → migre a auditoria para o Cloud Run e a coleta fica automatizada.
- **403 ou 500** → a política discrimina faixas de datacenter, e nenhuma nuvem resolve. O
  único ponto de observação que serve é uma conexão residencial brasileira, e a decisão passa
  a ser o runner auto-hospedado.

Os dois resultados encerram a dúvida, e o segundo economiza a migração inteira.

## 2. O que roda

`sonda.py` faz dez requisições `GET`, com dois segundos de intervalo, e imprime uma tabela. A
imagem tem cerca de 60 MB — sem Chromium, porque não audita — e o job executa em menos de
meio minuto. O custo por execução é fração de centavo.

**A lista de endereços não é duplicada.** O contêiner lê o próprio
[`targets.yaml`](../../backend/src/acessisaude_audit/catalog/targets.yaml), aplicando a mesma
regra de `auditable_seeds`: alvos habilitados, exceto o conjunto sintético, e sementes que não
exigem autenticação. Se o catálogo mudar, a sonda muda junto — ao contrário da
[sonda do Apps Script](../sonda-de-vantagem/README.md), que precisa duplicar a lista porque
não consegue ler o repositório.

Conduta de coleta: identificação obrigatória no `User-Agent` — sem ela o contêiner recusa
executar, com código de saída 2 —, dois segundos entre requisições, apenas `GET` a páginas
públicas.

## 3. Passo a passo

> **Verificado:** o contêiner e o `sonda.py` foram executados nesta máquina e devolveram
> 10 de 10 respostas 200, que é a linha de base residencial. **Não verificado:** os comandos
> `gcloud` abaixo, porque não há `gcloud` nem Docker instalados aqui. Se algum falhar, me
> mande a mensagem.

Tudo pelo **Cloud Shell**, que já traz `gcloud`, `docker` e `git` — não é preciso instalar
nada na máquina.

### 3.1 Abrir o Cloud Shell e obter o código

No console do Google Cloud, clique no ícone do terminal (canto superior direito).

```bash
# O repositório é privado. Use o mesmo token fine-grained da sonda do Apps Script,
# ou crie outro com permissão de Contents: Read.
git clone https://SEU_TOKEN@github.com/ThallesCosta-dev/acessisaude-audit.git
cd acessisaude-audit
```

### 3.2 Definir as variáveis da sessão

```bash
export PROJETO="$(gcloud config get-value project)"
export REGIAO="southamerica-east1"
export IMAGEM="${REGIAO}-docker.pkg.dev/${PROJETO}/sondas/sonda:v1"
export CONTATO="AcessiSaude-Audit/0.1 (sonda de vantagem; +thalles.costa@ioc.fiocruz.br)"

echo "projeto=$PROJETO  imagem=$IMAGEM"
```

Confira que o projeto apareceu. Se vier vazio, rode `gcloud config set project SEU_PROJETO`.

### 3.3 Habilitar as APIs

```bash
gcloud services enable run.googleapis.com \
                       cloudbuild.googleapis.com \
                       artifactregistry.googleapis.com
```

### 3.4 Criar o repositório de imagens

```bash
gcloud artifacts repositories create sondas \
  --repository-format=docker \
  --location="$REGIAO" \
  --description="Sondas de vantagem do AcessiSaude-Audit"
```

Se disser que já existe, siga em frente.

### 3.5 Construir a imagem

```bash
gcloud builds submit \
  --config scripts/sonda-cloud-run/cloudbuild.yaml \
  --substitutions=_IMAGEM="$IMAGEM"
```

O `cloudbuild.yaml` existe por um motivo de segurança, não de conveniência: `--source .`
procuraria o `Dockerfile` da raiz, que é o do coletor — com Chromium e um `CMD` que varre
portais públicos. Construir e rodar a imagem errada aqui imporia carga indevida a servidor de
terceiro.

### 3.6 Criar o job

```bash
gcloud run jobs deploy sonda-vantagem-br \
  --image "$IMAGEM" \
  --region "$REGIAO" \
  --max-retries 0 \
  --task-timeout 5m \
  --memory 512Mi \
  --set-env-vars "ACESSISAUDE_USER_AGENT_SUFFIX=${CONTATO},VANTAGEM=cloud-run-southamerica-east1"
```

`--max-retries 0` é deliberado: uma sonda que falha por indisponibilidade do alvo **mediu**, e
repetir apagaria a observação, que é o dado.

### 3.7 Executar

```bash
gcloud run jobs execute sonda-vantagem-br --region "$REGIAO" --wait
```

### 3.8 Ler o resultado

```bash
gcloud logging read \
  'resource.type=cloud_run_job AND resource.labels.job_name=sonda-vantagem-br' \
  --limit 40 --format='value(textPayload)' --freshness=15m
```

Ou abra **Cloud Run → Jobs → sonda-vantagem-br → Execuções → Registros** no console.

A tabela impressa tem uma linha por endereço, com status, bytes e tempo. **A linha do
`meususdigital` e as duas da SES-RJ são a resposta.**

## 4. Interpretando

| Resultado | Leitura | O que fazer |
|---|---|---|
| 10 de 10 respondem 200 | IP brasileiro de datacenter é tratado como residencial | Migrar a auditoria para o Cloud Run |
| `meususdigital` 403, SES-RJ 500 | a política alcança faixas de datacenter, brasileiras inclusive | Runner auto-hospedado; a nuvem não resolve |
| resultado intermediário | há mais de uma política em jogo | Repetir em outra janela antes de decidir |

Qualquer que seja, é resultado publicável: são quatro posições de observação sobre o mesmo
conjunto de endereços, e a literatura de avaliação de acessibilidade levantada para este
trabalho não mede essa dimensão.

## 5. Se quiser mantê-la rodando

Publicação automática no ramo da série, como faz a sonda do Apps Script — acrescente o token à
variável de ambiente do job:

```bash
gcloud run jobs update sonda-vantagem-br --region "$REGIAO" \
  --set-env-vars "ACESSISAUDE_USER_AGENT_SUFFIX=${CONTATO},VANTAGEM=cloud-run-southamerica-east1,GITHUB_TOKEN=SEU_TOKEN"
```

Em uso prolongado, prefira o Secret Manager a variável de ambiente para o token.

Agendamento a cada seis horas:

```bash
gcloud scheduler jobs create http sonda-vantagem-br-6h \
  --location "$REGIAO" \
  --schedule "23 */6 * * *" \
  --uri "https://${REGIAO}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJETO}/jobs/sonda-vantagem-br:run" \
  --http-method POST \
  --oauth-service-account-email "$(gcloud projects describe "$PROJETO" --format='value(projectNumber)')-compute@developer.gserviceaccount.com"
```

## 6. Desmontar

```bash
gcloud scheduler jobs delete sonda-vantagem-br-6h --location "$REGIAO"
gcloud run jobs delete sonda-vantagem-br --region "$REGIAO"
gcloud artifacts repositories delete sondas --location "$REGIAO"
```

## 7. Executando localmente, para comparar

A linha de base residencial, medida nesta máquina em 19/08/2026, foi **10 de 10 com 200**:

```powershell
$env:ACESSISAUDE_USER_AGENT_SUFFIX = "AcessiSaude-Audit/0.1 (pesquisa academica; +seu@email)"
$env:CATALOGO = "backend\src\acessisaude_audit\catalog\targets.yaml"
$env:VANTAGEM = "local-brasil-residencial"
python scripts\sonda-cloud-run\sonda.py
```

É o mesmo código que roda no contêiner, com o mesmo catálogo — a única variável é a posição de
rede, que é exatamente o que se quer medir.
