# Script de Teste - Dashboard e Metricas
# Data: 27/02/2026

Write-Host "Teste Dashboard Avancado e Metricas" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Verificando containers..." -ForegroundColor Yellow
docker-compose ps frontend
docker-compose ps api
Write-Host ""

Write-Host "2. Logs do frontend:" -ForegroundColor Yellow
docker logs coruja-frontend --tail 5
Write-Host ""

Write-Host "3. Testando endpoint de metricas..." -ForegroundColor Yellow

try {
    $loginBody = @{
        email = "admin@coruja.com"
        password = "admin123"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    
    $token = $loginResponse.access_token
    Write-Host "   OK - Login realizado" -ForegroundColor Green
    
    $headers = @{ "Authorization" = "Bearer $token" }
    
    $metricsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h" -Method Get -Headers $headers
    
    Write-Host "   OK - Endpoint respondendo" -ForegroundColor Green
    Write-Host "     Servidores: $($metricsResponse.summary.servers_online)/$($metricsResponse.summary.servers_total)" -ForegroundColor Cyan
    
} catch {
    Write-Host "   ERRO: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "TESTE MANUAL:" -ForegroundColor Cyan
Write-Host "1. Abrir http://localhost:3000" -ForegroundColor White
Write-Host "2. Login: admin@coruja.com / admin123" -ForegroundColor White
Write-Host "3. Testar Dashboard Avancado e Metricas" -ForegroundColor White
