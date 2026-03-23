import React, { useState, useEffect } from 'react';
import './EventsTimeline.css';

const API = '';

const SEV_COLOR = { critical: '#ef4444', warning: '#f59e0b', info: '#60a5fa', ok: '#22c55e' };
const SEV_ICON = { critical: '🔴', warning: '🟡', info: '🔵', ok: '🟢' };

export default function EventsTimeline() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ severity: '', type: '', search: '' });
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 50;

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: PAGE_SIZE, offset: page * PAGE_SIZE });
      if (filter.severity) params.set('severity', filter.severity);
      if (filter.type) params.set('type', filter.type);

      const token = localStorage.getItem('token') || localStorage.getItem('access_token') || '';
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const r = await fetch(`${API}/api/v1/incidents?${params}`, { headers });
      if (r.ok) {
        const d = await r.json();
        const list = Array.isArray(d) ? d : (Array.isArray(d.incidents) ? d.incidents : []);
        setEvents(list);
      } else if (r.status === 403 || r.status === 401) {
        // Sem autenticação — mostrar lista vazia sem crash
        setEvents([]);
      }
    } catch (e) {
      console.error(e);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchEvents(); }, [filter, page]);

  const filtered = events.filter(e => {
    if (!filter.search) return true;
    const q = filter.search.toLowerCase();
    return (e.title || '').toLowerCase().includes(q) ||
           (e.description || '').toLowerCase().includes(q) ||
           (e.server_name || '').toLowerCase().includes(q);
  });

  // Group by date
  const grouped = filtered.reduce((acc, e) => {
    const date = e.created_at
      ? new Date(e.created_at).toLocaleDateString('pt-BR')
      : 'Sem data';
    if (!acc[date]) acc[date] = [];
    acc[date].push(e);
    return acc;
  }, {});

  return (
    <div className="etl-container">
      <div className="etl-header">
        <h2>📋 Timeline de Eventos</h2>
        <div className="etl-filters">
          <input
            type="text"
            placeholder="Buscar eventos..."
            value={filter.search}
            onChange={e => setFilter(f => ({ ...f, search: e.target.value }))}
            className="etl-search"
          />
          <select value={filter.severity} onChange={e => setFilter(f => ({ ...f, severity: e.target.value }))}>
            <option value="">Todas as severidades</option>
            <option value="critical">Crítico</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
          <select value={filter.type} onChange={e => setFilter(f => ({ ...f, type: e.target.value }))}>
            <option value="">Todos os tipos</option>
            <option value="host_unreachable">Host Inacessível</option>
            <option value="high_cpu">CPU Alta</option>
            <option value="low_memory">Memória Baixa</option>
            <option value="disk_full">Disco Cheio</option>
            <option value="service_down">Serviço Down</option>
          </select>
        </div>
      </div>

      {loading && <div className="etl-loading">Carregando eventos...</div>}

      {!loading && filtered.length === 0 && (
        <div className="etl-empty">
          <div style={{ fontSize: 32, marginBottom: 8 }}>🕐</div>
          <div>Nenhum evento encontrado com os filtros aplicados</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
            Eventos são gerados quando sensores detectam mudanças de estado
          </div>
        </div>
      )}

      <div className="etl-timeline">
        {Object.entries(grouped).map(([date, evts]) => (
          <div key={date} className="etl-day-group">
            <div className="etl-day-header">
              <span className="etl-day-label">{date}</span>
              <span className="etl-day-count">{evts.length} evento{evts.length !== 1 ? 's' : ''}</span>
            </div>
            <div className="etl-events">
              {evts.map((e, i) => {
                const sev = e.severity || (e.status === 'open' ? 'critical' : 'info');
                return (
                  <div key={e.id || i} className="etl-event-item">
                    <div className="etl-event-line">
                      <div className="etl-event-dot" style={{ background: SEV_COLOR[sev] || '#94a3b8' }}></div>
                      <div className="etl-event-connector"></div>
                    </div>
                    <div className="etl-event-body">
                      <div className="etl-event-header">
                        <span className="etl-event-icon">{SEV_ICON[sev] || '⚪'}</span>
                        <span className="etl-event-title">{e.title || e.description || 'Evento'}</span>
                        <span className="etl-event-time">
                          {e.created_at ? new Date(e.created_at).toLocaleTimeString('pt-BR') : ''}
                        </span>
                      </div>
                      <div className="etl-event-details">
                        {e.server_name && <span className="etl-tag">🖥️ {e.server_name}</span>}
                        {e.type && <span className="etl-tag">{e.type}</span>}
                        <span className={`etl-sev-badge etl-sev-${sev}`}>{sev}</span>
                        {e.status && <span className="etl-status">{e.status}</span>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="etl-pagination">
        <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}>← Anterior</button>
        <span>Página {page + 1}</span>
        <button onClick={() => setPage(p => p + 1)} disabled={events.length < PAGE_SIZE}>Próxima →</button>
      </div>
    </div>
  );
}
