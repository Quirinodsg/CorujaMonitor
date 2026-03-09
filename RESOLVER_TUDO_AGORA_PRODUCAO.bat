@echo off
chcp 65001 >nul
cls
echo ════════════════════════════════════════════════════════════════
echo   RESOLVER TUDO - PRODUCAO
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script vai:
echo   1. Copiar disk_collector.py atualizado (filtrar CD-ROM)
echo   2. Instalar probe como serviço Windows (auto-start)
echo.
echo IMPORTANTE: Execute como ADMINISTRADOR!
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 1: Copiar disk_collector.py atualizado
echo ════════════════════════════════════════════════════════════════
echo.

set "ORIGEM=C:\Users\andre.quirino\Coruja\probe\collectors\disk_collector.py"
set "DESTINO=C:\Program Files\CorujaMonitor\Probe\collectors\disk_collector.py"

if not exist "%ORIGEM%" (
    echo [ERRO] Arquivo origem não encontrado: %ORIGEM%
    echo.
    echo Execute este script na máquina de desenvolvimento!
    pause
    exit /b 1
)

echo Copiando arquivo...
copy /Y "%ORIGEM%" "%DESTINO%"

if %errorLevel% equ 0 (
    echo [OK] Arquivo copiado com sucesso!
) else (
    echo [ERRO] Falha ao copiar arquivo
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 2: Copiar config.yaml atualizado (porta 8000)
echo ════════════════════════════════════════════════════════════════
echo.

set "ORIGEM_CONFIG=C:\Users\andre.quirino\Coruja\probe\config.yaml"
set "DESTINO_CONFIG=C:\Program Files\CorujaMonitor\Probe\config.yaml"

if exist "%ORIGEM_CONFIG%" (
    echo Copiando config.yaml...
    copy /Y "%ORIGEM_CONFIG%" "%DESTINO_CONFIG%"
    
    if %errorLevel% equ 0 (
        echo [OK] Config.yaml copiado (porta 8000)
    ) else (
        echo [AVISO] Falha ao copiar config.yaml
    )
) else (
    echo [AVISO] config.yaml não encontrado, mantendo existente
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 3: Parar probe (se estiver rodando)
echo ════════════════════════════════════════════════════════════════
echo.

echo Procurando processo da probe...
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul

if %errorLevel% equ 0 (
    echo Parando probe...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *probe*" >nul 2>&1
    timeout /t 3 /nobreak >nul
    echo [OK] Probe parada
) else (
    echo [OK] Probe não estava rodando
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 4: Baixar NSSM
echo ════════════════════════════════════════════════════════════════
echo.

cd "C:\Program Files\CorujaMonitor\Probe"

if not exist "nssm.exe" (
    echo Baixando NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.' -Force"
    copy "nssm-2.24\win64\nssm.exe" "nssm.exe"
    del nssm.zip
    rmdir /s /q nssm-2.24
    echo [OK] NSSM baixado
) else (
    echo [OK] NSSM já existe
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 5: Remover serviço antigo (se existir)
echo ════════════════════════════════════════════════════════════════
echo.

nssm stop CorujaProbe >nul 2>&1
nssm remove CorujaProbe confirm >nul 2>&1
echo [OK] Serviço anterior removido (se existia)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 6: Criar serviço
echo ════════════════════════════════════════════════════════════════
echo.

set PYTHON_PATH=python
set PROBE_PATH=C:\Program Files\CorujaMonitor\Probe
set SCRIPT_PATH=%PROBE_PATH%\probe_core.py

echo Criando serviço...
nssm install CorujaProbe "%PYTHON_PATH%" "%SCRIPT_PATH%"

echo Configurando diretório de trabalho...
nssm set CorujaProbe AppDirectory "%PROBE_PATH%"

echo Configurando saída de logs...
nssm set CorujaProbe AppStdout "%PROBE_PATH%\logs\service_stdout.log"
nssm set CorujaProbe AppStderr "%PROBE_PATH%\logs\service_stderr.log"

echo Configurando inicio automático...
nssm set CorujaProbe Start SERVICE_AUTO_START

echo Configurando descrição...
nssm set CorujaProbe Description "Coruja Monitor Probe - Coleta de métricas"

echo Configurando nome de exibição...
nssm set CorujaProbe DisplayName "Coruja Monitor Probe"

echo.
echo [OK] Serviço criado!

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 7: Iniciar serviço
echo ════════════════════════════════════════════════════════════════
echo.

nssm start CorujaProbe

timeout /t 5 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 8: Verificar status
echo ════════════════════════════════════════════════════════════════
echo.

nssm status CorujaProbe

echo.
echo ════════════════════════════════════════════════════════════════
echo   TUDO RESOLVIDO!
echo ════════════════════════════════════════════════════════════════
echo.
echo ✓ disk_collector.py atualizado (CD-ROM filtrado)
echo ✓ config.yaml atualizado (porta 8000)
echo ✓ Serviço Windows instalado (auto-start)
echo.
echo AGORA:
echo   1. Aguarde 60 segundos
echo   2. Recarregue dashboard (Ctrl+F5)
echo   3. DISCO D não deve aparecer mais
echo   4. Reinicie a máquina para testar auto-start
echo.
echo COMANDOS ÚTEIS:
echo   - Ver status:    nssm status CorujaProbe
echo   - Parar:         nssm stop CorujaProbe
echo   - Iniciar:       nssm start CorujaProbe
echo   - Reiniciar:     nssm restart CorujaProbe
echo   - Remover:       nssm remove CorujaProbe confirm
echo.
echo LOGS:
echo   %PROBE_PATH%\logs\service_stdout.log
echo   %PROBE_PATH%\logs\service_stderr.log
echo   %PROBE_PATH%\probe.log
echo.
echo ════════════════════════════════════════════════════════════════
pause
