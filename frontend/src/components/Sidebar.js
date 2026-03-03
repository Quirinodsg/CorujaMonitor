import React from 'react';
import './Sidebar.css';

function Sidebar({ currentPage, onNavigate }) {
  const menuItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'companies', icon: '🏢', label: 'Empresas' },
    { id: 'servers', icon: '🖥️', label: 'Servidores' },
    { id: 'sensors', icon: '📡', label: 'Sensores' },
    { id: 'incidents', icon: '⚠️', label: 'Incidentes' },
    { id: 'reports', icon: '📈', label: 'Relatórios' },
    { id: 'knowledge-base', icon: '🧠', label: 'Base de Conhecimento' },
    { id: 'ai-activities', icon: '🤖', label: 'Atividades da IA' },
    { id: 'maintenance', icon: '🔧', label: 'GMUD' },
    { id: 'settings', icon: '⚙️', label: 'Configurações' },
    { id: 'aiops', icon: '🔮', label: 'AIOps' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header" onClick={() => onNavigate('dashboard')} style={{cursor: 'pointer'}}>
        <h2>🦉 Coruja</h2>
      </div>
      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={`sidebar-item ${currentPage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="sidebar-icon">{item.icon}</span>
            <span className="sidebar-label">{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}

export default Sidebar;
