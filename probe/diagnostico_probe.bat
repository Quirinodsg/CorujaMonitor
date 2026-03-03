@echo off
title Coruja Monitor - Diagnostico da Probe
color 0E

echo.
echo ========================================
echo   DIAGNOSTICO DA PROBE
echo ========================================
echo.

REM Mudar para o diretorio do script
cd /d "%~dp0"

echo [1] Verificando arquivo de configuracao...
echo.
if exist probe_config.json (
    echo [OK] Arquivo probe_config.json encontrado
    echo.
    echo Conteudo:
    type probe_config.json
    echo.
) else (
    echo [ERRO] Arquivo probe_config.json NAO encontrado!
    echo.
)

echo ========================================
echo [2] Verificando servico Windows...
echo.
sc query CorujaProbe
echo.

echo ========================================
echo [3] Verificando logs...
echo.
if exist probe.log (
    echo [OK] Arquivo de log encontrado
    echo.
    echo Ultimas 30 linhas:
    powershell -Command "Get-Content probe.log -Tail 30"
    echo.
) else (
    echo [AVISO] Arquivo probe.log nao encontrado
    echo.
)

echo ========================================
echo [4] Testando conectividade...
echo.
echo Testando API na porta 8000 (backend):
python -c "import httpx; r = httpx.get('http://localhost:8000/health', timeout=5); print('API OK - Status:', r.status_code)" 2>nul
if %errorLevel% neq 0 (
    echo [ERRO] API nao esta respondendo em http://localhost:8000
    echo.
    echo IMPORTANTE: A probe precisa se conectar a API (porta 8000), nao ao frontend (porta 3000)!
    echo.
)

echo.
echo ========================================
echo   INFORMACOES IMPORTANTES
echo ========================================
echo.
echo A URL correta da probe deve ser:
echo   http://localhost:8000  (API/Backend)
echo.
echo NAO use:
echo   http://localhost:3000  (Frontend/Interface)
echo.
echo Se voce configurou errado, edite o arquivo:
echo   probe_config.json
echo.
echo E altere "api_url" para: http://localhost:8000
echo.
echo Depois reinicie o servico:
echo   net stop CorujaProbe
echo   net start CorujaProbe
echo.

pause
