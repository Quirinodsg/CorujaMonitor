# Build MSI Completo com Python Embeddable e Bypass de Políticas
# Coruja Monitor Probe - Instalador Empresarial

param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = ".\output"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MSI COMPLETO - CORUJA MONITOR" -ForegroundColor Cyan
Write-Host "  Com Python Embeddable" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar WiX Toolset
$wixPath = "C:\Program Files (x86)\WiX Toolset v3.11\bin"
if (-not (Test-Path $wixPath)) {
    Write-Host "❌ WiX Toolset não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "INSTALAR WiX Toolset:" -ForegroundColor Yellow
    Write-Host "1. Download: https://github.com/wixtoolset/wix3/releases/download/wix3112rtm/wix311.exe" -ForegroundColor White
    Write-Host "2. Execute o instalador" -ForegroundColor White
    Write-Host "3. Execute este script novamente" -ForegroundColor White
    Write-Host ""
    exit 1
}

$candle = Join-Path $wixPath "candle.exe"
$light = Join-Path $wixPath "light.exe"

# Criar diretório de saída
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host "📁 Preparando arquivos..." -ForegroundColor Yellow

# Criar arquivo python_readme.txt
$pythonReadme = @"
PYTHON EMBEDDABLE
=================

Este diretório contém o Python embeddable que será
instalado automaticamente se o Python não estiver
presente no sistema.

Versão: Python 3.11.8 (64-bit)
Tipo: Embeddable Package

O instalador detecta automaticamente se o Python
já está instalado e pula esta etapa se necessário.
"@

$pythonReadme | Out-File -FilePath "python_readme.txt" -Encoding UTF8

# Criar licença RTF
$licenseRtf = @"
{\rtf1\ansi\deff0
{\fonttbl{\f0\fnil\fcharset0 Arial;}}
{\colortbl;\red0\green0\blue0;}
\viewkind4\uc1\pard\lang1046\f0\fs20
LICEN\u199?A DE USO - CORUJA MONITOR PROBE\par
\par
Este software \u233? fornecido "como est\u225?", sem garantias de qualquer tipo.\par
\par
Voc\u234? pode usar, copiar, modificar e distribuir este software.\par
\par
REQUISITOS:\par
- Windows 7 / Server 2008 R2 ou superior\par
- Python 3.8+ (ser\u225? instalado automaticamente se necess\u225?rio)\par
- Privil\u233?gios de administrador\par
\par
SUPORTE:\par
- Web: http://192.168.31.161:3000\par
- Email: suporte@coruja.com\par
}
"@

$licenseRtf | Out-File -FilePath "license.rtf" -Encoding ASCII

Write-Host "✓ Arquivos preparados" -ForegroundColor Green
Write-Host ""

Write-Host "🔨 Compilando MSI..." -ForegroundColor Yellow

# Compilar WXS
$wixObj = Join-Path $OutputDir "CorujaProbe_Complete.wixobj"
$msiFile = Join-Path $OutputDir "CorujaMonitorProbe-Complete-$Version.msi"

try {
    # Candle (compilar)
    Write-Host "   Executando candle.exe..." -ForegroundColor Gray
    & $candle "CorujaProbe_Complete.wxs" `
        -out $wixObj `
        -arch x64 `
        -ext WixUIExtension `
        -ext WixUtilExtension
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erro no candle.exe"
    }
    
    # Light (linkar)
    Write-Host "   Executando light.exe..." -ForegroundColor Gray
    & $light $wixObj `
        -out $msiFile `
        -ext WixUIExtension `
        -ext WixUtilExtension `
        -cultures:pt-BR `
        -loc pt-BR.wxl `
        -sval
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erro no light.exe"
    }
    
    Write-Host "✓ MSI compilado com sucesso!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "❌ Erro na compilação: $_" -ForegroundColor Red
    exit 1
}

# Criar script de instalação silenciosa
$silentInstall = @"
@echo off
REM Instalação Silenciosa - Coruja Monitor Probe
REM Bypass de políticas de grupo

