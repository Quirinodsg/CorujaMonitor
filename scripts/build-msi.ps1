# Build Windows MSI Installer for Coruja Monitoring
# Requires: WiX Toolset, Python, PyInstaller

param(
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Building Windows MSI Installer" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar WiX Toolset
if (-not (Get-Command candle.exe -ErrorAction SilentlyContinue)) {
    Write-Host "❌ WiX Toolset não encontrado!" -ForegroundColor Red
    Write-Host "Instale com: choco install wixtoolset" -ForegroundColor Yellow
    exit 1
}

# Criar diretório de build
$buildDir = "build/windows"
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

# 1. Compilar executáveis com PyInstaller
Write-Host "Compilando executáveis..." -ForegroundColor Yellow

# API
pyinstaller --onefile --windowed `
    --name coruja-api `
    --icon installer/coruja.ico `
    --add-data "api/templates;api/templates" `
    --hidden-import uvicorn `
    --hidden-import fastapi `
    api/main.py

# Probe
pyinstaller --onefile `
    --name coruja-probe `
    --icon installer/coruja.ico `
    --hidden-import wmi `
    --hidden-import pysnmp `
    probe/probe_core.py

# AI Agent
pyinstaller --onefile `
    --name coruja-ai `
    --icon installer/coruja.ico `
    --hidden-import ollama `
    ai-agent/main.py

Write-Host "✓ Executáveis compilados" -ForegroundColor Green

# 2. Copiar arquivos para build
Write-Host "Preparando arquivos de instalação..." -ForegroundColor Yellow

Copy-Item -Path "dist/coruja-api.exe" -Destination "$buildDir/"
Copy-Item -Path "dist/coruja-probe.exe" -Destination "$buildDir/"
Copy-Item -Path "dist/coruja-ai.exe" -Destination "$buildDir/"

# Copiar frontend build
if (Test-Path "frontend/build") {
    Copy-Item -Path "frontend/build" -Destination "$buildDir/frontend" -Recurse
}

# Copiar arquivos de configuração
Copy-Item -Path ".env.example" -Destination "$buildDir/.env"
Copy-Item -Path "docker-compose.yml" -Destination "$buildDir/"
Set-Content -Path "$buildDir/version.txt" -Value $Version

Write-Host "✓ Arquivos preparados" -ForegroundColor Green

# 3. Gerar WiX source
Write-Host "Gerando WiX source..." -ForegroundColor Yellow

$wixSource = @"
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="Coruja Monitoring System" 
           Language="1033" 
           Version="$Version" 
           Manufacturer="Coruja Team"
           UpgradeCode="12345678-1234-1234-1234-123456789012">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine"
             Description="Sistema de Monitoramento de Infraestrutura com IA"
             Comments="Coruja Monitoring v$Version" />
    
    <MajorUpgrade DowngradeErrorMessage="Uma versão mais recente já está instalada." />
    <MediaTemplate EmbedCab="yes" />
    
    <Feature Id="ProductFeature" Title="Coruja Monitoring" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
      <ComponentGroupRef Id="ServiceComponents" />
    </Feature>
    
    <Icon Id="CorujaIcon" SourceFile="installer\coruja.ico" />
    <Property Id="ARPPRODUCTICON" Value="CorujaIcon" />
    
    <!-- Diretórios -->
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFiles64Folder">
        <Directory Id="INSTALLFOLDER" Name="Coruja Monitoring">
          <Directory Id="BinFolder" Name="bin" />
          <Directory Id="FrontendFolder" Name="frontend" />
        </Directory>
      </Directory>
      
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="Coruja Monitoring"/>
      </Directory>
    </Directory>
    
    <!-- Componentes -->
    <ComponentGroup Id="ProductComponents" Directory="BinFolder">
      <Component Id="CorujaAPI" Guid="*">
        <File Source="$buildDir\coruja-api.exe" KeyPath="yes" />
      </Component>
      <Component Id="CorujaProbe" Guid="*">
        <File Source="$buildDir\coruja-probe.exe" />
      </Component>
      <Component Id="CorujaAI" Guid="*">
        <File Source="$buildDir\coruja-ai.exe" />
      </Component>
      <Component Id="ConfigFiles" Guid="*">
        <File Source="$buildDir\.env" />
        <File Source="$buildDir\version.txt" />
      </Component>
    </ComponentGroup>
    
    <!-- Serviços Windows -->
    <ComponentGroup Id="ServiceComponents" Directory="BinFolder">
      <Component Id="CorujaAPIService" Guid="*">
        <File Source="$buildDir\coruja-api.exe" KeyPath="yes" />
        <ServiceInstall Id="CorujaAPIServiceInstall"
                       Name="CorujaAPI"
                       DisplayName="Coruja Monitoring API"
                       Description="Serviço de API do Coruja Monitoring"
                       Type="ownProcess"
                       Start="auto"
                       ErrorControl="normal"
                       Account="LocalSystem">
          <ServiceDependency Id="Tcpip" />
        </ServiceInstall>
        <ServiceControl Id="StartCorujaAPIService" 
                       Name="CorujaAPI" 
                       Start="install" 
                       Stop="both" 
                       Remove="uninstall" />
      </Component>
      
      <Component Id="CorujaProbeService" Guid="*">
        <File Source="$buildDir\coruja-probe.exe" KeyPath="yes" />
        <ServiceInstall Id="CorujaProbeServiceInstall"
                       Name="CorujaProbe"
                       DisplayName="Coruja Monitoring Probe"
                       Description="Sonda de coleta do Coruja Monitoring"
                       Type="ownProcess"
                       Start="auto"
                       ErrorControl="normal"
                       Account="LocalSystem" />
        <ServiceControl Id="StartCorujaProbeService" 
                       Name="CorujaProbe" 
                       Start="install" 
                       Stop="both" 
                       Remove="uninstall" />
      </Component>
    </ComponentGroup>
    
    <!-- Atalhos -->
    <DirectoryRef Id="ApplicationProgramsFolder">
      <Component Id="ApplicationShortcut" Guid="*">
        <Shortcut Id="ApplicationStartMenuShortcut"
                 Name="Coruja Monitoring"
                 Description="Sistema de Monitoramento"
                 Target="http://localhost:3000"
                 WorkingDirectory="INSTALLFOLDER"/>
        <RemoveFolder Id="CleanUpShortCut" Directory="ApplicationProgramsFolder" On="uninstall"/>
        <RegistryValue Root="HKCU" Key="Software\Coruja\Monitoring" Name="installed" Type="integer" Value="1" KeyPath="yes"/>
      </Component>
    </DirectoryRef>
    
    <!-- UI -->
    <UIRef Id="WixUI_InstallDir" />
    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />
    
  </Product>
</Wix>
"@

Set-Content -Path "installer/coruja-generated.wxs" -Value $wixSource
Write-Host "✓ WiX source gerado" -ForegroundColor Green

# 4. Compilar MSI
Write-Host "Compilando MSI..." -ForegroundColor Yellow

candle.exe installer/coruja-generated.wxs -out installer/coruja.wixobj
light.exe installer/coruja.wixobj `
    -out "installer/CorujaMonitoring-$Version.msi" `
    -ext WixUIExtension `
    -cultures:en-us

Write-Host "✓ MSI compilado" -ForegroundColor Green

# 5. Limpar arquivos temporários
Write-Host "Limpando arquivos temporários..." -ForegroundColor Yellow
Remove-Item -Path "installer/*.wixobj" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "installer/*.wixpdb" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✓ Instalador MSI criado com sucesso!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Arquivo: installer/CorujaMonitoring-$Version.msi" -ForegroundColor Cyan

$msiFile = Get-Item "installer/CorujaMonitoring-$Version.msi"
Write-Host "Tamanho: $([math]::Round($msiFile.Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para instalar:" -ForegroundColor Yellow
Write-Host "  msiexec /i installer\CorujaMonitoring-$Version.msi" -ForegroundColor White
