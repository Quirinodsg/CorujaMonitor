# Sistema AIOps - Coruja Monitor

## Visão Geral

O Coruja Monitor implementa um sistema AIOps (Artificial Intelligence for IT Operations) completo seguindo as melhores práticas da indústria. O sistema fornece capacidades avançadas de análise e automação para operações de TI.

## Capacidades Principais

### 1. Detecção de Anomalias (Anomaly Detection)

Detecta comportamentos anormais em métricas usando múltiplos métodos:

#### Métodos Implementados

**1.1 Análise Estatística (Z-score)**
- Calcula desvio padrão e identifica valores fora da normalidade
- Threshold: 2.5 desvios padrão
- Melhor para: Detectar outliers em distribuições normais

**1.2 Média Móvel (Moving Average)**
- Compara valores atuais com média de janela deslizante
- Janela padrão: 5 amostras
- Melhor para: Detectar mudanças graduais de tendência

**1.3 Taxa de Mudança (Rate of Change)**
- Detecta mudanças bruscas em curto período
- Threshold: 20% de mudança em 2 minutos
- Melhor para: Detectar spikes e crashes súbitos

#### Endpoint API

```http
POST /api/v1/aiops/anomaly-detection
Content-Type: application/json

{
  "sensor_id": 123,
  "lookback_hours": 24
}
```

#### Resposta

```json
{
  "sensor_id": 123,
  "sensor_name": "CPU Usage",
  "anomaly_detected": true,
  "confidence": 0.85,
  "anomalies": [
    {
      "index": 45,
      "value": 95.2,
      "z_score": 3.2,
      "method": "statistical",
      "deviation_percent": 45.3
    }
  ],
  "recommendation": "Investigar processos com alto consumo de CPU"
}
```

### 2. Correlação de Eventos (Event Correlation)

Identifica relações entre incidentes usando análise temporal e espacial.

#### Tipos de Correlação

**2.1 Correlação Temporal**
- Agrupa incidentes que ocorrem próximos no tempo
- Janela padrão: 5 minutos
- Identifica: Falhas em cascata, problemas sistêmicos

**2.2 Correlação Espacial**
- Agrupa incidentes no mesmo servidor ou infraestrutura
- Identifica: Problemas de hardware, falhas de rede

**2.3 Correlação Causal**
- Identifica relações de causa e efeito
- Exemplo: Disco cheio → Serviço falha → CPU alta

#### Padrões Identificados

- `infrastructure_wide`: Problema afeta múltiplos servidores
- `cascading_failure`: Falha em cascata (um problema causa outros)
- `isolated_incidents`: Incidentes isolados sem correlação

#### Endpoint API

```http
POST /api/v1/aiops/event-correlation
Content-Type: application/json

{
  "time_window_minutes": 30,
  "severity_filter": ["critical", "warning"]
}
```

#### Resposta

```json
{
  "correlated": true,
  "total_groups": 2,
  "groups": [
    {
      "correlation_type": "temporal_spatial",
      "incident_count": 5,
      "time_span_seconds": 180,
      "affected_servers": ["server1", "server2"],
      "severity": "critical"
    }
  ],
  "analysis": {
    "total_correlated_incidents": 5,
    "total_affected_servers": 2,
    "largest_group_size": 5,
    "pattern": "infrastructure_wide"
  }
}
```

### 3. Análise de Causa Raiz (Root Cause Analysis - RCA)

Determina a causa raiz de incidentes usando análise multi-dimensional.

#### Componentes da RCA

**3.1 Análise de Sintomas**
- Sintoma primário (alerta que disparou)
- Sintomas secundários (tendências, spikes)
- Classificação de severidade

**3.2 Reconstrução de Timeline**
- Linha do tempo de eventos
- Mudanças em métricas
- Incidentes relacionados
- Ordem cronológica de ocorrências

**3.3 Análise de Dependências**
- Incidentes no mesmo servidor
- Incidentes do mesmo tipo
- Nível de dependência (low/medium/high)

**3.4 Matching de Padrões**
- Memory leak
- CPU spike
- Disk full
- Service crash
- Network congestion

#### Endpoint API

```http
POST /api/v1/aiops/root-cause-analysis
Content-Type: application/json

{
  "incident_id": 456
}
```

#### Resposta

```json
{
  "incident_id": 456,
  "root_cause": "Memory leak em aplicação - memória não sendo liberada",
  "confidence": 0.85,
  "symptoms": [
    {
      "type": "primary",
      "description": "memory at 95.2%",
      "severity": "critical"
    },
    {
      "type": "trend",
      "description": "Gradual increase detected",
      "severity": "warning"
    }
  ],
  "timeline": [
    {
      "timestamp": "2026-02-18T10:00:00",
      "event": "metric_change",
      "description": "Value changed from 60.0 to 75.0"
    }
  ],
  "contributing_factors": [
    "Múltiplos sintomas detectados indicando problema complexo",
    "Problema evoluiu ao longo do tempo"
  ]
}
```

### 4. Planos de Ação (Action Plans)

Cria planos de ação estruturados para resolução de incidentes.

#### Estrutura do Plano

**4.1 Ações Imediatas (Immediate Actions)**
- Objetivo: Parar o sangramento
- Prioridade: Alta
- Tempo: 1-5 minutos
- Risco: Baixo a Médio
- Exemplos:
  - Identificar processo problemático
  - Verificar status de serviços
  - Coletar informações iniciais

