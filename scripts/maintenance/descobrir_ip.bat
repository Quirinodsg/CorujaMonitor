@echo off
title Descobrir IP do Servidor Coruja
color 0A

echo.
echo ========================================
echo   DESCOBRIR IP DO SERVIDOR
echo ========================================
echo.

echo [1] IP da maquina Windows (use este para probes remotos):
echo.
ipconfig | findstr /i "IPv4"
echo.

echo [2] Testando conectividade local:
echo.
curl -s http://localhost:8000/health
if %errorLevel% equ 0 (
    echo.
    echo [OK] Servidor acessivel via localhost
    echo.
    echo Para probes na MESMA maquina, use:
    echo   http://localhost:8000
    echo.
) else (
    echo [AVISO] Servidor nao acessivel via localhost
)

echo.
echo [3] Testando conectividade via IP local:
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do (
    set IP=%%a
    set IP=!IP: =!
    echo Testando: !IP!
    curl -s http://!IP!:8000/health >nul 2>&1
    if !errorLevel! equ 0 (
        echo [OK] Servidor acessivel via !IP!
        echo.
        echo Para probes em OUTRAS maquinas, use:
        echo   http://!IP!:8000
        echo.
    )
)

echo.
echo ========================================
echo   RESUMO
echo ========================================
echo.
echo Probe na MESMA maquina:
echo   URL: http://localhost:8000
echo.
echo Probe em OUTRA maquina:
echo   URL: http://SEU-IP:8000
echo   (use um dos IPs mostrados acima)
echo.
echo Para testar de outra maquina:
echo   curl http://SEU-IP:8000/health
echo.
pause
