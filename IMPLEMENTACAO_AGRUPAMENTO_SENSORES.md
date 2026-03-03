# 🚀 Implementação: Agrupamento de Sensores

## 📋 Resumo da Sessão

Implementamos com sucesso:
1. ✅ Correção do erro "Preencha todos os campos"
2. ✅ Implementação do DockerCollector
3. ✅ Correção do erro SSL (HTTPS → HTTP)
4. ✅ Aplicação do token de autenticação
5. ✅ Probe funcionando e coletando métricas

**Próxima melhoria:** Agrupamento de sensores para melhor visualização

## 🎯 Objetivo

Agrupar sensores por tipo (Sistema, Docker, Serviços, etc.) com visualização colapsável, inspirado em PRTG e Zabbix.

## 📊 Solução Proposta

### Estrutura Visual

```
🖥️ Sistema (7 sensores) ━━━━━━━━━━━━━━━━━━━━
  [Ping] [CPU] [Memória] [Disco] [Uptime] [Network IN] [Network OUT]

🐳 Docker (15 sensores) ▼ ━━━━━━━━━━━━━━━━━━
  📊 Resumo: 6 containers, 5 rodando, 1 parado
  
  [Docker Total: 6]  [Running: 5]  [Stopped: 1]
  
  📦 Containers:
  ▼ coruja-frontend
    Status: OK | CPU: 2.5% | Memory: 15.3%
  ▼ coruja-api  
    Status: OK | CPU: 1.8% | Memory: 12.1%
  ▶ coruja-postgres (colapsado)
  ▶ coruja-redis (colapsado)

⚙️ Serviços (3 sensores) ▶ ━━━━━━━━━━━━━━━━━
  (colapsado)
```

## 🔧 Implementação Técnica

### 1. Adicionar Estado no Servers.js

```javascript
// Adicionar após os outros useState
const [sensorViewMode, setSensorViewMode] = useState('grouped'); // 'grouped' or 'flat'
const [expandedSensorGroups, setExpandedSensorGroups] = useState({
  system: true,    // Sistema sempre expandido
  docker: true,    // Docker expandido por padrão
  services: false, // Serviços colapsados
  applications: false,
  network: false
});
const [expandedDockerContainers, setExpandedDockerContainers] = useState({});
```

### 2. Criar Função de Agrupamento

```javascript
const groupSensorsByType = (sensors) => {
  const groups = {
    system: {
      name: 'Sistema',
      icon: '🖥️',
      sensors: [],
      priority: 1,
      color: '#4caf50'
    },
    docker: {
      name: 'Docker',
      icon: '🐳',
      sensors: [],
      priority: 2,
      color: '#2196f3',
      showSummary: true
    },
    services: {
      name: 'Serviços',
      icon: '⚙️',
      sensors: [],
      priority: 3,
      color: '#ff9800'
    },
    applications: {
      name: 'Aplicações',
      icon: '📦',
      sensors: [],
      priority: 4,
      color: '#9c27b0'
    },
    network: {
      name: 'Rede',
      icon: '🌐',
      sensors: [],
      priority: 5,
      color: '#00bcd4'
    }
  };

  sensors.forEach(sensor => {
    const type = sensor.sensor_type;
    
    if (['ping', 'cpu', 'memory', 'disk', 'system', 'network'].includes(type)) {
      groups.system.sensors.push(sensor);
    } else if (type === 'docker') {
      groups.docker.sensors.push(sensor);
    } else if (type === 'service') {
      groups.services.sensors.push(sensor);
    } else if (['hyperv', 'kubernetes'].includes(type)) {
      groups.applications.sensors.push(sensor);
    } else if (['http', 'port', 'dns', 'ssl', 'snmp'].includes(type)) {
      groups.network.sensors.push(sensor);
    }
  });

  // Remover grupos vazios e ordenar por prioridade
  return Object.entries(groups)
    .filter(([_, group]) => group.sensors.length > 0)
    .sort((a, b) => a[1].priority - b[1].priority);
};
```

### 3. Criar Função de Toggle

```javascript
const toggleSensorGroup = (groupKey) => {
  setExpandedSensorGroups(prev => ({
    ...prev,
    [groupKey]: !prev[groupKey]
  }));
};

const toggleDockerContainer = (containerName) => {
  setExpandedDockerContainers(prev => ({
    ...prev,
    [containerName]: !prev[containerName]
  }));
};
```

### 4. Criar Componente de Resumo Docker

