import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
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
  const [allStandaloneSensors, setAllStandaloneSensors] = useState([]);
  const [networkAssets, setNetworkAssets] = useState([]);
  const [networkAssetStatuses, setNetworkAssetStatuses] = useState({});
  const [siteModalSensor, setSiteModalSensor] = useState(null);
  const [siteHistory, setSiteHistory] = useState([]);
  const [siteHistoryLoading, setSiteHistoryLoading] = useState(false);
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
      if (serversRes.status === 'fulfilled') {
        setServers(serversRes.value.data);
        // Filtrar ativos de rede (switch, router, firewall, access_point, ap, ups)
        const netTypes = ['switch', 'router', 'firewall', 'access_point', 'ap', 'ups', 'storage'];
        const assets = serversRes.value.data.filter(s => netTypes.includes((s.device_type || '').toLowerCase()));
        setNetworkAssets(assets);
        // Buscar status dos ativos de rede
        if (assets.length > 0) {
          try {
            const statusRes = await api.get('/dashboard/network-assets-status?ids=' + assets.map(a => a.id).join(','));
            setNetworkAssetStatuses(statusRes.data);
          } catch (_) {
            // Fallback: marcar como unknown
            const fallback = {};
            assets.forEach(a => { fallback[a.id] = 'unknown'; });
            setNetworkAssetStatuses(fallback);
          }
        }
      }

      try {
        const standaloneRes = await api.get('/sensors/standalone');
        const allStandalone = standaloneRes.data;
        setAllStandaloneSensors(allStandalone);
        const http = allStandalone.filter(s => s.sensor_type === 'http' || s.category === 'network');
        setHttpSensors(http);
        if (allStandalone.length > 0) {
          const ids = allStandalone.map(s => s.id).join(',');
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

  const openSiteModal = async (sensor) => {
    setSiteModalSensor(sensor);
    setSiteHistory([]);
    setSiteHistoryLoading(true);
    try {
      const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
      const res = await api.get(`/metrics/?sensor_id=${sensor.id}&start_time=${since}&limit=2000`);
      setSiteHistory(res.data || []);
    } catch (e) {
      console.error('Erro ao carregar histórico:', e);
    } finally {
      setSiteHistoryLoading(false);
    }
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
                <div key={sensor.id} className="dash-site-card" style={{ '--site-color': color, cursor: 'pointer' }} onClick={() => openSiteModal(sensor)}>
                  <div className="dash-site-status">
                    <span className="dash-site-badge">
                      <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'white' }} />
                      {label}
                    </span>
                    {responseMs !== null && <span className="dash-site-ms">{responseMs}ms</span>}
                  </div>
                  <div className="dash-site-name">{sensor.name}</div>
                  {url && <div className="dash-site-url">{url}</div>}
                  <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', marginTop: 4 }}>Clique para ver histórico</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Ativos de Rede ── */}
      {networkAssets.length > 0 && (
        <div className="dash-section">
          <div className="dash-section-header">
            <span className="dash-section-title">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3h12l3 6H3zm0 12h12l3 6H3zM3 9h18M3 15h18"/></svg>
              Ativos de Rede
            </span>
            <button className="dash-section-link" onClick={() => onNavigate('sensor-library')}>Ver todos →</button>
          </div>
          <div className="dash-sites-grid">
            {networkAssets.map(asset => {
              const status = networkAssetStatuses[asset.id] || 'unknown';
              const color = status === 'ok' ? '#22C55E' : status === 'warning' ? '#F59E0B' : status === 'critical' ? '#EF4444' : '#6B7280';
              const label = status === 'ok' ? 'ONLINE' : status === 'warning' ? 'AVISO' : status === 'critical' ? 'CRÍTICO' : 'Aguardando';
              const deviceIcons = { switch: '🔀', router: '📡', firewall: '🔥', access_point: '📶', ap: '📶', ups: '🔋', storage: '🧠' };
              const deviceLabels = { switch: 'Switch', router: 'Roteador', firewall: 'Firewall', access_point: 'Access Point', ap: 'Access Point', ups: 'Nobreak', storage: 'Storage' };
              const dt = (asset.device_type || 'other').toLowerCase();
              return (
                <div key={asset.id} className="dash-site-card" style={{ '--site-color': color, cursor: 'pointer' }} onClick={() => onNavigate('sensor-library')}>
                  <div className="dash-site-status">
                    <span className="dash-site-badge">
                      <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'white' }} />
                      {label}
                    </span>
                    <span style={{ fontSize: 11, color: '#9CA3AF' }}>{deviceLabels[dt] || dt}</span>
                  </div>
                  <div className="dash-site-name">{deviceIcons[dt] || '📦'} {asset.hostname}</div>
                  {asset.ip_address && <div className="dash-site-url">{asset.ip_address}</div>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Datacenter (Energia + Ar-Condicionado) ── */}
      {(() => {
        const energySensors = (allStandaloneSensors || []).filter(s => (s.name || '').toLowerCase().match(/nobreak|ups|gerador|energia|battery|power|engetron/));
        const hvacSensors = (allStandaloneSensors || []).filter(s => (s.name || '').toLowerCase().match(/ar.condicionado|hvac|temperatura|cooling|climate|chiller|conflex/));
        const storageSensors = (allStandaloneSensors || []).filter(s => (s.name || '').toLowerCase().match(/storage|equallogic|san|iscsi/));
        const printerSensors = (allStandaloneSensors || []).filter(s => (s.name || '').toLowerCase().match(/impressora|printer|samsung|hp laserjet|canon/));
        if (energySensors.length === 0 && hvacSensors.length === 0 && storageSensors.length === 0 && printerSensors.length === 0) return null;
        return (
          <div className="dash-section">
            <div className="dash-section-header">
              <span className="dash-section-title">
                🏢 Datacenter
              </span>
              <button className="dash-section-link" onClick={() => onNavigate('sensor-library')}>Ver todos →</button>
            </div>
            <div className="dash-sites-grid">
              {energySensors.map(s => {
                const m = httpMetrics[String(s.id)];
                const status = m?.status || 'unknown';
                const color = status === 'ok' ? '#22C55E' : status === 'warning' ? '#F59E0B' : status === 'critical' ? '#EF4444' : '#6B7280';
                const label = status === 'ok' ? 'ONLINE' : status === 'warning' ? 'AVISO' : status === 'critical' ? 'OFFLINE' : 'Aguardando';
                return (
                  <div key={s.id} className="dash-site-card" style={{ '--site-color': color, cursor: 'pointer' }} onClick={() => onNavigate('sensor-library')}>
                    <div className="dash-site-status">
                      <span className="dash-site-badge"><span style={{ width: 5, height: 5, borderRadius: '50%', background: 'white' }} />{label}</span>
                      <span style={{ fontSize: 11, color: '#94a3b8' }}>⚡ Energia</span>
                    </div>
                    <div className="dash-site-name">🔋 {s.name}</div>
                    {m?.metadata?.['Engetron temperatura'] && (
                      <div className="dash-site-url">🌡️ {m.metadata['Engetron temperatura'].value}°C · 🔋 {m.metadata['Engetron bateria_autonomia']?.value || '?'} min</div>
                    )}
                    {!m?.metadata?.['Engetron temperatura'] && m && (
                      <div className="dash-site-url">📊 {m.value?.toFixed(1)} {m.unit}</div>
                    )}
                  </div>
                );
              })}
              {hvacSensors.map(s => {
                const m = httpMetrics[String(s.id)];
                const status = m?.status || 'unknown';
                const color = status === 'ok' ? '#22C55E' : status === 'warning' ? '#F59E0B' : status === 'critical' ? '#EF4444' : '#6B7280';
                const label = status === 'ok' ? 'ONLINE' : status === 'warning' ? 'AVISO' : status === 'critical' ? 'OFFLINE' : 'Aguardando';
                return (
                  <div key={s.id} className="dash-site-card" style={{ '--site-color': color, cursor: 'pointer' }} onClick={() => onNavigate('sensor-library')}>
                    <div className="dash-site-status">
                      <span className="dash-site-badge"><span style={{ width: 5, height: 5, borderRadius: '50%', background: 'white' }} />{label}</span>
                      <span style={{ fontSize: 11, color: '#94a3b8' }}>❄️ HVAC</span>
                    </div>
                    <div className="dash-site-name">❄️ {s.name}</div>
                    {(() => {
                      const md2 = m?.metadata || {};
                      const temp = md2['Conflex temp_interna']?.value
                        ?? md2['Conflex temp_retorno_maq1']?.value
                        ?? md2['Conflex temp_retorno_maq2']?.value;
                      const tempAlta = md2['Conflex alarme_temp_alta']?.value;
                      const plc = md2['Conflex status_plc']?.value;
                      if (temp != null) return <div className="dash-site-url">🌡️ {temp}°C{tempAlta === 1 ? ' ⚠️' : ''}</div>;
                      // Fallback: mostrar status das máquinas se não tem temperatura
                      if (plc != null) return <div className="dash-site-url">🔌 PLC: {plc === 1 ? 'ON' : 'OFF'}</div>;
                      if (m) return <div className="dash-site-url">📊 {m.value?.toFixed(1)} {m.unit}</div>;
                      return null;
                    })()}
                  </div>
                );
              })}
              {storageSensors.map(s => {
                const m = httpMetrics[String(s.id)];
                const status = m?.status || 'unknown';
                const color = status === 'ok' ? '#22C55E' : status === 'warning' ? '#F59E0B' : status === 'critical' ? '#EF4444' : '#6B7280';
                const label = status === 'ok' ? 'ONLINE' : status === 'warning' ? 'AVISO' : status === 'critical' ? 'CRÍTICO' : 'Aguardando';
                const md = m?.metadata || {};
                const pct = md['EqualLogic storage_percent']?.value;
                const totalGb = md['EqualLogic storage_total']?.value;
                const freeGb = md['EqualLogic storage_free']?.value;
                const disksTotal = md['EqualLogic disks_total']?.value;
                const disksOnline = md['EqualLogic disks_online']?.value;
                const conns = md['EqualLogic iscsi_connections']?.value || md['EqualLogic connections']?.value;
                const uptime = md['EqualLogic uptime']?.value;
                return (
                  <div key={s.id} className="dash-site-card" style={{ '--site-color': color, cursor: 'pointer' }} onClick={() => onNavigate('sensor-library')}>
                    <div className="dash-site-status">
                      <span className="dash-site-badge"><span style={{ width: 5, height: 5, borderRadius: '50%', background: 'white' }} />{label}</span>
                      <span style={{ fontSize: 11, color: '#94a3b8' }}>💾 Storage</span>
                    </div>
                    <div className="dash-site-name">💾 {s.name}</div>
                    {pct != null && (
                      <>
                        <div className="dash-site-url">📊 Uso: {pct}% · Total: {totalGb >= 1024 ? (totalGb/1024).toFixed(1) + ' TB' : totalGb + ' GB'}</div>
                        <div className="dash-site-url">💿 Livre: {freeGb >= 1024 ? (freeGb/1024).toFixed(2) + ' TB' : freeGb + ' GB'}</div>
                      </>
                    )}
                    {disksTotal != null && (
                      <div className="dash-site-url">💿 Discos: {disksOnline}/{disksTotal} online{conns ? ` · 🔗 ${conns} iSCSI` : ''}{uptime ? ` · ⏱️ ${uptime}d` : ''}</div>
                    )}
                    {!pct && !disksTotal && m && (
                      <div className="dash-site-url">⏱️ Uptime: {uptime || '?'}d · 🔗 {conns || '?'} conexões</div>
                    )}
                  </div>
                );
              })}
              {printerSensors.map(s => {
                const m = httpMetrics[String(s.id)];
                const status = m?.status || 'unknown';
                const color = status === 'ok' ? '#22C55E' : status === 'warning' ? '#F59E0B' : status === 'critical' ? '#EF4444' : '#6B7280';
                const label = status === 'ok' ? 'ONLINE' : status === 'warning' ? 'AVISO' : status === 'critical' ? 'OFFLINE' : 'Aguardando';
                const md = m?.metadata || {};
                const toner = md['Printer toner']?.value;
                const pages = md['Printer total_pages']?.value ?? md['Printer page_count']?.value;
                return (
                  <div key={s.id} className="dash-site-card" style={{ '--site-color': color, cursor: 'pointer' }} onClick={() => onNavigate('sensor-library')}>
                    <div className="dash-site-status">
                      <span className="dash-site-badge"><span style={{ width: 5, height: 5, borderRadius: '50%', background: 'white' }} />{label}</span>
                      <span style={{ fontSize: 11, color: '#94a3b8' }}>🖨️ Impressora</span>
                    </div>
                    <div className="dash-site-name">🖨️ {s.name}</div>
                    {toner != null && <div className="dash-site-url">🖨️ Toner: {toner}%{pages ? ` · 📄 ${Number(pages).toLocaleString('pt-BR')} páginas` : ''}</div>}
                    {toner == null && m && <div className="dash-site-url">📊 {m.value?.toFixed(1)} {m.unit}</div>}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })()}

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

      {/* ── Modal Histórico do Site ── */}
      {siteModalSensor && (
        <div
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}
          onClick={() => setSiteModalSensor(null)}
        >
          <div
            style={{ background: '#1e293b', borderRadius: 16, padding: 24, width: '100%', maxWidth: 760, maxHeight: '85vh', overflowY: 'auto', border: '1px solid #334155' }}
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700, color: '#e2e8f0' }}>🌐 {siteModalSensor.name}</div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>
                  {siteModalSensor.config?.http?.url || siteModalSensor.config?.http_url || siteModalSensor.http_url || ''}
                </div>
              </div>
              <button onClick={() => setSiteModalSensor(null)} style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 20, cursor: 'pointer', padding: '0 4px' }}>✕</button>
            </div>

            {siteHistoryLoading ? (
              <div style={{ textAlign: 'center', padding: 40, color: '#64748b' }}>Carregando histórico...</div>
            ) : siteHistory.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 40, color: '#64748b' }}>Nenhum dado nos últimos 7 dias</div>
            ) : (() => {
              // Calcular estatísticas
              const okCount = siteHistory.filter(m => m.status === 'ok').length;
              const critCount = siteHistory.filter(m => m.status === 'critical').length;
              const warnCount = siteHistory.filter(m => m.status === 'warning').length;
              const uptime = ((okCount / siteHistory.length) * 100).toFixed(2);
              const responseTimes = siteHistory.filter(m => m.value > 0).map(m => m.value);
              const avgMs = responseTimes.length ? Math.round(responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length) : 0;
              const maxMs = responseTimes.length ? Math.round(Math.max(...responseTimes)) : 0;
              const minMs = responseTimes.length ? Math.round(Math.min(...responseTimes)) : 0;

              // Preparar dados para o gráfico (amostrar para não sobrecarregar)
              const step = Math.max(1, Math.floor(siteHistory.length / 200));
              const chartData = siteHistory
                .filter((_, i) => i % step === 0)
                .reverse()
                .map(m => ({
                  time: new Date(m.timestamp).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }),
                  ms: m.value > 0 ? Math.round(m.value) : null,
                  status: m.status,
                }));

              // Calcular incidentes (períodos offline)
              const incidents = [];
              let offlineStart = null;
              for (const m of [...siteHistory].reverse()) {
                if (m.status === 'critical' && !offlineStart) {
                  offlineStart = m.timestamp;
                } else if (m.status === 'ok' && offlineStart) {
                  incidents.push({ start: offlineStart, end: m.timestamp });
                  offlineStart = null;
                }
              }
              if (offlineStart) incidents.push({ start: offlineStart, end: null });

              return (
                <>
                  {/* KPIs */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
                    {[
                      { label: 'Uptime 7d', value: `${uptime}%`, color: parseFloat(uptime) >= 99 ? '#22C55E' : parseFloat(uptime) >= 95 ? '#F59E0B' : '#EF4444' },
                      { label: 'Tempo Médio', value: `${avgMs}ms`, color: avgMs < 1000 ? '#22C55E' : avgMs < 3000 ? '#F59E0B' : '#EF4444' },
                      { label: 'Pior Resposta', value: `${maxMs}ms`, color: '#94a3b8' },
                      { label: 'Melhor Resposta', value: `${minMs}ms`, color: '#94a3b8' },
                    ].map(kpi => (
                      <div key={kpi.label} style={{ background: '#0f172a', borderRadius: 10, padding: '12px 16px', textAlign: 'center' }}>
                        <div style={{ fontSize: 20, fontWeight: 700, color: kpi.color }}>{kpi.value}</div>
                        <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>{kpi.label}</div>
                      </div>
                    ))}
                  </div>

                  {/* Gráfico de tempo de resposta */}
                  <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#94a3b8', marginBottom: 8 }}>Tempo de Resposta (ms) — últimos 7 dias</div>
                    <ResponsiveContainer width="100%" height={180}>
                      <LineChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="time" tick={{ fontSize: 9, fill: '#475569' }} interval="preserveStartEnd" />
                        <YAxis tick={{ fontSize: 9, fill: '#475569' }} />
                        <Tooltip
                          contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                          formatter={(v, n) => [`${v}ms`, 'Resposta']}
                        />
                        <ReferenceLine y={avgMs} stroke="#F59E0B" strokeDasharray="4 4" label={{ value: `Média ${avgMs}ms`, fill: '#F59E0B', fontSize: 10 }} />
                        <Line type="monotone" dataKey="ms" stroke="#6366F1" strokeWidth={1.5} dot={false} connectNulls={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Barra de disponibilidade por dia */}
                  <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#94a3b8', marginBottom: 8 }}>Disponibilidade por Dia</div>
                    <div style={{ display: 'flex', gap: 4 }}>
                      {Array.from({ length: 7 }, (_, i) => {
                        const day = new Date(Date.now() - (6 - i) * 86400000);
                        const dayStr = day.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
                        const dayMetrics = siteHistory.filter(m => {
                          const d = new Date(m.timestamp);
                          return d.toDateString() === day.toDateString();
                        });
                        const dayOk = dayMetrics.filter(m => m.status === 'ok').length;
                        const dayTotal = dayMetrics.length;
                        const dayUptime = dayTotal > 0 ? (dayOk / dayTotal * 100) : null;
                        const barColor = dayUptime === null ? '#334155' : dayUptime >= 99 ? '#22C55E' : dayUptime >= 95 ? '#F59E0B' : '#EF4444';
                        return (
                          <div key={i} style={{ flex: 1, textAlign: 'center' }}>
                            <div title={dayUptime !== null ? `${dayUptime.toFixed(1)}%` : 'Sem dados'} style={{ height: 32, background: barColor, borderRadius: 4, marginBottom: 4, opacity: dayUptime === null ? 0.3 : 1 }} />
                            <div style={{ fontSize: 10, color: '#475569' }}>{dayStr}</div>
                            <div style={{ fontSize: 10, color: barColor, fontWeight: 600 }}>{dayUptime !== null ? `${dayUptime.toFixed(0)}%` : '—'}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Incidentes recentes */}
                  {incidents.length > 0 && (
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: '#94a3b8', marginBottom: 8 }}>🔴 Quedas Detectadas ({incidents.length})</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {incidents.slice(0, 5).map((inc, i) => {
                          const start = new Date(inc.start);
                          const end = inc.end ? new Date(inc.end) : new Date();
                          const dur = Math.round((end - start) / 60000);
                          return (
                            <div key={i} style={{ background: '#0f172a', borderRadius: 8, padding: '8px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: '3px solid #EF4444' }}>
                              <div>
                                <div style={{ fontSize: 12, color: '#e2e8f0' }}>
                                  {start.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}
                                  {inc.end && ` → ${end.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}`}
                                  {!inc.end && ' → Agora'}
                                </div>
                              </div>
                              <div style={{ fontSize: 12, color: '#EF4444', fontWeight: 600 }}>
                                {dur < 60 ? `${dur}min` : `${Math.floor(dur/60)}h ${dur%60}min`}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
