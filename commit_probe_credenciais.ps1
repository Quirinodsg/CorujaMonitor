# Commit: Probe busca credenciais WMI do banco via API

Write-Host "🔐 Enviando atualização da Probe para usar credenciais do banco..." -ForegroundColor Cyan

# Add files
git add probe/probe_core.py
git add COMECE_AQUI_PROBE_CREDENCIAIS.txt
git add COPIAR_PROBE_CORE_MANUAL_SRVSONDA001.txt
git add NOTA_CAMINHO_PROBE_SRVSONDA001.txt
git add DIAGNOSTICO_PROBE_ATUAL_12MAR.txt
git add ATUALIZAR_PROBE_CREDENCIAIS_AGORA.txt
git add RESUMO_PROBE_CREDENCIAIS_12MAR.md
git add SESSAO_12MAR_PROBE_CREDENCIAIS.md
git add FLUXO_PROBE_CREDENCIAIS_VISUAL.txt
git add CHECKLIST_VALIDACAO_PROBE.txt
git add commit_probe_credenciais.ps1

# Commit
git commit -m "feat: Probe busca credenciais WMI do banco via API (moderno como PRTG)

- Adiciona função _get_server_credential() para buscar credenciais via API
- Modifica _collect_wmi_remote() para usar credenciais do banco
- Sistema de herança: Servidor → Grupo → Empresa
- Logs informativos com emojis (🔐, ⚠️, 💡)
- Credencial descriptografada automaticamente pela API
- Compatível com sistema de credenciais centralizadas implementado

Documentação completa:
- ATUALIZAR_PROBE_CREDENCIAIS_AGORA.txt (instruções de deploy)
- RESUMO_PROBE_CREDENCIAIS_12MAR.md (documentação técnica)
- SESSAO_12MAR_PROBE_CREDENCIAIS.md (resumo da sessão)
- FLUXO_PROBE_CREDENCIAIS_VISUAL.txt (fluxo visual)
- CHECKLIST_VALIDACAO_PROBE.txt (checklist de validação)

Refs: TASK 2 - Atualizar Probe Windows para Usar Credenciais do Banco"

# Push
git push origin master

Write-Host ""
Write-Host "✅ Atualização enviada com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "   1. No servidor SRVSONDA001 (Windows):" -ForegroundColor White
Write-Host "      Stop-Service -Name 'CorujaProbe' -Force" -ForegroundColor Gray
Write-Host "      cd 'C:\Program Files\CorujaMonitor\Probe'" -ForegroundColor Gray
Write-Host "      git pull origin master" -ForegroundColor Gray
Write-Host "      Start-Service -Name 'CorujaProbe'" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Verificar logs:" -ForegroundColor White
Write-Host "      Get-Content 'C:\Program Files\CorujaMonitor\Probe\logs\probe.log' -Tail 50 -Wait" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Aguardar 60 segundos e verificar dashboard" -ForegroundColor White
Write-Host "      http://192.168.31.161:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Usar checklist de validação:" -ForegroundColor White
Write-Host "      CHECKLIST_VALIDACAO_PROBE.txt" -ForegroundColor Gray
Write-Host ""
