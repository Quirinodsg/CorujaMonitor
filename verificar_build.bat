@echo off
echo ========================================
echo Verificando Status do Build
echo ========================================
echo.

echo [1] Status dos containers:
docker-compose ps
echo.

echo [2] Logs do frontend (ultimas 20 linhas):
docker-compose logs --tail=20 frontend
echo.

echo [3] Processos Docker:
docker ps
echo.

echo ========================================
echo Pressione qualquer tecla para sair...
pause >nul
