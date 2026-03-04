@echo off
echo ========================================
echo  Teste TOPdesk com Debug
echo ========================================
echo.

echo [1/2] Aguardando API inicializar...
timeout /t 10 /nobreak >nul

echo [2/2] Acompanhando logs em tempo real...
echo.
echo Agora:
echo 1. Abra o navegador
echo 2. Va em Configuracoes ^> Integracoes
echo 3. Clique em "Testar Criacao de Chamado" no TOPdesk
echo 4. Observe os logs abaixo
echo.
echo Pressione Ctrl+C para parar
echo ========================================
echo.

docker logs coruja-api -f --tail 50
