# Script para commit da organização final
# Data: 04 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMMIT DA ORGANIZAÇÃO FINAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Git está instalado
$gitPath = Get-Command git -ErrorAction SilentlyContinue

if (-not $gitPath) {
    Write-Host "[ERRO] Git não encontrado no PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Soluções:" -ForegroundColor Yellow
    Write-Host "1. Instale o Git: https://git-scm.com/download/win"
    Write-Host "2. Ou use o Git Bash manualmente"
    Write-Host "3. Ou adicione o Git ao PATH do sistema"
    Write-Host ""
    Write-Host "Comandos manuais:" -ForegroundColor Cyan
    Write-Host "  git add -A"
    Write-Host "  git commit -m 'docs: Organização final - move 126 arquivos para docs/changelog/04MAR'"
    Write-Host "  git push origin master"
    exit 1
}

Write-Host "Git encontrado: $($gitPath.Source)" -ForegroundColor Green
Write-Host ""

# Verificar status
Write-Host "Verificando mudanças..." -ForegroundColor Yellow
$status = & git status --short
$changesCount = ($status | Measure-Object).Count

Write-Host "Mudanças detectadas: $changesCount arquivos" -ForegroundColor Cyan
Write-Host ""

if ($changesCount -eq 0) {
    Write-Host "Nenhuma mudança para commitar!" -ForegroundColor Yellow
    exit 0
}

# Mostrar resumo
Write-Host "Resumo das mudanças:" -ForegroundColor Yellow
& git status --short | Select-Object -First 10
if ($changesCount -gt 10) {
    Write-Host "... e mais $($changesCount - 10) arquivos" -ForegroundColor Gray
}
Write-Host ""

# Confirmar
$confirm = Read-Host "Deseja fazer o commit e push? (S/N)"

if ($confirm -eq "S" -or $confirm -eq "s") {
    Write-Host ""
    Write-Host "Adicionando arquivos ao stage..." -ForegroundColor Yellow
    & git add -A
    
    Write-Host "Fazendo commit..." -ForegroundColor Yellow
    & git commit -m "docs: Organização final - move 126 arquivos para docs/changelog/04MAR"
    
    Write-Host "Enviando para GitHub..." -ForegroundColor Yellow
    & git push origin master
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "SUCESSO!" -ForegroundColor Green
    Write-Host "Organização enviada para o GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para commitar manualmente:" -ForegroundColor Cyan
    Write-Host "  git add -A"
    Write-Host "  git commit -m 'docs: Organização final - move 126 arquivos para docs/changelog/04MAR'"
    Write-Host "  git push origin master"
}

Write-Host ""
