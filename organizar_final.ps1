# Script para organização FINAL do repositório
# Move TODOS os arquivos markdown restantes para docs/changelog/04MAR/
# Data: 04 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ORGANIZAÇÃO FINAL DO REPOSITÓRIO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar pasta de destino se não existir
$destFolder = "docs/changelog/04MAR"
if (-not (Test-Path $destFolder)) {
    New-Item -ItemType Directory -Path $destFolder -Force | Out-Null
}

# Arquivos que devem permanecer na raiz
$keepInRoot = @(
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "LICENSE"
)

# Obter todos os arquivos .md na raiz (exceto os que devem ficar)
$mdFiles = Get-ChildItem -Path . -File -Filter "*.md" | Where-Object {
    $keepInRoot -notcontains $_.Name
}

Write-Host "Arquivos markdown encontrados na raiz: $($mdFiles.Count)" -ForegroundColor Yellow
Write-Host ""

if ($mdFiles.Count -eq 0) {
    Write-Host "Nenhum arquivo para mover. Repositório já está organizado!" -ForegroundColor Green
    exit 0
}

Write-Host "Movendo arquivos para: $destFolder" -ForegroundColor Yellow
Write-Host ""

$movedCount = 0
$errorCount = 0

foreach ($file in $mdFiles) {
    try {
        $destPath = Join-Path $destFolder $file.Name
        
        # Usar git mv para preservar histórico
        git mv $file.Name $destPath 2>&1 | Out-Null
        
        Write-Host "[OK] $($file.Name)" -ForegroundColor Green
        $movedCount++
    }
    catch {
        Write-Host "[ERRO] $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Arquivos movidos: $movedCount" -ForegroundColor Green
if ($errorCount -gt 0) {
    Write-Host "Erros: $errorCount" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mover também os scripts temporários
Write-Host "Movendo scripts temporários..." -ForegroundColor Yellow
$tempScripts = @(
    "organizar_repositorio.ps1",
    "organizar_restante.ps1",
    "corrigir_cards_definitivo.ps1"
)

foreach ($script in $tempScripts) {
    if (Test-Path $script) {
        $destPath = Join-Path $destFolder $script
        git mv $script $destPath 2>&1 | Out-Null
        Write-Host "[OK] $script" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Verificando arquivos restantes na raiz..." -ForegroundColor Yellow
$remaining = Get-ChildItem -Path . -File -Filter "*.md" | Where-Object {
    $keepInRoot -notcontains $_.Name
}

if ($remaining.Count -eq 0) {
    Write-Host "[OK] Nenhum arquivo markdown solto na raiz!" -ForegroundColor Green
} else {
    Write-Host "[AVISO] Ainda há $($remaining.Count) arquivos na raiz:" -ForegroundColor Yellow
    $remaining | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "1. git status (verificar mudanças)"
Write-Host "2. git commit -m 'docs: Organização final - move todos arquivos para docs/changelog/04MAR'"
Write-Host "3. git push origin master"
Write-Host "========================================" -ForegroundColor Cyan
