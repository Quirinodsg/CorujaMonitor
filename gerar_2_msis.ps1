# Script para gerar 2 MSIs: Básico e com AD

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GERADOR DE 2 MSIs - CORUJA PROBE" -ForegroundColor Cyan
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
        Write-Host "   ✓ WiX 3.11 baixado" -ForegroundColor Green
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

Set-Location installer

$candleExe = "$wixBinDir\candle.exe"
$lightExe = "$wixBinDir\light.exe"

# ========================================
# MSI 1: BÁSICO (Auto-Start)
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MSI 1: BÁSICO (Auto-Start)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "3. Compilando WXS Básico..." -ForegroundColor Yellow
& $candleExe CorujaProbe_AutoStart.wxs -out output\CorujaProbe_AutoStart.wixobj

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Erro ao compilar" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Write-Host "   ✓ Compilado" -ForegroundColor Green

Write-Host ""
Write-Host "4. Gerando MSI Básico..." -ForegroundColor Yellow
& $lightExe output\CorujaProbe_AutoStart.wixobj `
    -ext WixUIExtension `
    -cultures:en-us `
    -out output\CorujaProbe_Basico.msi

if ($LASTEXITCODE -eq 0) {
    $msiFile = Get-Item ".\output\CorujaProbe_Basico.msi"
    Write-Host "   ✓ MSI Básico gerado!" -ForegroundColor Green
    Write-Host "   Arquivo: CorujaProbe_Basico.msi" -ForegroundColor White
    Write-Host "   Tamanho: $([math]::Round($msiFile.Length / 1KB, 2)) KB" -ForegroundColor White
} else {
    Write-Host "   ✗ Erro ao gerar MSI" -ForegroundColor Red
}

# ========================================
# MSI 2: COM AD
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MSI 2: COM ACTIVE DIRECTORY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "5. Compilando WXS com AD..." -ForegroundColor Yellow
& $candleExe CorujaProbe_AD_Simple.wxs -out output\CorujaProbe_AD.wixobj

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Erro ao compilar" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Write-Host "   ✓ Compilado" -ForegroundColor Green

Write-Host ""
Write-Host "6. Gerando MSI com AD..." -ForegroundColor Yellow
& $lightExe output\CorujaProbe_AD.wixobj `
    -ext WixUIExtension `
    -cultures:en-us `
    -out output\CorujaProbe_AD.msi

if ($LASTEXITCODE -eq 0) {
    $msiFile = Get-Item ".\output\CorujaProbe_AD.msi"
    Write-Host "   ✓ MSI com AD gerado!" -ForegroundColor Green
    Write-Host "   Arquivo: CorujaProbe_AD.msi" -ForegroundColor White
    Write-Host "   Tamanho: $([math]::Round($msiFile.Length / 1KB, 2)) KB" -ForegroundColor White
} else {
    Write-Host "   ✗ Erro ao gerar MSI" -ForegroundColor Red
}

Set-Location ..

# Resumo
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "2 MSIs GERADOS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "MSI 1 - BÁSICO:" -ForegroundColor Cyan
Write-Host "  Arquivo: .\installer\output\CorujaProbe_Basico.msi" -ForegroundColor White
Write-Host "  Uso: Instalação simples sem AD" -ForegroundColor Gray
Write-Host "  - Auto-start via Task Scheduler" -ForegroundColor Gray
Write-Host "  - Instalação de dependências Python" -ForegroundColor Gray
Write-Host "  - Atalhos no Menu Iniciar" -ForegroundColor Gray
Write-Host ""
Write-Host "MSI 2 - COM AD:" -ForegroundColor Cyan
Write-Host "  Arquivo: .\installer\output\CorujaProbe_AD.msi" -ForegroundColor White
Write-Host "  Uso: Instalação com usuário do Active Directory" -ForegroundColor Gray
Write-Host "  - Solicita domínio, usuário e senha" -ForegroundColor Gray
Write-Host "  - Configura Task Scheduler com usuário AD" -ForegroundColor Gray
Write-Host "  - Solicita URL da API e token" -ForegroundColor Gray
Write-Host ""
Write-Host "INSTALAÇÃO:" -ForegroundColor Yellow
Write-Host "  Duplo clique no arquivo MSI desejado" -ForegroundColor White
Write-Host "  Ou: msiexec /i CorujaProbe_Basico.msi" -ForegroundColor White
Write-Host "  Ou: msiexec /i CorujaProbe_AD.msi" -ForegroundColor White
Write-Host ""

pause
