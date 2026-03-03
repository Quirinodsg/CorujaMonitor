import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Management.css';

function Probes() {
  const [probes, setProbes] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [probeToDelete, setProbeToDelete] = useState(null);
  const [newProbe, setNewProbe] = useState(null);
  const [formData, setFormData] = useState({ name: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProbes();
  }, []);

  const loadProbes = async () => {
    try {
      const response = await api.get('/api/v1/probes');
      setProbes(response.data);
    } catch (error) {
      console.error('Erro ao carregar probes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/api/v1/probes', formData);
      setNewProbe(response.data);
      setShowModal(false);
      setShowTokenModal(true);
      setFormData({ name: '' });
      loadProbes();
    } catch (error) {
      alert('Erro ao criar probe: ' + (error.response?.data?.detail || error.message));
    }
  };

  const copyToken = () => {
    navigator.clipboard.writeText(newProbe.token);
    alert('Token copiado!');
  };

  const handleDeleteClick = (probe) => {
    setProbeToDelete(probe);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await api.delete(`/api/v1/probes/${probeToDelete.id}`);
      setShowDeleteModal(false);
      setProbeToDelete(null);
      loadProbes();
      alert('Probe excluído com sucesso!');
    } catch (error) {
      alert('Erro ao excluir probe: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getStatusColor = (lastHeartbeat) => {
    if (!lastHeartbeat) return 'gray';
    const diff = Date.now() - new Date(lastHeartbeat).getTime();
    if (diff < 120000) return 'green'; // < 2 min
    if (diff < 300000) return 'orange'; // < 5 min
    return 'red';
  };

  if (loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="management-page">
      <div className="page-header">
        <h1>🔌 Probes</h1>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + Novo Probe
        </button>
      </div>

      <div className="cards-grid">
        {probes.map(probe => (
          <div key={probe.id} className="card">
            <div className="card-header">
              <h3>{probe.name}</h3>
              <span 
                className="status-dot" 
                style={{ backgroundColor: getStatusColor(probe.last_heartbeat) }}
                title={probe.last_heartbeat ? `Último contato: ${new Date(probe.last_heartbeat).toLocaleString('pt-BR')}` : 'Nunca conectou'}
              />
            </div>
            <div className="card-body">
              <p><strong>ID:</strong> {probe.id}</p>
              <p><strong>Versão:</strong> {probe.version || 'N/A'}</p>
              <p><strong>Último contato:</strong> {probe.last_heartbeat ? new Date(probe.last_heartbeat).toLocaleString('pt-BR') : 'Nunca'}</p>
              <p><strong>Status:</strong> {probe.is_active ? '✅ Ativo' : '❌ Inativo'}</p>
            </div>
            <div className="card-footer" style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', padding: '12px', borderTop: '1px solid #e5e7eb' }}>
              <button 
                className="btn-danger"
                onClick={() => handleDeleteClick(probe)}
                style={{
                  padding: '8px 16px',
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.target.style.background = '#dc2626'}
                onMouseLeave={(e) => e.target.style.background = '#ef4444'}
              >
                🗑️ Excluir
              </button>
            </div>
          </div>
        ))}
      </div>

      {showDeleteModal && probeToDelete && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h2>⚠️ Confirmar Exclusão</h2>
              <button className="btn-close" onClick={() => setShowDeleteModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="alert alert-warning" style={{ background: '#fef3c7', border: '1px solid #fbbf24', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
                <strong>Atenção!</strong> Esta ação não pode ser desfeita.
              </div>
              <p>Você tem certeza que deseja excluir o probe:</p>
              <div style={{ background: '#f3f4f6', padding: '12px', borderRadius: '6px', margin: '12px 0' }}>
                <strong>{probeToDelete.name}</strong>
                <br />
                <small style={{ color: '#6b7280' }}>ID: {probeToDelete.id}</small>
              </div>
              <p style={{ color: '#ef4444', fontSize: '14px' }}>
                ⚠️ Todos os dados associados a este probe serão perdidos.
              </p>
            </div>
            <div className="modal-footer">
              <button 
                type="button" 
                className="btn-secondary" 
                onClick={() => setShowDeleteModal(false)}
              >
                Cancelar
              </button>
              <button 
                type="button" 
                className="btn-danger"
                onClick={handleDeleteConfirm}
                style={{
                  background: '#ef4444',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Sim, Excluir Probe
              </button>
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Novo Probe</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nome do Probe</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                  required
                  placeholder="Ex: Probe - Matriz"
                />
                <small>Identifique o local ou cliente deste probe</small>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  Criar Probe
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showTokenModal && newProbe && (
        <div className="modal-overlay">
          <div className="modal" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h2>✅ Probe Criado com Sucesso!</h2>
            </div>
            <div className="modal-body">
              <div className="alert alert-warning">
                <strong>⚠️ IMPORTANTE:</strong> Copie este token agora! Ele não será mostrado novamente.
              </div>
              <div className="form-group">
                <label>Token do Probe</label>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <input
                    type="text"
                    value={newProbe.token}
                    readOnly
                    style={{ flex: 1, fontFamily: 'monospace', fontSize: '12px' }}
                  />
                  <button type="button" className="btn-primary" onClick={copyToken}>
                    📋 Copiar
                  </button>
                </div>
              </div>
              <div className="info-box">
                <h4>Próximos Passos:</h4>
                <ol>
                  <li>Copie o token acima</li>
                  <li>Instale o probe na máquina Windows</li>
                  <li>Configure o arquivo <code>probe_config.json</code></li>
                  <li>Cole o token no arquivo de configuração</li>
                  <li>Inicie o serviço do probe</li>
                </ol>
                <p>
                  <a href="/probe/INSTALACAO.md" target="_blank">📖 Ver guia de instalação completo</a>
                </p>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-primary" onClick={() => setShowTokenModal(false)}>
                Entendi, Fechar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Probes;
