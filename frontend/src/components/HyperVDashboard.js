import React, { useState, useEffect, useRef, useCallback } from 'react';
import api from '../services/api';
import './HyperVDashboard.css';

/* ── WebSocket URL ── */
const WS_URL = (() => {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}/api/v1/ws/hyperv`;
})();

/* ── Helpers ── */
function healthColor(score) {
  if (score >= 80) return 'var(--success)';
  if (score >= 50) return 'var(--warning)';
  return 'var(--critical)';
}

function healthClass(score) {
  if (score >= 80) return 'success';
  if (score >= 50) return 'warning';
  return 'critical';
}

function statusDotClass(status) {
  if (status === 'online') return 'online';
  if (status === 'unreachable') return 'unreachable';
  return 'unknown';
}

function fmt(v, suffix) {
  if (v == null) return '—';
  return Number(v).toFixed(1) + (suffix || '');
}

/* ── Gauge Component (pure CSS/SVG) ── */
function Gauge({ label, value, color }) {
  var pct = Math.min(100, Math.max(0, value || 0));
  var r = 42, circ = 2 * Math.PI * r;
  var offset = circ - (pct / 100) * circ;
  return (
    <div className="hyperv-gauge-card">
      <div className="gauge-label">{label}</div>
      <div className="gauge-ring">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <circle className="gauge-bg" cx="50" cy="50" r={r} />
          <circle className="gauge-fill" cx="50" cy="50" r={r}
            stroke={color} strokeDasharray={circ} strokeDashoffset={offset} />
        </svg>
        <span className="gauge-text" style={{ color }}>{pct.toFixed(0)}%</span>
      </div>
    </div>
  );
}

/* ── Main Dashboard Component ── */
function HyperVDashboard() {
  // State
  const [overview, setOverview] = useState(null);
  const [hosts, setHosts] = useState([]);
  const [vms, setVms] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedHost, setExpandedHost] = useState(null);
  const [hostVms, setHostVms] = useState({});

  // Filters
  const [period, setPeriod] = useState('24h');
  const [filterHost, setFilterHost] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // WebSocket
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const reconnectDelay = useRef(1000);

  /* ── Data Fetching ── */
  const fetchData = useCallback(async () => {
    try {
      var params = {};
      if (period) params.period = period;
      if (filterHost) params.host = filterHost;
      if (filterStatus) params.status = filterStatus;

      var [ovRes, hostRes, vmRes, finRes, aiRes] = await Promise.allSettled([
        api.get('/hyperv/overview', { params }),
        api.get('/hyperv/hosts', { params }),
        api.get('/hyperv/vms', { params }),
        api.get('/hyperv/finops/recommendations', { params }),
        api.get('/hyperv/ai/suggestions', { params }),
      ]);

      if (ovRes.status === 'fulfilled') setOverview(ovRes.value.data);
      if (hostRes.status === 'fulfilled') setHosts(Array.isArray(hostRes.value.data) ? hostRes.value.data : []);
      if (vmRes.status === 'fulfilled') setVms(Array.isArray(vmRes.value.data) ? vmRes.value.data : []);
      if (finRes.status === 'fulfilled') {
        var finData = finRes.value.data;
        setRecommendations(Array.isArray(finData) ? finData : (finData.recommendations || []));
      }
      if (aiRes.status === 'fulfilled') {
        var aiData = aiRes.value.data;
        setSuggestions(Array.isArray(aiData) ? aiData : (aiData.suggestions || []));
      }
    } catch (err) {
      console.error('Erro ao carregar dados Hyper-V:', err);
    } finally {
      setLoading(false);
    }
  }, [period, filterHost, filterStatus]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  /* ── WebSocket Connection ── */
  const connectWs = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState <= 1) return;
    try {
      var ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
        reconnectDelay.current = 1000;
        // Subscribe with current filters
        ws.send(JSON.stringify({
          action: 'subscribe',
          filters: { host: filterHost || undefined, status: filterStatus || undefined }
        }));
      };

      ws.onmessage = (evt) => {
        try {
          var msg = JSON.parse(evt.data);
          if (msg.type === 'overview_update' && msg.data) setOverview(msg.data);
          if (msg.type === 'host_update' && msg.data) {
            setHosts(prev => {
              var idx = prev.findIndex(h => h.id === msg.data.id);
              if (idx >= 0) { var n = [...prev]; n[idx] = msg.data; return n; }
              return [...prev, msg.data];
            });
          }
        } catch (_) {}
      };

      ws.onclose = () => {
        setWsConnected(false);
        // Auto-reconnect with exponential backoff
        reconnectTimer.current = setTimeout(() => {
          reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000);
          connectWs();
        }, reconnectDelay.current);
      };

      ws.onerror = () => { ws.close(); };
    } catch (_) {}
  }, [filterHost, filterStatus]);

  useEffect(() => {
    connectWs();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connectWs]);

  /* ── Expand host row to show VMs ── */
  const toggleHost = async (hostId) => {
    if (expandedHost === hostId) { setExpandedHost(null); return; }
    setExpandedHost(hostId);
    if (!hostVms[hostId]) {
      try {
        var res = await api.get(`/hyperv/hosts/${hostId}/vms`);
        setHostVms(prev => ({ ...prev, [hostId]: Array.isArray(res.data) ? res.data : [] }));
      } catch (_) {
        setHostVms(prev => ({ ...prev, [hostId]: [] }));
      }
    }
  };

  /* ── Computed: aggregate gauges ── */
  var avgCpu = 0, avgMem = 0, avgStor = 0;
  if (hosts.length > 0) {
    avgCpu = hosts.reduce((s, h) => s + (h.cpu_percent || 0), 0) / hosts.length;
    avgMem = hosts.reduce((s, h) => s + (h.memory_percent || 0), 0) / hosts.length;
    avgStor = hosts.reduce((s, h) => s + (h.storage_percent || 0), 0) / hosts.length;
  }

  /* ── Computed: top consumers ── */
  var topCpu = [...vms].sort((a, b) => (b.cpu_percent || 0) - (a.cpu_percent || 0)).slice(0, 5);
  var topMem = [...vms].sort((a, b) => (b.memory_percent || 0) - (a.memory_percent || 0)).slice(0, 5);

  /* ── Gauge color ── */
  function gaugeColor(v) {
    if (v >= 75) return 'var(--critical)';
    if (v >= 50) return 'var(--warning)';
    return 'var(--success)';
  }

  /* ── Loading state ── */
  if (loading) {
    return (
      <div className="hyperv-dashboard">
        <div className="hyperv-loading">
          <div className="spinner" />
          <div>Carregando dados Hyper-V...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="hyperv-dashboard">
      {/* ── Header ── */}
      <h2>
        🖥️ Hyper-V Observabilidade
        <span className="hyperv-ws-indicator">
          <span className={`ws-dot ${wsConnected ? 'connected' : 'disconnected'}`} />
          {wsConnected ? 'Tempo real' : 'Desconectado'}
        </span>
      </h2>

      {/* ── Summary Cards ── */}
      <div className="hyperv-summary-cards">
        <div className="hyperv-card">
          <div className="card-label">Total Hosts</div>
          <div className="card-value">{overview?.total_hosts ?? hosts.length}</div>
        </div>
        <div className="hyperv-card">
          <div className="card-label">Total VMs</div>
          <div className="card-value">{overview?.total_vms ?? vms.length}</div>
        </div>
        <div className="hyperv-card">
          <div className="card-label">VMs Rodando</div>
          <div className="card-value success">{overview?.running_vms ?? vms.filter(v => v.state === 'Running').length}</div>
        </div>
        <div className="hyperv-card">
          <div className="card-label">Alertas Ativos</div>
          <div className="card-value critical">{overview?.active_alerts ?? 0}</div>
        </div>
        <div className="hyperv-card">
          <div className="card-label">Health Score</div>
          <div className={'card-value ' + healthClass(overview?.health_score ?? 0)}>
            {fmt(overview?.health_score)}
          </div>
        </div>
      </div>

      {/* ── Gauges + Filters ── */}
      <div className="hyperv-gauges-row">
        <Gauge label="CPU Médio" value={avgCpu} color={gaugeColor(avgCpu)} />
        <Gauge label="Memória Média" value={avgMem} color={gaugeColor(avgMem)} />
        <Gauge label="Storage Médio" value={avgStor} color={gaugeColor(avgStor)} />

        <div className="hyperv-filters">
          <div>
            <label>Período</label>
            <div className="hyperv-period-btns">
              {['24h', '7d', '30d'].map(p => (
                <button key={p} className={period === p ? 'active' : ''} onClick={() => setPeriod(p)}>{p}</button>
              ))}
            </div>
          </div>
          <div>
            <label>Host</label>
            <select value={filterHost} onChange={e => setFilterHost(e.target.value)}>
              <option value="">Todos os hosts</option>
              {hosts.map(h => <option key={h.id} value={h.hostname}>{h.hostname}</option>)}
            </select>
          </div>
          <div>
            <label>Status VM</label>
            <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
              <option value="">Todos</option>
              <option value="running">Running</option>
              <option value="stopped">Stopped</option>
              <option value="paused">Paused</option>
              <option value="saved">Saved</option>
            </select>
          </div>
        </div>
      </div>

      {/* ── Host Table ── */}
      <div className="hyperv-host-table-wrap">
        <h3>🖥️ Hosts Hyper-V</h3>
        {hosts.length === 0 ? (
          <div className="hyperv-empty">Nenhum host encontrado</div>
        ) : (
          <table className="hyperv-host-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Status</th>
                <th>CPU%</th>
                <th>Memória%</th>
                <th>Storage%</th>
                <th>Latência WMI</th>
                <th>VMs</th>
                <th>Health Score</th>
              </tr>
            </thead>
            <tbody>
              {hosts.map(h => (
                <React.Fragment key={h.id}>
                  <tr className="host-row" onClick={() => toggleHost(h.id)}>
                    <td>{expandedHost === h.id ? '▼' : '▶'} {h.hostname}</td>
                    <td>
                      <span className="status-badge">
                        <span className={`dot ${statusDotClass(h.status)}`} />
                        {h.status}
                      </span>
                    </td>
                    <td style={{ color: gaugeColor(h.cpu_percent || 0) }}>{fmt(h.cpu_percent, '%')}</td>
                    <td style={{ color: gaugeColor(h.memory_percent || 0) }}>{fmt(h.memory_percent, '%')}</td>
                    <td style={{ color: gaugeColor(h.storage_percent || 0) }}>{fmt(h.storage_percent, '%')}</td>
                    <td>{h.wmi_latency_ms != null ? h.wmi_latency_ms.toFixed(0) + 'ms' : '—'}</td>
                    <td>{h.vm_count ?? 0}</td>
                    <td>
                      <div className="health-score-bar">
                        <span style={{ color: healthColor(h.health_score || 0) }}>{fmt(h.health_score)}</span>
                        <div className="bar">
                          <div className="bar-fill" style={{ width: (h.health_score || 0) + '%', background: healthColor(h.health_score || 0) }} />
                        </div>
                      </div>
                    </td>
                  </tr>
                  {expandedHost === h.id && (hostVms[h.id] || []).map(vm => {
                    var memGB = vm.memory_mb != null ? (vm.memory_mb / 1024).toFixed(1) : '—';
                    var diskUsed = vm.disk_bytes != null && vm.disk_bytes > 0 ? (vm.disk_bytes / 1073741824).toFixed(1) : '—';
                    var diskMax = vm.disk_max_bytes != null && vm.disk_max_bytes > 0 ? (vm.disk_max_bytes / 1073741824).toFixed(0) : null;
                    var diskLabel = diskMax ? diskUsed + '/' + diskMax + ' GB' : (diskUsed !== '—' ? diskUsed + ' GB' : '—');
                    return (
                    <tr key={vm.id} className="vm-row">
                      <td>💻 {vm.name}</td>
                      <td>{vm.state}</td>
                      <td>{fmt(vm.cpu_percent, '%')}</td>
                      <td>{memGB} GB {vm.memory_percent != null && vm.memory_percent > 0 ? '(' + fmt(vm.memory_percent, '%') + ')' : ''}</td>
                      <td>{diskLabel}</td>
                      <td>—</td>
                      <td>{vm.vcpus ?? '—'} vCPU</td>
                      <td>—</td>
                    </tr>
                    );
                  })}
                  {expandedHost === h.id && (!hostVms[h.id] || hostVms[h.id].length === 0) && (
                    <tr className="vm-row"><td colSpan={8} style={{ textAlign: 'center' }}>Nenhuma VM encontrada</td></tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ── Bottom Grid: Top Consumers + FinOps ── */}
      <div className="hyperv-bottom-grid">
        {/* Top Consumers */}
        <div className="hyperv-section">
          <h3>🔥 Top Consumers</h3>
          <div className="top-consumers-cols">
            <div>
              <h4>Top 5 CPU</h4>
              {topCpu.length === 0 && <div className="hyperv-empty">Sem dados</div>}
              {topCpu.map((vm, i) => (
                <div key={vm.id || i} className="consumer-item">
                  <span className="rank">{i + 1}.</span>
                  <span className="name">{vm.name}</span>
                  <span className="value" style={{ color: gaugeColor(vm.cpu_percent || 0) }}>{fmt(vm.cpu_percent, '%')}</span>
                </div>
              ))}
            </div>
            <div>
              <h4>Top 5 Memória</h4>
              {topMem.length === 0 && <div className="hyperv-empty">Sem dados</div>}
              {topMem.map((vm, i) => (
                <div key={vm.id || i} className="consumer-item">
                  <span className="rank">{i + 1}.</span>
                  <span className="name">{vm.name}</span>
                  <span className="value" style={{ color: gaugeColor(vm.memory_percent || 0) }}>{fmt(vm.memory_percent, '%')}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* FinOps Recommendations */}
        <div className="hyperv-section">
          <h3>💰 Recomendações FinOps</h3>
          {recommendations.length === 0 && <div className="hyperv-empty">Nenhuma recomendação disponível</div>}
          {recommendations.slice(0, 8).map((rec, i) => (
            <div key={rec.id || i} className="finops-item">
              <span className="finops-icon">
                {rec.category === 'idle' ? '🔴' : rec.category === 'overprovisioned' ? '🟡' : rec.category === 'rebalance' ? '🔵' : '🟢'}
              </span>
              <div className="finops-body">
                <div className={`finops-category ${rec.category || ''}`}>{rec.category}</div>
                <div className="finops-desc">{rec.vm_name || rec.description}</div>
                {rec.suggested_action && <div className="finops-desc">{rec.suggested_action}</div>}
              </div>
              {rec.estimated_savings != null && (
                <span className="finops-savings">-R$ {rec.estimated_savings.toFixed(0)}/mês</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* ── AI Suggestions ── */}
      <div className="hyperv-section" style={{ marginBottom: 'var(--space-6)' }}>
        <h3>🤖 Sugestões da IA</h3>
        {suggestions.length === 0 && <div className="hyperv-empty">Nenhuma sugestão disponível</div>}
        {suggestions.map((s, i) => (
          <div key={i} className="ai-suggestion-item">
            <div className="ai-suggestion-header">
              <span className="ai-category">{s.category}</span>
              {s.confidence > 0.8 && <span className="badge-recomendado">✓ Recomendado</span>}
            </div>
            <div className="ai-suggestion-desc">{s.description}</div>
            <div className="ai-suggestion-meta">
              VMs: {(s.affected_vms || []).join(', ')}
              {s.target_host && <> · Host alvo: {s.target_host}</>}
              {' · '}Confiança: {((s.confidence || 0) * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HyperVDashboard;
