# Script para Corrigir Login do Admin
# Data: 03 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRIGIR LOGIN DO ADMIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Reiniciando API..." -ForegroundColor Yellow
docker-compose restart api

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: API reiniciada!" -ForegroundColor Green
} else {
    Write-Host "ERRO: Falha ao reiniciar API!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] Aguardando API inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "OK: API deve estar pronta!" -ForegroundColor Green

Write-Host ""
Write-Host "[3/3] Testando login..." -ForegroundColor Yellow
Write-Host ""

$body = @{
    username = "admin@coruja.com"
    password = "admin123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
                                   -Method Post `
                                   -Body $body `
                                   -ContentType "application/json"
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  LOGIN FUNCIONANDO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usuario: $($response.user.email)" -ForegroundColor White
    Write-Host "Nome: $($response.user.full_name)" -ForegroundColor White
    Write-Host "Role: $($response.user.role)" -ForegroundColor White
    Write-Host "Token: $($response.access_token.Substring(0, 20))..." -ForegroundColor White
    Write-Host ""
    Write-Host "Agora voce pode fazer login no sistema!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  ERRO NO LOGIN" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique:" -ForegroundColor Yellow
    Write-Host "1. API esta rodando: docker ps" -ForegroundColor White
    Write-Host "2. Logs da API: docker logs coruja-api --tail 50" -ForegroundColor White
    Write-Host "3. Usuario existe no banco de dados" -ForegroundColor White
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CREDENCIAIS DO ADMIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Usuario: admin@coruja.com" -ForegroundColor White
Write-Host "Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "URL: http://localhost:3000" -ForegroundColor White
Write-Host ""
