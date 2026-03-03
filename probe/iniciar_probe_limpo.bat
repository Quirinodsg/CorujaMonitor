@echo off
echo ========================================
echo   INICIAR PROBE (LIMPO)
echo ========================================
echo.

REM Verificar se probe_config.json existe
if not exist "probe_config.json" (
    echo [ERRO] Arquivo probe_config.json nao encontrado!
    echo.
    echo Execute primeiro: configurar_probe.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Configuracao encontrada:
type probe_config.json
echo.
echo.

echo [1/2] Verificando se ja existe probe rodando...
tasklist | findstr /I "python" >nul 2>&1
if %errorLevel% equ 0 (
    echo [AVISO] Ja existem processos Python rodando:
    tasklist | findstr /I "python"
    echo.
    echo Execute primeiro: parar_todas_probes.bat (como Administrador)
    echo.
    pause
    exit /b 1
)

echo [OK] Nenhuma probe rodando
echo.

echo [2/2] Iniciando probe em segundo plano...
start /MIN python probe_core.py

timeout /t 3 /nobreak >nul

echo.
echo [OK] Probe iniciada!
echo.
echo Para verificar se esta funcionando:
echo   1. Veja o arquivo probe.log
echo   2. Aguarde 60 segundos
echo   3. Verifique no dashboard se os sensores receberam dados
echo.
echo Para parar a probe:
echo   Execute parar_todas_probes.bat como Administrador
echo.
pause
