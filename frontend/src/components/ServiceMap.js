import React, { useState, useEffect, useRef, useCallback } from "react";
import api from "../services/api";
import "./ServiceMap.css";

const STATUS_COLOR = {
  ok: "#22c55e",
  warning: "#f59e0b",
  critical: "#ef4444",
  unknown: "#6b7280",
};

const TYPE_ICON = {
  server: "🖥️",
  switch: "🔀",
  router: "🌐",
  firewall: "🛡️",
  service: "⚙️",
  database: "🗄️",
  app: "📱",
  http: "🌍",
  probe: "🔌",
};

function NodeCard({ node, selected, onClick }) {
  return (
    <div
      className={"sm-node" + (selected ? " sm-node--selected" : "") + ` sm-node--${node.status}`}
      onClick={() => onClick(node)}
      title={`${node.name} (${node.status})`}
    >
      <span className="sm-node-icon">{TYPE_ICON[node.type] || "📦"}</span>
      <span className="sm-node-name">{node.name}</span>
      <span className="sm-node-status" style={{ background: STATUS_COLOR[node.status] }} />
    </div>
  );
}

export default function ServiceMap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [impact, setImpact] = useState(null);
  const [filter, setFilter] = useState("all");
  const intervalRef = useRef(null);

  const load = useCallback(async () => {
    try {
      const res = await api.get("/service-map");
      setData(res.data);
    } catch (e) {
      console.error("ServiceMap load error:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    intervalRef.current = setInterval(load, 15000);
    return () => clearInterval(intervalRef.current);
  }, [load]);

  const handleNodeClick = async (node) => {
    setSelected(node);
    try {
      const res = await api.get(`/service-map/impact/${node.id}`);
      setImpact(res.data);
    } catch (e) {
      setImpact(null);
    }
  };

  const filteredNodes = data
    ? data.nodes.filter((n) => filter === "all" || n.status === filter)
    : [];

  const impactedIds = new Set(impact ? impact.impacted_nodes : []);

  if (loading) return <div className="sm-loading">Carregando Service Map...</div>;
  if (!data) return <div className="sm-error">Erro ao carregar Service Map</div>;

  return (
    <div className="service-map">
      <div className="sm-header">
        <h2 className="sm-title">🕸️ Service Map</h2>
        <div className="sm-stats">
          <span className="sm-stat sm-stat--ok">✓ {data.stats.status.ok} OK</span>
          <span className="sm-stat sm-stat--warning">⚠ {data.stats.status.warning} Warning</span>
          <span className="sm-stat sm-stat--critical">✗ {data.stats.status.critical} Critical</span>
        </div>
        <div className="sm-filters">
          {["all", "ok", "warning", "critical"].map((f) => (
            <button
              key={f}
              className={"sm-filter-btn" + (filter === f ? " active" : "")}
              onClick={() => setFilter(f)}
            >
              {f === "all" ? "Todos" : f}
            </button>
          ))}
        </div>
      </div>

      <div className="sm-body">
        <div className="sm-graph">
          {filteredNodes.length === 0 ? (
            <div className="sm-empty">Nenhum nó encontrado</div>
          ) : (
            <div className="sm-nodes-grid">
              {filteredNodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  selected={selected?.id === node.id}
                  onClick={handleNodeClick}
                />
              ))}
            </div>
          )}

          {/* Highlight de nós impactados */}
          {impactedIds.size > 0 && (
            <div className="sm-impact-overlay">
              <span className="sm-impact-label">
                ⚡ {impactedIds.size} nós impactados por falha em "{selected?.name}"
              </span>
            </div>
          )}
        </div>

        {selected && (
          <div className="sm-detail">
            <h3 className="sm-detail-title">
              {TYPE_ICON[selected.type] || "📦"} {selected.name}
            </h3>
            <div className="sm-detail-row">
              <span>Status</span>
              <span style={{ color: STATUS_COLOR[selected.status] }}>
                ● {selected.status.toUpperCase()}
              </span>
            </div>
            <div className="sm-detail-row">
              <span>Tipo</span>
              <span>{selected.type}</span>
            </div>
            {selected.metadata?.ip && (
              <div className="sm-detail-row">
                <span>IP</span>
                <span>{selected.metadata.ip}</span>
              </div>
            )}
            {selected.metadata?.group && (
              <div className="sm-detail-row">
                <span>Grupo</span>
                <span>{selected.metadata.group}</span>
              </div>
            )}
            {impact && (
              <div className="sm-impact-section">
                <h4>Raio de Impacto</h4>
                {impact.impacted_nodes.length === 0 ? (
                  <p className="sm-no-impact">Nenhum nó dependente</p>
                ) : (
                  <ul className="sm-impact-list">
                    {impact.impacted_nodes.slice(0, 10).map((id) => (
                      <li key={id}>{id}</li>
                    ))}
                    {impact.impacted_nodes.length > 10 && (
                      <li>+{impact.impacted_nodes.length - 10} mais...</li>
                    )}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
