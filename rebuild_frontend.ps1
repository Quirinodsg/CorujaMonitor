# Script para rebuild do frontend com novas integrações
# Data: 04 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REBUILD DO FRONTEND" -ForegroundColor Cyan
Write-Host "  Novas Integrações: Dynamics 365" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
Write-Host "1️⃣ Verificando Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "   ✅ Docker está rodando" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker não está rodando!" -ForegroundColor Red
    Write-Host "   Inicie o Docker Desktop e tente novamente." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "2️⃣ Parando containers..." -ForegroundColor Yellow
docker-compose down
Write-Host "   ✅ Containers parados" -ForegroundColor Green

Write-Host ""
Write-Host "3️⃣ Rebuilding frontend..." -ForegroundColor Yellow
Write-Host "   ⏳ Isso pode levar 2-3 minutos..." -ForegroundColor Gray
docker-compose build frontend
Write-Host "   ✅ Frontend rebuilded" -ForegroundColor Green

Write-Host ""
Write-Host "4️⃣ Iniciando containers..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "   ✅ Containers iniciados" -ForegroundColor Green

Write-Host ""
Write-Host "5️⃣ Aguardando inicialização..." -ForegroundColor Yellow
Write-Host "   ⏳ Aguarde 30 segundos..." -ForegroundColor Gray
Start-Sleep -Seconds 30
Write-Host "   ✅ Sistema pronto!" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ REBUILD CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "2. Login: admin@coruja.com / admin123" -ForegroundColor White
Write-Host "3. Vá para: Configurações → Integrações" -ForegroundColor White
Write-Host "4. Role até o final da página" -ForegroundColor White
Write-Host "5. Você verá: 🏢 Microsoft Dynamics 365 CRM" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   Limpe o cache do navegador (Ctrl + Shift + R)" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
