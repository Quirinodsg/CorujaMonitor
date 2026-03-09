@echo off
chcp 65001 >nul
cls
echo ════════════════════════════════════════════════════════════════
echo   ENVIAR ALTERAÇÕES PARA GIT
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script vai:
echo   1. Adicionar todos os arquivos modificados
echo   2. Criar commit com mensagem descritiva
echo   3. Enviar para GitHub (branch master)
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 1: Verificar status
echo ════════════════════════════════════════════════════════════════
echo.

git status

echo.
echo ════════════════════════════════════════════════════════════════
echo   PASSO 2: Adicionar arquivos
echo ════════════════════════════════════════════════════════════════
echo.

git add .

echo [OK] Arquivos adicionados
echo.

echo ════════════════════════════════════════════════════════════════
echo   PASSO 3: Criar commit
echo ════════════════════════════════════════════════════════════════
echo.

git commit -m "feat: Filtro CD-ROM, Auto-start probe e correcao exclusao sensores - 09/03/2026" -m "- Adicionado filtro para ignorar CD-ROM/DVD no disk_collector.py" -m "- Criado script para instalar probe como servico Windows (auto-start)" -m "- Corrigido exclusao de sensores via interface web (fallback para desativar)" -m "- Adicionado suporte para is_active no endpoint PUT /sensors/{id}" -m "- Melhorado tratamento de erros no frontend" -m "- Corrigida porta no config.yaml (8000 em vez de 3000)" -m "- Criados scripts de instalacao e documentacao"

echo [OK] Commit criado
echo.

echo ════════════════════════════════════════════════════════════════
echo   PASSO 4: Enviar para GitHub
echo ════════════════════════════════════════════════════════════════
echo.

git push origin master

echo.
echo ════════════════════════════════════════════════════════════════
echo   CONCLUÍDO!
echo ════════════════════════════════════════════════════════════════
echo.
echo ✓ Alterações enviadas para GitHub
echo ✓ Branch: master
echo ✓ Repositório: https://github.com/Quirinodsg/CorujaMonitor
echo.
echo AGORA NO SERVIDOR LINUX:
echo   cd /home/administrador/CorujaMonitor
echo   git pull origin master
echo   docker-compose restart api frontend
echo.
echo ════════════════════════════════════════════════════════════════
pause
