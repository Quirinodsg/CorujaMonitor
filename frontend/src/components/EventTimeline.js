import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './EventTimeline.css';

const SEVERITY_CONFIG = {
  critical: { color: '#ef4444', bg: '#fef2f2', icon: '🔴', label: 'Crítico' },
  error:    { color: '#f97316', bg: '#fff7ed', icon: '🟠', label: 'Erro' },
  warning:  { color: '#f59e0b', bg: '#fffbeb', icon: '🟡', label: 'Aviso' },
  info:     { color: '#3b82f6', bg: '#eff6ff', icon: '🔵', label: 'Info' },
};

function EventTimeline({ onNavigate }) {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ severity: 'all', host: '', type: 'all', range: '24h' });
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    try {
      const res = await api.get('/incidents?limit=200');
      setIncidents(res.data || []);
    } catch (e) {
      console.error('Erro ao carregar eventos:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, [load]);

  const getFilteredEvents = () => {
    let filtered = [...incidents];
    const now = Date.now();
    const ranges = { '1h': 3600000, '6h': 21600000, '24h': 86400000, '7d': 604800000 };

    if (filters.range !== 'all') {
      const cutoff = now - (ranges[filters.range] || 86400000);
      filtered = filtered.filter(e => new Date(e.created_at).getTime() >= cutoff);
    }
    if (filters.severity !== 'all') filtered = filtered.filter(e => e.severity === filters.severity);
    if (filters.host) filtered = filtered.filter(e => e.title?.toLowerCase().includes(filters.host.toLowerCase()));
    if (filters.type !== 'all') filtered = filtered.filter(e => e.sensor_type === filters.type);

    return filtered;
  };

  const filtered = getFilteredEvents();
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const cfg = (sev) => SEVERITY_CONFIG[sev] || SEVERITY_CONFIG.info;

  if (loading) return <div className="et-loading">Carregando eventos...</div>;

  return (
    <div className="et-container">
      <div className="et-header">
        <div>
          <h1>📋 Timeline de Eventos</h1>
          <p className="et-subtitle">{filtered.length} eventos encontrados</p>
        </div>
        <button className="et-btn-refresh" onClick={load}>↻ Atualizar</button>
      </div>

      <div className="et-filters">
        <select value={filters.range} onChange={e => { setFilters({...filters, range: e.target.value}); setPage(1); }}>
          <option value="1h">Última hora</option>
          <option value="6h">Últimas 6h</option>
          <option value="24h">Últimas 24h</option>
          <option value="7d">Últimos 7 dias</option>
          <option value="all">Todos</option>
        </select>
        <select value={filters.severity} onChange={e => { setFilters({...filters, severity: e.target.value}); setPage(1); }}>
          <option value="all">Todas as severidades</option>
          <option value="critical">Crítico</option>
          <option value="warning">Aviso</option>
        </select>
        <select value={filters.type} onChange={e => { setFilters({...filters, type: e.target.value}); setPage(1); }}>
          <option value="all">Todos os tipos</option>
          <option value="ping">Ping</option>
          <option value="cpu">CPU</option>
          <option value="memory">Memória</option>
          <option value="disk">Disco</option>
          <option value="service">Serviço</option>
        </select>
        <input
          placeholder="🔍 Filtrar por host..."
          value={filters.host}
          onChange={e => { setFilters({...filters, host: e.target.value}); setPage(1); }}
          className="et-search"
        />
      </div>

      {paginated.length === 0 ? (
        <div className="et-empty">Nenhum evento encontrado com os filtros selecionados.</div>
      ) : (
        <div className="et-timeline">
          {paginated.map((event, idx) => {
            const c = cfg(event.severity);
            return (
              <div key={event.id || idx} className="et-event" style={{ borderLeftColor: c.color }}>
                <div className="et-event-time">
                  <span className="et-icon">{c.icon}</span>
                  <span className="et-ts">{new Date(event.created_at).toLocaleString('pt-BR')}</span>
                </div>
                <div className="et-event-body">
                  <div className="et-event-header">
                    <span className="et-badge" style={{ background: c.bg, color: c.color }}>{c.label}</span>
                    {event.sensor_type && (
                      <span className="et-type-badge">{event.sensor_type}</span>
                    )}
                  </div>
                  <h4 className="et-title">{event.title}</h4>
                  {event.description && <p className="et-desc">{event.description}</p>}
                  {event.root_cause && (
                    <div className="et-root-cause">
                      <strong>Causa raiz:</strong> {event.root_cause}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {totalPages > 1 && (
        <div className="et-pagination">
          <button disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Anterior</button>
          <span>Página {page} de {totalPages}</span>
          <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Próxima →</button>
        </div>
      )}
    </div>
  );
}

export default EventTimeline;
