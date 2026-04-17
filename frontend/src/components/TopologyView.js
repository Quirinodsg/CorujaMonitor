// TopologyView v3 - layout hierárquico multi-linha com zoom/pan e filtros
import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
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
  hosts: '#6366f1',
  network: '#334155',
};

// ── Layout hierárquico multi-linha ──────────────────────────────────────────
const MAX_PER_ROW = 8;
const NODE_SPACING_X = 130;  // espaço entre nós na mesma linha
const VM_SPACING_X = 80;     // espaço entre VMs (menores)
const ROW_HEIGHT = 120;
const LAYER_GAP = 50;
const PADDING_X = 120;       // margem lateral para não cortar labels

const LAYER_CONFIG = [
  { layer: 0, label: 'REDE',        color: '#64748b' },
  { layer: 1, label: 'HYPERVISORS', color: '#6366f1' },
  { layer: 2, label: 'SERVIDORES',  color: '#0ea5e9' },
  { layer: 3, label: 'SERVIÇOS',    color: '#22c55e' },
];

function buildHierarchicalLayout(nodes) {
  const pos = {};
  let currentY = 80;

  // Separar VMs HyperV — ficam agrupadas sob o host
  const hvVmIds = new Set(
    nodes.filter(n => n.type === 'vm' && n.parent_id?.startsWith('hv_host_')).map(n => n.id)
  );

  // Calcular largura total necessária para centralizar
  const maxLayerNodes = Math.max(
    ...LAYER_CONFIG.map(({ layer }) =>
      Math.min(MAX_PER_ROW, nodes.filter(n => (n.layer ?? 2) === layer && !hvVmIds.has(n.id)).length)
    ), 1
  );
  const canvasW = PADDING_X * 2 + (maxLayerNodes - 1) * NODE_SPACING_X;
  const centerX = canvasW / 2;

  LAYER_CONFIG.forEach(({ layer }) => {
    const layerNodes = nodes.filter(n => (n.layer ?? 2) === layer && !hvVmIds.has(n.id));
    if (!layerNodes.length) return;

    const rows = Math.ceil(layerNodes.length / MAX_PER_ROW);
    for (let row = 0; row < rows; row++) {
      const rowNodes = layerNodes.slice(row * MAX_PER_ROW, (row + 1) * MAX_PER_ROW);
      const rowTotalW = (rowNodes.length - 1) * NODE_SPACING_X;
      const rowStartX = centerX - rowTotalW / 2;
      rowNodes.forEach((n, i) => {
        pos[n.id] = { x: rowStartX + i * NODE_SPACING_X, y: currentY };
      });
      currentY += ROW_HEIGHT;
    }
    currentY += LAYER_GAP;

    // VMs HyperV: posicionar em grid abaixo do host pai
    if (layer === 1) {
      const VM_MAX_PER_ROW = 8;
      layerNodes.forEach(hostNode => {
        const hostPos = pos[hostNode.id];
        if (!hostPos) return;
        const vms = nodes.filter(n => n.parent_id === hostNode.id && hvVmIds.has(n.id));
        if (!vms.length) return;

        const vmRows = Math.ceil(vms.length / VM_MAX_PER_ROW);
        let vmY = hostPos.y + ROW_HEIGHT - 10;
        for (let vrow = 0; vrow < vmRows; vrow++) {
          const rowVms = vms.slice(vrow * VM_MAX_PER_ROW, (vrow + 1) * VM_MAX_PER_ROW);
          const rowW = (rowVms.length - 1) * VM_SPACING_X;
          const rowStartX = hostPos.x - rowW / 2;
          rowVms.forEach((vm, i) => {
            pos[vm.id] = { x: rowStartX + i * VM_SPACING_X, y: vmY };
          });
          vmY += 85;
        }
        // Avançar currentY se as VMs ultrapassarem
        const vmBottom = hostPos.y + ROW_HEIGHT - 10 + vmRows * 85;
        if (vmBottom > currentY) currentY = vmBottom + LAYER_GAP;
      });
      currentY += LAYER_GAP;
    }
  });

  // Fallback para nós sem posição
  nodes.forEach((n, i) => {
    if (!pos[n.id]) pos[n.id] = { x: centerX + (i % MAX_PER_ROW - MAX_PER_ROW/2) * NODE_SPACING_X, y: currentY };
  });

  return { pos, canvasW };
}

