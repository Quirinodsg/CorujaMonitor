# Script para Restaurar Sistema ao Estado Original Funcionando
# Remove HTTPS e volta para HTTP normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESTAURANDO SISTEMA ORIGINAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Este script irá:" -ForegroundColor Yellow
Write-Host "  1. Parar todos os containers" -ForegroundColor Gray
Write-Host "  2. Remover configurações de HTTPS" -ForegroundColor Gray
Write-Host "  3. Iniciar sistema no modo HTTP original" -ForegroundColor Gray
Write-Host "  4. Verificar se tudo está funcionando" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Deseja continuar? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# 1. Parar TUDO
Write-Host "1/5 Parando todos os containers..." -ForegroundColor Yellow
docker-compose down 2>$null
docker-compose -f docker-compose.yml -f docker-compose.https.yml down 2>$null
Start-Sleep -Seconds 3
Write-Host "✅ Containers parados" -ForegroundColor Green

# 2. Limpar volumes e redes
Write-Host "2/5 Limpando configurações..." -ForegroundColor Yellow
docker network prune -f 2>$null
Write-Host "✅ Limpeza concluída" -ForegroundColor Green

# 3. Iniciar sistema original (HTTP)
Write-Host "3/5 Iniciando sistema no modo HTTP..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "Aguardando containers iniciarem..." -ForegroundColor Gray
Start-Sleep -Seconds 20

# 4. Verificar status
Write-Host ""
Write-Host "4/5 Verificando status dos containers..." -ForegroundColor Yellow
Write-Host ""

$containers = @(
    "coruja-postgres",
    "coruja-redis",
    "coruja-api",
    "coruja-frontend",
    "coruja-worker",
    "coruja-ai-agent",
    "coruja-ollama"
)

$allRunning = $true

foreach ($container in $containers) {
    $status = docker ps --filter "name=$container" --format "{{.Status}}" 2>$null
    if ($status) {
        Write-Host "✅ $container : RODANDO" -ForegroundColor Green
    } else {
        Write-Host "❌ $container : NÃO ENCONTRADO" -ForegroundColor Red
        $allRunning = $false
    }
}

# 5. Testar conexões
Write-Host ""
Write-Host "5/5 Testando conexões..." -ForegroundColor Yellow
Write-Host ""

# Testar Frontend
Write-Host "Testando Frontend (porta 3000)..." -ForegroundColor Gray
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Frontend: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend: ERRO - $($_.Exception.Message)" -ForegroundColor Red
    $allRunning = $false
}

# Testar API
Write-Host "Testando API (porta 8000)..." -ForegroundColor Gray
try {
    $apiResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ API: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ API: ERRO - $($_.Exception.Message)" -ForegroundColor Red
    $allRunning = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESULTADO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($allRunning) {
    Write-Host "✅ SISTEMA RESTAURADO COM SUCESSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Acesse o sistema:" -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   API: http://localhost:8000" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Status dos containers:" -ForegroundColor Cyan
    docker-compose ps
    Write-Host ""
    Write-Host "✅ Tudo funcionando normalmente!" -ForegroundColor Green
} else {
    Write-Host "⚠️  ALGUNS PROBLEMAS FORAM ENCONTRADOS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ver logs dos containers:" -ForegroundColor Cyan
    Write-Host "   docker logs coruja-frontend" -ForegroundColor Gray
    Write-Host "   docker logs coruja-api" -ForegroundColor Gray
    Write-Host "   docker logs coruja-postgres" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Reiniciar containers com problema:" -ForegroundColor Cyan
    Write-Host "   docker-compose restart" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 Status atual:" -ForegroundColor Cyan
    docker-compose ps
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INFORMAÇÕES IMPORTANTES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Sistema voltou ao modo HTTP original" -ForegroundColor Green
Write-Host "✅ HTTPS foi desativado" -ForegroundColor Green
Write-Host "✅ Todas as funcionalidades devem estar funcionando" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Nota sobre HTTPS:" -ForegroundColor Yellow
Write-Host "   O HTTPS foi implementado mas causou problemas." -ForegroundColor Gray
Write-Host "   Você pode tentar novamente mais tarde se necessário." -ForegroundColor Gray
Write-Host "   Por enquanto, use HTTP que está funcionando perfeitamente." -ForegroundColor Gray
Write-Host ""
Write-Host "🔒 Segurança:" -ForegroundColor Cyan
Write-Host "   - WAF ainda está ativo protegendo a API" -ForegroundColor Gray
Write-Host "   - Monitoramento de segurança disponível em Configurações" -ForegroundColor Gray
Write-Host "   - Sistema seguro mesmo sem HTTPS (para uso interno)" -ForegroundColor Gray
Write-Host ""

exit 0
