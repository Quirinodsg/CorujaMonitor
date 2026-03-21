import React, { useState, useEffect, useRef, useCallback } from 'react';
import './TopologyView.css';

const API = process.env.REACT_APP_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`;

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

// ─── Force-directed layout (Fruchterman-Reingold simplificado) ───────────────
function useForceLayout(nodes, edges, width = 900, height = 480) {
  const [positions, setPositions] = useState({});

  useEffect(() => {
    if (!nodes.length) return;

    // Posição inicial: círculo
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
    const edgeSet = new Set(edges.map(e => `${e.source}|${e.target}`));

    const repulse = (d) => (k * k) / Math.max(d, 1);
    const attract = (d) => (d * d) / k;

    let current = { ...pos };

    for (let iter = 0; iter < 80; iter++) {
      const disp = {};
      nodes.forEach(n => { disp[n.id] = { x: 0, y: 0 }; });

      // Repulsão entre todos os pares
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

      // Atração pelas edges
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

      // Temperatura decrescente
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

// ─── Component ───────────────────────────────────────────────────────────────
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
    const token = localStorage.getItem('token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    try {
      const r = await fetch(`${API}/api/v1/topology/graph`, { headers });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      if (d.error && !d.nodes?.length) throw new Error(d.error);
      setGraphData({ nodes: d.nodes || [], edges: d.edges || [] });
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadGraph(); }, [loadGraph]);

  const syncFromServers = async () => {
    setSyncing(true);
    setSyncMsg(null);
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };
      const res = await fetch(`${API}/api/v1/topology/sync-from-servers`, { method: 'POST', headers });
      const data = await res.json();
      if (data.error && !data.created && !data.updated) {
        setSyncMsg(`❌ ${data.error}`);
        return;
      }
      await loadGraph();
      setSyncMsg(`✅ ${data.message || 'Sync concluído'}`);
    } catch (e) {
      setSyncMsg(`❌ ${e.message}`);
    } finally {
      setSyncing(false);
      setTimeout(() => setSyncMsg(null), 7000);
    }
  };

  const handleNodeClick = async (node) => {
    setSelected(node);
    setImpact(null);
    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const r = await fetch(`${API}/api/v1/topology/impact/${node.id}`, { headers });
      if (r.ok) setImpact(await r.json());
    } catch (_) {}
  };

  // Nós conectados ao hovered/selected (para highlight)
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

  if (loading) return <div className="topo-loading">Carregando topologia...</div>;

  if (error || graphData.nodes.length === 0) {
    return (
      <div className="topo-wrap">
        <div className="topo-empty-card">
          <div className="topo-empty-icon">🕸️</div>
          <div className="topo-empty-title">Topologia não configurada</div>
          <p className="topo-empty-desc">
            {error || 'Nenhum nó cadastrado. Importe os servidores monitorados para gerar o grafo.'}
          </p>
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
          {syncing ? 'Sincronizando...' : '↺ Sincronizar'}
        </button>
        {syncMsg && <span style={{ fontSize: '0.8rem', color: '#94a3b8', marginLeft: 8 }}>{syncMsg}</span>}
        <span className="topo-stats">
          {graphData.nodes.length} nós · {graphData.edges.length} conexões
        </span>
      </div>

      <div className="topo-main">
        <div className="topo-graph-card">
          <svg viewBox={`0 0 ${W} ${H}`} className="topo-svg" aria-label="Grafo de topologia">
            <defs>
              <marker id="arrow-dep" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
                <path d="M0,0 L0,7 L7,3.5 z" fill={EDGE_COLOR.dependency} />
              </marker>
              <marker id="arrow-db" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
                <path d="M0,0 L0,7 L7,3.5 z" fill={EDGE_COLOR.database} />
              </marker>
              <marker id="arrow-http" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
                <path d="M0,0 L0,7 L7,3.5 z" fill={EDGE_COLOR.http} />
              </marker>
              <marker id="arrow-infra" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
                <path d="M0,0 L0,7 L7,3.5 z" fill={EDGE_COLOR.infrastructure} />
              </marker>
              {graphData.nodes.map(node => {
                const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
                return (
                  <radialGradient key={`g-${node.id}`} id={`grad-${node.id}`} cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor={color} stopOpacity="0.25" />
                    <stop offset="100%" stopColor={color} stopOpacity="0.05" />
                  </radialGradient>
                );
              })}
            </defs>

            {/* Edges */}
            {graphData.edges.map((e, i) => {
              const src = positions[e.source];
              const tgt = positions[e.target];
              if (!src || !tgt) return null;

              const isHighlighted = highlightedEdges.has(i);
              const isDimmed = hasHighlight && !isHighlighted;
              const color = EDGE_COLOR[e.type] || EDGE_COLOR.dependency;
              const markerId = `arrow-${e.type || 'dep'}`;

              // Curva suave
              const mx = (src.x + tgt.x) / 2 + (tgt.y - src.y) * 0.15;
              const my = (src.y + tgt.y) / 2 - (tgt.x - src.x) * 0.15;

              return (
                <path
                  key={i}
                  d={`M${src.x},${src.y} Q${mx},${my} ${tgt.x},${tgt.y}`}
                  fill="none"
                  stroke={color}
                  strokeWidth={isHighlighted ? 2.5 : 1.5}
                  strokeOpacity={isDimmed ? 0.1 : isHighlighted ? 0.9 : 0.45}
                  markerEnd={`url(#${markerId})`}
                  style={{ transition: 'stroke-opacity 0.2s' }}
                />
              );
            })}

            {/* Nodes */}
            {graphData.nodes.map(node => {
              const pos = positions[node.id];
              if (!pos) return null;
              const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
              const isSelected = selected?.id === node.id;
              const isHovered = hovered?.id === node.id;
              const isDimmed = hasHighlight && !highlightedNodes.has(node.id);
              const r = isSelected ? 26 : isHovered ? 24 : 20;

              return (
                <g
                  key={node.id}
                  className="topo-node"
                  onClick={() => handleNodeClick(node)}
                  onMouseEnter={() => setHovered(node)}
                  onMouseLeave={() => setHovered(null)}
                  style={{ cursor: 'pointer', opacity: isDimmed ? 0.25 : 1, transition: 'opacity 0.2s' }}
                  role="button"
                  aria-label={`Nó: ${node.name}`}
                >
                  {/* Pulse ring para critical */}
                  {node.status === 'critical' && (
                    <circle cx={pos.x} cy={pos.y} r={r + 10}
                      fill="none" stroke="#ef4444" strokeWidth="1"
                      strokeOpacity="0.3" className="topo-pulse" />
                  )}
                  {/* Glow para selected */}
                  {isSelected && (
                    <circle cx={pos.x} cy={pos.y} r={r + 8}
                      fill="none" stroke={color} strokeWidth="2" strokeOpacity="0.4" />
                  )}
                  {/* Background */}
                  <circle cx={pos.x} cy={pos.y} r={r}
                    fill={`url(#grad-${node.id})`}
                    stroke={color}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                  />
                  {/* Status dot */}
                  <circle cx={pos.x + r - 5} cy={pos.y - r + 5} r="4.5"
                    fill={color} stroke="#0d1117" strokeWidth="1.5" />
                  {/* Label */}
                  <text x={pos.x} y={pos.y + 4} textAnchor="middle"
                    fontSize="9" fill={color} fontWeight="600" fontFamily="Inter, sans-serif"
                    style={{ pointerEvents: 'none' }}>
                    {(node.name || '').substring(0, 13)}
                  </text>
                  <text x={pos.x} y={pos.y + 38} textAnchor="middle"
                    fontSize="8" fill="#475569" fontFamily="Inter, sans-serif"
                    style={{ pointerEvents: 'none' }}>
                    {node.type}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Legend */}
          <div className="topo-legend">
            {Object.entries(STATUS_COLOR).map(([s, c]) => (
              <div key={s} className="topo-legend-item">
                <span className="topo-legend-dot" style={{ background: c }} />{s}
              </div>
            ))}
            <div className="topo-legend-sep" />
            {Object.entries(EDGE_COLOR).map(([t, c]) => (
              <div key={t} className="topo-legend-item">
                <span className="topo-legend-line" style={{ background: c }} />{t}
              </div>
            ))}
          </div>
        </div>

        {/* Detail panel */}
        <div className="topo-detail">
          {selected ? (
            <>
              <div className="topo-detail-title">{selected.name || selected.id}</div>
              <div className="topo-detail-row"><span>Tipo</span><strong>{selected.type || '—'}</strong></div>
              <div className="topo-detail-row">
                <span>Status</span>
                <strong style={{ color: STATUS_COLOR[selected.status] || '#9CA3AF' }}>
                  {selected.status || 'unknown'}
                </strong>
              </div>
              {selected.metadata?.ip && (
                <div className="topo-detail-row"><span>IP</span><strong>{selected.metadata.ip}</strong></div>
              )}
              {selected.metadata?.os_type && (
                <div className="topo-detail-row"><span>OS</span><strong>{selected.metadata.os_type}</strong></div>
              )}

              {impact && (
                <>
                  <div className="topo-detail-section-title">Blast Radius</div>
                  <div className="topo-blast-grid">
                    <div className="topo-blast-item">
                      <div className="topo-blast-value">{impact.total_impact || 0}</div>
                      <div className="topo-blast-label">Impacto Total</div>
                    </div>
                    <div className="topo-blast-item">
                      <div className="topo-blast-value">{impact.affected_hosts?.length || 0}</div>
                      <div className="topo-blast-label">Hosts</div>
                    </div>
                    <div className="topo-blast-item">
                      <div className="topo-blast-value">{impact.affected_services?.length || 0}</div>
                      <div className="topo-blast-label">Serviços</div>
                    </div>
                  </div>
                </>
              )}

              {/* Conexões do nó selecionado */}
              <div className="topo-detail-section-title">Conexões</div>
              {graphData.edges.filter(e => e.source === selected.id || e.target === selected.id).length === 0 ? (
                <div style={{ fontSize: '0.8rem', color: '#475569' }}>Nenhuma conexão</div>
              ) : (
                graphData.edges
                  .filter(e => e.source === selected.id || e.target === selected.id)
                  .map((e, i) => {
                    const otherId = e.source === selected.id ? e.target : e.source;
                    const other = graphData.nodes.find(n => n.id === otherId);
                    const dir = e.source === selected.id ? '→' : '←';
                    return (
                      <div key={i} className="topo-detail-row" style={{ fontSize: '0.78rem' }}>
                        <span style={{ color: EDGE_COLOR[e.type] || '#334155' }}>{dir} {other?.name || otherId.substring(0, 8)}</span>
                        <strong style={{ color: '#64748b' }}>{e.type}</strong>
                      </div>
                    );
                  })
              )}
            </>
          ) : (
            <div className="topo-detail-hint">Clique em um nó para ver detalhes, blast radius e conexões</div>
          )}
        </div>
      </div>
    </div>
  );
}
