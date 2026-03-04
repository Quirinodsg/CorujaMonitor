# Script para verificar se os screenshots estão prontos para commit
# Data: 04 de Março de 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICADOR DE SCREENSHOTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$screenshotsPath = "docs\screenshots"
$requiredFiles = @(
    "dashboard.png",
    "noc.png",
    "metrics.png",
    "aiops.png"
)

Write-Host "Verificando pasta: $screenshotsPath" -ForegroundColor Yellow
Write-Host ""

$allFilesPresent = $true
$totalSize = 0

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $screenshotsPath $file
    
    if (Test-Path $filePath) {
        $fileInfo = Get-Item $filePath
        $sizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
        $totalSize += $fileInfo.Length
        
        Write-Host "[OK]" -ForegroundColor Green -NoNewline
        Write-Host " $file " -NoNewline
        Write-Host "($sizeKB KB)" -ForegroundColor Gray
        
        # Verificar se o tamanho é razoável (entre 50KB e 2MB)
        if ($fileInfo.Length -lt 50KB) {
            Write-Host "     AVISO: Arquivo muito pequeno (pode estar corrompido)" -ForegroundColor Yellow
        }
        elseif ($fileInfo.Length -gt 2MB) {
            Write-Host "     AVISO: Arquivo muito grande (recomendado otimizar)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "[FALTA]" -ForegroundColor Red -NoNewline
        Write-Host " $file"
        $allFilesPresent = $false
    }
}

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan

if ($allFilesPresent) {
    $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
    Write-Host "STATUS: PRONTO PARA COMMIT!" -ForegroundColor Green
    Write-Host "Tamanho total: $totalSizeMB MB" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. git add docs/screenshots/*.png"
    Write-Host "2. git commit -m `"docs: Adiciona screenshots do sistema ao README`""
    Write-Host "3. git push origin master"
}
else {
    Write-Host "STATUS: SCREENSHOTS FALTANDO" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ações necessárias:" -ForegroundColor Yellow
    Write-Host "1. Acesse http://localhost:3000"
    Write-Host "2. Faça login (admin@coruja.com / admin123)"
    Write-Host "3. Capture as 4 telas (Win + Shift + S)"
    Write-Host "4. Salve como PNG em docs\screenshots\"
    Write-Host "5. Execute este script novamente"
    Write-Host ""
    Write-Host "Consulte: ADICIONAR_SCREENSHOTS_GIT.md" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
