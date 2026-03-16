import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import './Dashboard.css';

const WS_URL = (() => {
  const apiUrl = process.env.REACT_APP_API_URL;
  if (apiUrl && !apiUrl.includes('localhost')) {
    return apiUrl.replace(/^http/, 'ws') + '/ws/dashboard';
  }
  // Usar o host atual da página (funciona em produção sem precisar de rebuild)
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.hostname}:8000/ws/dashboard`;
})();

function Dashboard({ user, onLogout, onNavigate, onEnterNOC }) {
  const [overview, setOverview] = useState(null);
  const [healthSummary, setHealthSummary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [servers, setServers] = useState([]);
  const [filterCompany, setFilterCompany] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [filterCriticality, setFilterCriticality] = useState('all');
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      loadDashboardData();
    } else {
      onLogout();
    }

    // WebSocket para refresh em tempo real
    const connectWS = () => {
      try {
        const token = localStorage.getItem('token');
        const ws = new WebSocket(`${WS_URL}?token=${token}`);
        wsRef.current = ws;

        ws.onopen = () => setWsConnected(true);
        ws.onclose = () => {
          setWsConnected(false);
          // Reconectar após 5s
          reconnectRef.current = setTimeout(connectWS, 5000);
        };
        ws.onerror = () => ws.close();
        ws.onmessage = (evt) => {
          try {
            const msg = JSON.parse(evt.data);
            if (msg.type === 'overview') setOverview(msg.data);
            if (msg.type === 'health') setHealthSummary(msg.data);
            if (msg.type === 'incident') setIncidents(prev => [msg.data, ...prev].slice(0, 10));
          } catch (_) {}
        };
      } catch (_) {}
    };

    connectWS();

    // Fallback polling a cada 30s
    const interval = setInterval(() => {
      if (!wsConnected) loadDashboardData();
    }, 30000);

    return () => {
      clearInterval(interval);
      clearTimeout(reconnectRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [onLogout]);

  const loadDashboardData = async () => {
    try {
      const [overviewRes, healthRes, incidentsRes, serversRes] = await Promise.all([
        api.get('/dashboard/overview'),
        api.get('/dashboard/health-summary'),
        api.get('/incidents?limit=10'),
        api.get('/servers/')
      ]);

      setOverview(overviewRes.data);
      setHealthSummary(healthRes.data);
      setIncidents(incidentsRes.data);
      setServers(serversRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      
      // If unauthorized, logout
      if (error.response?.status === 401) {
        onLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'critical': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getSeverityBadge = (severity) => {
    const colors = {
      critical: '#ef4444',
      warning: '#f59e0b'
    };
    return (
      <span style={{
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: '600',
        backgroundColor: colors[severity] + '20',
        color: colors[severity]
      }}>
        {severity === 'critical' ? 'Crítico' : 'Aviso'}
      </span>
    );
  };

  const getUniqueCompanies = () => {
    const companies = new Set();
    servers.forEach(server => {
      if (server.group_name) {
        companies.add(server.group_name);
      }
    });
    return Array.from(companies).sort();
  };

  const getFilteredIncidents = () => {
    let filtered = [...incidents];
    
    // Filtro por empresa (group_name do servidor)
    if (filterCompany !== 'all') {
      filtered = filtered.filter(incident => {
        const server = servers.find(s => s.id === incident.server_id);
        return server && server.group_name === filterCompany;
      });
    }
    
    // Filtro por tipo (sensor_type)
    if (filterType !== 'all') {
      filtered = filtered.filter(incident => incident.sensor_type === filterType);
    }
    
    // Filtro por criticidade
    if (filterCriticality !== 'all') {
      filtered = filtered.filter(incident => incident.severity === filterCriticality);
    }
    
    return filtered;
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  const companies = getUniqueCompanies();
  const filteredIncidents = getFilteredIncidents();

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🦉 Coruja Monitor</h1>
          <span className="tenant-name">{user.full_name}</span>
          {wsConnected && (
            <span style={{ fontSize: '11px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', display: 'inline-block' }} />
              Tempo real
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button 
            onClick={onEnterNOC} 
            className="noc-mode-button"
            style={{
              padding: '10px 20px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.6)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
            }}
          >
            <span style={{ fontSize: '18px' }}>📺</span>
            Modo NOC
          </button>
          <button 
            onClick={() => onNavigate('advanced-dashboard')} 
            className="noc-mode-button"
            style={{
              padding: '10px 20px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 12px rgba(59, 130, 246, 0.4)'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 6px 16px rgba(59, 130, 246, 0.6)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.4)';
            }}
          >
            <span style={{ fontSize: '18px' }}>📊</span>
            Dashboard Avançado
          </button>
          <button 
            onClick={() => onNavigate('metrics-viewer')} 
            className="noc-mode-button"
            style={{
              padding: '10px 20px',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.4)'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 6px 16px rgba(16, 185, 129, 0.6)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.4)';
            }}
          >
            <span style={{ fontSize: '18px' }}>📈</span>
            Métricas (Grafana)
          </button>
          <button onClick={onLogout} className="logout-button">Sair</button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="status-overview">
          <div className="status-card clickable" style={{ 
            borderLeftColor: '#3b82f6',
            background: 'linear-gradient(135deg, #3b82f615 0%, #2563eb10 100%)',
            borderColor: '#3b82f630'
          }} onClick={() => onNavigate('servers')}>
            <div className="status-icon">🖥️</div>
            <div className="status-info">
              <h3>{overview?.total_servers || 0}</h3>
              <p>Servidores</p>
            </div>
          </div>

          <div className="status-card clickable" style={{ 
            borderLeftColor: '#8b5cf6',
            background: 'linear-gradient(135deg, #8b5cf615 0%, #7c3aed10 100%)',
            borderColor: '#8b5cf630'
          }} onClick={() => onNavigate('sensors')}>
            <div className="status-icon">📊</div>
            <div className="status-info">
              <h3>{overview?.total_sensors || 0}</h3>
              <p>Sensores</p>
            </div>
          </div>

          <div className="status-card clickable" style={{ 
            borderLeftColor: '#f59e0b',
            background: 'linear-gradient(135deg, #f59e0b15 0%, #d97706 10 100%)',
            borderColor: '#f59e0b30'
          }} onClick={() => onNavigate('incidents')}>
            <div className="status-icon">⚠️</div>
            <div className="status-info">
              <h3>{overview?.open_incidents || 0}</h3>
              <p>Incidentes Abertos</p>
            </div>
          </div>

          <div className="status-card clickable" style={{ 
            borderLeftColor: '#ef4444',
            background: 'linear-gradient(135deg, #ef444415 0%, #dc262610 100%)',
            borderColor: '#ef444430'
          }} onClick={() => onNavigate('incidents')}>
            <div className="status-icon">🔥</div>
            <div className="status-info">
              <h3>{overview?.critical_incidents || 0}</h3>
              <p>Críticos</p>
            </div>
          </div>
        </div>

        <div className="health-summary">
          <h2>Status de Saúde</h2>
          <div className="health-grid">
            <div className="health-item clickable" style={{ backgroundColor: '#10b98120' }} onClick={() => onNavigate('sensors', 'ok')}>
              <span className="health-count" style={{ color: '#10b981' }}>
                {healthSummary?.healthy || 0}
              </span>
              <span className="health-label">Saudável</span>
            </div>
            <div className="health-item clickable" style={{ backgroundColor: '#f59e0b20' }} onClick={() => onNavigate('sensors', 'warning')}>
              <span className="health-count" style={{ color: '#f59e0b' }}>
                {healthSummary?.warning || 0}
              </span>
              <span className="health-label">Aviso</span>
            </div>
            <div className="health-item clickable" style={{ backgroundColor: '#ef444420' }} onClick={() => onNavigate('sensors', 'critical')}>
              <span className="health-count" style={{ color: '#ef4444' }}>
                {healthSummary?.critical || 0}
              </span>
              <span className="health-label">Crítico</span>
            </div>
            <div className="health-item clickable" style={{ backgroundColor: '#2196f320' }} onClick={() => onNavigate('sensors', 'acknowledged')}>
              <span className="health-count" style={{ color: '#2196f3' }}>
                {healthSummary?.acknowledged || 0}
              </span>
              <span className="health-label">Verificado pela TI</span>
            </div>
            <div className="health-item clickable" style={{ backgroundColor: '#6b728020' }} onClick={() => onNavigate('sensors', 'unknown')}>
              <span className="health-count" style={{ color: '#6b7280' }}>
                {healthSummary?.unknown || 0}
              </span>
              <span className="health-label">Desconhecido</span>
            </div>
          </div>
        </div>

        <div className="incidents-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2>Incidentes Recentes</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select 
                value={filterCompany} 
                onChange={(e) => setFilterCompany(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb',
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                <option value="all">📁 Todas as Empresas</option>
                {companies.map(company => (
                  <option key={company} value={company}>{company}</option>
                ))}
              </select>
              
              <select 
                value={filterType} 
                onChange={(e) => setFilterType(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb',
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                <option value="all">📊 Todos os Tipos</option>
                <option value="ping">📡 Ping</option>
                <option value="cpu">🖥️ CPU</option>
                <option value="memory">💾 Memória</option>
                <option value="disk">💿 Disco</option>
                <option value="docker">🐳 Docker</option>
                <option value="service">⚙️ Serviço</option>
                <option value="network">🌐 Rede</option>
              </select>
              
              <select 
                value={filterCriticality} 
                onChange={(e) => setFilterCriticality(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb',
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                <option value="all">🎯 Todas as Criticidades</option>
                <option value="critical">🔥 Crítico</option>
                <option value="warning">⚠️ Aviso</option>
              </select>
            </div>
          </div>
          {filteredIncidents.length === 0 ? (
            <div className="no-incidents">
              <p>✅ Nenhum incidente encontrado com os filtros selecionados</p>
            </div>
          ) : (
            <div className="incidents-list">
              {filteredIncidents.map(incident => (
                <div 
                  key={incident.id} 
                  className="incident-card clickable" 
                  data-severity={incident.severity}
                  data-status={incident.status}
                  onClick={(e) => {
                    e.stopPropagation();
                    onNavigate('incidents');
                  }}
                  style={{ cursor: 'pointer' }}
                  role="button"
                  tabIndex={0}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onNavigate('incidents');
                    }
                  }}
                >
                  <div className="incident-header">
                    {getSeverityBadge(incident.severity)}
                    <span className="incident-time">
                      {new Date(incident.created_at).toLocaleString('pt-BR')}
                    </span>
                  </div>
                  <h3>{incident.title}</h3>
                  <p className="incident-description">{incident.description}</p>
                  {incident.root_cause && (
                    <div className="incident-root-cause">
                      <strong>Causa Raiz:</strong> {incident.root_cause}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
