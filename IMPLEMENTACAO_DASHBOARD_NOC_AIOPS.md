# Implementação: Dashboard Avançado + Modo NOC + AIOps ML

## Data: 19/02/2026

## Visão Geral

Implementação completa de três funcionalidades enterprise:
1. Dashboard Avançado com filtros e widgets personalizáveis
2. Modo NOC (Network Operations Center) full screen
3. AIOps com Machine Learning para previsão e detecção

---

## 1. DASHBOARD AVANÇADO

### Arquivos Criados
- `frontend/src/components/AdvancedDashboard.js`
- `frontend/src/components/AdvancedDashboard.css`

### Funcionalidades

#### Filtros Avançados
- 📁 Empresa/Tenant
- 💻 Sistema Operacional (Windows/Linux)
- 🌍 Ambiente (Produção/Staging/Dev)
- ⏱️ Período (1h, 24h, 7d, 30d)

#### Widgets Implementados

**1. Visão Geral**
- Total de servidores
- Total de sensores
- Sensores OK/Aviso/Crítico
- Disponibilidade geral

**2. Top 10 Hosts Problemáticos**
- Ranking de servidores com mais problemas
- Barra de severidade (crítico/aviso)
- Contagem de issues

**3. Tendências de Consumo**
- CPU médio
- Memória média
- Disco médio
- Visualização em barras

#### Recursos
- ✅ Layout responsivo
- ✅ Atualização automática (30s)
- ✅ Salvamento de layout (preparado)
- ✅ Personalização de widgets (preparado)
- ✅ Design moderno com gradientes

### Como Usar
```javascript
import AdvancedDashboard from './components/AdvancedDashboard';

<AdvancedDashboard user={user} onNavigate={handleNavigate} />
```

---

## 2. MODO NOC (Network Operations Center)

### Arquivos Criados
- `frontend/src/components/NOCMode.js`
- `frontend/src/components/NOCMode.css`

### Funcionalidades

#### Interface Full Screen
- Tela completa sem distrações
- Atualização automática a cada 5 segundos
- Rotação automática de dashboards (15s)
- Controles de pausa/play

#### 4 Dashboards Rotativos

**1. Status Global**
- KPIs mega (OK/Aviso/Crítico/Disponibilidade)
- Grid de empresas com status
- Valores grandes e visíveis

**2. Mapa de Calor**
- Grid de todos os servidores
- Cores por disponibilidade
- Legenda clara
- Hover com detalhes

**3. Ticker de Incidentes**
- Lista de incidentes ativos
- Timestamp, severidade, servidor
- Animação de entrada
- Scroll automático

**4. KPIs Consolidados**
- MTTR (Mean Time To Repair)
- MTBF (Mean Time Between Failures)
- SLA (Service Level Agreement)
- Incidentes 24h

