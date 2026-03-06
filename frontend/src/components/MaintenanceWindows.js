import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Management.css';

function MaintenanceWindows() {
  const [windows, setWindows] = useState([]);
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingWindow, setEditingWindow] = useState(null);
  const [filterActive, setFilterActive] = useState('all'); // all, active, current
  const [newWindow, setNewWindow] = useState({
    server_id: '',
    title: '',
    description: '',
    start_time: '',
    end_time: ''
  });

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [windowsRes, serversRes] = await Promise.all([
        api.get('/maintenance/'),
        api.get('/servers/')
      ]);
      
      setWindows(windowsRes.data);
      setServers(serversRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddWindow = async () => {
    if (!newWindow.title || !newWindow.start_time || !newWindow.end_time) {
      alert('Preencha todos os campos obrigatórios');
      return;
    }

    try {
      await api.post('/maintenance/', {
        server_id: newWindow.server_id || null,
        title: newWindow.title,
        description: newWindow.description,
        start_time: new Date(newWindow.start_time).toISOString(),
        end_time: new Date(newWindow.end_time).toISOString()
      });

      setShowAddModal(false);
      setNewWindow({
        server_id: '',
        title: '',
        description: '',
        start_time: '',
        end_time: ''
      });
      loadData();
      alert('Janela de manutenção criada com sucesso!');
    } catch (error) {
      console.error('Erro ao criar janela de manutenção:', error);
      alert('Erro: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleEditWindow = (window) => {
    setEditingWindow({
      ...window,
      start_time: new Date(window.start_time).toISOString().slice(0, 16),
      end_time: new Date(window.end_time).toISOString().slice(0, 16)
    });
    setShowEditModal(true);
  };

  const handleUpdateWindow = async () => {
    if (!editingWindow) return;

    try {
      await api.put(`/maintenance/${editingWindow.id}`, {
        title: editingWindow.title,
        description: editingWindow.description,
        start_time: new Date(editingWindow.start_time).toISOString(),
        end_time: new Date(editingWindow.end_time).toISOString(),
        is_active: editingWindow.is_active
      });

      setShowEditModal(false);
      setEditingWindow(null);
      loadData();
      alert('Janela de manutenção atualizada com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar janela de manutenção:', error);
      alert('Erro: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteWindow = async (windowId, title) => {
    if (!window.confirm(`Tem certeza que deseja remover a janela de manutenção "${title}"?`)) {
      return;
    }

    try {
      await api.delete(`/maintenance/${windowId}`);
      loadData();
      alert('Janela de manutenção removida com sucesso!');
    } catch (error) {
      console.error('Erro ao remover janela de manutenção:', error);
      alert('Erro: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getFilteredWindows = () => {
    if (filterActive === 'all') return windows;
    if (filterActive === 'active') return windows.filter(w => w.is_active);
    if (filterActive === 'current') return windows.filter(w => w.is_current);
    return windows;
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getDuration = (start, end) => {
    const diff = new Date(end) - new Date(start);
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      return `${days}d ${remainingHours}h`;
    }
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return <div className="management-container">Carregando...</div>;
  }

  const filteredWindows = getFilteredWindows();

  return (
    <div className="management-container">
      <div className="management-header">
        <h1>🔧 Janelas de Manutenção</h1>
        <button className="btn-add" onClick={() => setShowAddModal(true)}>
          + Agendar Manutenção
        </button>
      </div>

      <div className="info-banner" style={{ background: '#fff3cd', borderLeft: '4px solid #ffc107' }}>
        <p>ℹ️ <strong>Janelas de Manutenção:</strong></p>
        <p>• Durante a manutenção, alertas e ligações são suprimidos</p>
        <p>• Downtime não é contabilizado nos relatórios de SLA</p>
        <p>• Pode ser aplicado a um servidor específico ou toda a empresa</p>
      </div>

      {/* Filters */}
      <div className="maintenance-filters">
        <button 
          className={`filter-btn ${filterActive === 'all' ? 'active' : ''}`}
          onClick={() => setFilterActive('all')}
        >
          Todas ({windows.length})
        </button>
        <button 
          className={`filter-btn ${filterActive === 'active' ? 'active' : ''}`}
          onClick={() => setFilterActive('active')}
        >
          Ativas ({windows.filter(w => w.is_active).length})
        </button>
        <button 
          className={`filter-btn ${filterActive === 'current' ? 'active' : ''}`}
          onClick={() => setFilterActive('current')}
        >
          🔧 Em Andamento ({windows.filter(w => w.is_current).length})
        </button>
      </div>

      {/* Windows Table */}
      <div className="maintenance-table-container">
        <table className="maintenance-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Título</th>
              <th>Escopo</th>
              <th>Início</th>
              <th>Término</th>
              <th>Duração</th>
              <th>Criado por</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {filteredWindows.length === 0 ? (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                  Nenhuma janela de manutenção encontrada
                </td>
              </tr>
            ) : (
              filteredWindows.map(window => (
                <tr key={window.id} className={window.is_current ? 'maintenance-current' : ''}>
                  <td>
                    {window.is_current ? (
                      <span className="status-badge current">🔧 Em Andamento</span>
                    ) : window.is_active ? (
                      <span className="status-badge active">✓ Agendada</span>
                    ) : (
                      <span className="status-badge inactive">○ Inativa</span>
                    )}
                  </td>
                  <td>
                    <strong>{window.title}</strong>
                    {window.description && (
                      <p style={{ margin: '5px 0 0 0', fontSize: '13px', color: '#666' }}>
                        {window.description}
                      </p>
                    )}
                  </td>
                  <td>
                    {window.server_name === 'Toda a Empresa' ? (
                      <span style={{ color: '#f44336', fontWeight: '600' }}>
                        🏢 {window.server_name}
                      </span>
                    ) : (
                      <span style={{ color: '#2196f3' }}>
                        🖥️ {window.server_name}
                      </span>
                    )}
                  </td>
                  <td>{formatDateTime(window.start_time)}</td>
                  <td>{formatDateTime(window.end_time)}</td>
                  <td>
                    <span className="duration-badge">
                      ⏱️ {getDuration(window.start_time, window.end_time)}
                    </span>
                  </td>
                  <td>{window.created_by_name || 'Sistema'}</td>
                  <td>
                    <div className="table-actions">
                      <button
                        className="btn-action btn-small"
                        onClick={() => handleEditWindow(window)}
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-action btn-small btn-danger"
                        onClick={() => handleDeleteWindow(window.id, window.title)}
                        title="Remover"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <h2>🔧 Agendar Janela de Manutenção</h2>

            <div className="form-group">
              <label>Escopo: *</label>
              <select
                value={newWindow.server_id}
                onChange={(e) => setNewWindow({...newWindow, server_id: e.target.value})}
              >
                <option value="">🏢 Toda a Empresa</option>
                {servers.map(server => (
                  <option key={server.id} value={server.id}>
                    🖥️ {server.hostname}
                  </option>
                ))}
              </select>
              <small>Selecione um servidor específico ou deixe em branco para toda a empresa</small>
            </div>

            <div className="form-group">
              <label>Título: *</label>
              <input
                type="text"
                value={newWindow.title}
                onChange={(e) => setNewWindow({...newWindow, title: e.target.value})}
                placeholder="Ex: Atualização de Windows, Manutenção de Hardware"
              />
            </div>

            <div className="form-group">
              <label>Descrição:</label>
              <textarea
                value={newWindow.description}
                onChange={(e) => setNewWindow({...newWindow, description: e.target.value})}
                placeholder="Descreva o motivo da manutenção..."
                rows="3"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Data/Hora de Início: *</label>
                <input
                  type="datetime-local"
                  value={newWindow.start_time}
                  onChange={(e) => setNewWindow({...newWindow, start_time: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Data/Hora de Término: *</label>
                <input
                  type="datetime-local"
                  value={newWindow.end_time}
                  onChange={(e) => setNewWindow({...newWindow, end_time: e.target.value})}
                />
              </div>
            </div>

            <div className="info-box">
              <p>ℹ️ <strong>Durante a janela de manutenção:</strong></p>
              <ul>
                <li>Alertas e ligações serão suprimidos</li>
                <li>Downtime não será contabilizado no SLA</li>
                <li>Servidor/Empresa aparecerá com indicador "Em Manutenção"</li>
              </ul>
            </div>

            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowAddModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleAddWindow}>
                Agendar Manutenção
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingWindow && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <h2>✏️ Editar Janela de Manutenção</h2>

            <div className="form-group">
              <label>Título: *</label>
              <input
                type="text"
                value={editingWindow.title}
                onChange={(e) => setEditingWindow({...editingWindow, title: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Descrição:</label>
              <textarea
                value={editingWindow.description || ''}
                onChange={(e) => setEditingWindow({...editingWindow, description: e.target.value})}
                rows="3"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Data/Hora de Início: *</label>
                <input
                  type="datetime-local"
                  value={editingWindow.start_time}
                  onChange={(e) => setEditingWindow({...editingWindow, start_time: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Data/Hora de Término: *</label>
                <input
                  type="datetime-local"
                  value={editingWindow.end_time}
                  onChange={(e) => setEditingWindow({...editingWindow, end_time: e.target.value})}
                />
              </div>
            </div>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={editingWindow.is_active}
                  onChange={(e) => setEditingWindow({...editingWindow, is_active: e.target.checked})}
                />
                {' '}Janela ativa
              </label>
              <small>Desmarque para desativar esta janela de manutenção</small>
            </div>

            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowEditModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleUpdateWindow}>
                Salvar Alterações
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MaintenanceWindows;
