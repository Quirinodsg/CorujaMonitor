#!/bin/bash
# ========================================
# COMMIT E PUSH - AUTO-REGISTRO
# ========================================

echo "=========================================="
echo "FAZENDO COMMIT E PUSH"
echo "=========================================="

cd "/c/Users/andre.quirino/Coruja Monitor"

echo ""
echo "1. Verificando status..."
git status

echo ""
echo "2. Adicionando arquivos..."
git add .

echo ""
echo "3. Fazendo commit..."
git commit -m "Auto-registro de servidor e correcao de copia de token

- Probe cria servidor automaticamente ao iniciar
- Detecta hostname, IP e OS automaticamente  
- Endpoints /check e /auto-register na API
- Corrigido erro ao copiar token em HTTP
- Fallback para document.execCommand quando clipboard nao disponivel
- Config.yaml corrigido com porta 3000"

echo ""
echo "4. Enviando para GitHub..."
git push origin master

echo ""
echo "=========================================="
echo "✅ COMMIT E PUSH CONCLUÍDOS!"
echo "=========================================="
echo ""
echo "PRÓXIMO PASSO:"
echo "Conectar no servidor Linux e atualizar"
echo ""
