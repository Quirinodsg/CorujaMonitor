import React, { useState, useEffect, useRef, useCallback } from 'react';
import './ServiceMonitor.css';

const API = '/api/v1';

function ServiceMonitor() {
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [services, setServices] = useState([]);
  const [filter, setFilter] = useState('all'); // all | running | stopped
  const [search, setSearch] = useState('');
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [stats, setStats] = useState({ running: 0, stopped: 0, total: 0 });
  const wsRef = useRef(null);

  const token = localStorage.getItem('token');

  // Load servers list
  useEffect(() => {
    fetch(`${API}/servers`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => {
        const wmiServers = (data || []).filter(s => s.monitoring_protocol === 'wmi' && s.is_active);
        setServers(wmiServers);
        if (wmiServers.length > 0 && !selectedServer) {
          setSelectedServer(wmiServers[0].id);
        }
      })
      .catch(() => {});
  }, [token]);

  // WebSocket connection
  const connectWS = useCallback((serverId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host;
    const url = `${proto}://${host}/api/v1/ws/services?token=${token}&server_id=${serverId}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      // Reconnect after 5s
      setTimeout(() => {
        if (wsRef.current === ws) connectWS(serverId);
      }, 5000);
    };
    ws.onerror = () => setConnected(false);
    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.type === 'services') {
          setServices(msg.data || []);
          setStats({ running: msg.running || 0, stopped: msg.stopped || 0, total: msg.count || 0 });
          setLastUpdate(new Date());
        }
      } catch (_) {}
    };
  }, [token]);

  useEffect(() => {
    if (selectedServer) {
      connectWS(selectedServer);
    }
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [selectedServer, connectWS]);

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
          <span className={`sm-ws-dot ${connected ? 'connected' : 'disconnected'}`} />
          <span className="sm-ws-label">{connected ? 'Tempo real' : 'Reconectando...'}</span>
          {lastUpdate && (
            <span className="sm-last-update">
              Atualizado: {lastUpdate.toLocaleTimeString('pt-BR')}
            </span>
          )}
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
              {f === 'all' ? 'Todos' : f === 'running' ? 'Rodando' : 'Parados'}
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
            <span className="sm-stat-value">{selectedServerObj.hostname}</span>
            <span className="sm-stat-label">Servidor</span>
          </div>
        )}
      </div>

      {filtered.length === 0 ? (
        <div className="sm-empty">
          {services.length === 0
            ? 'Aguardando dados do servidor...'
            : 'Nenhum serviço encontrado com os filtros aplicados.'}
        </div>
      ) : (
        <div className="sm-table-wrap">
          <table className="sm-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Nome do Serviço</th>
                <th>Descrição</th>
                <th>Estado</th>
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
                  <td className="sm-display-name">{svc.display_name}</td>
                  <td>
                    <span className={`sm-state sm-state--${svc.is_running ? 'running' : 'stopped'}`}>
                      {svc.state || (svc.is_running ? 'Running' : 'Stopped')}
                    </span>
                  </td>
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
