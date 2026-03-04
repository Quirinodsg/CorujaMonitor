#!/usr/bin/env pwsh
# Script para abrir o Coruja Monitor e facilitar testes

Write-Host "🦉 Coruja Monitor - Abertura Rápida" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se containers estão rodando
Write-Host "📋 Verificando status dos containers..." -ForegroundColor Yellow
$containers = docker-compose ps --format json 2>$null | ConvertFrom-Json

if ($containers) {
    Write-Host "✅ Containers encontrados:" -ForegroundColor Green
    foreach ($container in $containers) {
        $status = if ($container.State -eq "running") { "🟢 RODANDO" } else { "🔴 PARADO" }
        Write-Host "   - $($container.Service): $status" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  Nenhum container encontrado. Iniciando sistema..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep -Seconds 10
}

Write-Host ""
Write-Host "🌐 Abrindo navegador..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📍 URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host "👤 Login: admin@coruja.com" -ForegroundColor Cyan
Write-Host "🔑 Senha: admin123" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Para testar a nova aba de Segurança:" -ForegroundColor Green
Write-Host "   1. Faça login" -ForegroundColor White
Write-Host "   2. Clique em 'Configurações' no menu lateral" -ForegroundColor White
Write-Host "   3. Clique na aba '🔐 Segurança'" -ForegroundColor White
Write-Host ""

# Aguardar 3 segundos para garantir que o frontend está pronto
Write-Host "⏳ Aguardando frontend inicializar (3 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Abrir navegador
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ Navegador aberto!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Documentação disponível:" -ForegroundColor Cyan
Write-Host "   - TESTE_SEGURANCA_RAPIDO.md (guia de teste)" -ForegroundColor White
Write-Host "   - IMPLEMENTACAO_SEGURANCA_AUTH_04MAR.md (documentação completa)" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Comandos úteis:" -ForegroundColor Cyan
Write-Host "   - Ver logs API: docker-compose logs api --tail 50" -ForegroundColor White
Write-Host "   - Ver logs Frontend: docker-compose logs frontend --tail 50" -ForegroundColor White
Write-Host "   - Reiniciar: docker-compose restart api frontend" -ForegroundColor White
Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
