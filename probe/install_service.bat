@echo off
REM Mudar para o diretorio do script
cd /d "%~dp0"

echo ========================================
echo   CORUJA MONITOR - INSTALADOR
echo ========================================

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Este script requer privilegios de administrador.
    echo Por favor, execute como administrador.
    pause
    exit /b 1
)
echo [OK] Executando como Administrador

REM Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8 ou superior.
    pause
    exit /b 1
)
echo [OK] Python instalado
python --version

echo ========================================
echo Instalando dependencias...
echo ========================================

REM Install Python dependencies
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

echo ========================================
echo Instalando servico Windows...
echo ========================================

REM Install Windows service
python probe_service.py install
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar servico
    pause
    exit /b 1
)
echo [OK] Servico instalado

echo ========================================
echo Iniciando servico...
echo ========================================

REM Start service
python probe_service.py start
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao iniciar servico
    pause
    exit /b 1
)
echo [OK] Servico iniciado

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Servico: Coruja Probe
echo Status: Rodando
echo.
echo Para configurar:
echo 1. Edite probe_config.json
echo 2. Reinicie: net stop "Coruja Probe" ^&^& net start "Coruja Probe"
echo.
echo Para verificar status:
echo - Execute: verificar_status.bat
echo.
pause
