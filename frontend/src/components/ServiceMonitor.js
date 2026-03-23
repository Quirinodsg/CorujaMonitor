import React, { useState, useEffect, useCallback } from 'react';
import './ServiceMonitor.css';

const API = '/api/v1';

function ServiceMonitor() {
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [services, setServices] = useState([]);
  const [filter, setFilter] = useState('all'); // all | monitored | unmonitored
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [error, setError] = useState(null);
  const [saveMsg, setSaveMsg] = useState(null);
  // pending changes: sensor_id -> is_active (true/false)
  const [pending, setPending] = useState({});

  const token = localStorage.getItem('token');

  // Load all servers for the tenant, then pick the first one that has service sensors
  useEffect(() => {
    fetch(`${API}/servers`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(async data => {
        const active = (data || []).filter(s => s.is_active !== false);
        setServers(active);
        if (active.length === 0) return;

        // Try to find a server that already has service sensors
        try {
          const res = await fetch(`${API}/services/debug`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          const all = await res.json();
          const serverIdsWithServices = new Set(
            (all.sensors || []).map(s => s.server_id)
          );
          // Pick first server that has services, fallback to first server
          const preferred = active.find(s => serverIdsWithServices.has(s.id));
          setSelectedServer(preferred ? preferred.id : active[0].id);
        } catch {
          setSelectedServer(active[0].id);
        }
      })
      .catch(() => {});
  }, [token]);

  // Fetch service list for selected server (includes inactive sensors = not yet discovered)
  const fetchServices = useCallback(() => {
    if (!selectedServer) return;
    setLoading(true);
    setError(null);

    // /services/debug returns ALL service sensors (active + inactive) for the server
    fetch(`${API}/services/debug?server_id=${selectedServer}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(data => {
        setServices(data.sensors || []);
        setPending({});
        setLastUpdate(new Date());
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [selectedServer, token]);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  // Toggle a single service
  const toggle = (sensorId, currentActive) => {
    setPending(prev => {
      const next = { ...prev };
      const original = services.find(s => s.sensor_id === sensorId)?.is_active;
      const newVal = !currentActive;
      if (newVal === original) {
        delete next[sensorId];
      } else {
        next[sensorId] = newVal;
      }
      return next;
    });
  };

  // Get effective is_active for a sensor (pending overrides saved)
  const effectiveActive = (svc) => {
    if (svc.sensor_id in pending) return pending[svc.sensor_id];
    return svc.is_active;
  };

  // Select all / deselect all (filtered)
  const toggleAll = (value) => {
    const updates = {};
    filtered.forEach(svc => {
      if (effectiveActive(svc) !== value) {
        updates[svc.sensor_id] = value;
      }
    });
    setPending(prev => ({ ...prev, ...updates }));
  };

  // Save changes via PUT /sensors/{id}
  const saveChanges = async () => {
    const entries = Object.entries(pending);
    if (entries.length === 0) return;
    setSaving(true);
    setSaveMsg(null);
    let ok = 0, fail = 0;
    for (const [sensorId, isActive] of entries) {
      try {
        const r = await fetch(`${API}/sensors/${sensorId}`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_active: isActive })
        });
        if (r.ok) ok++;
        else fail++;
      } catch { fail++; }
    }
    setSaving(false);
    setSaveMsg(fail === 0
      ? `✅ ${ok} serviço(s) atualizado(s)`
      : `⚠️ ${ok} ok, ${fail} erro(s)`
    );
    setTimeout(() => setSaveMsg(null), 4000);
    fetchServices();
  };

  // Derived stats
  const monitoredCount = services.filter(s => effectiveActive(s)).length;
  const pendingCount = Object.keys(pending).length;
  const hasDiscovery = services.length > 0;

  const filtered = services.filter(s => {
    const active = effectiveActive(s);
    if (filter === 'monitored' && !active) return false;
    if (filter === 'unmonitored' && active) return false;
    if (search) {
      const q = search.toLowerCase();
      return (s.service_name || '').toLowerCase().includes(q) ||
             (s.display_name || '').toLowerCase().includes(q);
    }
    return true;
  });

  const selectedServerObj = servers.find(s => s.id === selectedServer);

  return (
    <div className="service-monitor">
      <div className="sm-header">
        <div className="sm-title">
          <span className="sm-icon">⚙️</span>
          <div>
            <h2>Monitoramento de Serviços</h2>
            <p>Selecione quais serviços Windows deseja monitorar</p>
          </div>
        </div>
        <div className="sm-status-bar">
          {lastUpdate && (
            <span className="sm-last-update">Atualizado: {lastUpdate.toLocaleTimeString('pt-BR')}</span>
          )}
          <button className="sm-refresh-btn" onClick={fetchServices} disabled={loading} title="Recarregar">
            🔄
          </button>
        </div>
      </div>

      <div className="sm-controls">
        <div className="sm-server-select">
          <label>Servidor</label>
          <select value={selectedServer || ''} onChange={e => { setSelectedServer(Number(e.target.value)); setPending({}); }}>
            {servers.map(s => (
              <option key={s.id} value={s.id}>{s.hostname}</option>
            ))}
          </select>
        </div>

        <div className="sm-search">
          <input
            type="text"
            placeholder="Buscar serviço..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <div className="sm-filter-tabs">
          {[
            { key: 'all', label: `Todos (${services.length})` },
            { key: 'monitored', label: `Monitorados (${monitoredCount})` },
            { key: 'unmonitored', label: `Ignorados (${services.length - monitoredCount})` },
          ].map(f => (
            <button key={f.key} className={`sm-tab ${filter === f.key ? 'active' : ''}`} onClick={() => setFilter(f.key)}>
              {f.label}
            </button>
          ))}
        </div>
      </div>

      <div className="sm-stats">
        <div className="sm-stat sm-stat--ok">
          <span className="sm-stat-value">{monitoredCount}</span>
          <span className="sm-stat-label">Monitorados</span>
        </div>
        <div className="sm-stat">
          <span className="sm-stat-value">{services.length - monitoredCount}</span>
          <span className="sm-stat-label">Ignorados</span>
        </div>
        <div className="sm-stat">
          <span className="sm-stat-value">{services.length}</span>
          <span className="sm-stat-label">Total</span>
        </div>
        {selectedServerObj && (
          <div className="sm-stat sm-stat--info">
            <span className="sm-stat-value sm-stat-hostname">{selectedServerObj.hostname}</span>
            <span className="sm-stat-label">Servidor</span>
          </div>
        )}

        <div className="sm-actions">
          <button className="sm-btn sm-btn--secondary" onClick={() => toggleAll(true)} disabled={saving || !hasDiscovery}>
            Marcar todos
          </button>
          <button className="sm-btn sm-btn--secondary" onClick={() => toggleAll(false)} disabled={saving || !hasDiscovery}>
            Desmarcar todos
          </button>
          <button
            className={`sm-btn sm-btn--primary ${pendingCount === 0 ? 'disabled' : ''}`}
            onClick={saveChanges}
            disabled={saving || pendingCount === 0}
          >
            {saving ? 'Salvando...' : `Salvar${pendingCount > 0 ? ` (${pendingCount})` : ''}`}
          </button>
          {saveMsg && <span className="sm-save-msg">{saveMsg}</span>}
        </div>
      </div>

      {error && <div className="sm-error">⚠️ {error}</div>}

      {/* No discovery yet — guide the user */}
      {!loading && !hasDiscovery && (
        <div className="sm-no-discovery">
          <div className="sm-no-discovery-icon">🔍</div>
          <h3>Nenhum serviço descoberto ainda</h3>
          <p>
            A sonda Windows precisa fazer o discovery via WMI neste servidor.<br />
            Aguarde o próximo ciclo de coleta ou verifique se a credencial WMI está configurada para <strong>{selectedServerObj?.hostname}</strong>.
          </p>
          <div className="sm-no-discovery-steps">
            <div className="sm-step">
              <span className="sm-step-num">1</span>
              <span>Credencial WMI configurada no tenant/grupo/servidor</span>
            </div>
            <div className="sm-step">
              <span className="sm-step-num">2</span>
              <span>Sonda Windows conecta via WMI remoto</span>
            </div>
            <div className="sm-step">
              <span className="sm-step-num">3</span>
              <span>Catálogo de serviços aparece aqui para seleção</span>
            </div>
          </div>
        </div>
      )}

      {loading && services.length === 0 ? (
        <div className="sm-empty">Carregando serviços...</div>
      ) : hasDiscovery && filtered.length === 0 ? (
        <div className="sm-empty">Nenhum serviço encontrado.</div>
      ) : hasDiscovery ? (
        <div className="sm-table-wrap">
          <table className="sm-table">
            <thead>
              <tr>
                <th style={{ width: 48 }}>
                  <input
                    type="checkbox"
                    title="Marcar/desmarcar todos visíveis"
                    checked={filtered.length > 0 && filtered.every(s => effectiveActive(s))}
                    onChange={e => toggleAll(e.target.checked)}
                  />
                </th>
                <th>Nome do Serviço</th>
                <th>Descrição</th>
                <th>Estado Atual</th>
                <th>Última Coleta</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(svc => {
                const active = effectiveActive(svc);
                const changed = svc.sensor_id in pending;
                return (
                  <tr
                    key={svc.sensor_id}
                    className={`sm-row ${changed ? 'sm-row--changed' : ''} ${!active ? 'sm-row--inactive' : ''}`}
                    onClick={() => toggle(svc.sensor_id, active)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td onClick={e => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={active}
                        onChange={() => toggle(svc.sensor_id, active)}
                      />
                    </td>
                    <td className="sm-service-name">{svc.service_name}</td>
                    <td className="sm-display-name">{svc.display_name}</td>
                    <td>
                      {svc.metric_count > 0 ? (
                        <span className={`sm-state sm-state--${svc.is_running ? 'running' : 'stopped'}`}>
                          {svc.state && svc.state !== 'Unknown' ? svc.state : (svc.is_running ? 'Running' : 'Stopped')}
                        </span>
                      ) : (
                        <span className="sm-state sm-state--pending">Aguardando</span>
                      )}
                    </td>
                    <td className="sm-timestamp">
                      {svc.last_seen ? new Date(svc.last_seen).toLocaleTimeString('pt-BR') : '—'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}

export default ServiceMonitor;
