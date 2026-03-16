@echo off
echo ========================================
echo TESTAR PROBE_CORE.PY LOCALMENTE
echo ========================================
echo.
echo Este script testa se o probe_core.py nao tem erros de sintaxe
echo.

cd /d "%CD%\probe"

echo Verificando sintaxe Python...
python -m py_compile probe_core.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCESSO! Arquivo sem erros de sintaxe
    echo ========================================
    echo.
    echo Proximo passo: Copiar para SRVSONDA001
    echo Execute: COPIAR_PROBE_CORE_AGORA.bat
    echo.
) else (
    echo.
    echo ERRO! Arquivo tem erros de sintaxe
    echo Corrija os erros antes de copiar
    echo.
)

pause