**4.2 Ações de Curto Prazo (Short-term Actions)**
- Objetivo: Corrigir o problema
- Prioridade: Média a Alta
- Tempo: 5-30 minutos
- Risco: Médio
- Exemplos:
  - Reiniciar serviço
  - Limpar arquivos temporários
  - Ajustar configurações

**4.3 Ações de Longo Prazo (Long-term Actions)**
- Objetivo: Prevenir recorrência
- Prioridade: Baixa a Média
- Tempo: Horas a dias
- Risco: Baixo
- Exemplos:
  - Ajustar thresholds
  - Implementar monitoramento proativo
  - Criar runbooks
  - Implementar automação

#### Componentes Adicionais

- **Plano de Rollback**: Reverter mudanças se necessário
- **Critérios de Sucesso**: Como saber que o problema foi resolvido
- **Tempo Estimado**: Estimativa de tempo total de resolução
- **Automação Disponível**: Indica se ações podem ser automatizadas

#### Endpoint API

```http
POST /api/v1/aiops/action-plan/456?include_correlation=true
```

#### Resposta

```json
{
  "plan_id": "AP-456-20260218130000",
  "incident_id": 456,
  "severity": "critical",
  "estimated_resolution_time": "15 minutos",
  "immediate_actions": [
    {
      "priority": 1,
      "action": "Identificar processo com maior consumo de memória",
      "command": "Get-Process | Sort-Object WS -Descending | Select-Object -First 5",
      "automated": true,
      "estimated_time": "1 min",
      "risk_level": "low"
    }
  ],
  "short_term_actions": [
    {
      "priority": 1,
      "action": "Reiniciar aplicação com memory leak",
      "automated": false,
      "estimated_time": "5 min",
      "risk_level": "medium",
      "requires_approval": true
    }
  ],
  "long_term_actions": [
    {
      "priority": 1,
      "action": "Revisar e ajustar thresholds de monitoramento",
      "automated": false,
      "estimated_time": "30 min",
      "risk_level": "low"
    }
  ],
  "automation_available": true
}
```

## Fluxo de Trabalho AIOps

### Cenário 1: Detecção Proativa

```
1. Sistema coleta métricas continuamente
2. AIOps detecta anomalia antes de threshold ser atingido
3. Correlação identifica padrão de problema emergente
4. RCA determina causa provável
5. Plano de ação preventivo é criado
6. Equipe é notificada com contexto completo
```

### Cenário 2: Resposta a Incidente

```
1. Incidente é criado (threshold ultrapassado)
2. AIOps correlaciona com outros incidentes recentes
3. RCA analisa causa raiz
4. Plano de ação é gerado automaticamente
5. Ações imediatas são executadas (se automatizadas)
6. Equipe recebe plano completo para ações manuais
7. Sistema monitora resolução
```

## Melhores Práticas Implementadas

### 1. Multi-Method Approach
- Usa múltiplos métodos de detecção para maior precisão
- Combina análise estatística, ML e regras de negócio

### 2. Context-Aware Analysis
- Considera histórico e contexto
- Analisa dependências e relações

### 3. Confidence Scoring
- Todas as análises incluem score de confiança
- Permite priorização baseada em certeza

### 4. Actionable Insights
- Foco em ações práticas e executáveis
- Comandos prontos para execução

### 5. Automation-First
- Identifica oportunidades de automação
- Separa ações automáticas de manuais

### 6. Risk Assessment
- Cada ação tem nível de risco associado
- Ações de alto risco requerem aprovação

## Configuração

### Parâmetros Ajustáveis

```python
# ai-agent/aiops_engine.py

class AIOpsEngine:
    def __init__(self):
        self.anomaly_threshold = 2.5  # Desvios padrão
        self.correlation_window = 300  # 5 minutos
        self.min_samples_for_baseline = 20  # Mínimo de amostras
```

### Requisitos

- Python 3.11+
- Mínimo 20 amostras de métricas para análise
- Histórico de pelo menos 2 horas para RCA completa

## Integração com Frontend

### Dashboard AIOps (Futuro)

```javascript
// Exemplo de integração
const aiopsData = await api.get('/api/v1/aiops/anomaly-detection', {
  sensor_id: sensorId,
  lookback_hours: 24
});

if (aiopsData.anomaly_detected) {
  showAnomalyAlert(aiopsData);
}
```

## Métricas de Performance

### Objetivos

- Detecção de anomalias: < 1 segundo
- Correlação de eventos: < 2 segundos
- RCA completa: < 3 segundos
- Geração de plano: < 1 segundo

### Precisão

- Taxa de falsos positivos: < 5%
- Taxa de detecção: > 95%
- Confiança média: > 0.80

## Roadmap Futuro

### Fase 2 (Q2 2026)
- [ ] Machine Learning avançado (LSTM, Isolation Forest)
- [ ] Predição de falhas
- [ ] Auto-healing automático
- [ ] Integração com ChatOps

### Fase 3 (Q3 2026)
- [ ] Análise de logs com NLP
- [ ] Detecção de security threats
- [ ] Capacity planning automático
- [ ] Feedback loop para melhoria contínua

## Referências

- [AIOps Best Practices - Gartner](https://www.gartner.com/en/information-technology/glossary/aiops-platform)
- [Anomaly Detection Techniques](https://en.wikipedia.org/wiki/Anomaly_detection)
- [Root Cause Analysis Methods](https://en.wikipedia.org/wiki/Root_cause_analysis)
- [ITIL Incident Management](https://www.axelos.com/certifications/itil-service-management)
