import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import './NOCMode.css';

function NOCMode({ onExit }) {
  const [data, setData] = useState({
    global: null,
    heatmap: [],
    incidents: [],
    kpis: null
  });
  const [currentDashboard, setCurrentDashboard] = useState(0);
  const [autoRotate, setAutoRotate] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const dashboards = ['global', 'heatmap', 'incidents', 'kpis'];

  const loadNOCData = useCallback(async () => {
    try {
      const [global, heatmap, incidents, kpis] = await Promise.all([
        api.get('/noc/global-status', { timeout: 30000 }),
        api.get('/noc/heatmap', { timeout: 30000 }),
        api.get('/noc/active-incidents', { timeout: 30000 }),
        api.get('/noc/kpis', { timeout: 30000 })
      ]);

      setData({
        global: global.data,
        heatmap: heatmap.data,
        incidents: incidents.data,
        kpis: kpis.data
      });
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Erro ao carregar dados NOC:', error);
    }
  }, []);

  useEffect(() => {
    loadNOCData();
    const interval = setInterval(loadNOCData, 3000); // Atualiza a cada 3s
    return () => clearInterval(interval);
  }, [loadNOCData]);

  useEffect(() => {
    if (autoRotate) {
      const rotateInterval = setInterval(() => {
        setCurrentDashboard((prev) => (prev + 1) % dashboards.length);
      }, 15000); // Rotaciona a cada 15s
      return () => clearInterval(rotateInterval);
    }
  }, [autoRotate, dashboards.length]);

  const renderGlobalStatus = () => (
    <div className="noc-dashboard global-status">
      <div className="noc-title">
        <h1>🌍 STATUS GLOBAL DO SISTEMA</h1>
        <div className="noc-subtitle">Visão Multi-Empresa em Tempo Real</div>
      </div>

      <div className="kpi-mega-grid">
        <div className="kpi-mega ok">
          <div className="kpi-icon">✅</div>
          <div className="kpi-value">{data.global?.servers_ok || 0}</div>
          <div className="kpi-label">SERVIDORES OK</div>
        </div>
        <div className="kpi-mega warning">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-value">{data.global?.servers_warning || 0}</div>
          <div className="kpi-label">EM AVISO</div>
        </div>
        <div className="kpi-mega critical">
          <div className="kpi-icon">🔥</div>
          <div className="kpi-value">{data.global?.servers_critical || 0}</div>
          <div className="kpi-label">CRÍTICOS</div>
        </div>
        <div className="kpi-mega availability">
          <div className="kpi-icon">⚡</div>
          <div className="kpi-value">{data.global?.availability || '99.9'}%</div>
          <div className="kpi-label">DISPONIBILIDADE</div>
        </div>
      </div>

      <div className="companies-grid">
        {data.global?.companies?.map((company) => (
          <div key={company.id} className={`company-card ${company.status}`}>
            <div className="company-name">{company.name}</div>
            <div className="company-stats">
              <span className="stat ok">{company.ok}</span>
              <span className="stat warning">{company.warning}</span>
              <span className="stat critical">{company.critical}</span>
            </div>
            <div className="company-availability">{company.availability}%</div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderHeatmap = () => (
    <div className="noc-dashboard heatmap-view">
      <div className="noc-title">
        <h1>🗺️ MAPA DE CALOR - DISPONIBILIDADE</h1>
        <div className="noc-subtitle">Status de Todos os Servidores</div>
      </div>

      <div className="heatmap-grid">
        {data.heatmap?.map((server) => (
          <div 
            key={server.id} 
            className={`heatmap-cell ${server.status}`}
            title={`${server.hostname} - ${server.status}`}
          >
            <div className="cell-name">{server.hostname}</div>
            <div className="cell-status">{server.availability}%</div>
          </div>
        ))}
      </div>

      <div className="heatmap-legend">
        <div className="legend-item">
          <div className="legend-color ok"></div>
          <span>OK (95-100%)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color warning"></div>
          <span>Aviso (90-95%)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color critical"></div>
          <span>Crítico (&lt;90%)</span>
        </div>
      </div>
    </div>
  );

  const renderIncidentsTicker = () => (
    <div className="noc-dashboard incidents-ticker">
      <div className="noc-title">
        <h1>🚨 INCIDENTES ATIVOS</h1>
        <div className="noc-subtitle">
          {data.incidents && data.incidents.length > 0 
            ? `${data.incidents.length} Alertas do Sistema` 
            : 'Nenhum Incidente Ativo'}
        </div>
      </div>

      <div className="ticker-container">
        {!data.incidents || data.incidents.length === 0 ? (
          <div className="no-incidents-message">
            <div className="no-incidents-icon">✅</div>
            <div className="no-incidents-text">Sistema Operando Normalmente</div>
            <div className="no-incidents-subtext">Nenhum incidente ativo no momento</div>
          </div>
        ) : (
          data.incidents.map((incident) => (
            <div key={incident.id} className={`ticker-item ${incident.severity}`}>
              <div className="ticker-time">{new Date(incident.created_at).toLocaleTimeString()}</div>
              <div className="ticker-severity">{incident.severity === 'critical' ? '🔥' : '⚠️'}</div>
              <div className="ticker-server">{incident.server_name}</div>
              <div className="ticker-message">{incident.description}</div>
              <div className="ticker-duration">{incident.duration}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  const renderKPIs = () => (
    <div className="noc-dashboard kpis-view">
      <div className="noc-title">
        <h1>📊 INDICADORES CHAVE DE PERFORMANCE</h1>
        <div className="noc-subtitle">Métricas Consolidadas</div>
      </div>

      <div className="kpis-grid">
        <div className="kpi-card">
          <div className="kpi-header">MTTR</div>
          <div className="kpi-big-value">{data.kpis?.mttr || '15'} min</div>
          <div className="kpi-description">Tempo Médio de Resolução</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header">MTBF</div>
          <div className="kpi-big-value">{data.kpis?.mtbf || '720'} h</div>
          <div className="kpi-description">Tempo Médio Entre Falhas</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header">SLA</div>
          <div className="kpi-big-value">{data.kpis?.sla || '99.95'}%</div>
          <div className="kpi-description">Acordo de Nível de Serviço</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-header">INCIDENTES</div>
          <div className="kpi-big-value">{data.kpis?.incidents_24h || '12'}</div>
          <div className="kpi-description">Últimas 24 Horas</div>
        </div>
      </div>
    </div>
  );

  const renderCurrentDashboard = () => {
    switch (dashboards[currentDashboard]) {
      case 'global': return renderGlobalStatus();
      case 'heatmap': return renderHeatmap();
      case 'incidents': return renderIncidentsTicker();
      case 'kpis': return renderKPIs();
      default: return renderGlobalStatus();
    }
  };

  return (
    <div className="noc-mode">
      <div className="noc-header">
        <div className="noc-logo">🦉 CORUJA MONITOR - NOC</div>
        <div className="noc-controls">
          <button 
            className={`noc-btn ${autoRotate ? 'active' : ''}`}
            onClick={() => setAutoRotate(!autoRotate)}
          >
            {autoRotate ? '⏸️ Pausar' : '▶️ Rotação'}
          </button>
          <button className="noc-btn" onClick={onExit}>
            ❌ Sair
          </button>
        </div>
        <div className="noc-time">
          {lastUpdate.toLocaleTimeString()} • Atualização automática: 3s
        </div>
      </div>

      {renderCurrentDashboard()}

      <div className="noc-footer">
        <div className="dashboard-indicators">
          {dashboards.map((dash, index) => (
            <div 
              key={dash}
              className={`indicator ${index === currentDashboard ? 'active' : ''}`}
              onClick={() => {
                setCurrentDashboard(index);
                setAutoRotate(false);
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default NOCMode;
