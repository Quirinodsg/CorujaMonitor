@echo off
echo ========================================
echo Reconstruindo API com dependencias corretas
echo ========================================
echo.

echo [1/3] Parando container da API...
docker compose stop api

echo.
echo [2/3] Reconstruindo imagem da API...
docker compose build api

echo.
echo [3/3] Iniciando API...
docker compose up -d api

echo.
echo Aguardando API iniciar...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo API reconstruida!
echo ========================================
echo.
echo Agora execute: create_user_direct.bat
echo.
pause
