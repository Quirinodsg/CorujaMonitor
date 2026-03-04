# Solução Final: Descoberta de Serviços

## Problema Identificado

O frontend está tentando buscar serviços para o servidor com ID 1, mas esse servidor não existe no banco de dados.

**Erro nos logs:**
```
Server 1 not found for tenant 1
404 Not Found
```

**Servidor correto:** ID 8 (como mostra nas outras requisições: `server_id=8`)

## Por Que Acontece

Você provavelmente:
1. Deletou um servidor antigo (ID 1)
2. Criou um novo servidor (ID 8)
3. O frontend ainda está tentando usar o servidor antigo

## Solução

### Opção 1: Selecionar o Servidor Correto

1. Vá em "Servidores"
2. **Clique no servidor correto** (o que aparece na lista, provavelmente DESKTOP-P9VGN04)
3. Agora clique em "Adicionar Sensor"
4. Escolha "Serviço do Windows"
5. Deve funcionar!

### Opção 2: Recarregar a Página

1. Pressione F5 para recarregar a página
2. Vá em "Servidores"
3. Selecione o servidor
4. Clique em "Adicionar Sensor"

## Como Confirmar Que Está Funcionando

Quando funcionar, você verá nos logs da API:

```
Discovering services for server_id=8, user=admin@coruja.com
Found server: DESKTOP-P9VGN04 (ID: 8)
Found X services on DESKTOP-P9VGN04
```

E no frontend, a lista de serviços vai mostrar TODOS os serviços do Windows, não apenas 6-7 padrão.

## Teste Manual (Se Ainda Não Funcionar)

Execute no PowerShell para confirmar que o backend funciona:

```powershell
# Login
$body = @{username="admin@coruja.com"; password="admin123"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json"
$token = $response.access_token

# Buscar serviços do servidor correto (ID 8)
$headers = @{Authorization = "Bearer $token"}
$services = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/probe-commands/services/8" -Headers $headers

# Ver resultado
Write-Host "Total de serviços: $($services.count)"
$services.services | Select-Object -First 10 | Format-Table name, display_name, status
```

Isso deve retornar uma lista completa de serviços.

## Status

✅ Backend: 100% funcional
✅ Endpoint: Correto e testado
✅ PowerShell: Executando e retornando dados
❌ Frontend: Usando servidor ID errado (1 ao invés de 8)

## Próximo Passo

**Selecione o servidor correto antes de clicar em "Adicionar Sensor"!**

O servidor correto é o que aparece na lista de servidores (ID 8), não um servidor antigo que foi deletado (ID 1).
