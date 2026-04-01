import React, { useState, useEffect } from 'react';
import './IntelligentAlerts.css';

const API = '';

const SEV = {
  critical: { color: '#EF4444', bg: 'rgba(239,68,68,0.12)', label: 'Crítico' },
  warning:  { color: '#F59E0B', bg: 'rgba(245,158,11,0.12)', label: 'Aviso' },
  info:     { color: '#60A5FA', bg: 'rgba(96,165,250,0.12)', label: 'Info' },
};

const STATUS_LABEL = {
  open: 'Aberto', acknowledged: 'Reconhecido', resolved: 'Resolvido',
};

const IcoWarn = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
    <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>
);

export default function IntelligentAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [rootCause, setRootCause] = useState(null);
  const [filter, setFilter] = useState({ status: '', severity: '' });
  const [loading, setLoading] = useState(true);

  const fetchAlerts = async () => {
    const params = new URLSearchParams();
    if (filter.status) params.set('status', filter.status);
    if (filter.severity) params.set('severity', filter.severity);
    params.set('limit', '100');
    try {
      const token = localStorage.getItem('token');
      const r = await fetch(`${API}/api/v1/alerts/intelligent?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (r.ok) {
        const d = await r.json();
        setAlerts(d.alerts || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAlerts(); }, [filter]);

  const handleSelect = async (alert) => {
    setSelected(alert);
    setRootCause(null);
    try {
      const token = localStorage.getItem('token');
      const r = await fetch(`${API}/api/v1/alerts/intelligent/${alert.id}/root-cause`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (r.ok) setRootCause(await r.json());
    } catch (_) {}
  };

  const sevInfo = (sev) => SEV[sev] || { color: '#9CA3AF', bg: 'rgba(107,114,128,0.12)', label: sev };

  return (
    <div className="ia-wrap">
      {/* Toolbar */}
      <div className="ia-toolbar">
        <select className="ia-filter-select" value={filter.status} onChange={e => setFilter(f => ({ ...f, status: e.target.value }))}>
          <option value="">Todos os status</option>
          <option value="open">Aberto</option>
          <option value="acknowledged">Reconhecido</option>
          <option value="resolved">Resolvido</option>
        </select>
        <select className="ia-filter-select" value={filter.severity} onChange={e => setFilter(f => ({ ...f, severity: e.target.value }))}>
          <option value="">Todas as severidades</option>
          <option value="critical">Crítico</option>
          <option value="warning">Aviso</option>
          <option value="info">Info</option>
        </select>
        <span className="ia-count">{alerts.length} alertas</span>
      </div>

      <div className="ia-main">
        {/* List */}
        <div className="ia-list">
          {loading && <div className="ia-loading">Carregando alertas...</div>}
          {!loading && alerts.length === 0 && (
            <div className="ia-empty">
              <div style={{ fontSize: 32, marginBottom: 8 }}>🧠</div>
              <div>Nenhum alerta encontrado com os filtros selecionados</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                Alertas são gerados automaticamente pelo pipeline AIOps quando anomalias são detectadas
              </div>
            </div>
          )}
          {alerts.map(a => {
            const s = sevInfo(a.severity);
            return (
              <div
                key={a.id}
                className={`ia-list-item${selected?.id === a.id ? ' selected' : ''}`}
                style={{ '--sev-color': s.color, '--sev-bg': s.bg }}
                onClick={() => handleSelect(a)}
                role="button"
                tabIndex={0}
                onKeyDown={e => e.key === 'Enter' && handleSelect(a)}
                aria-label={`Alerta: ${a.title}`}
              >
                <div className="ia-item-icon"><IcoWarn /></div>
                <div className="ia-item-body">
                  <div className="ia-item-title">{a.title}</div>
                  <div className="ia-item-meta">
                    <span className="ia-badge" style={{ background: s.bg, color: s.color }}>{s.label}</span>
                    <span className="ia-badge" style={{ background: 'rgba(107,114,128,0.12)', color: '#9CA3AF' }}>
                      {STATUS_LABEL[a.status] || a.status}
                    </span>
                    <span className="ia-item-time">
                      {a.created_at ? new Date(a.created_at).toLocaleString('pt-BR') : '—'}
                    </span>
                    {a.confidence && (
                      <span className="ia-item-confidence">{(a.confidence * 100).toFixed(0)}% conf.</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Detail */}
        <div className="ia-detail">
          {selected ? (
            <>
              <div className="ia-detail-title">{selected.title}</div>

              <div className="ia-detail-section">
                <div className="ia-detail-section-title">Detalhes</div>
                <div className="ia-detail-row">
                  <span>Status</span>
                  <strong>{STATUS_LABEL[selected.status] || selected.status}</strong>
                </div>
                <div className="ia-detail-row">
                  <span>Severidade</span>
                  <strong style={{ color: sevInfo(selected.severity).color }}>
                    {sevInfo(selected.severity).label}
                  </strong>
                </div>
                {selected.confidence && (
                  <div className="ia-detail-row">
                    <span>Confiança</span>
                    <strong>{(selected.confidence * 100).toFixed(0)}%</strong>
                  </div>
                )}
                <div className="ia-detail-row">
                  <span>Criado em</span>
                  <strong>{selected.created_at ? new Date(selected.created_at).toLocaleString('pt-BR') : '—'}</strong>
                </div>
                {selected.status !== 'resolved' && (
                  <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                    {selected.status === 'open' && (
                      <button onClick={async () => {
                        try {
                          const token = localStorage.getItem('token');
                          await fetch(`${API}/api/v1/alerts/intelligent/${selected.id}/acknowledge`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
                          setSelected({ ...selected, status: 'acknowledged' });
                          fetchAlerts();
                        } catch (_) {}
                      }} style={{ padding: '6px 16px', background: '#f59e0b', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                        ✓ Reconhecer
                      </button>
                    )}
                    <button onClick={async () => {
                      try {
                        const token = localStorage.getItem('token');
                        await fetch(`${API}/api/v1/alerts/intelligent/${selected.id}/resolve`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
                        setSelected({ ...selected, status: 'resolved' });
                        fetchAlerts();
                      } catch (_) {}
                    }} style={{ padding: '6px 16px', background: '#22c55e', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                      ✅ Resolver
                    </button>
                    <button onClick={async () => {
                      if (!window.confirm('Excluir este alerta?')) return;
                      try {
                        const token = localStorage.getItem('token');
                        await fetch(`${API}/api/v1/alerts/intelligent/${selected.id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
                        setSelected(null);
                        fetchAlerts();
                      } catch (_) {}
                    }} style={{ padding: '6px 16px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 12, fontWeight: 600 }}>
                      🗑️ Excluir
                    </button>
                  </div>
                )}
              </div>

              {rootCause && (
                <div className="ia-detail-section">
                  <div className="ia-detail-section-title">Causa Raiz</div>
                  <p className="ia-root-cause">{rootCause.root_cause || 'Análise em andamento...'}</p>
                  {rootCause.affected_hosts?.length > 0 && (
                    <>
                      <div className="ia-detail-section-title" style={{ marginTop: 12 }}>
                        Hosts Afetados ({rootCause.affected_hosts.length})
                      </div>
                      <ul className="ia-hosts-list">
                        {rootCause.affected_hosts.map((h, i) => <li key={i}>{h}</li>)}
                      </ul>
                    </>
                  )}
                </div>
              )}

              <div className="ia-detail-section">
                <div className="ia-detail-section-title">Timeline</div>
                <div className="ia-timeline">
                  <div className="ia-timeline-item">
                    <span className="ia-timeline-dot ia-dot-open" />
                    <span>Criado: {selected.created_at ? new Date(selected.created_at).toLocaleString('pt-BR') : '—'}</span>
                  </div>
                  {selected.resolved_at && (
                    <div className="ia-timeline-item">
                      <span className="ia-timeline-dot ia-dot-resolved" />
                      <span>Resolvido: {new Date(selected.resolved_at).toLocaleString('pt-BR')}</span>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="ia-detail-hint">Selecione um alerta para ver detalhes e causa raiz</div>
          )}
        </div>
      </div>
    </div>
  );
}