function computeCanvasSize(pos, canvasW) {
  const xs = Object.values(pos).map(p => p.x);
  const ys = Object.values(pos).map(p => p.y);
  if (!xs.length) return { w: 1200, h: 600 };
  return {
    w: Math.max(canvasW, Math.max(...xs) + PADDING_X),
    h: Math.max(500, Math.max(...ys) + 120),
  };
}

// ── Filtros de tipo ──────────────────────────────────────────────────────────
const TYPE_FILTERS = [
  { key: 'network',    label: 'Rede',       types: ['switch','router','firewall','gateway','ap'] },
  { key: 'hypervisor', label: 'Hypervisors',types: ['hypervisor'] },
  { key: 'vm',         label: 'VMs',        types: ['vm'] },
  { key: 'server',     label: 'Servidores', types: ['server','host'] },
  { key: 'service',    label: 'Serviços',   types: ['service','application'] },
];

export default function TopologyView() {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [selected, setSelected] = useState(null);
  const [hovered, setHovered] = useState(null);
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState(null);
  const [viewMode, setViewMode] = useState('graph');
  const [listSearch, setListSearch] = useState('');
  const [activeFilters, setActiveFilters] = useState(new Set(['network','hypervisor','vm','server','service']));

  // Zoom/pan state
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const svgRef = useRef(null);
  const isPanning = useRef(false);
  const panStart = useRef({ x: 0, y: 0 });

  // Filtrar nós pelos filtros ativos
  const visibleNodes = useMemo(() => {
    return graphData.nodes.filter(n => {
      const t = (n.metadata?.device_type || n.type || 'server').toLowerCase();
      return TYPE_FILTERS.some(f => activeFilters.has(f.key) && f.types.some(ft => t.includes(ft)));
    });
  }, [graphData.nodes, activeFilters]);

  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map(n => n.id)), [visibleNodes]);

  const visibleEdges = useMemo(() => {
    return graphData.edges.filter(e => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target));
  }, [graphData.edges, visibleNodeIds]);

  // Layout
  const { pos: positions, canvasW } = useMemo(() => buildHierarchicalLayout(visibleNodes), [visibleNodes]);
  const { w: W, h: H } = useMemo(() => computeCanvasSize(positions, canvasW), [positions, canvasW]);

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
    visibleEdges.forEach((e, i) => {
      if (e.source === focusId || e.target === focusId) {
        highlightedEdges.add(i);
        highlightedNodes.add(e.source);
        highlightedNodes.add(e.target);
      }
    });
  }
  const hasHighlight = highlightedNodes.size > 0;

  // Zoom/pan handlers
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setTransform(t => ({
      ...t,
      scale: Math.max(0.3, Math.min(3, t.scale * delta)),
    }));
  }, []);

  const handleMouseDown = useCallback((e) => {
    if (e.button !== 0) return;
    isPanning.current = true;
    panStart.current = { x: e.clientX - transform.x, y: e.clientY - transform.y };
  }, [transform]);

  const handleMouseMove = useCallback((e) => {
    if (!isPanning.current) return;
    setTransform(t => ({ ...t, x: e.clientX - panStart.current.x, y: e.clientY - panStart.current.y }));
  }, []);

  const handleMouseUp = useCallback(() => { isPanning.current = false; }, []);

  const resetView = () => setTransform({ x: 0, y: 0, scale: 1 });

  const toggleFilter = (key) => {
    setActiveFilters(prev => {
      const next = new Set(prev);
      if (next.has(key)) { if (next.size > 1) next.delete(key); }
      else next.add(key);
      return next;
    });
  };

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
          <button className={`ds-btn ${viewMode === 'graph' ? 'ds-btn--primary' : 'ds-btn--ghost'}`} style={{ fontSize: 12 }} onClick={() => setViewMode('graph')}>🕸️ Grafo</button>
          <button className={`ds-btn ${viewMode === 'list' ? 'ds-btn--primary' : 'ds-btn--ghost'}`} style={{ fontSize: 12 }} onClick={() => setViewMode('list')}>📋 Lista</button>
        </div>
        {/* Filtros de tipo */}
        {viewMode === 'graph' && (
          <div style={{ display: 'flex', gap: 4, marginLeft: 12, flexWrap: 'wrap' }}>
            {TYPE_FILTERS.map(f => (
              <button key={f.key}
                onClick={() => toggleFilter(f.key)}
                style={{
                  fontSize: 11, padding: '3px 8px', borderRadius: 6, border: '1px solid',
                  borderColor: activeFilters.has(f.key) ? '#6366f1' : '#334155',
                  background: activeFilters.has(f.key) ? 'rgba(99,102,241,0.15)' : 'transparent',
                  color: activeFilters.has(f.key) ? '#a5b4fc' : '#64748b',
                  cursor: 'pointer', transition: 'all 0.15s',
                }}
              >{f.label}</button>
            ))}
          </div>
        )}
        {viewMode === 'graph' && (
          <button onClick={resetView} style={{ fontSize: 11, padding: '3px 8px', borderRadius: 6, border: '1px solid #334155', background: 'transparent', color: '#64748b', cursor: 'pointer', marginLeft: 4 }}>
            ⟳ Reset zoom
          </button>
        )}
        {syncMsg && <span style={{ fontSize: '0.8rem', color: '#94a3b8', marginLeft: 8 }}>{syncMsg}</span>}
        <span className="topo-stats">{visibleNodes.length}/{graphData.nodes.length} nós · {visibleEdges.length} conexões</span>
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
          <div className="topo-graph-card"
            style={{ overflow: 'hidden', cursor: isPanning.current ? 'grabbing' : 'grab', userSelect: 'none' }}
            onWheel={handleWheel}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
          <svg
            ref={svgRef}
            viewBox={`0 0 ${W} ${H}`}
            width="100%" height={Math.min(H, 680)}
            className="topo-svg"
            aria-label="Grafo de topologia"
            style={{ display: 'block', minHeight: 400 }}
          >
            <defs>
              {['dep','db','http','infra','hosts','network'].map(t => (
                <marker key={t} id={'arrow-' + t} markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                  <path d="M0,0 L0,6 L6,3 z" fill="#334155" opacity="0.6" />
                </marker>
              ))}
              {visibleNodes.map(node => {
                const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
                return (
                  <radialGradient key={'g-' + node.id} id={'grad-' + node.id} cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor={color} stopOpacity="0.3" />
                    <stop offset="100%" stopColor={color} stopOpacity="0.05" />
                  </radialGradient>
                );
              })}
            </defs>

            <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>

            {/* Layer bands */}
            {(() => {
              // Calcular faixas Y reais baseadas nas posições
              const bands = {};
              visibleNodes.forEach(n => {
                const layer = n.layer ?? 2;
                const p = positions[n.id];
                if (!p) return;
                if (!bands[layer]) bands[layer] = { minY: p.y, maxY: p.y };
                bands[layer].minY = Math.min(bands[layer].minY, p.y);
                bands[layer].maxY = Math.max(bands[layer].maxY, p.y);
              });
              return LAYER_CONFIG.map(({ layer, label, color }) => {
                const b = bands[layer];
                if (!b) return null;
                const y1 = b.minY - 45;
                const y2 = b.maxY + 45;
                return (
                  <g key={layer}>
                    <rect x={10} y={y1} width={W - 20} height={y2 - y1}
                      fill={color} fillOpacity="0.03" rx="8"
                      stroke={color} strokeOpacity="0.08" strokeWidth="1" />
                    <text x={20} y={y1 + 14} fontSize="9.5" fill={color} fillOpacity="0.7"
                      fontFamily="Inter, sans-serif" fontWeight="700" letterSpacing="0.08em">
                      {label.toUpperCase()}
                    </text>
                  </g>
                );
              });
            })()}

            {/* Edges */}
            {visibleEdges.map((e, i) => {
              const src = positions[e.source];
              const tgt = positions[e.target];
              if (!src || !tgt) return null;
              const isHighlighted = highlightedEdges.has(i);
              const isDimmed = hasHighlight && !isHighlighted;
              // Arestas hosts (hypervisor→VM) só aparecem no hover
              const isHostsEdge = e.type === 'hosts';
              if (isHostsEdge && !isHighlighted) return null;
              if (isDimmed) return null;
              const color = EDGE_COLOR[e.type] || EDGE_COLOR.dependency;
              const mx = (src.x + tgt.x) / 2 + (tgt.y - src.y) * 0.1;
              const my = (src.y + tgt.y) / 2 - (tgt.x - src.x) * 0.1;
              return (
                <path key={i}
                  d={`M${src.x},${src.y} Q${mx},${my} ${tgt.x},${tgt.y}`}
                  fill="none" stroke={color}
                  strokeWidth={isHighlighted ? 2 : 1}
                  strokeOpacity={isHighlighted ? 0.85 : 0.2}
                  markerEnd={`url(#arrow-${e.type || 'dep'})`}
                />
              );
            })}

            {/* Nodes */}
            {visibleNodes.map(node => {
              const pos = positions[node.id];
              if (!pos) return null;
              const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
              const isSelected = selected?.id === node.id;
              const isHovered = hovered?.id === node.id;
              const isDimmed = hasHighlight && !highlightedNodes.has(node.id);
              const isVM = node.type === 'vm';
              const isHypervisor = node.type === 'hypervisor';
              const r = isSelected ? 24 : isHovered ? 22 : isVM ? 14 : isHypervisor ? 22 : 18;
              const iconSize = isVM ? 11 : 16;
              return (
                <g key={node.id} className="topo-node"
                  onClick={() => handleNodeClick(node)}
                  onMouseEnter={() => setHovered(node)}
                  onMouseLeave={() => setHovered(null)}
                  style={{ cursor: 'pointer', opacity: isDimmed ? 0.15 : 1, transition: 'opacity 0.2s' }}
                  role="button" aria-label={'Nó: ' + node.name}
                >
                  {node.status === 'critical' && (
                    <circle cx={pos.x} cy={pos.y} r={r + 8} fill="none" stroke="#ef4444" strokeWidth="1" strokeOpacity="0.3" className="topo-pulse" />
                  )}
                  {isSelected && (
                    <circle cx={pos.x} cy={pos.y} r={r + 6} fill="none" stroke={color} strokeWidth="2" strokeOpacity="0.5" />
                  )}
                  <circle cx={pos.x} cy={pos.y} r={r} fill={`url(#grad-${node.id})`} stroke={color} strokeWidth={isSelected ? 2.5 : isHypervisor ? 2 : 1.5} />
                  <svg x={pos.x - iconSize/2} y={pos.y - iconSize/2 - 2} width={iconSize} height={iconSize} viewBox="0 0 24 24"
                    fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"
                    style={{ pointerEvents: 'none' }}>
                    <path d={getDeviceIcon(node)} />
                  </svg>
                  <circle cx={pos.x + r - 4} cy={pos.y - r + 4} r={isVM ? 3 : 4} fill={color} stroke="#0d1117" strokeWidth="1.5" />
                  <text x={pos.x} y={pos.y + r + 12} textAnchor="middle"
                    fontSize={isVM ? 7 : isHypervisor ? 9.5 : 8.5}
                    fill={isHypervisor ? color : '#cbd5e1'}
                    fontWeight={isHypervisor ? '700' : '500'}
                    fontFamily="Inter, sans-serif" style={{ pointerEvents: 'none' }}>
                    {(node.name || '').substring(0, isVM ? 9 : 14)}
                  </text>
                  {isHypervisor && node.metadata?.vm_count != null && (
                    <text x={pos.x} y={pos.y + r + 23} textAnchor="middle" fontSize="7.5" fill="#6366f1" fillOpacity="0.8" fontFamily="Inter, sans-serif" style={{ pointerEvents: 'none' }}>
                      {node.metadata.running_vm_count ?? 0}/{node.metadata.vm_count} VMs
                    </text>
                  )}
                </g>
              );
            })}
            </g>
          </svg>
          <div className="topo-legend">
            {Object.entries(STATUS_COLOR).map(([s, c]) => (
              <div key={s} className="topo-legend-item"><span className="topo-legend-dot" style={{ background: c }} />{s}</div>
            ))}
            <div className="topo-legend-sep" />
            <div className="topo-legend-item" style={{ fontSize: 10, color: '#475569' }}>Scroll = zoom · Drag = mover</div>
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