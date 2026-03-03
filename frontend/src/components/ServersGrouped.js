// Adicione estas funções após os outros useState no componente Servers

// Estado para controlar grupos expandidos
const [expandedSensorGroups, setExpandedSensorGroups] = useState({
  system: true,
  docker: true,
  services: false,
  applications: false,
  network: false
});

// Função para agrupar sensores por tipo
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

  return Object.entries(groups)
    .filter(([_, group]) => group.sensors.length > 0)
    .sort((a, b) => a[1].priority - b[1].priority);
};

// Função para toggle de grupos
const toggleSensorGroup = (groupKey) => {
  setExpandedSensorGroups(prev => ({
    ...prev,
    [groupKey]: !prev[groupKey]
  }));
};

// Função para contar status dos sensores
const getGroupStatusCounts = (groupSensors) => {
  const counts = { ok: 0, warning: 0, critical: 0, unknown: 0 };
  
  groupSensors.forEach(sensor => {
    const metric = metrics[sensor.id];
    if (metric) {
      counts[metric.status] = (counts[metric.status] || 0) + 1;
    } else {
      counts.unknown++;
    }
  });
  
  return counts;
};

// Função para renderizar resumo Docker
const renderDockerSummary = (dockerSensors) => {
  const totalSensor = dockerSensors.find(s => s.name.includes('Total'));
  const runningSensor = dockerSensors.find(s => s.name.includes('Running'));
  const stoppedSensor = dockerSensors.find(s => s.name.includes('Stopped'));
  
  const totalMetric = totalSensor ? metrics[totalSensor.id] : null;
  const runningMetric = runningSensor ? metrics[runningSensor.id] : null;
  const stoppedMetric = stoppedSensor ? metrics[stoppedSensor.id] : null;
  
  if (!totalMetric && !runningMetric && !stoppedMetric) return null;
  
  return (
    <div className="docker-summary">
      {totalMetric && (
        <div className="summary-card">
          <div className="summary-icon">📦</div>
          <div className="summary-value">{totalMetric.value || 0}</div>
          <div className="summary-label">Total</div>
        </div>
      )}
      {runningMetric && (
        <div className="summary-card">
          <div className="summary-icon">✅</div>
          <div className="summary-value">{runningMetric.value || 0}</div>
          <div className="summary-label">Rodando</div>
        </div>
      )}
      {stoppedMetric && (
        <div className="summary-card">
          <div className="summary-icon">⏸️</div>
          <div className="summary-value">{stoppedMetric.value || 0}</div>
          <div className="summary-label">Parados</div>
        </div>
      )}
    </div>
  );
};

// Função para renderizar um sensor card (extraída do map original)
const renderSensorCard = (sensor) => {
  const metric = metrics[sensor.id];
  const hasNote = sensor.last_note && sensor.last_note_by;
  const isAcknowledged = sensor.is_acknowledged;
  
  return (
    <div 
      key={sensor.id} 
      className="sensor-card"
      title={hasNote ? `Última nota: ${sensor.last_note}\n\nPor: ${sensor.last_note_by_name || 'Técnico'}\nEm: ${sensor.last_note_at ? new Date(sensor.last_note_at).toLocaleString('pt-BR') : ''}` : ''}
    >
      <div className="sensor-card-actions">
        <button 
          className="sensor-action-btn"
          onClick={(e) => handleViewSensorDetails(sensor, e)}
          title="Ver detalhes e análise da IA"
        >
          🔍
        </button>
        <button 
          className="sensor-action-btn"
          onClick={(e) => {
            e.stopPropagation();
            handleEditSensor(sensor);
          }}
          title="Editar sensor"
        >
          ✏️
        </button>
        <button 
          className="sensor-delete-btn"
          onClick={(e) => {
            e.stopPropagation();
            handleDeleteSensor(sensor.id, sensor.name);
          }}
          title="Remover sensor"
        >
          ×
        </button>
      </div>
      
      {isAcknowledged && (
        <div className="sensor-acknowledged-badge" title="Verificado pela TI - Alertas suprimidos">
          ✓ Verificado pela TI
        </div>
      )}
      
      <div className="sensor-header">
        <span className="sensor-icon">{getSensorIcon(sensor.sensor_type)}</span>
        <h3>{sensor.name}</h3>
      </div>
      {metric ? (
        <>
          <div className="sensor-value">
            {formatValue(metric.value, metric.unit)}
          </div>
          <div 
            className={`sensor-status-bar ${isAcknowledged ? 'acknowledged' : ''}`}
            style={{ backgroundColor: isAcknowledged ? '#2196f3' : getStatusColor(metric.status) }}
          >
            {isAcknowledged ? 'EM ANÁLISE' : metric.status.toUpperCase()}
          </div>
          <div className="sensor-timestamp">
            Atualizado: {new Date(metric.timestamp).toLocaleString('pt-BR')}
          </div>
        </>
      ) : (
        <div className="sensor-no-data">Aguardando dados...</div>
      )}
      <div className="sensor-thresholds">
        {sensor.sensor_type === 'ping' ? (
          <>⚠️ {sensor.threshold_warning || 100}ms | 🔥 {sensor.threshold_critical || 200}ms</>
        ) : sensor.sensor_type === 'network' ? (
          <>⚠️ {sensor.threshold_warning || 80}MB/s | 🔥 {sensor.threshold_critical || 95}MB/s</>
        ) : (
          <>⚠️ {sensor.threshold_warning || 80}% | 🔥 {sensor.threshold_critical || 95}%</>
        )}
      </div>
      
      {hasNote && (
        <div className="sensor-last-note">
          <span className="note-icon">📝</span>
          <span className="note-preview">{sensor.last_note.substring(0, 50)}{sensor.last_note.length > 50 ? '...' : ''}</span>
        </div>
      )}
    </div>
  );
};

// SUBSTITUA o <div className="sensors-grid"> por este código:
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
              <span className="group-count">({group.sensors.length})</span>
              <span className="group-status">
                {statusCounts.ok > 0 && <span className="status-badge status-ok">● {statusCounts.ok}</span>}
                {statusCounts.warning > 0 && <span className="status-badge status-warning">● {statusCounts.warning}</span>}
                {statusCounts.critical > 0 && <span className="status-badge status-critical">● {statusCounts.critical}</span>}
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

// No JSX, substitua:
// <div className="sensors-grid">
//   {sensors.map(sensor => { ... })}
// </div>
//
// Por:
// {renderGroupedSensors()}
