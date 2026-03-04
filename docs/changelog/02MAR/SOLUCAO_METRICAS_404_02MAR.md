# 🔧 SOLUÇÃO: Erro 404 nas Métricas - 02 MAR 2026

## 🎯 PROBLEMA IDENTIFICADO

O endpoint `/metrics/dashboard/servers` está retornando 404 mesmo após a correção no `api/main.py`.

**Causa Raiz:** CACHE DO NAVEGADOR está usando configuração antiga da API.

## 📊 ANÁLISE TÉCNICA

### Logs do Console
```
🚀 [REQUEST v2.0] URL completa: http://localhost:8000/metrics/dashboard/servers?range=24h
🚀 [REQUEST v2.0] baseURL: http://localhost:8000
🚀 [REQUEST v2.0] url relativa: /metrics/dashboard/servers?range=24h
```

### Problema
- **URL Esperada:** `http://localhost:8000/api/v1/metrics/dashboard/servers`
- **URL Atual:** `http://localhost:8000/metrics/dashboard/servers` ❌
- **Faltando:** `/api/v1` no baseURL

### Configuração Correta (frontend/src/config.js)
```javascript
export const API_URL = getApiUrl();
// Retorna: 'http://localhost:8000/api/v1' ✅
```

### Por que está errado?
O navegador está usando uma versão CACHEADA do arquivo `config.js` que tinha:
```javascript
// Versão antiga (cacheada)
return 'http://localhost:8000';  // SEM /api/v1
```

## ✅ SOLUÇÃO DEFINITIVA

### Passo 1: Limpar Cache Completo do Navegador

**Opção A - Limpeza Rápida (Recomendado):**
1. Pressione `Ctrl + Shift + Delete`
2. Selecione "Todo o período"
3. Marque:
   - ✅ Cookies e dados de sites
   - ✅ Imagens e arquivos em cache
   - ✅ Dados de aplicativos hospedados
4. Clique em "Limpar dados"
5. Feche TODAS as abas do Coruja Monitor
6. Feche o navegador completamente
7. Abra novamente e acesse `http://localhost:3000`

**Opção B - Modo Anônimo (Teste Rápido):**
1. Abra uma janela anônima (`Ctrl + Shift + N`)
2. Acesse `http://localhost:3000`
3. Faça login
4. Teste as métricas

**Opção C - DevTools (Desenvolvedor):**
1. Pressione `F12` para abrir DevTools
2. Clique com botão direito no ícone de recarregar
3. Selecione "Limpar cache e recarregar forçado"
4. Ou vá em Application > Storage > Clear site data

### Passo 2: Verificar se Funcionou

Após limpar o cache, verifique no console:
```
🔧 [CONFIG v2.0] API URL configurada: http://localhost:8000/api/v1
🚀 [REQUEST v2.0] URL completa: http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h
```

Se aparecer `/api/v1` na URL, está correto! ✅

### Passo 3: Testar Endpoint Diretamente

Abra uma nova aba e acesse:
```
http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h
```

Se retornar JSON (não 404), a API está funcionando! ✅

## 🔍 VERIFICAÇÃO TÉCNICA

### Status da API
```bash
docker-compose ps api
# Deve mostrar: Up X seconds
```

### Logs da API
```bash
docker-compose logs --tail=20 api
# Deve mostrar: Application startup complete
```

### Ordem dos Routers (Correto)
```python
# api/main.py - linhas 60-61
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(metrics_dashboard.router, prefix="/api/v1/metrics", tags=["Metrics Dashboard"])
```

### Rota Definida (Correto)
```python
# api/routers/metrics_dashboard.py - linha 32
@router.get("/dashboard/servers")
async def get_servers_dashboard(...):
```

### URL Final (Correto)
```
Prefix: /api/v1/metrics
Route: /dashboard/servers
Final: /api/v1/metrics/dashboard/servers ✅
```

## 🎯 POR QUE ACONTECEU?

1. **Histórico:** O sistema foi atualizado várias vezes
2. **Cache Agressivo:** Navegadores cacheiam arquivos JS por muito tempo
3. **Service Workers:** Podem estar cacheando a versão antiga
4. **LocalStorage:** Pode ter configurações antigas

## 🚀 SOLUÇÃO ALTERNATIVA (Se cache persistir)

Se mesmo após limpar o cache o problema persistir:

### 1. Forçar Rebuild do Frontend
```powershell
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

### 2. Adicionar Cache Buster
Edite `frontend/public/index.html` e adicione:
```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```

### 3. Verificar Service Worker
No DevTools:
1. Application > Service Workers
2. Clique em "Unregister" se houver algum
3. Recarregue a página

## 📝 CHECKLIST DE VERIFICAÇÃO

- [ ] API está rodando (docker-compose ps api)
- [ ] Ordem dos routers está correta (metrics antes de metrics_dashboard)
- [ ] Cache do navegador foi limpo (Ctrl + Shift + Delete)
- [ ] Todas as abas do Coruja foram fechadas
- [ ] Navegador foi fechado e reaberto
- [ ] Console mostra `/api/v1` na URL
- [ ] Endpoint retorna dados (não 404)

## 🎉 RESULTADO ESPERADO

Após limpar o cache, você deve ver:

**Console do Navegador:**
```
🔧 [CONFIG v2.0] API URL configurada: http://localhost:8000/api/v1
🚀 [REQUEST v2.0] URL completa: http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h
✅ Dados carregados com sucesso
```

**Tela de Métricas:**
- Gráficos carregando
- Sem erros 404
- Dados sendo exibidos

## 📞 SE O PROBLEMA PERSISTIR

Execute este comando para rebuild completo:
```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

Aguarde 30 segundos e teste novamente.

---

**Documentação criada em:** 02 de Março de 2026, 12:55 BRT
**Status:** ✅ SOLUÇÃO IDENTIFICADA - CACHE DO NAVEGADOR
