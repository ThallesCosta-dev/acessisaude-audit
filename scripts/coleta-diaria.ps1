<#
.SYNOPSIS
    Uma janela diária da série temporal, a partir da posição de rede brasileira.

.DESCRIPTION
    Braço brasileiro do desenho pareado. O braço estrangeiro roda no GitHub
    Actions, três vezes ao dia, e não consegue auditar dois dos cinco alvos
    porque eles recusam requisições de origem estrangeira. Este script roda da
    conexão residencial, que responde 200 em todos os endereços.

    A ordem dos passos não é arbitrária:

        1. varre o conjunto de validação sintético
        2. AFERE o instrumento contra essa varredura ─── reprovou? aborta aqui
        3. varre os alvos habilitados no catálogo
        4. exporta o dataset acumulado
        5. publica no ramo serie-temporal (tolerante a falha)

    Se o passo 2 falhar, nada toca portal público: um instrumento não aferido
    produz número, não resultado, e ainda impõe carga a servidor de terceiro.

    O passo 5 tolera falha de propósito. A coleta já está salva em disco quando
    ele roda; deixar um erro de rede ou de git derrubar a execução transformaria
    problema de transporte em perda de observação.

.PARAMETER SemPublicar
    Não publica no ramo remoto. Os dados ficam apenas em data/scans.

.PARAMETER Contato
    Identificação da pesquisa no User-Agent. Sem ela a coleta recusa executar.

.EXAMPLE
    .\scripts\coleta-diaria.ps1

.EXAMPLE
    .\scripts\coleta-diaria.ps1 -SemPublicar
#>
[CmdletBinding()]
param(
    [switch]$SemPublicar,
    [string]$Contato = "AcessiSaude-Audit/0.1 (pesquisa academica; +thalles.costa@ioc.fiocruz.br)"
)

# "Continue", e nao "Stop", por uma razao especifica do Windows PowerShell 5.1:
# ele empacota cada linha de stderr de um executavel nativo num ErrorRecord, e
# com "Stop" a primeira linha de log do coletor — que e informativa — derrubaria
# a coleta inteira. O controle de falha aqui e feito por $LASTEXITCODE apos cada
# chamada nativa, que e explicito e nao depende do que o programa escreve.
$ErrorActionPreference = "Continue"

# ---------------------------------------------------------------------------
# Ambiente
# ---------------------------------------------------------------------------

$Raiz = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Raiz

$Python = Join-Path $Raiz ".venv\Scripts\python.exe"
$Acessisaude = Join-Path $Raiz ".venv\Scripts\acessisaude.exe"

if (-not (Test-Path $Python)) {
    throw "Ambiente virtual nao encontrado em $Python. Crie com: python -m venv .venv"
}

# Registro em arquivo: a tarefa agendada roda sem ninguem olhando, e uma falha
# que nao deixa rastro e indistinguivel de uma execucao que nao aconteceu.
$PastaLog = Join-Path $Raiz "data\logs"
if (-not (Test-Path $PastaLog)) { New-Item -ItemType Directory -Path $PastaLog -Force | Out-Null }
$Log = Join-Path $PastaLog ("coleta-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".log")

# Start-Transcript captura tambem a saida dos executaveis nativos, o que a
# redirecao por fluxo nao faz sem transformar stderr em erro.
Start-Transcript -Path $Log -Force | Out-Null

function Escrever($Mensagem) {
    Write-Host ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $Mensagem)
}

$env:ACESSISAUDE_USER_AGENT_SUFFIX = $Contato
$env:PYTHONIOENCODING = "utf-8"

Escrever "Coleta diaria — posicao de rede: residencial, Brasil"
Escrever "Registro: $Log"

# ---------------------------------------------------------------------------
# 1. Conjunto de validacao
# ---------------------------------------------------------------------------

Escrever "Subindo o servidor do conjunto de validacao..."
$Servidor = Start-Process -FilePath $Python `
    -ArgumentList "scripts\servidor_fixtures.py", "--porta", "8080" `
    -WorkingDirectory $Raiz -PassThru -WindowStyle Hidden

