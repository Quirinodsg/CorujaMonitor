@echo off
echo ========================================
echo RESET COMPLETO - Coruja Monitor
echo ========================================
echo.
echo ATENCAO: Isso vai apagar todos os dados!
echo.
pause

echo [1/8] Parando todos os containers...
docker compose down

echo.
echo [2/8] Removendo volumes (dados do banco)...
docker volume rm coruja-monitor_postgres_data 2>nul
docker volume rm coruja-monitor_redis_data 2>nul
docker volume rm coruja-monitor_api_logs 2>nul
docker volume rm coruja-monitor_worker_logs 2>nul
docker volume rm coruja-monitor_ai_logs 2>nul

echo.
echo [3/8] Removendo imagens antigas...
docker rmi coruja-monitor-api 2>nul
docker rmi coruja-monitor-worker 2>nul
docker rmi coruja-monitor-ai-agent 2>nul
docker rmi coruja-monitor-frontend 2>nul

echo.
echo [4/8] Limpando cache do Docker...
docker system prune -f

echo.
echo [5/8] Reconstruindo todas as imagens...
docker compose build --no-cache

echo.
echo [6/8] Iniciando servicos...
docker compose up -d

echo.
echo [7/8] Aguardando servicos iniciarem (30 segundos)...
timeout /t 30 /nobreak

echo.
echo [8/8] Criando usuario administrador...
timeout /t 5 /nobreak
docker exec -it coruja-api pip install --upgrade bcrypt==4.0.1
docker exec -it coruja-api python init_admin.py

echo.
echo ========================================
echo RESET COMPLETO!
echo ========================================
echo.
echo Testando login...
timeout /t 2 /nobreak

curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@coruja.com\",\"password\":\"admin123\"}"

echo.
echo.
echo ========================================
echo Acesse: http://localhost:3000
echo Email: admin@coruja.com
echo Senha: admin123
echo ========================================
echo.
pause
