@echo off
REM ========================================
REM Instalar Probe como Servico com Conta de Dominio
REM Resolve problema de WMI "Access Denied"
REM ========================================

echo ========================================
echo   CORUJA MONITOR - SERVICO COM DOMINIO
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    pause
    exit /b 1
)

echo [OK] Privilegios de administrador verificados
echo.

REM Obter diretorio atual
set "PROBE_DIR=%~dp0"
set "PROBE_DIR=%PROBE_DIR:~0,-1%"

echo Diretorio da probe: %PROBE_DIR%
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

REM Verificar NSSM
where nssm >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: NSSM nao encontrado!
    echo.
    echo Baixe de: https://nssm.cc/download
    echo Extraia nssm.exe para: C:\Windows\System32\
    pause
    exit /b 1
)

echo [OK] NSSM encontrado
echo.

echo ========================================
echo CONFIGURACAO DA CONTA DE DOMINIO
echo ========================================
echo.
echo IMPORTANTE: O servico rodara com conta de dominio
echo Isso permite WMI usar Kerberos automaticamente
echo.
set /p DOMAIN_USER="Digite o usuario (ex: TECHBIZ\coruja.monitor): "
set /p DOMAIN_PASS="Digite a senha: "
echo.

REM Parar e remover servico existente
echo [1/5] Removendo servico existente (se houver)...
nssm stop CorujaProbe >nul 2>&1
timeout /t 2 /nobreak >nul
nssm remove CorujaProbe confirm >nul 2>&1
echo [OK] Servico removido
echo.

echo [2/5] Instalando servico...
nssm install CorujaProbe python "%PROBE_DIR%\probe_core.py"
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao instalar servico
    pause
    exit /b 1
)
echo [OK] Servico instalado
echo.

echo [3/5] Configurando servico...
nssm set CorujaProbe AppDirectory "%PROBE_DIR%"
nssm set CorujaProbe DisplayName "Coruja Monitor Probe"
nssm set CorujaProbe Description "Coleta metricas com autenticacao Kerberos"
nssm set CorujaProbe Start SERVICE_AUTO_START
nssm set CorujaProbe AppStdout "%PROBE_DIR%\logs\service.log"
nssm set CorujaProbe AppStderr "%PROBE_DIR%\logs\service_error.log"
nssm set CorujaProbe AppRotateFiles 1
nssm set CorujaProbe AppRotateOnline 1
nssm set CorujaProbe AppRotateSeconds 86400
echo [OK] Configuracao basica aplicada
echo.

echo [4/5] Configurando conta de dominio...
nssm set CorujaProbe ObjectName "%DOMAIN_USER%" "%DOMAIN_PASS%"
if %errorLevel% neq 0 (
    echo [ERRO] Falha ao configurar conta de dominio
    echo Verifique usuario e senha
    pause
    exit /b 1
)
echo [OK] Conta de dominio configurada
echo.

echo [5/5] Iniciando servico...
nssm start CorujaProbe
if %errorLevel% equ 0 (
    echo [OK] Servico iniciado
) else (
    echo [AVISO] Falha ao iniciar servico
    echo Verifique os logs em: %PROBE_DIR%\logs\
)

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Servico: CorujaProbe
echo Usuario: %DOMAIN_USER%
echo Logs: %PROBE_DIR%\logs\
echo.
echo COMANDOS UTEIS:
echo   nssm status CorujaProbe
echo   nssm restart CorujaProbe
echo   nssm stop CorujaProbe
echo.
pause
