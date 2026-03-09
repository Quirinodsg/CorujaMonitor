@echo off
REM Script para instalar sonda remotamente em outra máquina Windows
REM Requer: PsExec (Sysinternals) ou acesso administrativo remoto

echo ========================================
echo   Instalacao Remota - Coruja Probe
echo ========================================
echo.

REM Solicitar informações
set /p REMOTE_IP="Digite o IP da maquina remota: "
set /p REMOTE_USER="Digite o usuario administrador (ex: Administrator): "
set /p REMOTE_PASS="Digite a senha: "
set /p API_URL="Digite a URL da API (ex: http://192.168.0.38:8000): "
set /p PROBE_TOKEN="Digite o token da probe: "

echo.
echo Configuracao:
echo - IP Remoto: %REMOTE_IP%
echo - Usuario: %REMOTE_USER%
echo - API URL: %API_URL%
echo.

pause

REM Criar pasta temporária
set TEMP_DIR=%TEMP%\coruja_probe_install
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Copiar arquivos da probe
echo.
echo [1/5] Copiando arquivos da probe...
xcopy /E /I /Y "%~dp0*" "%TEMP_DIR%"

REM Criar arquivo de configuração
echo.
echo [2/5] Criando arquivo de configuracao...
(
echo {
echo   "api_url": "%API_URL%",
echo   "probe_token": "%PROBE_TOKEN%",
echo   "collection_interval": 60,
echo   "monitored_services": [
echo     "W3SVC",
echo     "MSSQLSERVER",
echo     "Spooler"
echo   ],
echo   "udm_targets": []
echo }
) > "%TEMP_DIR%\probe_config.json"

REM Copiar para máquina remota
echo.
echo [3/5] Copiando para maquina remota...
net use \\%REMOTE_IP%\C$ /user:%REMOTE_USER% %REMOTE_PASS%
if errorlevel 1 (
    echo ERRO: Nao foi possivel conectar a maquina remota!
    echo Verifique:
    echo - IP esta correto
    echo - Usuario e senha estao corretos
    echo - Compartilhamento administrativo esta habilitado
    echo - Firewall permite conexao SMB (porta 445)
    pause
    exit /b 1
)

if not exist "\\%REMOTE_IP%\C$\Coruja" mkdir "\\%REMOTE_IP%\C$\Coruja"
xcopy /E /I /Y "%TEMP_DIR%" "\\%REMOTE_IP%\C$\Coruja\probe"

REM Instalar serviço remotamente
echo.
echo [4/5] Instalando servico remotamente...

REM Verificar se PsExec está disponível
where psexec >nul 2>&1
if errorlevel 1 (
    echo.
    echo AVISO: PsExec nao encontrado!
    echo.
    echo Para instalar o servico remotamente, voce precisa:
    echo 1. Baixar PsExec: https://docs.microsoft.com/en-us/sysinternals/downloads/psexec
    echo 2. Extrair psexec.exe para C:\Windows\System32\
    echo.
    echo OU instalar manualmente na maquina remota:
    echo 1. Acessar a maquina %REMOTE_IP%
    echo 2. Abrir CMD como Administrador
    echo 3. Executar: cd C:\Coruja\probe
    echo 4. Executar: install_service.bat
    echo.
    pause
) else (
    REM Instalar usando PsExec
    psexec \\%REMOTE_IP% -u %REMOTE_USER% -p %REMOTE_PASS% -accepteula cmd /c "cd C:\Coruja\probe && install_service.bat"
    
    if errorlevel 1 (
        echo ERRO: Falha ao instalar servico!
        echo Tente instalar manualmente na maquina remota.
        pause
    ) else (
        echo Servico instalado com sucesso!
    )
)

REM Limpar
echo.
echo [5/5] Limpando arquivos temporarios...
net use \\%REMOTE_IP%\C$ /delete
rd /s /q "%TEMP_DIR%"

echo.
echo ========================================
echo   Instalacao Concluida!
echo ========================================
echo.
echo A sonda foi instalada em: C:\Coruja\probe
echo.
echo Para verificar o status:
echo 1. Acesse a maquina %REMOTE_IP%
echo 2. Execute: C:\Coruja\probe\verificar_status.bat
echo.
echo Ou aguarde 1-2 minutos e verifique na interface web
echo se o servidor apareceu automaticamente.
echo.
pause
