@echo off
chcp 65001 >nul
cls
echo ========================================
echo   COPIAR PROBE COMPLETA PARA PRODUCAO
echo ========================================
echo.
echo ORIGEM: C:\Users\andre.quirino\Coruja\probe
echo DESTINO: C:\Program Files\CorujaMonitor\Probe
echo.
echo Este script vai copiar TODOS os arquivos necessarios:
echo   - probe_core.py
echo   - config.py
echo   - __init__.py
echo   - Pasta collectors/ (17 arquivos)
echo   - config.yaml (se existir)
echo.
pause

echo.
echo ========================================
echo   VERIFICANDO PASTAS...
echo ========================================
echo.

if not exist "C:\Users\andre.quirino\Coruja\probe\probe_core.py" (
    echo [ERRO] Pasta de origem nao encontrada!
    echo Verifique se esta na maquina de desenvolvimento.
    pause
    exit /b 1
)
echo [OK] Pasta de origem encontrada

if not exist "C:\Program Files\CorujaMonitor\Probe" (
    echo [ERRO] Pasta de destino nao encontrada!
    echo Criando pasta...
    mkdir "C:\Program Files\CorujaMonitor\Probe"
)
echo [OK] Pasta de destino pronta

echo.
echo ========================================
echo   COPIANDO ARQUIVOS PRINCIPAIS...
echo ========================================
echo.

echo [1/5] Copiando probe_core.py...
copy /Y "C:\Users\andre.quirino\Coruja\probe\probe_core.py" "C:\Program Files\CorujaMonitor\Probe\" >nul
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao copiar probe_core.py
    echo Execute este script como ADMINISTRADOR
    pause
    exit /b 1
)
echo       [OK] probe_core.py

echo [2/5] Copiando config.py...
copy /Y "C:\Users\andre.quirino\Coruja\probe\config.py" "C:\Program Files\CorujaMonitor\Probe\" >nul
echo       [OK] config.py

echo [3/5] Copiando __init__.py...
if exist "C:\Users\andre.quirino\Coruja\probe\__init__.py" (
    copy /Y "C:\Users\andre.quirino\Coruja\probe\__init__.py" "C:\Program Files\CorujaMonitor\Probe\" >nul
    echo       [OK] __init__.py
) else (
    echo       [AVISO] __init__.py nao encontrado (opcional)
)

echo [4/5] Copiando config.yaml...
if exist "C:\Users\andre.quirino\Coruja\config_producao_pronto.yaml" (
    copy /Y "C:\Users\andre.quirino\Coruja\config_producao_pronto.yaml" "C:\Program Files\CorujaMonitor\Probe\config.yaml" >nul
    echo       [OK] config.yaml (configuracao de producao)
) else if exist "C:\Users\andre.quirino\Coruja\probe\config.yaml" (
    copy /Y "C:\Users\andre.quirino\Coruja\probe\config.yaml" "C:\Program Files\CorujaMonitor\Probe\" >nul
    echo       [OK] config.yaml
) else (
    echo       [AVISO] config.yaml nao encontrado (sera criado automaticamente)
)

echo [5/5] Copiando pasta collectors...
if not exist "C:\Program Files\CorujaMonitor\Probe\collectors" (
    mkdir "C:\Program Files\CorujaMonitor\Probe\collectors"
)
xcopy /E /I /Y /Q "C:\Users\andre.quirino\Coruja\probe\collectors" "C:\Program Files\CorujaMonitor\Probe\collectors" >nul
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao copiar pasta collectors
    pause
    exit /b 1
)
echo       [OK] collectors/ (17 arquivos)

echo.
echo ========================================
echo   VERIFICANDO ARQUIVOS COPIADOS...
echo ========================================
echo.

cd /d "C:\Program Files\CorujaMonitor\Probe"

if exist "probe_core.py" (
    echo [OK] probe_core.py
) else (
    echo [ERRO] probe_core.py NAO ENCONTRADO!
)

if exist "config.py" (
    echo [OK] config.py
) else (
    echo [ERRO] config.py NAO ENCONTRADO!
)

if exist "collectors\__init__.py" (
    echo [OK] collectors\__init__.py
) else (
    echo [ERRO] collectors\__init__.py NAO ENCONTRADO!
)

if exist "collectors\cpu_collector.py" (
    echo [OK] collectors\cpu_collector.py
) else (
    echo [ERRO] collectors\cpu_collector.py NAO ENCONTRADO!
)

if exist "collectors\memory_collector.py" (
    echo [OK] collectors\memory_collector.py
) else (
    echo [ERRO] collectors\memory_collector.py NAO ENCONTRADO!
)

if exist "collectors\disk_collector.py" (
    echo [OK] collectors\disk_collector.py
) else (
    echo [ERRO] collectors\disk_collector.py NAO ENCONTRADO!
)

if exist "collectors\network_collector.py" (
    echo [OK] collectors\network_collector.py
) else (
    echo [ERRO] collectors\network_collector.py NAO ENCONTRADO!
)

if exist "collectors\system_collector.py" (
    echo [OK] collectors\system_collector.py
) else (
    echo [ERRO] collectors\system_collector.py NAO ENCONTRADO!
)

if exist "collectors\ping_collector.py" (
    echo [OK] collectors\ping_collector.py
) else (
    echo [ERRO] collectors\ping_collector.py NAO ENCONTRADO!
)

echo.
echo ========================================
echo   COPIA CONCLUIDA!
echo ========================================
echo.
echo Todos os arquivos foram copiados para:
echo C:\Program Files\CorujaMonitor\Probe
echo.
echo PROXIMOS PASSOS:
echo.
echo 1. Edite o arquivo config.yaml com:
echo    - Token correto: V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY
echo    - Nome da probe: SRVSONDA001
echo    - IP do servidor: 192.168.31.161
echo    - Porta: 3000
echo.
echo 2. Execute: INICIAR_PROBE.bat
echo.
echo ========================================
pause
