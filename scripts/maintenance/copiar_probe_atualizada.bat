@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Copiar Probe Atualizada
echo ========================================
echo.

REM Detectar pasta da probe instalada
set "PROBE_PATH=C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe"

echo Pasta da probe detectada: %PROBE_PATH%
echo.

if not exist "%PROBE_PATH%" (
    echo ERRO: Pasta da probe nao encontrada!
    echo.
    echo Digite o caminho completo da pasta onde a probe esta instalada:
    set /p PROBE_PATH="Caminho: "
    
    if not exist "!PROBE_PATH!" (
        echo ERRO: Caminho invalido!
        pause
        exit /b 1
    )
)

echo.
echo [1/4] Parando probe...
net stop CorujaProbe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Coruja*" 2>nul
timeout /t 2 /nobreak >nul
echo.

echo [2/4] Fazendo backup dos arquivos antigos...
if exist "%PROBE_PATH%\probe_core.py" (
    copy /Y "%PROBE_PATH%\probe_core.py" "%PROBE_PATH%\probe_core.py.backup" >nul
    echo Backup: probe_core.py.backup
)
if exist "%PROBE_PATH%\collectors\ping_collector.py" (
    copy /Y "%PROBE_PATH%\collectors\ping_collector.py" "%PROBE_PATH%\collectors\ping_collector.py.backup" >nul
    echo Backup: ping_collector.py.backup
)
echo.

echo [3/4] Copiando arquivos atualizados...
copy /Y "%~dp0probe\probe_core.py" "%PROBE_PATH%\probe_core.py"
if %errorlevel% neq 0 (
    echo ERRO ao copiar probe_core.py
    pause
    exit /b 1
)
echo Copiado: probe_core.py

if not exist "%PROBE_PATH%\collectors" mkdir "%PROBE_PATH%\collectors"
copy /Y "%~dp0probe\collectors\ping_collector.py" "%PROBE_PATH%\collectors\ping_collector.py"
if %errorlevel% neq 0 (
    echo ERRO ao copiar ping_collector.py
    pause
    exit /b 1
)
echo Copiado: collectors\ping_collector.py
echo.

echo [4/4] Reiniciando probe...
net start CorujaProbe 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Servico nao configurado. Inicie manualmente:
    echo.
    echo   cd "%PROBE_PATH%"
    echo   python main.py
    echo.
) else (
    echo Probe reiniciada com sucesso!
)
echo.

echo ========================================
echo Atualizacao Concluida!
echo ========================================
echo.
echo Ordem dos sensores padrao:
echo   1. Ping (8.8.8.8)
echo   2. CPU
echo   3. Memoria  
echo   4. Disco C
echo   5. Uptime
echo   6. Network IN
echo   7. Network OUT
echo.
echo Aguarde 30 segundos e verifique na interface web
echo.
pause
