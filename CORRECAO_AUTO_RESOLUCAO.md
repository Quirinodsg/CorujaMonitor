# Correção: Auto-Resolução de Incidentes de Rede

## Status: ✅ CORRIGIDO

### Problema Identificado
Incidentes de rede (network_in e network_out) permaneciam abertos mesmo após os sensores voltarem ao normal (status OK).

### Causa Raiz
O `threshold_evaluator.py` estava comparando valores incompatíveis:
- **Valor no banco**: bytes/s (ex: 358161 bytes/s = 0.34 MB/s)
- **Threshold configurado**: MB/s (ex: 80 MB/s)
- **Comparação errada**: `358161 >= 80` = TRUE ❌ (sempre ultrapassava o threshold)

Isso fazia com que o sistema sempre considerasse os sensores de rede como críticos, impedindo a auto-resolução.

### Correção Aplicada

**Arquivo**: `worker/threshold_evaluator.py`

Adicionada conversão de bytes/s para MB/s antes de comparar com thresholds:

```python
# Special handling for network sensors
# Network sensors: value is in bytes/s, thresholds are in MB/s
if sensor.sensor_type == 'network':
    # Convert bytes/s to MB/s
    value_mbps = value / 1024 / 1024
    
    if sensor.threshold_critical is not None and value_mbps >= sensor.threshold_critical:
        return True, "critical"
    
    if sensor.threshold_warning is not None and value_mbps >= sensor.threshold_warning:
        return True, "warning"
    
    return False, "ok"
```

### Exemplo de Conversão
- Sensor network_in: 358161 bytes/s ÷ 1024 ÷ 1024 = **0.34 MB/s**
- Threshold critical: 95 MB/s
- Comparação: 0.34 < 95 = FALSE ✅ (não ultrapassou, está OK)

### Resultados

#### Antes da Correção
```
ID | Sensor ID | Status | Resolved At
---|-----------|--------|------------
 1 |        13 | open   | NULL
 2 |        14 | open   | NULL
 3 |        27 | open   | NULL
 4 |        28 | open   | NULL
```

#### Depois da Correção
```
ID | Sensor ID | Status        | Resolved At
---|-----------|---------------|---------------------------
 1 |        13 | auto_resolved | 2026-02-13 16:50:31+00
 2 |        14 | auto_resolved | 2026-02-13 16:50:31+00
 3 |        27 | open          | NULL (serviço ainda offline)
 4 |        28 | open          | NULL (serviço ainda offline)
```

### Logs do Worker
```
[2026-02-13 16:50:31,226: WARNING/ForkPoolWorker-4] ✅ Incidente 1 auto-resolvido
[2026-02-13 16:50:31,239: WARNING/ForkPoolWorker-4] ✅ Incidente 2 auto-resolvido
```

### Comportamento Esperado

#### Sensores de Rede (network)
- Valor armazenado: bytes/s
- Threshold configurado: MB/s
- Conversão automática: bytes/s → MB/s antes de comparar
- Auto-resolução: Quando tráfego voltar abaixo do threshold

#### Sensores de Serviço (service)
- Valor: 0 = offline (crítico), 1 = online (ok)
- Threshold: Ignorado (não aplicável)
- Auto-resolução: Quando serviço voltar online (value=1)

#### Sensores de Ping (ping)
- Valor: 0 = offline (crítico), >0 = latência em ms
- Threshold: Latência máxima em ms
- Auto-resolução: Quando ping voltar e latência ficar abaixo do threshold

#### Sensores Padrão (cpu, memory, disk)
- Valor: Porcentagem (0-100)
- Threshold: Porcentagem
- Auto-resolução: Quando valor voltar abaixo do threshold

### Testes Realizados
1. ✅ Threshold evaluator atualizado com conversão bytes/s → MB/s
2. ✅ Worker reiniciado
3. ✅ Avaliação manual de thresholds executada
4. ✅ Incidentes de rede auto-resolvidos com sucesso
5. ✅ Incidentes de serviço permanecem abertos (comportamento correto)

### Teste no Navegador
1. Abrir http://localhost:3000
2. Ir para página "Incidentes"
3. Clicar em "🔄 Atualizar" ou pressionar F5
4. Verificar contadores:
   - **Total**: 4 incidentes
   - **Abertos**: 2 (service_W3SVC, service_MSSQLSERVER)
   - **Críticos**: 2
   - **Resolvidos**: 2 (network_in, network_out)
5. Verificar filtro "Todos" mostra os 4 incidentes
6. Verificar filtro "Abertos" mostra apenas os 2 de serviço
7. Verificar filtro "Resolvidos" mostra os 2 de rede com badge "✅ Auto-Resolvido"

### Comandos Úteis

#### Ver status dos incidentes
```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT id, sensor_id, severity, status, resolved_at FROM incidents ORDER BY id;"
```

#### Ver métricas de rede atuais
```bash
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "SELECT sensor_id, value/1024/1024 as value_mbps, status FROM metrics WHERE sensor_id IN (13, 14) ORDER BY timestamp DESC LIMIT 2;"
```

#### Forçar avaliação de thresholds
```bash
docker exec coruja-worker celery -A tasks call tasks.evaluate_all_thresholds
```

#### Ver logs do worker
```bash
docker logs coruja-worker --tail 50 | findstr "auto-resolvido"
```

## Resumo das Correções de Hoje

### 1. ✅ Display de Reconhecimento
- API retornando campos de acknowledgement
- Badge "✓ Verificado pela TI" funcionando

### 2. ✅ Incidentes de Serviço
- Threshold evaluator com lógica especial para service (value=0 → critical)
- Incidentes criados para service_W3SVC e service_MSSQLSERVER

### 3. ✅ Auto-Resolução de Rede
- Conversão bytes/s → MB/s para sensores de rede
- Incidentes de network_in e network_out auto-resolvidos

### Tipos de Sensor Suportados
| Tipo | Unidade Valor | Unidade Threshold | Conversão | Status |
|------|---------------|-------------------|-----------|--------|
| cpu | % | % | Não | ✅ |
| memory | % | % | Não | ✅ |
| disk | % | % | Não | ✅ |
| network | bytes/s | MB/s | Sim (÷1024÷1024) | ✅ |
| service | 0/1 | N/A | Não | ✅ |
| ping | ms (0=offline) | ms | Não | ✅ |

---

**Data da Correção**: 13/02/2026 16:50 UTC
**Responsável**: Kiro AI Assistant
**Status**: ✅ FUNCIONANDO PERFEITAMENTE
