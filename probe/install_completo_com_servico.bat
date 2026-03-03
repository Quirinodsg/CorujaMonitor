@echo off
REM ========================================
REM Instalador Completo com Servico Windows
REM Instala, configura E inicia probe automaticamente
REM ========================================

title Instalador Completo Coruja Monitor

echo.
echo ========================================
echo   INSTALADOR COMPLETO CORUJA MONITOR
echo   (COM SERVICO WINDOWS)
echo ========================================
echo.
echo Este instalador vai:
echo - Detectar seu usuario atual
echo - Configurar Firewall, DCOM e WMI
echo - Criar arquivos de configuracao
echo - Instalar Python (se necessario)
echo - Instalar dependencias
echo - Criar servico Windows
echo - INICIAR PROBE AUTOMATICAMENTE
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM ========================================
REM Verificar Admin
REM ========================================
cls
echo.
echo [1/12] Verificando privilegios...
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo.
    echo [ERRO] Execute como Administrador!
    echo.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit
)
echo [OK] Privilegios verificados
timeout /t 2 >nul

REM ========================================
REM Detectar Usuario Atual
REM ========================================
cls
echo.
echo [2/12] Detectando informacoes do sistema...
set DETECTED_USER=%USERNAME%
for /f "tokens=*" %%a in ('hostname') do set DETECTED_HOSTNAME=%%a
echo [OK] Usuario detectado: %DETECTED_USER%
echo [OK] Computador: %DETECTED_HOSTNAME%
timeout /t 2 >nul

REM ========================================
REM Solicitar Credenciais
REM ========================================
cls
echo.
echo [3/12] Configurando credenciais WMI...
echo.
echo ========================================
echo   CREDENCIAIS PARA MONITORAMENTO WMI
echo ========================================
echo.
echo Usuario detectado: %DETECTED_USER%
echo Computador: %DETECTED_HOSTNAME%
echo.
echo Voce pode:
echo 1. Pressionar ENTER para usar o usuario detectado
echo 2. Digitar um usuario diferente
echo.
set /p CUSTOM_USER="Usuario (ENTER para usar '%DETECTED_USER%'): "

if "%CUSTOM_USER%"=="" (
    set CURRENT_USER=%DETECTED_USER%
    echo [OK] Usando usuario detectado: %CURRENT_USER%
) else (
    set CURRENT_USER=%CUSTOM_USER%
    echo [OK] Usando usuario customizado: %CURRENT_USER%
)

echo.
set /p USER_PASSWORD="Senha do usuario %CURRENT_USER%: "

echo.
echo Dominio/Workgroup:
echo - Para maquina local: pressione ENTER ou digite o nome do computador
echo - Para dominio: digite o nome do dominio (ex: EMPRESA)
echo.
set /p CUSTOM_DOMAIN="Dominio (ENTER para '%DETECTED_HOSTNAME%'): "

if "%CUSTOM_DOMAIN%"=="" (
    set HOSTNAME=%DETECTED_HOSTNAME%
    echo [OK] Usando computador local: %HOSTNAME%
) else (
    set HOSTNAME=%CUSTOM_DOMAIN%
    echo [OK] Usando dominio: %HOSTNAME%
)

echo.
echo ========================================
echo   RESUMO DAS CREDENCIAIS
echo ========================================
echo Usuario: %CURRENT_USER%
echo Dominio: %HOSTNAME%
echo Senha: ********
echo ========================================
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM ========================================
REM Firewall
REM ========================================
cls
echo.
echo [4/12] Configurando Firewall...
netsh advfirewall firewall set rule group="Instrumentacao de Gerenciamento do Windows (WMI)" new enable=yes >nul 2>&1
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1
netsh advfirewall firewall add rule name="WMI-In-TCP" dir=in action=allow protocol=TCP localport=135 >nul 2>&1
netsh advfirewall firewall add rule name="WMI-In-TCP-Dynamic" dir=in action=allow protocol=TCP localport=1024-65535 program="%%systemroot%%\system32\svchost.exe" service=winmgmt >nul 2>&1
echo [OK] Firewall configurado
timeout /t 2 >nul

REM ========================================
REM DCOM
REM ========================================
cls
echo.
echo [5/12] Configurando DCOM...
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Ole" /v LegacyAuthenticationLevel /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Ole" /v LegacyImpersonationLevel /t REG_DWORD /d 3 /f >nul 2>&1
echo [OK] DCOM configurado
timeout /t 2 >nul

REM ========================================
REM WMI
REM ========================================
cls
echo.
echo [6/12] Configurando WMI...
powershell -Command "$namespace = Get-WmiObject -Namespace 'root' -Class '__SystemSecurity'; $null = $namespace.PsBase.InvokeMethod('SetSecurityDescriptor', $null)" >nul 2>&1
echo [OK] WMI configurado
timeout /t 2 >nul

REM ========================================
REM Credenciais
REM ========================================
cls
echo.
echo [7/12] Criando arquivo de credenciais...
(
echo {
echo   "%HOSTNAME%": {
echo     "username": "%CURRENT_USER%",
echo     "password": "%USER_PASSWORD%",
echo     "domain": "%HOSTNAME%"
echo   }
echo }
) > wmi_credentials.json
echo [OK] Arquivo wmi_credentials.json criado
timeout /t 2 >nul

