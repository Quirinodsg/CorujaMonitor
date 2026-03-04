@echo off
echo ========================================
echo Atualizar Probe Instalada
echo ========================================
echo.

set "SOURCE=%~dp0probe"
set "DEST=C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\Coruja Monitor\probe"

echo Origem: %SOURCE%
echo Destino: %DEST%
echo.

if not exist "%DEST%" (
    echo ERRO: Pasta da probe instalada nao encontrada!
    pause
    exit /b 1
)

echo [1/4] Parando servico...
net stop CorujaProbe
timeout /t 2 /nobreak >nul
echo.

echo [2/4] Fazendo backup...
if exist "%DEST%\probe_core.py" (
    copy /Y "%DEST%\probe_core.py" "%DEST%\probe_core.py.backup" >nul
    echo Backup: probe_core.py.backup
)
if exist "%DEST%\collectors\ping_collector.py" (
    copy /Y "%DEST%\collectors\ping_collector.py" "%DEST%\collectors\ping_collector.py.backup" >nul
    echo Backup: ping_collector.py.backup
)
echo.

echo [3/4] Copiando arquivos atualizados...
copy /Y "%SOURCE%\probe_core.py" "%DEST%\probe_core.py"
if %errorlevel% neq 0 (
    echo ERRO ao copiar probe_core.py
    pause
    exit /b 1
)
echo Copiado: probe_core.py

if not exist "%DEST%\collectors" mkdir "%DEST%\collectors"
copy /Y "%SOURCE%\collectors\ping_collector.py" "%DEST%\collectors\ping_collector.py"
if %errorlevel% neq 0 (
    echo ERRO ao copiar ping_collector.py
    pause
    exit /b 1
)
echo Copiado: ping_collector.py

REM Copiar outros collectors atualizados
copy /Y "%SOURCE%\collectors\cpu_collector.py" "%DEST%\collectors\cpu_collector.py" >nul 2>&1
copy /Y "%SOURCE%\collectors\memory_collector.py" "%DEST%\collectors\memory_collector.py" >nul 2>&1
copy /Y "%SOURCE%\collectors\disk_collector.py" "%DEST%\collectors\disk_collector.py" >nul 2>&1
copy /Y "%SOURCE%\collectors\network_collector.py" "%DEST%\collectors\network_collector.py" >nul 2>&1
copy /Y "%SOURCE%\collectors\system_collector.py" "%DEST%\collectors\system_collector.py" >nul 2>&1
echo Copiados: outros collectors
echo.

echo [4/4] Reiniciando servico...
net start CorujaProbe
if %errorlevel% neq 0 (
    echo ERRO ao iniciar servico!
    pause
    exit /b 1
)
echo.

echo ========================================
echo Probe Atualizada com Sucesso!
echo ========================================
echo.
echo Sensores padrao (na ordem):
echo   1. Ping (8.8.8.8)
echo   2. CPU
echo   3. Memoria
echo   4. Disco C
echo   5. Uptime
echo   6. Network IN
echo   7. Network OUT
echo.
echo Aguarde 30-60 segundos e verifique na interface web
echo.
echo Para ver os logs:
echo   cd "%DEST%"
echo   type probe.log
echo.
pause
