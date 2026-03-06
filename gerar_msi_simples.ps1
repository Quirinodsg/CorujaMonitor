# Script para gerar MSI simples (sem UI) do Coruja Probe

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GERADOR DE MSI SIMPLES - CORUJA PROBE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar .NET SDK
Write-Host "1. Verificando .NET SDK..." -ForegroundColor Yellow
$dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
if (!$dotnet) {
    Write-Host "   ✗ .NET SDK não encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ .NET SDK encontrado" -ForegroundColor Green

# Verificar WiX
Write-Host ""
Write-Host "2. Verificando WiX..." -ForegroundColor Yellow
$wix = Get-Command wix -ErrorAction SilentlyContinue
if (!$wix) {
    Write-Host "   Instalando WiX..." -ForegroundColor Yellow
    dotnet tool install --global wix
}
Write-Host "   ✓ WiX disponível" -ForegroundColor Green

# Criar diretório de saída
Write-Host ""
Write-Host "3. Preparando diretórios..." -ForegroundColor Yellow
$outputDir = ".\installer\output"
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}
Write-Host "   ✓ Diretório criado" -ForegroundColor Green

# Compilar MSI sem UI
Write-Host ""
Write-Host "4. Compilando MSI (instalação silenciosa)..." -ForegroundColor Yellow
Set-Location installer

# Compilar sem extensão UI
wix build CorujaProbe.wxs -out output\CorujaProbe.msi

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "MSI GERADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    $msiFile = Get-Item ".\output\CorujaProbe.msi"
    Write-Host "Arquivo: .\installer\output\CorujaProbe.msi" -ForegroundColor Cyan
    Write-Host "Tamanho: $([math]::Round($msiFile.Length / 1MB, 2)) MB" -ForegroundColor White
    Write-Host ""
    Write-Host "INSTALAÇÃO:" -ForegroundColor Yellow
    Write-Host "  Silenciosa: msiexec /i CorujaProbe.msi /quiet" -ForegroundColor White
    Write-Host "  Com log: msiexec /i CorujaProbe.msi /l*v install.log" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERRO AO GERAR MSI!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Set-Location ..
