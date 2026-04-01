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
  const [allHosts, setAllHosts] = useState([]);

  // Cost section
  const [showCostBreakdown, setShowCostBreakdown] = useState(false);
  const [calcRam, setCalcRam] = useState(4);
  const [calcCpu, setCalcCpu] = useState(16);
  const [calcDisk, setCalcDisk] = useState(512);
  const [calcIp, setCalcIp] = useState(false);

  // Editable cost config from API
  const [costConfig, setCostConfig] = useState({
    cost_vcpu: 19.70, cost_ram_gb: 12.31, cost_disk_gb: 0.45, cost_ip: 315.18
  });
  const [costItems, setCostItems] = useState([]);
  const [reajuste, setReajuste] = useState(0);
  const [editingCosts, setEditingCosts] = useState(false);
  const [editingInfra, setEditingInfra] = useState(false);
  const [costDraft, setCostDraft] = useState({});
  const [infraDraft, setInfraDraft] = useState([]);
  const [reajusteDraft, setReajusteDraft] = useState(0);
  const [savingCosts, setSavingCosts] = useState(false);

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

      var [ovRes, hostRes, vmRes, finRes, aiRes, costRes] = await Promise.allSettled([
        api.get('/hyperv/overview', { params }),
        api.get('/hyperv/hosts', { params }),
        api.get('/hyperv/vms', { params }),
        api.get('/hyperv/finops/recommendations', { params }),
        api.get('/hyperv/ai/suggestions', { params }),
        api.get('/hyperv/cost-config'),
      ]);

      if (ovRes.status === 'fulfilled') setOverview(ovRes.value.data);
      if (hostRes.status === 'fulfilled') {
        var hostData = Array.isArray(hostRes.value.data) ? hostRes.value.data : [];
        setHosts(hostData);
        // Manter lista completa de hosts para o dropdown (não filtrada)
        if (!filterHost && hostData.length > 0) setAllHosts(hostData);
      }
      if (vmRes.status === 'fulfilled') setVms(Array.isArray(vmRes.value.data) ? vmRes.value.data : []);
      if (finRes.status === 'fulfilled') {
        var finData = finRes.value.data;
        setRecommendations(Array.isArray(finData) ? finData : (finData.recommendations || []));
      }
      if (aiRes.status === 'fulfilled') {
        var aiData = aiRes.value.data;
        setSuggestions(Array.isArray(aiData) ? aiData : (aiData.suggestions || []));
      }
      if (costRes.status === 'fulfilled' && costRes.value.data && costRes.value.data.items) {
        var map = {};
        costRes.value.data.items.forEach(function(item) { map[item.key] = item.value; });
        setCostConfig(function(prev) { return Object.assign({}, prev, map, {
          cost_vcpu: costRes.value.data.cost_vcpu,
          cost_ram_gb: costRes.value.data.cost_ram_gb,
          cost_disk_gb: costRes.value.data.cost_disk_gb,
          cost_ip: costRes.value.data.cost_ip,
        }); });
        setCostItems(costRes.value.data.items);
        setReajuste(costRes.value.data.reajuste_anual || 0);
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
  // Sort memory by internal VM usage (demand/assigned), not % of host
  var topMem = [...vms].map(v => {
    var intPct = (v.memory_demand_mb && v.memory_mb > 0) ? (v.memory_demand_mb / v.memory_mb) * 100 : (v.memory_percent || 0);
    return { ...v, _memInternalPct: intPct };
  }).sort((a, b) => b._memInternalPct - a._memInternalPct).slice(0, 5);

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
              {(allHosts.length > 0 ? allHosts : hosts).map(h => <option key={h.id} value={h.hostname}>{h.hostname}</option>)}
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
        // ── Custos editáveis via API (tabela hyperv_cost_config) ──
        var COST_VCPU = costConfig.cost_vcpu;
        var COST_RAM_GB = costConfig.cost_ram_gb;
        var COST_DISK_GB = costConfig.cost_disk_gb;
        var COST_IP = costConfig.cost_ip;
        // Composição mensal fixa do datacenter
        var infraItems = [
          { cat: 'Energia', desc: 'Energia elétrica CPD', valor: 8050.13 },
          { cat: 'Energia', desc: 'Energia ar condicionado', valor: 2388.62 },
          { cat: 'Infra', desc: 'Manutenção nobreak', valor: 250.00 },
          { cat: 'Infra', desc: 'Reparos elétricos', valor: 450.00 },
          { cat: 'Infra', desc: 'Manutenção ar condicionado', valor: 333.33 },
          { cat: 'Rede', desc: 'Link dedicado / IPs públicos', valor: 3500.00 },
          { cat: 'Software', desc: 'Licença Twilio', valor: 25.00 },
          { cat: 'Hardware', desc: 'Garantia servidores Dell', valor: 1666.67 },
          { cat: 'Hardware', desc: 'Depreciação servidores', valor: 8333.33 },
          { cat: 'Hardware', desc: 'Garantia storage', valor: 2000.00 },
          { cat: 'Hardware', desc: 'Depreciação storage', valor: 2410.00 },
          { cat: 'Hardware', desc: 'Depreciação storage bkp', valor: 1000.00 },
          { cat: 'Hardware', desc: 'Depreciação switches', valor: 581.62 },
          { cat: 'Pessoal', desc: 'Equipe infraestrutura (30%)', valor: 19440.00 },
        ];
        var totalCost = infraItems.reduce((s, i) => s + i.valor, 0);
        // Custo alocado por recurso (pesos)
        var costCpuPool = totalCost * 0.40;
        var costRamPool = totalCost * 0.25;
        var costDiskPool = totalCost * 0.25;
        var costNetPool = totalCost * 0.10;
        // Custo das VMs alocadas
        var costVcpu = totalVcpus * COST_VCPU;
        var costMem = usedMemGB * COST_RAM_GB;
        var costStor = totalStorGB * COST_DISK_GB;
        // Savings
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
              <div className="cluster-label">CPUs Lógicas / vCPUs</div>
              <div className="cluster-value">{clusterCpus} / {totalVcpus}</div>
              <div className="cluster-detail">Overcommit {clusterCpus > 0 ? (totalVcpus / clusterCpus).toFixed(1) : 0}:1 (máx 8:1)</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">Memória Total</div>
              <div className="cluster-value">{totalMemGB.toFixed(0)} GB</div>
              <div className="cluster-detail">{usedMemGB.toFixed(0)} GB alocada · {freeMemGB.toFixed(0)} GB livre</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">Storage Total</div>
              <div className="cluster-value">{totalStorGB.toFixed(0)} GB</div>
              <div className="cluster-detail">Uso médio {avgStor.toFixed(1)}% · Cap. útil 28.000 GB</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">Capacidade de Expansão</div>
              <div className="cluster-value" style={{color: freeMemGB > 64 ? 'var(--success)' : 'var(--warning)'}}>{freeMemGB > 64 ? '✓ Disponível' : '⚠ Limitada'}</div>
              <div className="cluster-detail">{freeMemGB.toFixed(0)} GB RAM livre · ~{vcpuFree} vCPUs (4:1)</div>
            </div>
            <div className="cluster-card">
              <div className="cluster-label">Custo Mensal Datacenter</div>
              <div className="cluster-value">R$ {totalCost.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
              <div className="cluster-detail">CPU 40% · RAM 25% · Disco 25% · Rede 10%</div>
            </div>
          </div>

          {/* ── Composição de Custos (collapsible) ── */}
          <div className="cluster-cost-breakdown">
            <h4 className="collapsible-header" onClick={() => setShowCostBreakdown(!showCostBreakdown)}>
              {showCostBreakdown ? '▼' : '▶'} 📊 Composição de Custos Mensais — R$ {totalCost.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
              {reajuste > 0 && <span style={{fontSize:'0.75rem', color:'var(--warning)', marginLeft:8}}>+{reajuste}% reajuste anual</span>}
            </h4>
            {showCostBreakdown && (<>
            {/* ── Editar Itens de Infraestrutura ── */}
            <div className="cost-edit-section">
              {!editingInfra ? (
                <button className="btn-edit-costs" onClick={() => { setInfraDraft(costItems.filter(i => i.editable !== false)); setReajusteDraft(reajuste); setEditingInfra(true); }}>✏️ Editar Itens de Custo</button>
              ) : (
                <div className="cost-edit-form">
                  <h5>Editar Composição de Custos</h5>
                  <div style={{maxHeight:300, overflowY:'auto', marginBottom:'var(--space-3)'}}>
                    <table className="hw-table" style={{width:'100%'}}>
                      <thead><tr><th>Item</th><th>Categoria</th><th style={{textAlign:'right', width:140}}>Valor (R$)</th></tr></thead>
                      <tbody>
                        {infraDraft.map((item, i) => (
                          <tr key={item.key || i}>
                            <td style={{fontSize:'0.8rem'}}>{item.label}</td>
                            <td style={{fontSize:'0.8rem'}}>{item.category}</td>
                            <td><input type="number" step="0.01" min="0" value={item.value} onChange={e => {
                              var next = [...infraDraft]; next[i] = {...next[i], value: Number(e.target.value) || 0}; setInfraDraft(next);
                            }} style={{width:'100%', background:'var(--surface-1)', border:'1px solid var(--border)', borderRadius:4, padding:'4px 8px', color:'var(--text-primary)', textAlign:'right'}} /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div style={{display:'flex', alignItems:'center', gap:'var(--space-3)', marginBottom:'var(--space-3)'}}>
                    <label style={{fontSize:'0.8rem', color:'var(--text-secondary)'}}>📈 Reajuste Anual (%)
                      <input type="number" step="0.1" min="0" max="50" value={reajusteDraft} onChange={e => setReajusteDraft(Number(e.target.value) || 0)}
                        style={{width:80, marginLeft:8, background:'var(--surface-1)', border:'1px solid var(--border)', borderRadius:4, padding:'4px 8px', color:'var(--text-primary)'}} />
                    </label>
                  </div>
                  <div className="cost-edit-actions">
                    <button disabled={savingCosts} onClick={async () => {
                      setSavingCosts(true);
                      try {
                        var items = infraDraft.map(i => ({key: i.key, value: i.value}));
                        items.push({key: 'reajuste_anual', value: reajusteDraft});
                        await api.put('/hyperv/cost-config', { items });
                        setReajuste(reajusteDraft);
                        setEditingInfra(false);
                        fetchData();
                      } catch (err) { console.error('Erro ao salvar:', err); }
                      finally { setSavingCosts(false); }
                    }}>{savingCosts ? 'Salvando...' : '💾 Salvar'}</button>
                    <button onClick={() => setEditingInfra(false)}>Cancelar</button>
                  </div>
                </div>
              )}
            </div>
            <div className="cost-cols">
              <div className="cost-col">
                <table className="hw-table">
                  <thead><tr><th>Item</th><th>Categoria</th><th style={{textAlign:'right'}}>Valor</th></tr></thead>
                  <tbody>
                    {(costItems.length > 0 ? costItems.filter(i => ['infra','rede','software','hardware','pessoal','energia'].includes((i.category||'').toLowerCase())) : infraItems).map((item, i) => (
                      <tr key={i}><td>{item.label || item.desc}</td><td>{item.category || item.cat}</td><td style={{textAlign:'right'}}>R$ {(item.value || item.valor || 0).toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>
                    ))}
                    <tr style={{fontWeight:700, borderTop:'2px solid var(--border)'}}><td colSpan={2}>Total Mensal {reajuste > 0 ? `(+${reajuste}% reajuste)` : ''}</td><td style={{textAlign:'right'}}>R$ {totalCost.toLocaleString('pt-BR',{minimumFractionDigits:2})}</td></tr>
                  </tbody>
                </table>
              </div>
              <div className="cost-col">
                <table className="hw-table">
                  <thead><tr><th>Recurso</th><th>Peso</th><th style={{textAlign:'right'}}>Pool</th><th style={{textAlign:'right'}}>Unitário</th></tr></thead>
                  <tbody>
                    <tr><td>CPU ({totalVcpus} vCPUs)</td><td>40%</td><td style={{textAlign:'right'}}>R$ {costCpuPool.toLocaleString('pt-BR',{minimumFractionDigits:0})}</td><td style={{textAlign:'right'}}>R$ {COST_VCPU.toFixed(2)}/vCPU</td></tr>
                    <tr><td>RAM ({totalMemGB.toFixed(0)} GB)</td><td>25%</td><td style={{textAlign:'right'}}>R$ {costRamPool.toLocaleString('pt-BR',{minimumFractionDigits:0})}</td><td style={{textAlign:'right'}}>R$ {COST_RAM_GB.toFixed(2)}/GB</td></tr>
                    <tr><td>Disco (28.000 GB)</td><td>25%</td><td style={{textAlign:'right'}}>R$ {costDiskPool.toLocaleString('pt-BR',{minimumFractionDigits:0})}</td><td style={{textAlign:'right'}}>R$ {COST_DISK_GB.toFixed(2)}/GB</td></tr>
                    <tr><td>Rede/IP (16 IPs)</td><td>10%</td><td style={{textAlign:'right'}}>R$ {costNetPool.toLocaleString('pt-BR',{minimumFractionDigits:0})}</td><td style={{textAlign:'right'}}>R$ {COST_IP.toFixed(2)}/IP</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ── Calculadora de VM Premium ── */}
            {(() => {
              var vmTotal = calcCpu * COST_VCPU + calcRam * COST_RAM_GB + calcDisk * COST_DISK_GB + (calcIp ? COST_IP : 0);
              var vmAnual = vmTotal * 12;
              return (
              <div className="vm-calc-premium">
                <div className="vm-calc-header">
                  <span className="vm-calc-icon">🧮</span>
                  <div>
                    <h4 style={{margin:0}}>Calculadora de Custo VM</h4>
                    <span style={{fontSize:'0.75rem', color:'var(--text-secondary)'}}>Simule o custo mensal de uma nova VM</span>
                  </div>
                </div>
                <div className="vm-calc-grid">
                  <div className="vm-calc-card">
                    <div className="vm-calc-card-icon" style={{background:'linear-gradient(135deg, #6366f1, #818cf8)'}}>💻</div>
                    <label>vCPUs</label>
                    <input type="range" min="1" max="128" value={calcCpu} onChange={e => setCalcCpu(Number(e.target.value))} />
                    <div className="vm-calc-card-row">
                      <input type="number" min="1" max="128" value={calcCpu} onChange={e => setCalcCpu(Number(e.target.value) || 1)} className="vm-calc-num" />
                      <span className="vm-calc-price">R$ {(calcCpu * COST_VCPU).toLocaleString('pt-BR',{minimumFractionDigits:2})}</span>
                    </div>
                  </div>
                  <div className="vm-calc-card">
                    <div className="vm-calc-card-icon" style={{background:'linear-gradient(135deg, #06b6d4, #22d3ee)'}}>🧠</div>
                    <label>RAM (GB)</label>
                    <input type="range" min="1" max="512" value={calcRam} onChange={e => setCalcRam(Number(e.target.value))} />
                    <div className="vm-calc-card-row">
                      <input type="number" min="1" max="512" value={calcRam} onChange={e => setCalcRam(Number(e.target.value) || 1)} className="vm-calc-num" />
                      <span className="vm-calc-price">R$ {(calcRam * COST_RAM_GB).toLocaleString('pt-BR',{minimumFractionDigits:2})}</span>
                    </div>
                  </div>
                  <div className="vm-calc-card">
                    <div className="vm-calc-card-icon" style={{background:'linear-gradient(135deg, #f59e0b, #fbbf24)'}}>💾</div>
                    <label>Disco (GB)</label>
                    <input type="range" min="10" max="4000" step="10" value={calcDisk} onChange={e => setCalcDisk(Number(e.target.value))} />
                    <div className="vm-calc-card-row">
                      <input type="number" min="10" max="10000" value={calcDisk} onChange={e => setCalcDisk(Number(e.target.value) || 10)} className="vm-calc-num" />
                      <span className="vm-calc-price">R$ {(calcDisk * COST_DISK_GB).toLocaleString('pt-BR',{minimumFractionDigits:2})}</span>
                    </div>
                  </div>
                  <div className="vm-calc-card">
                    <div className="vm-calc-card-icon" style={{background:'linear-gradient(135deg, #10b981, #34d399)'}}>🌐</div>
                    <label>IP Público</label>
                    <div className="vm-calc-toggle">
                      <button className={calcIp ? 'active' : ''} onClick={() => setCalcIp(true)}>Sim</button>
                      <button className={!calcIp ? 'active' : ''} onClick={() => setCalcIp(false)}>Não</button>
                    </div>
                    <span className="vm-calc-price" style={{marginTop:8}}>{calcIp ? 'R$ ' + COST_IP.toLocaleString('pt-BR',{minimumFractionDigits:2}) : 'R$ 0,00'}</span>
                  </div>
                </div>
                <div className="vm-calc-result">
                  <div className="vm-calc-result-row">
                    <span>Custo Mensal</span>
                    <span className="vm-calc-result-value">R$ {vmTotal.toLocaleString('pt-BR',{minimumFractionDigits:2})}</span>
                  </div>
                  <div className="vm-calc-result-row vm-calc-result-annual">
                    <span>Custo Anual</span>
                    <span>R$ {vmAnual.toLocaleString('pt-BR',{minimumFractionDigits:2})}</span>
                  </div>
                  <div className="vm-calc-result-breakdown">
                    <span>vCPU: {((calcCpu * COST_VCPU / vmTotal) * 100).toFixed(0)}%</span>
                    <span>RAM: {((calcRam * COST_RAM_GB / vmTotal) * 100).toFixed(0)}%</span>
                    <span>Disco: {((calcDisk * COST_DISK_GB / vmTotal) * 100).toFixed(0)}%</span>
                    {calcIp && <span>IP: {((COST_IP / vmTotal) * 100).toFixed(0)}%</span>}
                  </div>
                </div>
              </div>
              );
            })()}
            </>)}
          </div>

          {totalSavings > 0 && (
            <div className="cluster-savings">
              💰 Economia potencial com FinOps: <strong>R$ {totalSavings.toLocaleString('pt-BR', {minimumFractionDigits: 2})}/mês</strong>
              <span className="savings-detail"> (Overprovisioned: R${savingsVcpu.toLocaleString('pt-BR',{minimumFractionDigits:0})} · Idle: R${savingsIdle.toLocaleString('pt-BR',{minimumFractionDigits:0})} · Right-size: R${savingsRightSize.toLocaleString('pt-BR',{minimumFractionDigits:0})})</span>
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
                    // Show % of VM's own allocated RAM used (demand/assigned), not % of host
                    var memVmPct = (memDemandGB && vm.memory_mb > 0) ? ((vm.memory_demand_mb / vm.memory_mb) * 100).toFixed(0) : null;
                    if (memVmPct) memLabel += ' (' + memVmPct + '%)';
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
                  <span className="value" style={{ color: gaugeColor(vm._memInternalPct || 0) }}>{fmt(vm._memInternalPct, '%')}</span>
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
