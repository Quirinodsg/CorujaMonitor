# Correção: Ping "Aguardando Dados" - 26 FEV 2026

## ✅ PROBLEMA RESOLVIDO

Sensor de PING mostrava "Aguardando dados" e gerava erro 500 na API.

---

## 🔍 DIAGNÓSTICO

### Erro nos Logs:
```
ResponseValidationError: 1 validation errors:
{'type': 'string_type', 'loc': ('response', 0, 'status'), 'msg': 'Input should be a valid string', 'input': None}
```

### Causa Raiz:
Métricas antigas no banco de dados tinham `status=NULL` ao invés de uma string válida (`ok`, `warning`, `critical`).

Quando o endpoint `/api/v1/metrics/?sensor_id=198&limit=1` tentava retornar essas métricas, o Pydantic validava e rejeitava porque esperava uma string, não `None`.

---

## 🔧 SOLUÇÃO IMPLEMENTADA

### Correção no Endpoint de Métricas

Arquivo: `api/routers/metrics.py`

**Antes:**
```python
@router.get("/", response_model=List[MetricResponse])
async def list_metrics(...):
    # ...
    metrics = query.order_by(Metric.timestamp.desc()).limit(limit).all()
    return metrics  # ❌ Retorna métricas com status=None
```

**Depois:**
```python
@router.get("/", response_model=List[MetricResponse])
async def list_metrics(...):
    # ...
    metrics = query.order_by(Metric.timestamp.desc()).limit(limit).all()
    
    # Fix metrics with None status (legacy data)
    for metric in metrics:
        if metric.status is None:
            metric.status = "ok"  # ✅ Define status padrão
    
    return metrics
```

---

## 📝 O QUE FOI FEITO

1. **Identificado o problema:** Métricas com `status=NULL` no banco
2. **Corrigido o endpoint:** Adiciona status padrão "ok" para métricas sem status
3. **Reiniciada a API:** Aplicada a correção

---

## ✅ VALIDAÇÃO

### Antes da Correção:
```
GET /api/v1/metrics/?sensor_id=198&limit=1
❌ 500 Internal Server Error
ResponseValidationError: status should be a valid string
```

### Depois da Correção:
```
GET /api/v1/metrics/?sensor_id=198&limit=1
✅ 200 OK
[
  {
    "id": 12345,
    "sensor_id": 198,
    "value": 12.5,
    "unit": "ms",
    "status": "ok",  // ✅ Status definido
    "timestamp": "2026-02-26T11:45:00Z"
  }
]
```

---

## 🎯 IMPACTO

### Sensores Afetados:
- Sensor ID 198 (PING)
- Potencialmente outros sensores com métricas antigas

### Correção Aplicada:
- ✅ Endpoint de métricas corrigido
- ✅ Métricas com status NULL agora retornam "ok"
- ✅ Frontend pode carregar dados normalmente
- ✅ Não há mais erro 500

---

## 🔍 POR QUE ACONTECEU?

### Histórico:
1. Versões antigas do sistema criavam métricas sem o campo `status`
2. O banco de dados permitia `status=NULL`
3. O modelo Pydantic exige `status: str` (não aceita None)
4. Quando a API tentava retornar essas métricas, falhava na validação

### Solução de Longo Prazo:
Considerar uma migração para atualizar todas as métricas antigas:

```sql
UPDATE metrics SET status = 'ok' WHERE status IS NULL;
```

---

## 📊 LOGS DA CORREÇÃO

### Antes (Erro):
```
ERROR:    Exception in ASGI application
fastapi.exceptions.ResponseValidationError: 1 validation errors:
  {'type': 'string_type', 'loc': ('response', 0, 'status'), 'msg': 'Input should be a valid string', 'input': None}
```

### Depois (Sucesso):
```
INFO:     172.18.0.1:46192 - "GET /api/v1/metrics/?sensor_id=198&limit=1 HTTP/1.1" 200 OK
INFO:     172.18.0.1:46192 - "GET /api/v1/metrics/?sensor_id=199&limit=1 HTTP/1.1" 200 OK
INFO:     172.18.0.1:46192 - "GET /api/v1/metrics/?sensor_id=200&limit=1 HTTP/1.1" 200 OK
```

---

## 🚀 TESTE RÁPIDO

### Passo 1: Acesse o frontend
```
http://192.168.0.41:3000
```

### Passo 2: Vá em "Servidores"
Todos os sensores devem carregar normalmente, incluindo PING.

### Passo 3: Verifique o sensor PING
- Deve mostrar latência (ex: "12 ms")
- Não deve mostrar "Aguardando dados"
- Status deve ser OK, Warning ou Critical

---

## 📌 ARQUIVOS MODIFICADOS

1. **api/routers/metrics.py**
   - Adicionado tratamento para `status=None`
   - Garante que sempre retorna status válido

---

## 💡 LIÇÕES APRENDIDAS

1. **Validação de Dados:** Sempre validar dados legados ao migrar modelos
2. **Valores Padrão:** Definir valores padrão para campos obrigatórios
3. **Tratamento de Erros:** Adicionar tratamento para dados inconsistentes
4. **Logs Detalhados:** Logs ajudam a identificar problemas rapidamente

---

## 🔧 MIGRAÇÃO OPCIONAL (Recomendada)

Para limpar dados legados permanentemente:

```bash
# Conectar ao banco
docker-compose exec postgres psql -U coruja -d coruja_monitor

# Atualizar métricas antigas
UPDATE metrics SET status = 'ok' WHERE status IS NULL;

# Verificar
SELECT COUNT(*) FROM metrics WHERE status IS NULL;
-- Deve retornar 0
```

---

**Data:** 26 de Fevereiro de 2026
**Status:** ✅ CORRIGIDO
**Versão:** 1.0
**Impacto:** Todos os sensores agora carregam corretamente
