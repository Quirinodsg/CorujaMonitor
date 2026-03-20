import React, { useState, useEffect, useCallback } from "react";
import api from "../services/api";

const ACTION_ICON = {
  "user.login": "🔑",
  "user.logout": "🚪",
  "sensor.pause": "⏸️",
  "sensor.resume": "▶️",
  "sensor.create": "➕",
  "sensor.delete": "🗑️",
  "incident.acknowledge": "✅",
  "incident.resolve": "🔧",
  "ai.remediation": "🤖",
  "ai.healing": "💊",
  "ai.prediction": "🔮",
  "config.change": "⚙️",
  "system.reset": "🔄",
};

export default function AuditLogView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [page, setPage] = useState(0);
  const limit = 50;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit, offset: page * limit });
      if (filter) params.set("action", filter);
      const res = await api.get(`/audit?${params}`);
      setData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [filter, page]);

  useEffect(() => { load(); }, [load]);

  const items = data?.items || [];

  return (
    <div style={{ padding: 24, background: "var(--bg-primary, #0f1117)", minHeight: "100vh", color: "#e2e8f0" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
        <h2 style={{ margin: 0, fontSize: "1.4rem" }}>📋 Audit Log</h2>
        <input
          placeholder="Filtrar por ação..."
          value={filter}
          onChange={(e) => { setFilter(e.target.value); setPage(0); }}
          style={{
            padding: "6px 12px", borderRadius: 6, border: "1px solid rgba(255,255,255,0.1)",
            background: "rgba(255,255,255,0.05)", color: "#e2e8f0", fontSize: "0.85rem", width: 200,
          }}
        />
        <span style={{ marginLeft: "auto", color: "#64748b", fontSize: "0.82rem" }}>
          {data?.total || 0} entradas
        </span>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: 40, color: "#64748b" }}>Carregando...</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.83rem" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
              {["Ação", "Recurso", "ID", "Usuário", "IP", "Data/Hora"].map((h) => (
                <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "#64748b", fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map((e) => (
              <tr key={e.id} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <td style={{ padding: "8px 12px" }}>
                  {ACTION_ICON[e.action] || "📌"} {e.action}
                </td>
                <td style={{ padding: "8px 12px", color: "#94a3b8" }}>{e.resource_type || "—"}</td>
                <td style={{ padding: "8px 12px", color: "#64748b" }}>{e.resource_id || "—"}</td>
                <td style={{ padding: "8px 12px", color: "#94a3b8" }}>{e.user_id || "IA"}</td>
                <td style={{ padding: "8px 12px", color: "#64748b" }}>{e.ip_address || "—"}</td>
                <td style={{ padding: "8px 12px", color: "#64748b" }}>
                  {e.created_at ? e.created_at.replace("T", " ").slice(0, 19) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "center" }}>
        <button
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
          style={{ padding: "6px 16px", borderRadius: 6, border: "1px solid rgba(255,255,255,0.1)", background: "transparent", color: "#94a3b8", cursor: page === 0 ? "not-allowed" : "pointer" }}
        >← Anterior</button>
        <span style={{ padding: "6px 12px", color: "#64748b", fontSize: "0.82rem" }}>Página {page + 1}</span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={items.length < limit}
          style={{ padding: "6px 16px", borderRadius: 6, border: "1px solid rgba(255,255,255,0.1)", background: "transparent", color: "#94a3b8", cursor: items.length < limit ? "not-allowed" : "pointer" }}
        >Próxima →</button>
      </div>
    </div>
  );
}
