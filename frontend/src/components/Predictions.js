import React, { useState, useEffect, useCallback } from "react";
import api from "../services/api";
import "./Predictions.css";

const SEV_COLOR = { critical: "#ef4444", warning: "#f59e0b", info: "#3b82f6" };
const SEV_ICON = { critical: "🔴", warning: "🟡", info: "🔵" };

export default function Predictions() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  const load = useCallback(async () => {
    try {
      const res = await api.get("/predictions?hours=24");
      setData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [load]);

  const items = data
    ? data.predictions.filter((p) => filter === "all" || p.severity === filter)
    : [];

  return (
    <div className="predictions">
      <div className="pred-header">
        <h2 className="pred-title">🔮 Predições de Falha — Próximas 24h</h2>
        <div className="pred-filters">
          {["all", "critical", "warning", "info"].map((f) => (
            <button
              key={f}
              className={"pred-filter" + (filter === f ? " active" : "")}
              onClick={() => setFilter(f)}
            >
              {f === "all" ? "Todos" : f}
            </button>
          ))}
        </div>
        <button className="pred-refresh" onClick={load}>↻ Atualizar</button>
      </div>

      {loading ? (
        <div className="pred-loading">Calculando predições...</div>
      ) : items.length === 0 ? (
        <div className="pred-empty">
          <span>✅</span>
          <p>Nenhuma falha prevista nas próximas 24 horas</p>
        </div>
      ) : (
        <div className="pred-list">
          {items.map((p, i) => (
            <div key={i} className={`pred-card pred-card--${p.severity}`}>
              <div className="pred-card-header">
                <span className="pred-sev-icon">{SEV_ICON[p.severity]}</span>
                <span className="pred-message">{p.message}</span>
                <span className="pred-time" style={{ color: SEV_COLOR[p.severity] }}>
                  em {p.hours_until_breach < 1
                    ? `${Math.round(p.hours_until_breach * 60)}min`
                    : `${p.hours_until_breach.toFixed(1)}h`}
                </span>
              </div>
              <div className="pred-card-body">
                <div className="pred-metric">
                  <span>Atual</span>
                  <strong>{p.current_value?.toFixed(1)}%</strong>
                </div>
                <div className="pred-metric">
                  <span>Threshold</span>
                  <strong>{p.threshold}%</strong>
                </div>
                <div className="pred-metric">
                  <span>Tendência</span>
                  <strong>+{(p.trend_slope * 3600).toFixed(2)}/h</strong>
                </div>
                <div className="pred-metric">
                  <span>Confiança R²</span>
                  <strong>{(p.r_squared * 100).toFixed(0)}%</strong>
                </div>
                <div className="pred-metric">
                  <span>Previsto em</span>
                  <strong>{p.predicted_breach_iso?.replace("T", " ").replace("Z", "")}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {data && (
        <div className="pred-footer">
          {data.total} predições ativas · atualizado em {data.generated_at?.replace("T", " ").replace("Z", "")}
        </div>
      )}
    </div>
  );
}
