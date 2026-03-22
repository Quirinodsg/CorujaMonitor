import React, { useState, useEffect, useCallback } from 'react';
import './ServiceMonitor.css';

const API = `${window.location.protocol}//${window.location.hostname}:8000/api/v1`;

function ServiceMonitor() {
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [services, setServices] = useState([]);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [stats, setStats] = useState({ running: 0, stopped: 0, total: 0 });
  const [error, setError] = useState(null);

  const token = localStorage.getItem('token');

  // Load servers list
  useEffect(() => {
    fetch(`${API}/servers`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => {
        const activeServers = (data || []).filter(s => s.is_active !== false);
        setServers(activeServers);
        if (activeServers.length > 0) {
          setSelectedServer(activeServers[0].id);
        }
      })
      .catch(() => {});
  }, [token]);

  // Fetch services for selected server
  const fetchServices = useCallback(() => {
    if (!selectedServer) return;
    setLoading(true);
    setError(null);

    fetch(`${API}/services/debug?server_id=${selectedServer}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(data => {
        const sensors = data.sensors || [];
        const mapped = sensors.map(s => ({
          sensor_id: s.sensor_id,
          server_id: s.server_id,
          service_name: s.service_name || s.name.replace(/^Service /, ''),
          display_name: s.display_name || s.name.replace(/^Service /, ''),
          state: s.state || (s.is_running ? 'Running' : s.is_running === false ? 'Stopped' : 'Unknown'),
          is_running: s.is_running,
          status: s.last_status || 'unknown',
          last_seen: s.last_seen,
          metric_count: s.metric_count,
        }));

        setServices(mapped);
        const running = mapped.filter(s => s.is_running).length;
        const stopped = mapped.filter(s => !s.is_running && s.status !== 'unknown').length;
        setStats({ running, stopped, total: mapped.length });
        setLastUpdate(new Date());
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [selectedServer, token]);

  // Poll every 10s
  useEffect(() => {
    fetchServices();
    const interval = setInterval(fetchServices, 10000);
    return () => clearInterval(interval);
  }, [fetchServices]);

  const filtered = services.filter(s => {
    if (filter === 'running' && !s.is_running) return false;
    if (filter === 'stopped' && s.is_running !== false) return false;
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
            <p>Serviços Windows (StartMode=Auto) via WMI</p>
          </div>
        </div>
        <div className="sm-status-bar">
          <span className={`sm-ws-dot ${loading ? 'loading' : lastUpdate ? 'connected' : 'disconnected'}`} />
          <span className="sm-ws-label">{loading ? 'Atualizando...' : lastUpdate ? 'Atualizado' : 'Aguardando...'}</span>
          {lastUpdate && (
            <span className="sm-last-update">
              {lastUpdate.toLocaleTimeString('pt-BR')}
            </span>
          )}
          <button className="sm-refresh-btn" onClick={fetchServices} disabled={loading} title="Atualizar agora">
            🔄
          </button>
        </div>
      </div>

      <div className="sm-controls">
        <div className="sm-server-select">
          <label>Servidor</label>
          <select
            value={selectedServer || ''}
            onChange={e => setSelectedServer(Number(e.target.value))}
          >
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
          {['all', 'running', 'stopped'].map(f => (
            <button
              key={f}
              className={`sm-tab ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f === 'all' ? `Todos (${stats.total})` : f === 'running' ? `Rodando (${stats.running})` : `Parados (${stats.stopped})`}
            </button>
          ))}
        </div>
      </div>

      <div className="sm-stats">
        <div className="sm-stat sm-stat--ok">
          <span className="sm-stat-value">{stats.running}</span>
          <span className="sm-stat-label">Rodando</span>
        </div>
        <div className="sm-stat sm-stat--critical">
          <span className="sm-stat-value">{stats.stopped}</span>
          <span className="sm-stat-label">Parados</span>
        </div>
        <div className="sm-stat">
          <span className="sm-stat-value">{stats.total}</span>
          <span className="sm-stat-label">Total</span>
        </div>
        {selectedServerObj && (
          <div className="sm-stat sm-stat--info">
            <span className="sm-stat-value sm-stat-hostname">{selectedServerObj.hostname}</span>
            <span className="sm-stat-label">Servidor</span>
          </div>
        )}
      </div>

      {error && (
        <div className="sm-error">
          ⚠️ Erro ao carregar serviços: {error}
        </div>
      )}

      {!error && filtered.length === 0 ? (
        <div className="sm-empty">
          {loading
            ? 'Carregando serviços...'
            : services.length === 0
              ? 'Nenhum serviço encontrado. A sonda precisa coletar dados deste servidor via WMI.'
              : 'Nenhum serviço encontrado com os filtros aplicados.'}
        </div>
      ) : (
        <div className="sm-table-wrap">
          <table className="sm-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Nome do Serviço</th>
                <th>Estado</th>
                <th>Métricas</th>
                <th>Última Atualização</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(svc => (
                <tr key={svc.sensor_id} className={`sm-row sm-row--${svc.status}`}>
                  <td>
                    <span className={`sm-badge sm-badge--${svc.is_running ? 'ok' : 'critical'}`}>
                      {svc.is_running ? '●' : '●'}
                    </span>
                  </td>
                  <td className="sm-service-name">{svc.service_name}</td>
                  <td>
                    <span className={`sm-state sm-state--${svc.is_running ? 'running' : 'stopped'}`}>
                      {svc.state}
                    </span>
                  </td>
                  <td className="sm-metric-count">{svc.metric_count || 0}</td>
                  <td className="sm-timestamp">
                    {svc.last_seen
                      ? new Date(svc.last_seen).toLocaleTimeString('pt-BR')
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ServiceMonitor;
