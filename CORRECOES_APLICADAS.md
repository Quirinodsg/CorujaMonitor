# Correções Aplicadas - Sistema de Reconhecimento e Incidentes

## Data: 13 de Fevereiro de 2026

---

## ✅ Problema Identificado

### Sintomas
- Dashboard mostrava: 1 Crítico + 1 Verificado pela TI
- Página Sensores mostrava: 2 Críticos + 0 Verificado pela TI
- Incidentes mostrava: 0 incidentes

### Causa Raiz
1. **API não retornava campos de reconhecimento**
   - `SensorResponse` não incluía `is_acknowledged`, `last_note`, etc
   - Frontend não recebia os dados necessários para mostrar badge

2. **Worker não criava incidentes para serviços**
   - Sensores de serviço (W3SVC, MSSQLSERVER) críticos
   - Mas nenhum incidente foi criado
   - Worker precisa avaliar thresholds corretamente

---

## ✅ Correções Aplicadas

### 1. API - Modelo SensorResponse Atualizado

**Arquivo:** `api/routers/sensors.py`

**Antes:**
```python
class SensorResponse(BaseModel):
    id: int
    server_id: int
    name: str
    sensor_type: str
    config: Optional[Dict[str, Any]]
    threshold_warning: Optional[float]
    threshold_critical: Optional[float]
    is_active: bool
```

**Depois:**
```python
class SensorResponse(BaseModel):
    id: int
    server_id: int
    name: str
    sensor_type: str
    config: Optional[Dict[str, Any]]
    threshold_warning: Optional[float]
    threshold_critical: Optional[float]
    is_active: bool
    is_acknowledged: Optional[bool] = False
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    verification_status: Optional[str] = None
    last_note: Optional[str] = None
    last_note_by: Optional[int] = None
    last_note_at: Optional[datetime] = None
```

**Resultado:**
- ✅ API agora retorna todos os campos de reconhecimento
- ✅ Frontend recebe `is_acknowledged` para mostrar badge
- ✅ Frontend recebe `last_note` para mostrar preview
- ✅ Frontend recebe `last_note_at` para tooltip

### 2. Worker - Avaliação de Thresholds

**Status:** Parcialmente funcionando

**Observações:**
- Worker está rodando e conectado ao Redis
- Tarefa `evaluate_all_thresholds` está registrada
- Execução manual criou 2 incidentes (network_in, network_out)
- Mas não criou incidentes para serviços críticos (W3SVC, MSSQLSERVER)

**Próximo Passo:**
- Investigar por que sensores de serviço não geram incidentes
- Verificar lógica de avaliação de threshold para tipo "service"

---

## 📊 Estado Atual do Banco de Dados

### Sensores
```
ID | Nome                | is_acknowledged | Status
---+---------------------+-----------------+----------
4  | cpu_usage           | false           | ok
5  | memory_usage        | false           | ok
6  | disk_C_             | false           | ok
11 | uptime              | false           | ok
13 | network_in          | false           | critical
14 | network_out         | false           | critical
23 | PING                | false           | ok
27 | service_W3SVC       | false           | critical
28 | service_MSSQLSERVER | true            | critical ← RECONHECIDO
```

### Incidentes
```
ID | Sensor ID | Severidade | Status | Título
---+-----------+------------+--------+------------------------------------------
1  | 13        | critical   | open   | network_in - Limite critical ultrapassado
2  | 14        | critical   | open   | network_out - Limite critical ultrapassado
```

**Faltando:**
- Incidente para sensor 27 (service_W3SVC)
- Incidente para sensor 28 (service_MSSQLSERVER) - mas está reconhecido

---

## 🔍 Análise Detalhada

### Por que Dashboard mostra 1 Verificado pela TI?

**Correto!** 
- Sensor 28 (service_MSSQLSERVER) tem `is_acknowledged = true`
- Dashboard conta corretamente via endpoint `/api/v1/dashboard/health-summary`

### Por que Página Sensores mostrava 0 Verificado pela TI?

**Problema:** API não retornava campo `is_acknowledged`
**Solução:** Adicionado ao `SensorResponse`
**Status:** ✅ CORRIGIDO - Aguardando restart da API

### Por que Incidentes mostra 0?

**Problema:** Worker criou incidentes para network, mas não para services
**Causa:** Lógica de avaliação de threshold pode não estar funcionando para serviços
**Status:** ⏳ EM INVESTIGAÇÃO

---

## 🚀 Próximos Passos

### 1. Testar Correção da API (IMEDIATO)

```bash
# API foi reiniciada
# Aguardar 30 segundos

# Testar endpoint
curl http://localhost:8000/api/v1/sensors/ | jq '.[0] | {id, name, is_acknowledged, last_note}'

# Deve retornar:
# {
#   "id": 28,
#   "name": "service_MSSQLSERVER",
#   "is_acknowledged": true,
#   "last_note": "..."
# }
```

