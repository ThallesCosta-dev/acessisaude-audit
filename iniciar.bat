@echo off
setlocal EnableExtensions
chcp 65001 >nul
title AcessiSaúde-Audit

:: =============================================================================
:: AcessiSaúde-Audit — inicialização em um clique
:: =============================================================================
:: Faz, nesta ordem, só o que ainda falta:
::   1. cria o ambiente virtual Python (.venv) e instala o backend
::   2. baixa o Chromium do Playwright
::   3. instala as dependências do painel (frontend/node_modules)
::   4. se ainda não há nenhuma varredura, oferece rodar a primeira contra o
::      conjunto de validação local (sem tocar em servidor público)
::   5. sobe a API (porta 8000) e o painel (porta 5173) em janelas próprias
::
:: Uso:  iniciar.bat            inicia tudo
::       iniciar.bat --auditar  força a auditoria do conjunto de validação
:: =============================================================================

cd /d "%~dp0"
set "RAIZ=%CD%"
set "VENV=%RAIZ%\.venv"
set "ATIVAR=%VENV%\Scripts\activate.bat"
set "CLI=%VENV%\Scripts\acessisaude.exe"

echo.
echo  ===== AcessiSaúde-Audit =====
echo.

:: ---------------------------------------------------------------- requisitos
where python >nul 2>&1 || (
    echo [ERRO] Python não encontrado no PATH. Instale o Python 3.11+ em https://www.python.org/downloads/
    goto :falha
)
where npm >nul 2>&1 || (
    echo [ERRO] Node.js/npm não encontrado no PATH. Instale o Node 18+ em https://nodejs.org/
    goto :falha
)

:: ---------------------------------------------------------- backend (Python)
set "PRIMEIRA_INSTALACAO=0"
if not exist "%ATIVAR%" (
    echo [1/5] Criando ambiente virtual em .venv ...
    python -m venv "%VENV%" || goto :falha
    set "PRIMEIRA_INSTALACAO=1"
)
call "%ATIVAR%" || goto :falha

if not exist "%CLI%" (
    echo [1/5] Instalando o backend ^(pode levar alguns minutos^) ...
    python -m pip install --upgrade pip >nul
    pip install -e "backend[analysis,dev]" || goto :falha
    set "PRIMEIRA_INSTALACAO=1"
) else (
    echo [1/5] Backend já instalado.
)

if "%PRIMEIRA_INSTALACAO%"=="1" (
    echo [2/5] Baixando o Chromium do Playwright ^(~150 MB^) ...
    playwright install chromium || goto :falha
) else (
    echo [2/5] Chromium: pulando ^(rode "playwright install chromium" se a auditoria reclamar^).
)

:: ------------------------------------------------------------ painel (Node)
if not exist "frontend\node_modules" (
    echo [3/5] Instalando dependências do painel ...
    pushd frontend
    call npm install || (popd & goto :falha)
    popd
) else (
    echo [3/5] Painel já instalado.
)

:: ------------------------------------------------------- primeira auditoria
set "AUDITAR=0"
if /i "%~1"=="--auditar" set "AUDITAR=1"
if "%AUDITAR%"=="0" (
    dir /b "data\scans\*.json" >nul 2>&1 || (
        echo.
        echo [4/5] Nenhuma varredura encontrada em data\scans. Sem ela o painel abre vazio.
        choice /C SN /T 20 /D S /M "      Auditar o conjunto de validação local agora? (S/N, padrão S em 20 s)"
        if errorlevel 2 (set "AUDITAR=0") else (set "AUDITAR=1")
    )
)

if "%AUDITAR%"=="1" (
    echo [4/5] Subindo o servidor do conjunto de validação ^(porta 8080^) ...
    start "AcessiSaúde - fixtures :8080" /min cmd /k "call "%ATIVAR%" && python scripts\servidor_fixtures.py"
    timeout /t 3 /nobreak >nul
    set "ACESSISAUDE_REQUEST_DELAY_MS=0"
    set "ACESSISAUDE_RESPECT_ROBOTS_TXT=false"
    set "ACESSISAUDE_ROBOTS_OVERRIDE_REASON=Conjunto de validacao local."
    echo [4/5] Auditando fixtures-local ...
    acessisaude varrer fixtures-local || echo [AVISO] A auditoria terminou com erro. O painel sobe mesmo assim.
) else (
    echo [4/5] Auditoria inicial: pulando.
)

:: ------------------------------------------------------------ API + painel
echo [5/5] Subindo a API e o painel ...
start "AcessiSaúde - API :8000" cmd /k "call "%ATIVAR%" && acessisaude servir"
start "AcessiSaúde - painel :5173" cmd /k "cd /d "%RAIZ%\frontend" && npm run dev"

:: Abre o navegador só quando o painel e a API respondem de fato: na primeira
:: execução o Vite e o servidor Python demoram alguns segundos para subir, e um
:: navegador aberto cedo demais mostra "conexão recusada".
set /a TENTATIVAS=0
:aguardar
curl -s -o nul http://127.0.0.1:5173/ && curl -s -o nul http://127.0.0.1:8000/saude && goto :abrir
set /a TENTATIVAS+=1
if %TENTATIVAS% geq 60 (
    echo [AVISO] O painel não respondeu em 60 s. Veja as janelas "API" e "painel" para o erro.
    goto :resumo
)
timeout /t 1 /nobreak >nul
goto :aguardar

:abrir
start "" http://127.0.0.1:5173

:resumo

echo.
echo  Pronto.
echo    Painel : http://127.0.0.1:5173
echo    API    : http://127.0.0.1:8000/docs
echo.
echo  Cada serviço roda na sua própria janela. Feche as janelas para encerrar.
echo  Outros comandos ^(com a .venv ativada^): acessisaude alvos ^| criterios ^| matriz ^| exportar
echo.
pause
exit /b 0

:falha
echo.
echo [FALHA] A inicialização foi interrompida. Veja a mensagem acima.
pause
exit /b 1
