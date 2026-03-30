import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import './Dashboard.css';

const WS_URL = (() => {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}/api/v1/ws/dashboard`;
})();

const IcoServer = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>;
const IcoWifi  = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><circle cx="12" cy="20" r="1"/></svg>;
const IcoWarn  = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>;
const IcoFire  = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>;

function calcHealthScore(healthy, warning, critical, unknown) {
  const total = healthy + warning + critical + unknown;
  if (!total) return 100;
  return Math.round(((healthy * 100 + warning * 60 + unknown * 40) / total));
}

function HealthColor(score) {
  if (score >= 80) return '#22C55E';
  if (score >= 50) return '#F59E0B';
  return '#EF4444';
}

function Dashboard({ user, onLogout, onNavigate, onEnterNOC }) {
  const [overview, setOverview] = useState(null);
  const [healthSummary, setHealthSummary] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [servers, setServers] = useState([]);
  const [filterCompany, setFilterCompany] = useState('all');
  const [filterCriticality, setFilterCriticality] = useState('all');
  const [wsConnected, setWsConnected] = useState(false);
  const [httpSensors, setHttpSensors] = useState([]);
  const [httpMetrics, setHttpMetrics] = useState({});
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

    const connectWS = () => {
      try {
        const t = localStorage.getItem('token');
        const ws = new WebSocket(`${WS_URL}?token=${t}`);
        wsRef.current = ws;
        ws.onopen = () => setWsConnected(true);
        ws.onclose = () => {
          setWsConnected(false);
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

    const interval = setInterval(() => { if (!wsConnected) loadDashboardData(); }, 30000);
    return () => {
      clearInterval(interval);
      clearTimeout(reconnectRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [onLogout]);

  const loadDashboardData = async () => {
    try {
      const [overviewRes, healthRes, incidentsRes, serversRes] = await Promise.allSettled([
        api.get('/dashboard/overview'),
        api.get('/dashboard/health-summary'),
        api.get('/incidents?status=open&limit=10'),
        api.get('/servers')
      ]);

      if (overviewRes.status === 'fulfilled') setOverview(overviewRes.value.data);
      else if (overviewRes.reason?.response?.status === 401) { onLogout(); return; }

      if (healthRes.status === 'fulfilled') setHealthSummary(healthRes.value.data);
      if (incidentsRes.status === 'fulfilled') setIncidents(incidentsRes.value.data);
      if (serversRes.status === 'fulfilled') setServers(serversRes.value.data);

      try {
        const standaloneRes = await api.get('/sensors/standalone');
        const http = standaloneRes.data.filter(s => s.sensor_type === 'http' || s.category === 'network');
        setHttpSensors(http);
        if (http.length > 0) {
          const ids = http.map(s => s.id).join(',');
          const metricsRes = await api.get(`/metrics/latest/batch?sensor_ids=${ids}`);
          setHttpMetrics(metricsRes.data);
        }
      } catch (_) {}
    } catch (error) {
      if (error.response?.status === 401) onLogout();
    } finally {
      setLoading(false);
    }
  };

  const getUniqueCompanies = () => {
    const s = new Set();
    servers.forEach(sv => { if (sv.group_name) s.add(sv.group_name); });
    return Array.from(s).sort();
  };

  const getFilteredIncidents = () => {
    let f = [...incidents];
    if (filterCompany !== 'all') {
      f = f.filter(i => {
        const sv = servers.find(s => s.id === i.server_id);
        return sv && sv.group_name === filterCompany;
      });
    }
    if (filterCriticality !== 'all') f = f.filter(i => i.severity === filterCriticality);
    return f;
  };

  if (loading) {
    return (
      <div className="dash">
        <div className="dash-skeleton" style={{ height: 120 }} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16 }}>
          {[1,2,3,4].map(i => <div key={i} className="dash-skeleton" style={{ height: 100 }} />)}
        </div>
      </div>
    );
  }

  const hs = healthSummary || {};
  const healthy = hs.healthy || 0;
  const warning = hs.warning || 0;
  const critical = hs.critical || 0;
  const unknown = hs.unknown || 0;
  const acknowledged = hs.acknowledged || 0;
  const score = calcHealthScore(healthy, warning, critical, unknown);
  const scoreColor = HealthColor(score);
  const companies = getUniqueCompanies();
  const filteredIncidents = getFilteredIncidents();

  const KPI_CARDS = [
    {
      label: 'Servidores',
      value: overview?.total_servers || 0,
      icon: <IcoServer />,
      color: '#6366F1',
      bg: 'rgba(99,102,241,0.12)',
      page: 'servers',
    },
    {
      label: 'Sensores',
      value: overview?.total_sensors || 0,
      icon: <IcoWifi />,
      color: '#8B5CF6',
      bg: 'rgba(139,92,246,0.12)',
      page: 'sensors',
    },
    {
      label: 'Incidentes Abertos',
      value: overview?.open_incidents || 0,
      icon: <IcoWarn />,
      color: '#F59E0B',
      bg: 'rgba(245,158,11,0.12)',
      page: 'incidents',
    },
    {
      label: 'Críticos',
      value: overview?.critical_incidents || 0,
      icon: <IcoFire />,
      color: '#EF4444',
      bg: 'rgba(239,68,68,0.12)',
      page: 'incidents',
    },
  ];

  return (
    <div className="dash">
      {/* ── Health Banner ── */}
      <div className="dash-health-banner">
        <div className="dash-health-score">
          <span className="dash-health-number" style={{ color: scoreColor }}>{score}</span>
          <span className="dash-health-label">Health Score</span>
          <span className="dash-health-trend" style={{ color: scoreColor }}>
            {score >= 80 ? '↑ Saudável' : score >= 50 ? '→ Atenção' : '↓ Crítico'}
          </span>
        </div>

        <div className="dash-health-divider" />

        <div className="dash-health-stats">
          <div className="dash-health-stat">
            <span className="dash-health-stat-value" style={{ color: '#22C55E' }}>{healthy}</span>
            <span className="dash-health-stat-label">Saudáveis</span>
          </div>
          <div className="dash-health-stat">
            <span className="dash-health-stat-value" style={{ color: '#F59E0B' }}>{warning}</span>
            <span className="dash-health-stat-label">Avisos</span>
          </div>
          <div className="dash-health-stat">
            <span className="dash-health-stat-value" style={{ color: '#EF4444' }}>{critical}</span>
            <span className="dash-health-stat-label">Críticos</span>
          </div>
          <div className="dash-health-stat">
            <span className="dash-health-stat-value" style={{ color: '#60A5FA' }}>{acknowledged}</span>
            <span className="dash-health-stat-label">Verificados</span>
          </div>
          <div className="dash-health-stat">
            <span className="dash-health-stat-value" style={{ color: '#6B7280' }}>{unknown}</span>
            <span className="dash-health-stat-label">Desconhecidos</span>
          </div>
        </div>

        <div className="dash-health-actions">
          {wsConnected && (
            <span style={{ fontSize: 11, color: '#22C55E', display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22C55E', boxShadow: '0 0 6px #22C55E' }} />
              Tempo real
            </span>
          )}
          <button className="ds-btn ds-btn--ghost" onClick={onEnterNOC} style={{ fontSize: 12 }}>
            Modo NOC
          </button>
        </div>
      </div>

      {/* ── KPI Cards ── */}
      <div className="dash-kpi-grid">
        {KPI_CARDS.map(card => (
          <div
            key={card.label}
            className="dash-kpi-card"
            style={{ '--kpi-color': card.color, '--kpi-bg': card.bg }}
            onClick={() => onNavigate(card.page)}
            role="button"
            tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && onNavigate(card.page)}
            aria-label={`${card.label}: ${card.value}`}
          >
            <div className="dash-kpi-header">
              <div className="dash-kpi-icon">{card.icon}</div>
            </div>
            <div className="dash-kpi-value">{card.value}</div>
            <div className="dash-kpi-label">{card.label}</div>
          </div>
        ))}
      </div>

      {/* ── HTTP Sites ── */}
      {httpSensors.length > 0 && (
        <div className="dash-section">
          <div className="dash-section-header">
            <span className="dash-section-title">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              Sites Monitorados
            </span>
            <button className="dash-section-link" onClick={() => onNavigate('sensor-library')}>Ver todos →</button>
          </div>
          <div className="dash-sites-grid">
            {httpSensors.map(sensor => {
              const metric = httpMetrics[String(sensor.id)];
              const isOnline = metric?.status === 'ok';
              const hasData = !!metric;
              const color = !hasData ? '#6B7280' : isOnline ? '#22C55E' : '#EF4444';
              const label = !hasData ? 'Aguardando' : isOnline ? 'ONLINE' : 'OFFLINE';
              const url = sensor.config?.http_url || sensor.http_url || '';
              const responseMs = metric?.value ? Math.round(metric.value) : null;
              return (
                <div key={sensor.id} className="dash-site-card" style={{ '--site-color': color }}>
                  <div className="dash-site-status">
                    <span className="dash-site-badge">
                      <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'white' }} />
                      {label}
                    </span>
                    {responseMs !== null && <span className="dash-site-ms">{responseMs}ms</span>}
                  </div>
                  <div className="dash-site-name">{sensor.name}</div>
                  {url && <div className="dash-site-url">{url}</div>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Incidents ── */}
      <div className="dash-section">
        <div className="dash-section-header">
          <span className="dash-section-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            Incidentes Recentes
          </span>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <select className="dash-filter-select" value={filterCompany} onChange={e => setFilterCompany(e.target.value)}>
              <option value="all">Todas as empresas</option>
              {companies.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <select className="dash-filter-select" value={filterCriticality} onChange={e => setFilterCriticality(e.target.value)}>
              <option value="all">Todas as criticidades</option>
              <option value="critical">Crítico</option>
              <option value="warning">Aviso</option>
            </select>
            <button className="dash-section-link" onClick={() => onNavigate('incidents')}>Ver todos →</button>
          </div>
        </div>

        {filteredIncidents.length === 0 ? (
          <div className="dash-empty">Nenhum incidente encontrado</div>
        ) : (
          <div className="dash-incident-list">
            {filteredIncidents.slice(0, 8).map(incident => {
              const sevColor = incident.severity === 'critical' ? '#EF4444' : '#F59E0B';
              return (
                <div
                  key={incident.id}
                  className="dash-incident-item"
                  onClick={() => onNavigate('incidents')}
                  role="button"
                  tabIndex={0}
                  onKeyDown={e => e.key === 'Enter' && onNavigate('incidents')}
                >
                  <span className="dash-incident-sev" style={{ background: sevColor, boxShadow: `0 0 6px ${sevColor}` }} />
                  <div className="dash-incident-body">
                    <div className="dash-incident-title">{incident.title}</div>
                    <div className="dash-incident-meta">
                      <span>{new Date(incident.created_at).toLocaleString('pt-BR')}</span>
                      {incident.root_cause && <span>· {incident.root_cause}</span>}
                    </div>
                  </div>
                  <span
                    className="dash-incident-badge"
                    style={{ background: sevColor + '20', color: sevColor }}
                  >
                    {incident.severity === 'critical' ? 'Crítico' : 'Aviso'}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
