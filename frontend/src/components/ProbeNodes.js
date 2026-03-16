import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './ProbeNodes.css';

function ProbeNodes({ onNavigate }) {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newNode, setNewNode] = useState({ name: '', location: '', version: '2.0', capacity: 500 });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    try {
      const res = await api.get('/probe-nodes');
      setNodes(res.data.nodes || []);
    } catch (e) {
      console.error('Erro ao carregar probe nodes:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, [load]);

  const handleAdd = async () => {
    if (!newNode.name.trim()) return;
    setSaving(true);
    try {
      await api.post('/probe-nodes/register', newNode);
      setShowAddModal(false);
      setNewNode({ name: '', location: '', version: '2.0', capacity: 500 });
      load();
    } catch (e) {
      alert('Erro ao registrar probe: ' + (e.response?.data?.detail || e.message));
    } finally {
      setSaving(false);
    }
  };

  const handleRemove = async (nodeId) => {
    if (!window.confirm('Remover este probe node?')) return;
    try {
      await api.delete(`/probe-nodes/${nodeId}`);
      load();
    } catch (e) {
      alert('Erro ao remover: ' + (e.response?.data?.detail || e.message));
    }
  };

  const statusColor = (s) => s === 'online' ? '#10b981' : '#ef4444';
  const statusIcon = (s) => s === 'online' ? '🟢' : '🔴';

  const utilizationPct = (node) => {
    if (!node.capacity) return 0;
    return Math.round((node.sensors_active / node.capacity) * 100);
  };

  if (loading) return <div className="pn-loading">Carregando probe nodes...</div>;

  return (
    <div className="pn-container">
      <div className="pn-header">
        <div>
          <h1>🔌 Probe Nodes</h1>
          <p className="pn-subtitle">Gerenciamento de sondas de monitoramento distribuídas</p>
        </div>
        <button className="pn-btn-add" onClick={() => setShowAddModal(true)}>
          + Adicionar Probe
        </button>
      </div>

      <div className="pn-summary">
        <div className="pn-stat">
          <span className="pn-stat-value">{nodes.length}</span>
          <span className="pn-stat-label">Total</span>
        </div>
        <div className="pn-stat online">
          <span className="pn-stat-value">{nodes.filter(n => n.status === 'online').length}</span>
          <span className="pn-stat-label">Online</span>
        </div>
        <div className="pn-stat offline">
          <span className="pn-stat-value">{nodes.filter(n => n.status === 'offline').length}</span>
          <span className="pn-stat-label">Offline</span>
        </div>
        <div className="pn-stat">
          <span className="pn-stat-value">{nodes.reduce((s, n) => s + (n.sensors_active || 0), 0)}</span>
          <span className="pn-stat-label">Sensores Ativos</span>
        </div>
      </div>

      {nodes.length === 0 ? (
        <div className="pn-empty">
          <p>Nenhum probe node registrado.</p>
          <p>Adicione um probe para começar o monitoramento distribuído.</p>
        </div>
      ) : (
        <div className="pn-grid">
          {nodes.map(node => (
            <div key={node.id} className={`pn-card ${node.status}`}>
              <div className="pn-card-header">
                <div className="pn-card-title">
                  <span className="pn-status-icon">{statusIcon(node.status)}</span>
                  <h3>{node.name}</h3>
                </div>
                <span className="pn-version">v{node.version}</span>
              </div>

              <div className="pn-card-body">
                <div className="pn-info-row">
                  <span className="pn-label">📍 Localização</span>
                  <span className="pn-value">{node.location || '—'}</span>
                </div>
                <div className="pn-info-row">
                  <span className="pn-label">📊 Sensores</span>
                  <span className="pn-value">{node.sensors_active} / {node.capacity}</span>
                </div>
                <div className="pn-info-row">
                  <span className="pn-label">🖥️ Servidores</span>
                  <span className="pn-value">{node.servers_monitored}</span>
                </div>
                <div className="pn-info-row">
                  <span className="pn-label">⚡ CPU</span>
                  <span className="pn-value">{node.cpu_percent?.toFixed(1) || 0}%</span>
                </div>
                <div className="pn-info-row">
                  <span className="pn-label">💾 Memória</span>
                  <span className="pn-value">{node.memory_mb?.toFixed(0) || 0} MB</span>
                </div>
                <div className="pn-info-row">
                  <span className="pn-label">🕐 Heartbeat</span>
                  <span className="pn-value pn-heartbeat">
                    {node.last_heartbeat
                      ? new Date(node.last_heartbeat).toLocaleString('pt-BR')
                      : '—'}
                  </span>
                </div>

                <div className="pn-utilization">
                  <div className="pn-util-label">
                    <span>Utilização</span>
                    <span>{utilizationPct(node)}%</span>
                  </div>
                  <div className="pn-util-bar">
                    <div
                      className="pn-util-fill"
                      style={{
                        width: `${utilizationPct(node)}%`,
                        backgroundColor: utilizationPct(node) > 80 ? '#ef4444' : utilizationPct(node) > 60 ? '#f59e0b' : '#10b981'
                      }}
                    />
                  </div>
                </div>
              </div>

              <div className="pn-card-footer">
                <button className="pn-btn-remove" onClick={() => handleRemove(node.id)}>
                  Remover
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showAddModal && (
        <div className="pn-modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="pn-modal" onClick={e => e.stopPropagation()}>
            <h2>Adicionar Probe Node</h2>
            <div className="pn-form">
              <label>Nome *</label>
              <input
                value={newNode.name}
                onChange={e => setNewNode({ ...newNode, name: e.target.value })}
                placeholder="ex: SRVSONDA001"
              />
              <label>Localização</label>
              <input
                value={newNode.location}
                onChange={e => setNewNode({ ...newNode, location: e.target.value })}
                placeholder="ex: Datacenter SP"
              />
              <label>Versão</label>
              <input
                value={newNode.version}
                onChange={e => setNewNode({ ...newNode, version: e.target.value })}
              />
              <label>Capacidade (sensores)</label>
              <input
                type="number"
                value={newNode.capacity}
                onChange={e => setNewNode({ ...newNode, capacity: parseInt(e.target.value) || 500 })}
              />
            </div>
            <div className="pn-modal-actions">
              <button className="pn-btn-cancel" onClick={() => setShowAddModal(false)}>Cancelar</button>
              <button className="pn-btn-save" onClick={handleAdd} disabled={saving}>
                {saving ? 'Salvando...' : 'Registrar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProbeNodes;
