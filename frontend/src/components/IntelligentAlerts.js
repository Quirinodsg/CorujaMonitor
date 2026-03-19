import React, { useState, useEffect } from 'react';
import './IntelligentAlerts.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const SEV_COLOR = { critical: '#ef4444', warning: '#f59e0b', info: '#60a5fa' };
const STATUS_LABEL = { open: '🔴 Aberto', acknowledged: '🟡 Reconhecido', resolved: '✅ Resolvido' };

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
      const r = await fetch(`${API}/api/v1/alerts/intelligent?${params}`);
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
      const r = await fetch(`${API}/api/v1/alerts/intelligent/${alert.id}/root-cause`);
      if (r.ok) setRootCause(await r.json());
    } catch (e) {}
  };

  return (
    <div className="ia-container">
      <div className="ia-header">
        <h2>🧠 Alertas Inteligentes</h2>
        <div className="ia-filters">
          <select value={filter.status} onChange={e => setFilter(f => ({ ...f, status: e.target.value }))}>
            <option value="">Todos os status</option>
            <option value="open">Aberto</option>
            <option value="acknowledged">Reconhecido</option>
            <option value="resolved">Resolvido</option>
          </select>
          <select value={filter.severity} onChange={e => setFilter(f => ({ ...f, severity: e.target.value }))}>
            <option value="">Todas as severidades</option>
            <option value="critical">Crítico</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
        </div>
      </div>

      <div className="ia-main">
        {/* Alert list */}
        <div className="ia-list">
          {loading && <div className="ia-loading">Carregando alertas...</div>}
          {!loading && alerts.length === 0 && (
            <div className="ia-empty">✅ Nenhum alerta inteligente encontrado</div>
          )}
          {alerts.map(a => (
            <div
              key={a.id}
              className={`ia-alert-item ${selected?.id === a.id ? 'ia-alert-item--selected' : ''}`}
              style={{ borderLeft: `4px solid ${SEV_COLOR[a.severity] || '#94a3b8'}` }}
              onClick={() => handleSelect(a)}
            >
              <div className="ia-alert-title">{a.title}</div>
              <div className="ia-alert-meta">
                <span className="ia-badge" style={{ background: SEV_COLOR[a.severity] + '33', color: SEV_COLOR[a.severity] }}>
                  {a.severity}
                </span>
                <span className="ia-status">{STATUS_LABEL[a.status] || a.status}</span>
                {a.confidence && <span className="ia-confidence">{(a.confidence * 100).toFixed(0)}% confiança</span>}
              </div>
              <div className="ia-alert-time">
                {a.created_at ? new Date(a.created_at).toLocaleString('pt-BR') : '—'}
              </div>
            </div>
          ))}
        </div>

        {/* Detail panel */}
        <div className="ia-detail">
          {selected ? (
            <>
              <h3>{selected.title}</h3>
              <div className="ia-detail-section">
                <div className="ia-detail-row"><span>Status</span><strong>{STATUS_LABEL[selected.status]}</strong></div>
                <div className="ia-detail-row"><span>Severidade</span>
                  <strong style={{ color: SEV_COLOR[selected.severity] }}>{selected.severity}</strong>
                </div>
                {selected.confidence && (
                  <div className="ia-detail-row">
                    <span>Confiança</span>
                    <strong>{(selected.confidence * 100).toFixed(0)}%</strong>
                  </div>
                )}
              </div>

              {rootCause && (
                <div className="ia-detail-section">
                  <h4>🔍 Causa Raiz</h4>
                  <p className="ia-root-cause">{rootCause.root_cause || 'Análise em andamento...'}</p>
                  {rootCause.affected_hosts?.length > 0 && (
                    <>
                      <h4>Hosts Afetados ({rootCause.affected_hosts.length})</h4>
                      <ul className="ia-hosts-list">
                        {rootCause.affected_hosts.map((h, i) => <li key={i}>{h}</li>)}
                      </ul>
                    </>
                  )}
                </div>
              )}

              <div className="ia-detail-section">
                <h4>📋 Timeline</h4>
                <div className="ia-timeline">
                  <div className="ia-timeline-item">
                    <span className="ia-timeline-dot ia-dot-open"></span>
                    <span>Alerta criado: {selected.created_at ? new Date(selected.created_at).toLocaleString('pt-BR') : '—'}</span>
                  </div>
                  {selected.resolved_at && (
                    <div className="ia-timeline-item">
                      <span className="ia-timeline-dot ia-dot-resolved"></span>
                      <span>Resolvido: {new Date(selected.resolved_at).toLocaleString('pt-BR')}</span>
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="ia-detail-hint">Selecione um alerta para ver detalhes, causa raiz e timeline</div>
          )}
        </div>
      </div>
    </div>
  );
}
