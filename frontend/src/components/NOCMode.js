import React, { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';
import './NOCMode.css';

// Intervalo de polling aumentado para reduzir carga no servidor
const POLL_INTERVAL_MS = 10000;   // 10s (era 3s)
const DC_POLL_INTERVAL_MS = 60000; // 60s (era 30s)

function NOCMode({ onExit }) {
  const [data, setData] = useState({
    global: null,
    heatmap: [],
    incidents: [],
    kpis: null
  });
  const [currentDashboard, setCurrentDashboard] = useState(0);
  const [autoRotate, setAutoRotate] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const dashboards = ['global', 'heatmap', 'incidents', 'kpis', 'datacenter'];

  const [dcSites, setDcSites] = useState([]);
  const [dcNetwork, setDcNetwork] = useState([]);
  const [dcEnergy, setDcEnergy] = useState([]);
  const [dcHvac, setDcHvac] = useState([]);
  const [dcMetrics, setDcMetrics] = useState({});
  const [dcNetStatuses, setDcNetStatuses] = useState({});

  // Refs para cancelar requests em voo ao desmontar
  const abortRef = useRef(null);
  const dcAbortRef = useRef(null);
  const mountedRef = useRef(true);

  const loadNOCData = useCallback(async () => {
    // Cancela request anterior se ainda estiver em voo
    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();
    const signal = abortRef.current.signal;

    try {
      const [global, heatmap, incidents, kpis] = await Promise.all([
        api.get('/noc/global-status', { timeout: 15000, signal }),
        api.get('/noc/heatmap', { timeout: 15000, signal }),
        api.get('/noc/active-incidents', { timeout: 15000, signal }),
        api.get('/noc/kpis', { timeout: 15000, signal })
      ]);

      if (!mountedRef.current) return;
      setData({
        global: global.data,
        heatmap: heatmap.data,
        incidents: incidents.data,
        kpis: kpis.data
      });
      setLastUpdate(new Date());
    } catch (error) {
      if (error.name === 'CanceledError' || error.name === 'AbortError' || error.message === 'canceled') return;
      console.error('Erro ao carregar dados NOC:', error);
    }
  }, []);

  const loadDatacenterData = useCallback(async () => {
    if (dcAbortRef.current) dcAbortRef.current.abort();
    dcAbortRef.current = new AbortController();
    const signal = dcAbortRef.current.signal;

    try {
      const [sr, svr] = await Promise.all([
        api.get('/sensors/standalone', { signal }),
        api.get('/servers', { signal })
      ]);
      if (!mountedRef.current) return;
      const all = sr.data;
      setDcSites(all.filter(s => s.sensor_type === 'http' || s.category === 'network'));
      setDcEnergy(all.filter(s => (s.name||'').toLowerCase().match(/nobreak|ups|gerador|energia|engetron/)));
      setDcHvac(all.filter(s => (s.name||'').toLowerCase().match(/ar.condicionado|hvac|temperatura|cooling|conflex/)));
      const netTypes = ['switch','router','firewall','access_point','ap','gateway'];
      const assets = svr.data.filter(s => netTypes.includes((s.device_type||'').toLowerCase()));
      setDcNetwork(assets);
      if (all.length > 0) {
        const mr = await api.get('/metrics/latest/batch?sensor_ids=' + all.map(s=>s.id).join(','), { signal });
        if (mountedRef.current) setDcMetrics(mr.data);
      }
      if (assets.length > 0) {
        try {
          const ns = await api.get('/dashboard/network-assets-status?ids=' + assets.map(a=>a.id).join(','), { signal });
          if (mountedRef.current) setDcNetStatuses(ns.data);
        } catch(_){}
      }
    } catch(e) {
      if (e.name === 'CanceledError' || e.name === 'AbortError' || e.message === 'canceled') return;
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    loadNOCData();
    loadDatacenterData();
    const interval = setInterval(loadNOCData, POLL_INTERVAL_MS);
    const dcInterval = setInterval(loadDatacenterData, DC_POLL_INTERVAL_MS);
    return () => {
      mountedRef.current = false;
      clearInterval(interval);
      clearInterval(dcInterval);
      // Cancela qualquer request em voo
      if (abortRef.current) abortRef.current.abort();
      if (dcAbortRef.current) dcAbortRef.current.abort();
    };
  }, [loadNOCData, loadDatacenterData]);

  useEffect(() => {
    if (autoRotate) {
      const rotateInterval = setInterval(() => {
        setCurrentDashboard((prev) => (prev + 1) % dashboards.length);
      }, 15000);
      return () => clearInterval(rotateInterval);
    }
  }, [autoRotate, dashboards.length]);

  const renderGlobalStatus = () => (
    <div className="noc-dashboard global-status">
      <div className="noc-title">
        <h1>🌍 STATUS GLOBAL DO SISTEMA</h1>
        <div className="noc-subtitle">Visão Multi-Empresa em Tempo Real</div>
      </div>

      <div className="kpi-mega-grid">
        <div className="kpi-mega ok">
          <div className="kpi-icon">✅</div>
          <div className="kpi-value">{data.global?.servers_ok || 0}</div>
          <div className="kpi-label">SERVIDORES OK</div>
        </div>
        <div className="kpi-mega warning">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-value">{data.global?.servers_warning || 0}</div>
          <div className="kpi-label">EM AVISO</div>
        </div>
        <div className="kpi-mega critical">
          <div className="kpi-icon">🔥</div>
          <div className="kpi-value">{data.global?.servers_critical || 0}</div>
          <div className="kpi-label">CRÍTICOS</div>
        </div>
        <div className="kpi-mega availability">
          <div className="kpi-icon">⚡</div>
          <div className="kpi-value">{data.global?.availability || '99.9'}%</div>
          <div className="kpi-label">DISPONIBILIDADE</div>
        </div>
      </div>

      <div className="companies-grid">
        {data.global?.companies?.map((company) => (
          <div key={company.id} className={`company-card ${company.status}`}>
            <div className="company-name">{company.name}</div>
            <div className="company-stats">
              <span className="stat ok">{company.ok}</span>
              <span className="stat warning">{company.warning}</span>
              <span className="stat critical">{company.critical}</span>
            </div>
            <div className="company-availability">{company.availability}%</div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderHeatmap = () => (
    <div className="noc-dashboard heatmap-view">
      <div className="noc-title">
        <h1>🗺️ MAPA DE CALOR - DISPONIBILIDADE</h1>
        <div className="noc-subtitle">Status de Todos os Servidores</div>
      </div>

      <div className="heatmap-grid">
        {data.heatmap?.map((server) => (
          <div 
            key={server.id} 
            className={`heatmap-cell ${server.status}`}
            title={`${server.hostname} - ${server.status}`}
          >
            <div className="cell-name">{server.hostname}</div>
            <div className="cell-status">{server.availability}%</div>
          </div>
        ))}
      </div>

      <div className="heatmap-legend">
        <div className="legend-item">
          <div className="legend-color ok"></div>
          <span>OK (95-100%)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color warning"></div>
          <span>Aviso (90-95%)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color critical"></div>
          <span>Crítico (&lt;90%)</span>
        </div>
      </div>
    </div>
  );

  const renderIncidentsTicker = () => (
    <div className="noc-dashboard incidents-ticker">
      <div className="noc-title">
        <h1>🚨 INCIDENTES ATIVOS</h1>
        <div className="noc-subtitle">
          {data.incidents && data.incidents.length > 0 
            ? `${data.incidents.length} Alertas do Sistema` 
            : 'Nenhum Incidente Ativo'}
        </div>
      </div>

      <div className="ticker-container">
        {!data.incidents || data.incidents.length === 0 ? (
          <div className="no-incidents-message">
            <div className="no-incidents-icon">✅</div>
            <div className="no-incidents-text">Sistema Operando Normalmente</div>
            <div className="no-incidents-subtext">Nenhum incidente ativo no momento</div>
          </div>
        ) : (
          data.incidents.map((incident) => (
            <div key={incident.id} className={`ticker-item ${incident.severity}`}>
              <div className="ticker-time">{new Date(incident.created_at).toLocaleTimeString()}</div>
              <div className="ticker-severity">{incident.severity === 'critical' ? '🔥' : '⚠️'}</div>
              <div className="ticker-server">{incident.server_name}</div>
              <div className="ticker-message">{incident.description}</div>
              <div className="ticker-duration">{incident.duration}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  const renderKPIs = () => (
    <div className="noc-dashboard kpis-view">
      <div className="noc-title">
        <h1>📊 INDICADORES CHAVE DE PERFORMANCE</h1>
        <div className="noc-subtitle">Métricas Consolidadas</div>
      </div>

      <div className="kpis-grid">
        <div className="kpi-card">
          <div className="kpi-header">MTTR</div>
          <div className="kpi-big-value">{data.kpis?.mttr || '15'} min</div>
          <div className="kpi-description">Tempo Médio de Resolução</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header">MTBF</div>
          <div className="kpi-big-value">{data.kpis?.mtbf || '720'} h</div>
          <div className="kpi-description">Tempo Médio Entre Falhas</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header">SLA</div>
          <div className="kpi-big-value">{data.kpis?.sla || '99.95'}%</div>
          <div className="kpi-description">Acordo de Nível de Serviço</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header">INCIDENTES</div>
          <div className="kpi-big-value">{data.kpis?.incidents_24h || '12'}</div>
          <div className="kpi-description">Últimas 24 Horas</div>
        </div>
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
    const Gauge = ({ value, max, color, label, unit, size = 80 }) => {
      const pct = Math.min(100, Math.max(0, (value / max) * 100));
      const r = (size - 10) / 2;
      const circ = 2 * Math.PI * r;
      const dashOffset = circ - (pct / 100) * circ * 0.75;
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
    const dcIc = { switch: '🔀', router: '📡', firewall: '🔥', access_point: '📶', ap: '📶', gateway: '📡' };
    const dcLb = { switch: 'Switch', router: 'Router', firewall: 'Firewall', access_point: 'AP', ap: 'AP', gateway: 'Gateway' };
    const totalOnline = dcSites.filter(s => dcMetrics[String(s.id)]?.status === 'ok').length + Object.values(dcNetStatuses).filter(s => s === 'ok').length + dcEnergy.filter(s => dcMetrics[String(s.id)]?.status === 'ok').length + dcHvac.filter(s => dcMetrics[String(s.id)]?.status === 'ok').length;
    const totalAll = dcSites.length + dcNetwork.length + dcEnergy.length + dcHvac.length;
    return (
      <div className="noc-dashboard" style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, padding: '16px 20px', background: 'linear-gradient(135deg, #0f172a, #1e1b4b)', borderRadius: 16, border: '1px solid #312e81' }}>
          <div>
            <div style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0' }}>🏢 DATACENTER</div>
            <div style={{ fontSize: 12, color: '#818cf8', marginTop: 2 }}>Monitoramento em tempo real</div>
          </div>
          <div style={{ display: 'flex', gap: 24 }}>
            <div style={{ textAlign: 'center' }}><div style={{ fontSize: 28, fontWeight: 800, color: '#22c55e', textShadow: '0 0 20px rgba(34,197,94,0.5)' }}>{totalOnline}</div><div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase' }}>Online</div></div>
            <div style={{ textAlign: 'center' }}><div style={{ fontSize: 28, fontWeight: 800, color: '#94a3b8' }}>{totalAll}</div><div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase' }}>Total</div></div>
            <div style={{ textAlign: 'center' }}><div style={{ fontSize: 28, fontWeight: 800, color: totalOnline===totalAll?'#22c55e':'#f59e0b', textShadow: '0 0 20px rgba(34,197,94,0.5)' }}>{totalAll>0?Math.round(totalOnline/totalAll*100):0}%</div><div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase' }}>Uptime</div></div>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <div style={{ background: '#0f172a', borderRadius: 16, padding: 20, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 13, color: '#818cf8', fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}><span style={{ width: 8, height: 8, borderRadius: '50%', background: '#818cf8', boxShadow: '0 0 8px #818cf8' }} />SITES<span style={{ marginLeft: 'auto', fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{dcSites.length}</span></div>
            {dcSites.map(s => { const m = dcMetrics[String(s.id)]; const st = gs(m?.status); return (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', marginBottom: 6, background: st.g, borderRadius: 10, border: `1px solid ${st.c}33`, boxShadow: st.glow }}>
                <span style={{ width: 10, height: 10, borderRadius: '50%', background: st.c, boxShadow: `0 0 8px ${st.c}`, animation: st.pulse ? 'nocPulse 2s infinite' : 'none', flexShrink: 0 }} />
                <div style={{ flex: 1 }}><div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>{s.name}</div></div>
                <div style={{ fontSize: 14, fontWeight: 800, color: st.c, fontFamily: 'monospace' }}>{m ? Math.round(m.value||0)+'ms' : '—'}</div>
              </div>); })}
          </div>
          <div style={{ background: '#0f172a', borderRadius: 16, padding: 20, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 13, color: '#f59e0b', fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}><span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b', boxShadow: '0 0 8px #f59e0b' }} />ATIVOS DE REDE<span style={{ marginLeft: 'auto', fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{dcNetwork.length}</span></div>
            {dcNetwork.map(a => { const st = gs(dcNetStatuses[a.id]); const dt = (a.device_type||'').toLowerCase(); return (
              <div key={'n'+a.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', marginBottom: 6, background: st.g, borderRadius: 10, border: `1px solid ${st.c}33`, boxShadow: st.glow }}>
                <span style={{ fontSize: 18 }}>{dcIc[dt]||'📦'}</span>
                <div style={{ flex: 1 }}><div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0' }}>{a.hostname}</div><div style={{ fontSize: 10, color: '#94a3b8', fontFamily: 'monospace' }}>{a.ip_address}</div></div>
                <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 6, background: `${st.c}20`, color: st.c, fontWeight: 700 }}>{dcLb[dt]||dt}</span>
              </div>); })}
          </div>
          <div style={{ background: '#0f172a', borderRadius: 16, padding: 20, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 13, color: '#22c55e', fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}><span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 8px #22c55e' }} />ENERGIA<span style={{ marginLeft: 'auto', fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{dcEnergy.length}</span></div>
            {dcEnergy.map(s => { const m = dcMetrics[String(s.id)]; const md = m?.metadata||{}; const st = gs(m?.status); const temp = md['Engetron temperatura']?.value; const auto = md['Engetron bateria_autonomia']?.value; const carga = md['Engetron carga_max']?.value; const batV = md['Engetron bateria_tensao']?.value; return (
              <div key={s.id} style={{ background: st.g, borderRadius: 12, padding: 16, border: `1px solid ${st.c}33`, boxShadow: st.glow }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <span style={{ width: 10, height: 10, borderRadius: '50%', background: st.c, boxShadow: `0 0 8px ${st.c}`, animation: st.pulse ? 'nocPulse 2s infinite' : 'none' }} />
                  <span style={{ fontSize: 14, fontWeight: 700, color: '#e2e8f0' }}>🔋 {s.name}</span>
                  <span style={{ marginLeft: 'auto', fontSize: 10, padding: '2px 8px', borderRadius: 6, background: `${st.c}20`, color: st.c, fontWeight: 700 }}>{st.l}</span>
                </div>
                {temp !== undefined ? (
                  <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
                    <Gauge value={temp||0} max={50} color={temp>38?'#ef4444':temp>35?'#f59e0b':'#22c55e'} label="TEMP" unit="°C" />
                    <Gauge value={carga||0} max={100} color={carga>90?'#ef4444':carga>80?'#f59e0b':'#22c55e'} label="CARGA" unit="%" />
                    <Gauge value={auto||0} max={180} color={auto<5?'#ef4444':auto<10?'#f59e0b':'#22c55e'} label="AUTONOMIA" unit="m" />
                    <div style={{ textAlign: 'center' }}><div style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0' }}>{batV||'—'}</div><div style={{ fontSize: 9, color: '#64748b' }}>BATERIA (V)</div></div>
                  </div>
                ) : <div style={{ fontSize: 12, color: '#475569', textAlign: 'center', padding: 10 }}>Aguardando dados...</div>}
              </div>); })}
          </div>
          <div style={{ background: '#0f172a', borderRadius: 16, padding: 20, border: '1px solid #1e293b' }}>
            <div style={{ fontSize: 13, color: '#06b6d4', fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}><span style={{ width: 8, height: 8, borderRadius: '50%', background: '#06b6d4', boxShadow: '0 0 8px #06b6d4' }} />AR-CONDICIONADO<span style={{ marginLeft: 'auto', fontSize: 20, fontWeight: 800, color: '#e2e8f0' }}>{dcHvac.length}</span></div>
            {dcHvac.length === 0 && <div style={{ fontSize: 12, color: '#475569', textAlign: 'center', padding: 20 }}>Nenhum sensor configurado</div>}
            {dcHvac.map(s => { const m = dcMetrics[String(s.id)]; const md = m?.metadata||{}; const st = gs(m?.status); const tempInterna = md['Conflex temp_interna']?.value; const tempMaq1 = md['Conflex temp_retorno_maq1']?.value; const tempMaq2 = md['Conflex temp_retorno_maq2']?.value; const maq1 = md['Conflex maquina_1']?.value; const maq2 = md['Conflex maquina_2']?.value; const plc = md['Conflex status_plc']?.value; return (
              <div key={s.id} style={{ background: st.g, borderRadius: 12, padding: 16, border: `1px solid ${st.c}33`, boxShadow: st.glow }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                  <span style={{ width: 10, height: 10, borderRadius: '50%', background: st.c, boxShadow: `0 0 8px ${st.c}`, animation: 'nocPulse 2s infinite' }} />
                  <span style={{ fontSize: 14, fontWeight: 700, color: '#e2e8f0' }}>❄️ {s.name}</span>
                  <span style={{ marginLeft: 'auto', fontSize: 10, padding: '2px 8px', borderRadius: 6, background: `${st.c}20`, color: st.c, fontWeight: 700 }}>{st.l}</span>
                </div>
                {tempInterna !== undefined ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 32, fontWeight: 800, color: tempInterna >= 26 ? '#ef4444' : '#22c55e', textShadow: `0 0 20px ${tempInterna >= 26 ? 'rgba(239,68,68,0.5)' : 'rgba(34,197,94,0.3)'}` }}>{tempInterna}°C</div>
                      <div style={{ fontSize: 9, color: '#64748b' }}>SALA</div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94a3b8' }}>
                        <span>❄️ Máq 1: <span style={{color: maq1 === 1 ? '#22c55e' : '#ef4444', fontWeight: 700}}>{maq1 === 1 ? 'ON' : 'OFF'}</span>{tempMaq1 !== undefined && ` · ${tempMaq1}°C`}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94a3b8' }}>
                        <span>❄️ Máq 2: <span style={{color: maq2 === 1 ? '#22c55e' : '#ef4444', fontWeight: 700}}>{maq2 === 1 ? 'ON' : 'OFF'}</span>{tempMaq2 !== undefined && ` · ${tempMaq2}°C`}</span>
                      </div>
                      <div style={{ fontSize: 11, color: '#94a3b8' }}>🔌 PLC: <span style={{color: plc === 1 ? '#22c55e' : '#ef4444', fontWeight: 700}}>{plc === 1 ? 'ON' : 'OFF'}</span></div>
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ fontSize: 18 }}>❄️</span>
                    <div style={{ flex: 1 }}><div style={{ fontSize: 10, color: '#94a3b8', fontFamily: 'monospace' }}>{s.config?.ip_address||''}</div></div>
                  </div>
                )}
              </div>); })}
          </div>
        </div>
      </div>
    );
  };

  const renderCurrentDashboard = () => {
    switch (dashboards[currentDashboard]) {
      case 'global': return renderGlobalStatus();
      case 'heatmap': return renderHeatmap();
      case 'incidents': return renderIncidentsTicker();
      case 'kpis': return renderKPIs();
      case 'datacenter': return renderDatacenter();
      default: return renderGlobalStatus();
    }
  };

  return (
    <div className="noc-mode">
      <div className="noc-header">
        <div className="noc-logo">🦉 CORUJA MONITOR - NOC</div>
        <div className="noc-controls">
          <button 
            className={`noc-btn ${autoRotate ? 'active' : ''}`}
            onClick={() => setAutoRotate(!autoRotate)}
          >
            {autoRotate ? '⏸️ Pausar' : '▶️ Rotação'}
          </button>
          <button className="noc-btn" onClick={onExit}>
            ❌ Sair
          </button>
        </div>
        <div className="noc-time">
          {lastUpdate.toLocaleTimeString()} • Atualização automática: 10s
        </div>
      </div>

      {renderCurrentDashboard()}

      <div className="noc-footer">
        <div className="dashboard-indicators">
          {dashboards.map((dash, index) => (
            <div 
              key={dash}
              className={`indicator ${index === currentDashboard ? 'active' : ''}`}
              onClick={() => {
                setCurrentDashboard(index);
                setAutoRotate(false);
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default NOCMode;
