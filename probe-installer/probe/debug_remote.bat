@echo off
echo ========================================
echo CORUJA MONITOR - DEBUG REMOTO
echo ========================================
echo.

echo Verificando probe.log...
echo.
if exist probe.log (
    echo Ultimas 50 linhas do log:
    powershell -Command "Get-Content probe.log -Tail 50"
) else (
    echo [AVISO] Arquivo probe.log nao encontrado
)

echo.
echo ========================================
echo Testando conexao com API...
echo.

REM Ler config.py para pegar API_URL e PROBE_TOKEN
for /f "tokens=2 delims='" %%a in ('findstr "API_URL" config.py') do set API_URL=%%a
for /f "tokens=2 delims='" %%a in ('findstr "PROBE_TOKEN" config.py') do set PROBE_TOKEN=%%a

echo API_URL: %API_URL%
echo PROBE_TOKEN: %PROBE_TOKEN%
echo.

echo Testando endpoint /api/v1/probes/servers...
curl -k "%API_URL%/api/v1/probes/servers?probe_token=%PROBE_TOKEN%"

echo.
echo ========================================
echo Pressione qualquer tecla para sair...
pause >nul
