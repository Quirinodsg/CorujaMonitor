import React, { useState, useEffect, useRef } from 'react';
import './TopologyView.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const STATUS_COLOR = {
  ok: '#22c55e', warning: '#f59e0b', critical: '#ef4444',
  unknown: '#94a3b8', impacted: '#f97316',
};

// Simple force-directed layout (no external lib dependency)
function useForceLayout(nodes, edges) {
  const [positions, setPositions] = useState({});

  useEffect(() => {
    if (!nodes.length) return;
    const pos = {};
    const cx = 500, cy = 300, r = 220;
    nodes.forEach((n, i) => {
      const angle = (2 * Math.PI * i) / nodes.length;
      pos[n.id] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
    });
    setPositions(pos);
  }, [nodes.length]);

  return positions;
}

export default function TopologyView() {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [selected, setSelected] = useState(null);
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const svgRef = useRef(null);

  const syncFromServers = async () => {
    setSyncing(true);
    try {
      await fetch(`${API}/api/v1/topology/sync-from-servers`, { method: 'POST' });
      const gr = await fetch(`${API}/api/v1/topology/graph`);
      if (gr.ok) {
        const gd = await gr.json();
        setGraphData({ nodes: gd.nodes || [], edges: gd.edges || [] });
        setError(null);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSyncing(false);
    }
  };

  const positions = useForceLayout(graphData.nodes, graphData.edges);

  useEffect(() => {
    fetch(`${API}/api/v1/topology/graph`)
      .then(r => r.json())
      .then(d => {
        setGraphData({ nodes: d.nodes || [], edges: d.edges || [] });
        setLoading(false);
      })
      .catch(e => {
        setError('Topologia não disponível. Execute a migração v3 primeiro.');
        setLoading(false);
      });
  }, []);

  const handleNodeClick = async (node) => {
    setSelected(node);
    try {
      const r = await fetch(`${API}/api/v1/topology/impact/${node.id}`);
      if (r.ok) setImpact(await r.json());
    } catch (e) {
      setImpact(null);
    }
  };

  if (loading) return <div className="topo-loading">Carregando topologia...</div>;

  if (error || graphData.nodes.length === 0) {
    return (
      <div className="topo-container">
        <div className="topo-header"><h2>🕸️ Topologia de Rede</h2></div>
        <div className="topo-empty">
          <div className="topo-empty-icon">🕸️</div>
          <p>{error || 'Nenhum nó de topologia cadastrado.'}</p>
          <p className="topo-hint">A topologia é populada automaticamente via descoberta SNMP/WMI ou pode ser configurada manualmente.</p>
          <button
            className="topo-sync-btn"
            onClick={syncFromServers}
            disabled={syncing}
          >
            {syncing ? '⏳ Sincronizando...' : '🔄 Importar servidores monitorados'}
          </button>
        </div>
      </div>
    );
  }

  const W = 1000, H = 600;

  return (
    <div className="topo-container">
      <div className="topo-header">
        <h2>🕸️ Topologia de Rede</h2>
        <span className="topo-count">{graphData.nodes.length} nós · {graphData.edges.length} conexões</span>
      </div>

      <div className="topo-main">
        <div className="topo-graph-wrap">
          <svg ref={svgRef} viewBox={`0 0 ${W} ${H}`} className="topo-svg">
            <defs>
              <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                <path d="M0,0 L0,6 L8,3 z" fill="#475569" />
              </marker>
            </defs>

            {/* Edges */}
            {graphData.edges.map((e, i) => {
              const src = positions[e.source || e.from];
              const tgt = positions[e.target || e.to];
              if (!src || !tgt) return null;
              return (
                <line key={i}
                  x1={src.x} y1={src.y} x2={tgt.x} y2={tgt.y}
                  stroke="#334155" strokeWidth="1.5"
                  markerEnd="url(#arrow)"
                />
              );
            })}

            {/* Nodes */}
            {graphData.nodes.map(node => {
              const pos = positions[node.id];
              if (!pos) return null;
              const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
              const isSelected = selected?.id === node.id;
              return (
                <g key={node.id} onClick={() => handleNodeClick(node)} style={{ cursor: 'pointer' }}>
                  <circle cx={pos.x} cy={pos.y} r={isSelected ? 22 : 18}
                    fill={color} fillOpacity={0.2}
                    stroke={color} strokeWidth={isSelected ? 3 : 1.5}
                  />
                  <text x={pos.x} y={pos.y + 4} textAnchor="middle" fontSize="11" fill={color} fontWeight="600">
                    {(node.name || node.id || '').substring(0, 10)}
                  </text>
                  <text x={pos.x} y={pos.y + 32} textAnchor="middle" fontSize="9" fill="#64748b">
                    {node.type}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Detail panel */}
        <div className="topo-detail">
          {selected ? (
            <>
              <h3>Nó Selecionado</h3>
              <div className="topo-detail-row"><span>Nome</span><strong>{selected.name || selected.id}</strong></div>
              <div className="topo-detail-row"><span>Tipo</span><strong>{selected.type}</strong></div>
              <div className="topo-detail-row"><span>Status</span>
                <span className="topo-status-dot" style={{ color: STATUS_COLOR[selected.status] || '#94a3b8' }}>
                  ● {selected.status || 'unknown'}
                </span>
              </div>
              {impact && (
                <>
                  <h4>Blast Radius</h4>
                  <div className="topo-detail-row"><span>Impacto Total</span><strong>{impact.total_impact}</strong></div>
                  <div className="topo-detail-row"><span>Hosts</span><strong>{impact.affected_hosts?.length || 0}</strong></div>
                  <div className="topo-detail-row"><span>Serviços</span><strong>{impact.affected_services?.length || 0}</strong></div>
                </>
              )}
            </>
          ) : (
            <div className="topo-detail-hint">Clique em um nó para ver detalhes e blast radius</div>
          )}
        </div>
      </div>
    </div>
  );
}
