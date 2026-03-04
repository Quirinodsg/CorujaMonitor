@echo off
echo ========================================
echo Reinicio Completo - Coruja Monitor
echo ========================================
echo.

echo [1/6] Parando todos os containers...
docker compose down

echo.
echo [2/6] Limpando volumes antigos (opcional)...
REM docker volume prune -f

echo.
echo [3/6] Reconstruindo todas as imagens...
docker compose build --no-cache

echo.
echo [4/6] Iniciando servicos...
docker compose up -d

echo.
echo [5/6] Aguardando servicos iniciarem (30 segundos)...
timeout /t 30 /nobreak

echo.
echo [6/6] Verificando status...
docker ps --filter "name=coruja"

echo.
echo ========================================
echo Testando conectividade...
echo ========================================
echo.

echo API Health:
curl -s http://localhost:8000/health
echo.

echo.
echo Frontend:
curl -s -I http://localhost:3000 | findstr "HTTP"

echo.
echo ========================================
echo Servicos reiniciados!
echo ========================================
echo.
echo Proximos passos:
echo 1. Execute: fix_and_create_user.bat
echo 2. Acesse: http://localhost:3000
echo 3. Login: admin@coruja.com / admin123
echo.
pause
