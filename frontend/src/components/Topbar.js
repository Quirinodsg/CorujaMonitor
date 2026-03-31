import React, { useState, useEffect, useRef, useCallback } from "react";
import "./Topbar.css";
import { API_URL } from "../config";

const PAGE_LABELS = {
  dashboard: "Dashboard", observability: "Observabilidade", topology: "Topologia",
  "intelligent-alerts": "Alertas Inteligentes", incidents: "Incidentes",
  "aiops-v3": "AIOps Pipeline", "advanced-metrics": "Metricas Avancadas",
  "events-timeline": "Eventos", "knowledge-base": "Base de Conhecimento",
  servers: "Servidores", sensors: "Sensores", companies: "Empresas",
  "probe-nodes": "Probe Nodes", maintenance: "GMUD", settings: "Configuracoes",
  aiops: "AIOps", "ai-activities": "Atividades da IA", discovery: "Discovery",
  "system-health": "Saude do Sistema", "noc-realtime": "NOC",
};

const RESULT_ICONS = { server: "🖥️", sensor: "📡", default: "🔍" };

const base = API_URL;

let _cache = null;
let _cacheTs = 0;
const CACHE_TTL = 30000;

function IcoSearch() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function IcoBell() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}

async function fetchAllData() {
  const now = Date.now();
  if (_cache && now - _cacheTs < CACHE_TTL) return _cache;
  const token = localStorage.getItem("token");
  const headers = { Authorization: "Bearer " + token };
  const [r1, r2] = await Promise.allSettled([
    fetch(base + "/servers?limit=200", { headers }),
    fetch(base + "/sensors?limit=200", { headers }),
  ]);
  const items = [];
  if (r1.status === "fulfilled" && r1.value.ok) {
    const d = await r1.value.json();
    (Array.isArray(d) ? d : (d.items || [])).forEach(s =>
      items.push({ type: "server", id: s.id, label: s.hostname || s.name || "", sub: s.ip_address || "", page: "servers" })
    );
  }
  if (r2.status === "fulfilled" && r2.value.ok) {
    const d = await r2.value.json();
    (Array.isArray(d) ? d : (d.items || [])).forEach(s =>
      items.push({ type: "sensor", id: s.id, label: s.name || "", sub: s.sensor_type || "", page: "sensors" })
    );
  }
  _cache = items;
  _cacheTs = now;
  return items;
}

function Topbar({ currentPage, systemStatus, alertCount = 0, onNavigate }) {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [activeIdx, setActiveIdx] = useState(-1);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") { e.preventDefault(); inputRef.current?.focus(); }
      if (e.key === "Escape") { setOpen(false); setSearch(""); }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target) &&
          inputRef.current && !inputRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const doSearch = useCallback(async (q) => {
    if (!q || q.length < 2) { setResults([]); setOpen(false); return; }
    setLoading(true);
    try {
      const ql = q.toLowerCase();
      const all = await fetchAllData();
      const filtered = all.filter(item =>
        (item.label || "").toLowerCase().includes(ql) ||
        (item.sub || "").toLowerCase().includes(ql)
      ).slice(0, 10);
      setResults(filtered);
      setOpen(true);
    } catch (_) {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleChange = (e) => {
    const q = e.target.value;
    setSearch(q);
    setActiveIdx(-1);
    clearTimeout(debounceRef.current);
    if (!q) { setResults([]); setOpen(false); return; }
    debounceRef.current = setTimeout(() => doSearch(q), 200);
  };

  const handleSelect = (r) => { onNavigate && onNavigate(r.page); setSearch(""); setResults([]); setOpen(false); };

  const handleKeyDown = (e) => {
    if (!open || !results.length) return;
    if (e.key === "ArrowDown") { e.preventDefault(); setActiveIdx(i => Math.min(i + 1, results.length - 1)); }
    if (e.key === "ArrowUp") { e.preventDefault(); setActiveIdx(i => Math.max(i - 1, 0)); }
    if (e.key === "Enter" && activeIdx >= 0) handleSelect(results[activeIdx]);
  };

  const statusClass = systemStatus === "ok" ? "topbar-status--ok" : systemStatus === "warning" ? "topbar-status--warning" : "topbar-status--critical";
  const statusLabel = systemStatus === "ok" ? "Sistema OK" : systemStatus === "warning" ? "Atencao" : "Critico";
  const pageLabel = PAGE_LABELS[currentPage] || currentPage;

  return (
    <header className="topbar" role="banner">
      <span className="topbar-title">{pageLabel}</span>
      <div className="topbar-search" role="search">
        <span className="topbar-search-icon"><IcoSearch /></span>
        <input
          ref={inputRef}
          className="topbar-search-input"
          type="text"
          placeholder="Buscar servidores, sensores..."
          value={search}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={() => search.length >= 2 && results.length > 0 && setOpen(true)}
          aria-label="Busca global"
          autoComplete="off"
        />
        {!search && <span className="topbar-search-kbd">Ctrl+K</span>}
        {loading && <span className="topbar-search-spinner" aria-hidden="true" />}
        {open && (
          <div className="topbar-search-dropdown" ref={dropdownRef} role="listbox">
            {results.length === 0 && !loading && (
              <div className="topbar-search-empty">Nenhum resultado para "{search}"</div>
            )}
            {results.map((r, idx) => (
              <button
                key={r.type + "-" + r.id}
                className={"topbar-search-result" + (idx === activeIdx ? " active" : "")}
                onClick={() => handleSelect(r)}
                role="option"
                aria-selected={idx === activeIdx}
              >
                <span className="topbar-result-icon">{RESULT_ICONS[r.type] || RESULT_ICONS.default}</span>
                <span className="topbar-result-body">
                  <span className="topbar-result-label">{r.label}</span>
                  {r.sub && <span className="topbar-result-sub">{r.sub}</span>}
                </span>
                <span className="topbar-result-type">{r.type}</span>
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="topbar-right">
        <div
          className={"topbar-status " + statusClass}
          onClick={() => onNavigate && onNavigate("observability")}
          role="button" tabIndex={0}
          aria-label={"Status: " + statusLabel}
          onKeyDown={e => e.key === "Enter" && onNavigate && onNavigate("observability")}
        >
          <span className="topbar-status-dot" />
          {statusLabel}
        </div>
        <button className="topbar-icon-btn" onClick={() => onNavigate && onNavigate("intelligent-alerts")} aria-label="Alertas" title="Alertas">
          <IcoBell />
          {alertCount > 0 && <span className="topbar-badge" aria-hidden="true">{alertCount > 9 ? "9+" : alertCount}</span>}
        </button>
      </div>
    </header>
  );
}

export default Topbar;