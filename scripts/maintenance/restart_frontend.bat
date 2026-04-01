@echo off
echo ========================================
echo  Reiniciando Frontend - Coruja Monitor
echo ========================================
echo.

cd "C:\Users\user\Coruja Monitor"

echo [1/5] Parando frontend...
docker-compose stop frontend

echo.
echo [2/5] Removendo container antigo...
docker rm coruja-frontend

echo.
echo [3/5] Reconstruindo sem cache...
docker-compose build --no-cache frontend

echo.
echo [4/5] Iniciando frontend...
docker-compose up -d frontend

echo.
echo [5/5] Aguardando inicializacao...
timeout /t 30 /nobreak

echo.
echo ========================================
echo  Frontend reiniciado com sucesso!
echo ========================================
echo.
echo Acesse: http://localhost:3000
echo Login: admin@coruja.com / admin123
echo.
echo IMPORTANTE: Faca Ctrl+Shift+R no navegador
echo para forcar atualizacao do cache!
echo.
pause
