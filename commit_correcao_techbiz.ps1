# Script PowerShell para commit da correção Techbiz

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMMIT: Correção Techbiz + Scripts" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Caminho do Git
$gitPath = "C:\Program Files\Git\bin\git.exe"

if (!(Test-Path $gitPath)) {
    Write-Host "Git não encontrado em: $gitPath" -ForegroundColor Red
    Write-Host "Procurando Git..." -ForegroundColor Yellow
    
    # Tentar outros caminhos comuns
    $possiblePaths = @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files (x86)\Git\bin\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $gitPath = $path
            Write-Host "Git encontrado em: $gitPath" -ForegroundColor Green
            break
        }
    }
    
    if (!(Test-Path $gitPath)) {
        Write-Host "ERRO: Git não encontrado!" -ForegroundColor Red
        Write-Host "Instale o Git ou use Git Bash" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Usando Git: $gitPath" -ForegroundColor Green
Write-Host ""

# Adicionar arquivos
Write-Host "1. Adicionando arquivos..." -ForegroundColor Yellow
& $gitPath add frontend/src/config.js
& $gitPath add rebuild_frontend_completo_linux.sh
& $gitPath add commit_final_techbiz.sh
& $gitPath add commit_correcao_techbiz.ps1
& $gitPath add RESUMO_FINAL_PROBLEMA_TECHBIZ.md
& $gitPath add LIMPAR_CACHE_AGRESSIVO.txt
& $gitPath add excluir_techbiz_direto.sh
& $gitPath add LEIA_ISTO_AGORA.txt
& $gitPath add SOLUCAO_DEFINITIVA.txt
& $gitPath add gerar_msi_com_ui.ps1

Write-Host "   ✓ Arquivos adicionados" -ForegroundColor Green

# Commit
Write-Host ""
Write-Host "2. Fazendo commit..." -ForegroundColor Yellow
& $gitPath commit -m "fix: Correção completa Techbiz + CACHE_VERSION v4.0-REBUILD + MSI com UI

- Aumentado CACHE_VERSION para v4.0-REBUILD para forçar atualização
- Script rebuild_frontend_completo_linux.sh para rebuild total
- Script gerar_msi_com_ui.ps1 com WiX 3.11 para MSI com interface gráfica
- Documentação completa do problema e soluções
- Problema: Imagem Docker do frontend com código antigo
- Solução: Rebuild completo + cache busting no config.js"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Commit realizado" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro no commit" -ForegroundColor Red
    exit 1
}

# Push
Write-Host ""
Write-Host "3. Enviando para GitHub..." -ForegroundColor Yellow
& $gitPath push origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Push realizado" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro no push" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tente manualmente:" -ForegroundColor Yellow
    Write-Host "git push origin master" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "COMMIT CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "NO SERVIDOR LINUX, execute:" -ForegroundColor Yellow
Write-Host ""
Write-Host "cd ~/CorujaMonitor" -ForegroundColor White
Write-Host "git pull origin master" -ForegroundColor White
Write-Host "chmod +x rebuild_frontend_completo_linux.sh" -ForegroundColor White
Write-Host "./rebuild_frontend_completo_linux.sh" -ForegroundColor White
Write-Host ""
Write-Host "Aguarde 3-5 minutos para rebuild completar" -ForegroundColor Cyan
Write-Host "Depois acesse em aba anônima: http://192.168.31.161:3000" -ForegroundColor Cyan
Write-Host ""
