import React, { useState, useEffect, useRef } from 'react';
import './Topbar.css';

const PAGE_LABELS = {
  dashboard: 'Dashboard', observability: 'Observabilidade', topology: 'Topologia',
  'intelligent-alerts': 'Alertas Inteligentes', incidents: 'Incidentes',
  'aiops-v3': 'AIOps Pipeline', 'advanced-metrics': 'Métricas Avançadas',
  'events-timeline': 'Eventos', 'knowledge-base': 'Base de Conhecimento',
  servers: 'Servidores', sensors: 'Sensores', companies: 'Empresas',
  'probe-nodes': 'Probe Nodes', maintenance: 'GMUD', settings: 'Configurações',
};

const IcoSearch = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
  </svg>
);

const IcoBell = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
  </svg>
);

function Topbar({ currentPage, systemStatus, alertCount = 0, onNavigate }) {
  const [search, setSearch] = useState('');
  const inputRef = useRef(null);

  // Ctrl+K shortcut
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const statusClass = systemStatus === 'ok' ? 'topbar-status--ok'
    : systemStatus === 'warning' ? 'topbar-status--warning'
    : 'topbar-status--critical';

  const statusLabel = systemStatus === 'ok' ? 'Sistema OK'
    : systemStatus === 'warning' ? 'Atenção'
    : 'Crítico';

  const pageLabel = PAGE_LABELS[currentPage] || currentPage;

  return (
    <header className="topbar" role="banner">
      <span className="topbar-title">{pageLabel}</span>

      <div className="topbar-search">
        <span className="topbar-search-icon"><IcoSearch /></span>
        <input
          ref={inputRef}
          className="topbar-search-input"
          type="text"
          placeholder="Buscar servidores, alertas, sensores..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          aria-label="Busca global"
        />
        <span className="topbar-search-kbd">Ctrl+K</span>
      </div>

      <div className="topbar-right">
        <div
          className={`topbar-status ${statusClass}`}
          onClick={() => onNavigate && onNavigate('observability')}
          role="button"
          tabIndex={0}
          aria-label={`Status do sistema: ${statusLabel}`}
        >
          <span className="topbar-status-dot" />
          {statusLabel}
        </div>

        <button
          className="topbar-icon-btn"
          onClick={() => onNavigate && onNavigate('intelligent-alerts')}
          aria-label={`Alertas${alertCount > 0 ? ` — ${alertCount} ativos` : ''}`}
          title="Alertas"
        >
          <IcoBell />
          {alertCount > 0 && <span className="badge" aria-hidden="true" />}
        </button>
      </div>
    </header>
  );
}

export default Topbar;
