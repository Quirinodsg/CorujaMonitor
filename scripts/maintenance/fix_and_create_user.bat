@echo off
echo ========================================
echo Corrigindo bcrypt e criando usuario
echo ========================================
echo.

echo [1/3] Atualizando bcrypt no container...
docker exec -it coruja-api pip install --upgrade bcrypt==4.0.1

echo.
echo [2/3] Criando usuario administrador...
docker exec -it coruja-api python init_admin.py

echo.
echo [3/3] Testando login...
curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d "{\"email\":\"admin@coruja.com\",\"password\":\"admin123\"}"

echo.
echo.
echo ========================================
echo Pronto!
echo ========================================
echo.
echo Se viu "access_token" acima, esta funcionando!
echo.
echo Credenciais:
echo Email: admin@coruja.com
echo Senha: admin123
echo.
echo Acesse: http://localhost:3000
echo.
pause
