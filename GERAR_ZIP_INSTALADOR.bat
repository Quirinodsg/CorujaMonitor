@echo off
REM ========================================
REM GERAR ZIP DO INSTALADOR
REM ========================================

echo.
echo ========================================
echo   GERAR ZIP DO INSTALADOR
echo ========================================
echo.

cd /d "C:\Users\andre.quirino\Coruja Monitor"

echo [1/2] Verificando pasta probe-installer...
if not exist "probe-installer\probe" (
    echo [ERRO] Pasta probe-installer\probe nao encontrada!
    echo Execute primeiro: CRIAR_PACOTE_COMPLETO.bat
    pause
    exit /b 1
)

echo [2/2] Criando arquivo ZIP...
powershell -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'probe-installer\*' -DestinationPath 'CorujaMonitorProbe-Instalador-v1.0.0.zip' -Force"

if exist "CorujaMonitorProbe-Instalador-v1.0.0.zip" (
    echo.
    echo ========================================
    echo   ZIP CRIADO COM SUCESSO!
    echo ========================================
    echo.
    echo Arquivo: CorujaMonitorProbe-Instalador-v1.0.0.zip
    echo.
    
    REM Mostrar tamanho
    for %%A in ("CorujaMonitorProbe-Instalador-v1.0.0.zip") do (
        set SIZE=%%~zA
    )
    echo Tamanho: %SIZE% bytes
    echo.
    echo DISTRIBUIR:
    echo   1. Envie este ZIP para os clientes
    echo   2. Cliente descompacta
    echo   3. Cliente executa INSTALAR_TUDO.bat
    echo.
    
    REM Abrir pasta
    explorer /select,"CorujaMonitorProbe-Instalador-v1.0.0.zip"
) else (
    echo.
    echo [ERRO] Falha ao criar ZIP!
    echo.
)

pause
