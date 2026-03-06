import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Management.css';
import './Companies.css';

function Companies({ onNavigate }) {
  const [companies, setCompanies] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showProbeModal, setShowProbeModal] = useState(false);
  const [editingCompany, setEditingCompany] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [companyProbes, setCompanyProbes] = useState({});
  const [formData, setFormData] = useState({ name: '', slug: '' });
  const [probeFormData, setProbeFormData] = useState({ name: '' });
  const [loading, setLoading] = useState(true);
  const [expandedCompanies, setExpandedCompanies] = useState({});

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const response = await api.get('/tenants');
      setCompanies(response.data);
      
      // Load probes for each company
      const probesData = {};
      for (const company of response.data) {
        try {
          const probesResponse = await api.get(`/probes?tenant_id=${company.id}`);
          probesData[company.id] = probesResponse.data;
        } catch (error) {
          console.error(`Erro ao carregar probes da empresa ${company.id}:`, error);
          probesData[company.id] = [];
        }
      }
      setCompanyProbes(probesData);
    } catch (error) {
      console.error('Erro ao carregar empresas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/tenants', formData);
      setShowModal(false);
      setFormData({ name: '', slug: '' });
      loadCompanies();
      alert('Empresa criada com sucesso!');
    } catch (error) {
      alert('Erro ao criar empresa: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleEdit = (company) => {
    setEditingCompany(company);
    setShowEditModal(true);
  };

  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/tenants/${editingCompany.id}`, {
        name: editingCompany.name,
        slug: editingCompany.slug
      });
      setShowEditModal(false);
      setEditingCompany(null);
      loadCompanies();
      alert('Empresa atualizada com sucesso!');
    } catch (error) {
      alert('Erro ao atualizar empresa: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleToggleActive = async (company) => {
    const action = company.is_active ? 'desativar' : 'ativar';
    if (!window.confirm(`Tem certeza que deseja ${action} a empresa "${company.name}"?`)) {
      return;
    }

    try {
      await api.patch(`/tenants/${company.id}/toggle-active`);
      loadCompanies();
      alert(`Empresa ${action === 'desativar' ? 'desativada' : 'ativada'} com sucesso!`);
    } catch (error) {
      alert(`Erro ao ${action} empresa: ` + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async (company) => {
    if (!window.confirm(`ATENÇÃO: Tem certeza que deseja EXCLUIR permanentemente a empresa "${company.name}"?\n\nEsta ação não pode ser desfeita e todos os dados relacionados (usuários, probes, servidores, sensores) serão perdidos!`)) {
      return;
    }

    // Segunda confirmação
    const confirmText = window.prompt(`Digite o nome da empresa "${company.name}" para confirmar a exclusão:`);
    if (confirmText !== company.name) {
      alert('Nome não corresponde. Exclusão cancelada.');
      return;
    }

    try {
      await api.delete(`/tenants/${company.id}`);
      loadCompanies();
      alert('Empresa excluída com sucesso!');
    } catch (error) {
      alert('Erro ao excluir empresa: ' + (error.response?.data?.detail || error.message));
    }
  };

  const toggleCompany = (companyId) => {
    setExpandedCompanies(prev => ({
      ...prev,
      [companyId]: !prev[companyId]
    }));
  };

  const handleAddProbe = (company) => {
    setSelectedCompany(company);
    setShowProbeModal(true);
  };

  const handleCreateProbe = async (e) => {
    e.preventDefault();
    if (!selectedCompany) return;

    try {
      await api.post('/probes', {
        tenant_id: selectedCompany.id,
        name: probeFormData.name
      });
      
      setShowProbeModal(false);
      setProbeFormData({ name: '' });
      setSelectedCompany(null);
      loadCompanies();
      alert('Probe criada com sucesso!');
    } catch (error) {
      alert('Erro ao criar probe: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteProbe = async (probe, companyName) => {
    if (!window.confirm(`Tem certeza que deseja excluir a probe "${probe.name}" da empresa "${companyName}"?\n\nTodos os servidores e sensores associados serão perdidos!`)) {
      return;
    }

    try {
      await api.delete(`/probes/${probe.id}`);
      loadCompanies();
      alert('Probe excluída com sucesso!');
    } catch (error) {
      alert('Erro ao excluir probe: ' + (error.response?.data?.detail || error.message));
    }
  };

  const copyProbeToken = (token) => {
    // Fallback para navegadores sem clipboard API ou HTTP
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(token)
        .then(() => alert('Token copiado para a área de transferência!'))
        .catch(() => copyTokenFallback(token));
    } else {
      copyTokenFallback(token);
    }
  };

  const copyTokenFallback = (token) => {
    // Método alternativo usando textarea temporário
    const textarea = document.createElement('textarea');
    textarea.value = token;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      alert('Token copiado para a área de transferência!');
    } catch (err) {
      alert('Não foi possível copiar automaticamente. Token:\n\n' + token);
    }
    document.body.removeChild(textarea);
  };

  if (loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="management-page">
      <div className="page-header">
        <h1>🏢 Empresas</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            className="btn-primary" 
            onClick={() => onNavigate && onNavigate('probes')}
            style={{
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>🔌</span>
            Probes
          </button>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            + Nova Empresa
          </button>
        </div>
      </div>

      <div className="cards-grid">
        {companies.map(company => (
          <div key={company.id} className="card company-card">
            <div className="card-header" onClick={() => toggleCompany(company.id)} style={{ cursor: 'pointer' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span>{expandedCompanies[company.id] ? '📂' : '📁'}</span>
                <h3>{company.name}</h3>
              </div>
              <span className={`badge ${company.is_active ? 'badge-success' : 'badge-danger'}`}>
                {company.is_active ? 'Ativa' : 'Inativa'}
              </span>
            </div>
            <div className="card-body">
              <p><strong>Slug:</strong> {company.slug}</p>
              <p><strong>Criada em:</strong> {new Date(company.created_at).toLocaleDateString('pt-BR')}</p>
              <p><strong>Probes:</strong> {companyProbes[company.id]?.length || 0}</p>
            </div>
            
            {expandedCompanies[company.id] && (
              <div className="probes-section">
                <div className="probes-header">
                  <h4>🔌 Probes</h4>
                  <button 
                    className="btn-add-small"
                    onClick={() => handleAddProbe(company)}
                  >
                    + Nova Probe
                  </button>
                </div>
                
                {companyProbes[company.id]?.length > 0 ? (
                  <div className="probes-list">
                    {companyProbes[company.id].map(probe => (
                      <div key={probe.id} className="probe-item">
                        <div className="probe-info">
                          <strong>{probe.name}</strong>
                          <span className={`probe-status ${probe.is_active ? 'active' : 'inactive'}`}>
                            {probe.is_active ? '● Online' : '○ Offline'}
                          </span>
                        </div>
                        <div className="probe-token">
                          <code className="token-full">{probe.token}</code>
                          <button 
                            className="btn-copy"
                            onClick={() => copyProbeToken(probe.token)}
                            title="Copiar token completo"
                          >
                            📋
                          </button>
                        </div>
                        <button 
                          className="btn-delete-small"
                          onClick={() => handleDeleteProbe(probe, company.name)}
                          title="Excluir probe"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-probes">Nenhuma probe cadastrada. Clique em "+ Nova Probe" para adicionar.</p>
                )}
              </div>
            )}
            
            <div className="card-actions">
              <button 
                className="btn-action btn-edit" 
                onClick={() => handleEdit(company)}
                title="Editar empresa"
              >
                ✏️ Editar
              </button>
              <button 
                className={`btn-action ${company.is_active ? 'btn-warning' : 'btn-success'}`}
                onClick={() => handleToggleActive(company)}
                title={company.is_active ? 'Desativar empresa' : 'Ativar empresa'}
              >
                {company.is_active ? '⏸️ Desativar' : '▶️ Ativar'}
              </button>
              <button 
                className="btn-action btn-danger" 
                onClick={() => handleDelete(company)}
                title="Excluir empresa permanentemente"
              >
                🗑️ Excluir
              </button>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Nova Empresa</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nome da Empresa</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                  required
                  placeholder="Ex: Empresa ABC"
                />
              </div>
              <div className="form-group">
                <label>Slug (identificador único)</label>
                <input
                  type="text"
                  value={formData.slug}
                  onChange={e => setFormData({...formData, slug: e.target.value.toLowerCase().replace(/\s+/g, '-')})}
                  required
                  placeholder="Ex: empresa-abc"
                />
                <small>Usado para identificação única no sistema</small>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  Criar Empresa
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showEditModal && editingCompany && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Editar Empresa</h2>
              <button className="btn-close" onClick={() => setShowEditModal(false)}>×</button>
            </div>
            <form onSubmit={handleUpdateSubmit}>
              <div className="form-group">
                <label>Nome da Empresa</label>
                <input
                  type="text"
                  value={editingCompany.name}
                  onChange={e => setEditingCompany({...editingCompany, name: e.target.value})}
                  required
                  placeholder="Ex: Empresa ABC"
                />
              </div>
              <div className="form-group">
                <label>Slug (identificador único)</label>
                <input
                  type="text"
                  value={editingCompany.slug}
                  onChange={e => setEditingCompany({...editingCompany, slug: e.target.value.toLowerCase().replace(/\s+/g, '-')})}
                  required
                  placeholder="Ex: empresa-abc"
                />
                <small>Usado para identificação única no sistema</small>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowEditModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  Salvar Alterações
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showProbeModal && selectedCompany && (
        <div className="modal-overlay" onClick={() => setShowProbeModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Nova Probe - {selectedCompany.name}</h2>
              <button className="btn-close" onClick={() => setShowProbeModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreateProbe}>
              <div className="form-group">
                <label>Nome da Probe</label>
                <input
                  type="text"
                  value={probeFormData.name}
                  onChange={e => setProbeFormData({...probeFormData, name: e.target.value})}
                  required
                  placeholder="Ex: Probe Matriz, Probe Filial SP"
                />
                <small>Nome identificador da probe para esta empresa</small>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowProbeModal(false)}>
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
    </div>
  );
}

export default Companies;
