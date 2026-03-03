@echo off
title Coruja Probe - Instalacao Manual
color 0A

echo.
echo ========================================
echo   INSTALACAO MANUAL DO PROBE
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    pause
    exit /b 1
)

echo Este script vai guia-lo pela instalacao manual.
echo.
pause

REM Passo 1: Verificar Python
echo.
echo [Passo 1/5] Verificando Python...
echo.
python --version
if %errorLevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Execute: check_python.bat
    pause
    exit /b 1
)
echo [OK] Python encontrado
echo.
pause

REM Passo 2: Instalar dependencias
echo.
echo [Passo 2/5] Instalando dependencias...
echo.
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.
pause

REM Passo 3: Configurar
echo.
echo [Passo 3/5] Configuracao
echo.
echo Edite o arquivo probe_config.json com:
echo - api_url: URL do servidor Coruja
echo - probe_token: Token do probe
echo.
echo Exemplo:
echo {
echo   "api_url": "http://192.168.1.100:8000",
echo   "probe_token": "seu-token-aqui",
echo   "collection_interval": 60,
echo   "monitored_services": ["W3SVC", "MSSQLSERVER"],
echo   "udm_targets": ["8.8.8.8"]
echo }
echo.
echo Pressione qualquer tecla apos editar o arquivo...
pause

REM Passo 4: Testar
echo.
echo [Passo 4/5] Testando conexao...
echo.
echo Pressione Ctrl+C para parar o teste
echo.
timeout /t 3 /nobreak
python probe_core.py
echo.
echo Se funcionou, pressione qualquer tecla para continuar...
pause

REM Passo 5: Instalar servico
echo.
echo [Passo 5/5] Instalando como servico Windows...
echo.
python probe_service.py install
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar servico
    pause
    exit /b 1
)

python probe_service.py start
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao iniciar servico
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Comandos uteis:
echo - Ver status: sc query CorujaProbe
echo - Ver logs: type probe.log
echo - Parar: net stop CorujaProbe
echo - Iniciar: net start CorujaProbe
echo.
pause
