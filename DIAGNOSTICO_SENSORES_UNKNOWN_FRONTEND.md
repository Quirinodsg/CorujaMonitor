# 🔍 DIAGNÓSTICO: 6 Sensores "Unknown" no Frontend

**Data**: 11/03/2026 14:52  
**Status**: 🔎 EM INVESTIGAÇÃO

## 🎯 PROBLEMA REPORTADO

- **Frontend mostra**: 6 sensores "unknown"
- **Banco de dados**: 0 sensores unknown (confirmado via query)
- **Testado em**: 2 navegadores diferentes, aba anônima
- **Conclusão**: NÃO é cache do navegador

## 🔍 ANÁLISE DO CÓDIGO

### 1. Função `getGroupStatusCounts()` (linha 548)
```javascript
const getGroupStatusCounts = (groupSensors) => {
  const counts = { ok: 0, warning: 0, critical: 0, unknown: 0 };
  
  groupSensors.forEach(sensor => {
    const metric = metrics[sensor.id];
    if (metric) {
      counts[metric.status] = (counts[metric.status] || 0) + 1;
    } else {
      counts.unknown++;  // ⚠️ Conta como "unknown" se não tem métrica
    }
  });
  
  return counts;
};
```

**IMPORTANTE**: Esta função conta sensores como "unknown" quando:
- O sensor existe no banco
- MAS não tem métrica recente no estado `metrics`

### 2. Possíveis Causas

#### Causa A: Sensores sem métricas recentes
- Sensores existem no banco
- Worker não coletou métricas ainda
- Frontend não encontra `metrics[sensor.id]`
- Conta como "unknown"

#### Causa B: Problema na API
- API retorna sensores
- MAS não retorna métricas associadas
- Frontend não consegue popular `metrics` state

#### Causa C: Sensores inativos
- Sensores com `is_active = false`
- API retorna mas não tem métricas
- Frontend conta como "unknown"

## 📋 COMANDOS PARA DIAGNÓSTICO

### 1. Verificar sensores sem métricas recentes (LINUX)
```bash
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT 
  s.id,
  s.name,
  s.sensor_type,
  srv.hostname,
  s.is_active,
  COUNT(m.id) as metric_count,
  MAX(m.timestamp) as last_metric
FROM sensors s
JOIN servers srv ON s.server_id = srv.id
LEFT JOIN metrics m ON s.sensor_id = m.sensor_id 
  AND m.timestamp > NOW() - INTERVAL '10 minutes'
GROUP BY s.id, s.name, s.sensor_type, srv.hostname, s.is_active
HAVING COUNT(m.id) = 0
ORDER BY s.id;
"
```

### 2. Verificar sensores inativos
```bash
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT 
  s.id,
  s.name,
  s.sensor_type,
  srv.hostname,
  s.is_active,
  s.created_at
FROM sensors s
JOIN servers srv ON s.server_id = srv.id
WHERE s.is_active = false
ORDER BY s.id;
"
```

### 3. Verificar API retornando sensores (LINUX)
```bash
# Instalar jq primeiro
apt install -y jq

# Buscar todos os servidores e contar sensores
curl -s http://localhost:8000/api/v1/servers | jq '.[].sensors | length'

# Ver detalhes dos sensores
curl -s http://localhost:8000/api/v1/servers | jq '.[].sensors[] | {id, name, sensor_type}'
```

## 🔧 SOLUÇÕES POSSÍVEIS

### Solução 1: Filtrar sensores inativos no frontend
```javascript
// Adicionar filtro ao buscar sensores
const activeSensors = server.sensors.filter(s => s.is_active);
```

### Solução 2: Garantir métricas para todos os sensores
- Worker deve coletar métricas de TODOS os sensores ativos
- Verificar logs do worker para erros de coleta

### Solução 3: Melhorar exibição de "unknown"
```javascript
// Mostrar motivo do "unknown"
if (!metric) {
  counts.no_data++;  // Sem dados recentes
} else if (metric.status === 'unknown') {
  counts.unknown++;  // Status realmente desconhecido
}
```

## 🎯 PRÓXIMOS PASSOS

1. **Executar comandos de diagnóstico** (acima)
2. **Identificar quais são os 6 sensores**
3. **Verificar se têm métricas recentes**
4. **Aplicar solução apropriada**

## 📊 HIPÓTESE MAIS PROVÁVEL

Os 6 sensores "unknown" são provavelmente:
- Sensores SNMP criados automaticamente
- Ainda não têm métricas coletadas
- Worker precisa de tempo para coletar primeira métrica
- Frontend conta como "unknown" por falta de dados

**SOLUÇÃO TEMPORÁRIA**: Aguardar 5 minutos para worker coletar métricas.

---

**NOTA**: Após reiniciar o frontend (correção do PING 0ms), este problema pode se resolver automaticamente se for relacionado ao estado do React.
