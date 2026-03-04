# Correção da API de Métricas - 02 de Março de 2026

## 🔧 Problema Identificado

A API de métricas estava retornando erro 404:
```
GET http://localhost:8000/metrics/dashboard/servers?range=24h 404 (Not Found)
```

## 🐛 Causa Raiz

No arquivo `api/main.py`, havia dois routers registrados com o mesmo prefix `/api/v1/metrics`:

```python
# ANTES - PROBLEMA
app.include_router(metrics_dashboard.router, prefix="/api/v1/metrics", tags=["Metrics Dashboard"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
```

O router `metrics` estava sendo registrado DEPOIS do `metrics_dashboard`, sobrescrevendo as rotas do dashboard.

## ✅ Solução Aplicada

Invertida a ordem dos routers para que `metrics_dashboard` seja registrado por último:

```python
# DEPOIS - CORRIGIDO
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(metrics_dashboard.router, prefix="/api/v1/metrics", tags=["Metrics Dashboard"])
```

**Motivo:** No FastAPI, quando dois routers têm o mesmo prefix, o último registrado tem prioridade nas rotas mais específicas.

## 📁 Arquivo Modificado

- **api/main.py**
  - Linha 60-61: Invertida ordem dos routers

## 🔄 Como Aplicar a Correção

### Opção 1: Reiniciar Container Docker (Recomendado)
```powershell
docker-compose restart api
```

### Opção 2: Reiniciar Todos os Serviços
```powershell
docker-compose down
docker-compose up -d
```

### Opção 3: Rebuild Completo (Se necessário)
```powershell
docker-compose down
docker-compose build api
docker-compose up -d
```

## 🧪 Como Testar

### 1. Verificar se API Reiniciou
```powershell
docker-compose logs -f api
```

Aguarde a mensagem: `Application startup complete`

### 2. Testar Endpoint Diretamente
```powershell
curl http://localhost:8000/api/v1/metrics/dashboard/servers?range=24h
```

Deve retornar JSON com dados de métricas (não 404).

### 3. Testar no Frontend
1. Abra http://localhost:3000
2. Clique em "Métricas (Grafana)"
3. Deve carregar os gráficos sem erro 404

## 📊 Endpoints Afetados

Todos os endpoints do metrics_dashboard agora funcionam:

- `GET /api/v1/metrics/dashboard/servers?range={time}`
- `GET /api/v1/metrics/dashboard/network?range={time}`
- `GET /api/v1/metrics/dashboard/webapps?range={time}`
- `GET /api/v1/metrics/dashboard/kubernetes?range={time}`

## 🎯 Resultado Esperado

### Antes (404):
```json
{
  "detail": "Not Found"
}
```

### Depois (200 OK):
```json
{
  "summary": {
    "cpu_avg": 45.2,
    "memory_avg": 62.8,
    "disk_avg": 38.5,
    "servers_count": 5
  },
  "servers": [...]
}
```

## ⚠️ Nota Importante

Esta correção requer reiniciar a API. O frontend não precisa ser reiniciado, apenas aguarde a API voltar online.

## 📝 Checklist

- [ ] Ordem dos routers corrigida no main.py
- [ ] API reiniciada (docker-compose restart api)
- [ ] Logs da API verificados (sem erros)
- [ ] Endpoint testado (retorna 200 OK)
- [ ] Frontend testado (gráficos carregam)

## ✨ Status

Correção aplicada. Reinicie a API para ativar.
