# ========================================
# Instalar MFA (Multi-Factor Authentication)
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALANDO MFA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Instalar dependências Python
Write-Host "[1/3] Instalando dependências Python..." -ForegroundColor Yellow
docker-compose exec api pip install pyotp==2.9.0 qrcode[pil]==7.4.2

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dependências instaladas" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Falha ao instalar dependências" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. Executar migração do banco de dados
Write-Host "[2/3] Executando migração do banco de dados..." -ForegroundColor Yellow
docker-compose exec api python migrate_mfa.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Migração concluída" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Falha na migração" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. Reiniciar API
Write-Host "[3/3] Reiniciando API..." -ForegroundColor Yellow
docker-compose restart api

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] API reiniciada" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Falha ao reiniciar API" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  MFA INSTALADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Acesse: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Vá em: Configurações > Segurança > MFA" -ForegroundColor Cyan
Write-Host ""
Write-Host "Funcionalidades:" -ForegroundColor Yellow
Write-Host "  - Geração de QR Code para Google Authenticator" -ForegroundColor White
Write-Host "  - Códigos de backup para emergências" -ForegroundColor White
Write-Host "  - Suporte para TOTP (Time-based One-Time Password)" -ForegroundColor White
Write-Host "  - Compatível com Google Authenticator, Authy, Microsoft Authenticator" -ForegroundColor White
Write-Host ""
