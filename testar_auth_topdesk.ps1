# Teste de Autenticação TOPdesk
$url = "https://grupotechbiz.topdesk.net/tas/api/incidents"
$user = "coruja.monitor"
$pass = "adminOpLwqa!0"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Testando Autenticação TOPdesk" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL: $url"
Write-Host "Usuário: $user"
Write-Host "Senha: $('*' * $pass.Length)"
Write-Host ""

$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${user}:${pass}"))
$headers = @{
    "Authorization" = "Basic $base64"
    "Content-Type" = "application/json"
}

try {
    Write-Host "Enviando requisição..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers -ErrorAction Stop
    
    Write-Host ""
    Write-Host "✅ SUCESSO! Autenticação funcionou!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalhes:" -ForegroundColor Cyan
    Write-Host "- Incidentes encontrados: $($response.Count)"
    Write-Host "- API está acessível"
    Write-Host "- Credenciais estão corretas"
    Write-Host ""
    Write-Host "Próximo passo:" -ForegroundColor Yellow
    Write-Host "1. Volte ao Coruja Monitor"
    Write-Host "2. Clique em 'Testar Criação de Chamado'"
    Write-Host "3. Deve funcionar agora!"
    
} catch {
    Write-Host ""
    Write-Host "❌ ERRO! Autenticação falhou!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Detalhes do erro:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message
    Write-Host ""
    
    if ($_.Exception.Message -like "*401*" -or $_.Exception.Message -like "*Unauthorized*") {
        Write-Host "Causa: Credenciais inválidas ou sem permissão de API" -ForegroundColor Red
        Write-Host ""
        Write-Host "Soluções:" -ForegroundColor Cyan
        Write-Host "1. Verifique se usuário e senha estão corretos"
        Write-Host "2. Tente fazer login manual em: https://grupotechbiz.topdesk.net"
        Write-Host "3. Verifique se o usuário tem permissão de API no TOPdesk"
        Write-Host "4. Verifique se precisa de 'Application Password'"
        Write-Host ""
        Write-Host "Como habilitar permissão de API:" -ForegroundColor Yellow
        Write-Host "1. Login como admin no TOPdesk"
        Write-Host "2. Configurações > Operadores > Operadores"
        Write-Host "3. Procure: coruja.monitor"
        Write-Host "4. Aba Permissões > Marque 'API Access'"
    } elseif ($_.Exception.Message -like "*404*") {
        Write-Host "Causa: URL incorreta ou API não disponível" -ForegroundColor Red
        Write-Host ""
        Write-Host "Soluções:" -ForegroundColor Cyan
        Write-Host "1. Verifique se a URL está correta"
        Write-Host "2. Teste acessar: https://grupotechbiz.topdesk.net no navegador"
    } else {
        Write-Host "Causa: Erro de conexão ou outro problema" -ForegroundColor Red
        Write-Host ""
        Write-Host "Soluções:" -ForegroundColor Cyan
        Write-Host "1. Verifique sua conexão com a internet"
        Write-Host "2. Verifique se o firewall não está bloqueando"
        Write-Host "3. Tente acessar a URL no navegador"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
pause
