@echo off
chcp 65001 >nul
cls
echo ════════════════════════════════════════════════════════════════
echo   INSTALAR PROBE COMO SERVICO WINDOWS
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script vai:
echo   1. Baixar NSSM (gerenciador de serviços)
echo   2. Parar probe se estiver rodando
echo   3. Criar serviço "CorujaProbe"
echo   4. Configurar inicio automático
echo   5. Iniciar serviço
echo.
echo IMPORTANTE: Execute como ADMINISTRADOR!
echo.
pause

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    echo Clique com botão direito e "Executar como administrador"
    pause
    exit /b 1
)

echo [OK] Privilégios de administrador verificados
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
echo   PASSO 2: Parar probe se estiver rodando
echo ════════════════════════════════════════════════════════════════
echo.

tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if %errorLevel% equ 0 (
    echo Parando probe...
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 3 /nobreak >nul
    echo [OK] Probe parada
) else (
    echo [OK] Probe não estava rodando
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 3: Remover serviço antigo (se existir)
echo ════════════════════════════════════════════════════════════════
echo.

nssm stop CorujaProbe >nul 2>&1
nssm remove CorujaProbe confirm >nul 2>&1
echo [OK] Serviço anterior removido (se existia)

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 4: Criar serviço
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
if not exist "%PROBE_PATH%\logs" mkdir "%PROBE_PATH%\logs"
nssm set CorujaProbe AppStdout "%PROBE_PATH%\logs\service_stdout.log"
nssm set CorujaProbe AppStderr "%PROBE_PATH%\logs\service_stderr.log"

echo Configurando inicio automático...
nssm set CorujaProbe Start SERVICE_AUTO_START

echo Configurando descrição...
nssm set CorujaProbe Description "Coruja Monitor Probe - Coleta de métricas do sistema"

echo Configurando nome de exibição...
nssm set CorujaProbe DisplayName "Coruja Monitor Probe"

echo Configurando reinício automático em caso de falha...
nssm set CorujaProbe AppExit Default Restart
nssm set CorujaProbe AppRestartDelay 5000

echo.
echo [OK] Serviço criado!

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 5: Iniciar serviço
echo ════════════════════════════════════════════════════════════════
echo.

nssm start CorujaProbe

timeout /t 5 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 6: Verificar status
echo ════════════════════════════════════════════════════════════════
echo.

nssm status CorujaProbe

echo.
echo ════════════════════════════════════════════════════════════════
echo   INSTALAÇÃO CONCLUÍDA!
echo ════════════════════════════════════════════════════════════════
echo.
echo ✓ Serviço "CorujaProbe" instalado
echo ✓ Inicio automático configurado
echo ✓ Serviço iniciado
echo.
echo AGORA A PROBE VAI:
echo   ✓ Iniciar automaticamente quando o Windows ligar
echo   ✓ Rodar em segundo plano (sem janela)
echo   ✓ Reiniciar automaticamente se travar
echo.
echo COMANDOS ÚTEIS:
echo.
echo Ver status:
echo   nssm status CorujaProbe
echo.
echo Parar:
echo   nssm stop CorujaProbe
echo.
echo Iniciar:
echo   nssm start CorujaProbe
echo.
echo Reiniciar:
echo   nssm restart CorujaProbe
echo.
echo Remover serviço:
echo   nssm remove CorujaProbe confirm
echo.
echo Ver logs:
echo   type "%PROBE_PATH%\logs\probe.log"
echo   type "%PROBE_PATH%\logs\service_stdout.log"
echo   type "%PROBE_PATH%\logs\service_stderr.log"
echo.
echo TESTAR AUTO-START:
echo   Reinicie a máquina e verifique se probe inicia automaticamente
echo.
echo ════════════════════════════════════════════════════════════════
pause
