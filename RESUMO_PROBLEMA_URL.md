# Resumo do Problema de URL

## Situação Atual

### Login está funcionando ✓
- Conseguiu fazer login com sucesso
- Token JWT foi obtido

### Outras páginas com erro 404 ✗
- URLs estão duplicadas: `/api/v1/api/v1/...`

## Causa Raiz

O problema está em como os componentes fazem requisições:

1. **config.js** define: `API_URL = 'http://192.168.31.161:8000/api/v1'`
2. **api.js** (axios) usa: `baseURL: API_URL`
3. **Componentes** fazem: `api.get('/api/v1/tenants')`
4. **Resultado**: `http://192.168.31.161:8000/api/v1/api/v1/tenants` ❌

## Solução

Os componentes devem fazer requisições SEM `/api/v1`:

### Errado ❌
```javascript
api.get('/api/v1/tenants')
```

### Correto ✓
```javascript
api.get('/tenants')
```

## Arquivos que Precisam Correção

Todos os componentes que usam `api.get()`, `api.post()`, etc. e incluem `/api/v1` na URL.

Exemplos:
- `frontend/src/components/Settings.js`
- `frontend/src/components/Servers.js`
- `frontend/src/components/Dashboard.js`
- `frontend/src/components/Incidents.js`
- `frontend/src/components/Reports.js`
- `frontend/src/components/KnowledgeBase.js`
- `frontend/src/components/AIActivities.js`
- E outros...

## Próximos Passos

1. Criar script para buscar e substituir `/api/v1/` por `/` em todos os componentes
2. Rebuild do frontend
3. Testar todas as páginas
