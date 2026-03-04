# Script para aplicar design melhorado dos relatórios
Write-Host "=== APLICANDO DESIGN MELHORADO - RELATÓRIOS ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Melhorias aplicadas:" -ForegroundColor Yellow
Write-Host "  ✅ Removidos templates pré-definidos" -ForegroundColor Green
Write-Host "  ✅ Foco em relatórios personalizados do usuário" -ForegroundColor Green
Write-Host "  ✅ Botões de ação compactos e elegantes" -ForegroundColor Green
Write-Host "  ✅ Header com ações no relatório gerado" -ForegroundColor Green
Write-Host "  ✅ Estado vazio com call-to-action" -ForegroundColor Green
Write-Host "  ✅ Loading com spinner animado" -ForegroundColor Green
Write-Host "  ✅ Design responsivo melhorado" -ForegroundColor Green
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
Write-Host "=== DESIGN MELHORADO APLICADO ===" -ForegroundColor Green
Write-Host ""
Write-Host "🎨 Novo Design dos Relatórios!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Principais mudanças:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Sidebar Simplificada" -ForegroundColor White
Write-Host "   - Apenas 'Meus Relatórios Personalizados'" -ForegroundColor Gray
Write-Host "   - Botões compactos de editar (✏️) e excluir (🗑️)" -ForegroundColor Gray
Write-Host "   - Design mais limpo e organizado" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Header do Relatório" -ForegroundColor White
Write-Host "   - Título e descrição destacados" -ForegroundColor Gray
Write-Host "   - Botões de ação no topo (Editar, Excluir, Imprimir)" -ForegroundColor Gray
Write-Host "   - Gradiente roxo moderno" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Estado Vazio" -ForegroundColor White
Write-Host "   - Ícone animado flutuante" -ForegroundColor Gray
Write-Host "   - Mensagem de boas-vindas" -ForegroundColor Gray
Write-Host "   - Botão grande 'Criar Meu Primeiro Relatório'" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Loading" -ForegroundColor White
Write-Host "   - Spinner animado" -ForegroundColor Gray
Write-Host "   - Mensagem clara" -ForegroundColor Gray
Write-Host ""
Write-Host "Como usar:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acesse: http://localhost:3000" -ForegroundColor White
Write-Host "   Login: admin@coruja.com / admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Vá para 'Relatórios'" -ForegroundColor White
Write-Host ""
Write-Host "3. Se não tiver relatórios:" -ForegroundColor White
Write-Host "   - Clique em 'Criar Meu Primeiro Relatório'" -ForegroundColor Gray
Write-Host "   - Preencha o formulário" -ForegroundColor Gray
Write-Host "   - Salve" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Gerenciar relatórios:" -ForegroundColor White
Write-Host "   - Clique no relatório para visualizar" -ForegroundColor Gray
Write-Host "   - Use ✏️ para editar" -ForegroundColor Gray
Write-Host "   - Use 🗑️ para excluir" -ForegroundColor Gray
Write-Host "   - Use botões no header quando relatório estiver aberto" -ForegroundColor Gray
Write-Host ""
