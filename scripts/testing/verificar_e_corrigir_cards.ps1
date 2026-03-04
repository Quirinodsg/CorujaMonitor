# Script para verificar Docker e corrigir cards de categorias
Write-Host "=== VERIFICACAO E CORRECAO DE CARDS ===" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker Desktop está rodando
Write-Host "1. Verificando Docker Desktop..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    docker ps | Out-Null
    $dockerRunning = $true
    Write-Host "   ✓ Docker Desktop está rodando" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Docker Desktop NÃO está rodando" -ForegroundColor Red
    Write-Host ""
    Write-Host "ACAO NECESSARIA:" -ForegroundColor Yellow
    Write-Host "1. Abra o Docker Desktop manualmente" -ForegroundColor White
    Write-Host "2. Aguarde até que o Docker esteja completamente iniciado" -ForegroundColor White
    Write-Host "3. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    Read-Host "Pressione ENTER para sair"
    exit 1
}

Write-Host ""
Write-Host "2. Verificando containers..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "3. Fazendo rebuild do frontend (sem cache)..." -ForegroundColor Yellow
Write-Host "   Isso pode levar alguns minutos..." -ForegroundColor Gray
docker-compose build --no-cache frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Rebuild concluído com sucesso" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro no rebuild" -ForegroundColor Red
    Read-Host "Pressione ENTER para sair"
    exit 1
}

Write-Host ""
Write-Host "4. Reiniciando container frontend..." -ForegroundColor Yellow
docker-compose restart frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Frontend reiniciado" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro ao reiniciar" -ForegroundColor Red
    Read-Host "Pressione ENTER para sair"
    exit 1
}

Write-Host ""
Write-Host "=== CORRECAO CONCLUIDA ===" -ForegroundColor Green
Write-Host ""
Write-Host "PROXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Abra o navegador em: http://localhost:3000" -ForegroundColor White
Write-Host "2. Pressione Ctrl+Shift+R para limpar o cache" -ForegroundColor White
Write-Host "3. Va para a pagina Servidores" -ForegroundColor White
Write-Host "4. Verifique se os cards de categorias estao alinhados" -ForegroundColor White
Write-Host ""
Write-Host "Se ainda estiver com problema:" -ForegroundColor Yellow
Write-Host "- Abra uma aba anonima (Ctrl+Shift+N)" -ForegroundColor White
Write-Host "- Teste novamente" -ForegroundColor White
Write-Host ""

Read-Host "Pressione ENTER para sair"
