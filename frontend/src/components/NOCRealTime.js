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
    const gs = (s) => {
      if (s === 'ok') return { c: '#22C55E', g: 'linear-gradient(135deg, #065f46, #064e3b)', glow: '0 0 20px rgba(34,197,94,0.3)', l: 'ONLINE', pulse: true };
      if (s === 'warning') return { c: '#F59E0B', g: 'linear-gradient(135deg, #78350f, #713f12)', glow: '0 0 20px rgba(245,158,11,0.3)', l: 'AVISO', pulse: true };
      if (s === 'critical') return { c: '#EF4444', g: 'linear-gradient(135deg, #7f1d1d, #991b1b)', glow: '0 0 20px rgba(239,68,68,0.4)', l: 'OFFLINE', pulse: true };
      return { c: '#6B7280', g: 'linear-gradient(135deg, #1f2937, #111827)', glow: 'none', l: 'AGUARDANDO', pulse: false };
    };

    // SVG gauge component
    const Gauge = ({ value, max, color, label, unit, size = 80 }) => {
      const pct = Math.min(100, Math.max(0, (value / max) * 100));
      const r = (size - 10) / 2;
      const circ = 2 * Math.PI * r;
      const dashOffset = circ - (pct / 100) * circ * 0.75; // 270 degree arc
      return (
        <div style={{ textAlign: 'center', width: size }}>
          <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-225deg)' }}>
            <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1e293b" strokeWidth="6" strokeDasharray={`${circ * 0.75} ${circ * 0.25}`} strokeLinecap="round" />
            <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="6" strokeDasharray={`${circ * 0.75 - dashOffset + circ * 0.75 * (pct/100)} ${circ}`} strokeLinecap="round" style={{ filter: `drop-shadow(0 0 4px ${color})`, transition: 'stroke-dasharray 1s ease' }} />
          </svg>
          <div style={{ marginTop: -size * 0.55, fontSize: size * 0.22, fontWeight: 800, color: '#e2e8f0' }}>{value}{unit}</div>
          <div style={{ fontSize: 9, color: '#64748b', marginTop: size * 0.15 }}>{label}</div>
        </div>
      );
    };

    const dcIcons = { switch: '🔀', router: '📡', firewall: '🔥', access_point: '📶', ap: '📶', gateway: '📡' };
    const dcLabels = { switch: 'Switch', router: 'Router', firewall: 'Firewall', access_point: 'AP', ap: 'AP', gateway: 'Gateway' };

    const totalOnline = dcSites.filter(s => dcMetrics[String(s.id)]?.status === 'ok').length
      + Object.values(dcNetStatuses).filter(s => s === 'ok').length
      + dcEnergy.filter(s => dcMetrics[String(s.id)]?.status === 'ok').length
      + dcHvac.filter(s => dcMetrics[String(s.id)]?.status === 'ok').length;
    const totalAll = dcSites.length + dcNetwork.length + dcEnergy.length + dcHvac.length;

    return (
      <div style={{ padding: '12px 8px', animation: 'fadeIn 0.5s ease' }}>
        {/* Header stats */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, padding: '16px 20px', background: 'linear-gradient(135deg, #0f172a, #1e1b4b)', borderRadius: 16, border: '1px solid #312e81' }}>
          <div>
            <div style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0', letterSpacing: '-0.5px' }}>🏢 DATACENTER</div>
            <div style={{ fontSize: 12, color: '#818cf8', marginTop: 2 }}>Monitoramento em tempo real</div>
          </div>
          <div style={{ display: 'flex', gap: 24 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#22c55e', textShadow: '0 0 20px rgba(34,197,94,0.5)' }}>{totalOnline}</div>
              <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Online</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: '#94a3b8' }}>{totalAll}</div>
              <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Total</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color: totalOnline === totalAll ? '#22c55e' : '#f59e0b', textShadow: totalOnline === totalAll ? '0 0 20px rgba(34,197,94,0.5)' : '0 0 20px rgba(245,158,11,0.5)' }}>{totalAll > 0 ? Math.round(totalOnline/totalAll*100) : 0}%</div>
              <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Uptime</div>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          {/* Sites */}
          <div style={{ background: '#0f172a', borderRadius: 16, padding: 20, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 13, color: '#818cf8', fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#818cf8', boxShadow: '0 0 8px #818cf8' }} />
              SITES MONITORADOS
              <span style={{ marginLeft: 'auto', fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{dcSites.length}</span>
            </div>
            {dcSites.map(s => { const m = dcMetrics[String(s.id)]; const st = gs(m?.status); return (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', marginBottom: 6, background: st.g, borderRadius: 10, border: `1px solid ${st.c}33`, boxShadow: st.glow, transition: 'all 0.3s' }}>
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: st.c, boxShadow: `0 0 8px ${st.c}`, animation: st.pulse ? 'pulse 2s infinite' : 'none', flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>{s.name}</div>
                  <div style={{ fontSize: 10, color: '#94a3b8' }}>{s.config?.http?.url || s.config?.http_url || ''}</div>
                </div>
                <div style={{ fontSize: 14, fontWeight: 800, color: st.c, fontFamily: 'monospace' }}>{m ? Math.round(m.value||0) + 'ms' : '—'}</div>
              </div>
            ); })}
          </div>

          {/* Ativos de Rede */}
          <div style={{ background: '#0f172a', borderRadius: 16, padding: 20, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 13, color: '#f59e0b', fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b', boxShadow: '0 0 8px #f59e0b' }} />
              ATIVOS DE REDE
              <span style={{ marginLeft: 'auto', fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{dcNetwork.length}</span>
            </div>
            {dcNetwork.map(a => { const st = gs(dcNetStatuses[a.id]); const dt = (a.device_type||'').toLowerCase(); return (
              <div key={'n'+a.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', marginBottom: 6, background: st.g, borderRadius: 10, border: `1px solid ${st.c}33`, boxShadow: st.glow, transition: 'all 0.3s' }}>
                <span style={{ fontSize: 18 }}>{dcIcons[dt] || '📦'}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>{a.hostname}</div>
                  <div style={{ fontSize: 10, color: '#94a3b8', fontFamily: 'monospace' }}>{a.ip_address}</div>
                </div>
                <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 6, background: `${st.c}20`, color: st.c, fontWeight: 700 }}>{dcLabels[dt] || dt}</span>
              </div>
            ); })}
          </div>

          {/* Energia */}
          <div style={{ background: '#0f172a', borderRadius: 16, padding: 20, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 13, color: '#22c55e', fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 8px #22c55e' }} />
              ENERGIA
              <span style={{ marginLeft: 'auto', fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{dcEnergy.length}</span>
            </div>
            {dcEnergy.map(s => { const m = dcMetrics[String(s.id)]; const md = m?.metadata||{}; const st = gs(m?.status); const temp = md['Engetron temperatura']?.value; const auto = md['Engetron bateria_autonomia']?.value; const carga = md['Engetron carga_max']?.value; const batV = md['Engetron bateria_tensao']?.value; const fA = md['Engetron tensao_entrada_faseA']?.value; const fB = md['Engetron tensao_entrada_faseB']?.value; const fC = md['Engetron tensao_entrada_faseC']?.value; const oA = md['Engetron tensao_saida_faseA']?.value; const oB = md['Engetron tensao_saida_faseB']?.value; const oC = md['Engetron tensao_saida_faseC']?.value; const quedaFase = [fA,fB,fC].some(v => v !== undefined && v < 100); return (
              <div key={s.id} style={{ background: st.g, borderRadius: 12, padding: 16, border: `1px solid ${quedaFase ? '#ef4444' : st.c}33`, boxShadow: quedaFase ? '0 0 20px rgba(239,68,68,0.4)' : st.glow }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <span style={{ width: 10, height: 10, borderRadius: '50%', background: quedaFase ? '#ef4444' : st.c, boxShadow: `0 0 8px ${quedaFase ? '#ef4444' : st.c}`, animation: 'pulse 2s infinite' }} />
                  <span style={{ fontSize: 14, fontWeight: 700, color: '#e2e8f0' }}>🔋 {s.name}</span>
                  {quedaFase && <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 6, background: '#ef444430', color: '#ef4444', fontWeight: 700, animation: 'pulse 1s infinite' }}>⚠️ QUEDA DE FASE</span>}
                  <span style={{ marginLeft: 'auto', fontSize: 10, padding: '2px 8px', borderRadius: 6, background: `${st.c}20`, color: st.c, fontWeight: 700 }}>{st.l}</span>
                </div>
                {temp !== undefined && (<>
                  <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
                    <Gauge value={temp || 0} max={50} color={temp > 38 ? '#ef4444' : temp > 35 ? '#f59e0b' : '#22c55e'} label="TEMP" unit="°C" />
                    <Gauge value={carga || 0} max={100} color={carga > 90 ? '#ef4444' : carga > 80 ? '#f59e0b' : '#22c55e'} label="CARGA" unit="%" />
                    <Gauge value={auto || 0} max={180} color={auto < 5 ? '#ef4444' : auto < 10 ? '#f59e0b' : '#22c55e'} label="AUTONOMIA" unit="m" />
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0' }}>{batV || '—'}</div>
                      <div style={{ fontSize: 9, color: '#64748b' }}>BATERIA (V)</div>
                    </div>
                  </div>
                  {fA !== undefined && (
                    <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: 12, padding: '8px 0', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 9, color: '#64748b' }}>ENTRADA</div>
                        <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                          {[{l:'A',v:fA},{l:'B',v:fB},{l:'C',v:fC}].map(f => (
                            <div key={f.l} style={{ textAlign: 'center' }}>
                              <div style={{ fontSize: 14, fontWeight: 700, color: f.v < 100 ? '#ef4444' : '#22c55e', textShadow: f.v < 100 ? '0 0 10px rgba(239,68,68,0.5)' : 'none' }}>{f.v}V</div>
                              <div style={{ fontSize: 8, color: '#64748b' }}>Fase {f.l}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                      {oA !== undefined && (
                        <div style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 9, color: '#64748b' }}>SAÍDA</div>
                          <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
                            {[{l:'A',v:oA},{l:'B',v:oB},{l:'C',v:oC}].map(f => (
                              <div key={f.l} style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: 14, fontWeight: 700, color: '#e2e8f0' }}>{f.v}V</div>
                                <div style={{ fontSize: 8, color: '#64748b' }}>Fase {f.l}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </>)}
                {!temp && <div style={{ fontSize: 12, color: '#64748b', textAlign: 'center', padding: 10 }}>Aguardando dados...</div>}
              </div>
            ); })}
          </div>

          {/* Ar-Condicionado */}
          <div style={{ background: '#0f172a', borderRadius: 16, padding: 20, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 13, color: '#06b6d4', fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#06b6d4', boxShadow: '0 0 8px #06b6d4' }} />
              AR-CONDICIONADO
              <span style={{ marginLeft: 'auto', fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{dcHvac.length}</span>
            </div>
            {dcHvac.length === 0 && <div style={{ fontSize: 12, color: '#475569', textAlign: 'center', padding: 20 }}>Nenhum sensor configurado</div>}
            {dcHvac.map(s => { const m = dcMetrics[String(s.id)]; const st = gs(m?.status); return (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', marginBottom: 6, background: st.g, borderRadius: 10, border: `1px solid ${st.c}33`, boxShadow: st.glow }}>
                <span style={{ fontSize: 18 }}>❄️</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>{s.name}</div>
                  <div style={{ fontSize: 10, color: '#94a3b8', fontFamily: 'monospace' }}>{s.config?.ip_address || ''}</div>
                </div>
                <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 6, background: `${st.c}20`, color: st.c, fontWeight: 700 }}>{st.l}</span>
              </div>
            ); })}
          </div>
        </div>
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
