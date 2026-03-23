#!/bin/bash
# Renova certificado SSL se expirar em menos de 30 dias
# Adicionar ao cron: 0 3 * * * /path/to/scripts/renew-ssl-cert.sh

SSL_DIR="/etc/nginx/ssl"
CERT="$SSL_DIR/coruja.crt"
DAYS_THRESHOLD=30

if [ ! -f "$CERT" ]; then
    echo "⚠️  Certificado não encontrado em $CERT — gerando..."
    "$(dirname "$0")/generate-ssl-cert.sh"
    exit 0
fi

# Verificar data de expiração
EXPIRY=$(openssl x509 -enddate -noout -in "$CERT" | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))

echo "Certificado expira em: $EXPIRY ($DAYS_LEFT dias restantes)"

if [ "$DAYS_LEFT" -lt "$DAYS_THRESHOLD" ]; then
    echo "⚠️  Menos de $DAYS_THRESHOLD dias — renovando certificado..."
    "$(dirname "$0")/generate-ssl-cert.sh"

    # Recarregar nginx se estiver rodando
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q coruja-nginx; then
        docker exec coruja-nginx nginx -s reload
        echo "✅ Nginx recarregado"
    fi
else
    echo "✅ Certificado válido por mais $DAYS_LEFT dias — nenhuma ação necessária"
fi
