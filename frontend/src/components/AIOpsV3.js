import React, { useState, useEffect } from 'react';
import './AIOpsV3.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function AIOpsV3() {
  const [activities, setActivities] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [actRes, fbRes] = await Promise.all([
          fetch(`${API}/api/v1/ai-activities?limit=20`),
          fetch(`${API}/api/v1/aiops/feedback-metrics`).catch(() => null),
        ]);
        if (actRes.ok) {
          const d = await actRes.json();
          setActivities(d.activities || d || []);
        }
        if (fbRes?.ok) setFeedback(await fbRes.json());
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
    const t = setInterval(fetchAll, 30000);
    return () => clearInterval(t);
  }, []);

  const agentIcon = (name) => {
    const icons = {
      anomaly: '📈', correlation: '🔗', root_cause: '🔍',
      decision: '⚖️', remediation: '🔧', scheduler: '⏱️',
    };
    const key = Object.keys(icons).find(k => (name || '').toLowerCase().includes(k));
    return icons[key] || '🤖';
  };

  const outcomeColor = (outcome) => ({
    positive: '#22c55e', negative: '#ef4444', pending: '#f59e0b'
  })[outcome] || '#94a3b8';

  return (
    <div className="aiops3-container">
      <div className="aiops3-header">
        <h2>🤖 AIOps v3 — Pipeline de Agentes</h2>
      </div>

      {/* Pipeline diagram */}
      <div className="aiops3-pipeline">
        {['Anomaly Detection', 'Correlation', 'Root Cause', 'Decision', 'Auto Remediation'].map((stage, i) => (
          <React.Fragment key={stage}>
            <div className="aiops3-stage">
              <div className="aiops3-stage-icon">{['📈','🔗','🔍','⚖️','🔧'][i]}</div>
              <div className="aiops3-stage-name">{stage}</div>
            </div>
            {i < 4 && <div className="aiops3-arrow">→</div>}
          </React.Fragment>
        ))}
      </div>

      {/* Feedback metrics */}
      {feedback && (
        <div className="aiops3-metrics-row">
          <div className="aiops3-metric-card">
            <div className="aiops3-metric-value">{feedback.actions_total ?? '—'}</div>
            <div className="aiops3-metric-label">Ações Totais</div>
          </div>
          <div className="aiops3-metric-card">
            <div className="aiops3-metric-value" style={{ color: '#22c55e' }}>
              {feedback.actions_successful ?? '—'}
            </div>
            <div className="aiops3-metric-label">Bem-sucedidas</div>
          </div>
          <div className="aiops3-metric-card">
            <div className="aiops3-metric-value" style={{ color: '#60a5fa' }}>
              {feedback.mean_resolution_time_seconds
                ? `${feedback.mean_resolution_time_seconds.toFixed(0)}s`
                : '—'}
            </div>
            <div className="aiops3-metric-label">Tempo Médio Resolução</div>
          </div>
          <div className="aiops3-metric-card">
            <div className="aiops3-metric-value" style={{ color: '#f59e0b' }}>
              {feedback.false_positive_rate != null
                ? `${(feedback.false_positive_rate * 100).toFixed(1)}%`
                : '—'}
            </div>
            <div className="aiops3-metric-label">Taxa Falsos Positivos</div>
          </div>
        </div>
      )}

      {/* Activity log */}
      <div className="aiops3-card">
        <h3>📋 Atividades Recentes dos Agentes</h3>
        {loading && <div className="aiops3-loading">Carregando...</div>}
        {!loading && activities.length === 0 && (
          <div className="aiops3-empty">Nenhuma atividade registrada ainda.</div>
        )}
        <div className="aiops3-activity-list">
          {activities.map((a, i) => (
            <div key={a.id || i} className="aiops3-activity-item">
              <span className="aiops3-activity-icon">{agentIcon(a.agent_name || a.type)}</span>
              <div className="aiops3-activity-body">
                <div className="aiops3-activity-title">
                  {a.agent_name || a.type || 'Agente IA'}
                  {a.action_type && <span className="aiops3-action-type"> · {a.action_type}</span>}
                </div>
                <div className="aiops3-activity-desc">{a.description || a.target_host || a.message || ''}</div>
              </div>
              <div className="aiops3-activity-right">
                {a.outcome && (
                  <span className="aiops3-outcome" style={{ color: outcomeColor(a.outcome) }}>
                    {a.outcome}
                  </span>
                )}
                <div className="aiops3-activity-time">
                  {(a.timestamp || a.created_at)
                    ? new Date(a.timestamp || a.created_at).toLocaleString('pt-BR')
                    : '—'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
