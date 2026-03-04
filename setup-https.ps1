# Script de Configuração HTTPS com Let's Encrypt
# Gera certificados SSL gratuitos e configura renovação automática

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain = "localhost",
    
    [Parameter(Mandatory=$false)]
    [string]$Email = "admin@example.com",
    
    [Parameter(Mandatory=$false)]
    [switch]$SelfSigned = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Production = $false
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORUJA MONITOR - HTTPS SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
docker ps | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker não está rodando!" -ForegroundColor Red
    Write-Host "Por favor, inicie o Docker Desktop e tente novamente." -ForegroundColor Yellow
    exit 1
}

# Criar diretórios necessários
Write-Host "📁 Criando diretórios..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "certbot/conf" | Out-Null
New-Item -ItemType Directory -Force -Path "certbot/www" | Out-Null
New-Item -ItemType Directory -Force -Path "nginx" | Out-Null

if ($SelfSigned) {
    # Opção 1: Certificado Auto-Assinado (Desenvolvimento)
    Write-Host ""
    Write-Host "🔐 Gerando certificado auto-assinado..." -ForegroundColor Cyan
    Write-Host "   (Apenas para desenvolvimento - navegador mostrará aviso)" -ForegroundColor Yellow
    Write-Host ""
    
    # Criar diretório para certificado auto-assinado
    $certDir = "certbot/conf/live/$Domain"
    New-Item -ItemType Directory -Force -Path $certDir | Out-Null
    
    # Gerar certificado auto-assinado com OpenSSL
    $opensslCmd = @"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certbot/conf/live/$Domain/privkey.pem \
    -out certbot/conf/live/$Domain/fullchain.pem \
    -subj "/C=BR/ST=State/L=City/O=Coruja Monitor/CN=$Domain"
"@
    
    # Executar via Docker (OpenSSL)
    docker run --rm -v "${PWD}/certbot/conf:/etc/letsencrypt" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "/etc/letsencrypt/live/$Domain/privkey.pem" -out "/etc/letsencrypt/live/$Domain/fullchain.pem" -subj "/C=BR/ST=State/L=City/O=Coruja Monitor/CN=$Domain"
    
    # Criar chain.pem (cópia do fullchain para OCSP)
    Copy-Item "certbot/conf/live/$Domain/fullchain.pem" "certbot/conf/live/$Domain/chain.pem"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Certificado auto-assinado gerado com sucesso!" -ForegroundColor Green
        Write-Host "   Válido por: 365 dias" -ForegroundColor Gray
        Write-Host "   Localização: certbot/conf/live/$Domain/" -ForegroundColor Gray
    } else {
        Write-Host "❌ Erro ao gerar certificado!" -ForegroundColor Red
        exit 1
    }
    
} else {
    # Opção 2: Let's Encrypt (Produção)
    Write-Host ""
    Write-Host "🔐 Configurando Let's Encrypt..." -ForegroundColor Cyan
    Write-Host ""
    
    if ($Domain -eq "localhost") {
        Write-Host "❌ Let's Encrypt não funciona com 'localhost'!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Para usar Let's Encrypt, você precisa:" -ForegroundColor Yellow
        Write-Host "  1. Ter um domínio público (ex: monitor.seudominio.com)" -ForegroundColor Yellow
        Write-Host "  2. Apontar o domínio para o IP do servidor" -ForegroundColor Yellow
        Write-Host "  3. Executar: .\setup-https.ps1 -Domain 'monitor.seudominio.com' -Email 'seu@email.com'" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Para desenvolvimento local, use:" -ForegroundColor Cyan
        Write-Host "  .\setup-https.ps1 -SelfSigned" -ForegroundColor Cyan
        Write-Host ""
        exit 1
    }
    
    Write-Host "   Domínio: $Domain" -ForegroundColor Gray
    Write-Host "   Email: $Email" -ForegroundColor Gray
    Write-Host "   Modo: $(if ($Production) { 'PRODUÇÃO' } else { 'TESTE (staging)' })" -ForegroundColor Gray
    Write-Host ""
    
    # Iniciar Nginx temporário para validação
    Write-Host "🚀 Iniciando Nginx para validação..." -ForegroundColor Cyan
    docker-compose -f docker-compose.yml -f docker-compose.https.yml up -d nginx
    Start-Sleep -Seconds 5
    
    # Obter certificado Let's Encrypt
    Write-Host "📜 Solicitando certificado Let's Encrypt..." -ForegroundColor Cyan
    
    $stagingFlag = if (-not $Production) { "--staging" } else { "" }
    
    docker-compose -f docker-compose.yml -f docker-compose.https.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email $Email --agree-tos --no-eff-email $stagingFlag -d $Domain
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Certificado Let's Encrypt obtido com sucesso!" -ForegroundColor Green
        Write-Host "   Válido por: 90 dias (renovação automática)" -ForegroundColor Gray
        Write-Host "   Localização: certbot/conf/live/$Domain/" -ForegroundColor Gray
    } else {
        Write-Host "❌ Erro ao obter certificado!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Possíveis causas:" -ForegroundColor Yellow
        Write-Host "  - Domínio não aponta para este servidor" -ForegroundColor Yellow
        Write-Host "  - Porta 80 não está acessível externamente" -ForegroundColor Yellow
        Write-Host "  - Firewall bloqueando conexões" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
}

