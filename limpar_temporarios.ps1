# Script para limpar arquivos temporários após organização
# Data: 04 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LIMPEZA DE ARQUIVOS TEMPORÁRIOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Arquivos temporários para deletar
$tempFiles = @(
    "organizar_repositorio.ps1",
    "organizar_restante.ps1",
    "corrigir_cards_definitivo.ps1",
    "verificar_screenshots.ps1"
)

Write-Host "Arquivos temporários a serem removidos:" -ForegroundColor Yellow
foreach ($file in $tempFiles) {
    if (Test-Path $file) {
        Write-Host "  [X] $file" -ForegroundColor Red
    } else {
        Write-Host "  [ ] $file (já removido)" -ForegroundColor Gray
    }
}

Write-Host ""
$confirm = Read-Host "Deseja remover estes arquivos? (S/N)"

if ($confirm -eq "S" -or $confirm -eq "s") {
    Write-Host ""
    Write-Host "Removendo arquivos..." -ForegroundColor Yellow
    
    foreach ($file in $tempFiles) {
        if (Test-Path $file) {
            git rm $file
            Write-Host "  [OK] Removido: $file" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "Arquivos removidos com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. git commit -m 'chore: Remove scripts temporários de organização'"
    Write-Host "2. git push origin master"
} else {
    Write-Host ""
    Write-Host "Operação cancelada." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
