@echo off
echo ========================================
echo Testando Correcoes - Dashboard e NOC
echo ========================================
echo.

echo 1. Verificando status dos containers...
docker ps | findstr coruja

echo.
echo 2. Testando endpoint Dashboard Overview...
curl -s http://localhost:8000/api/v1/dashboard/overview -H "Authorization: Bearer %1" | python -m json.tool

echo.
echo 3. Testando endpoint NOC Global Status...
curl -s http://localhost:8000/api/v1/noc/global-status -H "Authorization: Bearer %1" | python -m json.tool

echo.
echo 4. Testando endpoint Falhas Simuladas...
curl -s http://localhost:8000/api/v1/test-tools/simulated-failures -H "Authorization: Bearer %1" | python -m json.tool

echo.
echo ========================================
echo Testes Concluidos!
echo ========================================
echo.
echo Para testar no navegador:
echo 1. Acesse http://localhost:3000
echo 2. Login: admin@coruja.com / admin123
echo 3. Verifique Dashboard (deve mostrar 1 servidor, 28 sensores)
echo 4. Entre no NOC (deve mostrar TENSO)
echo 5. Va em Testes e simule uma falha
echo.

pause