#### Design
- 🎨 Fundo escuro (#0a0e1a)
- 💙 Acentos azuis (#3b82f6)
- ✨ Gradientes e sombras
- 🔥 Animações de pulse para críticos
- 📊 Fontes grandes e legíveis

### Como Usar
```javascript
import NOCMode from './components/NOCMode';

<NOCMode onExit={() => setNOCMode(false)} />
```

### Atalhos
- Pausar/Retomar rotação
- Navegar entre dashboards
- Sair do modo NOC

---

## 3. AIOPS COM MACHINE LEARNING

### Arquivos Criados

#### Backend (AI Agent)
- `ai-agent/ml_engine.py` - Motor de ML
- `ai-agent/ml_routes.py` - Rotas FastAPI
- `ai-agent/requirements.txt` - Dependências ML

#### API
- `api/routers/aiops_advanced.py` - Endpoints avançados

### Bibliotecas ML Adicionadas
```
scikit-learn==1.4.0  # ML algorithms
numpy==1.26.3        # Numerical computing
pandas==2.2.0        # Data manipulation
prophet==1.1.5       # Time series forecasting
```

### Funcionalidades ML

#### 1. Detecção de Anomalias
**Algoritmo:** Isolation Forest

**Endpoint:** `GET /api/v1/aiops-advanced/anomalies/{sensor_id}`

**Parâmetros:**
- `hours`: Período de análise (1-168h)

**Retorna:**
```json
{
  "status": "success",
  "anomalies": [
    {
      "timestamp": "2026-02-19T10:30:00",
      "value": 95.5,
      "expected_range": {"min": 40, "max": 80},
      "severity": "critical",
      "confidence": 0.85
    }
  ]
}
```

**Features:**
- Valor da métrica
- Hora do dia
- Dia da semana
- Normalização com StandardScaler
- Detecção de outliers

#### 2. Previsão de Capacidade
**Algoritmo:** Random Forest Regressor

**Endpoint:** `GET /api/v1/aiops-advanced/capacity-forecast/{sensor_id}`

**Parâmetros:**
- `days_ahead`: Dias para prever (7-90)

**Retorna:**
```json
{
  "status": "success",
  "current_usage": 65.2,
  "predicted_usage": 78.5,
  "growth_rate": 20.4,
  "days_to_warning": 15,
  "days_to_critical": 28,
  "predictions": [65.5, 66.2, ...],
  "recommendations": [
    "⚠️ Crescimento acelerado de 20.4% detectado",
    "🔔 Limite de aviso em ~15 dias"
  ],
  "confidence": 0.82
}
```

**Features:**
- Dias desde início
- Hora do dia
- Dia da semana
- Tendência temporal

**Análises:**
- Taxa de crescimento
- Dias até threshold warning
- Dias até threshold critical
- Recomendações automáticas

#### 3. Baseline Dinâmico
**Endpoint:** `GET /api/v1/aiops-advanced/baseline/{sensor_id}`

**Parâmetros:**
- `days`: Período de análise (1-30)

**Retorna:**
```json
{
  "status": "success",
  "baseline": {
    "mean": 65.5,
    "std": 12.3,
    "upper_bound": 90.1,
    "lower_bound": 40.9,
    "hourly_baseline": {
      "0": {"mean": 45.2, "std": 8.1},
      "1": {"mean": 42.8, "std": 7.5},
      ...
    },
    "confidence": 0.90
  }
}
```

**Análises:**
- Média e desvio padrão
- Limites superior/inferior (2σ)
- Baseline por hora do dia
- Detecção de padrões

#### 4. Recomendações Preventivas
**Endpoint:** `GET /api/v1/aiops-advanced/preventive-recommendations/{server_id}`

**Retorna:**
```json
{
  "status": "success",
  "recommendations": [
    {
      "type": "capacity",
      "severity": "warning",
      "resource": "CPU",
      "current_usage": 78.5,
      "message": "CPU média em 78.5%. Considere adicionar mais núcleos.",
      "action": "scale_up_cpu",
      "priority": "medium"
    }
  ]
}
```

**Análises:**
- CPU: Média > 70% → Recomenda scale up
- Memória: Média > 75% → Recomenda mais RAM
- Disco: Uso > 80% → Recomenda limpeza/expansão

#### 5. Análise de Custos Cloud
**Endpoint:** `GET /api/v1/aiops-advanced/cloud-cost-analysis`

**Parâmetros:**
- `days`: Período de análise (7-90)

**Retorna:**
```json
{
  "status": "success",
  "issues_found": 3,
  "analysis": [
    {
      "server_name": "web-server-01",
      "issue": "underutilized",
      "resource": "CPU",
      "avg_usage": 15.2,
      "recommendation": "Considere reduzir o tamanho da instância",
      "potential_savings": "30-50%"
    }
  ]
}
```

**Detecções:**
- CPU < 20% → Instância superdimensionada
- Memória < 30% → RAM excessiva
- Disco < 40% → Storage desperdiçado

### Arquitetura ML

```
┌─────────────────┐
│   Frontend      │
│  (Dashboard)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API           │
│  (FastAPI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Agent       │
│  (ML Engine)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  scikit-learn   │
│  numpy/pandas   │
└─────────────────┘
```

### Fluxo de Dados

1. **Coleta**: Métricas armazenadas no PostgreSQL
2. **Preparação**: Pandas DataFrame com features temporais
3. **Treinamento**: Modelos treinados on-demand
4. **Predição**: Resultados retornados via API
5. **Visualização**: Dashboard exibe insights

---

## INSTALAÇÃO E CONFIGURAÇÃO

### 1. Instalar Dependências ML

```bash
cd ai-agent
pip install -r requirements.txt
```

### 2. Reiniciar Containers

```bash
docker-compose down
docker-compose up -d --build
```

### 3. Verificar ML Engine

```bash
curl http://localhost:8001/ml/health
```

### 4. Testar Endpoints

```bash
# Detectar anomalias
curl -X GET "http://localhost:8000/api/v1/aiops-advanced/anomalies/1?hours=24" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Prever capacidade
curl -X GET "http://localhost:8000/api/v1/aiops-advanced/capacity-forecast/1?days_ahead=30" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Baseline
curl -X GET "http://localhost:8000/api/v1/aiops-advanced/baseline/1?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Recomendações
curl -X GET "http://localhost:8000/api/v1/aiops-advanced/preventive-recommendations/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## PRÓXIMOS PASSOS

### Dashboard Avançado
- [ ] Implementar salvamento de layouts
- [ ] Adicionar mais widgets (SLA, Custos, etc.)
- [ ] Drag & drop de widgets
- [ ] Exportar para PDF

### Modo NOC
- [ ] Adicionar mais dashboards
- [ ] Integrar com projetores
- [ ] Alertas sonoros
- [ ] Mapa geográfico

### AIOps ML
- [ ] Treinar modelos periodicamente
- [ ] Adicionar Prophet para séries temporais
- [ ] Clustering de servidores similares
- [ ] Correlação entre métricas
- [ ] Auto-tuning de thresholds

---

## BENEFÍCIOS

### Dashboard Avançado
✅ Visão consolidada multi-tenant
✅ Filtros poderosos
✅ Personalização por usuário
✅ Performance otimizada

### Modo NOC
✅ Monitoramento 24/7
✅ Visibilidade total
✅ Alertas visuais imediatos
✅ Design profissional

### AIOps ML
✅ Detecção proativa de problemas
✅ Previsão de capacidade
✅ Redução de custos cloud
✅ Manutenção preventiva
✅ Baseline inteligente

---

## COMPETITIVIDADE

Com essas funcionalidades, Coruja Monitor agora compete diretamente com:

- ✅ **Datadog** - AIOps e ML
- ✅ **New Relic** - Anomaly detection
- ✅ **Dynatrace** - AI-powered insights
- ✅ **SolarWinds** - NOC mode
- ✅ **PRTG** - Dashboard avançado

**Diferencial:** Open source core + ML nativo + Multi-tenant
