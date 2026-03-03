@echo off
echo ========================================
echo Testando Login na API
echo ========================================
echo.

echo Testando com admin@coruja.com...
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@coruja.com\",\"password\":\"admin123\"}"

echo.
echo.
echo ========================================
echo Se viu "access_token" acima, esta OK!
echo ========================================
pause
