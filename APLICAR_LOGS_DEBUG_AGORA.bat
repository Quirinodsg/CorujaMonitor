@echo off
echo ========================================
echo APLICAR LOGS DEBUG - SNMP
echo ========================================
echo.
echo Este script:
echo 1. Copia probe_core.py com logs de debug
echo 2. Reinicia probe
echo 3. Mostra logs em tempo real
echo.

REM Passo 1: Copiar arquivo
echo [1/3] Copiando probe_core.py...
copy /Y "%CD%\probe\probe_core.py" "\\SRVSONDA001\C$\Program Files\CorujaMonitor\Probe\probe_core.py"

if %ERRORLEVEL% NEQ 0 (
    echo ERRO ao copiar arquivo!
    pause
    exit /b 1
)

echo OK - Arquivo copiado
echo.

REM Passo 2: Reiniciar probe
echo [2/3] Reiniciando probe...
sc \\SRVSONDA001 stop CorujaProbe
timeout /t 5 /nobreak
sc \\SRVSONDA001 start CorujaProbe

echo OK - Probe reiniciada
echo.

REM Passo 3: Aguardar e mostrar logs
echo [3/3] Aguardando 60 segundos para coleta...
timeout /t 60 /nobreak

echo.
echo ========================================
echo LOGS DA PROBE
echo ========================================
echo.
echo Conecte na SRVSONDA001 e execute:
echo   cd "C:\Program Files\CorujaMonitor\Probe"
echo   type probe.log | findstr /C:"SNMP" /C:"Parsing" /C:"Collected"
echo.
echo PROCURE POR:
echo - "Parsing SNMP data: X OIDs received" (deve ser ^> 0)
echo - "Sample OIDs: [...]" (deve mostrar OIDs)
echo - "Total metrics parsed: X" (deve ser ^> 0)
echo - "Collected X SNMP metrics" (deve ser ^> 0)
echo.

pause
