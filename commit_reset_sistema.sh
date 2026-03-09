#!/bin/bash

echo "========================================="
echo "  COMMIT: Sistema de Reset Implementado"
echo "========================================="
echo ""

# Adicionar arquivos
git add api/reset_sistema.py
git add api/routers/system_reset.py
git add api/main.py
git add frontend/src/components/SystemReset.js
git add frontend/src/components/SystemReset.css
git add limpar_banco_completo.py
git add adicionar_servidor_automatico.py
git add CORRIGIR_CONFIG_PROBE.bat
git add VERIFICAR_SERVIDOR_CADASTRADO.bat
git add ADICIONAR_SERVIDOR_AGORA.bat
git add CONFIGURAR_TUDO_AUTOMATICO.bat
git add EXECUTAR_ISTO_AGORA.txt
git add VER_LOGS_PROBE.bat
git add PROBLEMA_CONFIG_VAZIO.txt
git add PASSOS_RESOLVER_AGORA.txt

# Commit
git commit -m "feat: Sistema de Reset Completo + Correções Probe

- Implementado endpoint /api/v1/system/reset para apagar tudo
- Criado componente SystemReset.js no frontend
- Função administrativa para resetar: empresas, probes, sensores, servidores
- Script Python reset_sistema.py para linha de comando
- Corrigida porta do dashboard (3000 não 8000)
- Scripts BAT automáticos para configurar probe
- CONFIGURAR_TUDO_AUTOMATICO.bat faz tudo sem intervenção manual
- Mantém apenas usuário admin após reset
- Interface visual para confirmar reset (digitar RESETAR)
- Estatísticas do sistema antes de resetar"

echo ""
echo "Commit criado! Fazendo push..."
echo ""

# Push
git push origin main

echo ""
echo "========================================="
echo "  ✓ CÓDIGO ENVIADO PARA O GIT!"
echo "========================================="
echo ""
echo "No servidor Linux, execute:"
echo "  cd /caminho/do/projeto"
echo "  git pull origin main"
echo "  cd api"
echo "  python reset_sistema.py"
echo ""
