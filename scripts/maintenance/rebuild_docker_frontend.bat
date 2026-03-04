@echo off
echo ========================================
echo Reconstruindo Frontend no Docker
echo ========================================
echo.

echo [1/3] Parando containers...
docker-compose down
echo.

echo [2/3] Reconstruindo imagem do frontend (sem cache)...
docker-compose build --no-cache frontend
echo.

echo [3/3] Iniciando containers...
docker-compose up -d
echo.

echo ========================================
echo Pronto! Frontend reconstruido!
echo ========================================
echo.
echo Aguarde 30 segundos e acesse:
echo   http://localhost:3000
echo.
echo Verifique os logs:
echo   docker-compose logs -f frontend
echo.
pause
