/**
 * SystemHealth — painel de monitoramento interno do próprio sistema.
 * Mostra: CPU da probe, fila de sensores, latência WMI, taxa de ingestão.
 */
import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './SystemHealth.css';

function MetricGauge({ label, value, max, unit, color }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  const gaugeColor = pct > 80 ? '#ef4444' : pct > 60 ? '#f59e0b' : color || '#10b981';
  return (
    <div className="sh-gauge">
      <div className="sh-gauge-header">
        <span className="sh-gauge-label">{label}</span>
        <span className="sh-gauge-value" style={{ color: gaugeColor }}>
          {value}{unit}
        </span>
      </div>
      <div className="sh-gauge-bar">
        <div className="sh-gauge-fill" style={{ width: `${pct}%`, background: gaugeColor }} />
      </div>
      <div className="sh-gauge-pct">{pct}%</div>
    </div>
  );
}

function SystemHealth({ onNavigate }) {
  const [probeNodes, setProbeNodes] = useState([]);
  const [rateLimiter, setRateLimiter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const load = useCallback(async () => {
    try {
      const [nodesRes] = await Promise.all([
        api.get('/probe-nodes').catch(() => ({ data: { nodes: [] } })),
      ]);
      setProbeNodes(nodesRes.data.nodes || []);
      setLastUpdate(new Date());
    } catch (e) {
      console.error('SystemHealth load error:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, [load]);

  const totalSensors = probeNodes.reduce((s, n) => s + (n.sensors_active || 0), 0);
  const totalCapacity = probeNodes.reduce((s, n) => s + (n.capacity || 0), 0);
  const avgCpu = probeNodes.length
    ? probeNodes.reduce((s, n) => s + (n.cpu_percent || 0), 0) / probeNodes.length
    : 0;
  const avgMem = probeNodes.length
    ? probeNodes.reduce((s, n) => s + (n.memory_mb || 0), 0) / probeNodes.length
    : 0;
  const totalQueue = probeNodes.reduce((s, n) => s + (n.queue_depth || 0), 0);
  const totalWmi = probeNodes.reduce((s, n) => s + (n.wmi_connections || 0), 0);
  const totalSnmp = probeNodes.reduce((s, n) => s + (n.snmp_connections || 0), 0);

  if (loading) return <div className="sh-loading">Carregando métricas do sistema...</div>;

  return (
    <div className="sh-container">
      <div className="sh-header">
        <div>
          <h1>⚙️ Saúde do Sistema</h1>
          <p className="sh-subtitle">
            Monitoramento interno das sondas e pipelines
            {lastUpdate && ` · Atualizado ${lastUpdate.toLocaleTimeString('pt-BR')}`}
          </p>
        </div>
        <button className="sh-btn-refresh" onClick={load}>↻ Atualizar</button>
      </div>

      <div className="sh-overview">
        <div className="sh-kpi">
          <span className="sh-kpi-icon">🔌</span>
          <span className="sh-kpi-value">{probeNodes.filter(n => n.status === 'online').length}/{probeNodes.length}</span>
          <span className="sh-kpi-label">Probes Online</span>
        </div>
        <div className="sh-kpi">
          <span className="sh-kpi-icon">📊</span>
          <span className="sh-kpi-value">{totalSensors}</span>
          <span className="sh-kpi-label">Sensores Ativos</span>
        </div>
        <div className="sh-kpi">
          <span className="sh-kpi-icon">📬</span>
          <span className="sh-kpi-value">{totalQueue}</span>
          <span className="sh-kpi-label">Fila de Sensores</span>
        </div>
        <div className="sh-kpi">
          <span className="sh-kpi-icon">🔗</span>
          <span className="sh-kpi-value">{totalWmi}</span>
          <span className="sh-kpi-label">Conexões WMI</span>
        </div>
        <div className="sh-kpi">
          <span className="sh-kpi-icon">📡</span>
          <span className="sh-kpi-value">{totalSnmp}</span>
          <span className="sh-kpi-label">Conexões SNMP</span>
        </div>
      </div>

      <div className="sh-gauges">
        <MetricGauge label="CPU Média das Probes" value={avgCpu.toFixed(1)} max={100} unit="%" />
        <MetricGauge label="Memória Média" value={avgMem.toFixed(0)} max={4096} unit=" MB" color="#8b5cf6" />
        <MetricGauge label="Sensores Ativos" value={totalSensors} max={totalCapacity || 1000} unit="" color="#3b82f6" />
        <MetricGauge label="Fila de Sensores" value={totalQueue} max={1000} unit="" color="#f59e0b" />
      </div>

      {probeNodes.length > 0 && (
        <div className="sh-nodes-section">
          <h2>Detalhes por Probe</h2>
          <div className="sh-nodes-table">
            <table>
              <thead>
                <tr>
                  <th>Probe</th>
                  <th>Status</th>
                  <th>CPU</th>
                  <th>Memória</th>
                  <th>Sensores</th>
                  <th>Fila</th>
                  <th>WMI</th>
                  <th>SNMP</th>
                  <th>Heartbeat</th>
                </tr>
              </thead>
              <tbody>
                {probeNodes.map(node => (
                  <tr key={node.id} className={node.status === 'offline' ? 'sh-row-offline' : ''}>
                    <td><strong>{node.name}</strong><br /><small>{node.location}</small></td>
                    <td>
                      <span className={`sh-status-badge ${node.status}`}>
                        {node.status === 'online' ? '🟢 Online' : '🔴 Offline'}
                      </span>
                    </td>
                    <td>{node.cpu_percent?.toFixed(1) || 0}%</td>
                    <td>{node.memory_mb?.toFixed(0) || 0} MB</td>
                    <td>{node.sensors_active || 0} / {node.capacity}</td>
                    <td>{node.queue_depth || 0}</td>
                    <td>{node.wmi_connections || 0}</td>
                    <td>{node.snmp_connections || 0}</td>
                    <td className="sh-heartbeat">
                      {node.last_heartbeat
                        ? new Date(node.last_heartbeat).toLocaleTimeString('pt-BR')
                        : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {probeNodes.length === 0 && (
        <div className="sh-no-probes">
          <p>Nenhum probe node registrado.</p>
          <button onClick={() => onNavigate('probe-nodes')}>Adicionar Probe Node</button>
        </div>
      )}
    </div>
  );
}

export default SystemHealth;
