# Instruções para Limpar Cache do Navegador - 27/02/2026

## ✅ STATUS ATUAL

- ✅ Backend corrigido (ordem dos routers ajustada)
- ✅ Frontend reconstruído e compilado
- ✅ Endpoint testado via PowerShell (funcionando)
- ⚠️ Navegador ainda com cache antigo

## 🔧 PROBLEMA

O erro `SyntaxError: Unexpected token '<'` ainda aparece porque:
1. O navegador está usando código JavaScript em cache
2. O código antigo ainda tenta acessar o endpoint da forma errada
3. Mesmo com Ctrl+F5, alguns navegadores mantêm cache de service workers

## 📋 SOLUÇÃO: LIMPAR CACHE COMPLETAMENTE

### Opção 1: Hard Refresh (Mais Rápido)

**Chrome/Edge:**
1. Abrir DevTools (F12)
2. Clicar com botão direito no ícone de reload
3. Selecionar "Empty Cache and Hard Reload"

**Firefox:**
1. Pressionar Ctrl+Shift+Delete
2. Selecionar "Cache"
3. Clicar em "Clear Now"
4. Recarregar com Ctrl+F5

### Opção 2: Limpar Cache Manualmente

**Chrome/Edge:**
```
1. Abrir DevTools (F12)
2. Ir em Application (ou Aplicativo)
3. No menu lateral:
   - Storage → Clear site data
   - Service Workers → Unregister
   - Cache Storage → Delete all
4. Fechar DevTools
5. Recarregar com Ctrl+F5
```

**Firefox:**
```
1. Abrir DevTools (F12)
2. Ir em Storage (ou Armazenamento)
3. Clicar com direito em cada item:
   - Cache Storage → Delete All
   - Service Workers → Unregister
4. Fechar DevTools
5. Recarregar com Ctrl+F5
```

### Opção 3: Modo Anônimo (Teste Rápido)

```
1. Abrir janela anônima/privada
   - Chrome/Edge: Ctrl+Shift+N
   - Firefox: Ctrl+Shift+P
2. Acessar http://localhost:3000
3. Fazer login
4. Testar Métricas Grafana
```

Se funcionar no modo anônimo, confirma que é cache!

### Opção 4: Desabilitar Cache (Desenvolvimento)

**Chrome/Edge/Firefox:**
```
1. Abrir DevTools (F12)
2. Ir em Network (ou Rede)
3. Marcar checkbox "Disable cache"
4. Manter DevTools aberto
5. Recarregar página
```

## 🧪 COMO TESTAR APÓS LIMPAR CACHE

### 1. Verificar no Console

Abrir DevTools (F12) → Console

**Deve aparecer:**
```
✓ User authenticated from localStorage: admin@coruja.com
Request to: /api/v1/metrics/dashboard/servers?range=24h with token
```

**NÃO deve aparecer:**
```
❌ Error fetching metrics: SyntaxError: Unexpected token '<'
```

### 2. Verificar no Network

Abrir DevTools (F12) → Network

**Procurar requisição:**
```
/api/v1/metrics/dashboard/servers?range=24h
```

**Verificar:**
- Status: 200 OK (não 404)
- Response: JSON (não HTML)
- Headers: Authorization presente

### 3. Testar Métricas Grafana

```
1. Clicar em Dashboard
2. Clicar em Métricas (Grafana)
3. Deve carregar e mostrar:
   - Gauges de CPU, Memória, Disco
   - Gráficos de linha
   - Cards de servidores
```

## 🔍 SE AINDA NÃO FUNCIONAR

### Verificar Service Worker

**Chrome/Edge:**
```
1. Abrir chrome://serviceworker-internals/
2. Procurar por localhost:3000
3. Clicar em "Unregister"
4. Recarregar página
```

**Firefox:**
```
1. Abrir about:debugging#/runtime/this-firefox
2. Procurar por localhost:3000
3. Clicar em "Unregister"
4. Recarregar página
```

### Verificar se Frontend está Rodando

```powershell
docker ps | Select-String frontend
```

Deve mostrar:
```
coruja-frontend   Up X minutes   0.0.0.0:3000->3000/tcp
```

### Testar Endpoint Diretamente

```powershell
$body = '{"email":"admin@coruja.com","password":"admin123"}'
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json"
$token = $response.access_token
$headers = @{Authorization="Bearer $token"}
$result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h" -Headers $headers
$result.summary
```

Se retornar dados, o backend está OK!

## ✅ CONFIRMAÇÃO DE SUCESSO

Quando funcionar, você verá:

**Console:**
```
✓ User authenticated
Request to: /api/v1/metrics/dashboard/servers?range=24h with token
(sem erros)
```

**Página:**
- Gauges mostrando CPU, Memória, Disco
- Gráficos com linhas coloridas
- Cards de servidores com métricas
- Auto-refresh funcionando

**Network:**
- Status 200 OK
- Response type: application/json
- Dados de métricas no response

## 📝 RESUMO

1. ✅ Backend corrigido
2. ✅ Frontend reconstruído
3. ⚠️ Cache do navegador precisa ser limpo
4. 🎯 Use Hard Refresh ou modo anônimo
5. ✅ Depois disso, tudo funcionará!

---

**Data:** 27/02/2026  
**Frontend:** Compilado e rodando  
**Backend:** Testado e funcionando  
**Próxima ação:** Limpar cache do navegador
