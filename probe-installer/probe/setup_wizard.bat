@echo off
title Coruja Monitor - Instalador do Probe
color 0A

echo.
echo ========================================
echo    CORUJA MONITOR - INSTALADOR
echo ========================================
echo.

REM Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Este instalador precisa ser executado como Administrador!
    echo.
    echo Clique com botao direito e selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Executando como Administrador
echo.

REM Mudar para o diretorio do script
cd /d "%~dp0"
echo [OK] Diretorio: %CD%
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.11 ou superior:
    echo https://www.python.org/downloads/
    echo.
    echo Lembre-se de marcar "Add Python to PATH" durante a instalacao
    echo.
    pause
    exit /b 1
)

echo [OK] Python instalado
python --version
echo.

REM Instalar dependencias
echo ========================================
echo Instalando dependencias...
echo ========================================
echo.
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo.
echo [OK] Dependencias instaladas
echo.

REM Configurar probe
echo ========================================
echo Configuracao do Probe
echo ========================================
echo.

set /p API_URL="Digite a URL do servidor Coruja (ex: http://192.168.1.100:8000): "
set /p PROBE_TOKEN="Cole o token do probe: "

echo.
echo Criando arquivo de configuracao...

(
echo {
echo   "api_url": "%API_URL%",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "monitored_services": [
echo     "W3SVC",
echo     "MSSQLSERVER"
echo   ],
echo   "udm_targets": [
echo     "8.8.8.8"
echo   ]
echo }
) > probe_config.json

echo [OK] Configuracao salva
echo.

REM Testar conexao
echo ========================================
echo Testando conexao com o servidor...
echo ========================================
echo.

python -c "import httpx; r = httpx.get('%API_URL%/health', timeout=5); print('Conexao OK!' if r.status_code == 200 else 'Erro na conexao')" 2>nul
if %errorLevel% neq 0 (
    echo [AVISO] Nao foi possivel conectar ao servidor
    echo Verifique a URL e tente novamente
    echo.
    set /p CONTINUE="Deseja continuar mesmo assim? (S/N): "
    if /i not "%CONTINUE%"=="S" exit /b 1
)
echo.

REM Instalar servico
echo ========================================
echo Instalando servico Windows...
echo ========================================
echo.

python probe_service.py install
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar servico
    pause
    exit /b 1
)

echo [OK] Servico instalado
echo.

REM Iniciar servico
echo Iniciando servico...
python probe_service.py start
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao iniciar servico
    pause
    exit /b 1
)

echo [OK] Servico iniciado
echo.

REM Verificar status
sc query CorujaProbe | findstr "RUNNING" >nul
if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo   INSTALACAO CONCLUIDA COM SUCESSO!
    echo ========================================
    echo.
    echo O Coruja Probe esta rodando como servico Windows
    echo.
    echo Proximos passos:
    echo 1. Aguarde 2-3 minutos
    echo 2. Acesse o dashboard do Coruja Monitor
    echo 3. Verifique se o probe aparece como "Online"
    echo 4. Os dados comecarao a aparecer automaticamente
    echo.
    echo Comandos uteis:
    echo - Ver logs: type probe.log
    echo - Parar: net stop CorujaProbe
    echo - Iniciar: net start CorujaProbe
    echo - Desinstalar: uninstall_service.bat
    echo.
) else (
    echo [AVISO] Servico instalado mas nao esta rodando
    echo Execute: net start CorujaProbe
    echo.
)

pause
