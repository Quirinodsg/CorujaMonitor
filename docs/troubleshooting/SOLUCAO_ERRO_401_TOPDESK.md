# 🔴 ERRO 401 - TOPdesk Unauthorized

## 🐛 Problema Identificado

O TOPdesk está retornando **erro 401 - Unauthorized**, o que significa que as credenciais não estão sendo aceitas.

```
Erro 401 - Unauthorized
The request has not been applied because it lacks valid authentication credentials.
```

## 🔍 Causas Possíveis

### 1. Credenciais Incorretas
- Usuário: `coruja.monitor`
- Senha: `adminOpLwqa!0`
- Um deles pode estar incorreto

### 2. Usuário Sem Permissão de API
- O usuário existe no TOPdesk
- MAS não tem permissão para usar a API REST
- Precisa habilitar "Application Password" ou "API Access"

### 3. Usuário Bloqueado ou Inativo
- Usuário pode estar desativado
- Conta pode estar bloqueada por tentativas de login

### 4. Tipo de Autenticação Incorreto
- TOPdesk pode exigir autenticação diferente
- Pode precisar de token em vez de Basic Auth

## ✅ Soluções

### Solução 1: Verificar Credenciais Manualmente

**Teste 1 - Login no Navegador:**
1. Abra: `https://grupotechbiz.topdesk.net`
2. Faça login com:
   - Usuário: `coruja.monitor`
   - Senha: `adminOpLwqa!0`
3. Se NÃO conseguir fazer login:
   - ❌ Credenciais estão incorretas
   - Corrija usuário ou senha

**Teste 2 - Testar API Diretamente (PowerShell):**
```powershell
$url = "https://grupotechbiz.topdesk.net/tas/api/incidents"
$user = "coruja.monitor"
$pass = "adminOpLwqa!0"
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${user}:${pass}"))
$headers = @{
    "Authorization" = "Basic $base64"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
    Write-Host "✅ Autenticação funcionou!" -ForegroundColor Green
    Write-Host "Incidentes encontrados: $($response.Count)"
} catch {
    Write-Host "❌ Erro de autenticação!" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
```

### Solução 2: Habilitar Permissões de API no TOPdesk

**Passo 1: Verificar se o usuário tem permissão de API**

1. Faça login no TOPdesk como **administrador**
2. Vá em: **Configurações** > **Operadores** > **Operadores**
3. Procure por: `coruja.monitor`
4. Clique para editar
5. Verifique a aba **"Permissões"** ou **"API"**
6. Certifique-se que está marcado:
   - ✅ **"Application Password"** ou
   - ✅ **"API Access"** ou
   - ✅ **"REST API"**

**Passo 2: Criar Application Password (se necessário)**

Alguns TOPdesk exigem uma senha específica para API:

1. No perfil do usuário `coruja.monitor`
2. Procure por **"Application Passwords"**
3. Clique em **"Generate New Password"**
4. Copie a senha gerada
5. Use ESSA senha no Coruja Monitor (não a senha normal)

### Solução 3: Verificar Tipo de Usuário

O usuário `coruja.monitor` precisa ser:
- ✅ **Pessoa** (Person) - para ser requisitante
- ✅ **Ativo** (Active)
- ✅ **Não bloqueado**

**Como verificar:**
1. Login como admin no TOPdesk
2. Vá em: **Suporte** > **Pessoas**
3. Procure: `coruja.monitor`
4. Verifique:
   - Status: Ativo
   - Tipo: Pessoa
   - Email: Preenchido (pode ser necessário)

### Solução 4: Criar Usuário Específico para API

Se o `coruja.monitor` não funcionar, crie um usuário específico:

**Passo 1: Criar novo usuário no TOPdesk**
1. Login como admin
2. **Suporte** > **Pessoas** > **Novo**
3. Preencha:
   - Nome: `Coruja Monitor API`
   - Login: `coruja.api`
   - Email: `coruja.api@grupotechbiz.com.br`
   - Senha: [senha forte]
   - Status: Ativo

**Passo 2: Habilitar permissões de API**
1. Edite o usuário criado
2. Aba **Permissões**
3. Marque: **API Access** ou **Application Password**
4. Salve

**Passo 3: Configurar no Coruja Monitor**
- Usuário: `coruja.api`
- Senha: [senha do usuário]

## 🧪 Teste Rápido

Execute este comando para testar a autenticação:

```powershell
# Salve como: testar_auth_topdesk.ps1
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
pause
```

## 📋 Checklist de Verificação

- [ ] Testei fazer login manual no TOPdesk com as mesmas credenciais
- [ ] Login manual funcionou
- [ ] Verifiquei se o usuário está ativo
- [ ] Verifiquei se o usuário tem permissão de API
- [ ] Testei a autenticação com PowerShell
- [ ] Se necessário, criei Application Password
- [ ] Se necessário, criei novo usuário específico para API
- [ ] Atualizei as credenciais no Coruja Monitor
- [ ] Salvei a configuração
- [ ] Testei novamente

## 🎯 Próximos Passos

1. **Execute o teste de autenticação** (PowerShell acima)
2. **Se falhar**: Siga as soluções 1, 2 ou 3
3. **Se funcionar**: Volte ao Coruja Monitor e teste novamente
4. **Aguarde 10 segundos** após reiniciar a API
5. **Recarregue o frontend** (Ctrl+Shift+R)

## 📞 Informações Importantes

**Suas credenciais:**
- URL: `https://grupotechbiz.topdesk.net`
- Usuário: `coruja.monitor`
- Senha: `adminOpLwqa!0`

**Teste manual:**
1. Abra `https://grupotechbiz.topdesk.net` no navegador
2. Faça login com as credenciais acima
3. Se funcionar → Problema é permissão de API
4. Se não funcionar → Problema é credencial incorreta

---

**Status**: Aguardando verificação das credenciais e permissões de API
