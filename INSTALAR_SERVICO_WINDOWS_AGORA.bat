@echo off
chcp 65001 >nul
cls
echo ════════════════════════════════════════════════════════════════
echo   INSTALAR PROBE COMO SERVICO DO WINDOWS
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script vai:
echo   1. Instalar NSSM (gerenciador de serviços)
echo   2. Criar serviço "CorujaProbe"
echo   3. Configurar inicio automático
echo.
echo IMPORTANTE: Execute como ADMINISTRADOR!
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 1: Baixar NSSM
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
echo   PASSO 2: Parar serviço existente (se houver)
echo ════════════════════════════════════════════════════════════════
echo.

nssm stop CorujaProbe >nul 2>&1
nssm remove CorujaProbe confirm >nul 2>&1
echo [OK] Serviço anterior removido (se existia)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 3: Criar serviço
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
echo   PASSO 4: Iniciar serviço
echo ════════════════════════════════════════════════════════════════
echo.

nssm start CorujaProbe

timeout /t 5 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 5: Verificar status
echo ════════════════════════════════════════════════════════════════
echo.

nssm status CorujaProbe

echo.
echo ════════════════════════════════════════════════════════════════
echo   INSTALACAO CONCLUIDA!
echo ════════════════════════════════════════════════════════════════
echo.
echo O serviço "CorujaProbe" foi instalado e iniciado.
echo.
echo Agora a probe vai:
echo   ✓ Iniciar automaticamente com o Windows
echo   ✓ Rodar em segundo plano (sem janela)
echo   ✓ Reiniciar automaticamente se travar
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
