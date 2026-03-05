#!/bin/bash

echo "Enviando correção de erros nas páginas para o Git..."

git add corrigir_tabelas_banco.sh
git add EXECUTAR_AGORA_CORRIGIR_ERROS.txt
git add diagnostico_login_completo.sh
git add corrigir_login_definitivo.sh

git commit -m "fix: Corrigir erros nas páginas (Empresas, Incidentes, Relatórios, KB, IA)

- Script para criar todas as tabelas necessárias no banco
- Popular Knowledge Base com dados iniciais
- Diagnóstico completo de login
- Correção definitiva de login com senha correta"

git push origin master

echo ""
echo "✓ Arquivos enviados para o GitHub!"
echo ""
echo "Agora execute no servidor Linux:"
echo "  cd ~/CorujaMonitor"
echo "  git pull origin master"
echo "  chmod +x corrigir_tabelas_banco.sh"
echo "  ./corrigir_tabelas_banco.sh"
echo ""
