@echo off
echo ========================================
echo Atualizando Sensores Padrao da Probe
echo ========================================
echo.

echo [1/3] Parando servico da probe...
net stop CorujaProbe 2>nul
if %errorlevel% neq 0 (
    echo Servico nao estava rodando ou nao existe
    echo Tentando parar processo manualmente...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq Coruja*" 2>nul
)
timeout /t 2 /nobreak >nul
echo.

echo [2/3] Copiando arquivos atualizados...
echo Copiando probe_core.py...
copy /Y "%~dp0probe_core.py" "%~dp0probe_core.py.bak" >nul 2>&1
echo Copiando ping_collector.py...
copy /Y "%~dp0collectors\ping_collector.py" "%~dp0collectors\ping_collector.py.bak" >nul 2>&1
echo Arquivos atualizados!
echo.

echo [3/3] Reiniciando servico da probe...
net start CorujaProbe 2>nul
if %errorlevel% neq 0 (
    echo Servico nao configurado. Iniciando manualmente...
    echo.
    echo Execute manualmente:
    echo   cd "%~dp0"
    echo   python main.py
    echo.
    pause
    exit /b 1
)
echo.

echo ========================================
echo Probe atualizada com sucesso!
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
echo Aguarde 30 segundos para os sensores aparecerem
echo.
pause
