# 🎨 Design: Agrupamento de Sensores

## 🎯 Objetivo

Agrupar sensores por tipo/categoria para melhorar visualização quando há muitos sensores (especialmente Docker).

## 📊 Inspiração (Melhores Ferramentas)

### PRTG Network Monitor
```
📁 Servidor Web-01
  📂 Sistema (7 sensores)
    ├─ Ping
    ├─ CPU
    ├─ Memória
    └─ ...
  📂 Docker (15 sensores) ← Colapsável
    ├─ Docker Total: 6 containers
    ├─ Docker Running: 6
    ├─ coruja-frontend
    └─ ...
  📂 Serviços (5 sensores)
    └─ ...
```

### Zabbix
```
Host: Servidor-01
  ▼ System (5)
  ▼ Docker (12) ← Expandido
    • Docker Containers Total: 6
    • Docker Containers Running: 6
    • coruja-frontend Status: OK
    • coruja-frontend CPU: 2.5%
  ▶ Services (3) ← Colapsado
```

### Datadog
```
Infrastructure > Containers
  🐳 Docker Overview
    ├─ 6 containers running
    ├─ CPU: 15.3%
    └─ Memory: 2.1GB
  
  📦 Container List (expandir)
    ├─ coruja-frontend
    ├─ coruja-api
    └─ ...
```

## 🏗️ Proposta de Implementação

### Estrutura de Grupos

```javascript
const sensorGroups = {
  'system': {
    name: 'Sistema',
    icon: '🖥️',
    sensors: ['ping', 'cpu', 'memory', 'disk', 'system', 'network'],
    color: '#4caf50',
    priority: 1
  },
  'docker': {
    name: 'Docker',
    icon: '🐳',
    sensors: ['docker'],
    color: '#2196f3',
    priority: 2,
    collapsible: true,
    showSummary: true
  },
  'services': {
    name: 'Serviços',
    icon: '⚙️',
    sensors: ['service'],
    color: '#ff9800',
    priority: 3,
    collapsible: true
  },
  'applications': {
    name: 'Aplicações',
    icon: '📦',
    sensors: ['hyperv', 'kubernetes'],
    color: '#9c27b0',
    priority: 4,
    collapsible: true
  },
  'network': {
    name: 'Rede',
    icon: '🌐',
    sensors: ['http', 'port', 'dns', 'ssl', 'snmp'],
    color: '#00bcd4',
    priority: 5,
    collapsible: true
  }
};
```

### Visualização Proposta

```
┌─────────────────────────────────────────┐
│ Sensores de Servidor-01          [+ Add]│
├─────────────────────────────────────────┤
│                                          │
│ 🖥️ Sistema (7 sensores) ━━━━━━━━━━━━━━ │
│   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│   │ Ping │ │ CPU  │ │ Mem  │ │ Disk │  │
│   │ 12ms │ │ 45%  │ │ 62%  │ │ 78%  │  │
│   │  OK  │ │  OK  │ │  OK  │ │ WARN │  │
│   └──────┘ └──────┘ └──────┘ └──────┘  │
│                                          │
│ 🐳 Docker (15 sensores) ▼ ━━━━━━━━━━━━ │
│   📊 Resumo: 6 containers, 5 rodando    │
│   ┌────────────────┐ ┌────────────────┐ │
│   │ Total: 6       │ │ Running: 5     │ │
│   │ containers     │ │ containers     │ │
│   └────────────────┘ └────────────────┘ │
│                                          │
│   📦 Containers (clique para expandir)  │
│   ▼ coruja-frontend                     │
│     ├─ Status: OK                       │
│     ├─ CPU: 2.5%                        │
│     └─ Memory: 15.3%                    │
│   ▼ coruja-api                          │
│     ├─ Status: OK                       │
│     ├─ CPU: 1.8%                        │
│     └─ Memory: 12.1%                    │
│   ▶ coruja-postgres (colapsado)        │
│   ▶ coruja-redis (colapsado)           │
│                                          │
│ ⚙️ Serviços (3 sensores) ▶ ━━━━━━━━━━ │
│   (colapsado)                           │
│                                          │
└─────────────────────────────────────────┘
```

## 🎨 Componentes UI

