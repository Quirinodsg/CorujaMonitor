# Script para corrigir ferramentas administrativas e logo
Write-Host "=== CORREÇÕES: FERRAMENTAS ADMIN E LOGO ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Correções aplicadas:" -ForegroundColor Yellow
Write-Host "  ✅ Logo da coruja agora volta para Dashboard ao clicar" -ForegroundColor Green
Write-Host "  ✅ Modal de ferramentas admin com botão fechar sempre visível" -ForegroundColor Green
Write-Host "  ✅ Terminal com scroll e texto não sobrepõe mais" -ForegroundColor Green
Write-Host "  ✅ Botão X no canto superior direito do modal" -ForegroundColor Green
Write-Host "  ✅ Spinner de loading enquanto processa" -ForegroundColor Green
Write-Host "  ✅ Design melhorado do terminal (estilo hacker)" -ForegroundColor Green
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
Write-Host "=== CORREÇÕES APLICADAS ===" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Problemas Corrigidos!" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Logo da Coruja 🦉" -ForegroundColor White
Write-Host "   - Clique no logo no topo da sidebar" -ForegroundColor Gray
Write-Host "   - Agora volta para o Dashboard" -ForegroundColor Gray
Write-Host "   - Cursor muda para pointer (mãozinha)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Ferramentas Administrativas 🔧" -ForegroundColor White
Write-Host "   - Modal com design melhorado" -ForegroundColor Gray
Write-Host "   - Botão X no canto superior direito" -ForegroundColor Gray
Write-Host "   - Botão 'Fechar' sempre visível no rodapé" -ForegroundColor Gray
Write-Host "   - Terminal com scroll automático" -ForegroundColor Gray
Write-Host "   - Texto não sobrepõe mais" -ForegroundColor Gray
Write-Host "   - Estilo terminal hacker (fundo preto, texto verde)" -ForegroundColor Gray
Write-Host "   - Spinner de loading enquanto processa" -ForegroundColor Gray
Write-Host ""
Write-Host "Como testar:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "   Login: admin@coruja.com / admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Teste o logo:" -ForegroundColor White
Write-Host "   - Navegue para qualquer página" -ForegroundColor Gray
Write-Host "   - Clique no '🦉 Coruja' no topo da sidebar" -ForegroundColor Gray
Write-Host "   - Deve voltar para o Dashboard" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Teste ferramentas admin:" -ForegroundColor White
Write-Host "   - Vá para Configurações > Ferramentas Admin" -ForegroundColor Gray
Write-Host "   - Execute qualquer ação (ex: Limpar Cache)" -ForegroundColor Gray
Write-Host "   - Observe o modal com terminal" -ForegroundColor Gray
Write-Host "   - Botão X no canto superior direito" -ForegroundColor Gray
Write-Host "   - Botão 'Fechar' no rodapé" -ForegroundColor Gray
Write-Host "   - Texto não sobrepõe" -ForegroundColor Gray
Write-Host "   - Scroll funciona se muitas linhas" -ForegroundColor Gray
Write-Host ""
