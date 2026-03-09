@echo off
chcp 65001 >nul
cls
echo ════════════════════════════════════════════════════════════════
echo   COPIAR CONFIG.YAML CORRETO (PORTA 8000)
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script copia o config.yaml com a porta correta (8000)
echo.
pause

set "ORIGEM=C:\Users\andre.quirino\Coruja\probe\config.yaml"
set "DESTINO=C:\Program Files\CorujaMonitor\Probe\config.yaml"

if not exist "%ORIGEM%" (
    echo [ERRO] Arquivo origem não encontrado: %ORIGEM%
    pause
    exit /b 1
)

echo Copiando config.yaml...
copy /Y "%ORIGEM%" "%DESTINO%"

if %errorLevel% equ 0 (
    echo [OK] Config.yaml copiado com sucesso!
    echo.
    echo Porta configurada: 8000 (API)
    echo.
    echo Se a probe estiver rodando, reinicie-a para aplicar mudanças.
) else (
    echo [ERRO] Falha ao copiar arquivo
)

echo.
pause
