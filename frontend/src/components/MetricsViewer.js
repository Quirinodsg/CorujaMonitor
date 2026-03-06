import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import api from '../services/api';
import './MetricsViewer.css';

const MetricsViewer = () => {
  const [activeTab, setActiveTab] = useState('servers');
  const [timeRange, setTimeRange] = useState('24h');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  
  const [serversData, setServersData] = useState(null);
  const [networkData, setNetworkData] = useState(null);
  const [webappsData, setWebappsData] = useState(null);
  const [kubernetesData, setKubernetesData] = useState(null);

  // Fetch data
  useEffect(() => {
    fetchData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [activeTab, timeRange, autoRefresh, refreshInterval]);

  const fetchData = async () => {
    try {
      switch (activeTab) {
        case 'servers':
          const serversRes = await api.get(`/metrics/dashboard/servers?range=${timeRange}`);
          setServersData(serversRes.data);
          break;
        case 'network':
          const networkRes = await api.get(`/metrics/dashboard/network?range=${timeRange}`);
          setNetworkData(networkRes.data);
          break;
        case 'webapps':
          const webappsRes = await api.get(`/metrics/dashboard/webapps?range=${timeRange}`);
          setWebappsData(webappsRes.data);
          break;
        case 'kubernetes':
          const k8sRes = await api.get(`/metrics/dashboard/kubernetes?range=${timeRange}`);
          setKubernetesData(k8sRes.data);
          break;
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  return (
    <div className="metrics-viewer">
      {/* Header */}
      <div className="metrics-header">
        <div className="metrics-title">
          <h1>📊 Visualização de Métricas</h1>
          <p>Monitoramento em tempo real estilo Grafana</p>
        </div>
        
        <div className="metrics-controls">
          {/* Time Range Selector */}
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="1h">Última 1 hora</option>
            <option value="6h">Últimas 6 horas</option>
            <option value="24h">Últimas 24 horas</option>
            <option value="7d">Últimos 7 dias</option>
            <option value="30d">Últimos 30 dias</option>
          </select>

          {/* Auto Refresh Toggle */}
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <span>Auto-refresh ({refreshInterval / 1000}s)</span>
          </label>

          {/* Refresh Button */}
          <button onClick={fetchData} className="refresh-btn">
            🔄 Atualizar
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="metrics-tabs">
        <button
          className={`tab ${activeTab === 'servers' ? 'active' : ''}`}
          onClick={() => setActiveTab('servers')}
        >
          🖥️ Servidores
        </button>
        <button
          className={`tab ${activeTab === 'network' ? 'active' : ''}`}
          onClick={() => setActiveTab('network')}
        >
          📡 Rede (APs/Switches)
        </button>
        <button
          className={`tab ${activeTab === 'webapps' ? 'active' : ''}`}
          onClick={() => setActiveTab('webapps')}
        >
          🌐 WebApps
        </button>
        <button
          className={`tab ${activeTab === 'kubernetes' ? 'active' : ''}`}
          onClick={() => setActiveTab('kubernetes')}
        >
          ☸️ Kubernetes
        </button>
        <button
          className={`tab ${activeTab === 'custom' ? 'active' : ''}`}
          onClick={() => setActiveTab('custom')}
        >
          ⚙️ Personalizado
        </button>
      </div>

      {/* Content */}
      <div className="metrics-content">
        {activeTab === 'servers' && <ServersDashboard data={serversData} />}
        {activeTab === 'network' && <NetworkDashboard data={networkData} />}
        {activeTab === 'webapps' && <WebAppsDashboard data={webappsData} />}
        {activeTab === 'kubernetes' && <KubernetesDashboard data={kubernetesData} />}
        {activeTab === 'custom' && <CustomDashboard />}
      </div>
    </div>
  );
};

// Gauge Component
const GaugeChart = ({ value, max = 100, label, thresholds = { warning: 80, critical: 95 } }) => {
  const percentage = (value / max) * 100;
  
  let color = '#10b981'; // green
  if (percentage >= thresholds.critical) color = '#ef4444'; // red
  else if (percentage >= thresholds.warning) color = '#f59e0b'; // yellow

  return (
    <div className="gauge-chart">
      <div className="gauge-label">{label}</div>
      <div className="gauge-container">
        <svg viewBox="0 0 200 120" className="gauge-svg">
          {/* Background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="20"
            strokeLinecap="round"
          />
          {/* Value arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={color}
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 2.51} 251`}
          />
          {/* Value text */}
          <text x="100" y="90" textAnchor="middle" className="gauge-value">
            {value.toFixed(1)}%
          </text>
        </svg>
      </div>
    </div>
  );
};

// Servers Dashboard
const ServersDashboard = ({ data }) => {
  if (!data) return <div className="loading">Carregando dados...</div>;

  const { summary, servers, timeseries } = data;

  return (
    <div className="dashboard-content">
      {/* Summary Cards */}
      <div className="summary-cards">
        <GaugeChart 
          value={summary.cpu_avg} 
          label="CPU Média" 
          thresholds={{ warning: 80, critical: 95 }}
        />
        <GaugeChart 
          value={summary.memory_avg} 
          label="Memória Média" 
          thresholds={{ warning: 80, critical: 95 }}
        />
        <GaugeChart 
          value={summary.disk_avg} 
          label="Disco Médio" 
          thresholds={{ warning: 80, critical: 95 }}
        />
        <div className="status-card">
          <div className="status-label">Servidores</div>
          <div className="status-value">
            <span className="status-online">{summary.servers_online}</span>
            <span className="status-separator">/</span>
            <span className="status-total">{summary.servers_total}</span>
          </div>
          <div className="status-subtitle">Online</div>
        </div>
      </div>

      {/* Time Series Charts */}
      <div className="charts-grid">
        {/* CPU Over Time */}
        <div className="chart-card">
          <h3>CPU por Servidor</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeseries.cpu}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Legend />
              {servers.map((server, idx) => (
                <Line
                  key={server.id}
                  type="monotone"
                  dataKey={server.name}
                  stroke={`hsl(${idx * 360 / servers.length}, 70%, 50%)`}
                  strokeWidth={2}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Memory Over Time */}
        <div className="chart-card">
          <h3>Memória por Servidor</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timeseries.memory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Legend />
              {servers.map((server, idx) => (
                <Area
                  key={server.id}
                  type="monotone"
                  dataKey={server.name}
                  fill={`hsl(${idx * 360 / servers.length}, 70%, 50%)`}
                  stroke={`hsl(${idx * 360 / servers.length}, 70%, 40%)`}
                  fillOpacity={0.6}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Server Cards */}
      <div className="server-cards">
        {servers.map(server => (
          <div key={server.id} className={`server-card status-${server.status}`}>
            <div className="server-header">
              <h4>{server.name}</h4>
              <span className={`status-badge ${server.status}`}>
                {server.status === 'ok' ? '● Online' : 
                 server.status === 'warning' ? '⚠ Warning' : 
                 '● Offline'}
              </span>
            </div>
            <div className="server-metrics">
              <div className="metric">
                <span className="metric-label">CPU</span>
                <span className="metric-value">{server.cpu}%</span>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill" 
                    style={{ width: `${server.cpu}%`, backgroundColor: getMetricColor(server.cpu) }}
                  />
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Memória</span>
                <span className="metric-value">{server.memory}%</span>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill" 
                    style={{ width: `${server.memory}%`, backgroundColor: getMetricColor(server.memory) }}
                  />
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Disco</span>
                <span className="metric-value">{server.disk}%</span>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill" 
                    style={{ width: `${server.disk}%`, backgroundColor: getMetricColor(server.disk) }}
                  />
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Uptime</span>
                <span className="metric-value">{server.uptime}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Network Dashboard
const NetworkDashboard = ({ data }) => {
  if (!data) return <div className="loading">Carregando dados de rede...</div>;
  
  const { summary, devices } = data;

  return (
    <div className="dashboard-content">
      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="status-card">
          <div className="status-label">Dispositivos</div>
          <div className="status-value">
            <span className="status-online">{summary.devices_online}</span>
            <span className="status-separator">/</span>
            <span className="status-total">{summary.devices_total}</span>
          </div>
          <div className="status-subtitle">Online</div>
        </div>
        <div className="status-card">
          <div className="status-label">Clientes</div>
          <div className="status-value">
            <span className="status-online">{summary.total_clients}</span>
          </div>
          <div className="status-subtitle">Conectados</div>
        </div>
        <div className="status-card">
          <div className="status-label">Tráfego IN</div>
          <div className="status-value">
            <span className="status-online">{summary.traffic_in}</span>
          </div>
          <div className="status-subtitle">MB</div>
        </div>
        <div className="status-card">
          <div className="status-label">Tráfego OUT</div>
          <div className="status-value">
            <span className="status-online">{summary.traffic_out}</span>
          </div>
          <div className="status-subtitle">MB</div>
        </div>
      </div>

      {/* Device Cards */}
      <div className="server-cards">
        {devices.map(device => (
          <div key={device.id} className={`server-card status-${device.status}`}>
            <div className="server-header">
              <h4>
                {device.type === 'snmp' ? '📡' : device.type === 'network' ? '🔌' : '📶'} {device.name}
              </h4>
              <span className={`status-badge ${device.status}`}>
                {device.status === 'ok' ? '● Online' : 
                 device.status === 'warning' ? '⚠ Warning' : 
                 '● Offline'}
              </span>
            </div>
            <div className="server-metrics">
              <div className="metric">
                <span className="metric-label">Tipo</span>
                <span className="metric-value">{device.type.toUpperCase()}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Clientes</span>
                <span className="metric-value">{device.clients}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Tráfego IN</span>
                <span className="metric-value">{(device.traffic_in / 1024 / 1024).toFixed(2)} MB</span>
              </div>
              <div className="metric">
                <span className="metric-label">Tráfego OUT</span>
                <span className="metric-value">{(device.traffic_out / 1024 / 1024).toFixed(2)} MB</span>
              </div>
              {device.signal > 0 && (
                <div className="metric">
                  <span className="metric-label">Sinal</span>
                  <span className="metric-value">{device.signal} dBm</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {devices.length === 0 && (
        <div className="empty-state">
          <p>📡 Nenhum dispositivo de rede encontrado</p>
          <p className="empty-subtitle">Configure sensores SNMP para monitorar APs e Switches</p>
        </div>
      )}
    </div>
  );
};

// WebApps Dashboard
const WebAppsDashboard = ({ data }) => {
  if (!data) return <div className="loading">Carregando dados de WebApps...</div>;
  
  const { summary, apps } = data;

  return (
    <div className="dashboard-content">
      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="status-card">
          <div className="status-label">Aplicações</div>
          <div className="status-value">
            <span className="status-online">{summary.apps_online}</span>
            <span className="status-separator">/</span>
            <span className="status-total">{summary.apps_total}</span>
          </div>
          <div className="status-subtitle">Online</div>
        </div>
        <div className="status-card">
          <div className="status-label">Tempo Resposta</div>
          <div className="status-value">
            <span className="status-online">{summary.avg_response_time}</span>
          </div>
          <div className="status-subtitle">ms (média)</div>
        </div>
        <div className="status-card">
          <div className="status-label">Taxa de Erro</div>
          <div className="status-value">
            <span className={summary.error_rate > 10 ? "status-critical" : "status-online"}>
              {summary.error_rate}%
            </span>
          </div>
          <div className="status-subtitle">Erros</div>
        </div>
      </div>

      {/* App Cards */}
      <div className="server-cards">
        {apps.map(app => (
          <div key={app.id} className={`server-card status-${app.status}`}>
            <div className="server-header">
              <h4>🌐 {app.name}</h4>
              <span className={`status-badge ${app.status}`}>
                {app.status === 'ok' ? '● Online' : 
                 app.status === 'warning' ? '⚠ Warning' : 
                 '● Offline'}
              </span>
            </div>
            <div className="server-metrics">
              <div className="metric">
                <span className="metric-label">URL</span>
                <span className="metric-value" style={{ fontSize: '0.85em', wordBreak: 'break-all' }}>
                  {app.url || 'N/A'}
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Tempo de Resposta</span>
                <span className="metric-value">{app.response_time} ms</span>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill" 
                    style={{ 
                      width: `${Math.min(app.response_time / 10, 100)}%`, 
                      backgroundColor: app.response_time < 500 ? '#10b981' : app.response_time < 1000 ? '#f59e0b' : '#ef4444'
                    }}
                  />
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Status HTTP</span>
                <span className={`metric-value ${app.status_code >= 200 && app.status_code < 300 ? '' : 'text-red-500'}`}>
                  {app.status_code || 'N/A'}
                </span>
              </div>
              {app.ssl_expires && (
                <div className="metric">
                  <span className="metric-label">SSL</span>
                  <span className="metric-value">
                    {app.ssl_valid ? '✓ Válido' : '✗ Inválido'} - {app.ssl_expires}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {apps.length === 0 && (
        <div className="empty-state">
          <p>🌐 Nenhuma aplicação web encontrada</p>
          <p className="empty-subtitle">Configure sensores HTTP/HTTPS para monitorar suas aplicações</p>
        </div>
      )}
    </div>
  );
};

// Kubernetes Dashboard
const KubernetesDashboard = ({ data }) => {
  if (!data) return <div className="loading">Carregando dados de Kubernetes...</div>;
  
  const { summary, clusters } = data;

  return (
    <div className="dashboard-content">
      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="status-card">
          <div className="status-label">Clusters</div>
          <div className="status-value">
            <span className="status-online">{summary.clusters_total}</span>
          </div>
          <div className="status-subtitle">Total</div>
        </div>
        <div className="status-card">
          <div className="status-label">Pods</div>
          <div className="status-value">
            <span className="status-online">{summary.pods_total}</span>
          </div>
          <div className="status-subtitle">Total</div>
        </div>
        <GaugeChart 
          value={summary.cpu_total} 
          label="CPU Total" 
          thresholds={{ warning: 80, critical: 95 }}
        />
        <GaugeChart 
          value={summary.memory_total} 
          label="Memória Total" 
          thresholds={{ warning: 80, critical: 95 }}
        />
      </div>

      {/* Cluster Cards */}
      <div className="server-cards">
        {clusters.map(cluster => (
          <div key={cluster.id} className={`server-card status-${cluster.status}`}>
            <div className="server-header">
              <h4>☸️ {cluster.name}</h4>
              <span className={`status-badge ${cluster.status}`}>
                {cluster.status === 'ok' ? '● Healthy' : 
                 cluster.status === 'warning' ? '⚠ Warning' : 
                 '● Critical'}
              </span>
            </div>
            <div className="server-metrics">
              <div className="metric">
                <span className="metric-label">Nodes</span>
                <span className="metric-value">{cluster.nodes}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Namespaces</span>
                <span className="metric-value">{cluster.namespaces}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Pods</span>
                <span className="metric-value">{cluster.pods}</span>
              </div>
              <div className="metric">
                <span className="metric-label">CPU</span>
                <span className="metric-value">{cluster.cpu}%</span>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill" 
                    style={{ width: `${cluster.cpu}%`, backgroundColor: getMetricColor(cluster.cpu) }}
                  />
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Memória</span>
                <span className="metric-value">{cluster.memory}%</span>
                <div className="metric-bar">
                  <div 
                    className="metric-bar-fill" 
                    style={{ width: `${cluster.memory}%`, backgroundColor: getMetricColor(cluster.memory) }}
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {clusters.length === 0 && (
        <div className="empty-state">
          <p>☸️ Nenhum cluster Kubernetes encontrado</p>
          <p className="empty-subtitle">Configure sensores Kubernetes para monitorar seus clusters</p>
        </div>
      )}
    </div>
  );
};

// Custom Dashboard
const CustomDashboard = () => {
  const [widgets, setWidgets] = useState([
    { id: 1, type: 'metric', title: 'CPU Média', value: '45%', color: '#10b981' },
    { id: 2, type: 'metric', title: 'Memória Média', value: '62%', color: '#f59e0b' },
    { id: 3, type: 'metric', title: 'Servidores Online', value: '12/15', color: '#3b82f6' },
    { id: 4, type: 'metric', title: 'Incidentes Abertos', value: '3', color: '#ef4444' }
  ]);

  return (
    <div className="dashboard-content">
      <div className="custom-dashboard-header">
        <h2>Dashboard Personalizado</h2>
        <p className="custom-subtitle">
          Configure widgets personalizados para monitorar suas métricas mais importantes
        </p>
      </div>

      {/* Widget Grid */}
      <div className="custom-widgets-grid">
        {widgets.map(widget => (
          <div key={widget.id} className="custom-widget" style={{ borderLeft: `4px solid ${widget.color}` }}>
            <div className="widget-header">
              <h4>{widget.title}</h4>
              <button className="widget-remove" onClick={() => setWidgets(widgets.filter(w => w.id !== widget.id))}>
                ✕
              </button>
            </div>
            <div className="widget-value" style={{ color: widget.color }}>
              {widget.value}
            </div>
          </div>
        ))}
        
        {/* Add Widget Button */}
        <div className="custom-widget add-widget" onClick={() => {
          const newWidget = {
            id: Date.now(),
            type: 'metric',
            title: 'Nova Métrica',
            value: '0',
            color: '#6366f1'
          };
          setWidgets([...widgets, newWidget]);
        }}>
          <div className="add-widget-content">
            <span className="add-icon">+</span>
            <span>Adicionar Widget</span>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="custom-instructions">
        <h3>Como usar:</h3>
        <ul>
          <li>Clique em "Adicionar Widget" para criar novos widgets personalizados</li>
          <li>Clique no ✕ para remover widgets que não precisa</li>
          <li>Em breve: arraste e solte para reorganizar widgets</li>
          <li>Em breve: configure fontes de dados personalizadas para cada widget</li>
        </ul>
      </div>
    </div>
  );
};

// Helper function
const getMetricColor = (value) => {
  if (value >= 95) return '#ef4444'; // red
  if (value >= 80) return '#f59e0b'; // yellow
  return '#10b981'; // green
};

export default MetricsViewer;
