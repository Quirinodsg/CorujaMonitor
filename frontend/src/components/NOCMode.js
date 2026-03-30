import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './NOCMode.css';

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

  const loadNOCData = useCallback(async () => {
    try {
      const [global, heatmap, incidents, kpis] = await Promise.all([
        api.get('/noc/global-status', { timeout: 30000 }),
        api.get('/noc/heatmap', { timeout: 30000 }),
        api.get('/noc/active-incidents', { timeout: 30000 }),
        api.get('/noc/kpis', { timeout: 30000 })
      ]);

      setData({
        global: global.data,
        heatmap: heatmap.data,
        incidents: incidents.data,
        kpis: kpis.data
      });
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Erro ao carregar dados NOC:', error);
    }
  }, []);

  const loadDatacenterData = useCallback(async () => {
    try {
      const [sr, svr] = await Promise.all([api.get('/sensors/standalone'), api.get('/servers')]);
      const all = sr.data;
      setDcSites(all.filter(s => s.sensor_type === 'http' || s.category === 'network'));
      setDcEnergy(all.filter(s => (s.name||'').toLowerCase().match(/nobreak|ups|gerador|energia|engetron/)));
      setDcHvac(all.filter(s => (s.name||'').toLowerCase().match(/ar.condicionado|hvac|temperatura|cooling|conflex/)));
      const netTypes = ['switch','router','firewall','access_point','ap','gateway'];
      const assets = svr.data.filter(s => netTypes.includes((s.device_type||'').toLowerCase()));
      setDcNetwork(assets);
      if (all.length > 0) { const mr = await api.get('/metrics/latest/batch?sensor_ids=' + all.map(s=>s.id).join(',')); setDcMetrics(mr.data); }
      if (assets.length > 0) { try { const ns = await api.get('/dashboard/network-assets-status?ids=' + assets.map(a=>a.id).join(',')); setDcNetStatuses(ns.data); } catch(_){} }
    } catch(_){}
  }, []);

  useEffect(() => {
    loadNOCData();
    loadDatacenterData();
    const interval = setInterval(loadNOCData, 3000);
    const dcInterval = setInterval(loadDatacenterData, 30000);
    return () => { clearInterval(interval); clearInterval(dcInterval); };
  }, [loadNOCData, loadDatacenterData]);

  useEffect(() => {
    if (autoRotate) {
      const rotateInterval = setInterval(() => {
        setCurrentDashboard((prev) => (prev + 1) % dashboards.length);
      }, 15000); // Rotaciona a cada 15s
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
    const gs = (s) => ({ c: s==='ok'?'#22C55E':s==='warning'?'#F59E0B':s==='critical'?'#EF4444':'#6B7280', l: s==='ok'?'ONLINE':s==='warning'?'AVISO':s==='critical'?'OFFLINE':'AGUARDANDO' });
    const cd = (k,n,st,ic,sub,ex) => { const{c,l}=gs(st); return <div key={k} style={{background:`${c}10`,border:`1px solid ${c}33`,borderLeft:`4px solid ${c}`,borderRadius:12,padding:'14px 18px',minWidth:170}}><div style={{marginBottom:6}}><span style={{display:'inline-flex',alignItems:'center',gap:4,padding:'2px 8px',borderRadius:20,fontSize:10,fontWeight:700,background:c,color:'#fff'}}><span style={{width:5,height:5,borderRadius:'50%',background:'#fff'}}/>{l}</span></div><div style={{fontSize:15,fontWeight:700,color:'#e2e8f0'}}>{ic} {n}</div>{sub&&<div style={{fontSize:11,color:'#94a3b8',fontFamily:'monospace',marginTop:2}}>{sub}</div>}{ex&&<div style={{fontSize:11,color:'#94a3b8',marginTop:4}}>{ex}</div>}</div>; };
    const icons={switch:'🔀',router:'📡',firewall:'🔥',access_point:'📶',ap:'📶',gateway:'📡'};
    const labels={switch:'Switch',router:'Router',firewall:'Firewall',access_point:'AP',ap:'AP',gateway:'Gateway'};
    return (
      <div className="noc-dashboard" style={{padding:20}}>
        <h2 style={{color:'#e2e8f0',marginBottom:20,fontSize:20}}>🏢 Datacenter</h2>
        {dcSites.length>0&&<><h3 style={{fontSize:14,color:'#64748b',marginBottom:12}}>🌐 Sites ({dcSites.length})</h3><div style={{display:'flex',gap:12,flexWrap:'wrap',marginBottom:24}}>{dcSites.map(s=>{const m=dcMetrics[String(s.id)];return cd(s.id,s.name,m?.status||'unknown','🌐',s.config?.http?.url||'',m?`⏱️ ${Math.round(m.value||0)}ms`:null);})}</div></>}
        {dcNetwork.length>0&&<><h3 style={{fontSize:14,color:'#64748b',marginBottom:12}}>🔀 Ativos de Rede ({dcNetwork.length})</h3><div style={{display:'flex',gap:12,flexWrap:'wrap',marginBottom:24}}>{dcNetwork.map(a=>{const dt=(a.device_type||'').toLowerCase();return cd('n'+a.id,a.hostname,dcNetStatuses[a.id]||'unknown',icons[dt]||'📦',a.ip_address,labels[dt]||dt);})}</div></>}
        {dcEnergy.length>0&&<><h3 style={{fontSize:14,color:'#64748b',marginBottom:12}}>⚡ Energia ({dcEnergy.length})</h3><div style={{display:'flex',gap:12,flexWrap:'wrap',marginBottom:24}}>{dcEnergy.map(s=>{const m=dcMetrics[String(s.id)];const md=m?.metadata||{};const t=md['Engetron temperatura']?.value;const a=md['Engetron bateria_autonomia']?.value;return cd(s.id,s.name,m?.status||'unknown','🔋',s.config?.ip_address||'',t?`🌡️ ${t}°C · 🔋 ${a||'?'} min`:null);})}</div></>}
        {dcHvac.length>0&&<><h3 style={{fontSize:14,color:'#64748b',marginBottom:12}}>❄️ Ar-Condicionado ({dcHvac.length})</h3><div style={{display:'flex',gap:12,flexWrap:'wrap',marginBottom:24}}>{dcHvac.map(s=>{const m=dcMetrics[String(s.id)];return cd(s.id,s.name,m?.status||'unknown','❄️',s.config?.ip_address||'',m?`📊 ${m.value?.toFixed(1)} ${m.unit}`:null);})}</div></>}
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
          {lastUpdate.toLocaleTimeString()} • Atualização automática: 3s
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
