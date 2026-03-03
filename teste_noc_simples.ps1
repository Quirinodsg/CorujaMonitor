# Teste simples do NOC
$API_URL = "http://localhost:8000/api/v1"

# Login
$login = Invoke-RestMethod -Uri "$API_URL/auth/login" -Method Post -Body '{"email":"admin@coruja.com","password":"admin123"}' -ContentType "application/json"
$headers = @{"Authorization" = "Bearer $($login.access_token)"}

# Testar NOC
Write-Host "Testando NOC Global Status..." -ForegroundColor Cyan
$noc = Invoke-RestMethod -Uri "$API_URL/noc/global-status" -Method Get -Headers $headers

Write-Host "Servidores OK: $($noc.servers_ok)" -ForegroundColor Green
Write-Host "Servidores AVISO: $($noc.servers_warning)" -ForegroundColor Yellow
Write-Host "Servidores CRÍTICOS: $($noc.servers_critical)" -ForegroundColor Red
Write-Host "Total: $($noc.total_servers)" -ForegroundColor Cyan
Write-Host "Disponibilidade: $($noc.availability)%" -ForegroundColor Cyan
