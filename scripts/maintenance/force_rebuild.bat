@echo off
echo ========================================
echo REBUILD FORCADO - SEM CACHE
echo ========================================
echo.

echo [1/5] Parando TUDO...
docker compose down -v

echo.
echo [2/5] Removendo imagens antigas...
docker rmi coruja-monitor-frontend -f 2>nul
docker rmi coruja-monitor-api -f 2>nul

echo.
echo [3/5] Reconstruindo SEM CACHE...
docker compose build --no-cache --pull

echo.
echo [4/5] Iniciando servicos...
docker compose up -d

echo.
echo [5/5] Aguardando (30 segundos)...
timeout /t 30 /nobreak

echo.
echo Criando usuario...
docker exec -it coruja-api pip install --upgrade bcrypt==4.0.1
docker exec -it coruja-api python init_admin.py

echo.
echo ========================================
echo PRONTO!
echo ========================================
echo.
echo IMPORTANTE:
echo 1. Feche TODAS as abas do navegador
echo 2. Abra o navegador novamente
echo 3. Ou use modo anonimo (Ctrl+Shift+N)
echo 4. Acesse: http://localhost:3000
echo.
echo Credenciais:
echo Email: admin@coruja.com
echo Senha: admin123
echo.
pause
