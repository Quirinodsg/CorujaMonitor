// TopologyView v2 - api relativo via Axios (sem :8000 hardcoded)
import React, { useState, useEffect, useCallback } from 'react';
import './TopologyView.css';
import api from '../services/api';

const STATUS_COLOR = {
  ok: '#22c55e',
  warning: '#f59e0b',
  critical: '#ef4444',
  unknown: '#6b7280',
  impacted: '#f97316',
};

// Ícone SVG por tipo de dispositivo (path dentro de viewBox 0 0 24 24)
const DEVICE_ICONS = {
  server:     'M2 3h20v6H2zm0 12h20v6H2zm0-6h20v3H2zM5 6h.01M5 18h.01',
  switch:     'M6 3h12l3 6H3zm0 12h12l3 6H3zM3 9h18M3 15h18',
  router:     'M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zm0 4v4m0 4v4m-4-8h8',
  firewall:   'M12 2L2 7v5c0 5.25 4.25 10.15 10 11.35C17.75 22.15 22 17.25 22 12V7z',
  hypervisor: 'M3 3h18v18H3zM9 3v18M15 3v18M3 9h18M3 15h18',
  ap:         'M8.5 8.5a5 5 0 0 1 7 0M5.5 5.5a9 9 0 0 1 13 0M12 12m-1 0a1 1 0 1 0 2 0a1 1 0 1 0-2 0M12 16v4',
  vm:         'M4 4h16v12H4zM8 20h8M12 16v4',
  container:  'M12 2l9 4.5v11L12 22l-9-4.5v-11zM12 2v20M3 6.5l9 4.5 9-4.5',
  database:   'M12 2C6.48 2 2 4.24 2 7v10c0 2.76 4.48 5 10 5s10-2.24 10-5V7c0-2.76-4.48-5-10-5zm0 3c4.42 0 8 1.57 8 3.5S16.42 12 12 12 4 10.43 4 8.5 7.58 5 12 5z',
  application:'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5',
  service:    'M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z',
  default:    'M20 7H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2zM12 15a2 2 0 1 1 0-4 2 2 0 0 1 0 4z',
};

function getDeviceIcon(node) {
  const t = (node.metadata?.device_type || node.type || 'server').toLowerCase();
  const name = (node.name || '').toLowerCase();
  // UDM (UniFi Dream Machine) = gateway/router — detectar pelo nome antes de tudo
  if (name.includes('udm')) return DEVICE_ICONS.router;
  if (t.includes('application') || t.includes('app')) return DEVICE_ICONS.application;
  if (t.includes('service')) return DEVICE_ICONS.service;
  if (t.includes('gateway')) return DEVICE_ICONS.router;
  if (t.includes('switch')) return DEVICE_ICONS.switch;
  if (t.includes('router')) return DEVICE_ICONS.router;
  if (t.includes('firewall')) return DEVICE_ICONS.firewall;
  if (t.includes('hypervisor') || t.includes('hv')) return DEVICE_ICONS.hypervisor;
  if (t.includes('ap') || t.includes('access_point') || t.includes('wifi')) return DEVICE_ICONS.ap;
  if (t.includes('udm')) return DEVICE_ICONS.router;
  if (t.includes('vm') || t.includes('virtual')) return DEVICE_ICONS.vm;
  if (t.includes('container') || t.includes('docker')) return DEVICE_ICONS.container;
  if (t.includes('database') || t.includes('db') || t.includes('sql')) return DEVICE_ICONS.database;
  if (t.includes('server')) return DEVICE_ICONS.server;
  return DEVICE_ICONS.default;
}

const EDGE_COLOR = {
  dependency: '#334155',
  database: '#6366f1',
  http: '#0ea5e9',
  infrastructure: '#1e293b',
};

