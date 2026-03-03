# Script para testar endpoint de métricas no backend
Write-Host "=== TESTE DE MÉTRICAS BACKEND ===" -ForegroundColor Cyan
Write-Host ""

# Obter token
Write-Host "1. Fazendo login..." -ForegroundColor Yellow
$loginBody = @{
    email = "admin@coruja.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✓ Login bem-sucedido!" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Erro no login: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Testando endpoint de métricas..." -ForegroundColor Yellow

# Testar endpoint
$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $metricsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h" -Method Get -Headers $headers
    Write-Host "✓ Endpoint funcionando!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Resposta:" -ForegroundColor Cyan
    $metricsResponse | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ Erro ao buscar métricas: $_" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== TESTE CONCLUÍDO ===" -ForegroundColor Cyan
