# Script completo para gerar MSI do Coruja Probe

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GERADOR DE MSI - CORUJA PROBE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se .NET SDK está instalado
Write-Host "1. Verificando .NET SDK..." -ForegroundColor Yellow
$dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
if ($dotnet) {
    Write-Host "   ✓ .NET SDK encontrado: $($dotnet.Version)" -ForegroundColor Green
} else {
    Write-Host "   ✗ .NET SDK não encontrado!" -ForegroundColor Red
    Write-Host "   Instale em: https://dotnet.microsoft.com/download" -ForegroundColor Yellow
    exit 1
}

# Instalar WiX Toolset
Write-Host ""
Write-Host "2. Instalando WiX Toolset..." -ForegroundColor Yellow
dotnet tool install --global wix --version 5.0.0
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Tentando atualizar WiX..." -ForegroundColor Yellow
    dotnet tool update --global wix
}

# Instalar extensão UI do WiX
Write-Host ""
Write-Host "3. Instalando extensão UI do WiX..." -ForegroundColor Yellow
wix extension add WixToolset.UI.wixext
Write-Host "   ✓ Extensão UI instalada!" -ForegroundColor Green

# Verificar instalação do WiX
Write-Host ""
Write-Host "4. Verificando WiX..." -ForegroundColor Yellow
$wix = Get-Command wix -ErrorAction SilentlyContinue
if ($wix) {
    Write-Host "   ✓ WiX instalado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "   ✗ Erro ao instalar WiX!" -ForegroundColor Red
    exit 1
}

# Criar diretório de saída
Write-Host ""
Write-Host "5. Preparando diretórios..." -ForegroundColor Yellow
$outputDir = ".\installer\output"
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}
Write-Host "   ✓ Diretório criado: $outputDir" -ForegroundColor Green

# Compilar o WiX
Write-Host ""
Write-Host "6. Compilando MSI..." -ForegroundColor Yellow
Set-Location installer

# Compilar com WiX 5.0
wix build CorujaProbe.wxs -out output\CorujaProbe.msi -ext WixToolset.UI.wixext

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "MSI GERADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Arquivo: .\installer\output\CorujaProbe.msi" -ForegroundColor Cyan
    Write-Host ""
    
    # Mostrar informações do arquivo
    $msiFile = Get-Item ".\output\CorujaProbe.msi"
    Write-Host "Tamanho: $([math]::Round($msiFile.Length / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "Data: $($msiFile.LastWriteTime)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERRO AO GERAR MSI!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifique os erros acima." -ForegroundColor Yellow
}

Set-Location ..
