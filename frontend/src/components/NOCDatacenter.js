import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './NOCRealTime.css';

function NOCDatacenter({ onExit }) {
  const [sites, setSites] = useState([]);
  const [networkAssets, setNetworkAssets] = useState([]);
  const [energySensors, setEnergySensors] = useState([]);
  const [hvacSensors, setHvacSensors] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [networkStatuses, setNetworkStatuses] = useState({});
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [standaloneRes, serversRes] = await Promise.all([
        api.get('/sensors/standalone'),
        api.get('/servers'),
      ]);

      const allSensors = standaloneRes.data;
      const httpSensors = allSensors.filter(s => s.sensor_type === 'http' || s.category === 'network');
      const energy = allSensors.filter(s => (s.name || '').toLowerCase().match(/nobreak|ups|gerador|energia|battery|power|engetron/));
      const hvac = allSensors.filter(s => (s.name || '').toLowerCase().match(/ar.condicionado|hvac|temperatura|cooling|climate|chiller|conflex/));

      setSites(httpSensors);
      setEnergySensors(energy);
      setHvacSensors(hvac);

      // Network assets
      const netTypes = ['switch', 'router', 'firewall', 'access_point', 'ap', 'ups', 'storage', 'gateway'];
      const assets = serversRes.data.filter(s => netTypes.includes((s.device_type || '').toLowerCase()));
      setNetworkAssets(assets);

      // Metrics for all standalone
      if (allSensors.length > 0) {
        const ids = allSensors.map(s => s.id).join(',');
        const metricsRes = await api.get(`/metrics/latest/batch?sensor_ids=${ids}`);
        setMetrics(metricsRes.data);
      }

      // Network statuses
      if (assets.length > 0) {
        try {
          const statusRes = await api.get('/dashboard/network-assets-status?ids=' + assets.map(a => a.id).join(','));
          setNetworkStatuses(statusRes.data);
        } catch (_) {}
      }

      setLastUpdate(new Date());
    } catch (e) {
      console.error('NOC Datacenter load error:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  const getStatusInfo = (status) => {
    if (status === 'ok') return { color: '#22C55E', label: 'ONLINE', bg: 'rgba(34,197,94,0.1)' };
    if (status === 'warning') return { color: '#F59E0B', label: 'AVISO', bg: 'rgba(245,158,11,0.1)' };
    if (status === 'critical') return { color: '#EF4444', label: 'OFFLINE', bg: 'rgba(239,68,68,0.1)' };
    return { color: '#6B7280', label: 'AGUARDANDO', bg: 'rgba(107,114,128,0.1)' };
  };

  const renderCard = (name, status, subtitle, icon, extra) => {
    const s = getStatusInfo(status);
    return (
      <div style={{
        background: s.bg, border: `1px solid ${s.color}33`, borderLeft: `4px solid ${s.color}`,
        borderRadius: 12, padding: '16px 20px', minWidth: 180, flex: '0 0 auto',
        transition: 'transform 0.2s, box-shadow 0.2s',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 4,
            padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700,
            background: s.color, color: '#fff',
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#fff', boxShadow: status === 'ok' ? '0 0 6px #fff' : 'none' }} />
            {s.label}
          </span>
        </div>
        <div style={{ fontSize: 16, fontWeight: 700, color: '#e2e8f0', marginBottom: 4 }}>{icon} {name}</div>
        {subtitle && <div style={{ fontSize: 12, color: '#94a3b8', fontFamily: 'monospace' }}>{subtitle}</div>}
        {extra && <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 6 }}>{extra}</div>}
      </div>
    );
  };

  if (loading) return <div className="noc-realtime loading"><div className="noc-loading-spinner" /><p>Carregando Datacenter...</p></div>;

  const totalItems = sites.length + networkAssets.length + energySensors.length + hvacSensors.length;
  const onlineCount = sites.filter(s => metrics[String(s.id)]?.status === 'ok').length
    + Object.values(networkStatuses).filter(s => s === 'ok').length
    + energySensors.filter(s => metrics[String(s.id)]?.status === 'ok').length
    + hvacSensors.filter(s => metrics[String(s.id)]?.status === 'ok').length;
  const criticalCount = sites.filter(s => metrics[String(s.id)]?.status === 'critical').length
    + Object.values(networkStatuses).filter(s => s === 'critical').length
    + energySensors.filter(s => metrics[String(s.id)]?.status === 'critical').length
    + hvacSensors.filter(s => metrics[String(s.id)]?.status === 'critical').length;

  return (
    <div className="noc-realtime" style={{ background: '#0a0e1a', minHeight: '100vh', padding: 0 }}>
      {/* Header */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '12px 24px', background: '#0f1629', borderBottom: '1px solid #1e293b',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: 22, fontWeight: 800, color: '#e2e8f0' }}>🏢 NOC Datacenter</span>
          <span style={{ fontSize: 12, color: '#64748b' }}>
            {totalItems} dispositivos · {onlineCount} online · {criticalCount > 0 ? <span style={{color:'#ef4444'}}>{criticalCount} críticos</span> : <span style={{color:'#22c55e'}}>0 críticos</span>}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 11, color: '#475569' }}>Atualizado: {lastUpdate.toLocaleTimeString('pt-BR')}</span>
          <button onClick={onExit} style={{
            padding: '6px 16px', background: '#1e293b', border: '1px solid #334155',
            borderRadius: 6, color: '#94a3b8', cursor: 'pointer', fontSize: 12,
          }}>❌ Sair</button>
        </div>
      </div>

      <div style={{ padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: 32 }}>
        {/* Sites */}
        {sites.length > 0 && (
          <div>
            <h2 style={{ fontSize: 16, color: '#94a3b8', marginBottom: 16, fontWeight: 600 }}>🌐 Sites Monitorados ({sites.length})</h2>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              {sites.map(s => {
                const m = metrics[String(s.id)];
                return renderCard(s.name, m?.status || 'unknown',
                  s.config?.http?.url || s.config?.http_url || '',
                  '🌐',
                  m ? `⏱️ ${Math.round(m.value || 0)}ms` : null
                );
              })}
            </div>
          </div>
        )}

        {/* Ativos de Rede */}
        {networkAssets.length > 0 && (
          <div>
            <h2 style={{ fontSize: 16, color: '#94a3b8', marginBottom: 16, fontWeight: 600 }}>🔀 Ativos de Rede ({networkAssets.length})</h2>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              {networkAssets.map(a => {
                const status = networkStatuses[a.id] || 'unknown';
                const dt = (a.device_type || 'other').toLowerCase();
                const icons = { switch: '🔀', router: '📡', firewall: '🔥', access_point: '📶', ap: '📶', gateway: '📡' };
                const labels = { switch: 'Switch', router: 'Router', firewall: 'Firewall', access_point: 'AP', ap: 'AP', gateway: 'Gateway' };
                return renderCard(a.hostname, status, a.ip_address, icons[dt] || '📦', labels[dt] || dt);
              })}
            </div>
          </div>
        )}

        {/* Energia */}
        {energySensors.length > 0 && (
          <div>
            <h2 style={{ fontSize: 16, color: '#94a3b8', marginBottom: 16, fontWeight: 600 }}>⚡ Energia ({energySensors.length})</h2>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              {energySensors.map(s => {
                const m = metrics[String(s.id)];
                const md = m?.metadata || {};
                const temp = md['Engetron temperatura']?.value;
                const autonomia = md['Engetron bateria_autonomia']?.value;
                const extra = temp ? `🌡️ ${temp}°C · 🔋 ${autonomia || '?'} min` : (m ? `📊 ${m.value?.toFixed(1)} ${m.unit}` : null);
                return renderCard(s.name, m?.status || 'unknown', s.config?.ip_address || '', '🔋', extra);
              })}
            </div>
          </div>
        )}

        {/* Ar-Condicionado */}
        {hvacSensors.length > 0 && (
          <div>
            <h2 style={{ fontSize: 16, color: '#94a3b8', marginBottom: 16, fontWeight: 600 }}>❄️ Ar-Condicionado ({hvacSensors.length})</h2>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
              {hvacSensors.map(s => {
                const m = metrics[String(s.id)];
                return renderCard(s.name, m?.status || 'unknown', s.config?.ip_address || '', '❄️',
                  m ? `📊 ${m.value?.toFixed(1)} ${m.unit}` : null
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default NOCDatacenter;