// Layout hierárquico por camadas (layers 0→3) com agrupamento de VMs sob hosts HyperV
function useHierarchicalLayout(nodes, edges, width = 1100, height = 600) {
  return React.useMemo(() => {
    if (!nodes.length) return {};

    const pos = {};
    const PADDING_X = 80;
    const LAYER_Y = { 0: 80, 1: 200, 2: 340, 3: 500 };

    // Separar VMs HyperV (têm parent_id = hv_host_*) dos demais
    const hvVmIds = new Set(nodes.filter(n => n.type === 'vm' && n.parent_id?.startsWith('hv_host_')).map(n => n.id));
    const hvHostIds = new Set(nodes.filter(n => n.type === 'hypervisor').map(n => n.id));

    // Nós normais por layer (excluindo VMs HyperV — serão posicionadas sob o host)
    const byLayer = { 0: [], 1: [], 2: [], 3: [] };
    nodes.forEach(n => {
      if (hvVmIds.has(n.id)) return; // VMs HyperV tratadas separadamente
      const layer = n.layer ?? 2;
      const key = Math.min(Math.max(layer, 0), 3);
      byLayer[key].push(n);
    });

    // Posicionar nós normais em cada layer
    Object.entries(byLayer).forEach(([layerStr, layerNodes]) => {
      const layer = parseInt(layerStr);
      const y = LAYER_Y[layer] ?? 340;
      const count = layerNodes.length;
      if (!count) return;
      const usableW = width - PADDING_X * 2;
      const step = count === 1 ? 0 : usableW / (count - 1);
      layerNodes.forEach((n, i) => {
        pos[n.id] = {
          x: count === 1 ? width / 2 : PADDING_X + i * step,
          y,
        };
      });
    });

    // Posicionar VMs HyperV em arco abaixo do host pai
    hvHostIds.forEach(hostId => {
      const hostPos = pos[hostId];
      if (!hostPos) return;
      const vms = nodes.filter(n => n.parent_id === hostId && hvVmIds.has(n.id));
      if (!vms.length) return;
      const vmSpacing = Math.min(60, 300 / vms.length);
      const totalW = (vms.length - 1) * vmSpacing;
      vms.forEach((vm, i) => {
        pos[vm.id] = {
          x: hostPos.x - totalW / 2 + i * vmSpacing,
          y: hostPos.y + 120,
        };
      });
    });

    // Nós sem posição (fallback)
    nodes.forEach((n, i) => {
      if (!pos[n.id]) {
        pos[n.id] = { x: PADDING_X + (i % 10) * 90, y: 500 };
      }
    });

    return pos;
  }, [nodes, edges, width, height]);
}

