@echo off
REM ========================================
REM ATUALIZAR SCRIPT DE CONFIGURACAO
REM Copia a versao corrigida do configurador
REM ========================================

echo.
echo ========================================
echo   ATUALIZAR CONFIGURADOR DA PROBE
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERRO] Execute como Administrador!
    echo.
    echo Clique direito neste arquivo e selecione:
    echo "Executar como Administrador"
    echo.
    pause
    exit /b 1
)

set "INSTALL_DIR=%ProgramFiles%\CorujaMonitor\Probe"

if not exist "%INSTALL_DIR%" (
    color 0C
    echo [ERRO] Probe nao esta instalada!
    echo.
    echo Execute primeiro: INSTALAR_PROBE_AGORA.bat
    echo.
    pause
    exit /b 1
)

if not exist "probe\configurar_probe.bat" (
    color 0C
    echo [ERRO] Arquivo configurar_probe.bat nao encontrado!
    echo.
    echo Execute este script na pasta raiz do projeto
    echo.
    pause
    exit /b 1
)

echo Copiando versao corrigida...
copy /Y "probe\configurar_probe.bat" "%INSTALL_DIR%\configurar_probe.bat" >nul 2>&1

if %errorLevel% equ 0 (
    color 0A
    echo.
    echo ========================================
    echo   ATUALIZADO COM SUCESSO!
    echo ========================================
    echo.
    echo O script de configuracao foi atualizado.
    echo.
    echo Agora execute:
    echo - Desktop: "Configurar Coruja Probe"
    echo.
    echo OU
    echo.
    echo - Diretamente: %INSTALL_DIR%\configurar_probe.bat
    echo.
) else (
    color 0C
    echo [ERRO] Falha ao copiar arquivo!
    echo.
)

pause
