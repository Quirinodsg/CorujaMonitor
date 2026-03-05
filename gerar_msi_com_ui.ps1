# Script para gerar MSI com interface gráfica usando WiX 3.11

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GERADOR DE MSI COM UI - CORUJA PROBE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Diretórios
$wixDir = "$env:TEMP\wix311"
$wixBinDir = "$wixDir\wix311-binaries"

# Baixar WiX 3.11 se não existir
if (!(Test-Path "$wixBinDir\candle.exe")) {
    Write-Host "1. Baixando WiX Toolset 3.11..." -ForegroundColor Yellow
    
    $wixUrl = "https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311-binaries.zip"
    $wixZip = "$wixDir\wix311.zip"
    
    if (!(Test-Path $wixDir)) {
        New-Item -ItemType Directory -Path $wixDir | Out-Null
    }
    
    try {
        Invoke-WebRequest -Uri $wixUrl -OutFile $wixZip -UseBasicParsing
        Expand-Archive -Path $wixZip -DestinationPath $wixBinDir -Force
        Write-Host "   ✓ WiX 3.11 baixado e extraído" -ForegroundColor Green
    } catch {
        Write-Host "   ✗ Erro ao baixar WiX: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "1. WiX 3.11 já está disponível" -ForegroundColor Green
}

# Criar diretório de saída
Write-Host ""
Write-Host "2. Preparando diretórios..." -ForegroundColor Yellow
$outputDir = ".\installer\output"
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}
Write-Host "   ✓ Diretório criado" -ForegroundColor Green

# Compilar WXS para WIXOBJ
Write-Host ""
Write-Host "3. Compilando WXS..." -ForegroundColor Yellow
Set-Location installer

$candleExe = "$wixBinDir\candle.exe"
$lightExe = "$wixBinDir\light.exe"

& $candleExe CorujaProbe.wxs -out output\CorujaProbe.wixobj

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Erro ao compilar WXS" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Write-Host "   ✓ WXS compilado" -ForegroundColor Green

# Linkar WIXOBJ para MSI
Write-Host ""
Write-Host "4. Gerando MSI com interface gráfica..." -ForegroundColor Yellow

& $lightExe output\CorujaProbe.wixobj `
    -ext WixUIExtension `
    -cultures:en-us `
    -out output\CorujaProbe.msi

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "MSI COM UI GERADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    $msiFile = Get-Item ".\output\CorujaProbe.msi"
    Write-Host "Arquivo: .\installer\output\CorujaProbe.msi" -ForegroundColor Cyan
    Write-Host "Tamanho: $([math]::Round($msiFile.Length / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "Data: $($msiFile.LastWriteTime)" -ForegroundColor White
    Write-Host ""
    Write-Host "INSTALAÇÃO:" -ForegroundColor Yellow
    Write-Host "  Duplo clique no arquivo MSI" -ForegroundColor White
    Write-Host "  Ou: msiexec /i CorujaProbe.msi" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERRO AO GERAR MSI!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Set-Location ..
