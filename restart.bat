@echo off
echo ========================================
echo Reiniciando Coruja Monitor
echo ========================================
echo.

echo [1/3] Parando containers...
docker compose down

echo.
echo [2/3] Reconstruindo imagens...
docker compose build

echo.
echo [3/3] Iniciando containers...
docker compose up -d

echo.
echo Aguardando servicos iniciarem...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo Servicos reiniciados!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Para ver logs: docker compose logs -f
echo.
pause
