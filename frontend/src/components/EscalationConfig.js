import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './EscalationConfig.css';

const E164_REGEX = /^\+[1-9]\d{1,14}$/;

function EscalationConfig() {
  // ── Config state ──
  const [config, setConfig] = useState({
    enabled: false,
    mode: 'sequential',
    interval_minutes: 5,
    max_attempts: 10,
    call_duration_seconds: 30,
    phone_chain: [],
  });
  const [configMsg, setConfigMsg] = useState({ text: '', type: '' });
  const [savingConfig, setSavingConfig] = useState(false);

  // ── Phone chain add form ──
  const [newName, setNewName] = useState('');
  const [newNumber, setNewNumber] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [testCallLoading, setTestCallLoading] = useState(null);
  const [testCallMsg, setTestCallMsg] = useState({ text: '', type: '' });
  const [editingIndex, setEditingIndex] = useState(null);
  const [editName, setEditName] = useState('');
  const [editNumber, setEditNumber] = useState('');

  // ── Resources state ──
  const [resources, setResources] = useState([]);
  const [resourceSearch, setResourceSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [savingResources, setSavingResources] = useState(false);
  const [resourceMsg, setResourceMsg] = useState({ text: '', type: '' });

  // ── Active alarms ──
  const [alarms, setAlarms] = useState([]);
  const [alarmsLoading, setAlarmsLoading] = useState(true);
  const [ackLoading, setAckLoading] = useState(null);

  // ── History ──
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  // ── Loading ──
  const [loading, setLoading] = useState(true);

  // ─────────────────────────────────────────────────────────
  // Load config + resources
  // ─────────────────────────────────────────────────────────
  const loadConfig = useCallback(async () => {
    try {
      const res = await api.get('/escalation/config');
      setConfig(res.data);
    } catch (e) {
      console.error('Erro ao carregar config de escalação:', e);
    }
  }, []);

  const loadResources = useCallback(async () => {
    try {
      const res = await api.get('/escalation/resources');
      setResources(res.data.resources || []);
    } catch (e) {
      console.error('Erro ao carregar recursos:', e);
    }
  }, []);

  const loadAlarms = useCallback(async () => {
    try {
      const res = await api.get('/escalation/active');
      setAlarms(res.data || []);
    } catch (e) {
      console.error('Erro ao carregar alarmes ativos:', e);
    } finally {
      setAlarmsLoading(false);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const res = await api.get('/escalation/history?limit=20');
      setHistory(res.data || []);
    } catch (e) {
      console.error('Erro ao carregar histórico:', e);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    Promise.all([loadConfig(), loadResources(), loadAlarms(), loadHistory()])
      .finally(() => setLoading(false));
  }, [loadConfig, loadResources, loadAlarms, loadHistory]);

  // Polling alarms every 10s
  useEffect(() => {
    const interval = setInterval(() => {
      loadAlarms();
      loadHistory();
    }, 10000);
    return () => clearInterval(interval);
  }, [loadAlarms, loadHistory]);

  // ─────────────────────────────────────────────────────────
  // Save config
  // ─────────────────────────────────────────────────────────
  const saveConfig = async () => {
    // Client-side validation
    if (config.interval_minutes < 1 || config.interval_minutes > 60) {
      setConfigMsg({ text: 'Intervalo deve ser entre 1 e 60 minutos', type: 'error' });
      return;
    }
    if (config.max_attempts < 1 || config.max_attempts > 100) {
      setConfigMsg({ text: 'Retentativas deve ser entre 1 e 100', type: 'error' });
      return;
    }
    if (config.call_duration_seconds < 10 || config.call_duration_seconds > 120) {
      setConfigMsg({ text: 'Duração deve ser entre 10 e 120 segundos', type: 'error' });
      return;
    }

    setSavingConfig(true);
    setConfigMsg({ text: '', type: '' });
    try {
      await api.put('/escalation/config', config);
      setConfigMsg({ text: 'Configuração salva com sucesso', type: 'success' });
      setTimeout(() => setConfigMsg({ text: '', type: '' }), 3000);
    } catch (e) {
      const detail = e.response?.data?.detail || 'Erro ao salvar configuração';
      setConfigMsg({ text: detail, type: 'error' });
    } finally {
      setSavingConfig(false);
    }
  };

  // ─────────────────────────────────────────────────────────
  // Phone chain management
  // ─────────────────────────────────────────────────────────
  const addPhone = () => {
    setPhoneError('');
    if (!newName.trim()) { setPhoneError('Nome é obrigatório'); return; }
    if (!E164_REGEX.test(newNumber)) {
      setPhoneError('Número inválido. Use formato E.164: +5511999999999');
      return;
    }
    const updated = [...config.phone_chain, { name: newName.trim(), number: newNumber.trim(), order: config.phone_chain.length + 1 }];
    setConfig({ ...config, phone_chain: updated });
    setNewName('');
    setNewNumber('');
  };

  const removePhone = (index) => {
    const updated = config.phone_chain.filter((_, i) => i !== index)
      .map((p, i) => ({ ...p, order: i + 1 }));
    setConfig({ ...config, phone_chain: updated });
  };

  const movePhone = (index, direction) => {
    const arr = [...config.phone_chain];
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= arr.length) return;
    [arr[index], arr[newIndex]] = [arr[newIndex], arr[index]];
    setConfig({ ...config, phone_chain: arr.map((p, i) => ({ ...p, order: i + 1 })) });
  };

  const startEdit = (index) => {
    setEditingIndex(index);
    setEditName(config.phone_chain[index].name);
    setEditNumber(config.phone_chain[index].number);
    setPhoneError('');
  };

  const cancelEdit = () => {
    setEditingIndex(null);
    setEditName('');
    setEditNumber('');
    setPhoneError('');
  };

  const saveEdit = () => {
    if (!editName.trim()) { setPhoneError('Nome é obrigatório'); return; }
    if (!E164_REGEX.test(editNumber)) { setPhoneError('Número inválido. Use formato E.164: +5511999999999'); return; }
    const updated = config.phone_chain.map((p, i) =>
      i === editingIndex ? { ...p, name: editName.trim(), number: editNumber.trim() } : p
    );
    setConfig({ ...config, phone_chain: updated });
    setEditingIndex(null);
    setEditName('');
    setEditNumber('');
    setPhoneError('');
  };

  const testCall = async (number) => {
    setTestCallLoading(number);
    setTestCallMsg({ text: '', type: '' });
    try {
      await api.post('/escalation/test-call', { number });
      setTestCallMsg({ text: `Ligação de teste enviada para ${number}`, type: 'success' });
      setTimeout(() => setTestCallMsg({ text: '', type: '' }), 5000);
    } catch (e) {
      const detail = e.response?.data?.detail || 'Erro ao fazer ligação de teste';
      setTestCallMsg({ text: detail, type: 'error' });
    } finally {
      setTestCallLoading(null);
    }
  };

  // ─────────────────────────────────────────────────────────
  // Resources management
  // ─────────────────────────────────────────────────────────
  const searchResources = async (query) => {
    setResourceSearch(query);
    if (query.length < 2) { setSearchResults([]); return; }
    try {
      const res = await api.get(`/escalation/resources/search?q=${encodeURIComponent(query)}`);
      const items = res.data || [];
      // Filter out already added
      const existingIds = new Set(resources.map(r => `${r.type}:${r.id}`));
      setSearchResults(items.filter(r => !existingIds.has(`${r.type}:${r.id}`)).slice(0, 15));
    } catch (e) {
      console.error('Erro ao buscar recursos:', e);
      setSearchResults([]);
    }
  };

  const addResource = async (resource) => {
    const updated = [...resources, resource];
    setSavingResources(true);
    setResourceMsg({ text: '', type: '' });
    try {
      await api.put('/escalation/resources', { resources: updated });
      setResources(updated);
      setSearchResults(searchResults.filter(r => !(r.type === resource.type && r.id === resource.id)));
      setResourceMsg({ text: 'Recurso adicionado', type: 'success' });
      setTimeout(() => setResourceMsg({ text: '', type: '' }), 2000);
    } catch (e) {
      const detail = e.response?.data?.detail || 'Erro ao adicionar recurso';
      setResourceMsg({ text: detail, type: 'error' });
    } finally {
      setSavingResources(false);
    }
  };

  const removeResource = async (index) => {
    const updated = resources.filter((_, i) => i !== index);
    setSavingResources(true);
    try {
      await api.put('/escalation/resources', { resources: updated });
      setResources(updated);
    } catch (e) {
      console.error('Erro ao remover recurso:', e);
    } finally {
      setSavingResources(false);
    }
  };

  // ─────────────────────────────────────────────────────────
  // Acknowledge alarm
  // ─────────────────────────────────────────────────────────
  const acknowledgeAlarm = async (sensorId) => {
    setAckLoading(sensorId);
    try {
      await api.post(`/escalation/${sensorId}/acknowledge`, { notes: '' });
      loadAlarms();
      loadHistory();
    } catch (e) {
      console.error('Erro ao reconhecer alarme:', e);
    } finally {
      setAckLoading(null);
    }
  };

  // ─────────────────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────────────────
  const formatDate = (iso) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
    } catch { return iso; }
  };

  const reasonLabel = (reason) => {
    const map = { acknowledged: 'Reconhecido', expired: 'Expirado', resolved: 'Resolvido', resource_removed: 'Recurso removido' };
    return map[reason] || reason || '—';
  };

  if (loading) {
    return (
      <div className="escalation-page">
        <div className="esc-loading"><div className="spinner" /><p>Carregando escalação...</p></div>
      </div>
    );
  }

  return (
    <div className="escalation-page">
      <h2>📞 Escalação Contínua de Alarmes</h2>

      {/* ── 1. Configuração ── */}
      <div className="esc-section">
        <h3>⚙️ Configuração</h3>
        <div className="esc-config-grid">
          <div className="esc-field">
            <label>Modo de Chamada</label>
            <div className="esc-mode-toggle">
              <button
                className={config.mode === 'sequential' ? 'active' : ''}
                onClick={() => setConfig({ ...config, mode: 'sequential' })}
              >🔄 Sequencial</button>
              <button
                className={config.mode === 'simultaneous' ? 'active' : ''}
                onClick={() => setConfig({ ...config, mode: 'simultaneous' })}
              >📢 Simultâneo</button>
            </div>
          </div>
          <div className="esc-field">
            <label>Intervalo entre ciclos</label>
            <input
              type="range" min="1" max="60"
              value={config.interval_minutes}
              onChange={e => setConfig({ ...config, interval_minutes: parseInt(e.target.value) })}
            />
            <span className="esc-field-value">{config.interval_minutes} min</span>
          </div>
          <div className="esc-field">
            <label>Máximo de retentativas</label>
            <input
              type="range" min="1" max="100"
              value={config.max_attempts}
              onChange={e => setConfig({ ...config, max_attempts: parseInt(e.target.value) })}
            />
            <span className="esc-field-value">{config.max_attempts}x</span>
          </div>
          <div className="esc-field">
            <label>Duração da chamada</label>
            <input
              type="range" min="10" max="120"
              value={config.call_duration_seconds}
              onChange={e => setConfig({ ...config, call_duration_seconds: parseInt(e.target.value) })}
            />
            <span className="esc-field-value">{config.call_duration_seconds}s</span>
          </div>
        </div>
        <div className="esc-save-row">
          {configMsg.text && <span className={`esc-msg ${configMsg.type}`}>{configMsg.text}</span>}
          <button className="ds-btn ds-btn--primary" onClick={saveConfig} disabled={savingConfig}>
            {savingConfig ? 'Salvando...' : '💾 Salvar Configuração'}
          </button>
        </div>
      </div>

      {/* ── 2. Cadeia de Escalação ── */}
      <div className="esc-section">
        <h3>📱 Cadeia de Escalação ({config.phone_chain.length} contatos)</h3>
        {config.phone_chain.length > 0 ? (
          <div className="esc-phone-list">
            {config.phone_chain.map((phone, i) => (
              <div className="esc-phone-item" key={i}>
                <span className="esc-phone-order">#{i + 1}</span>
                {editingIndex === i ? (
                  <>
                    <div className="esc-phone-info" style={{ flex: 1, display: 'flex', gap: 8 }}>
                      <input type="text" value={editName} onChange={e => setEditName(e.target.value)} placeholder="Nome" style={{ flex: 1, background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--primary)', borderRadius: 4, padding: '4px 8px', fontSize: 13 }} />
                      <input type="text" value={editNumber} onChange={e => setEditNumber(e.target.value)} placeholder="+5511999999999" style={{ flex: 1, background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: '1px solid var(--primary)', borderRadius: 4, padding: '4px 8px', fontSize: 13, fontFamily: 'var(--font-mono)' }} />
                    </div>
                    <div className="esc-phone-actions">
                      <button onClick={saveEdit} title="Salvar" style={{ color: 'var(--success)' }}>✓</button>
                      <button onClick={cancelEdit} title="Cancelar">✕</button>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="esc-phone-info">
                      <span className="esc-phone-name">{phone.name}</span>
                      <span className="esc-phone-number">{phone.number}</span>
                    </div>
                    <div className="esc-phone-actions">
                      <button onClick={() => testCall(phone.number)} disabled={testCallLoading === phone.number} title="Testar ligação">
                        {testCallLoading === phone.number ? '⏳' : '📞'}
                      </button>
                      <button onClick={() => startEdit(i)} title="Editar">✏️</button>
                      <button onClick={() => movePhone(i, -1)} disabled={i === 0} title="Mover para cima">▲</button>
                      <button onClick={() => movePhone(i, 1)} disabled={i === config.phone_chain.length - 1} title="Mover para baixo">▼</button>
                      <button className="remove" onClick={() => removePhone(i)} title="Remover">✕</button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="esc-empty">
            <div className="esc-empty-icon">📵</div>
            <p>Nenhum contato na cadeia de escalação</p>
          </div>
        )}
        <div className="esc-add-phone">
          <input
            type="text"
            placeholder="Nome do contato"
            value={newName}
            onChange={e => setNewName(e.target.value)}
            style={{ flex: 1 }}
          />
          <input
            type="text"
            placeholder="+5511999999999"
            value={newNumber}
            onChange={e => setNewNumber(e.target.value)}
            className={phoneError ? 'invalid' : ''}
            style={{ flex: 1 }}
          />
          <button className="ds-btn ds-btn--primary" onClick={addPhone}>+ Adicionar</button>
        </div>
        {phoneError && <span className="esc-msg error" style={{ marginTop: 8, display: 'block' }}>{phoneError}</span>}
        {testCallMsg.text && <span className={`esc-msg ${testCallMsg.type}`} style={{ marginTop: 8, display: 'block' }}>{testCallMsg.text}</span>}
      </div>

      {/* ── 3. Recursos Monitorados ── */}
      <div className="esc-section">
        <h3>🖥️ Recursos Monitorados para Escalação ({resources.length})</h3>
        <div className="esc-resource-search">
          <input
            type="text"
            placeholder="Buscar servidor ou sensor por nome..."
            value={resourceSearch}
            onChange={e => searchResources(e.target.value)}
          />
        </div>
        {searchResults.length > 0 && (
          <div className="esc-resource-results">
            {searchResults.map(r => (
              <div className="esc-resource-result-item" key={`${r.type}-${r.id}`} onClick={() => addResource(r)}>
                <span>{r.type === 'server' ? '🖥️' : '📡'} {r.name}</span>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{r.type === 'server' ? 'Servidor' : 'Sensor'}</span>
              </div>
            ))}
          </div>
        )}
        {resourceMsg.text && <span className={`esc-msg ${resourceMsg.type}`} style={{ marginBottom: 8, display: 'block' }}>{resourceMsg.text}</span>}
        {resources.length > 0 ? (
          <div className="esc-resource-list">
            {resources.map((r, i) => (
              <div className="esc-resource-item" key={`${r.type}-${r.id}`}>
                <span className="res-icon">{r.type === 'server' ? '🖥️' : '📡'}</span>
                <div className="res-info">
                  <div className="res-name">{r.name}</div>
                  <div className="res-type">{r.type === 'server' ? 'Servidor' : 'Sensor'} · ID {r.id}</div>
                </div>
                <button
                  className="ds-btn ds-btn--danger"
                  style={{ padding: '4px 10px', fontSize: 12 }}
                  onClick={() => removeResource(i)}
                  disabled={savingResources}
                >✕ Remover</button>
              </div>
            ))}
          </div>
        ) : (
          <div className="esc-empty">
            <div className="esc-empty-icon">📋</div>
            <p>Nenhum recurso configurado para escalação</p>
          </div>
        )}
      </div>

      {/* ── 4. Alarmes Ativos ── */}
      <div className="esc-section">
        <h3>
          🚨 Alarmes Ativos ({alarms.length})
          <span className="esc-live-indicator">
            <span className="esc-live-dot" />
            Atualização a cada 10s
          </span>
        </h3>
        {alarmsLoading ? (
          <div className="esc-loading"><div className="spinner" /><p>Carregando alarmes...</p></div>
        ) : alarms.length > 0 ? (
          <div className="esc-alarms-list">
            {alarms.map(alarm => (
              <div className="esc-alarm-item" key={alarm.sensor_id}>
                <div className="esc-alarm-info">
                  <span className="esc-alarm-sensor">{alarm.sensor_name}</span>
                  <span className="esc-alarm-desc">
                    {alarm.device_type && <span className="esc-badge active" style={{ marginRight: 8 }}>{alarm.device_type}</span>}
                    {alarm.problem_description || 'Alarme crítico'}
                  </span>
                  <div className="esc-alarm-meta">
                    <span>Início: {formatDate(alarm.started_at)}</span>
                    <span>Tentativas: {alarm.attempt_count}/{alarm.max_attempts}</span>
                    <span>Próxima: {formatDate(alarm.next_attempt_at)}</span>
                    <span>Modo: {alarm.mode === 'simultaneous' ? 'Simultâneo' : 'Sequencial'}</span>
                  </div>
                </div>
                <button
                  className="ds-btn ds-btn--primary"
                  onClick={() => acknowledgeAlarm(alarm.sensor_id)}
                  disabled={ackLoading === alarm.sensor_id}
                >
                  {ackLoading === alarm.sensor_id ? '⏳...' : '✅ Reconhecer'}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="esc-empty">
            <div className="esc-empty-icon">✅</div>
            <p>Nenhum alarme ativo em escalação</p>
          </div>
        )}
      </div>

      {/* ── 5. Histórico Recente ── */}
      <div className="esc-section">
        <h3>📜 Histórico Recente</h3>
        {historyLoading ? (
          <div className="esc-loading"><div className="spinner" /><p>Carregando histórico...</p></div>
        ) : history.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table className="esc-history-table">
              <thead>
                <tr>
                  <th>Sensor</th>
                  <th>Severidade</th>
                  <th>Motivo</th>
                  <th>Tentativas</th>
                  <th>Início</th>
                  <th>Fim</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i}>
                    <td>{h.sensor_name}</td>
                    <td><span className={`esc-badge ${h.severity === 'critical' ? 'active' : h.severity === 'warning' ? 'expired' : 'resolved'}`}>{h.severity || '—'}</span></td>
                    <td><span className={`esc-badge ${h.reason}`}>{reasonLabel(h.reason)}</span></td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{h.attempt_count || 0}</td>
                    <td>{formatDate(h.started_at)}</td>
                    <td>{formatDate(h.ended_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="esc-empty">
            <div className="esc-empty-icon">📭</div>
            <p>Nenhum histórico de escalação</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default EscalationConfig;