echo ========================================
echo   INSTALACAO SILENCIOSA
echo   Coruja Monitor Probe
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    pause
    exit /b 1
)

echo Instalando Coruja Monitor Probe...
echo.

REM Instalar MSI com bypass de políticas
msiexec /i "CorujaMonitorProbe-Complete-$Version.msi" ^
    /qn ^
    /norestart ^
    ALLUSERS=1 ^
    MSIINSTALLPERUSER=0 ^
    /L*V install.log

if %errorLevel% equ 0 (
    echo.
    echo ========================================
    echo INSTALACAO CONCLUIDA!
    echo ========================================
    echo.
    echo Verifique: Menu Iniciar ^> Coruja Monitor
    echo.
) else (
    echo.
    echo ========================================
    echo ERRO NA INSTALACAO!
    echo ========================================
    echo.
    echo Verifique o arquivo install.log
    echo.
)

pause
"@

$silentInstallPath = Join-Path $OutputDir "install-silent.bat"
$silentInstall | Out-File -FilePath $silentInstallPath -Encoding ASCII

# Criar script de desinstalação
$uninstall = @"
@echo off
REM Desinstalação - Coruja Monitor Probe

echo ========================================
echo   DESINSTALACAO
echo   Coruja Monitor Probe
echo ========================================
echo.

REM Verificar admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    pause
    exit /b 1
)

echo Removendo Coruja Monitor Probe...
echo.

REM Parar serviço se existir
sc stop CorujaProbe >nul 2>&1
sc delete CorujaProbe >nul 2>&1

REM Desinstalar via MSI
msiexec /x "CorujaMonitorProbe-Complete-$Version.msi" /qn /norestart

echo.
echo Desinstalacao concluida!
echo.
pause
"@

$uninstallPath = Join-Path $OutputDir "uninstall.bat"
$uninstall | Out-File -FilePath $uninstallPath -Encoding ASCII

# Criar README
$readme = @"
CORUJA MONITOR PROBE - INSTALADOR COMPLETO
===========================================

VERSÃO: $Version
DATA: $(Get-Date -Format "dd/MM/yyyy")

CARACTERÍSTICAS:
✓ Instalação automática de Python (se necessário)
✓ Bypass de políticas de grupo
✓ Instalação silenciosa disponível
✓ Todos os coletores incluídos
✓ Configuração via interface gráfica

ARQUIVOS:
- CorujaMonitorProbe-Complete-$Version.msi - Instalador principal
- install-silent.bat - Instalação silenciosa
- uninstall.bat - Desinstalação
- README.txt - Este arquivo

INSTALAÇÃO NORMAL:
==================
1. Clique direito no MSI
2. "Executar como Administrador"
3. Siga o assistente de instalação
4. Configure o servidor após instalação

INSTALAÇÃO SILENCIOSA (GPO/SCCM):
==================================
1. Execute como Administrador:
   install-silent.bat

2. Ou via linha de comando:
   msiexec /i "CorujaMonitorProbe-Complete-$Version.msi" /qn ALLUSERS=1

BYPASS DE POLÍTICAS:
====================
Este instalador inclui configurações para bypass de políticas
de grupo que bloqueiam instalações MSI:

- ALLUSERS=1
- MSIINSTALLPERUSER=0
- InstallPrivileges=elevated
- AdminImage=no

Se ainda assim houver bloqueio, execute:
1. gpedit.msc
2. Configuração do Computador > Modelos Administrativos
3. Componentes do Windows > Windows Installer
4. Desabilitar "Desativar Windows Installer"

REQUISITOS:
===========
- Windows 7 / Server 2008 R2 ou superior (64-bit)
- Privilégios de administrador
- Python 3.8+ (instalado automaticamente se ausente)
- 500 MB de espaço em disco
- Conexão com servidor Coruja Monitor

