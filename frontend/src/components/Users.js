import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Management.css';

function Users() {
  const [users, setUsers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    role: 'viewer'
  });
  const [loading, setLoading] = useState(true);

  const roles = [
    { value: 'admin', label: 'Administrador', description: 'Acesso total ao sistema' },
    { value: 'technician', label: 'Técnico', description: 'Pode gerenciar servidores e sensores' },
    { value: 'viewer', label: 'Visualizador', description: 'Apenas visualização do dashboard' }
  ];

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const response = await api.get('/api/v1/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/v1/users', formData);
      setShowModal(false);
      setFormData({ email: '', full_name: '', password: '', role: 'viewer' });
      loadUsers();
      alert('Usuário criado com sucesso!');
    } catch (error) {
      alert('Erro ao criar usuário: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleEdit = (user) => {
    setEditingUser({
      id: user.id,
      email: user.email,
      full_name: user.full_name,
      role: user.role
    });
    setShowEditModal(true);
  };

  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/api/v1/users/${editingUser.id}`, {
        full_name: editingUser.full_name,
        role: editingUser.role
      });
      setShowEditModal(false);
      setEditingUser(null);
      loadUsers();
      alert('Usuário atualizado com sucesso!');
    } catch (error) {
      alert('Erro ao atualizar usuário: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleToggleActive = async (user) => {
    const action = user.is_active ? 'desativar' : 'ativar';
    if (!window.confirm(`Tem certeza que deseja ${action} o usuário "${user.full_name}"?`)) {
      return;
    }

    try {
      await api.patch(`/api/v1/users/${user.id}/toggle-active`);
      loadUsers();
      alert(`Usuário ${action === 'desativar' ? 'desativado' : 'ativado'} com sucesso!`);
    } catch (error) {
      alert(`Erro ao ${action} usuário: ` + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async (user) => {
    if (!window.confirm(`Tem certeza que deseja excluir o usuário "${user.full_name}"?`)) {
      return;
    }

    try {
      await api.delete(`/api/v1/users/${user.id}`);
      loadUsers();
      alert('Usuário excluído com sucesso!');
    } catch (error) {
      alert('Erro ao excluir usuário: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getRoleBadge = (role) => {
    const roleConfig = {
      admin: { color: '#f44336', label: 'Admin' },
      technician: { color: '#2196f3', label: 'Técnico' },
      viewer: { color: '#9e9e9e', label: 'Visualizador' }
    };
    const config = roleConfig[role] || roleConfig.viewer;
    return (
      <span style={{
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: '600',
        backgroundColor: config.color + '20',
        color: config.color
      }}>
        {config.label}
      </span>
    );
  };

  const getPermissions = (role) => {
    const permissions = {
      admin: ['Dashboard', 'Empresas', 'Servidores', 'Sensores', 'Incidentes', 'Relatórios', 'Usuários'],
      technician: ['Dashboard', 'Servidores', 'Sensores', 'Incidentes', 'Adicionar Notas'],
      viewer: ['Dashboard']
    };
    return permissions[role] || [];
  };

  if (loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="management-page">
      <div className="page-header">
        <h1>👥 Gerenciamento de Usuários</h1>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + Novo Usuário
        </button>
      </div>

      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Email</th>
              <th>Perfil</th>
              <th>Status</th>
              <th>Permissões</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td><strong>{user.full_name}</strong></td>
                <td>{user.email}</td>
                <td>{getRoleBadge(user.role)}</td>
                <td>
                  <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                    {user.is_active ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td>
                  <div className="permissions-list">
                    {getPermissions(user.role).slice(0, 3).map((perm, idx) => (
                      <span key={idx} className="permission-tag">{perm}</span>
                    ))}
                    {getPermissions(user.role).length > 3 && (
                      <span className="permission-tag">+{getPermissions(user.role).length - 3}</span>
                    )}
                  </div>
                </td>
                <td>
                  <div className="table-actions">
                    <button className="btn-action btn-edit" onClick={() => handleEdit(user)}>
                      ✏️
                    </button>
                    <button 
                      className={`btn-action ${user.is_active ? 'btn-warning' : 'btn-success'}`}
                      onClick={() => handleToggleActive(user)}
                    >
                      {user.is_active ? '⏸️' : '▶️'}
                    </button>
                    <button className="btn-action btn-danger" onClick={() => handleDelete(user)}>
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Novo Usuário</h2>
              <button className="btn-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nome Completo</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={e => setFormData({...formData, full_name: e.target.value})}
                  required
                  placeholder="Ex: João Silva"
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={e => setFormData({...formData, email: e.target.value})}
                  required
                  placeholder="Ex: joao@empresa.com"
                />
              </div>
              <div className="form-group">
                <label>Senha</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={e => setFormData({...formData, password: e.target.value})}
                  required
                  placeholder="Mínimo 6 caracteres"
                  minLength="6"
                />
              </div>
              <div className="form-group">
                <label>Perfil de Acesso</label>
                <select 
                  value={formData.role}
                  onChange={e => setFormData({...formData, role: e.target.value})}
                >
                  {roles.map(role => (
                    <option key={role.value} value={role.value}>
                      {role.label} - {role.description}
                    </option>
                  ))}
                </select>
              </div>
              <div className="permissions-preview">
                <h4>Permissões deste perfil:</h4>
                <ul>
                  {getPermissions(formData.role).map((perm, idx) => (
                    <li key={idx}>✓ {perm}</li>
                  ))}
                </ul>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  Criar Usuário
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showEditModal && editingUser && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Editar Usuário</h2>
              <button className="btn-close" onClick={() => setShowEditModal(false)}>×</button>
            </div>
            <form onSubmit={handleUpdateSubmit}>
              <div className="form-group">
                <label>Nome Completo</label>
                <input
                  type="text"
                  value={editingUser.full_name}
                  onChange={e => setEditingUser({...editingUser, full_name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={editingUser.email}
                  disabled
                  style={{ background: '#f5f5f5', cursor: 'not-allowed' }}
                />
                <small>O email não pode ser alterado</small>
              </div>
              <div className="form-group">
                <label>Perfil de Acesso</label>
                <select 
                  value={editingUser.role}
                  onChange={e => setEditingUser({...editingUser, role: e.target.value})}
                >
                  {roles.map(role => (
                    <option key={role.value} value={role.value}>
                      {role.label} - {role.description}
                    </option>
                  ))}
                </select>
              </div>
              <div className="permissions-preview">
                <h4>Permissões deste perfil:</h4>
                <ul>
                  {getPermissions(editingUser.role).map((perm, idx) => (
                    <li key={idx}>✓ {perm}</li>
                  ))}
                </ul>
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
    </div>
  );
}

export default Users;
