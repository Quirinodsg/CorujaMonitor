@echo off
REM ========================================
REM Instalador Usando Usuario Atual
REM Detecta automaticamente o usuario admin local
REM ========================================

title Instalador Coruja Monitor (Usuario Atual)

echo.
echo ========================================
echo   INSTALADOR CORUJA MONITOR
echo   (USANDO USUARIO ATUAL)
echo ========================================
echo.
echo Este instalador vai:
echo - Detectar seu usuario atual
echo - Configurar Firewall, DCOM e WMI
echo - Criar arquivos de configuracao
echo - Usar SEU usuario (nao cria novo)
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM ========================================
REM Verificar Admin
REM ========================================
cls
echo.
echo [1/8] Verificando privilegios...
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
echo [2/8] Detectando usuario atual...
set CURRENT_USER=%USERNAME%
for /f "tokens=*" %%a in ('hostname') do set HOSTNAME=%%a
echo [OK] Usuario detectado: %CURRENT_USER%
echo [OK] Computador: %HOSTNAME%
timeout /t 2 >nul

REM ========================================
REM Solicitar Senha
REM ========================================
cls
echo.
echo [3/8] Configurando credenciais...
echo.
echo Usuario detectado: %CURRENT_USER%
echo Computador: %HOSTNAME%
echo.
echo Digite a senha do usuario %CURRENT_USER%:
set /p USER_PASSWORD="Senha: "
echo.
echo [OK] Senha configurada
timeout /t 2 >nul

REM ========================================
REM Firewall
REM ========================================
cls
echo.
echo [4/8] Configurando Firewall...
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
echo [5/8] Configurando DCOM...
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
echo [6/8] Configurando WMI...
powershell -Command "$namespace = Get-WmiObject -Namespace 'root' -Class '__SystemSecurity'; $null = $namespace.PsBase.InvokeMethod('SetSecurityDescriptor', $null)" >nul 2>&1
echo [OK] WMI configurado
timeout /t 2 >nul

REM ========================================
REM Credenciais
REM ========================================
cls
echo.
echo [7/8] Criando arquivo de credenciais...
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
echo [8/8] Configurando probe...
echo.
echo Digite o IP do servidor Coruja Monitor
echo (exemplo: 192.168.0.9)
echo.
set /p API_IP="IP do servidor: "

cls
echo.
echo [8/8] Configurando probe...
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
echo Testando WMI...
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
echo Configuracao criada:
echo   Usuario: %CURRENT_USER%
echo   Computador: %HOSTNAME%
echo   Dominio: %HOSTNAME%
echo.
echo ========================================
echo   ARQUIVOS CRIADOS
echo ========================================
echo.
echo probe_config.json:
type probe_config.json
echo.
echo.
echo wmi_credentials.json:
type wmi_credentials.json
echo.
echo ========================================
echo   PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Instale Python 3.8 ou superior:
echo    https://www.python.org/downloads/
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