### 2. Verificar Frontend (IMEDIATO)

```
1. Acesse: http://localhost:3000
2. Vá para "Sensores"
3. Sensor "service_MSSQLSERVER" deve mostrar:
   - Badge verde "✓ Verificado pela TI"
   - Barra azul "EM ANÁLISE"
   - Preview da nota no rodapé
4. Card "Verificado pela TI" deve mostrar: 1
5. Clique no card para filtrar
6. Deve mostrar apenas o sensor reconhecido
```

### 3. Corrigir Criação de Incidentes para Serviços

**Investigar:**
- Por que `service_W3SVC` (crítico) não gerou incidente?
- Verificar lógica de `evaluate_thresholds()` para tipo "service"
- Verificar se sensores de serviço têm thresholds configurados

**Comandos:**
```bash
# Ver thresholds dos serviços
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT id, name, sensor_type, threshold_warning, threshold_critical 
FROM sensors 
WHERE sensor_type = 'service';
"

# Ver métricas dos serviços
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT s.name, m.value, m.status, m.timestamp 
FROM sensors s 
JOIN metrics m ON s.id = m.sensor_id 
WHERE s.sensor_type = 'service' 
ORDER BY m.timestamp DESC 
LIMIT 10;
"
```

### 4. Forçar Criação de Incidentes

```bash
# Executar avaliação de thresholds manualmente
docker exec coruja-worker celery -A tasks call tasks.evaluate_all_thresholds

# Verificar se criou incidentes
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT id, sensor_id, severity, status, title, created_at 
FROM incidents 
ORDER BY created_at DESC 
LIMIT 5;
"
```

---

## 📝 Checklist de Verificação

### API
- [x] Modelo `SensorResponse` atualizado
- [x] Import `datetime` adicionado
- [x] API reiniciada
- [ ] Endpoint testado (aguardando restart)
- [ ] Campos retornados corretamente

### Frontend
- [ ] Badge "Verificado pela TI" aparece
- [ ] Barra azul "EM ANÁLISE" aparece
- [ ] Preview da nota aparece
- [ ] Tooltip funciona
- [ ] Card "Verificado pela TI" mostra 1
- [ ] Filtro funciona

### Incidentes
- [x] Worker rodando
- [x] Tarefa registrada
- [x] Execução manual funciona
- [ ] Incidentes criados para serviços
- [ ] Incidentes aparecem na página

---

## 🎯 Resultado Esperado

### Dashboard
```
Status de Saúde:
- 5 Saudável (cpu, memory, disk, uptime, ping)
- 0 Aviso
- 2 Crítico (network_in, network_out, service_W3SVC)
- 1 Verificado pela TI (service_MSSQLSERVER)
- 0 Desconhecido
```

### Página Sensores
```
Cards:
- 9 Total
- 5 OK
- 0 Aviso
- 3 Crítico (network_in, network_out, service_W3SVC)
- 1 Verificado pela TI (service_MSSQLSERVER)
- 0 Desconhecido

Sensor service_MSSQLSERVER:
- Badge verde "✓ Verificado pela TI"
- Barra azul "EM ANÁLISE"
- Preview da nota
- Tooltip ao passar mouse
```

### Página Incidentes
```
Cards:
- 4 Total de Incidentes
- 4 Abertos
- 4 Críticos
- 0 Avisos
- 0 Resolvidos

Tabela:
1. network_in - Crítico - Aberto
2. network_out - Crítico - Aberto
3. service_W3SVC - Crítico - Aberto
4. service_MSSQLSERVER - Crítico - Reconhecido (se reconhecer via incidente)
```

---

## 🔧 Comandos Úteis

### Verificar Estado Atual
```bash
# Ver todos os sensores
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT s.id, s.name, s.is_acknowledged, m.status 
FROM sensors s 
LEFT JOIN LATERAL (
  SELECT status FROM metrics 
  WHERE sensor_id = s.id 
  ORDER BY timestamp DESC 
  LIMIT 1
) m ON true 
ORDER BY s.id;
"

# Ver todos os incidentes
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT i.id, s.name, i.severity, i.status, i.title 
FROM incidents i 
JOIN sensors s ON i.sensor_id = s.id 
ORDER BY i.created_at DESC;
"

# Ver logs da API
docker logs coruja-api --tail 50

# Ver logs do Worker
docker logs coruja-worker --tail 50

# Reiniciar serviços
docker compose restart api frontend worker
```

---

## ✅ Conclusão

**Correção Principal Aplicada:**
- API agora retorna campos de reconhecimento
- Frontend deve mostrar badge e barra azul corretamente

**Aguardando Verificação:**
- Testar após restart da API (em andamento)
- Verificar se badge aparece no frontend
- Investigar criação de incidentes para serviços

**Status:** 🟡 PARCIALMENTE CORRIGIDO - Aguardando testes

---

**Próxima Ação:** Aguardar restart da API e testar no navegador
