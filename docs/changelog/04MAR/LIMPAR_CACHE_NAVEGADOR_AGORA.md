# 🔥 LIMPAR CACHE DO NAVEGADOR - URGENTE

## ✅ BACKEND FUNCIONANDO

O backend está 100% funcional:
```
GET http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h
Status: 200 OK
Dados: CPU, Memória, Disco, Timeseries
```

## ❌ PROBLEMA: CACHE DO NAVEGADOR

O navegador está usando JavaScript compilado antigo em cache. O arquivo `config.js` foi atualizado mas o navegador não está carregando a nova versão.

## 🔧 SOLUÇÃO: LIMPAR CACHE COMPLETAMENTE

### OPÇÃO 1: Hard Refresh (RECOMENDADO)

1. **Feche TODAS as abas** do sistema Coruja
2. **Abra o DevTools** (F12)
3. **Clique com botão direito** no ícone de atualizar
4. **Selecione**: "Limpar cache e atualizar forçadamente" ou "Empty Cache and Hard Reload"
5. **Aguarde** a página recarregar completamente

### OPÇÃO 2: Limpar Cache Manualmente

#### Chrome/Edge:
1. Pressione `Ctrl + Shift + Delete`
2. Selecione "Imagens e arquivos em cache"
3. Período: "Última hora"
4. Clique em "Limpar dados"
5. Recarregue a página com `Ctrl + F5`

#### Firefox:
1. Pressione `Ctrl + Shift + Delete`
2. Selecione "Cache"
3. Período: "Última hora"
4. Clique em "Limpar agora"
5. Recarregue a página com `Ctrl + F5`

### OPÇÃO 3: Modo Anônimo (TESTE RÁPIDO)

1. Abra uma **janela anônima/privada**:
   - Chrome/Edge: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`
2. Acesse: `http://localhost:3000`
3. Faça login: admin@coruja.com / admin123
4. Vá em Métricas Grafana

## 🔍 COMO VERIFICAR SE FUNCIONOU

Abra o Console do navegador (F12 → Console) e procure por:

### ✅ LOGS CORRETOS (v2.0):
```
🔧 [CONFIG v2.0] API URL configurada: http://localhost:8000/api/v1
🌐 [CONFIG v2.0] Hostname detectado: localhost
✅ [CONFIG v2.0] Timestamp: 2026-02-28T...
🔗 [API v2.0] Axios baseURL configurado: http://localhost:8000/api/v1
🚀 [REQUEST v2.0] URL completa: http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h
```

### ❌ LOGS ANTIGOS (cache):
```
🔧 API URL configurada: http://localhost:8000
(sem /api/v1 no final)
```

## 📊 TESTE DO BACKEND

Backend testado e funcionando:
- Endpoint: `/api/v1/metrics/dashboard/servers?range=24h`
- Status: 200 OK
- Dados retornados:
  - CPU média: 100%
  - Memória média: 86.4%
  - Disco médio: 40.8%
  - Servidores: 1 total
  - Timeseries: 12 pontos de dados

## 🎯 RESUMO

1. ✅ Arquivo `config.js` corrigido (adicionado `/api/v1`)
2. ✅ Frontend recompilado (v2.0 com logs)
3. ✅ Backend testado e funcionando
4. ❌ Navegador com cache antigo
5. 🔧 **AÇÃO**: Limpar cache do navegador

## ⏰ HORÁRIO DA CORREÇÃO

- Arquivo corrigido: 14:08 BRT
- Frontend reiniciado: 14:11 BRT
- Compilação concluída: 14:12 BRT
- Backend testado: 14:15 BRT

---

**IMPORTANTE**: Após limpar o cache, você DEVE ver os logs com "[CONFIG v2.0]" e "[API v2.0]" no console. Se não ver, o cache ainda não foi limpo.
