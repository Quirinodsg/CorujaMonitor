@echo off
REM Mudar para o diretorio do script
cd /d "%~dp0"

REM Script para atualizar sonda existente com nova versao (coleta remota)

echo ========================================
echo   Atualizacao Sonda Coruja
echo   Versao: Agentless (PRTG-style)
echo ========================================
echo.

REM Verificar se esta rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    echo Clique com botao direito e selecione "Executar como administrador"
    pause
    exit /b 1
)

echo [1/4] Parando servico...
sc query "Coruja Probe" >nul 2>&1
if %errorLevel% equ 0 (
    net stop "Coruja Probe"
    timeout /t 2 /nobreak >nul
    echo Servico parado.
) else (
    echo Servico nao encontrado (primeira instalacao).
)

echo.
echo [2/4] Atualizando arquivos...
REM Os arquivos ja estao na pasta atual (probe_core.py foi atualizado)
echo Arquivos atualizados.

echo.
echo [3/4] Reinstalando servico...
if exist "uninstall_service.bat" (
    call uninstall_service.bat >nul 2>&1
)
call install_service.bat

echo.
echo [4/4] Iniciando servico...
net start "Coruja Probe"

echo.
echo ========================================
echo   Atualizacao Concluida!
echo ========================================
echo.
echo Nova funcionalidade:
echo - Coleta remota via WMI (agentless)
echo - Coleta remota via SNMP (agentless)
echo - Coleta remota via PING (agentless)
echo.
echo A sonda agora coleta dados de servidores remotos
echo sem precisar instalar nada neles!
echo.
echo Para usar:
echo 1. Adicione servidores na interface web
echo 2. Configure credenciais WMI (para Windows)
echo 3. Aguarde 1-2 minutos
echo 4. Dados aparecem automaticamente
echo.
pause
