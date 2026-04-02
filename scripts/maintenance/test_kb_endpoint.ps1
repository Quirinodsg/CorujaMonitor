# Testar endpoint da Base de Conhecimento

$API_URL = "http://192.168.30.189:8000"

# Login para pegar token
$loginBody = @{
    username = "admin@coruja.com"
    password = "admin123"
} | ConvertTo-Json

Write-Host "[LOGIN] Fazendo login..." -ForegroundColor Cyan
$loginResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access_token
Write-Host "[OK] Token obtido" -ForegroundColor Green

# Testar endpoint de stats
Write-Host "`n[STATS] Testando /knowledge-base/stats..." -ForegroundColor Cyan
$headers = @{
    "Authorization" = "Bearer $token"
}
$stats = Invoke-RestMethod -Uri "$API_URL/api/v1/knowledge-base/stats" -Headers $headers
Write-Host "Stats:" -ForegroundColor Yellow
$stats | ConvertTo-Json

# Testar endpoint de listagem
Write-Host "`n[LIST] Testando /knowledge-base/..." -ForegroundColor Cyan
$entries = Invoke-RestMethod -Uri "$API_URL/api/v1/knowledge-base/" -Headers $headers
Write-Host "Total de entradas: $($entries.Count)" -ForegroundColor Yellow

if ($entries.Count -gt 0) {
    Write-Host "`n[OK] Primeira entrada:" -ForegroundColor Green
    $entries[0] | ConvertTo-Json
} else {
    Write-Host "`n[ERRO] Nenhuma entrada retornada!" -ForegroundColor Red
}
