# ========================================
# GERAR AMBOS OS MSIS
# SetupDependencias.msi + SetupProbe.msi
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GERAR INSTALADORES MSI" -ForegroundColor Cyan
Write-Host "  Coruja Monitor Probe v1.0.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Verificar se está executando como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[AVISO] Execute como Administrador para melhores resultados" -ForegroundColor Yellow
    Write-Host ""
}

# ========================================
# PASSO 1: SETUP DEPENDENCIAS
# ========================================

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  PASSO 1: SETUP DEPENDENCIAS" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

try {
    & "$PSScriptRoot\installer\build-setup-dependencias.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao gerar SetupDependencias.msi"
    }
    
    Write-Host "[OK] SetupDependencias.msi criado!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERRO] Falha ao criar SetupDependencias.msi" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ========================================
# PASSO 2: SETUP PROBE
# ========================================

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  PASSO 2: SETUP PROBE" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

try {
    & "$PSScriptRoot\installer\build-setup-probe.ps1"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao gerar SetupProbe.msi"
    }
    
    Write-Host "[OK] SetupProbe.msi criado!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERRO] Falha ao criar SetupProbe.msi" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ========================================
# RESUMO FINAL
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  AMBOS OS MSIS CRIADOS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$outputDir = "$PSScriptRoot\installer\output"

# SetupDependencias.msi
if (Test-Path "$outputDir\SetupDependencias.msi") {
    $file1 = Get-Item "$outputDir\SetupDependencias.msi"
    $size1 = [math]::Round($file1.Length / 1MB, 2)
    
    Write-Host "1. SetupDependencias.msi" -ForegroundColor Cyan
    Write-Host "   Tamanho: $size1 MB" -ForegroundColor White
    Write-Host "   Instala: Python 3.11 + Dependencias" -ForegroundColor White
    Write-Host ""
}

# SetupProbe.msi
if (Test-Path "$outputDir\SetupProbe.msi") {
    $file2 = Get-Item "$outputDir\SetupProbe.msi"
    $size2 = [math]::Round($file2.Length / 1MB, 2)
    
    Write-Host "2. SetupProbe.msi" -ForegroundColor Cyan
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
Write-Host "1. Execute SetupDependencias.msi primeiro" -ForegroundColor White
Write-Host "   - Instala Python 3.11.8" -ForegroundColor Gray
Write-Host "   - Instala psutil, httpx, pywin32, pysnmp, pyyaml" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Execute SetupProbe.msi depois" -ForegroundColor White
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
Write-Host "Envie AMBOS os arquivos MSI para os clientes:" -ForegroundColor White
Write-Host "  - SetupDependencias.msi" -ForegroundColor Cyan
Write-Host "  - SetupProbe.msi" -ForegroundColor Cyan
Write-Host ""
Write-Host "Instrua a instalar nesta ordem!" -ForegroundColor Yellow
Write-Host ""

Write-Host "Pressione ENTER para abrir a pasta..." -ForegroundColor Green
Read-Host

# Abrir pasta output
Start-Process explorer.exe -ArgumentList $outputDir
