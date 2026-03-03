@echo off
echo ========================================
echo Verificando Servicos Coruja Monitor
echo ========================================
echo.

echo [1] Verificando containers rodando...
docker ps --filter "name=coruja" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [2] Testando API (http://localhost:8000)...
curl -s http://localhost:8000/health
echo.

echo.
echo [3] Testando Frontend (http://localhost:3000)...
curl -s -I http://localhost:3000 | findstr "HTTP"

echo.
echo [4] Verificando logs da API...
echo Ultimas 10 linhas:
docker logs coruja-api --tail 10

echo.
echo [5] Verificando logs do Frontend...
echo Ultimas 10 linhas:
docker logs coruja-frontend --tail 10

echo.
echo ========================================
echo Diagnostico completo
echo ========================================
pause
