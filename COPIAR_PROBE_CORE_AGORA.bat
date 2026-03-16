@echo off
echo ========================================
echo COPIAR PROBE_CORE.PY ATUALIZADO
echo ========================================
echo.
echo Este script copia o probe_core.py corrigido para SRVSONDA001
echo.

set SOURCE="%CD%\probe\probe_core.py"
set DEST="\\SRVSONDA001\C$\Program Files\CorujaMonitor\Probe\probe_core.py"

echo Origem: %SOURCE%
echo Destino: %DEST%
echo.

if not exist %SOURCE% (
    echo ERRO: Arquivo fonte nao encontrado!
    pause
    exit /b 1
)

echo Copiando arquivo...
copy /Y %SOURCE% %DEST%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCESSO! Arquivo copiado
    echo ========================================
    echo.
    echo PROXIMO PASSO:
    echo 1. Reiniciar servico CorujaProbe na SRVSONDA001
    echo 2. Verificar logs - deve mostrar "Collected X SNMP metrics" com X ^> 0
    echo.
    echo Para reiniciar o servico, execute:
    echo   sc \\SRVSONDA001 stop CorujaProbe
    echo   timeout /t 3
    echo   sc \\SRVSONDA001 start CorujaProbe
    echo.
) else (
    echo.
    echo ERRO ao copiar arquivo!
    echo Verifique:
    echo - Acesso de rede a SRVSONDA001
    echo - Permissoes de escrita
    echo - Servico CorujaProbe parado
)

pause
