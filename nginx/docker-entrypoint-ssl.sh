#!/bin/sh
# Entrypoint customizado para nginx com SSL auto-gerado e cron de renovação

# Gerar certificado se não existir
if [ ! -f /etc/nginx/ssl/coruja.crt ]; then
    echo "[entrypoint] Gerando certificado SSL..."
    /scripts/generate-ssl-cert.sh
fi

# Configurar cron de renovação (alpine usa busybox crond)
echo "0 3 * * * /scripts/renew-ssl-cert.sh >> /var/log/ssl-renew.log 2>&1" \
    > /etc/crontabs/root
crond -b -l 8

echo "[entrypoint] Cron de renovação SSL configurado (diário às 3h)"

# Iniciar nginx em foreground
exec nginx -g "daemon off;"
