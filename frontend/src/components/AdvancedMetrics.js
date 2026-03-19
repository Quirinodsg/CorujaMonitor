import React, { useState, useEffect } from 'react';
import './AdvancedMetrics.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const PERIODS = [
  { label: '1h', hours: 1 }, { label: '6h', hours: 6 },
  { label: '24h', hours: 24 }, { label: '7d', hours: 168 },
];

function Sparkline({ data, color = '#60a5fa', width = 200, height = 50 }) {
  if (!data || data.length < 2) return <span style={{ color: '#475569', fontSize: '0.75rem' }}>sem dados</span>;
  const vals = data.map(d => d.value ?? d);
  const min = Math.min(...vals), max = Math.max(...vals);
  const range = max - min || 1;
  const pts = vals.map((v, i) => {
    const x = (i / (vals.length - 1)) * width;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return `${x},${y}`;
  }).join(' ');
  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
  );
}

export default function AdvancedMetrics() {
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState('');
  const [period, setPeriod] = useState(24);
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch(`${API}/api/v1/servers`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(d => {
        // API pode retornar array direto, {servers: []}, ou objeto paginado
        const list = Array.isArray(d) ? d : (Array.isArray(d.servers) ? d.servers : []);
        setServers(list);
      })
      .catch(() => setServers([]));
  }, []);

  useEffect(() => {
    if (!selectedServer) return;
    const token = localStorage.getItem('token');
    setLoading(true);
    fetch(`${API}/api/v1/metrics?server_id=${selectedServer}&hours=${period}&limit=500`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(d => setMetrics(d.metrics || d || []))
      .catch(() => setMetrics([]))
      .finally(() => setLoading(false));
  }, [selectedServer, period]);

  // Group metrics by sensor type
  const grouped = metrics.reduce((acc, m) => {
    const key = m.sensor_type || m.type || 'other';
    if (!acc[key]) acc[key] = [];
    acc[key].push(m);
    return acc;
  }, {});

  const exportCSV = () => {
    if (!metrics.length) return;
    const header = 'timestamp,sensor_type,value,unit,status\n';
    const rows = metrics.map(m =>
      `${m.timestamp},${m.sensor_type || ''},${m.value},${m.unit || ''},${m.status || ''}`
    ).join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url;
    a.download = `metrics_${selectedServer}_${period}h.csv`; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="advm-container">
      <div className="advm-header">
        <h2>📊 Métricas Avançadas</h2>
        <div className="advm-controls">
          <select value={selectedServer} onChange={e => setSelectedServer(e.target.value)}>
            <option value="">Selecione um servidor</option>
            {servers.map(s => <option key={s.id} value={s.id}>{s.name || s.hostname}</option>)}
          </select>
          <div className="advm-period-btns">
            {PERIODS.map(p => (
              <button key={p.hours}
                className={`advm-period-btn ${period === p.hours ? 'active' : ''}`}
                onClick={() => setPeriod(p.hours)}
              >{p.label}</button>
            ))}
          </div>
          <button className="advm-export-btn" onClick={exportCSV} disabled={!metrics.length}>
            ⬇ Exportar CSV
          </button>
        </div>
      </div>

      {!selectedServer && (
        <div className="advm-empty">Selecione um servidor para visualizar métricas avançadas</div>
      )}

      {loading && <div className="advm-loading">Carregando métricas...</div>}

      {!loading && selectedServer && Object.keys(grouped).length === 0 && (
        <div className="advm-empty">Nenhuma métrica encontrada para o período selecionado</div>
      )}

      <div className="advm-charts-grid">
        {Object.entries(grouped).map(([type, data]) => {
          const latest = data[data.length - 1];
          const avg = data.reduce((s, d) => s + (d.value || 0), 0) / data.length;
          const max = Math.max(...data.map(d => d.value || 0));
          const min = Math.min(...data.map(d => d.value || 0));
          return (
            <div key={type} className="advm-chart-card">
              <div className="advm-chart-header">
                <span className="advm-chart-type">{type}</span>
                <span className="advm-chart-latest">
                  {latest?.value?.toFixed(2)} {latest?.unit || ''}
                </span>
              </div>
              <Sparkline data={data} color="#60a5fa" width={280} height={60} />
              <div className="advm-chart-stats">
                <span>Avg: {avg.toFixed(1)}</span>
                <span>Min: {min.toFixed(1)}</span>
                <span>Max: {max.toFixed(1)}</span>
                <span>{data.length} pts</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
