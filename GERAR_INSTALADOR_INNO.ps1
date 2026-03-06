# Gerar Instalador EXE Profissional com Inno Setup
# Funciona igual a MSI, instala Python automaticamente

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GERAR INSTALADOR EXE PROFISSIONAL" -ForegroundColor Cyan
Write-Host "  Com Python Embeddable Automático" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Procurar Inno Setup em vários locais
Write-Host "🔍 Procurando Inno Setup..." -ForegroundColor Yellow

$innoPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
)

$innoPath = $null
foreach ($path in $innoPaths) {
    if (Test-Path $path) {
        $innoPath = $path
        Write-Host "✓ Encontrado: $path" -ForegroundColor Green
        break
    }
}

# Tentar via registro do Windows
if (-not $innoPath) {
    Write-Host "   Procurando no registro..." -ForegroundColor Gray
    try {
        $uninstallKeys = @(
            "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
            "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
        )
        
        foreach ($key in $uninstallKeys) {
            $apps = Get-ItemProperty $key -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "*Inno Setup*" }
            if ($apps) {
                $installLocation = $apps[0].InstallLocation
                if ($installLocation) {
                    $possiblePath = Join-Path $installLocation "ISCC.exe"
                    if (Test-Path $possiblePath) {
                        $innoPath = $possiblePath
                        Write-Host "✓ Encontrado via registro: $possiblePath" -ForegroundColor Green
                        break
                    }
                }
            }
        }
    } catch {
        Write-Host "   Erro ao procurar no registro" -ForegroundColor Gray
    }
}

if (-not $innoPath) {
    Write-Host ""
    Write-Host "❌ Inno Setup não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Procurado em:" -ForegroundColor Gray
    foreach ($path in $innoPaths) {
        Write-Host "   • $path" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "═══════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  INSTALAR INNO SETUP" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Baixe de: https://jrsoftware.org/isdl.php" -ForegroundColor White
    Write-Host "2. Execute o instalador" -ForegroundColor White
    Write-Host "3. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    Write-Host "OU compile manualmente:" -ForegroundColor Cyan
    Write-Host "1. Abra o Inno Setup Compiler" -ForegroundColor White
    Write-Host "2. File > Open: installer\CorujaProbe.iss" -ForegroundColor White
    Write-Host "3. Build > Compile" -ForegroundColor White
    Write-Host ""
    
    $download = Read-Host "Deseja abrir a página de download? (S/N)"
    if ($download -eq "S" -or $download -eq "s") {
        Start-Process "https://jrsoftware.org/isdl.php"
    }
    
    Write-Host ""
    Write-Host "Pressione ENTER para sair..."
    Read-Host
    exit 1
}

Write-Host ""

# Compilar o script ISS
$issFile = Join-Path $PSScriptRoot "installer\CorujaProbe.iss"

if (-not (Test-Path $issFile)) {
    Write-Host "❌ Arquivo CorujaProbe.iss não encontrado!" -ForegroundColor Red
    Write-Host "   Esperado em: $issFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Pressione ENTER para sair..."
    Read-Host
    exit 1
}

Write-Host "📝 Compilando instalador..." -ForegroundColor Yellow
Write-Host "   Script: installer\CorujaProbe.iss" -ForegroundColor Gray
Write-Host "   Compilador: $innoPath" -ForegroundColor Gray
Write-Host ""

try {
    $output = & $innoPath $issFile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  INSTALADOR GERADO COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        
        $outputFile = Join-Path $PSScriptRoot "installer\output\CorujaMonitorProbe-Setup-v1.0.0.exe"
        
        if (Test-Path $outputFile) {
            $fileSize = [math]::Round((Get-Item $outputFile).Length / 1MB, 2)
            
            Write-Host "📦 INSTALADOR CRIADO:" -ForegroundColor Cyan
            Write-Host "   Arquivo: CorujaMonitorProbe-Setup-v1.0.0.exe" -ForegroundColor White
            Write-Host "   Tamanho: $fileSize MB" -ForegroundColor White
            Write-Host "   Local: installer\output\" -ForegroundColor White
            Write-Host ""
            
            Write-Host "✨ CARACTERÍSTICAS:" -ForegroundColor Yellow
            Write-Host "   ✓ Instala Python 3.11 automaticamente" -ForegroundColor Green
            Write-Host "   ✓ Instala dependências (psutil, httpx, etc)" -ForegroundColor Green
            Write-Host "   ✓ Cria atalhos (Desktop + Menu Iniciar)" -ForegroundColor Green
            Write-Host "   ✓ Configura firewall automaticamente" -ForegroundColor Green
            Write-Host "   ✓ Registra no Windows" -ForegroundColor Green
            Write-Host "   ✓ Desinstalação limpa" -ForegroundColor Green
            Write-Host "   ✓ Interface profissional" -ForegroundColor Green
            Write-Host "   ✓ Funciona igual a MSI" -ForegroundColor Green
            Write-Host ""
            
            Write-Host "📋 COMO USAR:" -ForegroundColor Yellow
            Write-Host "   1. Clique direito no EXE" -ForegroundColor White
            Write-Host "   2. Executar como Administrador" -ForegroundColor White
            Write-Host "   3. Siga o assistente de instalação" -ForegroundColor White
            Write-Host ""
            
            Write-Host "🚀 DISTRIBUIR:" -ForegroundColor Yellow
            Write-Host "   • Envie o EXE para os clientes" -ForegroundColor White
            Write-Host "   • Pode ser usado em GPO/SCCM" -ForegroundColor White
            Write-Host "   • Pode ser assinado digitalmente" -ForegroundColor White
            Write-Host ""
            
            # Abrir pasta
            Start-Process explorer.exe -ArgumentList (Join-Path $PSScriptRoot "installer\output")
            Write-Host "✓ Pasta aberta automaticamente!" -ForegroundColor Green
            Write-Host ""
            
        } else {
            Write-Host "⚠️  Instalador compilado mas arquivo não encontrado" -ForegroundColor Yellow
            Write-Host "   Procurado em: $outputFile" -ForegroundColor Gray
        }
        
    } else {
        Write-Host ""
        Write-Host "❌ Erro na compilação!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Saída do compilador:" -ForegroundColor Yellow
        Write-Host $output
        Write-Host ""
        Write-Host "Código de erro: $LASTEXITCODE" -ForegroundColor Gray
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Erro ao executar compilador: $_" -ForegroundColor Red
    Write-Host ""
}

Write-Host "Pressione ENTER para sair..."
Read-Host
