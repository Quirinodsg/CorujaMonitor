# ========================================
# GERAR INSTALADORES INNO SETUP
# SetupDependencias.exe + SetupProbe.exe
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GERAR INSTALADORES INNO SETUP" -ForegroundColor Cyan
Write-Host "  Coruja Monitor Probe v1.0.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Verificar Inno Setup
$innoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoPath)) {
    Write-Host "[ERRO] Inno Setup nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale Inno Setup 6:" -ForegroundColor Yellow
    Write-Host "https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ou ajuste o caminho em:" -ForegroundColor Yellow
    Write-Host "`$innoPath = ""C:\Program Files (x86)\Inno Setup 6\ISCC.exe""" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "[OK] Inno Setup encontrado" -ForegroundColor Green
Write-Host ""

# Diretórios
$sourceDir = $PSScriptRoot
$installerDir = "$sourceDir\installer"
$outputDir = "$installerDir\output"

# Criar pasta output
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# ========================================
# VERIFICAR PYTHON INSTALLER
# ========================================

Write-Host "[1/5] Verificando Python installer..." -ForegroundColor Yellow

$pythonInstaller = "$sourceDir\python-3.11.8-amd64.exe"
if (-not (Test-Path $pythonInstaller)) {
    Write-Host "[INFO] Baixando Python 3.11.8..." -ForegroundColor Yellow
    Write-Host ""
    
    $url = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
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

# ========================================
# COMPILAR SETUP DEPENDENCIAS
# ========================================

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  PASSO 2: SETUP DEPENDENCIAS" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "[2/5] Compilando SetupDependencias.iss..." -ForegroundColor Yellow

try {
    & $innoPath "$installerDir\SetupDependencias.iss" /Q
    
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao compilar SetupDependencias.iss"
    }
    
    Write-Host "[OK] SetupDependencias.exe criado!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERRO] Falha ao criar SetupDependencias.exe" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ========================================
# COMPILAR SETUP PROBE
# ========================================

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  PASSO 3: SETUP PROBE" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "[3/5] Compilando SetupProbe.iss..." -ForegroundColor Yellow

try {
    & $innoPath "$installerDir\SetupProbe.iss" /Q
    
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao compilar SetupProbe.iss"
    }
    
    Write-Host "[OK] SetupProbe.exe criado!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERRO] Falha ao criar SetupProbe.exe" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ========================================
# CRIAR README
# ========================================

Write-Host "[4/5] Criando README.txt..." -ForegroundColor Yellow

$readmeContent = @"
========================================
CORUJA MONITOR PROBE - INSTALADORES
Versao: 1.0.0
========================================

ARQUIVOS:
1. SetupDependencias-v1.0.0.exe (~30 MB)
   - Instala Python 3.11.8
   - Instala dependencias Python

2. SetupProbe-v1.0.0.exe (~2 MB)
   - Instala arquivos da Probe
   - Cria atalhos

========================================
ORDEM DE INSTALACAO
========================================

1. Execute SetupDependencias-v1.0.0.exe
   - Como Administrador
   - Siga o assistente
   - Tempo: 3-5 minutos

2. Execute SetupProbe-v1.0.0.exe
   - Como Administrador
   - Siga o assistente
   - Tempo: 1 minuto

3. Configure a Probe
   - Desktop > Configurar Coruja Probe
   - IP: 192.168.31.161
   - Token: [fornecido pelo admin]

========================================
SUPORTE
========================================

Web: http://192.168.31.161:3000
Email: admin@coruja.com
Login: admin@coruja.com
Senha: admin123

========================================
"@

$readmeContent | Out-File -FilePath "$outputDir\README.txt" -Encoding UTF8

Write-Host "[OK] README.txt criado" -ForegroundColor Green
Write-Host ""

# ========================================
# VERIFICAR ARQUIVOS
# ========================================

Write-Host "[5/5] Verificando arquivos gerados..." -ForegroundColor Yellow
Write-Host ""

$files = @(
    "SetupDependencias-v1.0.0.exe",
    "SetupProbe-v1.0.0.exe"
)

$allOk = $true
foreach ($file in $files) {
    $fullPath = "$outputDir\$file"
    if (Test-Path $fullPath) {
        $fileInfo = Get-Item $fullPath
        $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
        Write-Host "[OK] $file ($sizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "[ERRO] $file nao encontrado!" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""

if (-not $allOk) {
    Write-Host "[ERRO] Alguns arquivos nao foram gerados!" -ForegroundColor Red
    exit 1
}

# ========================================
# RESUMO FINAL
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  INSTALADORES CRIADOS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# SetupDependencias
if (Test-Path "$outputDir\SetupDependencias-v1.0.0.exe") {
    $file1 = Get-Item "$outputDir\SetupDependencias-v1.0.0.exe"
    $size1 = [math]::Round($file1.Length / 1MB, 2)
    
    Write-Host "1. SetupDependencias-v1.0.0.exe" -ForegroundColor Cyan
    Write-Host "   Tamanho: $size1 MB" -ForegroundColor White
    Write-Host "   Instala: Python 3.11 + Dependencias" -ForegroundColor White
    Write-Host ""
}

# SetupProbe
if (Test-Path "$outputDir\SetupProbe-v1.0.0.exe") {
    $file2 = Get-Item "$outputDir\SetupProbe-v1.0.0.exe"
    $size2 = [math]::Round($file2.Length / 1MB, 2)
    
    Write-Host "2. SetupProbe-v1.0.0.exe" -ForegroundColor Cyan
    Write-Host "   Tamanho: $size2 MB" -ForegroundColor White
    Write-Host "   Instala: Arquivos da Probe + Atalhos" -ForegroundColor White
    Write-Host ""
}

Write-Host "Local: $outputDir" -ForegroundColor Yellow
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ORDEM DE INSTALACAO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Execute SetupDependencias-v1.0.0.exe primeiro" -ForegroundColor White
Write-Host "   - Instala Python 3.11.8" -ForegroundColor Gray
Write-Host "   - Instala psutil, httpx, pywin32, pysnmp, pyyaml" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Execute SetupProbe-v1.0.0.exe depois" -ForegroundColor White
Write-Host "   - Copia arquivos da Probe" -ForegroundColor Gray
Write-Host "   - Cria atalhos" -ForegroundColor Gray
Write-Host "   - Configura firewall" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Configure a Probe" -ForegroundColor White
Write-Host "   - Desktop: Configurar Coruja Probe" -ForegroundColor Gray
Write-Host "   - Digite IP: 192.168.31.161" -ForegroundColor Gray
Write-Host "   - Digite token da probe" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DISTRIBUICAO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Envie AMBOS os arquivos EXE para os clientes:" -ForegroundColor White
Write-Host "  - SetupDependencias-v1.0.0.exe" -ForegroundColor Cyan
Write-Host "  - SetupProbe-v1.0.0.exe" -ForegroundColor Cyan
Write-Host "  - README.txt" -ForegroundColor Cyan
Write-Host ""
Write-Host "Instrua a instalar nesta ordem!" -ForegroundColor Yellow
Write-Host ""

Write-Host "Pressione ENTER para abrir a pasta..." -ForegroundColor Green
Read-Host

# Abrir pasta output
Start-Process explorer.exe -ArgumentList $outputDir
