@echo off
echo ========================================
echo Registrando Usuario via API
echo ========================================
echo.

curl -X POST "http://localhost:8000/api/v1/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@coruja.com\",\"password\":\"admin123\",\"full_name\":\"Administrator\",\"tenant_name\":\"Minha Empresa\"}"

echo.
echo.
echo ========================================
echo Se viu "user_id" acima, usuario criado!
echo ========================================
echo.
echo Credenciais:
echo Email: admin@coruja.com
echo Senha: admin123
echo.
echo Acesse: http://localhost:3000
echo.
pause
