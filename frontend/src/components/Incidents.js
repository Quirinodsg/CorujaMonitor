import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Management.css';

function Incidents({ onNavigateToServer, onNavigate }) {
  const [incidents, setIncidents] = useState([]);
  const [sensors, setSensors] = useState({});
  const [servers, setServers] = useState({});
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [remediationLogs, setRemediationLogs] = useState([]);

  useEffect(() => {
    loadIncidents();
    const interval = setInterval(loadIncidents, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadIncidents = async () => {
    try {
      // Load incidents
      const incidentsResponse = await api.get('/incidents/?limit=500');
      setIncidents(incidentsResponse.data);

      // Load sensors and servers
      const sensorsResponse = await api.get('/sensors');
      const serversResponse = await api.get('/servers');

      const sensorsMap = {};
      sensorsResponse.data.forEach(sensor => {
        sensorsMap[sensor.id] = sensor;
      });
      setSensors(sensorsMap);

      const serversMap = {};
      serversResponse.data.forEach(server => {
        serversMap[server.id] = server;
      });
      setServers(serversMap);
    } catch (error) {
      console.error('Erro ao carregar incidentes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (incident) => {
    setSelectedIncident(incident);
    setShowDetailsModal(true);
    
    // Load remediation logs
    try {
      const response = await api.get(`/incidents/${incident.id}/remediation`);
      setRemediationLogs(response.data);
    } catch (error) {
      console.error('Erro ao carregar logs de remediação:', error);
      setRemediationLogs([]);
    }
  };

  const handleReopen = async (incident) => {
    try {
      await api.post(`/incidents/${incident.id}/reopen`);
      await loadIncidents();
    } catch (error) {
      console.error('Erro ao reabrir incidente:', error);
      alert('Erro ao reabrir: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleStopCalls = async (incident) => {
    try {
      const res = await api.post(`/incidents/${incident.id}/stop-calls`);
      alert(res.data.message);
    } catch (error) {
      alert('Erro ao parar ligações: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleRedispatch = async (incident) => {
    try {
      await api.post(`/incidents/${incident.id}/redispatch`);
      alert('✅ Notificações enfileiradas para re-envio.\nVerifique SMS, WhatsApp e ligação em alguns segundos.');
    } catch (error) {
      alert('Erro ao re-despachar: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleAcknowledge = async (incident) => {
    try {
      await api.post(`/incidents/${incident.id}/acknowledge`, { notes: '' });
      await loadIncidents();
    } catch (error) {
      console.error('Erro ao reconhecer incidente:', error);
      alert('Erro ao reconhecer: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#f44336';
      case 'warning': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return '🔥';
      case 'warning': return '⚠️';
      default: return 'ℹ️';
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      open: { text: 'Aberto', color: '#f44336', icon: '🚨' },
      acknowledged: { text: 'Reconhecido', color: '#2196f3', icon: '✓' },
      auto_resolved: { text: 'Auto-Resolvido', color: '#4caf50', icon: '✅' },
      resolved: { text: 'Resolvido', color: '#4caf50', icon: '✅' }
    };
    
    const badge = badges[status] || badges.open;
    return (
      <span style={{
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: '600',
        backgroundColor: badge.color + '20',
        color: badge.color
      }}>
        {badge.icon} {badge.text}
      </span>
    );
  };

  const getDuration = (createdAt, resolvedAt) => {
    const start = new Date(createdAt);
    const end = resolvedAt ? new Date(resolvedAt) : new Date();
    const diff = Math.floor((end - start) / 1000); // seconds

    if (diff < 60) return `${diff}s`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
    return `${Math.floor(diff / 86400)}d ${Math.floor((diff % 86400) / 3600)}h`;
  };

  const getFilteredIncidents = () => {
    let filtered = incidents;

    if (filterStatus !== 'all') {
      filtered = filtered.filter(inc => inc.status === filterStatus);
    }

    if (filterSeverity !== 'all') {
      filtered = filtered.filter(inc => inc.severity === filterSeverity);
    }

    return filtered;
  };

  const getIncidentCounts = () => {
    const counts = {
      all: incidents.length,
      open: 0,
      acknowledged: 0,
      resolved: 0,
      critical: 0,
      warning: 0
    };

    incidents.forEach(inc => {
      if (inc.status === 'open') counts.open++;
      if (inc.status === 'acknowledged') counts.acknowledged++;
      if (inc.status === 'resolved' || inc.status === 'auto_resolved') counts.resolved++;
      if (inc.severity === 'critical') counts.critical++;
      if (inc.severity === 'warning') counts.warning++;
    });

    return counts;
  };

  if (loading) {
    return <div className="management-container">Carregando...</div>;
  }

  const counts = getIncidentCounts();
  const filteredIncidents = getFilteredIncidents();

  return (
    <div className="management-container">
      <div className="management-header">
        <h1>🚨 Incidentes</h1>
        <button className="btn-add" onClick={loadIncidents}>
          🔄 Atualizar
        </button>
      </div>

      {/* Summary Cards */}
      <div className="incidents-summary">
        <div className="summary-card" style={{ borderLeft: '4px solid #2196f3' }}>
          <div className="summary-icon">📊</div>
          <div className="summary-info">
            <h3>{counts.all}</h3>
            <p>Total de Incidentes</p>
          </div>
        </div>

        <div 
          className={`summary-card clickable ${filterStatus === 'open' ? 'active' : ''}`}
          style={{ borderLeft: '4px solid #f44336' }}
          onClick={() => setFilterStatus('open')}
        >
          <div className="summary-icon">🚨</div>
          <div className="summary-info">
            <h3>{counts.open}</h3>
            <p>Abertos</p>
          </div>
        </div>

        <div 
          className={`summary-card clickable ${filterSeverity === 'critical' ? 'active' : ''}`}
          style={{ borderLeft: '4px solid #f44336' }}
          onClick={() => setFilterSeverity('critical')}
        >
          <div className="summary-icon">🔥</div>
          <div className="summary-info">
            <h3>{counts.critical}</h3>
            <p>Críticos</p>
          </div>
        </div>

        <div 
          className={`summary-card clickable ${filterSeverity === 'warning' ? 'active' : ''}`}
          style={{ borderLeft: '4px solid #ff9800' }}
          onClick={() => setFilterSeverity('warning')}
        >
          <div className="summary-icon">⚠️</div>
          <div className="summary-info">
            <h3>{counts.warning}</h3>
            <p>Avisos</p>
          </div>
        </div>

        <div 
          className={`summary-card clickable ${filterStatus === 'resolved' || filterStatus === 'auto_resolved' ? 'active' : ''}`}
          style={{ borderLeft: '4px solid #4caf50' }}
          onClick={() => setFilterStatus(filterStatus === 'resolved' ? 'all' : 'resolved')}
        >
          <div className="summary-icon">✅</div>
          <div className="summary-info">
            <h3>{counts.resolved}</h3>
            <p>Resolvidos</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="incidents-filters">
        <button 
          className={`filter-btn ${filterStatus === 'all' && filterSeverity === 'all' ? 'active' : ''}`}
          onClick={() => { setFilterStatus('all'); setFilterSeverity('all'); }}
        >
          Todos
        </button>
        <button 
          className={`filter-btn ${filterStatus === 'open' ? 'active' : ''}`}
          onClick={() => setFilterStatus('open')}
        >
          Abertos
        </button>
        <button 
          className={`filter-btn ${filterStatus === 'acknowledged' ? 'active' : ''}`}
          onClick={() => setFilterStatus('acknowledged')}
        >
          Reconhecidos
        </button>
        <button 
          className={`filter-btn ${filterSeverity === 'critical' ? 'active' : ''}`}
          onClick={() => setFilterSeverity('critical')}
        >
          Críticos
        </button>
        <button 
          className={`filter-btn ${filterSeverity === 'warning' ? 'active' : ''}`}
          onClick={() => setFilterSeverity('warning')}
        >
          Avisos
        </button>
      </div>

      {/* Incidents Table */}
      <div className="incidents-table-container">
        <table className="incidents-table">
          <thead>
            <tr>
              <th>Severidade</th>
              <th>Status</th>
              <th>Servidor</th>
              <th>Sensor</th>
              <th>Descrição</th>
              <th>Duração</th>
              <th>Criado em</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {filteredIncidents.length === 0 ? (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                  {filterStatus !== 'all' || filterSeverity !== 'all' 
                    ? 'Nenhum incidente encontrado com os filtros selecionados'
                    : '✅ Nenhum incidente registrado'}
                </td>
              </tr>
            ) : (
              filteredIncidents.map(incident => {
                const sensor = sensors[incident.sensor_id];
                const server = sensor ? servers[sensor.server_id] : null;

                return (
                  <tr 
                    key={incident.id} 
                    className={`incident-row severity-${incident.severity}`}
                    data-status={incident.status}
                  >
                    <td>
                      <span 
                        className="severity-badge"
                        style={{ 
                          backgroundColor: getSeverityColor(incident.severity) + '20',
                          color: getSeverityColor(incident.severity)
                        }}
                      >
                        {getSeverityIcon(incident.severity)} {incident.severity.toUpperCase()}
                      </span>
                    </td>
                    <td>{getStatusBadge(incident.status)}</td>
                    <td>
                      <strong>{server?.hostname || (sensor ? '— Standalone —' : 'Desconhecido')}</strong>
                      <br />
                      <small style={{ color: '#999' }}>{server?.ip_address || (sensor ? sensor.sensor_type : '')}</small>
                    </td>
                    <td>
                      <strong>{sensor?.name || 'Sensor desconhecido'}</strong>
                      <br />
                      <small style={{ color: '#999' }}>{sensor?.sensor_type}</small>
                    </td>
                    <td>
                      <div className="incident-description">
                        <strong>{incident.title}</strong>
                        {incident.description && (
                          <p style={{ margin: '5px 0 0 0', fontSize: '13px', color: '#666' }}>
                            {incident.description}
                          </p>
                        )}
                        {incident.root_cause && (
                          <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#2196f3' }}>
                            🤖 {incident.root_cause}
                          </p>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="duration-badge">
                        ⏱️ {getDuration(incident.created_at, incident.resolved_at)}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontSize: '13px' }}>
                        {new Date(incident.created_at).toLocaleString('pt-BR')}
                      </div>
                      {incident.resolved_at && (
                        <div style={{ fontSize: '11px', color: '#4caf50', marginTop: '4px' }}>
                          ✅ {new Date(incident.resolved_at).toLocaleString('pt-BR')}
                        </div>
                      )}
                    </td>
                    <td>
                      <div className="incident-actions">
                        <button
                          className="btn-action btn-small"
                          onClick={() => handleViewDetails(incident)}
                          title="Ver detalhes"
                        >
                          🔍
                        </button>
                        {incident.status === 'open' && (
                          <button
                            className="btn-action btn-small"
                            onClick={() => handleAcknowledge(incident)}
                            title="Reconhecer incidente"
                            style={{ background: '#2196f3' }}
                          >
                            ✓
                          </button>
                        )}
                        {incident.status === 'open' && (
                          <button
                            className="btn-action btn-small"
                            onClick={() => handleRedispatch(incident)}
                            title="Re-enviar notificações (SMS, WhatsApp, Ligação)"
                            style={{ background: '#9c27b0' }}
                          >
                            📣
                          </button>
                        )}
                        {incident.status === 'open' && (
                          <button
                            className="btn-action btn-small"
                            onClick={() => handleStopCalls(incident)}
                            title="Parar ligações de escalação"
                            style={{ background: '#e53935' }}
                          >
                            🔕
                          </button>
                        )}
                        {(incident.status === 'acknowledged' || incident.status === 'resolved' || incident.status === 'auto_resolved') && (
                          <button
                            className="btn-action btn-small"
                            onClick={() => handleReopen(incident)}
                            title="Reabrir incidente"
                            style={{ background: '#ff9800' }}
                          >
                            🔄
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Details Modal */}
      {showDetailsModal && selectedIncident && (
        <div className="modal-overlay" onClick={() => setShowDetailsModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🔍 Detalhes do Incidente #{selectedIncident.id}</h2>
              <button className="btn-close" onClick={() => setShowDetailsModal(false)}>×</button>
            </div>

            <div className="incident-details-content">
              {/* Basic Info */}
              <div className="detail-section">
                <h3>Informações Básicas</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <strong>Severidade:</strong>
                    <span 
                      className="severity-badge"
                      style={{ 
                        backgroundColor: getSeverityColor(selectedIncident.severity) + '20',
                        color: getSeverityColor(selectedIncident.severity),
                        marginLeft: '10px'
                      }}
                    >
                      {getSeverityIcon(selectedIncident.severity)} {selectedIncident.severity.toUpperCase()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <strong>Status:</strong>
                    <span style={{ marginLeft: '10px' }}>{getStatusBadge(selectedIncident.status)}</span>
                  </div>
                  <div className="detail-item">
                    <strong>Servidor:</strong> {servers[sensors[selectedIncident.sensor_id]?.server_id]?.hostname}
                  </div>
                  <div className="detail-item">
                    <strong>Sensor:</strong> {sensors[selectedIncident.sensor_id]?.name}
                  </div>
                  <div className="detail-item">
                    <strong>Duração:</strong> ⏱️ {getDuration(selectedIncident.created_at, selectedIncident.resolved_at)}
                  </div>
                  <div className="detail-item">
                    <strong>Criado em:</strong> {new Date(selectedIncident.created_at).toLocaleString('pt-BR')}
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="detail-section">
                <h3>Descrição</h3>
                <p>{selectedIncident.description || 'Sem descrição'}</p>
              </div>

              {/* AI Analysis */}
              {selectedIncident.root_cause && (
                <div className="detail-section ai-section">
                  <h3>🤖 Análise da IA</h3>
                  <div className="ai-root-cause">
                    <strong>Causa Raiz:</strong>
                    <p>{selectedIncident.root_cause}</p>
                  </div>
                  {selectedIncident.ai_analysis && (
                    <div className="ai-details">
                      <pre>{JSON.stringify(selectedIncident.ai_analysis, null, 2)}</pre>
                    </div>
                  )}
                </div>
              )}

              {/* Remediation Logs */}
              {remediationLogs.length > 0 && (
                <div className="detail-section">
                  <h3>🔧 Tentativas de Remediação</h3>
                  <div className="remediation-logs">
                    {remediationLogs.map(log => (
                      <div key={log.id} className={`remediation-log ${log.success ? 'success' : 'failed'}`}>
                        <div className="log-header">
                          <span className="log-icon">{log.success ? '✅' : '❌'}</span>
                          <strong>{log.action_type}</strong>
                          <span className="log-time">{new Date(log.executed_at).toLocaleString('pt-BR')}</span>
                        </div>
                        {log.action_description && (
                          <p className="log-description">{log.action_description}</p>
                        )}
                        {log.error_message && (
                          <p className="log-error">❌ {log.error_message}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowDetailsModal(false)}>
                Fechar
              </button>
              {selectedIncident.status === 'open' && (
                <button 
                  className="btn-primary" 
                  onClick={() => {
                    handleAcknowledge(selectedIncident);
                    setShowDetailsModal(false);
                  }}
                >
                  ✓ Reconhecer Incidente
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Incidents;
