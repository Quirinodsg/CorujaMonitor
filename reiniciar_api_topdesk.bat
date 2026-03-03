@echo off
echo ========================================
echo  Reiniciando API para Aplicar Correcao
echo  TOPdesk Caller vs Operator
echo ========================================
echo.

echo [1/3] Parando API...
docker stop coruja-api
timeout /t 2 /nobreak >nul

echo [2/3] Iniciando API...
docker start coruja-api
timeout /t 2 /nobreak >nul

echo [3/3] Verificando status...
docker ps | findstr coruja-api

echo.
echo ========================================
echo  API Reiniciada com Sucesso!
echo ========================================
echo.
echo Aguarde 10 segundos para a API inicializar completamente.
echo Depois acesse o frontend e teste a integracao TOPdesk.
echo.
echo Guia de teste: TESTAR_TOPDESK_AGORA.md
echo.
pause
