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
          <div className="card-label">Recomendações</div>
          <div className="card-value warning">{recommendations.length}</div>
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

      {/* ── Cluster Overview ── */}
      {hosts.length > 0 && (() => {
        var totalCpus = hosts.reduce((s, h) => s + (h.total_cpus || 0), 0);
        // Fallback: estimate total_cpus from API overview if host data doesn't have it
        var clusterCpus = totalCpus > 0 ? totalCpus : (overview?.total_hosts || 0) * 48;
        var totalVcpus = vms.reduce((s, v) => s + (v.vcpus || 0), 0);
        var vcpuFree = Math.max(0, clusterCpus * 4 - totalVcpus); // 4:1 overcommit ratio
        var totalMemGB = hosts.reduce((s, h) => s + (h.total_memory_gb || 0), 0);
        var usedMemGB = vms.reduce((s, v) => s + ((v.memory_mb || 0) / 1024), 0);
        var freeMemGB = Math.max(0, totalMemGB - usedMemGB);
        var totalStorGB = hosts.reduce((s, h) => s + (h.total_storage_gb || 0), 0);
        // FinOps cost estimation in R$ — custos reais do datacenter Techbiz
        // Total mensal datacenter: R$ 50.428,70
        // Pesos: RAM 25%, CPU 40%, Disco 25%, Rede/IP 10%
        // Custos unitários: vCPU R$19,70/mês (8:1 oversub), RAM R$12,31/GB/mês, Disco R$0,45/GB/mês
        var COST_VCPU = 19.70;   // R$/vCPU/mês
        var COST_RAM_GB = 12.31; // R$/GB/mês
        var COST_DISK_GB = 0.45; // R$/GB/mês
        var COST_INFRA_HOST = 50428.70 / 2; // Infra fixa rateada por host (energia, ar, nobreak, pessoal, depreciação)
        var costVcpu = totalVcpus * COST_VCPU;
        var costMem = usedMemGB * COST_RAM_GB;
        var costStor = totalStorGB * COST_DISK_GB;
        var costInfra = hosts.length * COST_INFRA_HOST * 0.1; // 10% proporcional (resto é fixo)
        var totalCost = 50428.70; // Custo total real do datacenter
        var costVMs = costVcpu + costMem + costStor;
        // Savings: cada vCPU liberada = R$19,70, cada GB RAM = R$12,31
        var overRecs = recommendations.filter(r => r.category === 'overprovisioned');
        var idleRecs = recommendations.filter(r => r.category === 'idle');
        var rightRecs = recommendations.filter(r => r.category === 'right-size');
        var savingsVcpu = overRecs.reduce((s, r) => s + (r.estimated_savings || 0), 0);
        var savingsIdle = idleRecs.reduce((s, r) => s + (r.estimated_savings || 0), 0);
        var savingsRightSize = rightRecs.reduce((s, r) => s + (r.estimated_savings || 0), 0);
        var totalSavings = savingsVcpu + savingsIdle + savingsRightSize;
        return (
        <div className="hyperv-cluster-overview">
          <h3>🏢 Visão do Cluster</h3>
          <div className="cluster-grid">
            <div className="cluster-card">
              <div className="cluster-label">Servidores Físicos</div>
              <div className="cluster-value">{hosts.length}</div>
              <div className="cluster-detail">{hosts.map(h => h.hostname).join(', ')}</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">CPUs Físicas (Lógicas)</div>
              <div className="cluster-value">{clusterCpus}</div>
              <div className="cluster-detail">{totalVcpus} vCPUs alocadas · Ratio {clusterCpus > 0 ? (totalVcpus / clusterCpus).toFixed(1) : 0}:1</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">Memória Total</div>
              <div className="cluster-value">{totalMemGB.toFixed(0)} GB</div>
              <div className="cluster-detail">{usedMemGB.toFixed(0)} GB alocada · {freeMemGB.toFixed(0)} GB livre</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">Storage Total</div>
              <div className="cluster-value">{totalStorGB.toFixed(0)} GB</div>
              <div className="cluster-detail">Uso médio {avgStor.toFixed(1)}%</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">Capacidade de Expansão</div>
              <div className="cluster-value" style={{color: freeMemGB > 64 ? 'var(--success)' : 'var(--warning)'}}>{freeMemGB > 64 ? '✓ Disponível' : '⚠ Limitada'}</div>
              <div className="cluster-detail">{freeMemGB.toFixed(0)} GB RAM livre · ~{vcpuFree} vCPUs (4:1)</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">Custo Mensal Datacenter</div>
              <div className="cluster-value">R$ {totalCost.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
              <div className="cluster-detail">VMs: vCPU R${costVcpu.toLocaleString('pt-BR',{minimumFractionDigits:0})} · RAM R${costMem.toLocaleString('pt-BR',{minimumFractionDigits:0})} · Disco R${costStor.toLocaleString('pt-BR',{minimumFractionDigits:0})}</div>
            </div>
          </div>
          {totalSavings > 0 && (
            <div className="cluster-savings">
              💰 Economia potencial com FinOps: <strong>R$ {totalSavings.toLocaleString('pt-BR', {minimumFractionDigits: 0})}/mês</strong>
              <span className="savings-detail"> (vCPU overprovisioned: R${savingsVcpu.toFixed(0)} · VMs idle: R${savingsIdle.toFixed(0)} · Right-size: R${savingsRightSize.toFixed(0)})</span>
            </div>
          )}
          {/* ── Hardware Details per Host ── */}
          <div className="cluster-hw-details">
            <h4>🔧 Hardware dos Servidores</h4>
            <table className="hw-table">
              <thead>
                <tr>
                  <th>Host</th>
                  <th>Fabricante / Modelo</th>
                  <th>Serial</th>
                  <th>Processador</th>
                  <th>Sockets × Cores</th>
                  <th>Logical CPUs</th>
                  <th>RAM</th>
                  <th>SO</th>
                </tr>
              </thead>
              <tbody>
                {hosts.map(h => (
                  <tr key={h.id}>
                    <td>{h.hostname}</td>
                    <td>{[h.manufacturer, h.model].filter(Boolean).join(' ') || '—'}</td>
                    <td>{h.serial_number || '—'}</td>
                    <td style={{fontSize: '0.75rem'}}>{h.processor_name || '—'}</td>
                    <td>{h.processor_sockets || '—'} × {h.cores_per_socket || '—'}</td>
                    <td>{h.total_cpus || '—'}</td>
                    <td>{h.total_memory_gb ? h.total_memory_gb.toFixed(0) + ' GB' : '—'}</td>
                    <td style={{fontSize: '0.75rem'}}>{h.os_version || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        );
      })()}

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
                    var memAssignedGB = vm.memory_mb != null ? (vm.memory_mb / 1024).toFixed(1) : '—';
                    var memDemandGB = vm.memory_demand_mb != null && vm.memory_demand_mb > 0 ? (vm.memory_demand_mb / 1024).toFixed(1) : null;
                    var memLabel = memDemandGB ? memDemandGB + '/' + memAssignedGB + ' GB' : memAssignedGB + ' GB';
                    if (vm.memory_percent != null && vm.memory_percent > 0) memLabel += ' (' + fmt(vm.memory_percent, '%') + ')';
                    var diskUsed = vm.disk_bytes != null && vm.disk_bytes > 0 ? (vm.disk_bytes / 1073741824).toFixed(1) : '—';
                    var diskMax = vm.disk_max_bytes != null && vm.disk_max_bytes > 0 ? (vm.disk_max_bytes / 1073741824).toFixed(0) : null;
                    var diskLabel = diskMax ? diskUsed + '/' + diskMax + ' GB' : (diskUsed !== '—' ? diskUsed + ' GB' : '—');
                    return (
                    <tr key={vm.id} className="vm-row">
                      <td>💻 {vm.name}</td>
                      <td>{vm.state}</td>
                      <td>{fmt(vm.cpu_percent, '%')}</td>
                      <td>{memLabel}</td>
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
              {rec.estimated_savings != null && rec.estimated_savings > 0 && (
                <span className="finops-savings">-R$ {rec.estimated_savings.toLocaleString('pt-BR', {minimumFractionDigits: 0})}/mês</span>
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
