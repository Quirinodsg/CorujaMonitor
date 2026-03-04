@echo off
echo ========================================
echo Criando Usuario Administrador
echo ========================================
echo.

echo Criando usuario admin@coruja.com...
docker exec -it coruja-api python init_admin.py

echo.
echo ========================================
echo Pronto!
echo ========================================
echo.
echo Credenciais de acesso:
echo Email: admin@coruja.com
echo Senha: admin123
echo.
echo Acesse: http://localhost:3000
echo.
pause
