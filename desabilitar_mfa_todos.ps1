# ========================================
# Desabilitar MFA de Todos os Usuários
# Use este script se não conseguir fazer login
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DESABILITAR MFA DE TODOS OS USUÁRIOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  ATENÇÃO: Este script irá desabilitar o MFA de TODOS os usuários!" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Deseja continuar? (S/N)"

if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Desabilitando MFA..." -ForegroundColor Yellow

# Executar SQL no PostgreSQL
docker-compose exec -T postgres psql -U coruja -d coruja_monitor -c "UPDATE users SET mfa_enabled = FALSE, mfa_secret = NULL, mfa_backup_codes = NULL;"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  MFA DESABILITADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Agora você pode fazer login normalmente sem código MFA." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Para habilitar MFA novamente:" -ForegroundColor Yellow
    Write-Host "1. Faça login no sistema" -ForegroundColor White
    Write-Host "2. Vá em Configurações > Segurança > MFA" -ForegroundColor White
    Write-Host "3. Clique em 'Habilitar MFA'" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERRO] Falha ao desabilitar MFA" -ForegroundColor Red
    Write-Host "Verifique se o container PostgreSQL está rodando:" -ForegroundColor Yellow
    Write-Host "  docker ps | findstr postgres" -ForegroundColor White
    Write-Host ""
}
