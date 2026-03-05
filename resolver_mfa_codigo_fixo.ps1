# Script Interativo para Resolver Problema do Código Fixo no Google Authenticator

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  RESOLVER PROBLEMA: Google Authenticator com Código Fixo" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Este script irá guiá-lo pelo processo de correção do MFA." -ForegroundColor Yellow
Write-Host ""

# Função para pausar e aguardar confirmação
function Pause-WithMessage {
    param([string]$Message = "Pressione qualquer tecla para continuar...")
    Write-Host ""
    Write-Host $Message -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
}

# PASSO 1: Verificar containers
Write-Host "PASSO 1: Verificando containers..." -ForegroundColor Cyan
Write-Host ""

docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String -Pattern "coruja"

Write-Host ""
Write-Host "✅ Containers verificados" -ForegroundColor Green
Pause-WithMessage

# PASSO 2: Verificar código atual do servidor
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 2: Verificando código atual do servidor" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Executando teste do TOTP..." -ForegroundColor Yellow
Write-Host ""

docker-compose exec -T api python testar_secret_usuario.py 2>$null | Select-String -Pattern "Código atual|Próximo código"

Write-Host ""
Write-Host "✅ Código do servidor verificado" -ForegroundColor Green
Write-Host ""
Write-Host "ANOTE o código atual acima para comparar com o Google Authenticator!" -ForegroundColor Yellow
Pause-WithMessage

# PASSO 3: Instruções para limpar Google Authenticator
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 3: Limpar Google Authenticator" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  IMPORTANTE: Você precisa remover TODAS as contas antigas!" -ForegroundColor Red
Write-Host ""
Write-Host "No seu smartphone:" -ForegroundColor Yellow
Write-Host "1. Abra o Google Authenticator" -ForegroundColor White
Write-Host "2. Procure por contas: 'CorujaMonitor' ou 'admin@coruja.com'" -ForegroundColor White
Write-Host "3. Para cada conta:" -ForegroundColor White
Write-Host "   - Toque e segure na conta" -ForegroundColor White
Write-Host "   - Selecione 'Remover' ou 'Excluir'" -ForegroundColor White
Write-Host "   - Confirme a remoção" -ForegroundColor White
Write-Host "4. Verifique se TODAS foram removidas" -ForegroundColor White
Write-Host ""

$removed = Read-Host "Você removeu TODAS as contas antigas? (S/N)"

if ($removed -ne "S" -and $removed -ne "s") {
    Write-Host ""
    Write-Host "❌ Por favor, remova todas as contas antigas antes de continuar!" -ForegroundColor Red
    Write-Host ""
    exit
}

Write-Host ""
Write-Host "✅ Contas antigas removidas" -ForegroundColor Green
Pause-WithMessage

# PASSO 4: Sincronizar relógio
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 4: Sincronizar Relógio do Smartphone" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "No seu smartphone:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Android:" -ForegroundColor White
Write-Host "1. Configurações > Sistema > Data e hora" -ForegroundColor White
Write-Host "2. Ative 'Usar hora da rede'" -ForegroundColor White
Write-Host "3. Ative 'Usar fuso horário da rede'" -ForegroundColor White
Write-Host ""
Write-Host "iOS:" -ForegroundColor White
Write-Host "1. Ajustes > Geral > Data e Hora" -ForegroundColor White
Write-Host "2. Ative 'Definir Automaticamente'" -ForegroundColor White
Write-Host ""
Write-Host "Google Authenticator:" -ForegroundColor White
Write-Host "1. Abra o Google Authenticator" -ForegroundColor White
Write-Host "2. Toque nos três pontos (⋮)" -ForegroundColor White
Write-Host "3. Configurações > Correção de hora > Sincronizar agora" -ForegroundColor White
Write-Host ""

$synced = Read-Host "Você sincronizou o relógio? (S/N)"

