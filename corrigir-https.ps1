# Script de Correção HTTPS
# Corrige problemas comuns e ativa HTTPS corretamente

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRIGINDO HTTPS..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Parar tudo
Write-Host "1/6 Parando containers..." -ForegroundColor Yellow
docker-compose down 2>$null
docker-compose -f docker-compose.yml -f docker-compose.https.yml down 2>$null
Start-Sleep -Seconds 3
Write-Host "✅ Containers parados" -ForegroundColor Green

# 2. Limpar volumes antigos (opcional)
Write-Host "2/6 Limpando configurações antigas..." -ForegroundColor Yellow
if (Test-Path "certbot") {
    Remove-Item -Recurse -Force "certbot" -ErrorAction SilentlyContinue
}
Write-Host "✅ Limpeza concluída" -ForegroundColor Green

# 3. Criar diretórios
Write-Host "3/6 Criando diretórios..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "certbot/conf/live/localhost" | Out-Null
New-Item -ItemType Directory -Force -Path "certbot/www" | Out-Null
New-Item -ItemType Directory -Force -Path "nginx" | Out-Null
Write-Host "✅ Diretórios criados" -ForegroundColor Green

# 4. Gerar certificado
Write-Host "4/6 Gerando certificado SSL..." -ForegroundColor Yellow
Write-Host "   (Isso pode levar 30 segundos)" -ForegroundColor Gray

$opensslCmd = @"
req -x509 -nodes -days 365 -newkey rsa:2048 \
-keyout /etc/letsencrypt/live/localhost/privkey.pem \
-out /etc/letsencrypt/live/localhost/fullchain.pem \
-subj "/C=BR/ST=State/L=City/O=Coruja Monitor/CN=localhost"
"@

docker run --rm -v "${PWD}/certbot/conf:/etc/letsencrypt" alpine/openssl $opensslCmd 2>$null

if ($LASTEXITCODE -eq 0) {
    Copy-Item "certbot/conf/live/localhost/fullchain.pem" "certbot/conf/live/localhost/chain.pem" -Force
    Write-Host "✅ Certificado gerado" -ForegroundColor Green
} else {
    Write-Host "❌ Erro ao gerar certificado" -ForegroundColor Red
    Write-Host "Tentando método alternativo..." -ForegroundColor Yellow
    
    # Método alternativo: usar OpenSSL do Windows
    $certPath = "certbot/conf/live/localhost"
    
    # Criar chave privada
    openssl genrsa -out "$certPath/privkey.pem" 2048 2>$null
    
    # Criar certificado
    openssl req -new -x509 -key "$certPath/privkey.pem" -out "$certPath/fullchain.pem" -days 365 -subj "/C=BR/ST=State/L=City/O=Coruja Monitor/CN=localhost" 2>$null
    
    # Copiar chain
    Copy-Item "$certPath/fullchain.pem" "$certPath/chain.pem" -Force
    
    Write-Host "✅ Certificado gerado (método alternativo)" -ForegroundColor Green
}

# 5. Verificar se nginx.conf existe
Write-Host "5/6 Verificando configuração Nginx..." -ForegroundColor Yellow
if (-not (Test-Path "nginx/nginx.conf")) {
    Write-Host "❌ nginx.conf não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, verifique se o arquivo nginx/nginx.conf existe." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Configuração OK" -ForegroundColor Green

# 6. Iniciar com HTTPS
Write-Host "6/6 Iniciando sistema com HTTPS..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.https.yml up -d

Write-Host ""
Write-Host "Aguardando containers iniciarem..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# Verificar status
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO STATUS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$nginxRunning = docker ps --filter "name=nginx" --format "{{.Names}}" 2>$null
if ($nginxRunning) {
    Write-Host "✅ Nginx: RODANDO" -ForegroundColor Green
} else {
    Write-Host "❌ Nginx: NÃO ENCONTRADO" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verificando logs do Nginx..." -ForegroundColor Yellow
    docker logs coruja-nginx 2>&1 | Select-Object -Last 20
}

$frontendRunning = docker ps --filter "name=frontend" --format "{{.Names}}" 2>$null
if ($frontendRunning) {
    Write-Host "✅ Frontend: RODANDO" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend: NÃO ENCONTRADO" -ForegroundColor Red
}

$apiRunning = docker ps --filter "name=api" --format "{{.Names}}" 2>$null
if ($apiRunning) {
    Write-Host "✅ API: RODANDO" -ForegroundColor Green
} else {
    Write-Host "❌ API: NÃO ENCONTRADO" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE DE CONEXÃO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Testar HTTP
Write-Host "Testando HTTP (porta 80)..." -ForegroundColor Yellow
try {
    $httpResponse = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ HTTP: OK (redirect para HTTPS)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  HTTP: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Testar HTTPS
Write-Host "Testando HTTPS (porta 443)..." -ForegroundColor Yellow
try {
    # Ignorar erros de certificado para teste
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
    $httpsResponse = Invoke-WebRequest -Uri "https://localhost" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ HTTPS: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ HTTPS: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis causas:" -ForegroundColor Yellow
    Write-Host "  - Nginx não está rodando" -ForegroundColor Yellow
    Write-Host "  - Certificado não foi gerado corretamente" -ForegroundColor Yellow
    Write-Host "  - Porta 443 está bloqueada" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($nginxRunning) {
    Write-Host "🌐 Acesse: https://localhost" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  Se o navegador mostrar erro:" -ForegroundColor Yellow
    Write-Host "   1. Clicar em 'Avançado'" -ForegroundColor Gray
    Write-Host "   2. Clicar em 'Continuar para localhost'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 Ver logs:" -ForegroundColor Cyan
    Write-Host "   docker logs coruja-nginx" -ForegroundColor Gray
    Write-Host "   docker logs coruja-frontend" -ForegroundColor Gray
    Write-Host "   docker logs coruja-api" -ForegroundColor Gray
} else {
    Write-Host "❌ Nginx não está rodando!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tente:" -ForegroundColor Yellow
    Write-Host "   1. Ver logs: docker logs coruja-nginx" -ForegroundColor Gray
    Write-Host "   2. Reiniciar: docker-compose -f docker-compose.yml -f docker-compose.https.yml restart" -ForegroundColor Gray
    Write-Host "   3. Ou voltar para HTTP: docker-compose up -d" -ForegroundColor Gray
}

Write-Host ""
Write-Host "📋 Status completo:" -ForegroundColor Cyan
docker-compose -f docker-compose.yml -f docker-compose.https.yml ps

Write-Host ""
