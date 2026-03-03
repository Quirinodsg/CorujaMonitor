# Sistema de Reconhecimento de Sensores (PRTG-style)

## Visão Geral

O sistema de reconhecimento permite que técnicos marquem sensores como "em análise" para suprimir alertas e ligações enquanto trabalham na resolução do problema. Inspirado no PRTG, oferece visibilidade total da equipe sobre quem está trabalhando em cada sensor.

## Funcionalidades

### 1. Reconhecimento Automático
Quando um técnico adiciona uma nota com status "Em Análise" ou "Verificado", o sensor é automaticamente reconhecido:
- ✅ Alertas suprimidos
- ✅ Ligações bloqueadas
- ✅ Status visual alterado para azul
- ✅ Badge "Verificado pela TI" exibido

### 2. Visibilidade da Equipe
- Tooltip mostra última nota do técnico ao passar o mouse
- Nome do técnico e timestamp visíveis
- Histórico completo de notas preservado
- Dashboard mostra contagem de sensores verificados

### 3. Status de Verificação

#### ⏳ Pendente
- Sensor não reconhecido
- Alertas e ligações ativos
- Cor: vermelho/amarelo (conforme criticidade)

#### 🔍 Em Análise
- Sensor reconhecido automaticamente
- Alertas e ligações suprimidos
- Cor: azul
- Badge: "Verificado pela TI"

#### ✅ Verificado
- Sensor reconhecido automaticamente
- Problema confirmado e documentado
- Alertas e ligações suprimidos
- Cor: azul

#### 🎉 Resolvido
- Sensor desreconhecido automaticamente
- Volta ao monitoramento normal
- Alertas e ligações reativados

## Como Usar

### Para Técnicos

1. **Identificar Sensor Crítico**
   - Acesse "Servidores" no menu
   - Localize sensor com status crítico (vermelho)

2. **Reconhecer Sensor**
   - Clique no ícone 🔍 no sensor
   - Adicione nota descrevendo o problema
   - Selecione status "Em Análise"
   - Clique "Adicionar Nota"

3. **Sensor Reconhecido**
   - Badge verde "✓ Verificado pela TI" aparece
   - Barra de status fica azul
   - Alertas e ligações suprimidos
   - Outros técnicos veem que você está trabalhando

4. **Atualizar Progresso**
   - Adicione novas notas conforme trabalha
   - Mantenha status "Em Análise" ou "Verificado"
   - Equipe vê atualizações em tempo real

5. **Resolver Problema**
   - Quando resolver, adicione nota final
   - Selecione status "Resolvido"
   - Sensor volta ao monitoramento normal

### Para Gestores

**Dashboard - Nova Seção "Verificado pela TI"**
- Mostra quantos sensores estão sendo trabalhados
- Clique para ver lista completa
- Identifique gargalos e distribuição de trabalho

**Visão de Equipe**
- Veja quem está trabalhando em cada sensor
- Tooltip mostra última nota e técnico responsável
- Histórico completo de ações

## Campos do Banco de Dados

### Tabela: sensors

```sql
-- Campos de reconhecimento
is_acknowledged BOOLEAN DEFAULT FALSE
acknowledged_by INTEGER (FK para users.id)
acknowledged_at TIMESTAMP

-- Campos de última nota (cache para performance)
verification_status VARCHAR(50)
last_note TEXT
last_note_by INTEGER (FK para users.id)
last_note_at TIMESTAMP
```

### Tabela: sensor_notes

```sql
id SERIAL PRIMARY KEY
sensor_id INTEGER (FK para sensors.id)
user_id INTEGER (FK para users.id)
note TEXT
status VARCHAR(50) -- pending, in_analysis, verified, resolved
created_at TIMESTAMP
```

## API Endpoints

### POST /api/v1/sensor-notes/
Adiciona nota e reconhece/desreconhece sensor automaticamente

**Request:**
```json
{
  "sensor_id": 123,
  "note": "Reiniciando serviço IIS, aguardando estabilização",
  "status": "in_analysis"
}
```

**Response:**
```json
{
  "id": 456,
  "sensor_id": 123,
  "user_id": 789,
  "note": "Reiniciando serviço IIS, aguardando estabilização",
  "status": "in_analysis",
  "created_at": "2026-02-13T14:30:00",
  "user_name": "João Silva"
}
```

### GET /api/v1/sensor-notes/sensor/{sensor_id}
Lista todas as notas de um sensor

### GET /api/v1/dashboard/health-summary
Retorna contagem incluindo sensores reconhecidos

**Response:**
```json
{
  "healthy": 150,
  "warning": 5,
  "critical": 2,
  "acknowledged": 3,
  "unknown": 1
}
```

## Lógica de Reconhecimento

### Reconhecer Automaticamente
```python
if status in ['in_analysis', 'verified']:
    sensor.is_acknowledged = True
    sensor.acknowledged_by = current_user.id
    sensor.acknowledged_at = datetime.now()
```

### Desreconhecer Automaticamente
```python
if status in ['pending', 'resolved']:
    sensor.is_acknowledged = False
    sensor.acknowledged_by = None
    sensor.acknowledged_at = None
```

## Integração com Sistema de Alertas

### Worker de Notificações
O worker deve verificar `is_acknowledged` antes de enviar alertas:

```python
def should_send_alert(sensor):
    # Não enviar se sensor está reconhecido
    if sensor.is_acknowledged:
        return False
    
    # Verificar ambiente e horário
    if sensor.server.environment == 'production':
        return True  # 24x7
    
    # ... outras verificações
```

### Sistema de Ligações
Integração com Twilio deve respeitar reconhecimento:

```python
def should_make_call(incident):
    sensor = incident.sensor
    
    # Não ligar se técnico já está trabalhando
    if sensor.is_acknowledged:
        logger.info(f"Call suppressed - sensor {sensor.id} acknowledged by user {sensor.acknowledged_by}")
        return False
    
    # ... outras verificações
```

## Benefícios

### Para Técnicos
- ✅ Evita ligações repetidas durante trabalho
- ✅ Documenta ações tomadas
- ✅ Comunica status para equipe
- ✅ Histórico completo de troubleshooting

### Para Gestores
- ✅ Visibilidade de quem está trabalhando
- ✅ Métricas de tempo de resposta
- ✅ Identificação de gargalos
- ✅ Auditoria completa de ações

### Para Empresa
- ✅ Reduz fadiga de alertas
- ✅ Melhora comunicação da equipe
- ✅ Acelera resolução de problemas
- ✅ Documentação automática

## Migração

Execute o script de migração:

```bash
docker exec -it coruja-api python migrate_acknowledgement.py
```

Reinicie os serviços:

```bash
docker compose restart api frontend
```

## Próximos Passos

1. ✅ Sistema de reconhecimento implementado
2. ✅ Dashboard atualizado com status "Verificado pela TI"
3. ✅ Tooltip com última nota do técnico
4. ⏳ Integrar com worker de notificações
5. ⏳ Integrar com sistema de ligações Twilio
6. ⏳ Adicionar métricas de tempo de reconhecimento
7. ⏳ Relatório de performance da equipe

## Suporte

Para dúvidas ou problemas:
- Verifique logs: `docker logs coruja-api`
- Consulte documentação da API: `/docs`
- Entre em contato com suporte técnico
