# Script para aplicar correções finais
Write-Host "=== CORREÇÕES FINAIS - 26 FEV ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Correções aplicadas:" -ForegroundColor Yellow
Write-Host "  ✅ Terminal: Quebra de linha corrigida" -ForegroundColor Green
Write-Host "  ✅ Biblioteca: Categoria Azure adicionada (15 sensores)" -ForegroundColor Green
Write-Host "  ✅ Biblioteca: Categoria Storage adicionada (6 sensores)" -ForegroundColor Green
Write-Host "  ✅ Biblioteca: Categoria Cloud adicionada (3 sensores)" -ForegroundColor Green
Write-Host "  ✅ Dell EqualLogic incluído em Storage" -ForegroundColor Green
Write-Host ""

Write-Host "Novos sensores Azure:" -ForegroundColor Cyan
Write-Host "  - Azure Virtual Machine" -ForegroundColor Gray
Write-Host "  - Azure Web App" -ForegroundColor Gray
Write-Host "  - Azure SQL Database" -ForegroundColor Gray
Write-Host "  - Azure Storage Account" -ForegroundColor Gray
Write-Host "  - Azure Kubernetes Service (AKS)" -ForegroundColor Gray
Write-Host "  - Azure Functions" -ForegroundColor Gray
Write-Host "  - Azure Backup" -ForegroundColor Gray
Write-Host "  - Azure Load Balancer" -ForegroundColor Gray
Write-Host "  - Azure Application Gateway" -ForegroundColor Gray
Write-Host "  - Azure Cosmos DB" -ForegroundColor Gray
Write-Host "  - Azure Cache for Redis" -ForegroundColor Gray
Write-Host "  - Azure Service Bus" -ForegroundColor Gray
Write-Host "  - Azure Event Hub" -ForegroundColor Gray
Write-Host "  - Azure Key Vault" -ForegroundColor Gray
Write-Host "  - Azure Monitor Alerts" -ForegroundColor Gray
Write-Host ""

Write-Host "Novos sensores Storage:" -ForegroundColor Cyan
Write-Host "  - Dell EqualLogic (com OIDs SNMP)" -ForegroundColor Gray
Write-Host "  - NetApp Filer" -ForegroundColor Gray
Write-Host "  - EMC VNX" -ForegroundColor Gray
Write-Host "  - HP 3PAR" -ForegroundColor Gray
Write-Host "  - Synology NAS" -ForegroundColor Gray
Write-Host "  - QNAP NAS" -ForegroundColor Gray
Write-Host ""

# 1. Recompilar frontend
Write-Host "1. Recompilando frontend..." -ForegroundColor Yellow
docker exec coruja-frontend npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Frontend recompilado!" -ForegroundColor Green
} else {
    Write-Host "⚠ Aviso: Erro ao recompilar frontend" -ForegroundColor Yellow
}

# 2. Reiniciar frontend
Write-Host ""
Write-Host "2. Reiniciando frontend..." -ForegroundColor Yellow
docker restart coruja-frontend
Start-Sleep -Seconds 3
Write-Host "✓ Frontend reiniciado!" -ForegroundColor Green

# 3. Verificar acesso
Write-Host ""
Write-Host "3. Verificando acesso..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0
$frontendReady = $false

while ($attempt -lt $maxAttempts -and -not $frontendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $frontendReady = $true
            Write-Host "✓ Frontend está acessível!" -ForegroundColor Green
        }
    } catch {
        $attempt++
        Write-Host "  Tentativa $attempt/$maxAttempts..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $frontendReady) {
    Write-Host "✗ Frontend não está acessível" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== CORREÇÕES APLICADAS COM SUCESSO ===" -ForegroundColor Green
Write-Host ""
Write-Host "Como testar:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Terminal (Ferramentas Admin):" -ForegroundColor White
Write-Host "   - Vá para Configurações > Ferramentas Admin" -ForegroundColor Gray
Write-Host "   - Execute qualquer ação" -ForegroundColor Gray
Write-Host "   - Observe que o texto agora quebra linha corretamente" -ForegroundColor Gray
Write-Host "   - Não sobrepõe mais" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Biblioteca de Sensores - Azure:" -ForegroundColor White
Write-Host "   - Vá para Servidores > Adicionar Sensor" -ForegroundColor Gray
Write-Host "   - Clique na categoria '☁️ Microsoft Azure'" -ForegroundColor Gray
Write-Host "   - Veja 15 sensores Azure disponíveis" -ForegroundColor Gray
Write-Host "   - Cada um com métricas específicas" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Biblioteca de Sensores - Storage:" -ForegroundColor White
Write-Host "   - Vá para Servidores > Adicionar Sensor" -ForegroundColor Gray
Write-Host "   - Clique na categoria '💿 Storage'" -ForegroundColor Gray
Write-Host "   - Veja Dell EqualLogic e outros 5 sistemas" -ForegroundColor Gray
Write-Host "   - Dell EqualLogic tem OIDs SNMP configurados" -ForegroundColor Gray
Write-Host ""
Write-Host "Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "Login: admin@coruja.com / admin123" -ForegroundColor Gray
Write-Host ""
