import React, { useState, useEffect, useCallback } from 'react';
import './AIOpsV3.css';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const AGENT_ICONS = {
  anomaly: '📈', correlation: '🔗', root_cause: '🔍',
  rootcause: '🔍', decision: '⚖️', remediation: '🔧',
  autoremediationagent: '🔧', scheduler: '⏱️',
};

function agentIcon(name) {
  const key = Object.keys(AGENT_ICONS).find(k => (name || '').toLowerCase().replace(/\s/g, '').includes(k));
  return AGENT_ICONS[key] || '🤖';
}

function statusColor(s) {
  return { success: '#22c55e', error: '#ef4444', pending: '#f59e0b', positive: '#22c55e', negative: '#ef4444' }[s] || '#94a3b8';
}

export default function AIOpsV3() {
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [runs, setRuns] = useState([]);
  const [logs, setLogs] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [running, setRunning] = useState(false);
  const [lastSimResult, setLastSimResult] = useState(null);
  const [activeTab, setActiveTab] = useState('runs'); // runs | logs

  const fetchAll = useCallback(async () => {
    try {
      const [statusRes, runsRes, logsRes, fbRes] = await Promise.all([
        fetch(`${API}/api/v1/aiops-pipeline/status`),
        fetch(`${API}/api/v1/aiops-pipeline/runs?limit=10`),
        fetch(`${API}/api/v1/aiops-pipeline/logs?limit=30`),
        fetch(`${API}/api/v1/aiops-v3/feedback-metrics`).catch(() => null),
      ]);
      if (statusRes.ok) setPipelineStatus(await statusRes.json());
      if (runsRes.ok) setRuns((await runsRes.json()).runs || []);
      if (logsRes.ok) setLogs((await logsRes.json()).logs || []);
      if (fbRes?.ok) setFeedback(await fbRes.json());
    } catch (e) {
      console.error('AIOpsV3 fetch error:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const t = setInterval(fetchAll, 30000);
    return () => clearInterval(t);
  }, [fetchAll]);

  const handleRunPipeline = async () => {
    setRunning(true);
    try {
      const r = await fetch(`${API}/api/v1/aiops-pipeline/run`, { method: 'POST' });
      if (r.ok) {
        await fetchAll();
      }
    } catch (e) { console.error(e); }
    finally { setRunning(false); }
  };

  const handleSimulate = async () => {
    setSimulating(true);
    setLastSimResult(null);
    try {
      const r = await fetch(
        `${API}/api/v1/aiops-pipeline/simulate?sensor_type=cpu&value=95&host_label=SRV-SIMULADO`,
        { method: 'POST' }
      );
      if (r.ok) {
        const d = await r.json();
        setLastSimResult(d);
        await fetchAll();
      }
    } catch (e) { console.error(e); }
    finally { setSimulating(false); }
  };

  const STAGES = [
    { name: 'Anomaly Detection', icon: '📈' },
    { name: 'Correlation', icon: '🔗' },
    { name: 'Root Cause', icon: '🔍' },
    { name: 'Decision', icon: '⚖️' },
    { name: 'Auto Remediation', icon: '🔧' },
  ];

  return (
    <div className="aiops3-container">
      <div className="aiops3-header">
        <h2>🤖 AIOps v3 — Pipeline de Agentes</h2>
        <div className="aiops3-header-actions">
          <button className="aiops3-btn aiops3-btn--secondary" onClick={handleRunPipeline} disabled={running}>
            {running ? '⏳ Executando...' : '▶ Executar Pipeline'}
          </button>
          <button className="aiops3-btn aiops3-btn--primary" onClick={handleSimulate} disabled={simulating}>
            {simulating ? '⏳ Simulando...' : '🧪 Simular CPU 95%'}
          </button>
        </div>
      </div>

      {/* Pipeline diagram */}
      <div className="aiops3-pipeline">
        {STAGES.map((stage, i) => (
          <React.Fragment key={stage.name}>
            <div className="aiops3-stage">
              <div className="aiops3-stage-icon">{stage.icon}</div>
              <div className="aiops3-stage-name">{stage.name}</div>
            </div>
            {i < STAGES.length - 1 && <div className="aiops3-arrow">→</div>}
          </React.Fragment>
        ))}
      </div>

      {/* Status cards */}
      {pipelineStatus && (
        <div className="aiops3-metrics-row">
          <div className="aiops3-metric-card">
            <div className="aiops3-metric-value">{pipelineStatus.total_runs ?? '—'}</div>
            <div className="aiops3-metric-label">Runs Totais</div>
          </div>
          <div className="aiops3-metric-card">
            <div className="aiops3-metric-value" style={{ color: '#8b5cf6' }}>
              {pipelineStatus.total_intelligent_alerts ?? '—'}
            </div>
            <div className="aiops3-metric-label">Alertas Gerados</div>
          </div>
          <div className="aiops3-metric-card">
            <div className="aiops3-metric-value" style={{ color: '#f59e0b' }}>
              {pipelineStatus.total_remediation_actions ?? '—'}
            </div>
            <div className="aiops3-metric-label">Ações Remediação</div>
          </div>
          {feedback && (
            <div className="aiops3-metric-card">
              <div className="aiops3-metric-value" style={{ color: '#22c55e' }}>
                {feedback.actions_successful ?? '—'}
              </div>
              <div className="aiops3-metric-label">Ações Bem-sucedidas</div>
            </div>
          )}
        </div>
      )}

      {/* Resultado da simulação */}
      {lastSimResult && (
        <div className="aiops3-card aiops3-sim-result">
          <h3>🧪 Resultado da Simulação</h3>
          <div className="aiops3-sim-grid">
            <div><span>Run ID</span><strong>{lastSimResult.run_id?.substring(0, 8)}...</strong></div>
            <div><span>Eventos</span><strong>{lastSimResult.events_processed}</strong></div>
            <div><span>Agentes OK</span><strong>{lastSimResult.agents_success}/{lastSimResult.agents_run}</strong></div>
            <div><span>Alerta gerado</span>
              <strong style={{ color: lastSimResult.should_alert ? '#22c55e' : '#94a3b8' }}>
                {lastSimResult.should_alert ? '✅ Sim' : '— Não'}
              </strong>
            </div>
          </div>
          {lastSimResult.results && (
            <div className="aiops3-sim-agents">
              {lastSimResult.results.map((r, i) => (
                <div key={i} className="aiops3-sim-agent">
                  <span>{agentIcon(r.agent)}</span>
                  <span className="aiops3-sim-agent-name">{r.agent}</span>
                  <span style={{ color: statusColor(r.success ? 'success' : 'error') }}>
                    {r.success ? '✓' : '✗'}
                  </span>
                  {r.error && <span className="aiops3-sim-error">{r.error}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tabs: Runs | Logs */}
      <div className="aiops3-card">
        <div className="aiops3-tabs">
          <button
            className={`aiops3-tab ${activeTab === 'runs' ? 'active' : ''}`}
            onClick={() => setActiveTab('runs')}
          >
            📊 Runs ({runs.length})
          </button>
          <button
            className={`aiops3-tab ${activeTab === 'logs' ? 'active' : ''}`}
            onClick={() => setActiveTab('logs')}
          >
            📋 Logs de Agentes ({logs.length})
          </button>
        </div>

        {loading && <div className="aiops3-loading">Carregando...</div>}

        {/* Runs */}
        {!loading && activeTab === 'runs' && (
          <>
            {runs.length === 0 ? (
              <div className="aiops3-empty">
                Nenhum run registrado ainda. Clique em "Executar Pipeline" ou "Simular CPU 95%".
              </div>
            ) : (
              <div className="aiops3-runs-list">
                {runs.map((run, i) => (
                  <div key={run.run_id || i} className="aiops3-run-item">
                    <div className="aiops3-run-id">
                      <span className="aiops3-run-badge">run</span>
                      {run.run_id?.substring(0, 12)}...
                    </div>
                    <div className="aiops3-run-agents">
                      {(run.agents || []).map((a, j) => (
                        <span key={j} className="aiops3-run-agent-chip">{agentIcon(a)} {a.replace('Agent', '')}</span>
                      ))}
                    </div>
                    <div className="aiops3-run-stats">
                      <span style={{ color: '#22c55e' }}>{run.agents_success}✓</span>
                      {run.agents_error > 0 && <span style={{ color: '#ef4444' }}> {run.agents_error}✗</span>}
                    </div>
                    <div className="aiops3-run-time">
                      {run.started_at ? new Date(run.started_at).toLocaleString('pt-BR') : '—'}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Logs */}
        {!loading && activeTab === 'logs' && (
          <>
            {logs.length === 0 ? (
              <div className="aiops3-empty">Nenhum log de agente registrado ainda.</div>
            ) : (
              <div className="aiops3-activity-list">
                {logs.map((log, i) => (
                  <div key={log.id || i} className="aiops3-activity-item">
                    <span className="aiops3-activity-icon">{agentIcon(log.agent_name)}</span>
                    <div className="aiops3-activity-body">
                      <div className="aiops3-activity-title">
                        {log.agent_name}
                        <span className="aiops3-action-type"> · run {log.run_id?.substring(0, 8)}</span>
                      </div>
                      <div className="aiops3-activity-desc">
                        {log.error || (log.output ? JSON.stringify(log.output).substring(0, 80) + '...' : '—')}
                      </div>
                    </div>
                    <div className="aiops3-activity-right">
                      <span style={{ color: statusColor(log.status) }}>
                        {log.status === 'success' ? '✓' : '✗'} {log.status}
                      </span>
                      <div className="aiops3-activity-time">
                        {log.timestamp ? new Date(log.timestamp).toLocaleString('pt-BR') : '—'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
