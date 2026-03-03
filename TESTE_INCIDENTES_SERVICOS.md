# Teste de Incidentes para Sensores de Serviço

## Status: ✅ CORRIGIDO

### Problema Identificado
Os sensores de serviço (service_W3SVC e service_MSSQLSERVER) estavam com status CRITICAL mas não geravam incidentes.

### Causa Raiz
O arquivo `worker/threshold_evaluator.py` estava usando lógica genérica de threshold (value >= threshold_critical), mas sensores de serviço usam:
- `value = 0` quando o serviço está OFFLINE (crítico)
- `value = 1` quando o serviço está ONLINE (ok)
- Os thresholds 80/95 não fazem sentido para este tipo de sensor

### Correções Aplicadas

#### 1. Atualização do Threshold Evaluator
**Arquivo**: `worker/threshold_evaluator.py`

Adicionada lógica especial para sensores de serviço e ping:
```python
# Sensores de serviço: value=0 significa offline (crítico)
if sensor.sensor_type == 'service':
    if value == 0:
        return True, "critical"
    else:
        return False, "ok"

# Sensores de ping: value=0 significa offline (crítico)
if sensor.sensor_type == 'ping':
    if value == 0:
        return True, "critical"
    # Verifica thresholds de latência
    ...
```

#### 2. Correção do Self-Healing
**Arquivo**: `worker/self_healing.py`

Corrigido erro de atributo `config` que não existe no modelo Sensor:
- Antes: `sensor.config.get("service_name")`
- Depois: Extrai o nome do serviço do campo `sensor.name` (ex: "service_W3SVC" → "W3SVC")

### Resultados

#### Incidentes Criados
```sql
SELECT id, sensor_id, severity, status, title, created_at 
FROM incidents 
ORDER BY created_at DESC;

 id | sensor_id | severity | status |                       title                        
----+-----------+----------+--------+----------------------------------------------------
  4 |        28 | critical | open   | service_MSSQLSERVER - Limite critical ultrapassado
  3 |        27 | critical | open   | service_W3SVC - Limite critical ultrapassado      
  2 |        14 | critical | open   | network_out - Limite critical ultrapassado        
  1 |        13 | critical | open   | network_in - Limite critical ultrapassado         
```

✅ Incidentes 3 e 4 foram criados para os sensores de serviço!

### Testes Realizados
1. ✅ Threshold evaluator atualizado com lógica especial para service e ping
2. ✅ Self-healing corrigido para não usar campo config inexistente
3. ✅ Worker reiniciado
4. ✅ Avaliação manual de thresholds executada
5. ✅ Incidentes criados com sucesso para sensores de serviço

### Próximos Passos
1. Testar no navegador se os incidentes aparecem na página "Incidentes"
2. Verificar se o badge "✓ Verificado pela TI" aparece no sensor 28 (service_MSSQLSERVER)
3. Confirmar que o filtro "Verificado pela TI" mostra contagem correta

### Comandos Úteis

#### Ver incidentes no banco
```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, sensor_id, severity, status, title FROM incidents ORDER BY created_at DESC LIMIT 10;"
```

#### Ver sensores de serviço
```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, name, sensor_type, threshold_warning, threshold_critical FROM sensors WHERE sensor_type = 'service';"
```

#### Ver métricas de sensores de serviço
```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT sensor_id, value, status, timestamp FROM metrics WHERE sensor_id IN (27, 28) ORDER BY timestamp DESC LIMIT 4;"
```

#### Forçar avaliação de thresholds
```bash
docker exec coruja-worker celery -A tasks call tasks.evaluate_all_thresholds
```

## Data da Correção
13/02/2026 - 16:35 UTC