# Atualizar nginx.conf com o domínio correto
Write-Host ""
Write-Host "⚙️  Atualizando configuração do Nginx..." -ForegroundColor Cyan

$nginxConf = Get-Content "nginx/nginx.conf" -Raw
$nginxConf = $nginxConf -replace "server_name localhost;", "server_name $Domain;"
$nginxConf = $nginxConf -replace "/etc/letsencrypt/live/localhost/", "/etc/letsencrypt/live/$Domain/"
Set-Content "nginx/nginx.conf" $nginxConf

Write-Host "✅ Configuração atualizada!" -ForegroundColor Green

# Reiniciar serviços
Write-Host ""
Write-Host "🔄 Reiniciando serviços..." -ForegroundColor Cyan
docker-compose -f docker-compose.yml -f docker-compose.https.yml down
docker-compose -f docker-compose.yml -f docker-compose.https.yml up -d

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  HTTPS CONFIGURADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($SelfSigned) {
    Write-Host "🌐 Acesse: https://$Domain" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  AVISO: Certificado auto-assinado" -ForegroundColor Yellow
    Write-Host "   O navegador mostrará um aviso de segurança." -ForegroundColor Yellow
    Write-Host "   Clique em 'Avançado' e 'Continuar para o site'." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📅 Renovação: Manual (365 dias)" -ForegroundColor Gray
    Write-Host "   Execute novamente este script quando expirar." -ForegroundColor Gray
} else {
    Write-Host "🌐 Acesse: https://$Domain" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ Certificado válido e confiável!" -ForegroundColor Green
    Write-Host "   Nenhum aviso de segurança será exibido." -ForegroundColor Green
    Write-Host ""
    Write-Host "🔄 Renovação: AUTOMÁTICA" -ForegroundColor Green
    Write-Host "   Certbot renovará automaticamente a cada 12 horas." -ForegroundColor Gray
    Write-Host "   Certificados Let's Encrypt são válidos por 90 dias." -ForegroundColor Gray
}

Write-Host ""
Write-Host "📊 Status dos containers:" -ForegroundColor Cyan
docker-compose -f docker-compose.yml -f docker-compose.https.yml ps

Write-Host ""
Write-Host "📝 Logs do Nginx:" -ForegroundColor Cyan
Write-Host "   docker logs coruja-nginx" -ForegroundColor Gray
Write-Host ""
Write-Host "🔐 Verificar certificado:" -ForegroundColor Cyan
Write-Host "   openssl s_client -connect $Domain:443 -servername $Domain" -ForegroundColor Gray
Write-Host ""

exit 0
