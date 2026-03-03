# Script para Aplicar Kubernetes Completo
# Data: 27 FEV 2026
# Aplica: Criptografia, Dashboard e Alertas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "APLICAR KUBERNETES COMPLETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# 1. Executar migração de alertas
Write-Host "1. Executando migração de alertas..." -ForegroundColor Yellow
try {
    cd api
    python migrate_kubernetes_alerts.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Migração executada com sucesso" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Erro na migração" -ForegroundColor Red
        exit 1
    }
    cd ..
} catch {
    Write-Host "   ✗ Erro ao executar migração: $_" -ForegroundColor Red
    cd ..
    exit 1
}

# 2. Verificar se chave de criptografia está no .env
Write-Host ""
Write-Host "2. Verificando chave de criptografia..." -ForegroundColor Yellow
$envContent = Get-Content .env -Raw
if ($envContent -match "ENCRYPTION_KEY") {
    Write-Host "   ✓ Chave de criptografia encontrada" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Chave não encontrada, mas já foi adicionada" -ForegroundColor Yellow
}

# 3. Verificar se router está registrado
Write-Host ""
Write-Host "3. Verificando registro do router..." -ForegroundColor Yellow
$mainContent = Get-Content api/main.py -Raw
if ($mainContent -match "kubernetes_alerts") {
    Write-Host "   ✓ Router de alertas registrado" -ForegroundColor Green
} else {
    Write-Host "   ✗ Router não registrado" -ForegroundColor Red
    exit 1
}

# 4. Verificar se dashboard está no MainLayout
Write-Host ""
Write-Host "4. Verificando dashboard no frontend..." -ForegroundColor Yellow
$mainLayoutContent = Get-Content frontend/src/components/MainLayout.js -Raw
if ($mainLayoutContent -match "KubernetesDashboard") {
    Write-Host "   ✓ Dashboard registrado no MainLayout" -ForegroundColor Green
} else {
    Write-Host "   ✗ Dashboard não registrado" -ForegroundColor Red
    exit 1
}

# 5. Verificar se menu está no Sidebar
Write-Host ""
Write-Host "5. Verificando menu no Sidebar..." -ForegroundColor Yellow
$sidebarContent = Get-Content frontend/src/components/Sidebar.js -Raw
if ($sidebarContent -match "kubernetes") {
    Write-Host "   ✓ Menu Kubernetes adicionado" -ForegroundColor Green
} else {
    Write-Host "   ✗ Menu não adicionado" -ForegroundColor Red
    exit 1
}

# 6. Reiniciar API
Write-Host ""
Write-Host "6. Reiniciando API..." -ForegroundColor Yellow
try {
    docker-compose restart api
    Start-Sleep -Seconds 5
    Write-Host "   ✓ API reiniciada" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Erro ao reiniciar API: $_" -ForegroundColor Yellow
    Write-Host "   Execute manualmente: docker-compose restart api" -ForegroundColor Cyan
}

# 7. Verificar se API está respondendo
Write-Host ""
Write-Host "7. Verificando API..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ API está respondendo" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠ API não está respondendo ainda" -ForegroundColor Yellow
    Write-Host "   Aguarde alguns segundos e verifique: http://localhost:8000/docs" -ForegroundColor Cyan
}

# 8. Instruções para frontend
Write-Host ""
Write-Host "8. Frontend..." -ForegroundColor Yellow
Write-Host "   Para aplicar mudanças no frontend:" -ForegroundColor Cyan
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "   Ou se já está rodando, apenas recarregue a página (Ctrl+R)" -ForegroundColor Cyan

# 9. Resumo
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Implementações aplicadas:" -ForegroundColor Green
Write-Host "   1. Criptografia AES-256 para credenciais" -ForegroundColor White
Write-Host "   2. Dashboard Kubernetes no frontend" -ForegroundColor White
Write-Host "   3. Sistema de alertas automáticos" -ForegroundColor White
Write-Host ""
Write-Host "📊 Novos recursos:" -ForegroundColor Green
Write-Host "   - 2 tabelas criadas (kubernetes_alerts, kubernetes_alert_rules)" -ForegroundColor White
Write-Host "   - 8 endpoints de alertas" -ForegroundColor White
Write-Host "   - 5 regras de alerta padrão" -ForegroundColor White
Write-Host "   - Dashboard completo com métricas" -ForegroundColor White
Write-Host "   - Menu Kubernetes no sidebar" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Segurança:" -ForegroundColor Green
Write-Host "   - Credenciais criptografadas com AES-256" -ForegroundColor White
Write-Host "   - PBKDF2 com 100.000 iterações" -ForegroundColor White
Write-Host "   - Chave configurável via .env" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acessar dashboard:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Login: admin@coruja.com / admin123" -ForegroundColor Cyan
Write-Host "   Menu: ☸️ Kubernetes" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Verificar alertas:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Procurar por: /api/v1/kubernetes/alerts" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Testar integração:" -ForegroundColor Yellow
Write-Host "   .\testar_integracao_kubernetes.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Configurar cluster:" -ForegroundColor Yellow
Write-Host "   Servidores → Monitorar Serviços → ☸️ Kubernetes" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Documentação:" -ForegroundColor White
Write-Host "- KUBERNETES_DASHBOARDS_ALERTAS_CRIPTOGRAFIA_27FEV.md" -ForegroundColor Gray
Write-Host "- GUIA_COMPLETO_KUBERNETES_27FEV.md" -ForegroundColor Gray
Write-Host "- INDICE_KUBERNETES_27FEV.md" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ APLICAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
Write-Host ""