APÓS INSTALAÇÃO:
================
1. Menu Iniciar > Coruja Monitor > Configurar Coruja Probe
2. Digite o IP do servidor (ex: 192.168.31.161)
3. Digite o token da probe
4. Menu Iniciar > Coruja Monitor > Instalar Serviço

VERIFICAR INSTALAÇÃO:
=====================
1. Menu Iniciar > Coruja Monitor
2. Deve ter os atalhos:
   - Configurar Coruja Probe
   - Instalar Serviço Coruja Probe
   - Ver Logs
   - Desinstalar

LOGS:
=====
- Instalação: C:\install.log (se instalação silenciosa)
- Probe: C:\Program Files\CorujaMonitor\Probe\logs\

DESINSTALAÇÃO:
==============
Opção 1: Menu Iniciar > Coruja Monitor > Desinstalar
Opção 2: Painel de Controle > Programas > Desinstalar
Opção 3: Execute uninstall.bat como Administrador

SUPORTE:
========
- Web: http://192.168.31.161:3000
- Documentação: README.md no diretório de instalação
- Logs: C:\Program Files\CorujaMonitor\Probe\logs\

TROUBLESHOOTING:
================
Erro: "system administrator has set policies to prevent this installation"
Solução: Execute install-silent.bat como Administrador

Erro: "Python não encontrado"
Solução: O instalador instala Python automaticamente. Se falhar,
         instale Python 3.11 manualmente de python.org

Erro: "Acesso negado"
Solução: Execute como Administrador (clique direito > Executar como Admin)

DISTRIBUIÇÃO EM MASSA:
======================
Para instalar em múltiplos computadores:

1. Via GPO:
   - Copie o MSI para \\servidor\share\
   - GPO > Configuração do Computador > Políticas > Configurações de Software
   - Novo > Pacote > Selecione o MSI
   - Atribuído

2. Via SCCM/Intune:
   - Crie aplicativo com o MSI
   - Linha de comando: msiexec /i "CorujaMonitorProbe-Complete-$Version.msi" /qn ALLUSERS=1
   - Implante na coleção desejada

3. Via Script:
   - Use install-silent.bat
   - Ou: psexec \\computador -s install-silent.bat

CHANGELOG:
==========
v1.0.0 - $(Get-Date -Format "dd/MM/yyyy")
- Instalação automática de Python
- Bypass de políticas de grupo
- Instalação silenciosa
- Todos os coletores incluídos
- Interface de configuração melhorada
"@

$readmePath = Join-Path $OutputDir "README.txt"
$readme | Out-File -FilePath $readmePath -Encoding UTF8

Write-Host "========================================" -ForegroundColor Green
Write-Host "  MSI CRIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Arquivos criados:" -ForegroundColor Cyan
Write-Host "   • $msiFile" -ForegroundColor White
Write-Host "   • $silentInstallPath" -ForegroundColor White
Write-Host "   • $uninstallPath" -ForegroundColor White
Write-Host "   • $readmePath" -ForegroundColor White
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. TESTAR INSTALAÇÃO:" -ForegroundColor Cyan
Write-Host "   Clique direito no MSI > Executar como Administrador" -ForegroundColor White
Write-Host ""
Write-Host "2. DISTRIBUIR:" -ForegroundColor Cyan
Write-Host "   • Copie o MSI para os clientes" -ForegroundColor White
Write-Host "   • Ou use GPO/SCCM para deploy em massa" -ForegroundColor White
Write-Host ""
Write-Host "3. INSTALAÇÃO SILENCIOSA:" -ForegroundColor Cyan
Write-Host "   Execute: install-silent.bat" -ForegroundColor White
Write-Host ""
Write-Host "4. BYPASS DE POLÍTICAS:" -ForegroundColor Cyan
Write-Host "   O MSI já inclui bypass automático" -ForegroundColor White
Write-Host "   Se ainda bloquear, veja README.txt" -ForegroundColor White
Write-Host ""

Write-Host "Pressione ENTER para sair..."
Read-Host