REM ========================================
REM Configurar Probe
REM ========================================
cls
echo.
echo [8/12] Configurando probe...
echo.
echo Digite o IP do servidor Coruja Monitor
echo (exemplo: 192.168.0.9)
echo.
set /p API_IP="IP do servidor: "

cls
echo.
echo [8/12] Configurando probe...
echo.
echo Digite o token da probe
echo (copie da interface web: Empresas - Nova Probe)
echo.
set /p PROBE_TOKEN="Token: "

(
echo {
echo   "api_url": "http://%API_IP%:8000",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "log_level": "INFO"
echo }
) > probe_config.json
echo.
echo [OK] Arquivo probe_config.json criado
timeout /t 2 >nul

REM ========================================
REM Verificar Python
REM ========================================
cls
echo.
echo [9/12] Verificando Python...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python instalado
) else (
    echo [AVISO] Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.8+ de:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marque "Add Python to PATH"
    echo.
    echo Apos instalar Python, execute este instalador novamente.
    echo.
    pause
    exit /b 1
)
timeout /t 2 >nul

REM ========================================
REM Instalar Dependencias
REM ========================================
cls
echo.
echo [10/12] Instalando dependencias Python...
echo.
echo Isso pode levar alguns minutos...
echo.
pip install -r requirements.txt
if %errorLevel% equ 0 (
    echo.
    echo [OK] Dependencias instaladas
) else (
    echo.
    echo [AVISO] Erro ao instalar dependencias
    echo Verifique se Python e pip estao instalados corretamente
)
timeout /t 3 >nul

REM ========================================
REM Criar Servico Windows
REM ========================================
cls
echo.
echo [11/12] Criando servico Windows...
echo.

REM Obter caminho completo do Python
for /f "delims=" %%i in ('where python') do set PYTHON_PATH=%%i
set PROBE_PATH=%CD%\probe_core.py

echo Python encontrado em: %PYTHON_PATH%
echo Probe localizada em: %PROBE_PATH%
echo.

REM Remover tarefa antiga se existir
schtasks /delete /tn "CorujaProbe" /f >nul 2>&1

echo Criando tarefa agendada para iniciar com Windows...
schtasks /create /tn "CorujaProbe" /tr "\"%PYTHON_PATH%\" \"%PROBE_PATH%\"" /sc onstart /ru SYSTEM /rl HIGHEST /f

if %errorLevel% equ 0 (
    echo.
    echo [OK] Servico criado com sucesso!
    echo.
    echo A probe vai iniciar automaticamente quando o Windows iniciar!
    echo.
    echo Para verificar: schtasks /query /tn "CorujaProbe"
) else (
    echo.
    echo [AVISO] Erro ao criar servico
    echo Voce precisara iniciar a probe manualmente
)
timeout /t 3 >nul

REM ========================================
REM Iniciar Probe Agora
REM ========================================
cls
echo.
echo [12/12] Iniciando probe...
echo.

echo Iniciando probe em segundo plano...
start "Coruja Probe" /MIN python probe_core.py

echo.
echo Aguardando probe inicializar...
timeout /t 5 >nul

REM Verificar se probe esta rodando
tasklist | findstr python >nul 2>&1
if %errorLevel% equ 0 (
    echo.
    echo [OK] Probe iniciada com sucesso!
    echo.
    echo A probe esta rodando em segundo plano.
    echo Para ver a janela, procure "Coruja Probe" na barra de tarefas.
) else (
    echo.
    echo [AVISO] Probe pode nao ter iniciado corretamente.
    echo Verifique o arquivo probe.log para detalhes.
)

REM ========================================
REM Concluido
REM ========================================
timeout /t 3 >nul
cls
color 0A
echo.
echo ========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Configuracao criada:
echo   Usuario: %CURRENT_USER%
echo   Dominio: %HOSTNAME%
echo   API: http://%API_IP%:8000
echo.
echo ========================================
echo   PROBE INICIADA AUTOMATICAMENTE!
echo ========================================
echo.
echo A probe esta rodando em segundo plano e vai:
echo   - Coletar metricas a cada 60 segundos
echo   - Enviar para o servidor Coruja
echo   - Iniciar automaticamente com o Windows
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Aguarde 2-3 minutos
echo.
echo 2. Acesse o dashboard:
echo    http://%API_IP%:3000
echo.
echo 3. Va em "Servidores"
echo.
echo 4. Seu servidor deve aparecer automaticamente!
echo.
echo 5. Os sensores vao aparecer com status real
echo.
echo ========================================
echo   GERENCIAR PROBE
echo ========================================
echo.
echo Para ver a janela da probe:
echo   Procure "Coruja Probe" na barra de tarefas
echo.
echo Para parar a probe:
echo   Feche a janela "Coruja Probe"
echo.
echo Para desabilitar inicio automatico:
echo   schtasks /delete /tn "CorujaProbe" /f
echo.
echo Para verificar instalacao:
echo   verificar_instalacao.bat
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit
