# Script para popular Base de Conhecimento com 80 itens
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "  BASE DE CONHECIMENTO - POPULAR 80 ITENS" -ForegroundColor Yellow
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Ler credenciais do .env
$envFile = Get-Content .env
$apiUrl = "http://localhost:8000"
$username = "admin@coruja.local"
$password = ($envFile | Select-String "ADMIN_PASSWORD=" | ForEach-Object { $_.ToString().Split('=')[1] }).Trim()

Write-Host "1. Fazendo login..." -ForegroundColor Cyan
$loginBody = @{
    username = $username
    password = $password
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$apiUrl/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "   OK Login realizado com sucesso" -ForegroundColor Green
} catch {
    Write-Host "   ERRO ao fazer login: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Populando Base de Conhecimento..." -ForegroundColor Cyan
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "$apiUrl/api/v1/seed-kb/populate" -Method Post -Headers $headers
    
    Write-Host "   OK Base de conhecimento populada!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Estatisticas:" -ForegroundColor Yellow
    Write-Host "   - Entradas antes: $($response.entries_before)" -ForegroundColor White
    Write-Host "   - Entradas adicionadas: $($response.entries_added)" -ForegroundColor Green
    Write-Host "   - Total de entradas: $($response.entries_total)" -ForegroundColor Cyan
    
} catch {
    Write-Host "   ERRO ao popular: $_" -ForegroundColor Red
    Write-Host "   Detalhes: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. Verificando estatisticas..." -ForegroundColor Cyan
try {
    $stats = Invoke-RestMethod -Uri "$apiUrl/api/v1/knowledge-base/stats" -Method Get -Headers $headers
    
    Write-Host "   Total de entradas: $($stats.total_entries)" -ForegroundColor Cyan
    Write-Host "   Com auto-resolucao: $($stats.auto_resolution_enabled)" -ForegroundColor Green
    Write-Host "   Taxa de sucesso media: $([math]::Round($stats.average_success_rate * 100, 2))%" -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "   Por tipo de sensor:" -ForegroundColor Yellow
    $stats.by_sensor_type.PSObject.Properties | ForEach-Object {
        Write-Host "   - $($_.Name): $($_.Value)" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "   Por nivel de risco:" -ForegroundColor Yellow
    $stats.by_risk_level.PSObject.Properties | ForEach-Object {
        Write-Host "   - $($_.Name): $($_.Value)" -ForegroundColor White
    }
    
} catch {
    Write-Host "   AVISO: Nao foi possivel obter estatisticas" -ForegroundColor Yellow
}

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""
Write-Host "A Base de Conhecimento agora possui 80 itens cobrindo:" -ForegroundColor White
Write-Host "  - Windows Server (15 itens)" -ForegroundColor Gray
Write-Host "  - Linux (15 itens)" -ForegroundColor Gray
Write-Host "  - Docker (10 itens)" -ForegroundColor Gray
Write-Host "  - Azure/AKS (10 itens)" -ForegroundColor Gray
Write-Host "  - Rede/Ubiquiti (10 itens)" -ForegroundColor Gray
Write-Host "  - Nobreaks/UPS (5 itens)" -ForegroundColor Gray
Write-Host "  - Ar-condicionado (5 itens)" -ForegroundColor Gray
Write-Host "  - Web Applications (10 itens)" -ForegroundColor Gray
Write-Host ""
