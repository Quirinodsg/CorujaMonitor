#!/bin/bash
# Deploy do fix HTTPS no servidor Linux 192.168.31.161
# Corrige: SAN do certificado, WebSocket URL, cron de renovação SSL
set -e

echo "=== Fix HTTPS Coruja Monitor ==="
echo "Servidor: 192.168.31.161"
echo ""

# 1. Atualizar código
echo "[1/6] Atualizando código..."
git pull

# 2. Garantir que o entrypoint tem permissão de execução
chmod +x nginx/docker-entrypoint-ssl.sh
chmod +x scripts/generate-ssl-cert.sh
chmod +x scripts/renew-ssl-cert.sh 2>/dev/null || true

# 3. Recriar container nginx
# NOTA: docker-compose 1.29.2 tem bug com --force-recreate, usar docker rm -f + up
echo "[2/6] Recriando container nginx..."
docker rm -f coruja-nginx 2>/dev/null || true
docker-compose up -d nginx

# 4. Aguardar nginx iniciar e gerar certificado
echo "[3/6] Aguardando nginx iniciar..."
sleep 5

# 5. Verificar que nginx está rodando
echo "[4/6] Verificando containers..."
docker ps | grep coruja-nginx && echo "✅ nginx rodando" || echo "❌ nginx NÃO está rodando"

# 6. Verificar SAN do certificado gerado
echo "[5/6] Verificando certificado SSL..."
if [ -f ./nginx/ssl/coruja.crt ]; then
    openssl x509 -in ./nginx/ssl/coruja.crt -text -noout 2>/dev/null \
        | grep -A3 "Subject Alternative Name" \
        && echo "✅ Certificado com SAN OK" \
        || echo "⚠️  Verificar SAN do certificado"
else
    echo "⚠️  Certificado ainda não gerado no volume local"
    echo "   Verificando dentro do container..."
    docker exec coruja-nginx openssl x509 -in /etc/nginx/ssl/coruja.crt -text -noout 2>/dev/null \
        | grep -A3 "Subject Alternative Name" || echo "   Certificado não encontrado no container"
fi

# 7. Testar redirect HTTP→HTTPS
echo "[6/6] Testando redirect HTTP→HTTPS..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Redirect HTTP→HTTPS OK (HTTP $HTTP_CODE)"
else
    echo "⚠️  Redirect retornou HTTP $HTTP_CODE (esperado 301)"
fi

echo ""
echo "=== Deploy concluído ==="
echo ""
echo "PRÓXIMOS PASSOS:"
echo "  1. Acesse https://192.168.31.161 no browser"
echo "  2. Aceite o aviso de certificado self-signed (inevitável)"
echo "  3. Faça login com admin@coruja.com / admin123"
echo "  4. Verifique o Dashboard e WebSocket (indicador 'Tempo real')"
echo ""
echo "NOTA: O aviso de certificado no browser é esperado com self-signed."
echo "      Para suprimir, importe nginx/ssl/coruja.crt como CA confiável no browser."
