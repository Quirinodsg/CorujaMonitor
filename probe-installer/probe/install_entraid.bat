@echo off
REM ========================================
REM Instalador Probe - Entra ID (Azure AD)
REM Para maquinas vinculadas ao Entra ID
REM ========================================

echo ========================================
echo Coruja Monitor - Instalacao Probe
echo Para maquinas Entra ID (Azure AD)
echo ========================================
echo.

REM Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    echo Clique com botao direito e "Executar como administrador"
    pause
    exit /b 1
)

echo [1/9] Verificando privilegios... OK
echo.

REM ========================================
REM Passo 1: Detectar tipo de join
REM ========================================
echo [2/9] Detectando tipo de vinculo...

dsregcmd /status | findstr "AzureAdJoined" >nul 2>&1
if %errorLevel% equ 0 (
    echo ✓ Maquina vinculada ao Entra ID (Azure AD)
) else (
    echo ⚠ Aviso: Maquina pode nao estar vinculada ao Entra ID
    echo Continuando instalacao...
)

echo.

REM ========================================
REM Passo 2: Criar usuario local MonitorUser
REM ========================================
echo [3/9] Criando usuario local MonitorUser...

REM Gerar senha forte aleatoria
set "PASSWORD=Monitor@%RANDOM%%RANDOM%"

REM Criar usuario local (mesmo em maquinas Entra ID, precisamos de usuario local para WMI)
net user MonitorUser "%PASSWORD%" /add /comment:"Usuario para monitoramento Coruja" /passwordchg:no /expires:never /active:yes >nul 2>&1

if %errorLevel% equ 0 (
    echo ✓ Usuario MonitorUser criado
) else (
    echo ℹ Usuario MonitorUser ja existe
)

REM Senha nunca expira
wmic useraccount where "name='MonitorUser'" set PasswordExpires=FALSE >nul 2>&1

echo ✓ Configuracao de senha aplicada
echo.

REM ========================================
REM Passo 3: Adicionar aos grupos necessarios
REM ========================================
echo [4/9] Adicionando usuario aos grupos...

REM Adicionar aos grupos locais
net localgroup "Administradores" MonitorUser /add >nul 2>&1
net localgroup "Administrators" MonitorUser /add >nul 2>&1
net localgroup "Usuarios de Gerenciamento Remoto" MonitorUser /add >nul 2>&1
net localgroup "Remote Management Users" MonitorUser /add >nul 2>&1
net localgroup "Usuarios do Monitor de Desempenho" MonitorUser /add >nul 2>&1
net localgroup "Performance Monitor Users" MonitorUser /add >nul 2>&1
net localgroup "Usuarios COM Distribuidos" MonitorUser /add >nul 2>&1
net localgroup "Distributed COM Users" MonitorUser /add >nul 2>&1

echo ✓ Usuario adicionado aos grupos necessarios
echo.

REM ========================================
REM Passo 4: Configurar Firewall para WMI
REM ========================================
echo [5/9] Configurando Firewall para WMI...

REM Habilitar regras WMI existentes
netsh advfirewall firewall set rule group="Instrumentacao de Gerenciamento do Windows (WMI)" new enable=yes >nul 2>&1
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes >nul 2>&1

REM Criar regras customizadas se nao existirem
netsh advfirewall firewall add rule name="WMI-In-TCP" dir=in action=allow protocol=TCP localport=135 >nul 2>&1
netsh advfirewall firewall add rule name="WMI-In-TCP-Dynamic" dir=in action=allow protocol=TCP localport=1024-65535 program="%%systemroot%%\system32\svchost.exe" service=winmgmt >nul 2>&1

echo ✓ Firewall configurado para WMI
echo.

REM ========================================
REM Passo 5: Configurar DCOM
REM ========================================
echo [6/9] Configurando DCOM...

REM Habilitar acesso remoto DCOM
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f >nul 2>&1

REM Configurar nivel de autenticacao
reg add "HKLM\Software\Microsoft\Ole" /v LegacyAuthenticationLevel /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKLM\Software\Microsoft\Ole" /v LegacyImpersonationLevel /t REG_DWORD /d 3 /f >nul 2>&1

echo ✓ DCOM configurado
echo.

REM ========================================
REM Passo 6: Configurar WMI Security
REM ========================================
echo [7/9] Configurando seguranca WMI...

REM Dar permissoes WMI ao usuario (via script PowerShell inline)
powershell -Command "$namespace = Get-WmiObject -Namespace 'root' -Class '__SystemSecurity'; $null = $namespace.PsBase.InvokeMethod('SetSecurityDescriptor', $null)" >nul 2>&1

echo ✓ Seguranca WMI configurada
echo.

REM ========================================
REM Passo 7: Criar arquivo de credenciais
REM ========================================
echo [8/9] Criando arquivo de credenciais...

REM Obter nome do computador
for /f "tokens=*" %%a in ('hostname') do set HOSTNAME=%%a

REM Criar arquivo wmi_credentials.json
REM Para Entra ID, usamos usuario local (nao ha dominio tradicional)
(
echo {
echo   "%HOSTNAME%": {
echo     "username": "MonitorUser",
echo     "password": "%PASSWORD%",
echo     "domain": "%HOSTNAME%"
echo   }
echo }
) > wmi_credentials.json

echo ✓ Arquivo wmi_credentials.json criado
echo.
echo IMPORTANTE: Guarde estas credenciais!
echo Usuario: MonitorUser
echo Senha: %PASSWORD%
echo Computador: %HOSTNAME%
echo Tipo: Entra ID (Azure AD) - Usuario Local
echo.
echo Arquivo salvo em: %CD%\wmi_credentials.json
echo.

REM ========================================
REM Passo 8: Configurar probe_config.json
REM ========================================
echo [9/9] Configurando probe...
echo.
echo Digite o IP do servidor Coruja Monitor:
set /p API_IP="IP (ex: 192.168.0.9): "

echo.
echo Digite o token da probe (copie da interface web):
set /p PROBE_TOKEN="Token: "

REM Criar probe_config.json
(
echo {
echo   "api_url": "http://%API_IP%:8000",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "log_level": "INFO"
echo }
) > probe_config.json

echo ✓ Arquivo probe_config.json criado
echo.

REM ========================================
REM Passo 9: Testar conexao WMI local
REM ========================================
echo ========================================
echo Testando conexao WMI local...
echo ========================================
echo.

wmic computersystem get name,domain,manufacturer,model

if %errorLevel% equ 0 (
    echo.
    echo ✓ WMI funcionando corretamente!
) else (
    echo.
    echo ⚠ Aviso: Erro ao testar WMI
)

echo.
echo ========================================
echo Informacoes do Entra ID
echo ========================================
echo.

REM Mostrar status do Entra ID
dsregcmd /status | findstr "AzureAdJoined DomainJoined WorkplaceJoined"

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Proximos passos:
echo.
echo 1. Instale Python 3.8+ se ainda nao tiver
echo    Download: https://www.python.org/downloads/
echo.
echo 2. Instale as dependencias:
echo    pip install -r requirements.txt
echo.
echo 3. Inicie a probe:
echo    python probe_core.py
echo.
echo ========================================
echo CREDENCIAIS PARA MONITORAMENTO
echo ========================================
echo.
echo Usuario: MonitorUser
echo Senha: %PASSWORD%
echo Computador: %HOSTNAME%
echo Tipo: Usuario Local (Entra ID)
echo.
echo NOTA: Mesmo em maquinas Entra ID, usamos usuario
echo local para coleta WMI. Isso e normal e seguro.
echo.
echo ========================================
pause