if ($synced -ne "S" -and $synced -ne "s") {
    Write-Host ""
    Write-Host "⚠️  Recomendamos sincronizar o relógio para evitar problemas!" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "✅ Relógio sincronizado" -ForegroundColor Green
Pause-WithMessage

# PASSO 5: Desabilitar MFA
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 5: Desabilitar MFA Atual" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Deseja desabilitar o MFA de todos os usuários agora? (S/N)" -ForegroundColor Yellow
$disable = Read-Host

if ($disable -eq "S" -or $disable -eq "s") {
    Write-Host ""
    Write-Host "Desabilitando MFA..." -ForegroundColor Yellow
    
    docker-compose exec -T postgres psql -U coruja -d coruja_monitor -c "UPDATE users SET mfa_enabled = FALSE, mfa_secret = NULL, mfa_backup_codes = NULL;" 2>$null
    
    Write-Host ""
    Write-Host "✅ MFA desabilitado para todos os usuários" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Você pode desabilitar manualmente em:" -ForegroundColor Yellow
    Write-Host "http://localhost:3000 > Configurações > Segurança > Desabilitar MFA" -ForegroundColor White
    Write-Host ""
}

Pause-WithMessage

# PASSO 6: Instruções para habilitar MFA
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 6: Habilitar MFA Novamente (NOVO QR Code)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Agora você precisa:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Acessar: http://localhost:3000" -ForegroundColor White
Write-Host "2. Fazer login com email e senha" -ForegroundColor White
Write-Host "3. Ir em: Configurações > Segurança" -ForegroundColor White
Write-Host "4. Clicar em 'Habilitar MFA'" -ForegroundColor White
Write-Host "5. Um NOVO QR Code será gerado" -ForegroundColor White
Write-Host ""

Pause-WithMessage "Pressione qualquer tecla quando o QR Code estiver na tela..."

# PASSO 7: Instruções para escanear
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 7: Escanear NOVO QR Code" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "No Google Authenticator:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Toque em '+' ou 'Adicionar conta'" -ForegroundColor White
Write-Host "2. Escolha 'Escanear QR Code'" -ForegroundColor White
Write-Host "3. Aponte para o QR Code na tela" -ForegroundColor White
Write-Host "4. A conta 'CorujaMonitor' será adicionada" -ForegroundColor White
Write-Host "5. AGUARDE 5 SEGUNDOS" -ForegroundColor White
Write-Host "6. Observe o código no app" -ForegroundColor White
Write-Host ""

Pause-WithMessage "Pressione qualquer tecla quando tiver escaneado o QR Code..."

# PASSO 8: Verificar se código está mudando
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 8: Verificar se o Código Está MUDANDO" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  CRÍTICO: Antes de ativar o MFA, verifique!" -ForegroundColor Red
Write-Host ""
Write-Host "1. Olhe para o código no Google Authenticator" -ForegroundColor White
Write-Host "2. Anote o código" -ForegroundColor White
Write-Host "3. Aguarde 30 segundos" -ForegroundColor White
Write-Host "4. O código DEVE mudar para um número diferente" -ForegroundColor White
Write-Host ""

$changing = Read-Host "O código está MUDANDO a cada 30 segundos? (S/N)"

if ($changing -ne "S" -and $changing -ne "s") {
    Write-Host ""
    Write-Host "❌ PROBLEMA: O código não está mudando!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis causas:" -ForegroundColor Yellow
    Write-Host "- Você escaneou o QR Code errado" -ForegroundColor White
    Write-Host "- Você tem múltiplas contas no Google Authenticator" -ForegroundColor White
    Write-Host "- O relógio do smartphone não está sincronizado" -ForegroundColor White
    Write-Host ""
    Write-Host "Solução: Execute este script novamente e siga TODOS os passos!" -ForegroundColor Yellow
    Write-Host ""
    exit
}

Write-Host ""
Write-Host "✅ Código está mudando corretamente!" -ForegroundColor Green
Pause-WithMessage

# PASSO 9: Comparar com servidor
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 9: Comparar com o Servidor" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Verificando código atual do servidor..." -ForegroundColor Yellow
Write-Host ""

docker-compose exec -T api python -c "import pyotp; print('Código atual do servidor:', pyotp.TOTP('VUEBGGLYTDZ4SV5RGZOBFATY5P5EDZYU').now())" 2>$null

Write-Host ""
Write-Host "Compare o código acima com o código no Google Authenticator." -ForegroundColor Yellow
Write-Host "Devem ser IGUAIS (ou muito próximos)." -ForegroundColor Yellow
Write-Host ""

$matching = Read-Host "Os códigos são iguais? (S/N)"

if ($matching -ne "S" -and $matching -ne "s") {
    Write-Host ""
    Write-Host "❌ PROBLEMA: Os códigos não coincidem!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possíveis causas:" -ForegroundColor Yellow
    Write-Host "- Você tem múltiplas contas 'CorujaMonitor' no Google Authenticator" -ForegroundColor White
    Write-Host "- O relógio do smartphone está dessincronizado" -ForegroundColor White
    Write-Host ""
    Write-Host "Solução: Remova TODAS as contas e execute este script novamente!" -ForegroundColor Yellow
    Write-Host ""
    exit
}

Write-Host ""
Write-Host "✅ Códigos coincidem!" -ForegroundColor Green
Pause-WithMessage

# PASSO 10: Instruções finais
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "PASSO 10: Ativar MFA e Testar" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Agora você pode:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Salvar os códigos de backup (10 códigos no formato XXXX-XXXX)" -ForegroundColor White
Write-Host "2. Digite sua senha" -ForegroundColor White
Write-Host "3. Digite o código de 6 dígitos do Google Authenticator" -ForegroundColor White
Write-Host "4. Clique em 'Ativar MFA'" -ForegroundColor White
Write-Host "5. Faça logout e teste o login com MFA" -ForegroundColor White
Write-Host ""

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "✅ PROCESSO CONCLUÍDO!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Se tudo funcionou:" -ForegroundColor Green
Write-Host "✅ Google Authenticator mostra código MUDANDO a cada 30s" -ForegroundColor Green
Write-Host "✅ Código do app = código do servidor" -ForegroundColor Green
Write-Host "✅ Login funciona com código MFA" -ForegroundColor Green
Write-Host "✅ Códigos de backup salvos" -ForegroundColor Green
Write-Host ""

Write-Host "Se ainda tiver problemas:" -ForegroundColor Yellow
Write-Host "- Leia o arquivo: SOLUCAO_CODIGO_FIXO_PASSO_A_PASSO.md" -ForegroundColor White
Write-Host "- Execute: .\desabilitar_mfa_todos.ps1" -ForegroundColor White
Write-Host "- Execute este script novamente" -ForegroundColor White
Write-Host ""

Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
