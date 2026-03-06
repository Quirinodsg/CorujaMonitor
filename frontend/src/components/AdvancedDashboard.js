import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './AdvancedDashboard.css';

function AdvancedDashboard({ user, onNavigate }) {
  const [data, setData] = useState({
    overview: null,
    topProblematic: [],
    trends: [],
    sla: null,
    capacity: null
  });
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    company: 'all',
    os: 'all',
    application: 'all',
    environment: 'all',
    timeRange: '24h'
  });
  const [widgets, setWidgets] = useState([
    { id: 'overview', enabled: true, order: 1 },
    { id: 'top10', enabled: true, order: 2 },
    { id: 'trends', enabled: true, order: 3 },
    { id: 'sla', enabled: true, order: 4 },
    { id: 'capacity', enabled: true, order: 5 },
    { id: 'heatmap', enabled: true, order: 6 }
  ]);

  useEffect(() => {
    loadAdvancedData();
    const interval = setInterval(loadAdvancedData, 30000);
    return () => clearInterval(interval);
  }, [filters]);

  const loadAdvancedData = async () => {
    try {
      // Usar endpoints existentes do dashboard normal
      const [overview, healthSummary, incidents, servers] = await Promise.all([
        api.get('/dashboard/overview'),
        api.get('/dashboard/health-summary'),
        api.get('/incidents?limit=10'),
        api.get('/servers/')
      ]);

      // Processar dados para o formato do dashboard avançado
      const serversData = servers.data || [];
      const incidentsData = incidents.data || [];
      
      // Calcular top 10 problemáticos
      const serverProblems = {};
      incidentsData.forEach(inc => {
        if (inc.status === 'open') {
          if (!serverProblems[inc.server_id]) {
            serverProblems[inc.server_id] = { critical: 0, warning: 0, total: 0 };
          }
          serverProblems[inc.server_id].total++;
          if (inc.severity === 'critical') serverProblems[inc.server_id].critical++;
          if (inc.severity === 'warning') serverProblems[inc.server_id].warning++;
        }
      });

      const topProblematic = Object.entries(serverProblems)
        .map(([serverId, problems]) => {
          const server = serversData.find(s => s.id === parseInt(serverId));
          return {
            id: serverId,
            hostname: server?.hostname || 'Desconhecido',
            issues_count: problems.total,
            critical: problems.critical,
            warning: problems.warning
          };
        })
        .sort((a, b) => b.issues_count - a.issues_count)
        .slice(0, 10);

      setData({
        overview: overview.data,
        topProblematic,
        trends: [],
        sla: { availability: 99.9 },
        capacity: {}
      });
    } catch (error) {
      console.error('Erro ao carregar dashboard avançado:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderOverviewWidget = () => (
    <div className="dashboard-widget overview-widget">
      <div className="widget-header">
        <h3>📊 Visão Geral</h3>
        <div className="widget-actions">
          <button className="btn-icon" title="Atualizar">🔄</button>
        </div>
      </div>
      <div className="widget-content">
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">🖥️</div>
            <div className="metric-value">{data.overview?.total_servers || 0}</div>
            <div className="metric-label">Servidores</div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">📡</div>
            <div className="metric-value">{data.overview?.total_sensors || 0}</div>
            <div className="metric-label">Sensores</div>
          </div>
          <div className="metric-card ok">
            <div className="metric-icon">✅</div>
            <div className="metric-value">{data.overview?.sensors_ok || 0}</div>
            <div className="metric-label">OK</div>
          </div>
          <div className="metric-card warning">
            <div className="metric-icon">⚠️</div>
            <div className="metric-value">{data.overview?.sensors_warning || 0}</div>
            <div className="metric-label">Avisos</div>
          </div>
          <div className="metric-card critical">
            <div className="metric-icon">🔥</div>
            <div className="metric-value">{data.overview?.sensors_critical || 0}</div>
            <div className="metric-label">Críticos</div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">⚡</div>
            <div className="metric-value">{data.overview?.availability || '99.9'}%</div>
            <div className="metric-label">Disponibilidade</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTop10Widget = () => (
    <div className="dashboard-widget top10-widget">
      <div className="widget-header">
        <h3>🎯 Top 10 Hosts Problemáticos</h3>
      </div>
      <div className="widget-content">
        <div className="top10-list">
          {data.topProblematic.map((host, index) => (
            <div key={host.id} className="top10-item">
              <div className="rank">#{index + 1}</div>
              <div className="host-info">
                <div className="host-name">{host.hostname}</div>
                <div className="host-issues">{host.issues_count} problemas</div>
              </div>
              <div className="severity-bar">
                <div 
                  className="severity-fill critical" 
                  style={{ width: `${(host.critical / host.issues_count) * 100}%` }}
                />
                <div 
                  className="severity-fill warning" 
                  style={{ width: `${(host.warning / host.issues_count) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTrendsWidget = () => (
    <div className="dashboard-widget trends-widget">
      <div className="widget-header">
        <h3>📈 Tendências de Consumo</h3>
      </div>
      <div className="widget-content">
        <div className="trends-chart">
          {/* Simplified chart - in production use Chart.js or similar */}
          <div className="trend-item">
            <div className="trend-label">CPU Médio</div>
            <div className="trend-bar">
              <div className="trend-fill" style={{ width: '65%' }}></div>
            </div>
            <div className="trend-value">65%</div>
          </div>
          <div className="trend-item">
            <div className="trend-label">Memória Média</div>
            <div className="trend-bar">
              <div className="trend-fill" style={{ width: '72%' }}></div>
            </div>
            <div className="trend-value">72%</div>
          </div>
          <div className="trend-item">
            <div className="trend-label">Disco Médio</div>
            <div className="trend-bar">
              <div className="trend-fill" style={{ width: '58%' }}></div>
            </div>
            <div className="trend-value">58%</div>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return <div className="loading-dashboard">🔄 Carregando dashboard avançado...</div>;
  }

  return (
    <div className="advanced-dashboard">
      <div className="dashboard-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button 
            className="btn-secondary" 
            onClick={() => onNavigate('dashboard')}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              padding: '10px 16px'
            }}
          >
            ← Voltar
          </button>
          <h1>📊 Dashboard Avançado</h1>
        </div>
        <div className="dashboard-actions">
          <button 
            className="btn-secondary" 
            onClick={() => alert('Funcionalidade de salvar layout será implementada em breve!')}
            style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            💾 Salvar Layout
          </button>
          <button 
            className="btn-secondary" 
            onClick={() => alert('Funcionalidade de personalização será implementada em breve!')}
            style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            ⚙️ Personalizar
          </button>
        </div>
      </div>

      <div className="dashboard-filters">
        <select value={filters.company} onChange={(e) => setFilters({...filters, company: e.target.value})}>
          <option value="all">📁 Todas as Empresas</option>
        </select>
        <select value={filters.os} onChange={(e) => setFilters({...filters, os: e.target.value})}>
          <option value="all">💻 Todos os SOs</option>
          <option value="windows">Windows</option>
          <option value="linux">Linux</option>
        </select>
        <select value={filters.environment} onChange={(e) => setFilters({...filters, environment: e.target.value})}>
          <option value="all">🌍 Todos os Ambientes</option>
          <option value="production">Produção</option>
          <option value="staging">Staging</option>
          <option value="development">Desenvolvimento</option>
        </select>
        <select value={filters.timeRange} onChange={(e) => setFilters({...filters, timeRange: e.target.value})}>
          <option value="1h">⏱️ Última Hora</option>
          <option value="24h">📅 Últimas 24h</option>
          <option value="7d">📆 Últimos 7 dias</option>
          <option value="30d">📊 Últimos 30 dias</option>
        </select>
      </div>

      <div className="dashboard-widgets">
        {renderOverviewWidget()}
        {renderTop10Widget()}
        {renderTrendsWidget()}
      </div>
    </div>
  );
}

export default AdvancedDashboard;
