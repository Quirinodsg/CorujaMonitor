# Script de Assinatura Digital de Instaladores MSI
# Assina o instalador MSI com certificado Code Signing

param(
    [Parameter(Mandatory=$true, HelpMessage="Caminho para o arquivo MSI")]
    [string]$MsiPath,
    
    [Parameter(Mandatory=$false, HelpMessage="Thumbprint do certificado instalado")]
    [string]$CertThumbprint,
    
    [Parameter(Mandatory=$false, HelpMessage="Caminho para arquivo PFX")]
    [string]$CertPath,
    
    [Parameter(Mandatory=$false, HelpMessage="Senha do certificado PFX")]
    [string]$CertPassword,
    
    [Parameter(Mandatory=$false, HelpMessage="Criar certificado auto-assinado para desenvolvimento")]
    [switch]$CreateSelfSigned
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORUJA MONITOR - MSI SIGNING TOOL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o arquivo MSI existe
if (-not (Test-Path $MsiPath)) {
    Write-Host "❌ Arquivo MSI não encontrado: $MsiPath" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Arquivo MSI: $MsiPath" -ForegroundColor Green

# Localizar signtool.exe
$possiblePaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22000.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe"
)

$signtool = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $signtool = $path
        break
    }
}

if (-not $signtool) {
    Write-Host "❌ signtool.exe não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instale o Windows SDK:" -ForegroundColor Yellow
    Write-Host "https://developer.microsoft.com/windows/downloads/windows-sdk/" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "🔧 signtool encontrado: $signtool" -ForegroundColor Green

# Criar certificado auto-assinado se solicitado
if ($CreateSelfSigned) {
    Write-Host ""
    Write-Host "🔐 Criando certificado auto-assinado..." -ForegroundColor Cyan
    
    $cert = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject "CN=Coruja Monitor, O=Coruja Monitor, C=BR" `
        -KeyUsage DigitalSignature `
        -FriendlyName "Coruja Monitor Code Signing Certificate" `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3") `
        -KeyExportPolicy Exportable `
        -KeyLength 2048 `
        -KeyAlgorithm RSA `
        -HashAlgorithm SHA256 `
        -NotAfter (Get-Date).AddYears(3)
    
    $CertThumbprint = $cert.Thumbprint
    
    Write-Host "✅ Certificado criado com sucesso!" -ForegroundColor Green
    Write-Host "   Thumbprint: $CertThumbprint" -ForegroundColor Gray
    
    # Exportar certificado
    $certExportPath = Join-Path (Split-Path $MsiPath) "CorujaMonitor-SelfSigned.pfx"
    $certPasswordSecure = ConvertTo-SecureString -String "CorujaMonitor2026!" -Force -AsPlainText
    
    Export-PfxCertificate -Cert $cert -FilePath $certExportPath -Password $certPasswordSecure | Out-Null
    
    Write-Host "📄 Certificado exportado: $certExportPath" -ForegroundColor Green
    Write-Host "   Senha: CorujaMonitor2026!" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  ATENÇÃO: Certificado auto-assinado é apenas para DESENVOLVIMENTO!" -ForegroundColor Yellow
    Write-Host "   Para produção, adquira um certificado Code Signing de uma CA confiável." -ForegroundColor Yellow
    Write-Host ""
}

# Assinar o MSI
Write-Host ""
Write-Host "🔐 Assinando instalador MSI..." -ForegroundColor Cyan

$signSuccess = $false

if ($CertThumbprint) {
    # Assinar com certificado instalado (thumbprint)
    Write-Host "   Usando certificado instalado (Thumbprint: $CertThumbprint)" -ForegroundColor Gray
    
    $signArgs = @(
        "sign",
        "/sha1", $CertThumbprint,
        "/fd", "SHA256",
        "/t", "http://timestamp.digicert.com",
        "/d", "Coruja Monitor Probe",
        "/du", "https://github.com/Quirinodsg/CorujaMonitor",
        $MsiPath
    )
    
    & $signtool $signArgs
    $signSuccess = ($LASTEXITCODE -eq 0)
    
} elseif ($CertPath) {
    # Assinar com arquivo PFX
    Write-Host "   Usando arquivo PFX: $CertPath" -ForegroundColor Gray
    
    if (-not (Test-Path $CertPath)) {
        Write-Host "❌ Arquivo PFX não encontrado: $CertPath" -ForegroundColor Red
        exit 1
    }
    
    $signArgs = @(
        "sign",
        "/f", $CertPath,
        "/p", $CertPassword,
        "/fd", "SHA256",
        "/t", "http://timestamp.digicert.com",
        "/d", "Coruja Monitor Probe",
        "/du", "https://github.com/Quirinodsg/CorujaMonitor",
        $MsiPath
    )
    
    & $signtool $signArgs
    $signSuccess = ($LASTEXITCODE -eq 0)
    
} else {
    Write-Host "❌ Nenhum certificado fornecido!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Use uma das opções:" -ForegroundColor Yellow
    Write-Host "  -CertThumbprint <thumbprint>  : Usar certificado instalado" -ForegroundColor Yellow
    Write-Host "  -CertPath <path> -CertPassword <pwd> : Usar arquivo PFX" -ForegroundColor Yellow
    Write-Host "  -CreateSelfSigned : Criar certificado auto-assinado" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Verificar resultado
Write-Host ""
if ($signSuccess) {
    Write-Host "✅ MSI assinado com sucesso!" -ForegroundColor Green
    
    # Verificar assinatura
    Write-Host ""
    Write-Host "🔍 Verificando assinatura..." -ForegroundColor Cyan
    
    & $signtool verify /pa $MsiPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Assinatura verificada com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  INSTALADOR PRONTO PARA DISTRIBUIÇÃO" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "⚠️  Aviso: Não foi possível verificar a assinatura" -ForegroundColor Yellow
        Write-Host ""
    }
    
} else {
    Write-Host "❌ Erro ao assinar MSI!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis causas:" -ForegroundColor Yellow
    Write-Host "  - Certificado inválido ou expirado" -ForegroundColor Yellow
    Write-Host "  - Senha incorreta" -ForegroundColor Yellow
    Write-Host "  - Arquivo MSI corrompido" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Informações adicionais
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Teste o instalador em uma máquina limpa" -ForegroundColor Gray
Write-Host "  2. Verifique se não há avisos do Windows Defender" -ForegroundColor Gray
Write-Host "  3. Faça scan com antivírus (opcional)" -ForegroundColor Gray
Write-Host "  4. Distribua o instalador" -ForegroundColor Gray
Write-Host ""

# Informações do arquivo
$fileInfo = Get-Item $MsiPath
Write-Host "📊 Informações do arquivo:" -ForegroundColor Cyan
Write-Host "   Tamanho: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host "   Modificado: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
Write-Host ""

exit 0
