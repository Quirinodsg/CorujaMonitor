# Script para compilar o instalador MSI do Coruja Monitor Probe
# Requer WiX Toolset 3.11+ instalado

param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = ".\output",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORUJA MONITOR - BUILD MSI INSTALLER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se WiX está instalado
Write-Host "[1/8] Verificando WiX Toolset..." -ForegroundColor Yellow
$wixPath = "${env:WIX}bin"
if (-not (Test-Path $wixPath)) {
    Write-Host "   ✗ WiX Toolset não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "INSTALAR WIX TOOLSET:" -ForegroundColor Yellow
    Write-Host "1. Download: https://github.com/wixtoolset/wix3/releases" -ForegroundColor White
    Write-Host "2. Instale WiX Toolset 3.11 ou superior" -ForegroundColor White
    Write-Host "3. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    exit 1
}
Write-Host "   ✓ WiX encontrado em: $wixPath" -ForegroundColor Green
Write-Host ""

# Definir caminhos
$candle = Join-Path $wixPath "candle.exe"
$light = Join-Path $wixPath "light.exe"
$sourceDir = Split-Path -Parent $PSScriptRoot
$installerDir = $PSScriptRoot
$wxsFile = Join-Path $installerDir "CorujaProbe.wxs"
$wixobjFile = Join-Path $installerDir "CorujaProbe.wixobj"
$msiFile = Join-Path $OutputDir "CorujaMonitorProbe-$Version.msi"

# Criar diretório de saída
Write-Host "[2/8] Criando diretório de saída..." -ForegroundColor Yellow
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "   ✓ Diretório criado: $OutputDir" -ForegroundColor Green
} else {
    Write-Host "   ✓ Diretório já existe: $OutputDir" -ForegroundColor Green
}
Write-Host ""

# Limpar arquivos antigos se solicitado
if ($Clean) {
    Write-Host "[3/8] Limpando arquivos antigos..." -ForegroundColor Yellow
    if (Test-Path $wixobjFile) { Remove-Item $wixobjFile -Force }
    if (Test-Path $msiFile) { Remove-Item $msiFile -Force }
    Write-Host "   ✓ Arquivos limpos" -ForegroundColor Green
} else {
    Write-Host "[3/8] Pulando limpeza (use -Clean para limpar)" -ForegroundColor Gray
}
Write-Host ""

# Verificar arquivos necessários
Write-Host "[4/8] Verificando arquivos fonte..." -ForegroundColor Yellow
$requiredFiles = @(
    "..\probe\probe_core.py",
    "..\probe\config.py",
    "..\probe\requirements.txt",
    "..\probe\collectors\system_collector.py",
    "CorujaProbe.wxs"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $installerDir $file
    if (-not (Test-Path $fullPath)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "   ✗ Arquivos faltando:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "     - $file" -ForegroundColor Red
    }
    Write-Host ""
    exit 1
}
Write-Host "   ✓ Todos os arquivos encontrados" -ForegroundColor Green
Write-Host ""

# Criar assets se não existirem
Write-Host "[5/8] Verificando assets..." -ForegroundColor Yellow
$assetsDir = Join-Path $installerDir "assets"
if (-not (Test-Path $assetsDir)) {
    New-Item -ItemType Directory -Path $assetsDir | Out-Null
}

# Criar License.rtf se não existir
$licenseFile = Join-Path $assetsDir "License.rtf"
if (-not (Test-Path $licenseFile)) {
    @"
{\rtf1\ansi\ansicpg1252\deff0\nouicompat{\fonttbl{\f0\fnil\fcharset0 Calibri;}}
{\*\generator Riched20 10.0.19041}\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang22 LICEN\'c7A DE USO - CORUJA MONITOR\par
\par
Este software \'e9 fornecido "como est\'e1", sem garantias de qualquer tipo.\par
\par
Voc\'ea tem permiss\'e3o para usar, copiar e distribuir este software.\par
\par
Copyright (c) 2026 Coruja Monitor\par
}
"@ | Out-File -FilePath $licenseFile -Encoding ASCII
}
Write-Host "   ✓ Assets verificados" -ForegroundColor Green
Write-Host ""

# Compilar com candle.exe
Write-Host "[6/8] Compilando WXS com candle.exe..." -ForegroundColor Yellow
$candleArgs = @(
    "`"$wxsFile`"",
    "-out", "`"$wixobjFile`"",
    "-dVersion=$Version",
    "-ext", "WixUtilExtension",
    "-ext", "WixUIExtension"
)

Write-Host "   Comando: candle.exe $($candleArgs -join ' ')" -ForegroundColor Gray
& $candle $candleArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Erro na compilação com candle" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ Compilação concluída" -ForegroundColor Green
Write-Host ""

# Linkar com light.exe
Write-Host "[7/8] Linkando com light.exe..." -ForegroundColor Yellow
$lightArgs = @(
    "`"$wixobjFile`"",
    "-out", "`"$msiFile`"",
    "-ext", "WixUtilExtension",
    "-ext", "WixUIExtension",
    "-cultures:pt-BR",
    "-loc", "pt-BR.wxl"
)

Write-Host "   Comando: light.exe $($lightArgs -join ' ')" -ForegroundColor Gray
& $light $lightArgs 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Erro no link com light" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ Link concluído" -ForegroundColor Green
Write-Host ""

# Verificar MSI criado
Write-Host "[8/8] Verificando MSI..." -ForegroundColor Yellow
if (Test-Path $msiFile) {
    $fileInfo = Get-Item $msiFile
    Write-Host "   ✓ MSI criado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  BUILD CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Arquivo: $msiFile" -ForegroundColor White
    Write-Host "Tamanho: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "Versão: $Version" -ForegroundColor White
    Write-Host ""
    Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
    Write-Host "1. Teste o instalador: msiexec /i `"$msiFile`"" -ForegroundColor White
    Write-Host "2. Distribua para os clientes" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "   ✗ MSI não foi criado" -ForegroundColor Red
    exit 1
}

# Limpar arquivos temporários
if (Test-Path $wixobjFile) {
    Remove-Item $wixobjFile -Force
}

Write-Host "Pressione ENTER para sair..."
Read-Host
