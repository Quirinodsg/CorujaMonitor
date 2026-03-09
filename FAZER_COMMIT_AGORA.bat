@echo off
chcp 65001 >nul
echo ========================================
echo   COMMIT E PUSH - SISTEMA DE RESET
echo ========================================
echo.

echo [1/4] Adicionando arquivos...
git add .

echo [2/4] Fazendo commit...
git commit -m "Sistema de Reset Completo implementado - Endpoint /api/v1/system/reset - Componente SystemReset.js - Integrado em Settings - Script reset_sistema.py - Guias completos"

echo [3/4] Enviando para GitHub (branch master)...
git push origin master

echo [4/4] Concluído!
echo.
echo ========================================
echo   PRÓXIMO PASSO: ATUALIZAR NO LINUX
echo ========================================
echo.
echo Execute no servidor Linux:
echo.
echo cd /home/administrador/CorujaMonitor ^&^& \
echo git fetch origin ^&^& \
echo git checkout master ^&^& \
echo git pull origin master ^&^& \
echo docker-compose restart
echo.
echo Aguarde 30 segundos e acesse:
echo http://192.168.31.161:3000
echo.
echo Veja: EXECUTAR_NO_LINUX_AGORA.txt
echo.
pause
