# ========================================
# BUILD SETUP DEPENDENCIAS MSI
# Coruja Monitor Probe v1.0.0
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD SETUP DEPENDENCIAS MSI" -ForegroundColor Cyan
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

Write-Host "[1/4] Verificando Python installer..." -ForegroundColor Yellow

# Verificar se python-3.11.8-amd64.exe existe
$pythonInstaller = "$sourceDir\python-3.11.8-amd64.exe"
if (-not (Test-Path $pythonInstaller)) {
    Write-Host "[INFO] Baixando Python 3.11.8..." -ForegroundColor Yellow
    Write-Host ""
    
    $url = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $pythonInstaller -UseBasicParsing
        Write-Host "[OK] Python baixado!" -ForegroundColor Green
    } catch {
        Write-Host "[ERRO] Falha ao baixar Python!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Baixe manualmente:" -ForegroundColor Yellow
        Write-Host $url -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Salve em: $sourceDir" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
}

Write-Host "[OK] Python installer encontrado" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] Compilando WiX (candle.exe)..." -ForegroundColor Yellow
$candleArgs = @(
    "-dSourceDir=$sourceDir",
    "-out", "$outputDir\SetupDependencias.wixobj",
    "$installerDir\SetupDependencias.wxs"
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
    "-out", "$outputDir\SetupDependencias.msi",
    "$outputDir\SetupDependencias.wixobj"
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
$msiFile = Get-Item "$outputDir\SetupDependencias.msi"
$msiSize = [math]::Round($msiFile.Length / 1MB, 2)

Write-Host "========================================" -ForegroundColor Green
Write-Host "  MSI CRIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Arquivo: SetupDependencias.msi" -ForegroundColor Cyan
Write-Host "Local: $outputDir" -ForegroundColor Cyan
Write-Host "Tamanho: $msiSize MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COMO USAR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Execute SetupDependencias.msi como Administrador"
Write-Host "2. Siga o assistente de instalacao"
Write-Host "3. Python 3.11 sera instalado automaticamente"
Write-Host "4. Dependencias serao instaladas automaticamente"
Write-Host ""
Write-Host "Depois instale a Probe usando SetupProbe.msi"
Write-Host ""
