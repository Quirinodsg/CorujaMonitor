@echo off
echo ========================================
echo CORRECAO COMPLETA - Coruja Monitor
echo ========================================
echo.

echo [1/7] Parando containers...
docker compose down -v

echo.
echo [2/7] Reconstruindo API...
docker compose build api --no-cache

echo.
echo [3/7] Iniciando servicos...
docker compose up -d

echo.
echo [4/7] Aguardando (30 segundos)...
timeout /t 30 /nobreak

echo.
echo [5/7] Testando JWT...
docker exec -it coruja-api python test_jwt.py

echo.
echo [6/7] Criando usuario...
docker exec -it coruja-api pip install --upgrade bcrypt==4.0.1
docker exec -it coruja-api python init_admin.py

echo.
echo [7/7] Testando login completo...
docker exec -it coruja-api python test_login.py

echo.
echo ========================================
echo PRONTO!
echo ========================================
echo.
echo Agora:
echo 1. Limpe o localStorage no navegador:
echo    localStorage.clear(); location.reload()
echo.
echo 2. Acesse: http://localhost:3000
echo 3. Login: admin@coruja.com / admin123
echo.
pause