try {
    # Espera a porta abrir em vez de dormir um tempo fixo: em maquina fria o
    # servidor demora mais, e um sleep curto produziria falha intermitente.
    $pronto = $false
    foreach ($tentativa in 1..40) {
        Start-Sleep -Milliseconds 500
        $teste = Test-NetConnection -ComputerName 127.0.0.1 -Port 8080 `
                 -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($teste) { $pronto = $true; break }
    }
    if (-not $pronto) { throw "Servidor de fixtures nao subiu na porta 8080." }

    Escrever "Varrendo o conjunto de validacao..."
    & $Acessisaude varrer fixtures-local --sem-relatorio
    if ($LASTEXITCODE -ne 0) { throw "Falha ao varrer o conjunto de validacao." }

    # -----------------------------------------------------------------------
    # 2. Portao de afericao
    # -----------------------------------------------------------------------
    Escrever "Aferindo o instrumento..."
    & $Python "scripts\aferir_instrumento.py"
    if ($LASTEXITCODE -ne 0) {
        throw "AFERICAO REPROVADA. Nenhum portal publico foi acessado. Ver $Log"
    }
    Escrever "Afericao aprovada."
}
finally {
    if ($Servidor -and -not $Servidor.HasExited) {
        Stop-Process -Id $Servidor.Id -Force -ErrorAction SilentlyContinue
        Escrever "Servidor de fixtures encerrado."
    }
}

# ---------------------------------------------------------------------------
# 3. Alvos de producao
# ---------------------------------------------------------------------------

$Alvos = & $Python "scripts\listar_alvos.py"

if ([string]::IsNullOrWhiteSpace($Alvos)) {
    Escrever "Nenhum alvo habilitado no catalogo. Nada a fazer."
    exit 0
}

Escrever "Alvos: $Alvos"
$Falhas = 0

foreach ($alvo in ($Alvos -split '\s+' | Where-Object { $_ })) {
    Escrever "--- $alvo ---"
    # Um alvo indisponivel nao interrompe a serie: a perda e dado, e o motor ja
    # a reporta como taxa de perda. Interromper produziria lacuna silenciosa.
    & $Acessisaude varrer $alvo --sem-relatorio
    if ($LASTEXITCODE -ne 0) {
        Escrever "Falha ao varrer $alvo — prosseguindo."
        $Falhas++
    }
}

Escrever "Exportando o dataset acumulado..."
& $Acessisaude exportar

# ---------------------------------------------------------------------------
# 4. Publicacao no ramo da serie
# ---------------------------------------------------------------------------

if ($SemPublicar) {
    Escrever "Publicacao desativada por parametro."
}
else {
    # Tolerante a falha por decisao: os dados ja estao em disco, e um erro de
    # rede ou de git aqui nao pode custar a observacao.
    try {
        Escrever "Publicando em serie-temporal/scans-br ..."

        # Diretorio proprio: o braco estrangeiro publica em scans/, e misturar
        # as duas posicoes de rede no mesmo lugar destruiria a comparacao que e
        # a razao de existir do desenho pareado.
        $Arvore = Join-Path $env:TEMP "acessisaude-serie"
        if (Test-Path $Arvore) { git worktree remove $Arvore --force 2>$null }

        git fetch -q origin serie-temporal:serie-temporal --force
        git worktree add -q $Arvore serie-temporal

        $Destino = Join-Path $Arvore "scans-br"
        if (-not (Test-Path $Destino)) { New-Item -ItemType Directory -Path $Destino -Force | Out-Null }
        Copy-Item (Join-Path $Raiz "data\scans\*.json") $Destino -Force

        Push-Location $Arvore
        git add -A
        git diff --cached --quiet
        if ($LASTEXITCODE -ne 0) {
            $n = (Get-ChildItem (Join-Path $Arvore "scans-br") -Filter *.json).Count
            git commit -q -m ("Coleta BR {0} — {1} varreduras acumuladas" -f (Get-Date -Format "yyyy-MM-ddTHH:mmK"), $n)
            git push -q origin serie-temporal
            Escrever "Publicado: $n varreduras no braco brasileiro."
        }
        else {
            Escrever "Nada de novo a publicar."
        }
        Pop-Location

        git worktree remove $Arvore --force
    }
    catch {
        Escrever "AVISO: publicacao falhou ($($_.Exception.Message)). Os dados estao em data\scans."
        if ((Get-Location).Path -ne $Raiz) { Set-Location $Raiz }
    }
}

Escrever "Concluido. Alvos com falha de execucao: $Falhas"

Stop-Transcript | Out-Null
