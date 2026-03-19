import React, { useState, useEffect, useRef } from 'react';
import './ObservabilityDashboard.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = API.replace(/^http/, 'ws');

function HealthGauge({ score }) {
  const color = score >= 90 ? '#22c55e' : score >= 70 ? '#f59e0b' : '#ef4444';
  return (
    <div className="health-gauge">
      <svg viewBox="0 0 120 70" width="180">
        <path d="M10,60 A50,50 0 0,1 110,60" fill="none" stroke="#2d3748" strokeWidth="12" />
        <path
          d="M10,60 A50,50 0 0,1 110,60"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeDasharray={`${(score / 100) * 157} 157`}
        />
        <text x="60" y="58" textAnchor="middle" fontSize="22" fontWeight="bold" fill={color}>
          {score}
        </text>
        <text x="60" y="70" textAnchor="middle" fontSize="9" fill="#94a3b8">HEALTH SCORE</text>
      </svg>
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div className="obs-stat-card" style={{ borderLeft: `4px solid ${color}` }}>
      <div className="obs-stat-value" style={{ color }}>{value}</div>
      <div className="obs-stat-label">{label}</div>
    </div>
  );
}

export default function ObservabilityDashboard() {
  const [health, setHealth] = useState(null);
  const [impactMap, setImpactMap] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [wsStatus, setWsStatus] = useState('connecting');
  const [fetchError, setFetchError] = useState(null);
  const wsRef = useRef(null);

  const fetchData = async () => {
    try {
      const [hRes, iRes, aRes] = await Promise.all([
        fetch(`${API}/api/v1/observability/health-score`),
        fetch(`${API}/api/v1/observability/impact-map`),
        fetch(`${API}/api/v1/alerts/intelligent?status=open&limit=10`),
      ]);
      if (hRes.ok) {
        const d = await hRes.json();
        if (d.error && !d.score) {
          // Erro real sem dados úteis
          console.error('health-score error:', d.error);
          setFetchError(d.error);
        } else {
          setHealth(d);
          setFetchError(null);
          if (d.error) console.warn('health-score partial error:', d.error);
        }
      } else {
        setFetchError(`HTTP ${hRes.status}`);
      }
      if (iRes.ok) setImpactMap((await iRes.json()).nodes || []);
      if (aRes.ok) setAlerts((await aRes.json()).alerts || []);
    } catch (e) {
      console.error('ObservabilityDashboard fetch error:', e);
      setFetchError(e.message);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);

    // WebSocket for real-time updates
    let cancelled = false;
    let ws = null;

    const connect = () => {
      if (cancelled) return;
      try {
        ws = new WebSocket(`${WS_URL}/api/v1/ws/observability`);
        wsRef.current = ws;
        ws.onopen = () => { if (!cancelled) setWsStatus('connected'); };
        ws.onclose = () => {
          if (!cancelled) {
            setWsStatus('disconnected');
            setTimeout(connect, 5000);
          }
        };
        ws.onerror = () => { if (!cancelled) setWsStatus('error'); };
        ws.onmessage = (e) => {
          if (cancelled) return;
          try {
            const data = JSON.parse(e.data);
            if (data.type === 'observability_update') {
              setHealth(prev => prev ? {
                ...prev,
                score: data.health_score,
                breakdown: {
                  ...prev.breakdown,
                  sensors_ok: data.sensors_ok,
                  sensors_critical: data.sensors_critical,
                  sensors_total: data.sensors_total,
                }
              } : null);
            }
          } catch (_) {}
        };
      } catch (e) {
        if (!cancelled) setWsStatus('error');
      }
    };

    // Pequeno delay para evitar "closed before connection established" em StrictMode
    const wsTimer = setTimeout(connect, 100);

    return () => {
      cancelled = true;
      clearInterval(interval);
      clearTimeout(wsTimer);
      if (ws && ws.readyState !== WebSocket.CLOSED) ws.close();
    };
  }, []);

  const severityColor = (s) => s === 'critical' ? '#ef4444' : s === 'warning' ? '#f59e0b' : '#22c55e';

  return (
    <div className="obs-dashboard">
      <div className="obs-header">
        <h2>🔭 Observabilidade</h2>
        <span className={`ws-badge ws-${wsStatus}`}>
          {wsStatus === 'connected' ? '● Live' : wsStatus === 'connecting' ? '○ Conectando...' : '✕ Offline'}
        </span>
      </div>

      {/* Health Score */}
      <div className="obs-top-row">
        <div className="obs-card obs-card--gauge">
          <h3>Saúde da Infraestrutura</h3>
          {health ? (
            <>
              <HealthGauge score={health.score} />
              <div className={`obs-status-badge obs-status-${health.status}`}>
                {health.status === 'healthy' ? '✅ Saudável' : health.status === 'degraded' ? '⚠️ Degradado' : '🔴 Crítico'}
              </div>
            </>
          ) : fetchError ? (
            <div className="obs-error" title={fetchError}>⚠️ Erro: {fetchError}</div>
          ) : <div className="obs-loading">Carregando...</div>}
        </div>

        <div className="obs-card obs-card--stats">
          <h3>Sensores</h3>
          {health?.breakdown && Object.keys(health.breakdown).length > 0 ? (
            <div className="obs-stats-grid">
              <StatCard label="OK" value={health.breakdown.sensors_ok ?? 0} color="#22c55e" />
              <StatCard label="Warning" value={health.breakdown.sensors_warning ?? 0} color="#f59e0b" />
              <StatCard label="Crítico" value={health.breakdown.sensors_critical ?? 0} color="#ef4444" />
              <StatCard label="Unknown" value={health.breakdown.sensors_unknown ?? 0} color="#94a3b8" />
              <StatCard label="Incidentes" value={health.breakdown.open_incidents ?? 0} color="#8b5cf6" />
              <StatCard label="Total" value={health.breakdown.sensors_total ?? 0} color="#60a5fa" />
            </div>
          ) : health ? (
            <div className="obs-empty">Nenhum sensor ativo encontrado</div>
          ) : (
            <div className="obs-loading">Carregando...</div>
          )}
        </div>
      </div>

      {/* Impact Map */}
      <div className="obs-card">
        <h3>🗺️ Mapa de Impacto ({impactMap.length} afetados)</h3>
        {impactMap.length === 0 ? (
          <div className="obs-empty">✅ Nenhum servidor com alertas ativos</div>
        ) : (
          <div className="obs-impact-list">
            {impactMap.map(node => (
              <div key={node.id} className="obs-impact-item" style={{ borderLeft: `4px solid ${severityColor(node.severity)}` }}>
                <div className="obs-impact-name">{node.name}</div>
                <div className="obs-impact-ip">{node.ip}</div>
                <div className="obs-impact-badges">
                  {node.critical_sensors > 0 && <span className="badge badge-critical">{node.critical_sensors} crítico</span>}
                  {node.warning_sensors > 0 && <span className="badge badge-warning">{node.warning_sensors} warning</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Active Alerts */}
      <div className="obs-card">
        <h3>🚨 Alertas Inteligentes Ativos</h3>
        {alerts.length === 0 ? (
          <div className="obs-empty">✅ Nenhum alerta inteligente aberto</div>
        ) : (
          <table className="obs-table">
            <thead>
              <tr><th>Título</th><th>Severidade</th><th>Causa Raiz</th><th>Confiança</th><th>Criado</th></tr>
            </thead>
            <tbody>
              {alerts.map(a => (
                <tr key={a.id}>
                  <td>{a.title}</td>
                  <td><span className={`badge badge-${a.severity}`}>{a.severity}</span></td>
                  <td>{a.root_cause || '—'}</td>
                  <td>{a.confidence ? `${(a.confidence * 100).toFixed(0)}%` : '—'}</td>
                  <td>{a.created_at ? new Date(a.created_at).toLocaleString('pt-BR') : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
