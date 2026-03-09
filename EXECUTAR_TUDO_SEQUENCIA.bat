@echo off
chcp 65001 >nul
echo ==========================================
echo SEQUÊNCIA COMPLETA - AUTO-REGISTRO
echo ==========================================
echo.
echo Este script vai:
echo 1. Fazer commit e push para GitHub
echo 2. Conectar no Linux e atualizar
echo 3. Iniciar probe no Windows
echo.
echo ==========================================
pause
echo.

echo ==========================================
echo PASSO 1: COMMIT E PUSH
echo ==========================================
echo.
echo Abrindo Git Bash para commit...
echo.
start "" "C:\Program Files\Git\git-bash.exe" -c "cd '/c/Users/andre.quirino/Coruja Monitor' && ./COMMIT_E_PUSH_AGORA.sh && read -p 'Pressione ENTER para fechar...'"
echo.
echo Aguarde o commit terminar...
echo.
pause
echo.

echo ==========================================
echo PASSO 2: ATUALIZAR LINUX
echo ==========================================
echo.
echo COMANDOS PARA EXECUTAR NO LINUX:
echo.
echo cd /home/administrador/CorujaMonitor
echo git pull origin master
echo docker-compose restart
echo.
echo Aguarde 30 segundos após restart
echo.
echo ==========================================
echo.
echo Deseja conectar no Linux agora? (S/N)
set /p conectar=
if /i "%conectar%"=="S" (
    echo.
    echo Conectando via SSH...
    echo.
    ssh root@192.168.31.161
)
echo.

echo ==========================================
echo PASSO 3: INICIAR PROBE NO WINDOWS
echo ==========================================
echo.
echo Após atualizar o Linux, execute:
echo.
echo INICIAR_PROBE_DIRETO.bat
echo.
echo ==========================================
pause