```javascript
const renderDockerSummary = (dockerSensors) => {
  const totalSensor = dockerSensors.find(s => s.name.includes('Total'));
  const runningSensor = dockerSensors.find(s => s.name.includes('Running'));
  const stoppedSensor = dockerSensors.find(s => s.name.includes('Stopped'));
  
  const totalMetric = totalSensor ? metrics[totalSensor.id] : null;
  const runningMetric = runningSensor ? metrics[runningSensor.id] : null;
  const stoppedMetric = stoppedSensor ? metrics[stoppedSensor.id] : null;
  
  return (
    <div className="docker-summary">
      <div className="summary-card">
        <div className="summary-icon">📦</div>
        <div className="summary-value">{totalMetric?.value || 0}</div>
        <div className="summary-label">Total</div>
      </div>
      <div className="summary-card">
        <div className="summary-icon">✅</div>
        <div className="summary-value">{runningMetric?.value || 0}</div>
        <div className="summary-label">Rodando</div>
      </div>
      <div className="summary-card">
        <div className="summary-icon">⏸️</div>
        <div className="summary-value">{stoppedMetric?.value || 0}</div>
        <div className="summary-label">Parados</div>
      </div>
    </div>
  );
};
```

### 5. Renderizar Grupos

```javascript
const renderGroupedSensors = () => {
  const grouped = groupSensorsByType(sensors);
  
  return (
    <div className="sensors-grouped">
      {grouped.map(([groupKey, group]) => {
        const isExpanded = expandedSensorGroups[groupKey];
        const statusCounts = getGroupStatusCounts(group.sensors);
        
        return (
          <div key={groupKey} className="sensor-group">
            <div 
              className="sensor-group-header"
              onClick={() => toggleSensorGroup(groupKey)}
              style={{ borderLeftColor: group.color }}
            >
              <span className="group-icon">{group.icon}</span>
              <span className="group-name">{group.name}</span>
              <span className="group-count">({group.sensors.length} sensores)</span>
              <span className="group-status">
                {statusCounts.ok > 0 && <span className="status-ok">● {statusCounts.ok} OK</span>}
                {statusCounts.warning > 0 && <span className="status-warning">● {statusCounts.warning} Warning</span>}
                {statusCounts.critical > 0 && <span className="status-critical">● {statusCounts.critical} Critical</span>}
              </span>
              <span className="group-toggle">{isExpanded ? '▼' : '▶'}</span>
            </div>
            
            {isExpanded && (
              <div className="sensor-group-content">
                {groupKey === 'docker' && group.showSummary && renderDockerSummary(group.sensors)}
                
                <div className="sensors-grid">
                  {group.sensors.map(sensor => renderSensorCard(sensor))}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
```

### 6. Adicionar CSS

```css
/* Adicionar em Management.css */

.sensors-grouped {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sensor-group {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.sensor-group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.sensor-group-header:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.group-icon {
  font-size: 24px;
}

.group-name {
  font-size: 18px;
  font-weight: 600;
}

.group-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.group-status {
  margin-left: auto;
  display: flex;
  gap: 15px;
  font-size: 14px;
}

.status-ok { color: #4caf50; }
.status-warning { color: #ff9800; }
.status-critical { color: #f44336; }

.group-toggle {
  font-size: 20px;
  margin-left: 10px;
}

.sensor-group-content {
  padding: 20px;
}

.docker-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.summary-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.summary-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 36px;
  font-weight: 700;
  color: #333;
  margin-bottom: 5px;
}

.summary-label {
  font-size: 14px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
```

## 🎯 Resultado Esperado

### Antes (Flat)
```
[Ping] [CPU] [Memory] [Disk] [Uptime] [Network IN] [Network OUT]
[Docker Total] [Docker Running] [Docker Stopped]
[coruja-frontend Status] [coruja-frontend CPU] [coruja-frontend Memory]
[coruja-api Status] [coruja-api CPU] [coruja-api Memory]
[coruja-postgres Status] [coruja-postgres CPU] [coruja-postgres Memory]
... (15+ cards)
```

### Depois (Grouped)
```
🖥️ Sistema (7 sensores) ━━━━━━━━━━━━━━━━━━━━
  [Ping] [CPU] [Memory] [Disk] [Uptime] [Network IN] [Network OUT]

🐳 Docker (15 sensores) ▼ ━━━━━━━━━━━━━━━━━━
  📊 Resumo: [6 Total] [5 Running] [1 Stopped]
  [coruja-frontend] [coruja-api] [coruja-postgres] ...
```

## 📊 Benefícios

1. **Organização**: Sensores agrupados logicamente
2. **Escalabilidade**: Suporta centenas de sensores
3. **Usabilidade**: Menos scroll, informação contextualizada
4. **Performance**: Renderiza apenas grupos expandidos
5. **Profissionalismo**: Interface moderna e limpa

## 🚀 Próximos Passos

### Fase 2: Hierarquia Docker
- Containers individuais expandíveis
- Métricas agrupadas por container
- Drill-down navigation

### Fase 3: Filtros
- Filtrar por status
- Buscar sensores
- Ordenação customizada

### Fase 4: Persistência
- Salvar estado no localStorage
- Lembrar grupos expandidos
- Preferências do usuário

---

**Status**: Design completo, pronto para implementação
**Complexidade**: Média
**Tempo estimado**: 2-3 horas
**Impacto**: Alto (melhora significativa na UX)
