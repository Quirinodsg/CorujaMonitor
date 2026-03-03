import React, { useState, useEffect } from 'react';
import './KubernetesDashboard.css';

const KubernetesDashboard = () => {
  const [clusters, setClusters] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [resources, setResources] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 segundos
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Buscar clusters
  const fetchClusters = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/kubernetes/clusters', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setClusters(data);
        
        // Selecionar primeiro cluster automaticamente
        if (data.length > 0 && !selectedCluster) {
          setSelectedCluster(data[0]);
        }
      }
    } catch (err) {
      setError('Erro ao carregar clusters');
      console.error(err);
    }
  };

  // Buscar recursos do cluster
  const fetchResources = async (clusterId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/kubernetes/clusters/${clusterId}/resources`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setResources(data);
      }
    } catch (err) {
      console.error('Erro ao carregar recursos:', err);
    }
  };

  // Buscar métricas do cluster
  const fetchMetrics = async (clusterId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8000/api/v1/kubernetes/clusters/${clusterId}/metrics`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (err) {
      console.error('Erro ao carregar métricas:', err);
    } finally {
      setLoading(false);
    }
  };

  // Carregar dados iniciais
  useEffect(() => {
    fetchClusters();
  }, []);

  // Carregar dados do cluster selecionado
  useEffect(() => {
    if (selectedCluster) {
      setLoading(true);
      fetchResources(selectedCluster.id);
      fetchMetrics(selectedCluster.id);
    }
  }, [selectedCluster]);

  // Auto-refresh
  useEffect(() => {
    if (autoRefresh && selectedCluster) {
      const interval = setInterval(() => {
        fetchResources(selectedCluster.id);
        fetchMetrics(selectedCluster.id);
      }, refreshInterval);

      return () => clearInterval(interval);
    }
  }, [autoRefresh, selectedCluster, refreshInterval]);

  // Agrupar recursos por tipo
  const groupResourcesByType = () => {
    const grouped = {};
    resources.forEach(resource => {
      if (!grouped[resource.resource_type]) {
        grouped[resource.resource_type] = [];
      }
      grouped[resource.resource_type].push(resource);
    });
    return grouped;
  };

  // Calcular estatísticas
  const getResourceStats = (type) => {
    const typeResources = resources.filter(r => r.resource_type === type);
    const total = typeResources.length;
    const healthy = typeResources.filter(r => r.ready || r.status === 'Running' || r.status === 'Ready').length;
    const unhealthy = total - healthy;
    
    return { total, healthy, unhealthy };
  };

  // Renderizar card de cluster
  const renderClusterCard = (cluster) => {
    const isSelected = selectedCluster && selectedCluster.id === cluster.id;
    const statusColor = cluster.connection_status === 'connected' ? '#4caf50' : 
                       cluster.connection_status === 'error' ? '#f44336' : '#ff9800';

    return (
      <div
        key={cluster.id}
        className={`k8s-cluster-card ${isSelected ? 'selected' : ''}`}
        onClick={() => setSelectedCluster(cluster)}
      >
        <div className="k8s-cluster-header">
          <span className="k8s-cluster-icon">☸️</span>
          <span className="k8s-cluster-name">{cluster.cluster_name}</span>
          <span 
            className="k8s-cluster-status"
            style={{ backgroundColor: statusColor }}
          />
        </div>
        <div className="k8s-cluster-info">
          <div className="k8s-cluster-stat">
            <span className="k8s-stat-label">Nodes:</span>
            <span className="k8s-stat-value">{cluster.total_nodes || 0}</span>
          </div>
          <div className="k8s-cluster-stat">
            <span className="k8s-stat-label">Pods:</span>
            <span className="k8s-stat-value">{cluster.total_pods || 0}</span>
          </div>
        </div>
      </div>
    );
  };

  // Renderizar card de métrica
  const renderMetricCard = (title, value, unit, icon, color) => {
    return (
      <div className="k8s-metric-card" style={{ borderLeftColor: color }}>
        <div className="k8s-metric-icon" style={{ color }}>{icon}</div>
        <div className="k8s-metric-content">
          <div className="k8s-metric-title">{title}</div>
          <div className="k8s-metric-value">
            {value !== null && value !== undefined ? value : '-'}
            {unit && <span className="k8s-metric-unit">{unit}</span>}
          </div>
        </div>
      </div>
    );
  };

  // Renderizar tabela de recursos
  const renderResourceTable = (type, typeResources) => {
    const icons = {
      node: '🖥️',
      pod: '📦',
      deployment: '🚀',
      daemonset: '👥',
      statefulset: '💾',
      service: '🌐'
    };

    return (
      <div key={type} className="k8s-resource-section">
        <h3 className="k8s-resource-title">
          {icons[type] || '📋'} {type.charAt(0).toUpperCase() + type.slice(1)}s
          <span className="k8s-resource-count">({typeResources.length})</span>
        </h3>
        <div className="k8s-resource-table-container">
          <table className="k8s-resource-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Namespace</th>
                <th>Status</th>
                {type === 'node' && <><th>CPU</th><th>Memória</th><th>Pods</th></>}
                {type === 'pod' && <><th>Node</th><th>Restarts</th></>}
                {(type === 'deployment' || type === 'statefulset' || type === 'daemonset') && 
                  <><th>Réplicas</th><th>Ready</th></>}
              </tr>
            </thead>
            <tbody>
              {typeResources.slice(0, 10).map(resource => (
                <tr key={resource.id}>
                  <td className="k8s-resource-name">{resource.resource_name}</td>
                  <td>{resource.namespace || '-'}</td>
                  <td>
                    <span className={`k8s-status-badge ${resource.ready ? 'ready' : 'not-ready'}`}>
                      {resource.status}
                    </span>
                  </td>
                  {type === 'node' && (
                    <>
                      <td>{resource.node_cpu_usage ? `${resource.node_cpu_usage.toFixed(1)}%` : '-'}</td>
                      <td>{resource.node_memory_usage ? `${resource.node_memory_usage.toFixed(1)}%` : '-'}</td>
                      <td>{resource.node_pod_count || 0}/{resource.node_pod_capacity || 0}</td>
                    </>
                  )}
                  {type === 'pod' && (
                    <>
                      <td>{resource.pod_node_name || '-'}</td>
                      <td>{resource.pod_restart_count || 0}</td>
                    </>
                  )}
                  {(type === 'deployment' || type === 'statefulset' || type === 'daemonset') && (
                    <>
                      <td>{resource.desired_replicas || 0}</td>
                      <td>{resource.ready_replicas || 0}</td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {typeResources.length > 10 && (
            <div className="k8s-table-footer">
              Mostrando 10 de {typeResources.length} recursos
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading && clusters.length === 0) {
    return (
      <div className="k8s-dashboard">
        <div className="k8s-loading">
          <div className="k8s-spinner"></div>
          <p>Carregando clusters Kubernetes...</p>
        </div>
      </div>
    );
  }

  if (clusters.length === 0) {
    return (
      <div className="k8s-dashboard">
        <div className="k8s-empty">
          <span className="k8s-empty-icon">☸️</span>
          <h2>Nenhum cluster configurado</h2>
          <p>Configure um cluster Kubernetes em Servidores → Monitorar Serviços</p>
        </div>
      </div>
    );
  }

  const groupedResources = groupResourcesByType();

  return (
    <div className="k8s-dashboard">
      {/* Header */}
      <div className="k8s-header">
        <h1>
          <span className="k8s-header-icon">☸️</span>
          Dashboard Kubernetes
        </h1>
        <div className="k8s-header-controls">
          <label className="k8s-auto-refresh">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh ({refreshInterval / 1000}s)
          </label>
          <button 
            className="k8s-refresh-btn"
            onClick={() => {
              if (selectedCluster) {
                fetchResources(selectedCluster.id);
                fetchMetrics(selectedCluster.id);
              }
            }}
          >
            🔄 Atualizar
          </button>
        </div>
      </div>

      {/* Clusters */}
      <div className="k8s-clusters-section">
        <h2>Clusters</h2>
        <div className="k8s-clusters-grid">
          {clusters.map(cluster => renderClusterCard(cluster))}
        </div>
      </div>

      {/* Métricas do Cluster Selecionado */}
      {selectedCluster && metrics && (
        <div className="k8s-metrics-section">
          <h2>Métricas - {selectedCluster.cluster_name}</h2>
          <div className="k8s-metrics-grid">
            {renderMetricCard('Nodes', metrics.total_nodes, '', '🖥️', '#2196f3')}
            {renderMetricCard('Pods', metrics.total_pods, '', '📦', '#4caf50')}
            {renderMetricCard('Deployments', metrics.total_deployments, '', '🚀', '#ff9800')}
            {renderMetricCard('CPU', metrics.cluster_cpu_usage?.toFixed(1), '%', '⚡', '#f44336')}
            {renderMetricCard('Memória', metrics.cluster_memory_usage?.toFixed(1), '%', '💾', '#9c27b0')}
          </div>
        </div>
      )}

      {/* Recursos */}
      {selectedCluster && (
        <div className="k8s-resources-section">
          <h2>Recursos</h2>
          {loading ? (
            <div className="k8s-loading-small">
              <div className="k8s-spinner-small"></div>
              <p>Carregando recursos...</p>
            </div>
          ) : (
            <div className="k8s-resources-container">
              {Object.keys(groupedResources).length === 0 ? (
                <div className="k8s-no-resources">
                  <p>Nenhum recurso coletado ainda. Aguarde a próxima coleta (60 segundos).</p>
                </div>
              ) : (
                Object.entries(groupedResources).map(([type, typeResources]) =>
                  renderResourceTable(type, typeResources)
                )
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default KubernetesDashboard;
