# ========================================
# BUILD SETUP PROBE MSI
# Coruja Monitor Probe v1.0.0
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD SETUP PROBE MSI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar WiX Toolset
$wixPath = "C:\Program Files (x86)\WiX Toolset v3.11\bin"
if (-not (Test-Path $wixPath)) {
    Write-Host "[ERRO] WiX Toolset nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale WiX Toolset v3.11:" -ForegroundColor Yellow
    Write-Host "https://github.com/wixtoolset/wix3/releases" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

$env:Path += ";$wixPath"

# Diretórios
$sourceDir = Split-Path -Parent $PSScriptRoot
$installerDir = "$sourceDir\installer"
$outputDir = "$installerDir\output"

# Criar pasta output
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

Write-Host "[1/4] Verificando arquivos da Probe..." -ForegroundColor Yellow

# Verificar arquivos essenciais
$requiredFiles = @(
    "$sourceDir\probe\probe_core.py",
    "$sourceDir\probe\discovery_server.py",
    "$sourceDir\probe\configurar_probe.bat",
    "$sourceDir\probe\install.bat"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "[ERRO] Arquivos faltando:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Write-Host ""
    exit 1
}

Write-Host "[OK] Todos os arquivos encontrados" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] Compilando WiX (candle.exe)..." -ForegroundColor Yellow
$candleArgs = @(
    "-dSourceDir=$sourceDir",
    "-out", "$outputDir\SetupProbe.wixobj",
    "$installerDir\SetupProbe.wxs"
)

& candle.exe $candleArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha na compilacao WiX!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Compilacao concluida" -ForegroundColor Green
Write-Host ""

Write-Host "[3/4] Linkando MSI (light.exe)..." -ForegroundColor Yellow
$lightArgs = @(
    "-ext", "WixUIExtension",
    "-out", "$outputDir\SetupProbe.msi",
    "$outputDir\SetupProbe.wixobj"
)

& light.exe $lightArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha ao criar MSI!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] MSI criado com sucesso!" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] Limpando arquivos temporarios..." -ForegroundColor Yellow
Remove-Item "$outputDir\*.wixobj" -Force -ErrorAction SilentlyContinue
Remove-Item "$outputDir\*.wixpdb" -Force -ErrorAction SilentlyContinue

Write-Host "[OK] Limpeza concluida" -ForegroundColor Green
Write-Host ""

# Informações do arquivo
$msiFile = Get-Item "$outputDir\SetupProbe.msi"
$msiSize = [math]::Round($msiFile.Length / 1MB, 2)

Write-Host "========================================" -ForegroundColor Green
Write-Host "  MSI CRIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Arquivo: SetupProbe.msi" -ForegroundColor Cyan
Write-Host "Local: $outputDir" -ForegroundColor Cyan
Write-Host "Tamanho: $msiSize MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMO USAR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Instale SetupDependencias.msi primeiro (se ainda nao instalou)"
Write-Host "2. Execute SetupProbe.msi como Administrador"
Write-Host "3. Siga o assistente de instalacao"
Write-Host "4. Configure a Probe usando o atalho no Desktop"
Write-Host ""
Write-Host "Atalhos criados:"
Write-Host "  - Desktop: Configurar Coruja Probe"
Write-Host "  - Menu Iniciar: Configurar Coruja Probe"
Write-Host "  - Menu Iniciar: Instalar Servico Coruja"
Write-Host "  - Menu Iniciar: Diagnostico Coruja Probe"
Write-Host ""
