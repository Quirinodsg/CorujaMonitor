#!/bin/bash

echo "Fazendo commit da correção do login..."

git add frontend/src/components/Login.js
git add corrigir_senha_correto.sh
git add corrigir_login_final.sh
git add commit_correcao_login_final.sh

git commit -m "fix: Corrigir login para usar IP do servidor

- Login.js agora importa e usa API_URL do config.js
- config.js detecta automaticamente o IP do servidor
- Script corrigir_senha_correto.sh usa coluna correta (hashed_password)
- Script corrigir_login_final.sh faz correção completa + rebuild
- Remove uso de localhost hardcoded no Login.js"

git push origin master

echo ""
echo "✓ Commit enviado para o GitHub!"
echo ""
echo "PRÓXIMOS PASSOS NO SERVIDOR LINUX:"
echo "1. git pull origin master"
echo "2. chmod +x corrigir_login_final.sh"
echo "3. ./corrigir_login_final.sh"
echo "4. Aguardar 3 minutos para rebuild"
echo "5. Acessar em aba anônima: http://192.168.31.161:3000"
