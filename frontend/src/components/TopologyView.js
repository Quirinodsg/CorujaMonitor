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

const EDGE_COLOR = {
  dependency: '#334155',
  database: '#6366f1',
  http: '#0ea5e9',
  infrastructure: '#1e293b',
};

function useForceLayout(nodes, edges, width = 900, height = 480) {
  const [positions, setPositions] = React.useState({});
  React.useEffect(() => {
    if (!nodes.length) return;
    const pos = {};
    const cx = width / 2, cy = height / 2;
    const r = Math.min(width, height) * 0.35;
    nodes.forEach((n, i) => {
      const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
      pos[n.id] = {
        x: cx + r * Math.cos(angle) + (Math.random() - 0.5) * 20,
        y: cy + r * Math.sin(angle) + (Math.random() - 0.5) * 20,
      };
    });
    const k = Math.sqrt((width * height) / Math.max(nodes.length, 1));
    const repulse = (d) => (k * k) / Math.max(d, 1);
    const attract = (d) => (d * d) / k;
    let current = { ...pos };
    for (let iter = 0; iter < 80; iter++) {
      const disp = {};
      nodes.forEach(n => { disp[n.id] = { x: 0, y: 0 }; });
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const u = nodes[i].id, v = nodes[j].id;
          const dx = current[u].x - current[v].x;
          const dy = current[u].y - current[v].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
          const force = repulse(dist);
          disp[u].x += (dx / dist) * force;
          disp[u].y += (dy / dist) * force;
          disp[v].x -= (dx / dist) * force;
          disp[v].y -= (dy / dist) * force;
        }
      }
      edges.forEach(e => {
        const u = e.source, v = e.target;
        if (!current[u] || !current[v]) return;
        const dx = current[u].x - current[v].x;
        const dy = current[u].y - current[v].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 0.01;
        const force = attract(dist);
        disp[u].x -= (dx / dist) * force;
        disp[u].y -= (dy / dist) * force;
        disp[v].x += (dx / dist) * force;
        disp[v].y += (dy / dist) * force;
      });
      const temp = Math.max(5, 50 * (1 - iter / 80));
      nodes.forEach(n => {
        const d = disp[n.id];
        const mag = Math.sqrt(d.x * d.x + d.y * d.y) || 0.01;
        const capped = Math.min(mag, temp);
        current[n.id] = {
          x: Math.max(40, Math.min(width - 40, current[n.id].x + (d.x / mag) * capped)),
          y: Math.max(40, Math.min(height - 40, current[n.id].y + (d.y / mag) * capped)),
        };
      });
    }
    setPositions(current);
  }, [nodes.length, edges.length, width, height]);
  return positions;
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

  const W = 900, H = 480;
  const positions = useForceLayout(graphData.nodes, graphData.edges, W, H);

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
      setImpact(r.data);
    } catch (_) {}
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
        {syncMsg && <span style={{ fontSize: '0.8rem', color: '#94a3b8', marginLeft: 8 }}>{syncMsg}</span>}
        <span className="topo-stats">{graphData.nodes.length} nos - {graphData.edges.length} conexoes</span>
      </div>
      <div className="topo-main">
        <div className="topo-graph-card">
          <svg viewBox={'0 0 ' + W + ' ' + H} className="topo-svg" aria-label="Grafo de topologia">
            <defs>
              {['dep','db','http','infra'].map(t => (
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
              const r = isSelected ? 26 : isHovered ? 24 : 20;
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
                  <circle cx={pos.x + r - 5} cy={pos.y - r + 5} r="4.5" fill={color} stroke="#0d1117" strokeWidth="1.5" />
                  <text x={pos.x} y={pos.y + 4} textAnchor="middle" fontSize="9" fill={color} fontWeight="600" fontFamily="Inter, sans-serif" style={{ pointerEvents: 'none' }}>
                    {(node.name || '').substring(0, 13)}
                  </text>
                  <text x={pos.x} y={pos.y + 38} textAnchor="middle" fontSize="8" fill="#475569" fontFamily="Inter, sans-serif" style={{ pointerEvents: 'none' }}>
                    {node.type}
                  </text>
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
              <div className="topo-detail-title">{selected.name || selected.id}</div>
              <div className="topo-detail-row"><span>Tipo</span><strong>{selected.type || '-'}</strong></div>
              <div className="topo-detail-row">
                <span>Status</span>
                <strong style={{ color: STATUS_COLOR[selected.status] || '#9CA3AF' }}>{selected.status || 'unknown'}</strong>
              </div>
              {selected.metadata?.ip && <div className="topo-detail-row"><span>IP</span><strong>{selected.metadata.ip}</strong></div>}
              {impact && (
                <>
                  <div className="topo-detail-section-title">Blast Radius</div>
                  <div className="topo-blast-grid">
                    <div className="topo-blast-item"><div className="topo-blast-value">{impact.total_impact || 0}</div><div className="topo-blast-label">Impacto</div></div>
                    <div className="topo-blast-item"><div className="topo-blast-value">{impact.affected_hosts?.length || 0}</div><div className="topo-blast-label">Hosts</div></div>
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="topo-detail-hint">Clique em um no para ver detalhes</div>
          )}
        </div>
      </div>
    </div>
  );
}