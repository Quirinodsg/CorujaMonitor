@echo off
echo ============================================================
echo TESTE DE RESOLUCAO DE INCIDENTE
echo ============================================================

echo.
echo 1. Fazendo login...
curl -X POST "http://192.168.30.189:8000/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin@coruja.com&password=admin123" ^
  -o token.json

echo.
echo 2. Simulando falha no sensor 199 (CPU)...
for /f "tokens=*" %%a in ('powershell -Command "(Get-Content token.json | ConvertFrom-Json).access_token"') do set TOKEN=%%a

curl -X POST "http://192.168.30.189:8000/api/v1/test-tools/simulate-failure" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"sensor_id\": 199, \"failure_type\": \"critical\", \"value\": 96.0, \"duration_minutes\": 5}"

echo.
echo.
echo 3. Aguardando 3 segundos...
timeout /t 3 /nobreak > nul

echo.
echo 4. Verificando incidentes abertos...
curl -X GET "http://192.168.30.189:8000/api/v1/incidents/?status=open" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -o incidents.json

echo.
powershell -Command "Get-Content incidents.json | ConvertFrom-Json | ForEach-Object { Write-Host \"   Incidente ID: $($_.id) - $($_.title)\" }"

echo.
echo 5. Resolvendo primeiro incidente...
for /f "tokens=*" %%a in ('powershell -Command "(Get-Content incidents.json | ConvertFrom-Json)[0].id"') do set INCIDENT_ID=%%a

curl -X POST "http://192.168.30.189:8000/api/v1/incidents/%INCIDENT_ID%/resolve" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"resolution_notes\": \"Teste automatizado - incidente resolvido\"}"

echo.
echo.
echo 6. Aguardando 3 segundos...
timeout /t 3 /nobreak > nul

echo.
echo 7. Verificando se incidente foi resolvido...
curl -X GET "http://192.168.30.189:8000/api/v1/incidents/?status=open" ^
  -H "Authorization: Bearer %TOKEN%"

echo.
echo.
echo 8. Verificando metrica atual do sensor 199...
curl -X GET "http://192.168.30.189:8000/api/v1/metrics/?sensor_id=199&limit=1" ^
  -H "Authorization: Bearer %TOKEN%"

echo.
echo.
echo ============================================================
echo TESTE CONCLUIDO
echo ============================================================
echo.
echo Aguardando 60 segundos para probe coletar nova metrica...
timeout /t 60 /nobreak

echo.
echo Verificando metrica final...
curl -X GET "http://192.168.30.189:8000/api/v1/metrics/?sensor_id=199&limit=1" ^
  -H "Authorization: Bearer %TOKEN%"

echo.
echo.
pause
