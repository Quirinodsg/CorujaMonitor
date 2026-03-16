import React, { useState, useEffect } from 'react';
import api from '../services/api';
import SensorLibrary from './SensorLibrary';
import './Management.css';
import './SensorGroups.css';

function Sensors({ onNavigateToServer, initialFilter = 'all' }) {
  const [sensors, setSensors] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [servers, setServers] = useState({});
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState(initialFilter);
  const [searchText, setSearchText] = useState('');
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 50;
  const [sensorIncidents, setSensorIncidents] = useState({});
  const [viewMode, setViewMode] = useState('sensors'); // 'sensors' ou 'library'
  const [expandedSensorGroups, setExpandedSensorGroups] = useState({
    system: false,
    docker: false,
    services: false,
    applications: false,
    network: false
  });

  useEffect(() => {
    // Update filter when initialFilter changes
    setFilterStatus(initialFilter);
  }, [initialFilter]);

  useEffect(() => {
    loadAllSensors();
    const interval = setInterval(loadAllSensors, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadSensorIncidents = async () => {
    try {
      const response = await api.get('/incidents/?status=open');
      const incidentsMap = {};
      response.data.forEach(incident => {
        incidentsMap[incident.sensor_id] = incident;
      });
      setSensorIncidents(incidentsMap);
    } catch (error) {
      console.error('Erro ao carregar incidentes:', error);
    }
  };

  const loadAllSensors = async () => {
    try {
      // Load all servers first
      const serversResponse = await api.get('/servers/');
      const serversMap = {};
      serversResponse.data.forEach(server => {
        serversMap[server.id] = server;
      });
      setServers(serversMap);

      // Load all sensors
      const sensorsResponse = await api.get('/sensors/');
      setSensors(sensorsResponse.data);

      // Load incidents
      await loadSensorIncidents();

      // Load latest metrics for each sensor
      const metricsData = {};
      for (const sensor of sensorsResponse.data) {
        try {
          const metricsResponse = await api.get(`/metrics/?sensor_id=${sensor.id}&limit=1`);
          if (metricsResponse.data.length > 0) {
            metricsData[sensor.id] = metricsResponse.data[0];
          }
        } catch (err) {
          console.error(`Erro ao carregar métricas do sensor ${sensor.id}:`, err);
        }
      }
      setMetrics(metricsData);
    } catch (error) {
      console.error('Erro ao carregar sensores:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ok': return '#4caf50';
      case 'warning': return '#ff9800';
      case 'critical': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const formatValue = (value, unit) => {
    if (unit === 'percent') {
      return `${value.toFixed(1)}%`;
    } else if (unit === 'bytes/s') {
      const mbps = value / 1024 / 1024;
      return `${mbps.toFixed(2)} MB/s`;
    } else if (unit === 'status') {
      return value === 1 ? 'Online' : 'Offline';
    } else if (unit === 'days') {
      const days = Math.floor(value);
      const hours = Math.floor((value - days) * 24);
      const minutes = Math.floor(((value - days) * 24 - hours) * 60);
      return `${days}d ${hours}h ${minutes}m`;
    } else if (unit === 'ms') {
      return `${value.toFixed(0)} ms`;
    }
    return value.toFixed(2);
  };

  const getSensorIcon = (type) => {
    switch (type) {
      case 'ping': return '📡';
      case 'cpu': return '🖥️';
      case 'memory': return '💾';
      case 'disk': return '💿';
      case 'network': return '🌐';
      case 'service': return '⚙️';
      case 'system': return '⏱️';
      case 'hyperv': return '🖼️';
      case 'docker': return '🐳';
      default: return '📊';
    }
  };

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

    // Retornar TODOS os grupos, mesmo vazios, ordenados por prioridade
    return Object.entries(groups).sort((a, b) => a[1].priority - b[1].priority);
  };

  const toggleSensorGroup = (groupKey) => {
    setExpandedSensorGroups(prev => ({
      ...prev,
      [groupKey]: !prev[groupKey]
    }));
  };

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

  const handleSensorClick = (sensor) => {
    // Navigate to servers page with this server and sensor selected
    if (onNavigateToServer) {
      onNavigateToServer(sensor.server_id, sensor.id);
    }
  };

  const handleResolveIncident = async (e, sensorId, sensorName) => {
    e.stopPropagation(); // Prevent card click
    
    const incident = sensorIncidents[sensorId];
    if (!incident) return;
    
    const notes = prompt(`Resolver incidente do sensor "${sensorName}"?\n\nAdicione uma nota de resolução (opcional):`);
    if (notes === null) return; // User cancelled
    
    try {
      await api.post(`/incidents/${incident.id}/resolve`, {
        resolution_notes: notes || 'Incidente resolvido manualmente pelo administrador'
      });
      
      alert('Incidente resolvido com sucesso!');
      
      // Reload data
      await loadAllSensors();
    } catch (error) {
      console.error('Erro ao resolver incidente:', error);
      alert('Erro ao resolver incidente: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getFilteredSensors = () => {
    let result = sensors;
    if (filterStatus !== 'all') {
      if (filterStatus === 'acknowledged') {
        result = result.filter(sensor => sensor.is_acknowledged);
      } else {
        result = result.filter(sensor => {
          const metric = metrics[sensor.id];
          if (!metric) return filterStatus === 'unknown';
          return metric.status === filterStatus;
        });
      }
    }
    if (searchText) {
      const q = searchText.toLowerCase();
      result = result.filter(s => s.name?.toLowerCase().includes(q) || s.sensor_type?.toLowerCase().includes(q));
    }
    return result;
  };

  const getStatusCounts = () => {
    const counts = { ok: 0, warning: 0, critical: 0, unknown: 0, acknowledged: 0 };
    sensors.forEach(sensor => {
      // Sensores reconhecidos contam separadamente
      if (sensor.is_acknowledged) {
        counts.acknowledged++;
        return;
      }
      
      const metric = metrics[sensor.id];
      if (!metric) {
        counts.unknown++;
      } else {
        counts[metric.status] = (counts[metric.status] || 0) + 1;
      }
    });
    return counts;
  };

  if (loading) {
    return <div className="management-container">Carregando...</div>;
  }

  const statusCounts = getStatusCounts();
  const filteredSensors = getFilteredSensors();
  const totalPages = Math.ceil(filteredSensors.length / PAGE_SIZE);
  const paginatedSensors = filteredSensors.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="management-container">
      <div className="management-header">
        <h1>📡 Sensores</h1>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={() => setViewMode('sensors')}
            style={{
              padding: '8px 16px',
              background: viewMode === 'sensors' ? '#2196f3' : '#f5f5f5',
              color: viewMode === 'sensors' ? 'white' : '#666',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 'bold',
              transition: 'all 0.2s'
            }}
          >
            📡 Todos os Sensores
          </button>
          <button
            onClick={() => setViewMode('library')}
            style={{
              padding: '8px 16px',
              background: viewMode === 'library' ? '#2196f3' : '#f5f5f5',
              color: viewMode === 'library' ? 'white' : '#666',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 'bold',
              transition: 'all 0.2s'
            }}
          >
            📚 Biblioteca
          </button>
        </div>
      </div>

      {viewMode === 'sensors' ? (
        <>
      <div className="sensors-summary">
        <div 
          className={`summary-card ${filterStatus === 'all' ? 'active' : ''}`}
          onClick={() => setFilterStatus('all')}
        >
          <div className="summary-icon">📊</div>
          <div className="summary-info">
            <h3>{sensors.length}</h3>
            <p>Total</p>
          </div>
        </div>

        <div 
          className={`summary-card ok ${filterStatus === 'ok' ? 'active' : ''}`}
          onClick={() => setFilterStatus('ok')}
        >
          <div className="summary-icon">✅</div>
          <div className="summary-info">
            <h3>{statusCounts.ok}</h3>
            <p>OK</p>
          </div>
        </div>

        <div 
          className={`summary-card warning ${filterStatus === 'warning' ? 'active' : ''}`}
          onClick={() => setFilterStatus('warning')}
        >
          <div className="summary-icon">⚠️</div>
          <div className="summary-info">
            <h3>{statusCounts.warning}</h3>
            <p>Aviso</p>
          </div>
        </div>

        <div 
          className={`summary-card critical ${filterStatus === 'critical' ? 'active' : ''}`}
          onClick={() => setFilterStatus('critical')}
        >
          <div className="summary-icon">🔥</div>
          <div className="summary-info">
            <h3>{statusCounts.critical}</h3>
            <p>Crítico</p>
          </div>
        </div>

        <div 
          className={`summary-card ${filterStatus === 'acknowledged' ? 'active' : ''}`}
          onClick={() => setFilterStatus('acknowledged')}
          style={{ borderLeft: '4px solid #2196f3' }}
        >
          <div className="summary-icon">✓</div>
          <div className="summary-info">
            <h3>{statusCounts.acknowledged}</h3>
            <p>Verificado pela TI</p>
          </div>
        </div>

        <div 
          className={`summary-card unknown ${filterStatus === 'unknown' ? 'active' : ''}`}
          onClick={() => setFilterStatus('unknown')}
        >
          <div className="summary-icon">❓</div>
          <div className="summary-info">
            <h3>{statusCounts.unknown}</h3>
            <p>Desconhecido</p>
          </div>
        </div>
      </div>

      <div className="sensors-grouped">
        <div style={{ marginBottom: '12px' }}>
          <input
            type="text"
            placeholder="🔍 Buscar sensor por nome ou tipo..."
            value={searchText}
            onChange={e => { setSearchText(e.target.value); setPage(1); }}
            style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '14px', boxSizing: 'border-box' }}
          />
        </div>
        {groupSensorsByType(paginatedSensors).map(([groupKey, group]) => {
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
                    {group.sensors.map(sensor => {
                      const metric = metrics[sensor.id];
                      const server = servers[sensor.server_id];
                      const isAcknowledged = sensor.is_acknowledged;
                      const hasNote = sensor.last_note && sensor.last_note_by;
                      
                      return (
                        <div 
                          key={sensor.id} 
                          className="sensor-card clickable"
                          onClick={() => handleSensorClick(sensor)}
                          style={{ cursor: 'pointer' }}
                          title={hasNote ? `Última nota: ${sensor.last_note}\n\nPor: ${sensor.last_note_by_name || 'Técnico'}\nEm: ${sensor.last_note_at ? new Date(sensor.last_note_at).toLocaleString('pt-BR') : ''}` : ''}
                        >
                          {isAcknowledged && (
                            <div className="sensor-acknowledged-badge" title="Verificado pela TI - Alertas suprimidos">
                              ✓ Verificado pela TI
                            </div>
                          )}
                          
                          <div className="sensor-header">
                            <span className="sensor-icon">{getSensorIcon(sensor.sensor_type)}</span>
                            <div className="sensor-title">
                              <h3>{sensor.name}</h3>
                              <p className="sensor-server">{server?.hostname || 'Servidor desconhecido'}</p>
                            </div>
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
                                {new Date(metric.timestamp).toLocaleString('pt-BR')}
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
                          
                          {/* Botão Resolver Incidente */}
                          {sensorIncidents[sensor.id] && metric && (metric.status === 'critical' || metric.status === 'warning') && !isAcknowledged && (
                            <button
                              className="resolve-incident-btn"
                              onClick={(e) => handleResolveIncident(e, sensor.id, sensor.name)}
                              style={{
                                width: '100%',
                                padding: '8px 12px',
                                marginTop: '8px',
                                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                                color: 'white',
                                border: 'none',
                                borderRadius: '6px',
                                fontSize: '13px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '6px'
                              }}
                              onMouseEnter={(e) => e.target.style.transform = 'translateY(-1px)'}
                              onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
                            >
                              ✓ Resolver Incidente
                            </button>
                          )}
                          
                          {hasNote && (
                            <div className="sensor-last-note">
                              <span className="note-icon">📝</span>
                              <span className="note-preview">{sensor.last_note.substring(0, 50)}{sensor.last_note.length > 50 ? '...' : ''}</span>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {filteredSensors.length === 0 && (
        <div className="no-data">
          <p>Nenhum sensor encontrado com o filtro selecionado</p>
        </div>
      )}

      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '12px', padding: '16px 0' }}>
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid #ddd', cursor: page === 1 ? 'not-allowed' : 'pointer' }}>← Anterior</button>
          <span style={{ fontSize: '14px', color: '#666' }}>Página {page} de {totalPages} ({filteredSensors.length} sensores)</span>
          <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)} style={{ padding: '6px 14px', borderRadius: '6px', border: '1px solid #ddd', cursor: page === totalPages ? 'not-allowed' : 'pointer' }}>Próxima →</button>
        </div>
      )}
      </>
      ) : (
        <SensorLibrary />
      )}
    </div>
  );
}

export default Sensors;