### 1. Grupo de Sensores (SensorGroup)
```jsx
<div className="sensor-group">
  <div className="sensor-group-header" onClick={toggleGroup}>
    <span className="group-icon">🐳</span>
    <span className="group-name">Docker</span>
    <span className="group-count">(15 sensores)</span>
    <span className="group-status">● 5 OK, 1 Warning</span>
    <span className="group-toggle">{expanded ? '▼' : '▶'}</span>
  </div>
  
  {expanded && showSummary && (
    <div className="sensor-group-summary">
      <div className="summary-card">
        <div className="summary-value">6</div>
        <div className="summary-label">Total Containers</div>
      </div>
      <div className="summary-card">
        <div className="summary-value">5</div>
        <div className="summary-label">Running</div>
      </div>
    </div>
  )}
  
  {expanded && (
    <div className="sensor-group-content">
      {sensors.map(sensor => <SensorCard sensor={sensor} />)}
    </div>
  )}
</div>
```

### 2. Container Docker Expandível
```jsx
<div className="docker-container-item">
  <div className="container-header" onClick={toggleContainer}>
    <span className="container-icon">📦</span>
    <span className="container-name">coruja-frontend</span>
    <span className="container-status">● OK</span>
    <span className="container-toggle">{expanded ? '▼' : '▶'}</span>
  </div>
  
  {expanded && (
    <div className="container-metrics">
      <div className="metric-row">
        <span className="metric-label">Status:</span>
        <span className="metric-value">Running</span>
      </div>
      <div className="metric-row">
        <span className="metric-label">CPU:</span>
        <span className="metric-value">2.5%</span>
      </div>
      <div className="metric-row">
        <span className="metric-label">Memory:</span>
        <span className="metric-value">15.3%</span>
      </div>
    </div>
  )}
</div>
```

## 🎯 Funcionalidades

### 1. Agrupamento Automático
- Sensores agrupados por tipo automaticamente
- Ordem de prioridade configurável
- Grupos colapsáveis/expansíveis

### 2. Resumo do Grupo
- Estatísticas agregadas (total, OK, warning, critical)
- Métricas principais (para Docker: total containers, running, stopped)
- Status geral do grupo

### 3. Visualização Hierárquica
- Grupo → Sensores → Detalhes
- Docker: Grupo → Resumo → Containers → Métricas
- Navegação intuitiva

### 4. Filtros e Busca
- Filtrar por status (OK, Warning, Critical)
- Buscar por nome de sensor
- Mostrar/ocultar grupos

### 5. Persistência de Estado
- Lembrar quais grupos estão expandidos
- Salvar no localStorage
- Restaurar ao recarregar página

## 📱 Responsividade

### Desktop (> 1200px)
- Grupos lado a lado
- 3-4 sensores por linha
- Resumo expandido

### Tablet (768px - 1200px)
- Grupos empilhados
- 2-3 sensores por linha
- Resumo compacto

### Mobile (< 768px)
- Grupos em lista
- 1 sensor por linha
- Resumo mínimo

## 🎨 Estilos CSS

```css
.sensor-group {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.sensor-group-header {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sensor-group-header:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.sensor-group-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  padding: 20px;
  background: #f5f5f5;
}

.summary-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.docker-container-item {
  border-left: 3px solid #2196f3;
  margin: 10px 0;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}

.container-metrics {
  padding: 10px 20px;
  background: white;
  margin-top: 10px;
  border-radius: 4px;
}
```

## 🚀 Implementação Faseada

### Fase 1: Agrupamento Básico
- Agrupar sensores por tipo
- Grupos colapsáveis
- Contagem de sensores

### Fase 2: Resumo e Estatísticas
- Resumo do grupo Docker
- Status agregado
- Métricas principais

### Fase 3: Hierarquia Docker
- Containers expandíveis
- Métricas por container
- Navegação drill-down

### Fase 4: Filtros e Busca
- Filtrar por status
- Buscar sensores
- Ordenação

### Fase 5: Persistência
- Salvar estado no localStorage
- Preferências do usuário
- Restaurar ao recarregar

## 📊 Benefícios

### Organização
- ✅ Sensores agrupados logicamente
- ✅ Fácil navegação
- ✅ Visão geral clara

### Escalabilidade
- ✅ Suporta centenas de sensores
- ✅ Performance mantida
- ✅ Interface limpa

### Usabilidade
- ✅ Menos scroll
- ✅ Informação contextualizada
- ✅ Ações rápidas

### Profissionalismo
- ✅ Interface moderna
- ✅ Padrão da indústria
- ✅ Experiência premium

---

**Próximo Passo:** Implementar Fase 1 (Agrupamento Básico)
