import React, { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';
import './NOCRealTime.css';

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 2000;

function NOCRealTime({ onExit }) {
  const [data, setData] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [currentView, setCurrentView] = useState('overview');
  const [autoRotate, setAutoRotate] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [dcSites, setDcSites] = useState([]);
  const [dcNetwork, setDcNetwork] = useState([]);
  const [dcEnergy, setDcEnergy] = useState([]);
  const [dcHvac, setDcHvac] = useState([]);
  const [dcMetrics, setDcMetrics] = useState({});
  const [dcNetStatuses, setDcNetStatuses] = useState({});
  const retryCountRef = useRef(0);

  // Sons de alerta
  const playAlert = useCallback((severity) => {
    if (!soundEnabled) return;
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      oscillator.frequency.value = severity === 'critical' ? 800 : 600;
      gainNode.gain.value = severity === 'critical' ? 0.3 : 0.2;
      oscillator.start();
      setTimeout(() => oscillator.stop(), 200);
    } catch (_) {}
  }, [soundEnabled]);

  // Carregar dados com retry
  const loadDashboard = useCallback(async () => {
    try {
      const response = await api.get('/noc-realtime/realtime/dashboard', {
        timeout: 30000,
      });

      if (data && response.data.incidents) {
        const newCritical = response.data.incidents.filter(inc =>
          inc.severity === 'critical' &&
          !data.incidents?.some(old => old.id === inc.id)
        );
        if (newCritical.length > 0) playAlert('critical');
      }

      setData(response.data);
      setLastUpdate(new Date());
      setConnectionStatus('connected');
      setLoadError(null);
      retryCountRef.current = 0;
    } catch (error) {
      const isTimeout = error.code === 'ECONNABORTED' || error.message?.includes('timeout');
      console.error('Erro ao carregar dashboard NOC:', error);

      if (retryCountRef.current < MAX_RETRIES) {
        retryCountRef.current += 1;
        setConnectionStatus('connecting');
        setTimeout(loadDashboard, RETRY_DELAY_MS);
      } else {
        setConnectionStatus('error');
        setLoadError(isTimeout ? 'Timeout de conexão' : 'Falha ao carregar dados');
      }
    }
  }, [data, playAlert]);

  // Atualização automática
  useEffect(() => {
    loadDashboard();
    loadDatacenterData();
    const interval = setInterval(loadDashboard, 3000);
    const dcInterval = setInterval(loadDatacenterData, 30000);
    return () => { clearInterval(interval); clearInterval(dcInterval); };
  }, [loadDashboard]);

  const loadDatacenterData = async () => {
    try {
      const [standaloneRes, serversRes] = await Promise.all([
        api.get('/sensors/standalone'),
        api.get('/servers'),
      ]);
      const all = standaloneRes.data;
      setDcSites(all.filter(s => s.sensor_type === 'http' || s.category === 'network'));
      setDcEnergy(all.filter(s => (s.name || '').toLowerCase().match(/nobreak|ups|gerador|energia|battery|power|engetron/)));
      setDcHvac(all.filter(s => (s.name || '').toLowerCase().match(/ar.condicionado|hvac|temperatura|cooling|climate|chiller|conflex/)));
      const netTypes = ['switch', 'router', 'firewall', 'access_point', 'ap', 'ups', 'storage', 'gateway'];
      const assets = serversRes.data.filter(s => netTypes.includes((s.device_type || '').toLowerCase()));
      setDcNetwork(assets);
      if (all.length > 0) {
        const ids = all.map(s => s.id).join(',');
        const mr = await api.get(`/metrics/latest/batch?sensor_ids=${ids}`);
        setDcMetrics(mr.data);
      }
      if (assets.length > 0) {
        try { const sr = await api.get('/dashboard/network-assets-status?ids=' + assets.map(a => a.id).join(',')); setDcNetStatuses(sr.data); } catch (_) {}
      }
    } catch (_) {}
  };

  // Rotação automática de views
  useEffect(() => {
    if (autoRotate) {
      const views = ['overview', 'servers', 'incidents', 'metrics', 'datacenter'];
      const rotateInterval = setInterval(() => {
        setCurrentView(prev => {
          const currentIndex = views.indexOf(prev);
          return views[(currentIndex + 1) % views.length];
        });
      }, 20000); // Rotaciona a cada 20s
      return () => clearInterval(rotateInterval);
    }
  }, [autoRotate]);

  if (!data) {
    return (
      <div className="noc-realtime loading">
        {loadError ? (
          <>
            <div className="loading-text" style={{ color: '#ff4444' }}>⚠️ {loadError}</div>
            <button
              style={{ marginTop: 16, padding: '8px 20px', cursor: 'pointer' }}
              onClick={() => { retryCountRef.current = 0; setLoadError(null); setConnectionStatus('connecting'); loadDashboard(); }}
            >
              Tentar novamente
            </button>
          </>
        ) : (
          <>
            <div className="loading-spinner"></div>
            <div className="loading-text">Carregando NOC em Tempo Real...</div>
          </>
        )}
      </div>
    );
  }

  const renderOverview = () => (
    <div className="noc-view overview-view">
      <div className="noc-title">
        <h1>🌐 VISÃO GERAL DO SISTEMA</h1>
        <div className="noc-subtitle">Monitoramento em Tempo Real</div>
      </div>

      {/* KPIs Principais */}
      <div className="kpi-grid-main">
        <div className="kpi-card-main ok">
          <div className="kpi-icon">✅</div>
          <div className="kpi-value">{data.summary.servers_ok}</div>
          <div className="kpi-label">SERVIDORES OK</div>
          <div className="kpi-percentage">
            {((data.summary.servers_ok / data.summary.total_servers) * 100).toFixed(1)}%
          </div>
        </div>

        <div className="kpi-card-main warning">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-value">{data.summary.servers_warning}</div>
          <div className="kpi-label">EM AVISO</div>
          <div className="kpi-percentage">
            {((data.summary.servers_warning / data.summary.total_servers) * 100).toFixed(1)}%
          </div>
        </div>

        <div className="kpi-card-main critical">
          <div className="kpi-icon">🔥</div>
          <div className="kpi-value">{data.summary.servers_critical}</div>
          <div className="kpi-label">CRÍTICOS</div>
          <div className="kpi-percentage">
            {((data.summary.servers_critical / data.summary.total_servers) * 100).toFixed(1)}%
          </div>
        </div>

        <div className="kpi-card-main offline">
          <div className="kpi-icon">⚫</div>
          <div className="kpi-value">{data.summary.servers_offline}</div>
          <div className="kpi-label">OFFLINE</div>
          <div className="kpi-percentage">
            {((data.summary.servers_offline / data.summary.total_servers) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Estatísticas de Incidentes */}
      <div className="incidents-summary">
        <div className="summary-card">
          <div className="summary-icon">🚨</div>
          <div className="summary-content">
            <div className="summary-value">{data.summary.total_incidents}</div>
            <div className="summary-label">Incidentes Ativos</div>
          </div>
        </div>

        <div className="summary-card critical">
          <div className="summary-icon">🔥</div>
          <div className="summary-content">
            <div className="summary-value">{data.summary.critical_incidents}</div>
            <div className="summary-label">Críticos</div>
          </div>
        </div>

        <div className="summary-card warning">
          <div className="summary-icon">⚠️</div>
          <div className="summary-content">
            <div className="summary-value">{data.summary.warning_incidents}</div>
            <div className="summary-label">Avisos</div>
          </div>
        </div>

        <div className="summary-card info">
          <div className="summary-icon">📊</div>
          <div className="summary-content">
            <div className="summary-value">{data.kpis.sla}%</div>
            <div className="summary-label">SLA (30d)</div>
          </div>
        </div>
      </div>

      {/* Empresas (se admin) */}
      {data.companies && data.companies.length > 0 && (
        <div className="companies-section">
          <h2>📊 Status por Empresa</h2>
          <div className="companies-grid-modern">
            {data.companies.map(company => (
              <div key={company.id} className={`company-card-modern ${company.status}`}>
                <div className="company-header">
                  <div className="company-name">{company.name}</div>
                  <div className={`company-status-badge ${company.status}`}>
                    {company.status === 'ok' && '✅'}
                    {company.status === 'warning' && '⚠️'}
                    {company.status === 'critical' && '🔥'}
                  </div>
                </div>
                <div className="company-stats-grid">
                  <div className="stat-item">
                    <div className="stat-value">{company.servers}</div>
                    <div className="stat-label">Servidores</div>
                  </div>
                  <div className="stat-item critical">
                    <div className="stat-value">{company.critical_incidents}</div>
                    <div className="stat-label">Críticos</div>
                  </div>
                  <div className="stat-item warning">
                    <div className="stat-value">{company.warning_incidents}</div>
                    <div className="stat-label">Avisos</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderServers = () => (
    <div className="noc-view servers-view">
      <div className="noc-title">
        <h1>🖥️ MAPA DE SERVIDORES</h1>
        <div className="noc-subtitle">{data.servers.length} Servidores Monitorados</div>
      </div>

      <div className="servers-grid-modern">
        {data.servers.map(server => (
          <div key={server.id} className={`server-card-modern ${server.status}`}>
            <div className="server-header">
              <div className="server-icon">
                {server.status === 'ok' && '✅'}
                {server.status === 'warning' && '⚠️'}
                {server.status === 'critical' && '🔥'}
                {server.status === 'offline' && '⚫'}
              </div>
              <div className="server-info">
                <div className="server-hostname">{server.hostname}</div>
                <div className="server-ip">{server.ip_address}</div>
              </div>
            </div>

            <div className="server-metrics">
              <div className="metric-row">
                <span className="metric-label">Disponibilidade:</span>
                <span className="metric-value">{server.availability}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Sensores:</span>
                <span className="metric-value">{server.total_sensors}</span>
              </div>
              {server.critical_incidents > 0 && (
                <div className="metric-row critical">
                  <span className="metric-label">Críticos:</span>
                  <span className="metric-value">{server.critical_incidents}</span>
                </div>
              )}
              {server.warning_incidents > 0 && (
                <div className="metric-row warning">
                  <span className="metric-label">Avisos:</span>
                  <span className="metric-value">{server.warning_incidents}</span>
                </div>
              )}
            </div>

            {server.last_update && (
              <div className="server-footer">
                <span className="last-update">
                  Atualizado: {new Date(server.last_update).toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderIncidents = () => (
    <div className="noc-view incidents-view">
      <div className="noc-title">
        <h1>🚨 INCIDENTES ATIVOS</h1>
        <div className="noc-subtitle">{data.incidents.length} Incidentes em Aberto</div>
      </div>

      <div className="incidents-list-modern">
        {data.incidents.length === 0 ? (
          <div className="no-incidents">
            <div className="no-incidents-icon">✅</div>
            <div className="no-incidents-text">Nenhum incidente ativo</div>
            <div className="no-incidents-subtext">Sistema operando normalmente</div>
          </div>
        ) : (
          data.incidents.map(incident => (
            <div key={incident.id} className={`incident-card-modern ${incident.severity}`}>
              <div className="incident-header">
                <div className="incident-severity-badge">
                  {incident.severity === 'critical' ? '🔥 CRÍTICO' : '⚠️ AVISO'}
                </div>
                <div className="incident-duration">{incident.duration_text}</div>
              </div>

              <div className="incident-body">
                <div className="incident-server">
                  <span className="label">Servidor:</span>
                  <span className="value">{incident.server_name}</span>
                </div>
                <div className="incident-sensor">
                  <span className="label">Sensor:</span>
                  <span className="value">{incident.sensor_name}</span>
                </div>
                <div className="incident-description">{incident.description}</div>
              </div>

              <div className="incident-footer">
                <div className="incident-time">
                  {new Date(incident.created_at).toLocaleString()}
                </div>
                {incident.status === 'acknowledged' && (
                  <div className="incident-status-badge acknowledged">
                    ✓ Reconhecido
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  const renderMetrics = () => (
    <div className="noc-view metrics-view">
      <div className="noc-title">
        <h1>📊 MÉTRICAS CRÍTICAS</h1>
        <div className="noc-subtitle">Sensores em Estado de Alerta</div>
      </div>

      {/* KPIs Operacionais */}
      <div className="kpis-operational">
        <div className="kpi-op-card">
          <div className="kpi-op-label">MTTR</div>
          <div className="kpi-op-value">{data.kpis.mttr} min</div>
          <div className="kpi-op-desc">Tempo Médio de Resolução</div>
        </div>

        <div className="kpi-op-card">
          <div className="kpi-op-label">SLA</div>
          <div className="kpi-op-value">{data.kpis.sla}%</div>
          <div className="kpi-op-desc">Últimos 30 Dias</div>
        </div>

        <div className="kpi-op-card">
          <div className="kpi-op-label">INCIDENTES</div>
          <div className="kpi-op-value">{data.kpis.incidents_24h}</div>
          <div className="kpi-op-desc">Últimas 24 Horas</div>
        </div>

        <div className="kpi-op-card">
          <div className="kpi-op-label">RESOLVIDOS</div>
          <div className="kpi-op-value">{data.kpis.resolved_30d}</div>
          <div className="kpi-op-desc">Últimos 30 Dias</div>
        </div>
      </div>

      {/* Sensores Críticos */}
      <div className="critical-sensors-section">
        <h2>⚠️ Sensores em Alerta</h2>
        {data.critical_sensors.length === 0 ? (
          <div className="no-critical-sensors">
            <div className="no-critical-icon">✅</div>
            <div className="no-critical-text">Todos os sensores operando normalmente</div>
          </div>
        ) : (
          <div className="critical-sensors-grid">
            {data.critical_sensors.map((sensor, index) => (
              <div key={index} className={`critical-sensor-card ${sensor.status}`}>
                <div className="sensor-header">
                  <div className="sensor-server">{sensor.server_name}</div>
                  <div className={`sensor-status-badge ${sensor.status}`}>
                    {sensor.status === 'critical' ? '🔥' : '⚠️'}
                  </div>
                </div>
                <div className="sensor-name">{sensor.sensor_name}</div>
                <div className="sensor-value-large">
                  {sensor.value.toFixed(1)} {sensor.unit}
                </div>
                <div className="sensor-thresholds">
                  <span className="threshold warning">
                    ⚠️ {sensor.threshold_warning}
                  </span>
                  <span className="threshold critical">
                    🔥 {sensor.threshold_critical}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderDatacenter = () => {
    const getStatus = (s) => {
      const c = s === 'ok' ? '#22C55E' : s === 'warning' ? '#F59E0B' : s === 'critical' ? '#EF4444' : '#6B7280';
      const l = s === 'ok' ? 'ONLINE' : s === 'warning' ? 'AVISO' : s === 'critical' ? 'OFFLINE' : 'AGUARDANDO';
      return { c, l };
    };
    const card = (key, name, status, icon, sub, extra) => {
      const { c, l } = getStatus(status);
      return (
        <div key={key} style={{ background: `${c}10`, border: `1px solid ${c}33`, borderLeft: `4px solid ${c}`, borderRadius: 12, padding: '14px 18px', minWidth: 170 }}>
          <div style={{ marginBottom: 6 }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 8px', borderRadius: 20, fontSize: 10, fontWeight: 700, background: c, color: '#fff' }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#fff' }} />{l}
            </span>
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#e2e8f0' }}>{icon} {name}</div>
          {sub && <div style={{ fontSize: 11, color: '#94a3b8', fontFamily: 'monospace', marginTop: 2 }}>{sub}</div>}
          {extra && <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>{extra}</div>}
        </div>
      );
    };
    const icons = { switch: '🔀', router: '📡', firewall: '🔥', access_point: '📶', ap: '📶', gateway: '📡' };
    const labels = { switch: 'Switch', router: 'Router', firewall: 'Firewall', access_point: 'AP', ap: 'AP', gateway: 'Gateway' };
    return (
      <div style={{ padding: '8px 0' }}>
        {dcSites.length > 0 && (<>
          <h3 style={{ fontSize: 14, color: '#64748b', marginBottom: 12 }}>🌐 Sites Monitorados ({dcSites.length})</h3>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
            {dcSites.map(s => { const m = dcMetrics[String(s.id)]; return card(s.id, s.name, m?.status || 'unknown', '🌐', s.config?.http?.url || '', m ? `⏱️ ${Math.round(m.value||0)}ms` : null); })}
          </div>
        </>)}
        {dcNetwork.length > 0 && (<>
          <h3 style={{ fontSize: 14, color: '#64748b', marginBottom: 12 }}>🔀 Ativos de Rede ({dcNetwork.length})</h3>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
            {dcNetwork.map(a => { const dt = (a.device_type||'').toLowerCase(); return card('n'+a.id, a.hostname, dcNetStatuses[a.id]||'unknown', icons[dt]||'📦', a.ip_address, labels[dt]||dt); })}
          </div>
        </>)}
        {dcEnergy.length > 0 && (<>
          <h3 style={{ fontSize: 14, color: '#64748b', marginBottom: 12 }}>⚡ Energia ({dcEnergy.length})</h3>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
            {dcEnergy.map(s => { const m = dcMetrics[String(s.id)]; const md = m?.metadata||{}; const t = md['Engetron temperatura']?.value; const a = md['Engetron bateria_autonomia']?.value; return card(s.id, s.name, m?.status||'unknown', '🔋', s.config?.ip_address||'', t ? `🌡️ ${t}°C · 🔋 ${a||'?'} min` : null); })}
          </div>
        </>)}
        {dcHvac.length > 0 && (<>
          <h3 style={{ fontSize: 14, color: '#64748b', marginBottom: 12 }}>❄️ Ar-Condicionado ({dcHvac.length})</h3>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
            {dcHvac.map(s => { const m = dcMetrics[String(s.id)]; return card(s.id, s.name, m?.status||'unknown', '❄️', s.config?.ip_address||'', m ? `📊 ${m.value?.toFixed(1)} ${m.unit}` : null); })}
          </div>
        </>)}
      </div>
    );
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'overview': return renderOverview();
      case 'servers': return renderServers();
      case 'incidents': return renderIncidents();
      case 'metrics': return renderMetrics();
      case 'datacenter': return renderDatacenter();
      default: return renderOverview();
    }
  };

  return (
    <div className="noc-realtime">
      {/* Header */}
      <div className="noc-header-modern">
        <div className="noc-logo-modern">
          <span className="logo-icon">🦉</span>
          <span className="logo-text">CORUJA MONITOR</span>
          <span className="logo-subtitle">NOC</span>
        </div>

        <div className="noc-status-bar">
          <div className={`connection-status ${connectionStatus}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {connectionStatus === 'connected' && 'Conectado'}
              {connectionStatus === 'connecting' && 'Conectando...'}
              {connectionStatus === 'error' && 'Erro de Conexão'}
            </span>
          </div>
          <div className="last-update-time">
            Atualizado: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>

        <div className="noc-controls-modern">
          <button 
            className={`noc-btn-modern ${soundEnabled ? 'active' : ''}`}
            onClick={() => setSoundEnabled(!soundEnabled)}
            title="Alertas Sonoros"
          >
            {soundEnabled ? '🔊' : '🔇'}
          </button>

          <button 
            className={`noc-btn-modern ${autoRotate ? 'active' : ''}`}
            onClick={() => setAutoRotate(!autoRotate)}
            title="Rotação Automática"
          >
            {autoRotate ? '⏸️' : '▶️'}
          </button>

          <button 
            className="noc-btn-modern exit"
            onClick={onExit}
            title="Sair do Modo NOC"
          >
            ❌
          </button>
        </div>
      </div>

      {/* Navigation */}
      <div className="noc-navigation">
        <button 
          className={`nav-btn ${currentView === 'overview' ? 'active' : ''}`}
          onClick={() => { setCurrentView('overview'); setAutoRotate(false); }}
        >
          <span className="nav-icon">🌐</span>
          <span className="nav-label">Visão Geral</span>
        </button>
        <button 
          className={`nav-btn ${currentView === 'servers' ? 'active' : ''}`}
          onClick={() => { setCurrentView('servers'); setAutoRotate(false); }}
        >
          <span className="nav-icon">🖥️</span>
          <span className="nav-label">Servidores</span>
        </button>
        <button 
          className={`nav-btn ${currentView === 'incidents' ? 'active' : ''}`}
          onClick={() => { setCurrentView('incidents'); setAutoRotate(false); }}
        >
          <span className="nav-icon">🚨</span>
          <span className="nav-label">Incidentes</span>
          {data.summary.total_incidents > 0 && (
            <span className="nav-badge">{data.summary.total_incidents}</span>
          )}
        </button>
        <button 
          className={`nav-btn ${currentView === 'metrics' ? 'active' : ''}`}
          onClick={() => { setCurrentView('metrics'); setAutoRotate(false); }}
        >
          <span className="nav-icon">📊</span>
          <span className="nav-label">Métricas</span>
        </button>
        <button 
          className={`nav-btn ${currentView === 'datacenter' ? 'active' : ''}`}
          onClick={() => { setCurrentView('datacenter'); setAutoRotate(false); }}
        >
          <span className="nav-icon">🏢</span>
          <span className="nav-label">Datacenter</span>
        </button>
      </div>

      {/* Content */}
      <div className="noc-content-modern">
        {renderCurrentView()}
      </div>

      {/* Footer */}
      <div className="noc-footer-modern">
        <div className="footer-stats">
          <span className="stat">
            <span className="stat-icon">🖥️</span>
            {data.summary.total_servers} Servidores
          </span>
          <span className="stat">
            <span className="stat-icon">🚨</span>
            {data.summary.total_incidents} Incidentes
          </span>
          <span className="stat">
            <span className="stat-icon">⚡</span>
            Atualização: 3s
          </span>
        </div>
      </div>
    </div>
  );
}

export default NOCRealTime;
