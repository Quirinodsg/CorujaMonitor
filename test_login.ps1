# Test Coruja Monitor Login
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testando Login na API Coruja Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test API Health
Write-Host "[1] Testando API Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✓ API esta rodando: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ API nao esta respondendo!" -ForegroundColor Red
    Write-Host "Execute: docker compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[2] Testando Login..." -ForegroundColor Yellow

$body = @{
    email = "admin@coruja.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "✓ Login bem-sucedido!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Token: $($response.access_token.Substring(0,50))..." -ForegroundColor Gray
    Write-Host "Usuario: $($response.user.full_name)" -ForegroundColor Gray
    Write-Host "Email: $($response.user.email)" -ForegroundColor Gray
    Write-Host "Role: $($response.user.role)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Tudo funcionando! Acesse:" -ForegroundColor Green
    Write-Host "http://localhost:3000" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
} catch {
    Write-Host "✗ Erro no login!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Detalhes do erro:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        $errorDetail = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "API Response: $($errorDetail.detail)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Solucao:" -ForegroundColor Yellow
    Write-Host "1. Execute: fix_and_create_user.bat" -ForegroundColor White
    Write-Host "2. Tente novamente" -ForegroundColor White
}

Write-Host ""
Read-Host "Pressione Enter para sair"