export default function TopologyView() {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [selected, setSelected] = useState(null);
  const [hovered, setHovered] = useState(null);
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState(null);
  const [viewMode, setViewMode] = useState('graph'); // 'graph' | 'list'
  const [listSearch, setListSearch] = useState('');

  const W = 1100, H = 700;
  const positions = useHierarchicalLayout(graphData.nodes, graphData.edges, W, H);

  const loadGraph = useCallback(async () => {
    try {
      const r = await api.get('/topology/graph', { timeout: 30000 });
      const d = r.data;
      if (d.error && !d.nodes?.length) throw new Error(d.error);
      setGraphData({ nodes: d.nodes || [], edges: d.edges || [] });
      setError(null);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadGraph(); }, [loadGraph]);

  const syncFromServers = async () => {
    setSyncing(true);
    setSyncMsg(null);
    try {
      const res = await api.post('/topology/sync-from-servers', {}, { timeout: 30000 });
      const data = res.data;
      if (data.error && !data.created && !data.updated) { setSyncMsg('ERRO: ' + data.error); return; }
      await loadGraph();
      setSyncMsg('OK: ' + (data.message || 'Sync concluido'));
    } catch (e) {
      setSyncMsg('ERRO: ' + (e.response?.data?.detail || e.message));
    } finally {
      setSyncing(false);
      setTimeout(() => setSyncMsg(null), 7000);
    }
  };

  const handleNodeClick = async (node) => {
    setSelected(node);
    setImpact(null);
    try {
      const r = await api.get('/topology/impact/' + node.id, { timeout: 15000 });
      // Enriquecer com vizinhos diretos do grafo local
      const neighbors = graphData.edges
        .filter(e => e.source === node.id || e.target === node.id)
        .map(e => e.source === node.id ? e.target : e.source);
      const uniqueNeighbors = [...new Set(neighbors)];
      setImpact({ ...r.data, direct_neighbors: uniqueNeighbors });
    } catch (_) {
      // Fallback: só vizinhos locais
      const neighbors = graphData.edges
        .filter(e => e.source === node.id || e.target === node.id)
        .map(e => e.source === node.id ? e.target : e.source);
      setImpact({ total_impact: 0, affected_hosts: [], depends_on: [], direct_neighbors: [...new Set(neighbors)] });
    }
  };

  const highlightedNodes = new Set();
  const highlightedEdges = new Set();
  const focusId = hovered?.id || selected?.id;
  if (focusId) {
    highlightedNodes.add(focusId);
    graphData.edges.forEach((e, i) => {
      if (e.source === focusId || e.target === focusId) {
        highlightedEdges.add(i);
        highlightedNodes.add(e.source);
        highlightedNodes.add(e.target);
      }
    });
  }
  const hasHighlight = highlightedNodes.size > 0;

  if (loading) return React.createElement('div', { className: 'topo-loading' }, 'Carregando topologia...');

  if (error || graphData.nodes.length === 0) {
    return (
      <div className="topo-wrap">
        <div className="topo-empty-card">
          <div className="topo-empty-icon">🕸️</div>
          <div className="topo-empty-title">Topologia nao configurada</div>
          <p className="topo-empty-desc">{error || 'Nenhum no cadastrado. Importe os servidores monitorados.'}</p>
          <button className="ds-btn ds-btn--primary" onClick={syncFromServers} disabled={syncing}>
            {syncing ? 'Sincronizando...' : 'Importar servidores monitorados'}
          </button>
          {syncMsg && <p style={{ marginTop: 12, fontSize: '0.85rem', color: '#94a3b8' }}>{syncMsg}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="topo-wrap">
      <div className="topo-toolbar">
        <button className="ds-btn ds-btn--ghost" onClick={syncFromServers} disabled={syncing} style={{ fontSize: 12 }}>
          {syncing ? 'Sincronizando...' : 'Sincronizar'}
        </button>
        <div style={{ display: 'flex', gap: 4, marginLeft: 8 }}>
          <button
            className={`ds-btn ${viewMode === 'graph' ? 'ds-btn--primary' : 'ds-btn--ghost'}`}
            style={{ fontSize: 12 }}
            onClick={() => setViewMode('graph')}
          >🕸️ Grafo</button>
          <button
            className={`ds-btn ${viewMode === 'list' ? 'ds-btn--primary' : 'ds-btn--ghost'}`}
            style={{ fontSize: 12 }}
            onClick={() => setViewMode('list')}
          >📋 Lista</button>
        </div>
        {syncMsg && <span style={{ fontSize: '0.8rem', color: '#94a3b8', marginLeft: 8 }}>{syncMsg}</span>}
        <span className="topo-stats">{graphData.nodes.length} nos - {graphData.edges.length} conexoes</span>
      </div>

      {viewMode === 'list' ? (
        <div style={{ padding: '16px 0' }}>
          <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              type="text"
              placeholder="Buscar por nome ou IP..."
              value={listSearch}
              onChange={e => setListSearch(e.target.value)}
              style={{
                background: '#1e293b', border: '1px solid #334155', borderRadius: 6,
                color: '#e2e8f0', padding: '6px 12px', fontSize: 13, width: 260,
                outline: 'none'
              }}
            />
            <span style={{ fontSize: 12, color: '#475569' }}>
              {graphData.nodes.filter(n => {
                const q = listSearch.toLowerCase();
                return !q || (n.name || '').toLowerCase().includes(q) || (n.metadata?.ip || '').includes(q);
              }).length} servidores
            </span>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #1e293b' }}>
                {['Status', 'Nome', 'IP', 'Tipo', 'Conexões'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '8px 12px', color: '#64748b', fontWeight: 600, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {graphData.nodes
                .filter(n => {
                  const q = listSearch.toLowerCase();
                  return !q || (n.name || '').toLowerCase().includes(q) || (n.metadata?.ip || '').includes(q);
                })
                .sort((a, b) => {
                  const order = { critical: 0, warning: 1, unknown: 2, ok: 3 };
                  return (order[a.status] ?? 2) - (order[b.status] ?? 2);
                })
                .map(node => {
                  const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
                  const connCount = graphData.edges.filter(e => e.source === node.id || e.target === node.id).length;
                  return (
                    <tr key={node.id}
                      style={{ borderBottom: '1px solid #0f172a', cursor: 'pointer', transition: 'background 0.15s' }}
                      onMouseEnter={e => e.currentTarget.style.background = '#1e293b'}
                      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                      onClick={() => { setViewMode('graph'); setSelected(node); handleNodeClick(node); }}
                    >
                      <td style={{ padding: '10px 12px' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                          <span style={{ width: 8, height: 8, borderRadius: '50%', background: color, boxShadow: `0 0 6px ${color}` }} />
                          <span style={{ color, fontSize: 11, fontWeight: 600 }}>{(node.status || 'unknown').toUpperCase()}</span>
                        </span>
                      </td>
                      <td style={{ padding: '10px 12px', color: '#e2e8f0', fontWeight: 500 }}>{node.name || node.id}</td>
                      <td style={{ padding: '10px 12px', color: '#94a3b8', fontFamily: 'monospace' }}>{node.metadata?.ip || '—'}</td>
                      <td style={{ padding: '10px 12px', color: '#64748b' }}>{node.metadata?.device_type || node.type || 'server'}</td>
                      <td style={{ padding: '10px 12px', color: '#64748b', textAlign: 'center' }}>{connCount}</td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="topo-main">
          <div className="topo-graph-card" style={{ overflowX: 'auto', overflowY: 'auto' }}>
          <svg viewBox={'0 0 ' + W + ' ' + H} width={W} height={H} className="topo-svg" aria-label="Grafo de topologia" style={{ minWidth: W, display: 'block' }}>
            <defs>
              {['dep','db','http','infra','hosts','network'].map(t => (
                <marker key={t} id={'arrow-' + t} markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
                  <path d="M0,0 L0,7 L7,3.5 z" fill="#334155" />
                </marker>
              ))}
              {graphData.nodes.map(node => {
                const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
                return (
                  <radialGradient key={'g-' + node.id} id={'grad-' + node.id} cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor={color} stopOpacity="0.25" />
                    <stop offset="100%" stopColor={color} stopOpacity="0.05" />
                  </radialGradient>
                );
              })}
            </defs>

            {/* Layer labels */}
            {[
              { y: 80,  label: 'Rede (L0)',       color: '#475569' },
              { y: 200, label: 'Hypervisors (L1)', color: '#6366f1' },
              { y: 340, label: 'Servidores (L2)',  color: '#0ea5e9' },
              { y: 500, label: 'Serviços (L3)',    color: '#22c55e' },
            ].map(({ y, label, color }) => (
              <g key={label}>
                <line x1={20} y1={y - 30} x2={W - 20} y2={y - 30} stroke={color} strokeOpacity="0.12" strokeWidth="1" strokeDasharray="4 4" />
                <text x={24} y={y - 16} fontSize="10" fill={color} fillOpacity="0.6" fontFamily="Inter, sans-serif" fontWeight="600" letterSpacing="0.05em">
                  {label}
                </text>
              </g>
            ))}
            {graphData.edges.map((e, i) => {
              const src = positions[e.source];
              const tgt = positions[e.target];
              if (!src || !tgt) return null;
              const isHighlighted = highlightedEdges.has(i);
              const isDimmed = hasHighlight && !isHighlighted;
              const color = EDGE_COLOR[e.type] || EDGE_COLOR.dependency;
              const mx = (src.x + tgt.x) / 2 + (tgt.y - src.y) * 0.15;
              const my = (src.y + tgt.y) / 2 - (tgt.x - src.x) * 0.15;
              return (
                <path key={i}
                  d={'M' + src.x + ',' + src.y + ' Q' + mx + ',' + my + ' ' + tgt.x + ',' + tgt.y}
                  fill="none" stroke={color}
                  strokeWidth={isHighlighted ? 2.5 : 1.5}
                  strokeOpacity={isDimmed ? 0.1 : isHighlighted ? 0.9 : 0.45}
                  markerEnd={'url(#arrow-' + (e.type || 'dep') + ')'}
                />
              );
            })}
            {graphData.nodes.map(node => {
              const pos = positions[node.id];
              if (!pos) return null;
              const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
              const isSelected = selected?.id === node.id;
              const isHovered = hovered?.id === node.id;
              const isDimmed = hasHighlight && !highlightedNodes.has(node.id);
              const isVM = node.type === 'vm';
              const r = isSelected ? 22 : isHovered ? 20 : isVM ? 13 : 18;
              return (
                <g key={node.id} className="topo-node"
                  onClick={() => handleNodeClick(node)}
                  onMouseEnter={() => setHovered(node)}
                  onMouseLeave={() => setHovered(null)}
                  style={{ cursor: 'pointer', opacity: isDimmed ? 0.25 : 1 }}
                  role="button" aria-label={'No: ' + node.name}
                >
                  {node.status === 'critical' && (
                    <circle cx={pos.x} cy={pos.y} r={r + 10} fill="none" stroke="#ef4444" strokeWidth="1" strokeOpacity="0.3" className="topo-pulse" />
                  )}
                  {isSelected && (
                    <circle cx={pos.x} cy={pos.y} r={r + 8} fill="none" stroke={color} strokeWidth="2" strokeOpacity="0.4" />
                  )}
                  <circle cx={pos.x} cy={pos.y} r={r} fill={'url(#grad-' + node.id + ')'} stroke={color} strokeWidth={isSelected ? 2.5 : 1.5} />
                  {/* Ícone SVG do tipo de dispositivo */}
                  <svg x={pos.x - (isVM ? 6 : 9)} y={pos.y - (isVM ? 8 : 11)} width={isVM ? 12 : 18} height={isVM ? 12 : 18} viewBox="0 0 24 24"
                    fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"
                    style={{ pointerEvents: 'none' }}>
                    <path d={getDeviceIcon(node)} />
                  </svg>
                  {/* Badge de status */}
                  <circle cx={pos.x + r - 4} cy={pos.y - r + 4} r={isVM ? 3 : 4.5} fill={color} stroke="#0d1117" strokeWidth="1.5" />
                  {/* Nome do nó */}
                  <text x={pos.x} y={pos.y + r + 11} textAnchor="middle" fontSize={isVM ? 7.5 : 9} fill={color} fontWeight="600" fontFamily="Inter, sans-serif" style={{ pointerEvents: 'none' }}>
                    {(node.name || '').substring(0, isVM ? 10 : 13)}
                  </text>
                  {!isVM && (
                    <text x={pos.x} y={pos.y + r + 21} textAnchor="middle" fontSize="7.5" fill="#475569" fontFamily="Inter, sans-serif" style={{ pointerEvents: 'none' }}>
                      {(node.name || '').toLowerCase().includes('udm') ? 'router' : (node.metadata?.device_type || node.type || 'server').toLowerCase()}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
          <div className="topo-legend">
            {Object.entries(STATUS_COLOR).map(([s, c]) => (
              <div key={s} className="topo-legend-item"><span className="topo-legend-dot" style={{ background: c }} />{s}</div>
            ))}
          </div>
        </div>
        <div className="topo-detail">
          {selected ? (
            <>
              <div className="topo-detail-title" style={{display:'flex', alignItems:'center', gap:10}}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={STATUS_COLOR[selected.status] || '#6b7280'} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d={getDeviceIcon(selected)} />
                </svg>
                {selected.name || selected.id}
              </div>
              <div className="topo-detail-row"><span>Tipo</span><strong>{(selected.name || '').toLowerCase().includes('udm') ? 'router' : (selected.metadata?.device_type || selected.type || 'server')}</strong></div>
              <div className="topo-detail-row">
                <span>Status</span>
                <strong style={{ color: STATUS_COLOR[selected.status] || '#9CA3AF' }}>{selected.status || 'unknown'}</strong>
              </div>
              {selected.metadata?.ip && <div className="topo-detail-row"><span>IP</span><strong>{selected.metadata.ip}</strong></div>}
              {selected.metadata?.hostname && selected.metadata.hostname !== selected.name && (
                <div className="topo-detail-row"><span>Hostname</span><strong>{selected.metadata.hostname}</strong></div>
              )}
              {/* HyperV Host details */}
              {selected.type === 'hypervisor' && selected.metadata?.health_score != null && (
                <div className="topo-detail-row"><span>Health Score</span><strong style={{color: selected.metadata.health_score >= 80 ? '#22c55e' : selected.metadata.health_score >= 50 ? '#f59e0b' : '#ef4444'}}>{selected.metadata.health_score.toFixed(1)}%</strong></div>
              )}
              {selected.type === 'hypervisor' && selected.metadata?.cpu_percent != null && (
                <div className="topo-detail-row"><span>CPU</span><strong>{selected.metadata.cpu_percent.toFixed(1)}%</strong></div>
              )}
              {selected.type === 'hypervisor' && selected.metadata?.memory_percent != null && (
                <div className="topo-detail-row"><span>RAM</span><strong>{selected.metadata.memory_percent.toFixed(1)}%</strong></div>
              )}
              {selected.type === 'hypervisor' && selected.metadata?.storage_percent != null && (
                <div className="topo-detail-row"><span>Storage</span><strong>{selected.metadata.storage_percent.toFixed(1)}%</strong></div>
              )}
              {selected.type === 'hypervisor' && selected.metadata?.vm_count != null && (
                <div className="topo-detail-row"><span>VMs</span><strong>{selected.metadata.running_vm_count ?? 0} / {selected.metadata.vm_count} rodando</strong></div>
              )}
              {selected.type === 'hypervisor' && selected.metadata?.total_cpus != null && (
                <div className="topo-detail-row"><span>CPUs</span><strong>{selected.metadata.total_cpus} cores</strong></div>
              )}
              {selected.type === 'hypervisor' && selected.metadata?.total_memory_gb != null && (
                <div className="topo-detail-row"><span>RAM Total</span><strong>{selected.metadata.total_memory_gb.toFixed(0)} GB</strong></div>
              )}
              {selected.type === 'hypervisor' && selected.metadata?.model && (
                <div className="topo-detail-row"><span>Modelo</span><strong>{selected.metadata.model}</strong></div>
              )}
              {/* HyperV VM details */}
              {selected.type === 'vm' && selected.metadata?.vm_state && (
                <div className="topo-detail-row"><span>Estado</span><strong style={{color: selected.metadata.vm_state === 'Running' ? '#22c55e' : '#94a3b8'}}>{selected.metadata.vm_state}</strong></div>
              )}
              {selected.type === 'vm' && selected.metadata?.vcpus != null && (
                <div className="topo-detail-row"><span>vCPUs</span><strong>{selected.metadata.vcpus}</strong></div>
              )}
              {selected.type === 'vm' && selected.metadata?.memory_mb != null && (
                <div className="topo-detail-row"><span>RAM</span><strong>{(selected.metadata.memory_mb / 1024).toFixed(1)} GB</strong></div>
              )}
              {selected.type === 'vm' && selected.metadata?.cpu_percent != null && (
                <div className="topo-detail-row"><span>CPU</span><strong>{selected.metadata.cpu_percent.toFixed(1)}%</strong></div>
              )}
              {selected.type === 'vm' && selected.metadata?.memory_percent != null && (
                <div className="topo-detail-row"><span>RAM Uso</span><strong>{selected.metadata.memory_percent.toFixed(1)}%</strong></div>
              )}
              <div className="topo-detail-section-title">Blast Radius</div>
              <div className="topo-blast-grid">
                <div className="topo-blast-item">
                  <div className="topo-blast-value">{impact?.total_impact > 0 ? impact.total_impact : (impact?.direct_neighbors?.length ?? '—')}</div>
                  <div className="topo-blast-label">Impacto</div>
                </div>
                <div className="topo-blast-item">
                  <div className="topo-blast-value">{impact?.affected_hosts?.length > 0 ? impact.affected_hosts.length : (impact?.direct_neighbors?.filter(id => { const n = graphData.nodes.find(x => x.id === id); return n?.type === 'server' || n?.type === 'host'; }).length ?? '—')}</div>
                  <div className="topo-blast-label">Hosts</div>
                </div>
                <div className="topo-blast-item">
                  <div className="topo-blast-value">{impact?.depends_on?.length ?? 0}</div>
                  <div className="topo-blast-label">Depende de</div>
                </div>
                <div className="topo-blast-item">
                  <div className="topo-blast-value">{impact?.direct_neighbors?.length ?? graphData.edges.filter(e => e.source === selected?.id || e.target === selected?.id).length}</div>
                  <div className="topo-blast-label">Conexões</div>
                </div>
              </div>
              {impact && impact.total_impact === 0 && (
                <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: 8 }}>
                  Nenhum nó downstream detectado. Este servidor não tem dependentes diretos no grafo.
                </div>
              )}
              {impact?.all_affected?.length > 0 && (
                <>
                  <div className="topo-detail-section-title" style={{ marginTop: 12 }}>Nós Afetados</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', maxHeight: 80, overflowY: 'auto' }}>
                    {impact.all_affected.slice(0, 8).map(id => {
                      const n = graphData.nodes.find(x => x.id === id);
                      return <div key={id} style={{ padding: '2px 0' }}>• {n?.name || id}</div>;
                    })}
                    {impact.all_affected.length > 8 && <div>+{impact.all_affected.length - 8} mais...</div>}
                  </div>
                </>
              )}
              {impact?.direct_neighbors?.length > 0 && (
                <>
                  <div className="topo-detail-section-title" style={{ marginTop: 12 }}>Conexões Diretas ({impact.direct_neighbors.length})</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', maxHeight: 100, overflowY: 'auto' }}>
                    {impact.direct_neighbors.map(id => {
                      const n = graphData.nodes.find(x => x.id === id);
                      const c = STATUS_COLOR[n?.status] || '#6b7280';
                      return (
                        <div key={id} style={{ padding: '3px 0', display: 'flex', alignItems: 'center', gap: 6 }}>
                          <span style={{ width: 6, height: 6, borderRadius: '50%', background: c, flexShrink: 0 }} />
                          <span>{n?.name || id}</span>
                          <span style={{ color: '#475569', fontSize: '0.7rem' }}>{n?.metadata?.device_type || n?.type || ''}</span>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="topo-detail-hint">Clique em um no para ver detalhes</div>
          )}
        </div>
      </div>
      )}
    </div>
  );
}