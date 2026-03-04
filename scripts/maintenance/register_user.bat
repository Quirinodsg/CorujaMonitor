@echo off
echo Registrando novo usuario no Coruja Monitor...
echo.

curl -X POST "http://localhost:8000/api/v1/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@coruja.com\",\"password\":\"admin123\",\"full_name\":\"Administrator\",\"tenant_name\":\"Minha Empresa\"}"

echo.
echo.
echo Usuario criado com sucesso!
echo Email: admin@coruja.com
echo Senha: admin123
echo.
pause
