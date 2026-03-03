@echo off
echo ========================================
echo Reconstruindo Frontend com Correcoes
echo ========================================
echo.

cd frontend

echo [1/3] Limpando cache e build anterior...
if exist build rmdir /s /q build
if exist node_modules\.cache rmdir /s /q node_modules\.cache
echo Cache limpo!
echo.

echo [2/3] Instalando dependencias...
call npm install
echo.

echo [3/3] Reconstruindo frontend...
call npm run build
echo.

echo ========================================
echo Frontend reconstruido com sucesso!
echo ========================================
echo.
echo Agora reinicie o Docker:
echo   docker-compose down
echo   docker-compose up -d
echo.
pause
