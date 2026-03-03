@echo off
REM ========================================
REM Instalador SEM Criacao de Usuario
REM Configure a probe primeiro, usuario depois
REM ========================================

title Instalador Coruja Monitor (Sem Usuario)

echo.
echo ========================================
echo   INSTALADOR CORUJA MONITOR
echo   (SEM CRIACAO DE USUARIO)
echo ========================================
echo.
echo Este instalador vai:
echo - Configurar Firewall, DCOM e WMI
echo - Criar arquivos de configuracao da probe
echo - PULAR a criacao de usuario (faz depois)
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM ========================================
REM Verificar Admin
REM ========================================
cls
echo.
echo [1/7] Verificando privilegios...
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
REM Firewall
REM ========================================
cls
echo.
echo [2/7] Configurando Firewall...
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
echo [3/7] Configurando DCOM...
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
echo [4/7] Configurando WMI...
powershell -Command "$namespace = Get-WmiObject -Namespace 'root' -Class '__SystemSecurity'; $null = $namespace.PsBase.InvokeMethod('SetSecurityDescriptor', $null)" >nul 2>&1
echo [OK] WMI configurado
timeout /t 2 >nul

REM ========================================
REM Configurar Probe
REM ========================================
cls
echo.
echo [5/7] Configurando probe...
echo.
echo Digite o IP do servidor Coruja Monitor
echo (exemplo: 192.168.0.9)
echo.
set /p API_IP="IP do servidor: "

cls
echo.
echo [5/7] Configurando probe...
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
REM Criar Template de Credenciais
REM ========================================
cls
echo.
echo [6/7] Criando template de credenciais...
for /f "tokens=*" %%a in ('hostname') do set HOSTNAME=%%a
(
echo {
echo   "%HOSTNAME%": {
echo     "username": "SEU_USUARIO_AQUI",
echo     "password": "SUA_SENHA_AQUI",
echo     "domain": "%HOSTNAME%"
echo   }
echo }
) > wmi_credentials.json
echo [OK] Template criado: wmi_credentials.json
echo.
echo IMPORTANTE: Edite este arquivo depois!
timeout /t 2 >nul

REM ========================================
REM Testar WMI
REM ========================================
cls
echo.
echo [7/7] Testando WMI...
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
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Configuracoes criadas:
echo   - probe_config.json (pronto para usar)
echo   - wmi_credentials.json (precisa editar)
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. CRIAR USUARIO (escolha uma opcao):
echo.
echo    Opcao A - Usuario Local Simples:
echo      net user MonitorUser SuaSenha@123 /add
echo      net localgroup Administrators MonitorUser /add
echo.
echo    Opcao B - Usar Usuario Existente:
echo      Use um usuario que ja existe
echo.
echo 2. EDITAR wmi_credentials.json:
echo    Abra o arquivo e substitua:
echo      "username": "SEU_USUARIO_AQUI"  ^<-- Coloque o usuario
echo      "password": "SUA_SENHA_AQUI"    ^<-- Coloque a senha
echo.
echo 3. INSTALAR PYTHON:
echo    Download: https://www.python.org/downloads/
echo    IMPORTANTE: Marque "Add Python to PATH"
echo.
echo 4. INSTALAR DEPENDENCIAS:
echo    pip install -r requirements.txt
echo.
echo 5. INICIAR PROBE:
echo    python probe_core.py
echo.
echo 6. VERIFICAR NO DASHBOARD (aguarde 2-3 minutos):
echo    http://%API_IP%:3000
echo.
echo ========================================
echo   ARQUIVOS CRIADOS
echo ========================================
echo.
echo probe_config.json:
type probe_config.json
echo.
echo.
echo wmi_credentials.json (EDITE ESTE ARQUIVO):
type wmi_credentials.json
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit
