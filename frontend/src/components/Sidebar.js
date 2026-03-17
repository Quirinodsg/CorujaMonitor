import React from 'react';
import './Sidebar.css';

function Sidebar({ currentPage, onNavigate, darkMode, onToggleDark, collapsed, onToggleCollapse }) {
  const menuItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'companies', icon: '🏢', label: 'Empresas' },
    { id: 'servers', icon: '🖥️', label: 'Servidores' },
    { id: 'sensors', icon: '📡', label: 'Sensores' },
    { id: 'incidents', icon: '⚠️', label: 'Incidentes' },
    { id: 'event-timeline', icon: '📋', label: 'Timeline de Eventos' },
    { id: 'reports', icon: '📈', label: 'Relatórios' },
    { id: 'metrics-viewer', icon: '📉', label: 'Métricas' },
    { id: 'aiops', icon: '🔮', label: 'AIOps' },
    { id: 'discovery', icon: '🔍', label: 'Discovery' },
    { id: 'knowledge-base', icon: '🧠', label: 'Base de Conhecimento' },
    { id: 'ai-activities', icon: '🤖', label: 'Atividades da IA' },
    { id: 'probe-nodes', icon: '🔌', label: 'Probe Nodes' },
    { id: 'system-health', icon: '⚙️', label: 'Saúde do Sistema' },
    { id: 'maintenance', icon: '🔧', label: 'GMUD' },
    { id: 'settings', icon: '🛠️', label: 'Configurações' },
  ];

  return (
    <div className={`sidebar${collapsed ? ' sidebar--collapsed' : ''}`}>
      <div className="sidebar-header" onClick={() => onNavigate('dashboard')} style={{cursor: 'pointer'}}>
        {!collapsed && <h2>🦉 Coruja</h2>}
        {collapsed && <span style={{fontSize: '24px'}}>🦉</span>}
      </div>
      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={`sidebar-item ${currentPage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
            title={collapsed ? item.label : undefined}
          >
            <span className="sidebar-icon">{item.icon}</span>
            {!collapsed && <span className="sidebar-label">{item.label}</span>}
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <button className="sidebar-theme-toggle" onClick={onToggleDark} title={darkMode ? 'Modo claro' : 'Modo escuro'}>
          <span>{darkMode ? '☀️' : '🌙'}</span>
          {!collapsed && <span className="sidebar-label">{darkMode ? 'Modo Claro' : 'Modo Escuro'}</span>}
        </button>
        <button className="sidebar-collapse-btn" onClick={onToggleCollapse} title={collapsed ? 'Expandir menu' : 'Recolher menu'}>
          <span>{collapsed ? '▶' : '◀'}</span>
          {!collapsed && <span className="sidebar-label">Recolher</span>}
        </button>
      </div>
    </div>
  );
}

export default Sidebar;
