@echo off
chcp 65001 >nul
cls
echo ========================================
echo   COPIAR PROBE PARA PRODUCAO
echo ========================================
echo.

echo Este script vai copiar os arquivos da probe
echo do desenvolvimento para a maquina de producao.
echo.
echo ORIGEM: C:\Users\andre.quirino\Coruja\probe
echo DESTINO: C:\Program Files\CorujaMonitor\Probe
echo.
echo ========================================
pause
echo.

echo Verificando origem...
if not exist "C:\Users\andre.quirino\Coruja\probe\probe_core.py" (
    echo [ERRO] Pasta de origem nao encontrada!
    echo.
    echo Verifique se esta na maquina de desenvolvimento.
    echo.
    pause
    exit /b 1
)
echo [OK] Pasta de origem encontrada
echo.

echo Verificando destino...
if not exist "C:\Program Files\CorujaMonitor\Probe" (
    echo [ERRO] Pasta de destino nao encontrada!
    echo.
    echo Verifique se a probe foi instalada em:
    echo C:\Program Files\CorujaMonitor\Probe
    echo.
    pause
    exit /b 1
)
echo [OK] Pasta de destino encontrada
echo.

echo ========================================
echo   COPIANDO ARQUIVOS...
echo ========================================
echo.

echo Copiando probe_core.py...
copy /Y "C:\Users\andre.quirino\Coruja\probe\probe_core.py" "C:\Program Files\CorujaMonitor\Probe\"
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao copiar probe_core.py
    echo Pode precisar de permissoes de administrador
    pause
    exit /b 1
)
echo [OK] probe_core.py copiado

echo.
echo Copiando config.py...
copy /Y "C:\Users\andre.quirino\Coruja\probe\config.py" "C:\Program Files\CorujaMonitor\Probe\"
echo [OK] config.py copiado

echo.
echo Copiando __init__.py...
if exist "C:\Users\andre.quirino\Coruja\probe\__init__.py" (
    copy /Y "C:\Users\andre.quirino\Coruja\probe\__init__.py" "C:\Program Files\CorujaMonitor\Probe\"
    echo [OK] __init__.py copiado
)

echo.
echo Copiando pasta collectors...
xcopy /E /I /Y "C:\Users\andre.quirino\Coruja\probe\collectors" "C:\Program Files\CorujaMonitor\Probe\collectors"
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao copiar pasta collectors
    pause
    exit /b 1
)
echo [OK] Pasta collectors copiada

echo.
echo ========================================
echo   COPIA CONCLUIDA!
echo ========================================
echo.

echo Arquivos copiados com sucesso!
echo.
echo Proximos passos:
echo.
echo 1. Va para a maquina de producao
echo 2. Abra: C:\Program Files\CorujaMonitor\Probe
echo 3. Execute: INICIAR_PROBE.bat
echo.
echo ========================================
pause
