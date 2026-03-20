import React, { useState, useEffect, useRef } from 'react';
import './TopologyView.css';

const API = process.env.REACT_APP_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`;

const STATUS_COLOR = {
  ok: '#22c55e', warning: '#f59e0b', critical: '#ef4444',
  unknown: '#6b7280', impacted: '#f97316',
};

function useForceLayout(nodes) {
  const [positions, setPositions] = useState({});
  useEffect(() => {
    if (!nodes.length) return;
    const pos = {};
    const cx = 480, cy = 250, r = 200;
    nodes.forEach((n, i) => {
      const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
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
  const [syncMsg, setSyncMsg] = useState(null);

  const positions = useForceLayout(graphData.nodes);

  useEffect(() => {
    const token = localStorage.getItem('token');
    fetch(`${API}/api/v1/topology/graph`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then(r => r.json())
      .then(d => {
        setGraphData({ nodes: d.nodes || [], edges: d.edges || [] });
        setLoading(false);
      })
      .catch(() => {
        setError('Topologia não disponível. Execute a migração v3 primeiro.');
        setLoading(false);
      });
  }, []);

  const syncFromServers = async () => {
    setSyncing(true);
    setSyncMsg(null);
    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const syncResp = await fetch(`${API}/api/v1/topology/sync-from-servers`, {
        method: 'POST',
        headers,
      });
      const syncData = await syncResp.json();

      const gr = await fetch(`${API}/api/v1/topology/graph`, { headers });
      if (gr.ok) {
        const gd = await gr.json();
        setGraphData({ nodes: gd.nodes || [], edges: gd.edges || [] });
        setError(null);
        setSyncMsg(`✅ ${syncData.created || 0} nós criados, ${syncData.skipped || 0} já existentes`);
      } else {
        setSyncMsg('⚠️ Sync executado mas falha ao recarregar grafo');
      }
    } catch (e) {
      setSyncMsg(`❌ Erro: ${e.message}`);
    } finally {
      setSyncing(false);
      setTimeout(() => setSyncMsg(null), 4000);
    }
  };

  const handleNodeClick = async (node) => {
    setSelected(node);
    setImpact(null);
    try {
      const r = await fetch(`${API}/api/v1/topology/impact/${node.id}`);
      if (r.ok) setImpact(await r.json());
    } catch (_) {}
  };

  if (loading) return <div className="topo-loading">Carregando topologia...</div>;

  if (error || graphData.nodes.length === 0) {
    return (
      <div className="topo-wrap">
        <div className="topo-empty-card">
          <div className="topo-empty-icon">🕸️</div>
          <div className="topo-empty-title">Topologia não configurada</div>
          <p className="topo-empty-desc">
            {error || 'Nenhum nó cadastrado. A topologia é populada automaticamente via descoberta SNMP/WMI ou pode ser importada dos servidores monitorados.'}
          </p>
          <button className="ds-btn ds-btn--primary" onClick={syncFromServers} disabled={syncing}>
            {syncing ? 'Sincronizando...' : 'Importar servidores monitorados'}
          </button>
          {syncMsg && <p style={{ marginTop: 12, fontSize: '0.85rem', color: '#94a3b8' }}>{syncMsg}</p>}
        </div>
      </div>
    );
  }

  const W = 960, H = 500;

  return (
    <div className="topo-wrap">
      <div className="topo-toolbar">
        <button className="ds-btn ds-btn--ghost" onClick={syncFromServers} disabled={syncing} style={{ fontSize: 12 }}>
          {syncing ? 'Sincronizando...' : 'Sincronizar'}
        </button>
        {syncMsg && <span style={{ fontSize: '0.8rem', color: '#94a3b8', marginLeft: 8 }}>{syncMsg}</span>}
        <span className="topo-stats">{graphData.nodes.length} nós · {graphData.edges.length} conexões</span>
      </div>

      <div className="topo-main">
        <div className="topo-graph-card">
          <svg viewBox={`0 0 ${W} ${H}`} className="topo-svg" aria-label="Grafo de topologia de rede">
            <defs>
              <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <path d="M0,0 L0,6 L6,3 z" fill="#334155" />
              </marker>
              {graphData.nodes.map(node => {
                const color = STATUS_COLOR[node.status] || STATUS_COLOR.unknown;
                return (
                  <radialGradient key={`g-${node.id}`} id={`grad-${node.id}`} cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor={color} stopOpacity="0.3" />
                    <stop offset="100%" stopColor={color} stopOpacity="0.05" />
                  </radialGradient>
                );
              })}
            </defs>

            {/* Edges */}
            {graphData.edges.map((e, i) => {
              const src = positions[e.source || e.from];
              const tgt = positions[e.target || e.to];
              if (!src || !tgt) return null;
              return (
                <line key={i}
                  x1={src.x} y1={src.y} x2={tgt.x} y2={tgt.y}
                  stroke="#1e293b" strokeWidth="1.5"
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
              const r = isSelected ? 24 : 20;
              return (
                <g key={node.id} className="topo-node" onClick={() => handleNodeClick(node)}
                  role="button" aria-label={`Nó: ${node.name || node.id}`}>
                  {/* Glow ring for selected */}
                  {isSelected && (
                    <circle cx={pos.x} cy={pos.y} r={r + 8}
                      fill="none" stroke={color} strokeWidth="1" strokeOpacity="0.3" />
                  )}
                  {/* Background fill */}
                  <circle cx={pos.x} cy={pos.y} r={r}
                    fill={`url(#grad-${node.id})`}
                    stroke={color} strokeWidth={isSelected ? 2 : 1.5}
                  />
                  {/* Status dot */}
                  <circle cx={pos.x + r - 5} cy={pos.y - r + 5} r="4"
                    fill={color} stroke="#0d1117" strokeWidth="1.5" />
                  {/* Label */}
                  <text x={pos.x} y={pos.y + 4} textAnchor="middle"
                    fontSize="10" fill={color} fontWeight="600" fontFamily="Inter, sans-serif">
                    {(node.name || node.id || '').substring(0, 12)}
                  </text>
                  <text x={pos.x} y={pos.y + 36} textAnchor="middle"
                    fontSize="9" fill="#475569" fontFamily="Inter, sans-serif">
                    {node.type}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Legend */}
          <div className="topo-legend">
            {Object.entries(STATUS_COLOR).map(([status, color]) => (
              <div key={status} className="topo-legend-item">
                <span className="topo-legend-dot" style={{ background: color }} />
                {status}
              </div>
            ))}
          </div>
        </div>

        {/* Detail */}
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
              {selected.ip && <div className="topo-detail-row"><span>IP</span><strong>{selected.ip}</strong></div>}

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
            </>
          ) : (
            <div className="topo-detail-hint">Clique em um nó para ver detalhes e blast radius</div>
          )}
        </div>
      </div>
    </div>
  );
}
