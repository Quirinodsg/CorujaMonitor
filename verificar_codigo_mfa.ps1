# ========================================
# Verificar Código MFA
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICAR CÓDIGO MFA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Este script irá mostrar o código MFA atual do servidor." -ForegroundColor Yellow
Write-Host "Compare com o código no seu Google Authenticator." -ForegroundColor Yellow
Write-Host ""

# Executar teste
docker cp testar_mfa_totp.py coruja-api:/app/testar_mfa_totp.py 2>$null
docker-compose exec -T api python testar_mfa_totp.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMO RESOLVER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Se o código no Google Authenticator for DIFERENTE:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. REMOVA a conta 'CorujaMonitor' do Google Authenticator" -ForegroundColor White
Write-Host "2. Vá em Configurações > Segurança > MFA" -ForegroundColor White
Write-Host "3. Clique em 'Desabilitar MFA'" -ForegroundColor White
Write-Host "4. Clique em 'Habilitar MFA' novamente" -ForegroundColor White
Write-Host "5. Escaneie o NOVO QR Code" -ForegroundColor White
Write-Host "6. Teste o login" -ForegroundColor White
Write-Host ""

Write-Host "Se o código for IGUAL mas não funciona:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Verifique se o relógio do smartphone está sincronizado" -ForegroundColor White
Write-Host "2. Aguarde o código mudar (30 segundos)" -ForegroundColor White
Write-Host "3. Tente novamente com o novo código" -ForegroundColor White
Write-Host "4. Se não funcionar, use um código de backup" -ForegroundColor White
Write-Host ""
