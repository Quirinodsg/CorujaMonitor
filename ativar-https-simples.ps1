# Script Simplificado para Ativar HTTPS
# Executa automaticamente todas as etapas

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATIVANDO HTTPS - AGUARDE..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Docker
Write-Host "1/5 Verificando Docker..." -ForegroundColor Yellow
docker ps | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker não está rodando!" -ForegroundColor Red
    Write-Host "Por favor, inicie o Docker Desktop e execute novamente." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker OK" -ForegroundColor Green

# 2. Criar diretórios
Write-Host "2/5 Criando diretórios..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "certbot/conf/live/localhost" | Out-Null
New-Item -ItemType Directory -Force -Path "certbot/www" | Out-Null
New-Item -ItemType Directory -Force -Path "nginx" | Out-Null
Write-Host "✅ Diretórios criados" -ForegroundColor Green

# 3. Gerar certificado auto-assinado
Write-Host "3/5 Gerando certificado SSL..." -ForegroundColor Yellow
docker run --rm -v "${PWD}/certbot/conf:/etc/letsencrypt" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "/etc/letsencrypt/live/localhost/privkey.pem" -out "/etc/letsencrypt/live/localhost/fullchain.pem" -subj "/C=BR/ST=State/L=City/O=Coruja Monitor/CN=localhost" 2>$null
Copy-Item "certbot/conf/live/localhost/fullchain.pem" "certbot/conf/live/localhost/chain.pem" -Force
Write-Host "✅ Certificado gerado" -ForegroundColor Green

# 4. Parar containers atuais
Write-Host "4/5 Parando containers atuais..." -ForegroundColor Yellow
docker-compose down 2>$null
Write-Host "✅ Containers parados" -ForegroundColor Green

# 5. Iniciar com HTTPS
Write-Host "5/5 Iniciando sistema com HTTPS..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.https.yml up -d
Start-Sleep -Seconds 10
Write-Host "✅ Sistema iniciado" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  HTTPS ATIVADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Acesse: https://localhost" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   O navegador mostrará um aviso de segurança." -ForegroundColor Yellow
Write-Host "   Isso é NORMAL para certificados auto-assinados." -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 Como aceitar o certificado:" -ForegroundColor Cyan
Write-Host "   1. Clicar em 'Avançado'" -ForegroundColor Gray
Write-Host "   2. Clicar em 'Continuar para localhost (não seguro)'" -ForegroundColor Gray
Write-Host "   3. Pronto! Sistema funcionando em HTTPS" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Status dos containers:" -ForegroundColor Cyan
docker-compose -f docker-compose.yml -f docker-compose.https.yml ps
Write-Host ""
