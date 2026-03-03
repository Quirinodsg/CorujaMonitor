@echo off
echo ========================================
echo Diagnostico da Probe
echo ========================================
echo.

set "PROBE_PATH=C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\Coruja Monitor\probe"

echo [1] Verificando status do servico...
sc query CorujaProbe
echo.

echo [2] Verificando arquivos...
if exist "%PROBE_PATH%\probe_core.py" (
    echo [OK] probe_core.py existe
) else (
    echo [ERRO] probe_core.py NAO encontrado
)

if exist "%PROBE_PATH%\collectors\ping_collector.py" (
    echo [OK] ping_collector.py existe
) else (
    echo [ERRO] ping_collector.py NAO encontrado
)
echo.

echo [3] Ultimas linhas do log:
if exist "%PROBE_PATH%\probe.log" (
    powershell -Command "Get-Content '%PROBE_PATH%\probe.log' -Tail 30"
) else (
    echo [AVISO] probe.log nao encontrado
)
echo.

echo [4] Verificando processos Python:
tasklist | findstr python.exe
echo.

echo ========================================
echo Pressione qualquer tecla para continuar...
pause >nul
