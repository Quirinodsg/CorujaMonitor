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
          const serversRes = await api.get(`/api/v1/metrics/dashboard/servers?range=${timeRange}`);
          setServersData(serversRes.data);
          break;
        case 'network':
          const networkRes = await api.get(`/api/v1/metrics/dashboard/network?range=${timeRange}`);
          setNetworkData(networkRes.data);
          break;
        case 'webapps':
          const webappsRes = await api.get(`/api/v1/metrics/dashboard/webapps?range=${timeRange}`);
          setWebappsData(webappsRes.data);
          break;
        case 'kubernetes':
          const k8sRes = await api.get(`/api/v1/metrics/dashboard/kubernetes?range=${timeRange}`);
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

// Network Dashboard (placeholder)
const NetworkDashboard = ({ data }) => {
  if (!data) return <div className="loading">Carregando dados de rede...</div>;
  
  return (
    <div className="dashboard-content">
      <h2>Dashboard de Rede (APs/Switches)</h2>
      <p>Em desenvolvimento...</p>
    </div>
  );
};

// WebApps Dashboard (placeholder)
const WebAppsDashboard = ({ data }) => {
  if (!data) return <div className="loading">Carregando dados de WebApps...</div>;
  
  return (
    <div className="dashboard-content">
      <h2>Dashboard de WebApps</h2>
      <p>Em desenvolvimento...</p>
    </div>
  );
};

// Kubernetes Dashboard (placeholder)
const KubernetesDashboard = ({ data }) => {
  if (!data) return <div className="loading">Carregando dados de Kubernetes...</div>;
  
  return (
    <div className="dashboard-content">
      <h2>Dashboard de Kubernetes</h2>
      <p>Em desenvolvimento...</p>
    </div>
  );
};

// Custom Dashboard (placeholder)
const CustomDashboard = () => {
  return (
    <div className="dashboard-content">
      <h2>Dashboard Personalizado</h2>
      <p>Arraste e solte widgets para criar seu dashboard personalizado</p>
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
