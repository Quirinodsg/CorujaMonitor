@echo off
REM ========================================
REM Instalador Simples - Coruja Monitor
REM Versao minima sem menu
REM ========================================

title Instalador Coruja Monitor

echo.
echo ========================================
echo   INSTALADOR CORUJA MONITOR
echo ========================================
echo.
echo Este instalador vai configurar a probe
echo para monitoramento agentless.
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM ========================================
REM Verificar Admin
REM ========================================
cls
echo.
echo [1/10] Verificando privilegios...
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo.
    echo [ERRO] Execute como Administrador!
    echo.
    echo Como fazer:
    echo 1. Clique com botao direito neste arquivo
    echo 2. Escolha "Executar como administrador"
    echo.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit
)
echo [OK] Privilegios verificados
timeout /t 2 >nul

REM ========================================
REM Criar Usuario
REM ========================================
cls
echo.
echo [2/10] Criando usuario MonitorUser...
set "PASSWORD=Monitor@%RANDOM%%RANDOM%"
net user MonitorUser "%PASSWORD%" /add /comment:"Usuario para monitoramento Coruja" /passwordchg:no /expires:never /active:yes >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Usuario criado
) else (
    echo [INFO] Usuario ja existe
)
wmic useraccount where "name='MonitorUser'" set PasswordExpires=FALSE >nul 2>&1
timeout /t 2 >nul

REM ========================================
REM Adicionar Grupos
REM ========================================
cls
echo.
echo [3/10] Configurando grupos...
net localgroup "Administradores" MonitorUser /add >nul 2>&1
net localgroup "Administrators" MonitorUser /add >nul 2>&1
net localgroup "Usuarios de Gerenciamento Remoto" MonitorUser /add >nul 2>&1
net localgroup "Remote Management Users" MonitorUser /add >nul 2>&1
net localgroup "Usuarios do Monitor de Desempenho" MonitorUser /add >nul 2>&1
net localgroup "Performance Monitor Users" MonitorUser /add >nul 2>&1
net localgroup "Usuarios COM Distribuidos" MonitorUser /add >nul 2>&1
net localgroup "Distributed COM Users" MonitorUser /add >nul 2>&1
echo [OK] Grupos configurados
timeout /t 2 >nul

REM ========================================
REM Firewall
REM ========================================
cls
echo.
echo [4/10] Configurando Firewall...
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
echo [5/10] Configurando DCOM...
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
echo [6/10] Configurando WMI...
powershell -Command "$namespace = Get-WmiObject -Namespace 'root' -Class '__SystemSecurity'; $null = $namespace.PsBase.InvokeMethod('SetSecurityDescriptor', $null)" >nul 2>&1
echo [OK] WMI configurado
timeout /t 2 >nul

REM ========================================
REM Credenciais
REM ========================================
cls
echo.
echo [7/10] Criando arquivo de credenciais...
for /f "tokens=*" %%a in ('hostname') do set HOSTNAME=%%a
(
echo {
echo   "%HOSTNAME%": {
echo     "username": "MonitorUser",
echo     "password": "%PASSWORD%",
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
echo [8/10] Configurando probe...
echo.
echo Digite o IP do servidor Coruja Monitor
echo (exemplo: 192.168.0.9)
echo.
set /p API_IP="IP do servidor: "

cls
echo.
echo [8/10] Configurando probe...
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
REM Testar WMI
REM ========================================
cls
echo.
echo [9/10] Testando WMI...
wmic computersystem get name,domain,manufacturer,model >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] WMI funcionando corretamente
) else (
    color 0E
    echo [AVISO] Erro ao testar WMI
)
timeout /t 2 >nul

REM ========================================
REM Concluido
REM ========================================
cls
color 0A
echo.
echo ========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Credenciais criadas:
echo   Usuario: MonitorUser
echo   Senha: %PASSWORD%
echo   Computador: %HOSTNAME%
echo.
echo IMPORTANTE: Anote estas credenciais!
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Instale Python 3.8 ou superior
echo    Download: https://www.python.org/downloads/
echo    IMPORTANTE: Marque "Add Python to PATH"
echo.
echo 2. Instale as dependencias:
echo    pip install -r requirements.txt
echo.
echo 3. Inicie a probe:
echo    python probe_core.py
echo.
echo 4. Deixe a janela da probe aberta!
echo.
echo 5. Verifique no dashboard (aguarde 2-3 minutos):
echo    http://%API_IP%:3000
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit
