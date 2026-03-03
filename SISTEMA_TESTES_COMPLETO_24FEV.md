# SISTEMA DE TESTES COMPLETO - 24/02/2026

## FUNCIONALIDADES IMPLEMENTADAS

### ✅ 1. Simular Falhas
- Selecionar servidor e sensor
- Escolher tipo: Warning (⚠️) ou Critical (🔥)
- Definir valor customizado (opcional)
- Configurar duração em minutos
- Botão "⚡ Simular Falha"

### ✅ 2. Visualizar Falhas Ativas
- Seção "🔴 Falhas Ativas (X)"
- Lista todas as falhas simuladas em aberto
- Mostra:
  - Nome do sensor
  - Servidor
  - Severidade (Warning/Critical)
  - Duração configurada
  - Data/hora de criação
- Atualização automática a cada 5 segundos

### ✅ 3. Resolver Falhas Individuais
- Botão "✓ Resolver" em cada falha ativa
- Confirmação antes de resolver
- Marca incidente como resolvido
- Remove da lista de falhas ativas
- Atualiza dashboard automaticamente

### ✅ 4. Limpar Todas as Falhas
- Botão "🧹 Limpar Todas" (aparece quando há falhas)
- Confirmação antes de limpar
- Remove todas as métricas simuladas
- Resolve todos os incidentes de teste
- Mostra quantas métricas e incidentes foram limpos

## COMO USAR

### Criar uma Falha de Teste

1. Acesse "Ferramentas de Teste" no menu
2. Selecione um servidor (ex: DESKTOP-P9VGN04)
3. Selecione um sensor (ex: CPU)
4. Escolha o tipo de falha:
   - ⚠️ Warning: 85% (padrão)
   - 🔥 Critical: 98% (padrão)
5. (Opcional) Digite um valor customizado
6. Defina a duração (padrão: 5 minutos)
7. Clique em "⚡ Simular Falha"

### O Que Acontece

1. **Métrica Simulada Criada:**
   - Valor acima do threshold
   - Marcada como `simulated: true`
   - Status: warning ou critical

2. **Incidente Criado:**
   - Título: "[TESTE] Falha simulada - Nome do Sensor"
   - Descrição: "Falha simulada para teste de alertas. Valor: XX%"
   - Marcado como teste no campo `ai_analysis`

3. **Aparece na Interface:**
   - Dashboard: "⚠️1 Incidentes Abertos"
   - NOC: "🔥1 CRÍTICOS"
   - Sensores: Sensor mostra valor simulado
   - Ferramentas de Teste: Aparece em "Falhas Ativas"

### Resolver uma Falha

**Opção 1: Resolver Individual (RECOMENDADO)**
1. Vá em "Ferramentas de Teste"
2. Na seção "🔴 Falhas Ativas"
3. Clique no botão "✓ Resolver" da falha desejada
4. Confirme a ação
5. Falha é resolvida imediatamente

**Opção 2: Limpar Todas**
1. Vá em "Ferramentas de Teste"
2. Clique em "🧹 Limpar Todas"
3. Confirme a ação
4. Todas as falhas são resolvidas

**Opção 3: Aguardar Coleta Real**
- A probe coleta dados reais a cada 60 segundos
- Na próxima coleta, o valor real substitui o simulado
- Se o valor real estiver OK, o incidente é resolvido automaticamente

## ENDPOINTS DA API

### POST /api/v1/test-tools/simulate-failure
Cria uma falha simulada

**Request:**
```json
{
  "sensor_id": 199,
  "failure_type": "critical",
  "value": 96.0,
  "duration_minutes": 5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Falha critical simulada com sucesso",
  "sensor_id": 199,
  "sensor_name": "CPU",
  "value": 96.0,
  "status": "critical",
  "incident_created": true,
  "duration_minutes": 5
}
```

### GET /api/v1/test-tools/simulated-failures
Lista todas as falhas simuladas ativas

**Response:**
```json
{
  "success": true,
  "count": 1,
  "failures": [
    {
      "id": 8,
      "sensor_id": 199,
      "sensor_name": "CPU",
      "server_name": "DESKTOP-P9VGN04",
      "severity": "critical",
      "title": "[TESTE] Falha simulada - CPU",
      "created_at": "2026-02-24T14:18:39",
      "duration_minutes": 5
    }
  ]
}
```

### POST /api/v1/incidents/{incident_id}/resolve
Resolve um incidente específico

**Request:**
```json
{
  "resolution_notes": "Falha simulada resolvida manualmente"
}
```

**Response:**
```json
{
  "message": "Incident resolved successfully",
  "incident_id": 8,
  "resolved_at": "2026-02-24T17:30:00"
}
```

### POST /api/v1/test-tools/clear-simulated-failures
Remove todas as falhas simuladas

**Response:**
```json
{
  "success": true,
  "message": "Falhas simuladas removidas com sucesso",
  "metrics_deleted": 1,
  "incidents_resolved": 1
}
```

## FLUXO COMPLETO

```
1. CRIAR FALHA
   ↓
2. FALHA APARECE EM:
   - Dashboard (contador de incidentes)
   - NOC (servidor crítico)
   - Sensores (valor simulado)
   - Ferramentas de Teste (lista de falhas ativas)
   ↓
3. RESOLVER FALHA:
   a) Via botão "✓ Resolver" → Resolve individual
   b) Via botão "🧹 Limpar Todas" → Resolve todas
   c) Aguardar 60s → Probe coleta valor real
   ↓
4. FALHA RESOLVIDA:
   - Incidente marcado como resolvido
   - Remove da lista de falhas ativas
   - Dashboard atualiza contadores
   - NOC volta ao normal
   - Sensor mostra valor real
```

## VERIFICAÇÕES

### Verificar Falhas Ativas no Banco
```sql
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT i.id, i.title, i.severity, i.created_at, i.resolved_at, s.name as sensor_name
FROM incidents i
JOIN sensors s ON s.id = i.sensor_id
WHERE i.ai_analysis->>'simulated' = 'true'
ORDER BY i.created_at DESC;
"
```

### Verificar Métricas Simuladas
```sql
docker exec coruja-postgres psql -U coruja -d coruja_monitor -c "
SELECT m.id, m.sensor_id, m.value, m.status, m.timestamp, s.name as sensor_name
FROM metrics m
JOIN sensors s ON s.id = m.sensor_id
WHERE m.extra_metadata->>'simulated' = 'true'
ORDER BY m.timestamp DESC
LIMIT 10;
"
```

### Verificar Logs da API
```bash
docker logs coruja-api --tail 50 | grep -i "simul"
```

## COMPORTAMENTO ESPERADO

### Quando Criar Falha
- ✅ Aparece em "Falhas Ativas" imediatamente
- ✅ Dashboard mostra "⚠️1 Incidentes Abertos"
- ✅ NOC mostra "🔥1 CRÍTICOS"
- ✅ Sensor mostra valor simulado (ex: 96%)
- ✅ Status do sensor: "EM ANÁLISE" ou "CRÍTICO"

### Quando Resolver Falha
- ✅ Remove da lista "Falhas Ativas"
- ✅ Dashboard atualiza: "⚠️0 Incidentes Abertos"
- ✅ NOC atualiza: "✅1 SERVIDORES OK"
- ✅ Sensor volta ao valor real na próxima coleta
- ✅ Status do sensor: "OK"

## TROUBLESHOOTING

### Falha não aparece em "Falhas Ativas"
1. Verifique se o incidente foi criado:
   ```sql
   SELECT * FROM incidents WHERE title LIKE '%TESTE%' ORDER BY created_at DESC LIMIT 1;
   ```
2. Verifique se tem `ai_analysis->>'simulated' = 'true'`
3. Recarregue a página (F5)

### Botão "Resolver" não funciona
1. Verifique logs do navegador (F12 → Console)
2. Verifique logs da API:
   ```bash
   docker logs coruja-api --tail 50
   ```
3. Verifique se o endpoint existe:
   ```bash
   curl -X POST http://192.168.30.189:8000/api/v1/incidents/8/resolve \
     -H "Authorization: Bearer SEU_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"resolution_notes": "Teste"}'
   ```

### Falha não desaparece após resolver
1. Aguarde 5 segundos (atualização automática)
2. Recarregue a página (F5)
3. Verifique se foi resolvida no banco:
   ```sql
   SELECT id, resolved_at FROM incidents WHERE id = 8;
   ```

## ARQUIVOS RELACIONADOS

- `frontend/src/components/TestTools.js` - Interface de testes
- `api/routers/test_tools.py` - Endpoints de simulação
- `api/routers/incidents.py` - Endpoint de resolução
- `CORRECAO_TESTES_E_NOC_24FEV.md` - Correções aplicadas

## MELHORIAS FUTURAS

1. **Auto-Resolução Temporizada:**
   - Worker Celery que resolve após X minutos
   - Configurável por falha

2. **Notificações de Teste:**
   - Email de teste
   - Webhook de teste
   - Slack/Teams de teste

3. **Histórico de Testes:**
   - Log de todas as falhas simuladas
   - Relatório de testes realizados

4. **Testes Agendados:**
   - Agendar falhas para horários específicos
   - Testes recorrentes

---

**Data**: 24/02/2026
**Status**: ✅ Sistema completo e funcional
**Funcionalidades**: Simular, Visualizar, Resolver Individual, Limpar Todas
