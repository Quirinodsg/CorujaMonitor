import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Credentials.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Credentials() {
  const [credentials, setCredentials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCredential, setEditingCredential] = useState(null);
  const [groups, setGroups] = useState([]);
  const [servers, setServers] = useState([]);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    credential_type: 'wmi',
    level: 'tenant',
    group_name: '',
    server_id: null,
    is_default: false,
    // WMI
    wmi_username: '',
    wmi_password: '',
    wmi_domain: '',
    // SNMP v2c
    snmp_community: '',
    snmp_port: 161,
  });

  useEffect(() => {
    loadCredentials();
    loadGroups();
    loadServers();
  }, []);

  const loadCredentials = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/v1/credentials/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCredentials(response.data);
    } catch (error) {
      console.error('Erro ao carregar credenciais:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadGroups = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/v1/servers/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const uniqueGroups = [...new Set(response.data.map(s => s.group_name).filter(Boolean))];
      setGroups(uniqueGroups);
    } catch (error) {
      console.error('Erro ao carregar grupos:', error);
    }
  };

  const loadServers = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/v1/servers/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setServers(response.data);
    } catch (error) {
      console.error('Erro ao carregar servidores:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      let endpoint = '';
      let payload = { ...formData };
      
      if (formData.credential_type === 'wmi') {
        endpoint = `${API_URL}/api/v1/credentials/wmi`;
      } else if (formData.credential_type === 'snmp_v2c') {
        endpoint = `${API_URL}/api/v1/credentials/snmp-v2c`;
      }
      
      await axios.post(endpoint, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Credencial criada com sucesso!');
      setShowModal(false);
      resetForm();
      loadCredentials();
    } catch (error) {
      console.error('Erro ao criar credencial:', error);
      alert('Erro ao criar credencial: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja deletar esta credencial?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/v1/credentials/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Credencial deletada com sucesso!');
      loadCredentials();
    } catch (error) {
      console.error('Erro ao deletar credencial:', error);
      alert('Erro ao deletar credencial: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleTest = async (id, hostname) => {
    const testHostname = prompt('Digite o hostname ou IP para testar:', hostname || '');
    if (!testHostname) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/v1/credentials/${id}/test`,
        { hostname: testHostname },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        alert('✅ Teste bem-sucedido!\n\n' + response.data.message);
      } else {
        alert('❌ Teste falhou!\n\n' + response.data.message);
      }
      loadCredentials();
    } catch (error) {
      console.error('Erro ao testar credencial:', error);
      alert('Erro ao testar credencial: ' + (error.response?.data?.detail || error.message));
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      credential_type: 'wmi',
      level: 'tenant',
      group_name: '',
      server_id: null,
      is_default: false,
      wmi_username: '',
      wmi_password: '',
      wmi_domain: '',
      snmp_community: '',
      snmp_port: 161,
    });
    setEditingCredential(null);
  };

  const getCredentialTypeLabel = (type) => {
    const labels = {
      'wmi': 'WMI (Windows)',
      'snmp_v1': 'SNMP v1',
      'snmp_v2c': 'SNMP v2c',
      'snmp_v3': 'SNMP v3',
      'ssh': 'SSH'
    };
    return labels[type] || type;
  };

  const getLevelLabel = (level) => {
    const labels = {
      'tenant': 'Empresa (Tenant)',
      'group': 'Grupo',
      'server': 'Servidor'
    };
    return labels[level] || level;
  };

  const getStatusBadge = (status) => {
    if (!status) return <span className="badge badge-secondary">Não testado</span>;
    if (status === 'success') return <span className="badge badge-success">✓ OK</span>;
    if (status === 'failed') return <span className="badge badge-danger">✗ Falhou</span>;
    return <span className="badge badge-secondary">{status}</span>;
  };

  if (loading) {
    return <div className="credentials-container"><p>Carregando...</p></div>;
  }

  return (
    <div className="credentials-container">
      <div className="credentials-header">
        <h2>🔐 Credenciais Centralizadas</h2>
        <p className="subtitle">Sistema moderno como PRTG/SolarWinds - Configure uma vez, use em todos os servidores</p>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          ➕ Nova Credencial
        </button>
      </div>

      <div className="credentials-grid">
        {credentials.length === 0 ? (
          <div className="empty-state">
            <p>Nenhuma credencial configurada</p>
            <p className="hint">Crie credenciais WMI ou SNMP para monitorar servidores remotamente</p>
          </div>
        ) : (
          credentials.map(cred => (
            <div key={cred.id} className="credential-card">
              <div className="credential-header">
                <h3>{cred.name}</h3>
                {cred.is_default && <span className="badge badge-primary">Padrão</span>}
                {!cred.is_active && <span className="badge badge-secondary">Inativo</span>}
              </div>
              
              <div className="credential-info">
                <div className="info-row">
                  <span className="label">Tipo:</span>
                  <span className="value">{getCredentialTypeLabel(cred.credential_type)}</span>
                </div>
                <div className="info-row">
                  <span className="label">Nível:</span>
                  <span className="value">{getLevelLabel(cred.level)}</span>
                </div>
                {cred.group_name && (
                  <div className="info-row">
                    <span className="label">Grupo:</span>
                    <span className="value">{cred.group_name}</span>
                  </div>
                )}
                {cred.wmi_username && (
                  <div className="info-row">
                    <span className="label">Usuário:</span>
                    <span className="value">{cred.wmi_username}</span>
                  </div>
                )}
                {cred.wmi_domain && (
                  <div className="info-row">
                    <span className="label">Domínio:</span>
                    <span className="value">{cred.wmi_domain}</span>
                  </div>
                )}
                {cred.description && (
                  <div className="info-row">
                    <span className="label">Descrição:</span>
                    <span className="value">{cred.description}</span>
                  </div>
                )}
                <div className="info-row">
                  <span className="label">Status:</span>
                  {getStatusBadge(cred.last_test_status)}
                </div>
              </div>

              <div className="credential-actions">
                <button 
                  className="btn btn-sm btn-info" 
                  onClick={() => handleTest(cred.id)}
                  title="Testar conectividade"
                >
                  🧪 Testar
                </button>
                <button 
                  className="btn btn-sm btn-danger" 
                  onClick={() => handleDelete(cred.id)}
                  title="Deletar credencial"
                >
                  🗑️ Deletar
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal de Criação */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Nova Credencial</h3>
              <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nome *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="Ex: Domínio Principal, SNMP Switches"
                  required
                />
              </div>

              <div className="form-group">
                <label>Descrição</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Descrição opcional"
                  rows="2"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Tipo *</label>
                  <select
                    value={formData.credential_type}
                    onChange={(e) => setFormData({...formData, credential_type: e.target.value})}
                    required
                  >
                    <option value="wmi">WMI (Windows)</option>
                    <option value="snmp_v2c">SNMP v2c</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Nível *</label>
                  <select
                    value={formData.level}
                    onChange={(e) => setFormData({...formData, level: e.target.value, group_name: '', server_id: null})}
                    required
                  >
                    <option value="tenant">Empresa (Tenant)</option>
                    <option value="group">Grupo</option>
                    <option value="server">Servidor</option>
                  </select>
                </div>
              </div>

              {formData.level === 'group' && (
                <div className="form-group">
                  <label>Grupo *</label>
                  <select
                    value={formData.group_name}
                    onChange={(e) => setFormData({...formData, group_name: e.target.value})}
                    required
                  >
                    <option value="">Selecione um grupo</option>
                    {groups.map(group => (
                      <option key={group} value={group}>{group}</option>
                    ))}
                  </select>
                </div>
              )}

              {formData.level === 'server' && (
                <div className="form-group">
                  <label>Servidor *</label>
                  <select
                    value={formData.server_id || ''}
                    onChange={(e) => setFormData({...formData, server_id: parseInt(e.target.value)})}
                    required
                  >
                    <option value="">Selecione um servidor</option>
                    {servers.map(server => (
                      <option key={server.id} value={server.id}>
                        {server.hostname} ({server.ip_address})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Campos WMI */}
              {formData.credential_type === 'wmi' && (
                <>
                  <div className="form-group">
                    <label>Usuário WMI *</label>
                    <input
                      type="text"
                      value={formData.wmi_username}
                      onChange={(e) => setFormData({...formData, wmi_username: e.target.value})}
                      placeholder="Ex: Administrator ou DOMINIO\usuario"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Senha WMI *</label>
                    <input
                      type="password"
                      value={formData.wmi_password}
                      onChange={(e) => setFormData({...formData, wmi_password: e.target.value})}
                      placeholder="Senha do usuário WMI"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Domínio</label>
                    <input
                      type="text"
                      value={formData.wmi_domain}
                      onChange={(e) => setFormData({...formData, wmi_domain: e.target.value})}
                      placeholder="Ex: DOMINIO.local (deixe vazio para workgroup)"
                    />
                  </div>
                </>
              )}

              {/* Campos SNMP v2c */}
              {formData.credential_type === 'snmp_v2c' && (
                <>
                  <div className="form-group">
                    <label>Community String *</label>
                    <input
                      type="text"
                      value={formData.snmp_community}
                      onChange={(e) => setFormData({...formData, snmp_community: e.target.value})}
                      placeholder="Ex: public"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Porta SNMP</label>
                    <input
                      type="number"
                      value={formData.snmp_port}
                      onChange={(e) => setFormData({...formData, snmp_port: parseInt(e.target.value)})}
                      placeholder="161"
                    />
                  </div>
                </>
              )}

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.is_default}
                    onChange={(e) => setFormData({...formData, is_default: e.target.checked})}
                  />
                  <span>Usar como padrão para este nível</span>
                </label>
              </div>

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary">
                  Criar Credencial
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Credentials;
