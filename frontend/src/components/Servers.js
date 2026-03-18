import React, { useState, useEffect } from 'react';
import api from '../services/api';
import AddSensorModal from './AddSensorModal';
import './Management.css';
import './Management-override.css';
import './SensorGroups.css';

function Servers({ selectedServerId, selectedSensorId }) {
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [highlightedSensorId, setHighlightedSensorId] = useState(null);
  const [sensors, setSensors] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAddSensorModal, setShowAddSensorModal] = useState(false);
  const [showAddServerModal, setShowAddServerModal] = useState(false);
  const [showEditSensorModal, setShowEditSensorModal] = useState(false);
  const [showEditServerModal, setShowEditServerModal] = useState(false);
  const [showSensorDetailsModal, setShowSensorDetailsModal] = useState(false);
  const [editingSensor, setEditingSensor] = useState(null);
  const [editingServer, setEditingServer] = useState(null);
  const [selectedSensorDetails, setSelectedSensorDetails] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [sensorNotes, setSensorNotes] = useState([]);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [newNote, setNewNote] = useState({ note: '', status: 'pending' });
  const [viewMode, setViewMode] = useState('tree'); // 'tree' or 'list'
  const [expandedGroups, setExpandedGroups] = useState({});
  const [expandedSensorGroups, setExpandedSensorGroups] = useState({
    system: false,
    docker: false,
    services: false,
    applications: false,
    network: false
  });
  const [showMoveSensorModal, setShowMoveSensorModal] = useState(false);
  const [movingSensor, setMovingSensor] = useState(null);
  const [targetCategory, setTargetCategory] = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showMonitorServicesModal, setShowMonitorServicesModal] = useState(false);
  const [showAzureServicesModal, setShowAzureServicesModal] = useState(false);
  const [showDatacenterTempModal, setShowDatacenterTempModal] = useState(false);
  const [showAzureWizard, setShowAzureWizard] = useState(false);
  const [azureWizardStep, setAzureWizardStep] = useState(1);
  const [showSNMPWizard, setShowSNMPWizard] = useState(false);
  const [snmpWizardStep, setSNMPWizardStep] = useState(1);
  const [showPrinterWizard, setShowPrinterWizard] = useState(false);
  const [printerWizardStep, setPrinterWizardStep] = useState(1);
  const [showUPSWizard, setShowUPSWizard] = useState(false);
  const [upsWizardStep, setUPSWizardStep] = useState(1);
  const [showHTTPWizard, setShowHTTPWizard] = useState(false);
  const [httpWizardStep, setHTTPWizardStep] = useState(1);
  const [showK8sWizard, setShowK8sWizard] = useState(false);
  const [k8sWizardStep, setK8sWizardStep] = useState(1);
  const [currentWizardType, setCurrentWizardType] = useState(''); // 'snmp', 'ap', 'temp', 'http', 'storage', 'database', 'printer', 'ups', 'k8s'
  const [serverGroups, setServerGroups] = useState([]);
  const [showCreateGroupModal, setShowCreateGroupModal] = useState(false);
  const [showMoveGroupModal, setShowMoveGroupModal] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showGroupsSection, setShowGroupsSection] = useState(false);
  const [reorderingGroup, setReorderingGroup] = useState(null); // nome do grupo sendo reordenado
  const [newGroup, setNewGroup] = useState({
    name: '',
    parent_id: null,
    description: '',
    icon: '📁',
    color: '#2196f3'
  });
  const [azureConfig, setAzureConfig] = useState({
    subscription_id: '',
    tenant_id: '',
    client_id: '',
    client_secret: '',
    resource_group: '',
    selected_resources: []
  });
  const [snmpConfig, setSNMPConfig] = useState({
    probe_id: '',
    name: '',
    device_type: 'generic', // 'generic', 'ap', 'temp', 'storage', 'printer', 'ups'
    ip_address: '',
    snmp_version: 'v2c',
    snmp_community: 'public',
    snmp_port: 161,
    snmp_oid: '',
    threshold_warning: 80,
    threshold_critical: 95,
    description: ''
  });
  const [httpConfig, setHTTPConfig] = useState({
    probe_id: '',
    name: '',
    url: '',
    method: 'GET',
    expected_status: 200,
    timeout: 10,
    check_ssl: true,
    keyword: '',
    threshold_warning: 2000, // ms
    threshold_critical: 5000, // ms
    description: ''
  });
  const [k8sConfig, setK8sConfig] = useState({
    cluster_name: '',
    cluster_type: 'vanilla', // 'vanilla', 'aks', 'eks', 'gke', 'openshift'
    kubeconfig_content: '',
    api_endpoint: '',
    auth_method: 'kubeconfig', // 'kubeconfig', 'service_account', 'token'
    service_account_token: '',
    ca_cert: '',
    namespaces: [],
    monitor_all_namespaces: true,
    selected_resources: []
  });
  const [tempSensorConfig, setTempSensorConfig] = useState({
    name: '',
    ip_address: '',
    snmp_community: 'public',
    snmp_version: 'v2c',
    snmp_port: 161,
    temp_oid: '1.3.6.1.4.1.9.9.13.1.3.1.3',
    threshold_warning: 28,
    threshold_critical: 32
  });
  const [availableServices, setAvailableServices] = useState([]);
  const [availableDisks, setAvailableDisks] = useState([]);
  const [loadingServices, setLoadingServices] = useState(false);
  const [loadingDisks, setLoadingDisks] = useState(false);
  const [probes, setProbes] = useState([]);
  const [newServer, setNewServer] = useState({
    probe_id: '',
    hostname: '',
    ip_address: '',
    device_type: 'server',
    monitoring_protocol: 'wmi',
    snmp_version: 'v2c',
    snmp_community: 'public',
    snmp_port: 161,
    environment: 'production',
    monitoring_schedule: null,
    group_name: ''
  });
  const [newSensor, setNewSensor] = useState({
    sensor_type: 'service',
    name: '',
    service_name: '',
    disk_name: '',
    threshold_warning: 80,
    threshold_critical: 95
  });

  useEffect(() => {
    loadServers();
    loadProbes();
    loadServerGroups();
    const interval = setInterval(loadServers, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Auto-select server if selectedServerId is provided
    if (selectedServerId && servers.length > 0) {
      const server = servers.find(s => s.id === selectedServerId);
      if (server) {
        setSelectedServer(server);
      }
    }
  }, [selectedServerId, servers]);

  useEffect(() => {
    // Se também foi passado um sensor específico, destacá-lo após os sensores serem carregados
    if (selectedSensorId && sensors.length > 0) {
      console.log('🎯 Navegando para sensor ID:', selectedSensorId, 'Total sensores:', sensors.length);
      
      // Encontrar o sensor e expandir seu grupo
      const sensor = sensors.find(s => s.id === selectedSensorId);
      if (sensor) {
        console.log('✔ Sensor encontrado:', sensor.name, 'Tipo:', sensor.sensor_type);
        // Determinar qual grupo o sensor pertence
        let groupKey = null;
        const type = sensor.sensor_type;
        
        if (['ping', 'cpu', 'memory', 'disk', 'system', 'network', 'uptime', 'network_in', 'network_out'].includes(type)) {
          groupKey = 'system';
        } else if (type === 'docker') {
          groupKey = 'docker';
        } else if (type === 'service') {
          groupKey = 'services';
        } else if (['hyperv', 'kubernetes'].includes(type)) {
          groupKey = 'applications';
        } else if (['http', 'port', 'dns', 'ssl', 'snmp'].includes(type)) {
          groupKey = 'network';
        }
        
        // Expandir o grupo do sensor
        if (groupKey) {
          console.log('📂 Expandindo grupo:', groupKey);
          setExpandedSensorGroups(prev => ({
            ...prev,
            [groupKey]: true
          }));
        }
      } else {
        console.log('✖ Sensor NÃO encontrado! ID procurado:', selectedSensorId);
      }
      
      setHighlightedSensorId(selectedSensorId);
      
      // Rolar até o sensor após um delay maior para garantir que o grupo foi expandido
      setTimeout(() => {
        const sensorElement = document.getElementById(`sensor-${selectedSensorId}`);
        if (sensorElement) {
          console.log('📣 Rolando até o sensor');
          sensorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          
          // Remover destaque após 3 segundos
          setTimeout(() => {
            setHighlightedSensorId(null);
          }, 3000);
        } else {
          console.log('✖ Elemento DOM não encontrado: sensor-' + selectedSensorId);
        }
      }, 800);
    } else {
      if (selectedSensorId) {
        console.log('⏳ Aguardando sensores... ID:', selectedSensorId, 'Sensores:', sensors.length);
      }
    }
  }, [selectedSensorId, sensors]);

  const loadProbes = async () => {
    try {
      const response = await api.get('/probes');
      setProbes(response.data);
    } catch (error) {
      console.error('Erro ao carregar probes:', error);
    }
  };

  const loadServerGroups = async () => {
    try {
      const response = await api.get('/sensor-groups');
      setServerGroups(response.data);
    } catch (error) {
      console.error('Erro ao carregar grupos:', error);
    }
  };

  const handleCreateGroup = async () => {
    if (!newGroup.name.trim()) {
      alert('Digite um nome para o grupo');
      return;
    }

    try {
      await api.post('/sensor-groups', newGroup);
      setShowCreateGroupModal(false);
      setNewGroup({
        name: '',
        parent_id: null,
        description: '',
        icon: '📁',
        color: '#2196f3'
      });
      loadServerGroups();
      alert('Grupo criado com sucesso!');
    } catch (error) {
      console.error('Erro ao criar grupo:', error);
      alert('Erro ao criar grupo: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteGroup = async (groupId, groupName) => {
    if (!window.confirm(`Tem certeza que deseja excluir o grupo "${groupName}"?\n\nOs servidores/sensores deste grupo ficarão sem grupo.`)) {
      return;
    }

    try {
      await api.delete(`/sensor-groups/${groupId}`);
      loadServerGroups();
      alert('Grupo excluído com sucesso!');
    } catch (error) {
      console.error('Erro ao excluir grupo:', error);
      alert('Erro ao excluir grupo: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleMoveGroup = async () => {
    if (!selectedGroup) return;

    try {
      await api.post(`/sensor-groups/${selectedGroup.id}/move`, {
        new_parent_id: newGroup.parent_id
      });
      setShowMoveGroupModal(false);
      setSelectedGroup(null);
      setNewGroup({
        name: '',
        parent_id: null,
        description: '',
        icon: '📁',
        color: '#2196f3'
      });
      loadServerGroups();
      alert('Grupo movido com sucesso!');
    } catch (error) {
      console.error('Erro ao mover grupo:', error);
      alert('Erro ao mover grupo: ' + (error.response?.data?.detail || error.message));
    }
  };

  useEffect(() => {
    // Expand all groups by default
    const groups = {};
    Object.keys(groupServersByCompany()).forEach(group => {
      groups[group] = true;
    });
    setExpandedGroups(groups);
  }, [servers]);

  useEffect(() => {
    if (selectedServer) {
      loadSensors(selectedServer.id);
      const interval = setInterval(() => loadSensors(selectedServer.id), 10000); // Refresh every 10s
      return () => clearInterval(interval);
    }
  }, [selectedServer]);

  const loadServers = async () => {
    try {
      const response = await api.get('/servers/');
      setServers(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar servidores:', error);
      setLoading(false);
    }
  };

  const getSensorOrder = (sensor) => {
    // Define order: Ping, CPU, Memory, Disk, Uptime, Network IN, Network OUT
    const typeOrder = {
      'ping': 1,
      'cpu': 2,
      'memory': 3,
      'disk': 4,
      'system': 5,  // uptime
      'uptime': 5,
      'network': 6,
      'network_in': 6,
      'network_out': 6.5,
      'service': 7,
      'hyperv': 8,
      'process': 9,
      'custom': 10
    };
    
    const baseOrder = typeOrder[sensor.sensor_type] || 99;
    
    // For network, sort IN before OUT
    if (sensor.sensor_type === 'network') {
      if (sensor.name.includes('_in')) return 6.0;  // Network IN
      if (sensor.name.includes('_out')) return 6.5; // Network OUT
    }
    
    return baseOrder;
  };

  const loadSensors = async (serverId) => {
    try {
      const response = await api.get(`/sensors/?server_id=${serverId}`);
      
      // Sort sensors by defined order
      const sortedSensors = response.data.sort((a, b) => {
        return getSensorOrder(a) - getSensorOrder(b);
      });
      
      setSensors(sortedSensors);
      
      // Load latest metrics for ALL sensors in a single batch request
      if (sortedSensors.length > 0) {
        try {
          const ids = sortedSensors.map(s => s.id).join(',');
          const batchResponse = await api.get(`/metrics/latest/batch?sensor_ids=${ids}`);
          setMetrics(batchResponse.data);
        } catch (err) {
          console.error('Erro ao carregar métricas em batch:', err);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar sensores:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ok': return '#4caf50';
      case 'warning': return '#ff9800';
      case 'critical': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const formatValue = (value, unit) => {
    if (unit === 'percent') {
      return `${value.toFixed(1)}%`;
    } else if (unit === 'bytes/s') {
      const mbps = value / 1024 / 1024;
      return `${mbps.toFixed(2)} MB/s`;
    } else if (unit === 'status') {
      return value === 1 ? 'Online' : 'Offline';
    } else if (unit === 'days') {
      // Format uptime as Days/Hours/Minutes
      const days = Math.floor(value);
      const hours = Math.floor((value - days) * 24);
      const minutes = Math.floor(((value - days) * 24 - hours) * 60);
      return `${days}d ${hours}h ${minutes}m`;
    } else if (unit === 'ms') {
      // Para valores muito baixos (< 1ms), mostrar 2 casas decimais
      if (value < 1) {
        return `${value.toFixed(2)} ms`;
      }
      return `${Math.round(value)} ms`;
    }
    return value.toFixed(2);
  };

  const getSensorIcon = (type) => {
    switch (type) {
      case 'ping': return '📡';
      case 'cpu': return '🖥️';
      case 'memory': return '🧠';
      case 'disk': return '💾';
      case 'network': return '🌐';
      case 'service': return '⚙️';
      case 'system': return '⏱️';
      case 'hyperv': return '🖼️';
      case 'udm': return '📡';
      case 'docker': return '🐳';
      case 'snmp': return '🌐';
      case 'snmp_uptime': return '⏱️';
      case 'snmp_cpu': return '🖥️';
      case 'snmp_memory': return '🧠';
      case 'snmp_traffic': return '📊';
      case 'snmp_interface': return '🔎';
      default: return '📊';
    }
  };

  // Função para agrupar sensores por tipo
  const groupSensorsByType = (sensors) => {
    const groups = {
      system: {
        name: 'Sistema',
        icon: '🖥️',
        sensors: [],
        priority: 1,
        color: '#4caf50'
      },
      docker: {
        name: 'Docker',
        icon: '🐳',
        sensors: [],
        priority: 2,
        color: '#2196f3',
        showSummary: true
      },
      services: {
        name: 'Serviços',
        icon: '⚙️',
        sensors: [],
        priority: 3,
        color: '#ff9800'
      },
      applications: {
        name: 'Aplicações',
        icon: '📪',
        sensors: [],
        priority: 4,
        color: '#9c27b0'
      },
      network: {
        name: 'Rede',
        icon: '🌐',
        sensors: [],
        priority: 5,
        color: '#00bcd4'
      }
    };

    sensors.forEach(sensor => {
      const type = sensor.sensor_type;
      
      if (['ping', 'cpu', 'memory', 'disk', 'system', 'network', 'uptime', 'network_in', 'network_out'].includes(type)) {
        groups.system.sensors.push(sensor);
      } else if (type === 'docker') {
        groups.docker.sensors.push(sensor);
      } else if (type === 'service') {
        groups.services.sensors.push(sensor);
      } else if (['hyperv', 'kubernetes'].includes(type)) {
        groups.applications.sensors.push(sensor);
      } else if (['http', 'port', 'dns', 'ssl', 'snmp', 'snmp_uptime', 'snmp_cpu', 'snmp_memory', 'snmp_traffic', 'snmp_interface'].includes(type)) {
        groups.network.sensors.push(sensor);
      } else {
        // Sensor de tipo desconhecido - adicionar ao grupo apropriado ou criar novo
        console.warn('Sensor type not recognized:', type, sensor);
      }
    });

    // Retornar TODOS os grupos, mesmo vazios, ordenados por prioridade
    return Object.entries(groups).sort((a, b) => a[1].priority - b[1].priority);
  };

  const toggleSensorGroup = (groupKey) => {
    setExpandedSensorGroups(prev => {
      const isCurrentlyExpanded = prev[groupKey];
      
      // Se está expandindo, colapsa todos os outros
      if (!isCurrentlyExpanded) {
        return {
          system: false,
          docker: false,
          services: false,
          applications: false,
          network: false,
          [groupKey]: true
        };
      }
      
      // Se está colapsando, apenas colapsa este
      return {
        ...prev,
        [groupKey]: false
      };
    });
  };

  const getGroupStatusCounts = (groupSensors) => {
    const counts = { ok: 0, warning: 0, critical: 0, unknown: 0 };
    
    groupSensors.forEach(sensor => {
      const metric = metrics[sensor.id];
      if (metric) {
        counts[metric.status] = (counts[metric.status] || 0) + 1;
      } else {
        counts.unknown++;
      }
    });
    
    return counts;
  };

  const renderDockerSummary = (dockerSensors) => {
    const totalSensor = dockerSensors.find(s => s.name.includes('Total'));
    const runningSensor = dockerSensors.find(s => s.name.includes('Running'));
    const stoppedSensor = dockerSensors.find(s => s.name.includes('Stopped'));
    
    const totalMetric = totalSensor ? metrics[totalSensor.id] : null;
    const runningMetric = runningSensor ? metrics[runningSensor.id] : null;
    const stoppedMetric = stoppedSensor ? metrics[stoppedSensor.id] : null;
    
    if (!totalMetric && !runningMetric && !stoppedMetric) return null;
    
    return (
      <div className="docker-summary">
        {totalMetric && (
          <div className="summary-card">
            <div className="summary-icon">📪</div>
            <div className="summary-value">{totalMetric.value || 0}</div>
            <div className="summary-label">Total</div>
          </div>
        )}
        {runningMetric && (
          <div className="summary-card">
            <div className="summary-icon">✔</div>
            <div className="summary-value">{runningMetric.value || 0}</div>
            <div className="summary-label">Rodando</div>
          </div>
        )}
        {stoppedMetric && (
          <div className="summary-card">
            <div className="summary-icon">⏹️</div>
            <div className="summary-value">{stoppedMetric.value || 0}</div>
            <div className="summary-label">Parados</div>
          </div>
        )}
      </div>
    );
  };

  const renderSystemSummary = (systemSensors) => {
    let total = systemSensors.length;
    let ok = 0;
    let problems = 0;
    
    systemSensors.forEach(sensor => {
      const metric = metrics[sensor.id];
      if (metric) {
        if (metric.status === 'ok') ok++;
        else problems++;
      }
    });
    
    if (total === 0) return null;
    
    return (
      <div className="docker-summary">
        <div className="summary-card">
          <div className="summary-icon">📊</div>
          <div className="summary-value">{total}</div>
          <div className="summary-label">Total</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">✔</div>
          <div className="summary-value">{ok}</div>
          <div className="summary-label">OK</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">⚠️</div>
          <div className="summary-value">{problems}</div>
          <div className="summary-label">Problemas</div>
        </div>
      </div>
    );
  };

  const renderServicesSummary = (serviceSensors) => {
    let total = serviceSensors.length;
    let running = 0;
    let stopped = 0;
    
    serviceSensors.forEach(sensor => {
      const metric = metrics[sensor.id];
      if (metric) {
        if (metric.status === 'ok') running++;
        else stopped++;
      }
    });
    
    if (total === 0) return null;
    
    return (
      <div className="docker-summary">
        <div className="summary-card">
          <div className="summary-icon">📊</div>
          <div className="summary-value">{total}</div>
          <div className="summary-label">Total</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">✔</div>
          <div className="summary-value">{running}</div>
          <div className="summary-label">Rodando</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">⏹️</div>
          <div className="summary-value">{stopped}</div>
          <div className="summary-label">Parados</div>
        </div>
      </div>
    );
  };

  const renderApplicationsSummary = (appSensors) => {
    let total = appSensors.length;
    let active = 0;
    let inactive = 0;
    
    appSensors.forEach(sensor => {
      const metric = metrics[sensor.id];
      if (metric) {
        if (metric.status === 'ok') active++;
        else inactive++;
      }
    });
    
    if (total === 0) return null;
    
    return (
      <div className="docker-summary">
        <div className="summary-card">
          <div className="summary-icon">📪</div>
          <div className="summary-value">{total}</div>
          <div className="summary-label">Total</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">✔</div>
          <div className="summary-value">{active}</div>
          <div className="summary-label">Ativas</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">⏹️</div>
          <div className="summary-value">{inactive}</div>
          <div className="summary-label">Inativas</div>
        </div>
      </div>
    );
  };

  const renderNetworkSummary = (networkSensors) => {
    let total = networkSensors.length;
    let online = 0;
    let offline = 0;
    
    networkSensors.forEach(sensor => {
      const metric = metrics[sensor.id];
      if (metric) {
        if (metric.status === 'ok') online++;
        else offline++;
      }
    });
    
    if (total === 0) return null;
    
    return (
      <div className="docker-summary">
        <div className="summary-card">
          <div className="summary-icon">🌐</div>
          <div className="summary-value">{total}</div>
          <div className="summary-label">Total</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">✔</div>
          <div className="summary-value">{online}</div>
          <div className="summary-label">Online</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">✖</div>
          <div className="summary-value">{offline}</div>
          <div className="summary-label">Offline</div>
        </div>
      </div>
    );
  };

  const renderSensorCard = (sensor) => {
    const metric = metrics[sensor.id];
    const hasNote = sensor.last_note && sensor.last_note_by;
    const isAcknowledged = sensor.is_acknowledged;
    const sensorNameLength = sensor.name ? sensor.name.length : 0;
    
    return (
      <div 
        key={sensor.id}
        id={`sensor-${sensor.id}`}
        className={`sensor-card ${highlightedSensorId === sensor.id ? 'highlighted' : ''}`}
        data-sensor-type={sensor.sensor_type}
        data-sensor-name-length={sensorNameLength}
        data-status={sensor.status}
        title={hasNote ? `Última nota: ${sensor.last_note}\n\nPor: ${sensor.last_note_by_name || 'Técnico'}\nEm: ${sensor.last_note_at ? new Date(sensor.last_note_at).toLocaleString('pt-BR') : ''}` : ''}
      >
        <div className="sensor-card-actions">
          <button 
            className="sensor-action-btn"
            onClick={(e) => handleViewSensorDetails(sensor, e)}
            title="Ver detalhes e análise da IA"
          >
            🔬
          </button>
          <button 
            className="sensor-action-btn"
            onClick={(e) => handleOpenMoveSensorModal(sensor, e)}
            title="Mover para outra categoria"
          >
            📁
          </button>
          <button 
            className="sensor-action-btn"
            onClick={(e) => {
              e.stopPropagation();
              handleEditSensor(sensor);
            }}
            title="Editar sensor"
          >
            ✏️
          </button>
          <button 
            className="sensor-delete-btn"
            onClick={(e) => {
              e.stopPropagation();
              handleDeleteSensor(sensor.id, sensor.name);
            }}
            title="Remover sensor"
          >
            ×
          </button>
        </div>
        
        {isAcknowledged && (
          <div className="sensor-acknowledged-badge" title="Verificado pela TI - Alertas suprimidos">
            ✔ Verificado pela TI
          </div>
        )}
        
        <div className="sensor-header">
          <span className="sensor-icon">{getSensorIcon(sensor.sensor_type)}</span>
          <h3>{sensor.name}</h3>
        </div>
        {metric ? (
          <>
            <div className="sensor-value">
              {formatValue(metric.value, metric.unit)}
            </div>
            <div 
              className={`sensor-status-bar ${isAcknowledged ? 'acknowledged' : ''}`}
              style={{ backgroundColor: isAcknowledged ? '#2196f3' : getStatusColor(metric.status) }}
            >
              {isAcknowledged ? 'EM ANüLISE' : metric.status.toUpperCase()}
            </div>
            <div className="sensor-timestamp">
              Atualizado: {new Date(metric.timestamp).toLocaleString('pt-BR')}
            </div>
          </>
        ) : (
          <div className="sensor-no-data">Aguardando dados...</div>
        )}
        <div className="sensor-thresholds">
          {sensor.sensor_type === 'ping' ? (
            <>⚠️ {sensor.threshold_warning || 100}ms | 🔥 {sensor.threshold_critical || 200}ms</>
          ) : sensor.sensor_type === 'network' ? (
            <>⚠️ {sensor.threshold_warning || 80}MB/s | 🔥 {sensor.threshold_critical || 95}MB/s</>
          ) : (sensor.sensor_type === 'system' || sensor.sensor_type === 'uptime') ? (
            <>⚠️ {sensor.threshold_warning ? `${Math.floor(sensor.threshold_warning * 24)}h` : '12h'} | 🔥 {sensor.threshold_critical ? `${Math.floor(sensor.threshold_critical * 60)}min` : '2h'} (uptime mín.)</>
          ) : (
            <>⚠️ {sensor.threshold_warning || 80}% | 🔥 {sensor.threshold_critical || 95}%</>
          )}
        </div>
        
        {hasNote && (
          <div className="sensor-last-note">
            <span className="note-icon">📥</span>
            <span className="note-preview">{sensor.last_note.substring(0, 50)}{sensor.last_note.length > 50 ? '...' : ''}</span>
          </div>
        )}
      </div>
    );
  };

  const renderGroupedSensors = () => {
    const grouped = groupSensorsByType(sensors);
    
    return (
      <div className="sensors-grouped">
        {grouped.map(([groupKey, group]) => {
          const isExpanded = expandedSensorGroups[groupKey];
          const statusCounts = getGroupStatusCounts(group.sensors);
          
          return (
            <div key={groupKey} className="sensor-group">
              <div 
                className="sensor-group-header"
                onClick={() => toggleSensorGroup(groupKey)}
                style={{ borderLeftColor: group.color }}
              >
                <span className="group-icon">{group.icon}</span>
                <span className="group-name">{group.name}</span>
                <span className="group-count">({group.sensors.length})</span>
                <span className="group-status">
                  {statusCounts.ok > 0 && <span className="status-badge status-ok">● {statusCounts.ok}</span>}
                  {statusCounts.warning > 0 && <span className="status-badge status-warning">● {statusCounts.warning}</span>}
                  {statusCounts.critical > 0 && <span className="status-badge status-critical">● {statusCounts.critical}</span>}
                </span>
                <span className="group-toggle">{isExpanded ? '▼' : '▶'}</span>
              </div>
              
              {isExpanded && (
                <div className="sensor-group-content">
                  {groupKey === 'docker' && group.showSummary && renderDockerSummary(group.sensors)}
                  
                  <div className="sensors-grid">
                    {group.sensors.map(sensor => renderSensorCard(sensor))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  const renderMixedSensors = () => {
    const grouped = groupSensorsByType(sensors);
    const aggregatorCards = [];
    
    grouped.forEach(([groupKey, group]) => {
      const isExpanded = expandedSensorGroups[groupKey];
      const statusCounts = getGroupStatusCounts(group.sensors);
      
      // Card agregador compacto
      const aggregatorCard = (
        <div 
          key={`agg-${groupKey}`}
          className={`category-card ${isExpanded ? 'expanded' : ''}`}
          style={{ borderLeftColor: group.color }}
        >
          {/* Header compacto - só ícone e contador */}
          <div 
            className="category-header"
            onClick={() => toggleSensorGroup(groupKey)}
          >
            <span className="category-icon">{group.icon}</span>
            <span className="category-name">{group.name}</span>
            <span className="category-count">{group.sensors.length}</span>
            
            {/* Status badges */}
            {group.sensors.length > 0 && (
              <div className="category-status">
                {statusCounts.ok > 0 && <span className="status-badge ok">✔ {statusCounts.ok}</span>}
                {statusCounts.warning > 0 && <span className="status-badge warning">⚠️ {statusCounts.warning}</span>}
                {statusCounts.critical > 0 && <span className="status-badge critical">🔥 {statusCounts.critical}</span>}
              </div>
            )}
            
            <span className="category-toggle">{isExpanded ? '▲' : '▼'}</span>
          </div>
          
          {/* Sensores aparecem DENTRO do card quando expandido */}
          {isExpanded && group.sensors.length > 0 && (
            <div className="category-sensors">
              <div className="sensors-grid-inner">
                {group.sensors.map(sensor => renderSensorCard(sensor))}
              </div>
            </div>
          )}
        </div>
      );
      
      aggregatorCards.push(aggregatorCard);
    });
    
    return (
      <div className="categories-container">
        {aggregatorCards}
      </div>
    );
  };



  const handleDeleteSensor = async (sensorId, sensorName) => {
    if (!window.confirm(`Tem certeza que deseja remover o sensor "${sensorName}"?`)) {
      return;
    }

    try {
      console.log(`Tentando deletar sensor ${sensorId}...`);
      const response = await api.delete(`/sensors/${sensorId}`);
      console.log('Sensor deletado com sucesso:', response);
      loadSensors(selectedServer.id);
      alert('Sensor removido com sucesso!');
    } catch (error) {
      console.error('Erro ao remover sensor:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response,
        request: error.request
      });
      
      // Se DELETE falhar, tentar desativar o sensor
      // CORRECAO 09MAR: Fallback para quando sensor nao existe no banco mas probe continua enviando
      if (error.response && error.response.status === 404) {
        console.log('Sensor não encontrado no banco, tentando desativar...');
        try {
          await api.put(`/sensors/${sensorId}`, { is_active: false });
          console.log('Sensor desativado com sucesso');
          loadSensors(selectedServer.id);
          alert('Sensor não pôde ser deletado, mas foi desativado. Ele não aparecerá mais no dashboard.');
        } catch (deactivateError) {
          console.error('Erro ao desativar sensor:', deactivateError);
          alert('Erro ao remover/desativar sensor. Verifique os logs do console (F12).');
        }
      } else {
        let errorMessage = 'Erro desconhecido';
        if (error.response) {
          // Servidor respondeu com erro
          errorMessage = error.response.data?.detail || `Erro ${error.response.status}`;
        } else if (error.request) {
          // Requisição foi feita mas sem resposta
          errorMessage = 'Sem resposta do servidor. Verifique se a API está rodando.';
        } else {
          // Erro ao configurar requisição
          errorMessage = error.message;
        }
        
        alert('Erro ao remover sensor: ' + errorMessage);
      }
    }
  };

  const handleReorderServer = async (server, groupServers, direction) => {
    const currentIndex = groupServers.findIndex(s => s.id === server.id);
    const targetIndex = currentIndex + direction;
    if (targetIndex < 0 || targetIndex >= groupServers.length) return;

    const target = groupServers[targetIndex];
    const currentOrder = server.sort_order ?? currentIndex;
    const targetOrder = target.sort_order ?? targetIndex;

    try {
      await Promise.all([
        api.put(`/servers/${server.id}/reorder`, { sort_order: targetOrder }),
        api.put(`/servers/${target.id}/reorder`, { sort_order: currentOrder })
      ]);
      loadServers();
    } catch (error) {
      console.error('Erro ao reordenar servidor:', error);
    }
  };

  const handleDeleteServer = async (serverId, serverName, e) => {
    e.stopPropagation(); // Prevent server selection
    
    if (!window.confirm(`⚠️ ATENÇÃO: Tem certeza que deseja remover o servidor "${serverName}"?\n\nIsso irá remover:\n- O servidor\n- Todos os sensores\n- Todas as métricas\n- Todos os incidentes\n\nEsta ação NÃO pode ser desfeita!`)) {
      return;
    }

    try {
      await api.delete(`/servers/${serverId}`);
      
      // Clear selection if deleted server was selected
      if (selectedServer && selectedServer.id === serverId) {
        setSelectedServer(null);
        setSensors([]);
        setMetrics({});
      }
      
      loadServers();
      alert('Servidor removido com sucesso!');
    } catch (error) {
      console.error('Erro ao remover servidor:', error);
      alert('Erro ao remover servidor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleAddServer = async () => {
    if (!newServer.probe_id || !newServer.hostname || !newServer.ip_address) {
      alert('Preencha todos os campos obrigatórios');
      return;
    }

    // VALIDAÇÃO: Hostname não pode ser um IP (requisito para Kerberos)
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (ipPattern.test(newServer.hostname)) {
      alert('✖ ERRO: Hostname não pode ser um endereço IP!\n\n' +
            '⚠️ Para autenticação Kerberos funcionar, você DEVE usar:\n' +
            '✔ Hostname completo (FQDN): SRVHVSPRD010.ad.techbiz.com.br\n' +
            '✔ Hostname curto: SRVHVSPRD010\n\n' +
            '✖ NÃO use IP no campo Hostname: ' + newServer.hostname + '\n\n' +
            'O IP deve ser preenchido no campo "Endereço IP" separadamente.');
      return;
    }

    // Validação adicional: hostname deve ter pelo menos 3 caracteres
    if (newServer.hostname.length < 3) {
      alert('✖ Hostname muito curto. Use o nome completo do servidor (ex: SRVHVSPRD010)');
      return;
    }

    try {
      await api.post('/servers/', {
        probe_id: parseInt(newServer.probe_id),
        hostname: newServer.hostname,
        ip_address: newServer.ip_address,
        os_type: 'Windows',
        device_type: newServer.device_type,
        monitoring_protocol: newServer.monitoring_protocol,
        snmp_version: newServer.monitoring_protocol === 'snmp' ? newServer.snmp_version : null,
        snmp_community: newServer.monitoring_protocol === 'snmp' ? newServer.snmp_community : null,
        snmp_port: newServer.monitoring_protocol === 'snmp' ? parseInt(newServer.snmp_port) : null,
        environment: newServer.environment,
        monitoring_schedule: newServer.environment === 'custom' ? newServer.monitoring_schedule : null,
        group_name: newServer.group_name || null
      });

      setShowAddServerModal(false);
      setNewServer({
        probe_id: '',
        hostname: '',
        ip_address: '',
        device_type: 'server',
        monitoring_protocol: 'wmi',
        snmp_version: 'v2c',
        snmp_community: 'public',
        snmp_port: 161,
        environment: 'production',
        monitoring_schedule: null,
        group_name: ''
      });
      loadServers();
      alert('Servidor adicionado com sucesso! A probe começará a monitorá-lo automaticamente.');
    } catch (error) {
      console.error('Erro ao adicionar servidor:', error);
      alert('Erro ao adicionar servidor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleAddSensor = async (sensorData) => {
    if (!selectedServer || !sensorData || !sensorData.name) {
      alert('Preencha todos os campos obrigatórios');
      return;
    }

    try {
      await api.post('/sensors/', {
        server_id: selectedServer.id,
        sensor_type: sensorData.sensor_type,
        name: sensorData.name,
        threshold_warning: parseFloat(sensorData.threshold_warning),
        threshold_critical: parseFloat(sensorData.threshold_critical)
      });

      setShowAddSensorModal(false);
      loadSensors(selectedServer.id);
      alert('Sensor adicionado com sucesso!');
    } catch (error) {
      console.error('Erro ao adicionar sensor:', error);
      alert('Erro ao adicionar sensor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const loadAvailableServices = async () => {
    if (!selectedServer) return;
    
    setLoadingServices(true);
    try {
      const response = await api.get(`/probe-commands/services/${selectedServer.id}`);
      setAvailableServices(response.data.services || []);
    } catch (error) {
      console.error('Erro ao carregar serviços:', error);
      // Fallback to common services
      setAvailableServices([
        {name: "W3SVC", display_name: "IIS Web Server"},
        {name: "MSSQLSERVER", display_name: "SQL Server"},
        {name: "MySQL", display_name: "MySQL Server"},
        {name: "Spooler", display_name: "Print Spooler"},
        {name: "EventLog", display_name: "Windows Event Log"},
        {name: "WinRM", display_name: "Windows Remote Management"},
        {name: "TermService", display_name: "Remote Desktop Services"},
      ]);
    } finally {
      setLoadingServices(false);
    }
  };

  const loadAvailableDisks = async () => {
    if (!selectedServer) return;
    
    setLoadingDisks(true);
    try {
      const response = await api.get(`/probe-commands/disks/${selectedServer.id}`);
      setAvailableDisks(response.data.disks || []);
    } catch (error) {
      console.error('Erro ao carregar discos:', error);
      // Fallback to common disks
      setAvailableDisks([
        {name: "C:", display_name: "Disco Local (C:)"},
        {name: "D:", display_name: "Disco Local (D:)"},
        {name: "E:", display_name: "Disco Local (E:)"},
      ]);
    } finally {
      setLoadingDisks(false);
    }
  };

  const handleServiceSelect = (serviceName) => {
    setNewSensor({
      ...newSensor,
      service_name: serviceName,
      name: `service_${serviceName}`
    });
  };

  const handleDiskSelect = (diskName) => {
    // Remove colon and format disk name
    const formattedDisk = diskName.replace(':', '');
    setNewSensor({
      ...newSensor,
      disk_name: diskName,
      name: `disk_${formattedDisk}_`
    });
  };

  const handleOpenAddSensorModal = () => {
    setShowAddSensorModal(true);
    loadAvailableServices();
    loadAvailableDisks();
  };

  const handleEditSensor = (sensor) => {
    setEditingSensor({
      id: sensor.id,
      name: sensor.name,
      sensor_type: sensor.sensor_type,
      threshold_warning: sensor.threshold_warning || 80,
      threshold_critical: sensor.threshold_critical || 95,
      display_name: sensor.name // For renaming
    });
    setShowEditSensorModal(true);
  };

  const handleViewSensorDetails = async (sensor, e) => {
    e.stopPropagation();
    setSelectedSensorDetails(sensor);
    setShowSensorDetailsModal(true);
    setLoadingAnalysis(true);
    setAiAnalysis(null);
    setSensorNotes([]);
    setNewNote({ note: '', status: 'pending' });

    try {
      // Load AI analysis
      const analysisResponse = await api.get(`/ai-analysis/sensor/${sensor.id}`);
      setAiAnalysis(analysisResponse.data.ai_analysis);

      // Load sensor notes
      const notesResponse = await api.get(`/sensor-notes/sensor/${sensor.id}`);
      setSensorNotes(notesResponse.data);
    } catch (error) {
      console.error('Erro ao carregar detalhes do sensor:', error);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const handleAddNote = async () => {
    if (!newNote.note.trim()) {
      alert('Digite uma nota antes de salvar');
      return;
    }

    try {
      await api.post('/sensor-notes/', {
        sensor_id: selectedSensorDetails.id,
        note: newNote.note,
        status: newNote.status
      });

      // Reload notes
      const notesResponse = await api.get(`/sensor-notes/sensor/${selectedSensorDetails.id}`);
      setSensorNotes(notesResponse.data);
      setNewNote({ note: '', status: 'pending' });
      alert('Nota adicionada com sucesso!');
    } catch (error) {
      console.error('Erro ao adicionar nota:', error);
      alert('Erro ao adicionar nota: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleUpdateSensor = async () => {
    if (!editingSensor) return;

    try {
      await api.put(`/sensors/${editingSensor.id}`, {
        name: editingSensor.display_name,
        threshold_warning: parseFloat(editingSensor.threshold_warning),
        threshold_critical: parseFloat(editingSensor.threshold_critical)
      });

      setShowEditSensorModal(false);
      setEditingSensor(null);
      loadSensors(selectedServer.id);
      alert('Sensor atualizado com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar sensor:', error);
      alert('Erro ao atualizar sensor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleEditServer = (server, e) => {
    e.stopPropagation();
    setEditingServer({
      id: server.id,
      hostname: server.hostname,
      group_name: server.group_name || '',
      tags: server.tags || []
    });
    setShowEditServerModal(true);
  };

  const handleUpdateServer = async () => {
    if (!editingServer) return;

    try {
      await api.put(`/servers/${editingServer.id}`, {
        group_name: editingServer.group_name,
        tags: editingServer.tags
      });

      setShowEditServerModal(false);
      setEditingServer(null);
      loadServers();
      alert('Servidor atualizado com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar servidor:', error);
      alert('Erro ao atualizar servidor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleOpenMoveSensorModal = (sensor, e) => {
    e.stopPropagation();
    setMovingSensor(sensor);
    setTargetCategory(sensor.sensor_type);
    setShowMoveSensorModal(true);
  };

  const handleMoveSensor = async () => {
    if (!movingSensor || !targetCategory) {
      alert('Selecione uma categoria de destino');
      return;
    }

    if (targetCategory === movingSensor.sensor_type) {
      alert('O sensor já está nesta categoria');
      return;
    }

    try {
      await api.put(`/sensors/${movingSensor.id}`, {
        sensor_type: targetCategory
      });

      setShowMoveSensorModal(false);
      setMovingSensor(null);
      setTargetCategory('');
      loadSensors(selectedServer.id);
      alert(`Sensor movido para categoria "${getCategoryName(targetCategory)}" com sucesso!`);
    } catch (error) {
      console.error('Erro ao mover sensor:', error);
      alert('Erro ao mover sensor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getCategoryName = (type) => {
    const categories = {
      'ping': 'Sistema (Ping)',
      'cpu': 'Sistema (CPU)',
      'memory': 'Sistema (Memória)',
      'disk': 'Sistema (Disco)',
      'system': 'Sistema (Uptime)',
      'network': 'Sistema (Rede)',
      'docker': 'Docker',
      'service': 'Serviços',
      'hyperv': 'Aplicações (Hyper-V)',
      'kubernetes': 'Aplicações (Kubernetes)',
      'http': 'Rede (HTTP)',
      'port': 'Rede (Porta)',
      'dns': 'Rede (DNS)',
      'ssl': 'Rede (SSL)',
      'snmp': 'Rede (SNMP)'
    };
    return categories[type] || type;
  };

  const toggleGroup = (groupName) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupName]: !prev[groupName]
    }));
  };

  const renderGroupTree = (groups, parentId = null, level = 0) => {
    const filteredGroups = groups.filter(g => g.parent_id === parentId);
    
    return filteredGroups.map(group => {
      const isSelected = selectedGroup && selectedGroup.id === group.id;
      const isExpanded = expandedGroups[`group-${group.id}`];
      
      return (
        <div key={group.id} style={{ marginLeft: `${level * 12}px` }}>
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              padding: '5px 8px',
              cursor: 'pointer',
              borderRadius: '4px',
              marginBottom: '2px',
              background: isSelected ? '#e3f2fd' : (isExpanded ? '#f9f9f9' : 'transparent'),
              border: isSelected ? '1px solid #2196f3' : '1px solid transparent',
              transition: 'all 0.15s',
              fontSize: '12px'
            }}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedGroup(group);
              toggleGroup(`group-${group.id}`);
            }}
            onMouseOver={(e) => {
              if (!isSelected) e.currentTarget.style.background = '#f5f5f5';
            }}
            onMouseOut={(e) => {
              if (!isSelected) e.currentTarget.style.background = isExpanded ? '#f9f9f9' : 'transparent';
            }}
          >
            <span style={{ marginRight: '6px', fontSize: '14px' }}>
              {isExpanded ? '📂' : '📁'}
            </span>
            <span style={{ flex: 1, fontWeight: isSelected ? 'bold' : 'normal' }}>
              {group.icon} {group.name}
            </span>
            <span style={{ 
              fontSize: '10px', 
              color: '#999', 
              marginRight: '6px', 
              background: '#f0f0f0', 
              padding: '1px 5px', 
              borderRadius: '8px' 
            }}>
              {group.sensor_count || 0}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setSelectedGroup(group);
                setShowMoveGroupModal(true);
              }}
              title="Mover"
              style={{ 
                marginRight: '3px',
                padding: '2px 6px',
                fontSize: '11px',
                background: '#ff9800',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              ⚙️
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteGroup(group.id, group.name);
              }}
              title="Excluir"
              style={{ 
                padding: '2px 6px',
                fontSize: '11px',
                background: '#f44336',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                cursor: 'pointer'
              }}
            >
              🗑️
            </button>
          </div>
          {isExpanded && renderGroupTree(groups, group.id, level + 1)}
        </div>
      );
    });
  };

  const groupServersByCompany = () => {
    const grouped = {};
    servers.forEach(server => {
      const group = server.group_name || 'Sem Grupo';
      if (!grouped[group]) {
        grouped[group] = [];
      }
      grouped[group].push(server);
    });
    
    // Adicionar pastas vazias que foram criadas (estão em expandedGroups mas não têm servidores)
    Object.keys(expandedGroups).forEach(groupName => {
      if (!grouped[groupName] && groupName.includes(' / ')) {
        // Ë uma subpasta criada manualmente
        grouped[groupName] = [];
      }
    });
    
    return grouped;
  };

  if (loading) {
    return <div className="management-container">Carregando...</div>;
  }

  return (
    <div className="management-container">
      <div className="management-header">
        <h1>Servidores Monitorados</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn-add" onClick={() => setShowAddServerModal(true)}>
            + Adicionar Servidor
          </button>
          <button 
            className="btn-add" 
            onClick={() => setShowMonitorServicesModal(true)}
            style={{ background: '#2196f3' }}
          >
            ⚙️ Monitorar Serviços
          </button>
          <button 
            className="btn-add"
            style={{ background: '#f44336' }}
            onClick={async () => {
              if (!window.confirm('Deletar todos os sensores órfãos (sem servidor associado)?')) return;
              try {
                const res = await api.delete('/sensors/orphans');
                alert(`✔ ${res.data.message}`);
                loadServers();
              } catch (err) {
                alert('Erro: ' + (err.response?.data?.detail || err.message));
              }
            }}
            title="Deletar sensores sem servidor associado"
          >
            🗑️ Limpar Órfãos
          </button>
        </div>
      </div>

      <button 
        className="sidebar-toggle-btn"
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        title={sidebarCollapsed ? "Mostrar Servidores" : "Ocultar Servidores"}
      >
        {sidebarCollapsed ? '☰' : '✓'}
      </button>

      <div className={`servers-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="servers-list">
          <div className="servers-list-header">
            <h2>Servidores ({servers.length})</h2>
            <div className="view-toggle">
              <button 
                className={viewMode === 'tree' ? 'active' : ''}
                onClick={() => setViewMode('tree')}
                title="Visualização em ürvore"
              >
                🌳
              </button>
              <button 
                className={viewMode === 'list' ? 'active' : ''}
                onClick={() => setViewMode('list')}
                title="Visualização em Lista"
              >
                📏
              </button>
            </div>
          </div>

          {/* Seção de Grupos Hierárquicos - Colapsável */}
          <div style={{ borderBottom: '1px solid #e0e0e0' }}>
            <button
              onClick={() => setShowGroupsSection(!showGroupsSection)}
              style={{
                width: '100%',
                padding: '10px 12px',
                background: showGroupsSection ? '#f5f5f5' : 'white',
                border: 'none',
                borderBottom: '1px solid #e0e0e0',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '12px',
                fontWeight: 'bold',
                color: '#666',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.background = '#f5f5f5'}
              onMouseOut={(e) => e.currentTarget.style.background = showGroupsSection ? '#f5f5f5' : 'white'}
            >
              <span>⚙️ Gerenciar Grupos {serverGroups.length > 0 && `(${serverGroups.length})`}</span>
              <span style={{ fontSize: '10px' }}>{showGroupsSection ? '▲' : '▼'}</span>
            </button>

            {showGroupsSection && (
              <div style={{ background: '#fafafa' }}>
                {/* Botões de Ação */}
                <div style={{ padding: '10px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => {
                      setNewGroup({
                        name: '',
                        parent_id: null,
                        description: '',
                        icon: '📁',
                        color: '#2196f3'
                      });
                      setShowCreateGroupModal(true);
                    }}
                    style={{
                      padding: '6px 10px',
                      background: '#4caf50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '11px',
                      fontWeight: 'bold'
                    }}
                    title="Criar grupo raiz"
                  >
                    🗂️ Grupo
                  </button>
                  {selectedGroup && (
                    <>
                      <button
                        onClick={() => {
                          setNewGroup({
                            name: '',
                            parent_id: selectedGroup.id,
                            description: '',
                            icon: '📁',
                            color: '#2196f3'
                          });
                          setShowCreateGroupModal(true);
                        }}
                        style={{
                          padding: '6px 10px',
                          background: '#2196f3',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '11px',
                          fontWeight: 'bold'
                        }}
                        title={`Criar subgrupo em "${selectedGroup.name}"`}
                      >
                        🗂️ Subgrupo
                      </button>
                      <button
                        onClick={() => setSelectedGroup(null)}
                        style={{
                          padding: '6px 10px',
                          background: '#757575',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '11px',
                          fontWeight: 'bold'
                        }}
                      >
                        ✓
                      </button>
                    </>
                  )}
                </div>

                {/* ürvore de Grupos */}
                {serverGroups.length > 0 ? (
                  <div style={{ 
                    padding: '10px',
                    maxHeight: '250px',
                    overflowY: 'auto',
                    background: 'white',
                    margin: '0 10px 10px 10px',
                    borderRadius: '4px',
                    border: '1px solid #e0e0e0'
                  }}>
                    {selectedGroup && (
                      <div style={{ 
                        marginBottom: '8px', 
                        padding: '6px 8px', 
                        background: '#e3f2fd', 
                        borderRadius: '4px',
                        fontSize: '11px',
                        border: '1px solid #2196f3'
                      }}>
                        <strong>Selecionado:</strong> {selectedGroup.icon} {selectedGroup.name}
                      </div>
                    )}
                    {renderGroupTree(serverGroups)}
                  </div>
                ) : (
                  <div style={{ 
                    padding: '15px',
                    textAlign: 'center',
                    color: '#999',
                    fontSize: '11px',
                    margin: '0 10px 10px 10px'
                  }}>
                    Nenhum grupo criado
                  </div>
                )}
              </div>
            )}
          </div>

          {viewMode === 'tree' ? (
            <div className="tree-view">
              {Object.entries(groupServersByCompany()).map(([groupName, groupServers]) => (
                <div key={groupName} className="tree-group">
                  <div 
                    className="tree-group-header"
                    onClick={() => toggleGroup(groupName)}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                      <span className="tree-icon">
                        {expandedGroups[groupName] ? '📂' : '📁'}
                      </span>
                      <span className="tree-label">{groupName}</span>
                      <span className="tree-count">({groupServers.length})</span>
                    </div>
                    <div style={{ display: 'flex', gap: '4px', marginLeft: '8px' }} onClick={(e) => e.stopPropagation()}>
                      <button
                        className="btn-edit-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          setReorderingGroup(reorderingGroup === groupName ? null : groupName);
                        }}
                        title="Reordenar servidores"
                        style={{ padding: '2px 6px', fontSize: '11px', background: '#9c27b0', color: 'white' }}
                      >
                        ⇅
                      </button>
                      <button
                        className="btn-edit-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          const newName = prompt(`Renomear pasta "${groupName}":`, groupName);
                          if (newName && newName !== groupName) {
                            // Atualizar todos os servidores deste grupo
                            Promise.all(
                              groupServers.map(server => 
                                api.put(`/servers/${server.id}`, { group_name: newName })
                              )
                            ).then(() => {
                              loadServers();
                              alert('Pasta renomeada com sucesso!');
                            }).catch(err => {
                              console.error('Erro ao renomear pasta:', err);
                              alert('Erro ao renomear pasta');
                            });
                          }
                        }}
                        title="Renomear pasta"
                        style={{ padding: '2px 6px', fontSize: '11px' }}
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-edit-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          const subfolderName = prompt(`Criar subpasta dentro de "${groupName}":`);
                          if (subfolderName) {
                            // Criar nome hierárquico: "Pai / Filho"
                            const newGroupName = `${groupName} / ${subfolderName}`;
                            
                            // Perguntar se quer mover um servidor existente ou criar novo
                            const action = window.confirm(
                              `Subpasta "${newGroupName}" será criada.\n\n` +
                              `Clique OK para mover um servidor existente para esta pasta.\n` +
                              `Clique CANCELAR para criar a pasta vazia (você poderá adicionar servidores depois).`
                            );
                            
                            if (action) {
                              // Mover servidor existente
                              const serverToMove = groupServers[0]; // Pega o primeiro servidor
                              if (serverToMove) {
                                api.put(`/servers/${serverToMove.id}`, { 
                                  group_name: newGroupName 
                                }).then(() => {
                                  loadServers();
                                  // Expandir a nova pasta
                                  setTimeout(() => {
                                    setExpandedGroups(prev => ({
                                      ...prev,
                                      [newGroupName]: true
                                    }));
                                  }, 100);
                                  alert(`Subpasta criada e servidor "${serverToMove.hostname}" movido!`);
                                }).catch(err => {
                                  console.error('Erro ao criar subpasta:', err);
                                  alert('Erro ao criar subpasta');
                                });
                              }
                            } else {
                              // Criar pasta vazia - adiciona ao estado para aparecer
                              setExpandedGroups(prev => ({
                                ...prev,
                                [newGroupName]: true
                              }));
                              alert(
                                `Subpasta "${subfolderName}" criada!\n\n` +
                                `Para adicionar servidores:\n` +
                                `1. Clique em ✅ em um servidor\n` +
                                `2. No campo "Grupo / Empresa", digite: ${newGroupName}\n` +
                                `3. Salve`
                              );
                            }
                          }
                        }}
                        title="Criar subpasta"
                        style={{ padding: '2px 6px', fontSize: '11px', background: '#4caf50', color: 'white' }}
                      >
                        🗂️
                      </button>
                      <button
                        className="btn-delete-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (window.confirm(`Excluir pasta "${groupName}"?\n\nOs ${groupServers.length} servidor(es) ficarão sem pasta.`)) {
                            Promise.all(
                              groupServers.map(server => 
                                api.put(`/servers/${server.id}`, { group_name: null })
                              )
                            ).then(() => {
                              loadServers();
                              alert('Pasta excluída com sucesso!');
                            }).catch(err => {
                              console.error('Erro ao excluir pasta:', err);
                              alert('Erro ao excluir pasta');
                            });
                          }
                        }}
                        title="Excluir pasta"
                        style={{ padding: '2px 6px', fontSize: '11px' }}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  {expandedGroups[groupName] && (
                    <div className="tree-group-content">
                      {reorderingGroup === groupName && (
                        <div style={{ padding: '8px 12px', background: '#f3e5f5', borderBottom: '1px solid #ce93d8', fontSize: '12px' }}>
                          <div style={{ fontWeight: 'bold', marginBottom: '6px', color: '#7b1fa2' }}>⇅ Reordenar servidores:</div>
                          {groupServers.map((server, idx) => (
                            <div key={server.id} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', background: 'white', padding: '4px 8px', borderRadius: '4px', border: '1px solid #e1bee7' }}>
                              <span style={{ flex: 1, fontSize: '12px', fontWeight: '500' }}>{server.hostname}</span>
                              <button
                                onClick={() => handleReorderServer(server, groupServers, -1)}
                                disabled={idx === 0}
                                style={{ padding: '1px 6px', fontSize: '11px', cursor: idx === 0 ? 'not-allowed' : 'pointer', opacity: idx === 0 ? 0.4 : 1 }}
                              >▲</button>
                              <button
                                onClick={() => handleReorderServer(server, groupServers, 1)}
                                disabled={idx === groupServers.length - 1}
                                style={{ padding: '1px 6px', fontSize: '11px', cursor: idx === groupServers.length - 1 ? 'not-allowed' : 'pointer', opacity: idx === groupServers.length - 1 ? 0.4 : 1 }}
                              >▼</button>
                            </div>
                          ))}
                          <button onClick={() => setReorderingGroup(null)} style={{ marginTop: '6px', padding: '3px 10px', fontSize: '11px', background: '#7b1fa2', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Fechar</button>
                        </div>
                      )}
                      {groupServers.length > 0 ? (
                        groupServers.map(server => (
                          <div
                            key={server.id}
                            className={`tree-server ${selectedServer?.id === server.id ? 'selected' : ''}`}
                            onClick={() => setSelectedServer(server)}
                          >
                            <div className="server-info">
                              <h3>{server.hostname}</h3>
                              <p>{server.ip_address || 'IP não disponível'}</p>
                              {server.public_ip && <p className="public-ip">🌐 {server.public_ip}</p>}
                              {server.tags && server.tags.length > 0 && (
                                <div className="server-tags">
                                  {server.tags.map((tag, idx) => (
                                    <span key={idx} className="tag">{tag}</span>
                                  ))}
                                </div>
                              )}
                            </div>
                            <div className="server-actions">
                              <button 
                                className="btn-edit-small"
                                onClick={(e) => handleEditServer(server, e)}
                                title="Editar servidor"
                              >
                                ✏️
                              </button>
                              <button 
                                className="btn-delete-small"
                                onClick={(e) => handleDeleteServer(server.id, server.hostname, e)}
                                title="Excluir servidor"
                              >
                                🗑️
                              </button>
                              <div className={`server-status ${server.is_active ? 'active' : 'inactive'}`}>
                              {server.is_active ? '●' : '○'}
                            </div>
                          </div>
                        </div>
                      ))
                      ) : (
                        <div style={{ 
                          padding: '15px', 
                          textAlign: 'center', 
                          color: '#999', 
                          fontSize: '12px',
                          fontStyle: 'italic'
                        }}>
                          📂 Pasta vazia
                          <div style={{ fontSize: '11px', marginTop: '5px' }}>
                            Edite um servidor e defina o grupo como: {groupName}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="list-view">
              {servers.map(server => (
                <div
                  key={server.id}
                  className={`server-card ${selectedServer?.id === server.id ? 'selected' : ''}`}
                  onClick={() => setSelectedServer(server)}
                >
                  <div className="server-info">
                    <h3>{server.hostname}</h3>
                    <p>{server.ip_address || 'IP não disponível'}</p>
                    {server.public_ip && <p className="public-ip">🌐 {server.public_ip}</p>}
                    <p className="server-os">{server.os_type} {server.os_version}</p>
                    {server.group_name && <p className="server-group">📁 {server.group_name}</p>}
                  </div>
                  <div className="server-actions">
                    <button 
                      className="btn-edit-small"
                      onClick={(e) => handleEditServer(server, e)}
                      title="Editar servidor"
                    >
                      ✏️
                    </button>
                    <button 
                      className="btn-delete-small"
                      onClick={(e) => handleDeleteServer(server.id, server.hostname, e)}
                      title="Excluir servidor"
                    >
                      🗑️
                    </button>
                    <div className={`server-status ${server.is_active ? 'active' : 'inactive'}`}>
                      {server.is_active ? '●' : '○'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="server-details">
          {selectedServer ? (
            <>
              <div className="server-details-header">
                <h2>Sensores de {selectedServer.hostname}</h2>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button 
                    className="btn-add" 
                    onClick={async () => {
                      if (window.confirm('Deseja corrigir automaticamente as categorias de todos os sensores baseado no nome?\n\nExemplo: Sensores com "Docker" no nome serão movidos para categoria Docker.')) {
                        try {
                          const response = await api.post('/sensors/fix-categories');
                          alert(`✔ Correção concluída!\n\nTotal: ${response.data.total_sensors} sensores\nCorrigidos: ${response.data.fixed_count} sensores\n\nRecarregando...`);
                          loadSensors(selectedServer.id);
                        } catch (error) {
                          console.error('Erro ao corrigir categorias:', error);
                          alert('Erro ao corrigir categorias: ' + (error.response?.data?.detail || error.message));
                        }
                      }
                    }}
                    style={{ background: '#ff9800' }}
                  >
                    🔧 Corrigir Categorias
                  </button>
                  <button className="btn-add" onClick={handleOpenAddSensorModal}>
                    + Adicionar Sensor
                  </button>
                </div>
              </div>
              <div className="info-banner">
                <p>ℹ️ <strong>Sensores Padrão:</strong> Ping, CPU, Memória, Disco, Uptime, Network IN, Network OUT</p>
                <p>Os sensores padrão são criados automaticamente. Use "Adicionar Sensor" para monitorar serviços Windows, discos adicionais ou criar sensores customizados.</p>
              </div>
              {renderMixedSensors()}
              {sensors.length === 0 && (
                <div className="no-data">
                  <p>Nenhum sensor configurado para este servidor</p>
                  <p>Os sensores padrão são criados automaticamente. Clique em "Adicionar Sensor" para monitorar serviços ou discos adicionais.</p>
                </div>
              )}
            </>
          ) : (
            <div className="no-selection">
              <p>Selecione um servidor para ver os sensores</p>
            </div>
          )}
        </div>
      </div>

      {showAddServerModal && (
        <div className="modal-overlay" onClick={() => setShowAddServerModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <h2>Adicionar Novo Servidor / Dispositivo</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label>Probe Responsável: *</label>
                <select 
                  value={newServer.probe_id}
                  onChange={(e) => setNewServer({...newServer, probe_id: e.target.value})}
                  required
                >
                  <option value="">-- Selecione uma probe --</option>
                  {probes.map(probe => (
                    <option key={probe.id} value={probe.id}>
                      {probe.name}
                    </option>
                  ))}
                </select>
                <small>A probe que irá monitorar este dispositivo</small>
              </div>

              <div className="form-group">
                <label>Tipo de Dispositivo: *</label>
                <select
                  value={newServer.device_type}
                  onChange={(e) => setNewServer({...newServer, device_type: e.target.value})}
                >
                  <option value="server">🖥️ Servidor</option>
                  <option value="switch">🔀 Switch</option>
                  <option value="router">📡 Roteador</option>
                  <option value="firewall">🔥 Firewall</option>
                  <option value="printer">🖨️ Impressora</option>
                  <option value="storage">🧠 Storage</option>
                  <option value="ups">🔋 Nobreak</option>
                  <option value="other">📪 Outro</option>
                </select>
                <small>Tipo do dispositivo a ser monitorado</small>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Nome do Dispositivo / Hostname: *</label>
                <input
                  type="text"
                  value={newServer.hostname}
                  onChange={(e) => setNewServer({...newServer, hostname: e.target.value})}
                  required
                  placeholder="Ex: SERVER-01, SWITCH-CORE, RTR-01"
                />
                <small>Nome ou hostname do dispositivo na rede</small>
              </div>

              <div className="form-group">
                <label>Endereço IP: *</label>
                <input
                  type="text"
                  value={newServer.ip_address}
                  onChange={(e) => setNewServer({...newServer, ip_address: e.target.value})}
                  required
                  placeholder="Ex: 192.168.1.100"
                />
                <small>Endereço IP do dispositivo na rede local</small>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Grupo / Empresa:</label>
                <select
                  value={newServer.group_name || ''}
                  onChange={(e) => setNewServer({...newServer, group_name: e.target.value, newGroupInput: ''})}
                >
                  <option value="">Sem grupo</option>
                  {Array.from(new Set(servers.map(s => s.group_name).filter(g => g))).sort().map(group => (
                    <option key={group} value={group}>{group}</option>
                  ))}
                </select>
                <small>Selecione um grupo existente ou deixe sem grupo</small>
              </div>

              <div className="form-group">
                <label>Ou criar novo grupo:</label>
                <input
                  type="text"
                  placeholder="Ex: Empresa A, Datacenter SP, Produção"
                  value={newServer.newGroupInput || ''}
                  onChange={(e) => setNewServer({...newServer, newGroupInput: e.target.value, group_name: e.target.value})}
                />
                <small>Digite um novo nome de grupo para criar</small>
              </div>
            </div>

            <div className="form-section">
              <h3>⚙️ Protocolo de Monitoramento</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>Protocolo: *</label>
                  <select
                    value={newServer.monitoring_protocol}
                    onChange={(e) => setNewServer({...newServer, monitoring_protocol: e.target.value})}
                  >
                    <option value="wmi">WMI (Windows Management Instrumentation)</option>
                    <option value="snmp">SNMP (Simple Network Management Protocol)</option>
                  </select>
                  <small>WMI para Windows, SNMP para dispositivos de rede</small>
                </div>
              </div>

              {newServer.monitoring_protocol === 'snmp' && (
                <div className="form-row">
                  <div className="form-group">
                    <label>Versão SNMP:</label>
                    <select
                      value={newServer.snmp_version}
                      onChange={(e) => setNewServer({...newServer, snmp_version: e.target.value})}
                    >
                      <option value="v1">SNMP v1</option>
                      <option value="v2c">SNMP v2c (recomendado)</option>
                      <option value="v3">SNMP v3 (mais seguro)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Community String:</label>
                    <input
                      type="text"
                      value={newServer.snmp_community}
                      onChange={(e) => setNewServer({...newServer, snmp_community: e.target.value})}
                      placeholder="Ex: public, private"
                    />
                    <small>Community string configurada no dispositivo</small>
                  </div>

                  <div className="form-group">
                    <label>Porta SNMP:</label>
                    <input
                      type="number"
                      value={newServer.snmp_port}
                      onChange={(e) => setNewServer({...newServer, snmp_port: e.target.value})}
                      placeholder="161"
                    />
                    <small>Porta padrão: 161</small>
                  </div>
                </div>
              )}
            </div>

            <div className="form-section">
              <h3>🏷️ Classificação de Ambiente</h3>
              <div className="form-group">
                <label>Ambiente: *</label>
                <select
                  value={newServer.environment}
                  onChange={(e) => setNewServer({...newServer, environment: e.target.value})}
                >
                  <option value="production">🔴 Produção (24x7 - Ligações em caso de queda)</option>
                  <option value="staging">🧪 Homologação (Horário comercial 08-18h)</option>
                  <option value="development">💻 Desenvolvimento (Horário comercial 08-18h)</option>
                  <option value="custom">⚙️ Personalizado (Definir horários)</option>
                </select>
                <small>Define quando o sistema enviará notificações e ligações</small>
              </div>

              {newServer.environment === 'custom' && (
                <div className="custom-schedule-info">
                  <p>ℹ️ <strong>Horário Personalizado:</strong></p>
                  <p>Você poderá configurar horários específicos após criar o servidor.</p>
                </div>
              )}
            </div>

            <div className="info-box">
              <p>ℹ️ <strong>Importante:</strong></p>
              <ul>
                <li>O dispositivo deve estar acessível pela probe selecionada</li>
                <li><strong>WMI:</strong> Certifique-se que o firewall permite conexões WMI/RPC</li>
                <li><strong>SNMP:</strong> Verifique se o SNMP está habilitado no dispositivo</li>
                <li><strong>Produção:</strong> Sistema ligará 24x7 em caso de problemas críticos</li>
                <li><strong>Homologação/Dev:</strong> Notificações apenas em horário comercial</li>
              </ul>
            </div>

            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowAddServerModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleAddServer}>
                Adicionar Dispositivo
              </button>
            </div>
          </div>
        </div>
      )}
      <AddSensorModal
        show={showAddSensorModal}
        onClose={() => setShowAddSensorModal(false)}
        onAdd={handleAddSensor}
        server={selectedServer}
        availableServices={availableServices}
        availableDisks={availableDisks}
        loadingServices={loadingServices}
        loadingDisks={loadingDisks}
      />

      {showEditServerModal && editingServer && (
        <div className="modal-overlay" onClick={() => setShowEditServerModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Editar Servidor: {editingServer.hostname}</h2>
            <div className="form-group">
              <label>Grupo / Empresa:</label>
              <select
                value={editingServer.group_name || ''}
                onChange={(e) => setEditingServer({...editingServer, group_name: e.target.value})}
              >
                <option value="">Sem grupo</option>
                {Array.from(new Set(servers.map(s => s.group_name).filter(g => g))).sort().map(group => (
                  <option key={group} value={group}>{group}</option>
                ))}
              </select>
              <small>Selecione um grupo existente ou deixe sem grupo</small>
            </div>
            <div className="form-group">
              <label>Ou criar novo grupo:</label>
              <input
                type="text"
                placeholder="Ex: Empresa A, Datacenter SP, Produção"
                value=""
                onChange={(e) => {
                  if (e.target.value.trim()) {
                    setEditingServer({...editingServer, group_name: e.target.value});
                  }
                }}
              />
              <small>Digite um novo nome de grupo para criar</small>
            </div>
            <div className="form-group">
              <label>Tags (separadas por vírgula):</label>
              <input
                type="text"
                placeholder="Ex: crítico, produção, web-server"
                value={editingServer.tags ? editingServer.tags.join(', ') : ''}
                onChange={(e) => setEditingServer({
                  ...editingServer, 
                  tags: e.target.value.split(',').map(t => t.trim()).filter(t => t)
                })}
              />
              <small>Use tags para classificar por criticidade, função, etc</small>
            </div>
            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowEditServerModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleUpdateServer}>
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}

      {showEditSensorModal && editingSensor && (
        <div className="modal-overlay" onClick={() => setShowEditSensorModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Editar Sensor</h2>
            <div className="form-group">
              <label>Nome do Sensor:</label>
              <input
                type="text"
                value={editingSensor.display_name}
                onChange={(e) => setEditingSensor({...editingSensor, display_name: e.target.value})}
                placeholder="Ex: Ping Google, CPU Principal, Disco C:"
              />
              <small>Personalize o nome do sensor para facilitar identificação</small>
            </div>
            <div className="form-group">
              <label>Tipo:</label>
              <input type="text" value={editingSensor.sensor_type} disabled />
            </div>
            <div className="form-group">
              <label>
                Limite de Aviso 
                {editingSensor.sensor_type === 'ping' ? ' (ms)' : 
                 editingSensor.sensor_type === 'network' ? ' (MB/s)' : ' (%)'}:
              </label>
              <input
                type="number"
                value={editingSensor.threshold_warning}
                onChange={(e) => setEditingSensor({...editingSensor, threshold_warning: e.target.value})}
              />
              <small>
                {editingSensor.sensor_type === 'ping' ? 'Alerta amarelo quando latência ultrapassar este valor' :
                 editingSensor.sensor_type === 'network' ? 'Alerta amarelo quando tráfego ultrapassar este valor' :
                 'Alerta amarelo quando ultrapassar este valor'}
              </small>
            </div>
            <div className="form-group">
              <label>
                Limite Crítico 
                {editingSensor.sensor_type === 'ping' ? ' (ms)' : 
                 editingSensor.sensor_type === 'network' ? ' (MB/s)' : ' (%)'}:
              </label>
              <input
                type="number"
                value={editingSensor.threshold_critical}
                onChange={(e) => setEditingSensor({...editingSensor, threshold_critical: e.target.value})}
              />
              <small>
                {editingSensor.sensor_type === 'ping' ? 'Alerta vermelho quando latência ultrapassar este valor' :
                 editingSensor.sensor_type === 'network' ? 'Alerta vermelho quando tráfego ultrapassar este valor' :
                 'Alerta vermelho quando ultrapassar este valor'}
              </small>
            </div>
            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowEditSensorModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleUpdateSensor}>
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}

      {showMoveSensorModal && movingSensor && (
        <div className="modal-overlay" onClick={() => setShowMoveSensorModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>📁 Mover Sensor para Outra Categoria</h2>
            <div className="info-banner" style={{ marginBottom: '20px', background: '#fff3cd', padding: '15px', borderRadius: '8px', border: '1px solid #ffc107' }}>
              <p><strong>Sensor:</strong> {movingSensor.name}</p>
              <p><strong>Categoria Atual:</strong> {getCategoryName(movingSensor.sensor_type)}</p>
            </div>
            <div className="form-group">
              <label>Selecione a Nova Categoria:</label>
              <select 
                value={targetCategory} 
                onChange={(e) => setTargetCategory(e.target.value)}
                style={{ width: '100%', padding: '10px', fontSize: '14px', borderRadius: '6px', border: '1px solid #ddd' }}
              >
                <optgroup label="Sistema">
                  <option value="ping">📡 Ping</option>
                  <option value="cpu">🖥️ CPU</option>
                  <option value="memory">🧠 Memória</option>
                  <option value="disk">💾 Disco</option>
                  <option value="system">⏱️ Uptime</option>
                  <option value="network">🌐 Rede</option>
                </optgroup>
                <optgroup label="Docker">
                  <option value="docker">🐳 Docker</option>
                </optgroup>
                <optgroup label="Serviços">
                  <option value="service">⚙️ Serviço Windows</option>
                </optgroup>
                <optgroup label="Aplicações">
                  <option value="hyperv">🖼️ Hyper-V</option>
                  <option value="kubernetes">☸️ Kubernetes</option>
                </optgroup>
                <optgroup label="Rede">
                  <option value="http">🌐 HTTP</option>
                  <option value="port">🔎 Porta</option>
                  <option value="dns">🔬 DNS</option>
                  <option value="ssl">🔒 SSL</option>
                  <option value="snmp">📊 SNMP</option>
                </optgroup>
              </select>
              <small>O sensor será movido para a categoria selecionada e aparecerá no card correspondente</small>
            </div>
            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowMoveSensorModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleMoveSensor}>
                Mover Sensor
              </button>
            </div>
          </div>
        </div>
      )}

      {showSensorDetailsModal && selectedSensorDetails && (
        <div className="modal-overlay" onClick={() => setShowSensorDetailsModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🔬 Detalhes do Sensor: {selectedSensorDetails.name}</h2>
              <button className="btn-close" onClick={() => setShowSensorDetailsModal(false)}>×</button>
            </div>

            <div className="sensor-details-content">
              {/* AI Analysis Section */}
              <div className="ai-analysis-section">
                <h3>🤖 Análise da IA</h3>
                {loadingAnalysis ? (
                  <div className="loading-analysis">Analisando sensor...</div>
                ) : aiAnalysis ? (
                  <div className="ai-analysis-content">
                    <div className="root-cause">
                      <h4>Causa Raiz:</h4>
                      <p>{aiAnalysis.root_cause}</p>
                      <div className="confidence-badge">
                        Confiança: {(aiAnalysis.confidence * 100).toFixed(0)}%
                      </div>
                    </div>

                    <div className="evidence">
                      <h4>Evidências:</h4>
                      <ul>
                        {aiAnalysis.evidence.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="suggested-actions">
                      <h4>💡 Ações Sugeridas:</h4>
                      {aiAnalysis.suggested_actions.map((action, idx) => (
                        <div key={idx} className={`action-card priority-${action.priority}`}>
                          <div className="action-header">
                            <span className="priority-badge">{action.priority.toUpperCase()}</span>
                            <span className="action-title">{action.action}</span>
                          </div>
                          {action.command && (
                            <div className="action-command">
                              <code>{action.command}</code>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    <div className="remediation-info">
                      <div className="info-item">
                        <strong>Auto-remediação disponível:</strong> 
                        {aiAnalysis.auto_remediation_available ? ' ✔ Sim' : ' ✖ Não'}
                      </div>
                      <div className="info-item">
                        <strong>Tempo estimado de resolução:</strong> {aiAnalysis.estimated_resolution_time}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="no-analysis">Análise não disponível</div>
                )}
              </div>

              {/* Technician Notes Section */}
              <div className="technician-notes-section">
                <h3>📥 Notas do Técnico</h3>
                
                <div className="add-note-form">
                  <div className="form-group">
                    <label>Status de Verificação:</label>
                    <select 
                      value={newNote.status}
                      onChange={(e) => setNewNote({...newNote, status: e.target.value})}
                    >
                      <option value="pending">⏳ Pendente</option>
                      <option value="in_analysis">🔬 Em Análise</option>
                      <option value="verified">✔ Verificado</option>
                      <option value="resolved">✅ Resolvido</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Nota:</label>
                    <textarea
                      value={newNote.note}
                      onChange={(e) => setNewNote({...newNote, note: e.target.value})}
                      placeholder="Descreva as ações tomadas, observações ou próximos passos..."
                      rows="4"
                    />
                  </div>
                  <button className="btn-primary" onClick={handleAddNote}>
                    Adicionar Nota
                  </button>
                </div>

                <div className="notes-history">
                  <h4>Histórico de Notas:</h4>
                  {sensorNotes.length > 0 ? (
                    <div className="notes-list">
                      {sensorNotes.map(note => (
                        <div key={note.id} className="note-card">
                          <div className="note-header">
                            <span className="note-author">{note.user_name || 'Usuário'}</span>
                            <span className="note-date">
                              {new Date(note.created_at).toLocaleString('pt-BR')}
                            </span>
                          </div>
                          <div className="note-status">
                            Status: {
                              note.status === 'pending' ? '⏳ Pendente' :
                              note.status === 'in_analysis' ? '🔬 Em Análise' :
                              note.status === 'verified' ? '✔ Verificado' :
                              '✅ Resolvido'
                            }
                          </div>
                          <div className="note-content">{note.note}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="no-notes">Nenhuma nota registrada ainda</div>
                  )}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowSensorDetailsModal(false)}>
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Criar Grupo */}
      {showCreateGroupModal && (
        <div className="modal-overlay" onClick={() => setShowCreateGroupModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{newGroup.parent_id ? '🗂️ Criar Subgrupo' : '🗂️ Criar Grupo Raiz'}</h2>
              <button className="modal-close" onClick={() => setShowCreateGroupModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Nome do Grupo: *</label>
                <input
                  type="text"
                  value={newGroup.name}
                  onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                  placeholder="Ex: Produção, Datacenter SP, Clientes"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Descrição:</label>
                <textarea
                  value={newGroup.description}
                  onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
                  placeholder="Descrição opcional do grupo"
                  rows="3"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Ícone:</label>
                  <select
                    value={newGroup.icon}
                    onChange={(e) => setNewGroup({...newGroup, icon: e.target.value})}
                  >
                    <option value="📁">📁 Pasta</option>
                    <option value="🏢">🏢 Empresa</option>
                    <option value="🏭">🏭 Fábrica</option>
                    <option value="🏪">🏪 Loja</option>
                    <option value="🏥">🏥 Hospital</option>
                    <option value="🏫">🏫 Escola</option>
                    <option value="🌐">🌐 Rede</option>
                    <option value="☁️">☁️ Nuvem</option>
                    <option value="🖥️">🖥️ Servidores</option>
                    <option value="📊">📊 Monitoramento</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Cor:</label>
                  <input
                    type="color"
                    value={newGroup.color}
                    onChange={(e) => setNewGroup({...newGroup, color: e.target.value})}
                  />
                </div>
              </div>

              {newGroup.parent_id && (
                <div className="info-banner">
                  <p>ℹ️ Este será um subgrupo dentro de: <strong>{serverGroups.find(g => g.id === newGroup.parent_id)?.name}</strong></p>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn-cancel" onClick={() => setShowCreateGroupModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleCreateGroup}>
                Criar Grupo
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Mover Grupo */}
      {showMoveGroupModal && selectedGroup && (
        <div className="modal-overlay" onClick={() => setShowMoveGroupModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>⚙️ Mover Grupo</h2>
              <button className="modal-close" onClick={() => setShowMoveGroupModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="info-banner" style={{ marginBottom: '20px' }}>
                <p><strong>Grupo:</strong> {selectedGroup.icon} {selectedGroup.name}</p>
                <p><strong>Posição Atual:</strong> {selectedGroup.parent_id ? 'Subgrupo' : 'Raiz'}</p>
              </div>

              <div className="form-group">
                <label>Mover para:</label>
                <select
                  value={newGroup.parent_id || ''}
                  onChange={(e) => setNewGroup({...newGroup, parent_id: e.target.value ? parseInt(e.target.value) : null})}
                >
                  <option value="">📁 Raiz (sem pai)</option>
                  {serverGroups
                    .filter(g => g.id !== selectedGroup.id) // Não pode mover para si mesmo
                    .map(group => (
                      <option key={group.id} value={group.id}>
                        {'  '.repeat(group.level || 0)}{group.icon} {group.name}
                      </option>
                    ))}
                </select>
                <small>Selecione o grupo pai ou deixe em branco para mover para a raiz</small>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-cancel" onClick={() => setShowMoveGroupModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleMoveGroup}>
                Mover Grupo
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Monitorar Serviços */}
      {showMonitorServicesModal && (
        <div className="modal-overlay" onClick={() => setShowMonitorServicesModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '900px', maxHeight: '90vh', overflow: 'auto' }}>
            <div className="modal-header">
              <h2>⚙️ Monitorar Serviços e Dispositivos</h2>
              <button className="modal-close" onClick={() => setShowMonitorServicesModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <p style={{ marginBottom: '20px', color: '#666', fontSize: '15px' }}>
                Escolha o tipo de dispositivo ou serviço que deseja monitorar. Todos abrem na Biblioteca de Sensores Independentes.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '15px' }}>
                {/* SNMP Genérico */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setCurrentWizardType('snmp');
                    setShowSNMPWizard(true);
                    setSNMPWizardStep(1);
                    setSNMPConfig({...snmpConfig, device_type: 'generic'});
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>📡</div>
                  <div>SNMP Genérico</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Switches, Roteadores, Impressoras
                  </div>
                </button>

                {/* Access Point */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setCurrentWizardType('ap');
                    setShowSNMPWizard(true);
                    setSNMPWizardStep(1);
                    setSNMPConfig({...snmpConfig, device_type: 'ap'});
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>📡</div>
                  <div>Access Point WiFi</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Monitore APs via SNMP
                  </div>
                </button>

                {/* Azure */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setShowAzureWizard(true);
                    setAzureWizardStep(1);
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #0078d4 0%, #00bcf2 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>☁️</div>
                  <div>Microsoft Azure</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    VMs, Storage, Databases
                  </div>
                </button>

                {/* Temperatura */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setCurrentWizardType('temp');
                    setShowSNMPWizard(true);
                    setSNMPWizardStep(1);
                    setSNMPConfig({...snmpConfig, device_type: 'temp'});
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🌡️</div>
                  <div>Temperatura</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Sensores de temperatura SNMP
                  </div>
                </button>

                {/* HTTP/HTTPS */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setShowHTTPWizard(true);
                    setHTTPWizardStep(1);
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🌐</div>
                  <div>HTTP/HTTPS</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Websites, APIs, Endpoints
                  </div>
                </button>

                {/* Storage */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setCurrentWizardType('storage');
                    setShowSNMPWizard(true);
                    setSNMPWizardStep(1);
                    setSNMPConfig({...snmpConfig, device_type: 'storage'});
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
                    color: '#333',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🧠</div>
                  <div>Storage/NAS</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Armazenamento em rede
                  </div>
                </button>

                {/* Banco de Dados */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    window.location.hash = '#/sensor-library?type=database';
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                    color: '#333',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🗄️</div>
                  <div>Banco de Dados</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    MySQL, PostgreSQL, SQL Server
                  </div>
                </button>

                {/* Impressora */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setCurrentWizardType('printer');
                    setShowSNMPWizard(true);
                    setSNMPWizardStep(1);
                    setSNMPConfig({...snmpConfig, device_type: 'printer'});
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
                    color: '#333',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🖨️</div>
                  <div>Impressora</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Status, toner, papel via SNMP
                  </div>
                </button>

                {/* UPS/Nobreak */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setCurrentWizardType('ups');
                    setShowSNMPWizard(true);
                    setSNMPWizardStep(1);
                    setSNMPConfig({...snmpConfig, device_type: 'ups'});
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)',
                    color: '#333',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🔋</div>
                  <div>UPS/Nobreak</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Bateria, carga, autonomia
                  </div>
                </button>

                {/* Kubernetes */}
                <button
                  onClick={() => {
                    setShowMonitorServicesModal(false);
                    setShowK8sWizard(true);
                    setK8sWizardStep(1);
                  }}
                  style={{
                    padding: '18px',
                    background: 'linear-gradient(135deg, #326ce5 0%, #5a9fd4 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '15px',
                    fontWeight: 'bold',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                  }}
                >
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>☸️</div>
                  <div>Kubernetes</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Clusters, Pods, Deployments
                  </div>
                </button>
              </div>

              <div className="info-banner" style={{ marginTop: '20px' }}>
                <p>💡 <strong>Dica:</strong> Todos os tipos abrem na Biblioteca de Sensores Independentes com o tipo pré-selecionado para facilitar a configuração.</p>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowMonitorServicesModal(false)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Wizard Azure - Passo a Passo Completo */}
      {showAzureWizard && (
        <div className="modal-overlay" onClick={() => setShowAzureWizard(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px' }}>
            <div className="modal-header">
              <h2>☁️ Configurar Monitoramento Azure - Passo {azureWizardStep} de 4</h2>
              <button className="modal-close" onClick={() => setShowAzureWizard(false)}>×</button>
            </div>

            <div className="modal-body">
              {/* Passo 1: Requisitos e Instruções */}
              {azureWizardStep === 1 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#0078d4' }}>📏 Requisitos para Monitoramento Azure</h3>
                  
                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      <strong>ℹ️ Baseado nas melhores práticas do PRTG, SolarWinds e Zabbix</strong><br/>
                      Para monitorar recursos Azure, você precisa criar um Service Principal (App Registration) com permissões adequadas.
                    </p>
                  </div>

                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0, color: '#333' }}>📋 Passo a Passo - Azure Portal</h4>
                    <ol style={{ lineHeight: '1.8', fontSize: '14px', paddingLeft: '20px' }}>
                      <li>
                        <strong>Acesse o Azure Portal:</strong> <a href="https://portal.azure.com" target="_blank" rel="noopener noreferrer">portal.azure.com</a>
                      </li>
                      <li>
                        <strong>Criar App Registration:</strong>
                        <ul style={{ marginTop: '8px' }}>
                          <li>Vá em <code>Azure Active Directory</code> → <code>App registrations</code></li>
                          <li>Clique em <code>+ New registration</code></li>
                          <li>Nome: "Coruja Monitor" (ou nome de sua preferência)</li>
                          <li>Supported account types: "Single tenant"</li>
                          <li>Redirect URI: Deixe em branco</li>
                          <li>Clique em <code>Register</code></li>
                        </ul>
                      </li>
                      <li>
                        <strong>Copiar IDs necessários:</strong>
                        <ul style={{ marginTop: '8px' }}>
                          <li><strong>Application (client) ID</strong> - Copie este valor</li>
                          <li><strong>Directory (tenant) ID</strong> - Copie este valor</li>
                        </ul>
                      </li>
                      <li>
                        <strong>Criar Client Secret:</strong>
                        <ul style={{ marginTop: '8px' }}>
                          <li>No menu lateral, clique em <code>Certificates & secrets</code></li>
                          <li>Clique em <code>+ New client secret</code></li>
                          <li>Description: "Coruja Monitor Key"</li>
                          <li>Expires: 24 months (recomendado)</li>
                          <li><strong>⚠️ IMPORTANTE:</strong> Copie o <strong>Value</strong> imediatamente (não será mostrado novamente!)</li>
                        </ul>
                      </li>
                      <li>
                        <strong>Obter Subscription ID:</strong>
                        <ul style={{ marginTop: '8px' }}>
                          <li>Vá em <code>Subscriptions</code> no menu principal</li>
                          <li>Copie o <strong>Subscription ID</strong> da assinatura que deseja monitorar</li>
                        </ul>
                      </li>
                      <li>
                        <strong>Atribuir Permissões (CRÍTICO):</strong>
                        <ul style={{ marginTop: '8px' }}>
                          <li>Vá em <code>Subscriptions</code> → Selecione sua assinatura</li>
                          <li>Clique em <code>Access control (IAM)</code></li>
                          <li>Clique em <code>+ Add</code> → <code>Add role assignment</code></li>
                          <li>Role: <strong>"Monitoring Reader"</strong> (recomendado) ou "Reader"</li>
                          <li>Assign access to: <strong>"User, group, or service principal"</strong></li>
                          <li>Select members: Busque pelo nome do App Registration criado</li>
                          <li>Clique em <code>Review + assign</code></li>
                        </ul>
                      </li>
                    </ol>
                  </div>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      <strong>⚠️ Segurança:</strong> O role "Monitoring Reader" fornece acesso somente leitura às métricas.
                      Nunca use roles com permissões de escrita (Contributor, Owner) para monitoramento.
                    </p>
                  </div>

                  <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', border: '1px solid #4caf50' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>✔ Recursos que podem ser monitorados:</strong><br/>
                      Virtual Machines, Storage Accounts, SQL Databases, Web Apps, Function Apps, AKS Clusters, 
                      Load Balancers, Application Gateways, Cosmos DB, Redis Cache, Service Bus, Event Hubs, Key Vaults, Backups
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 2: Inserir Credenciais */}
              {azureWizardStep === 2 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#0078d4' }}>🔑 Credenciais Azure</h3>
                  
                  <div className="form-group">
                    <label>Subscription ID: *</label>
                    <input
                      type="text"
                      value={azureConfig.subscription_id}
                      onChange={(e) => setAzureConfig({...azureConfig, subscription_id: e.target.value})}
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                      style={{ fontFamily: 'monospace' }}
                    />
                    <small>ID da assinatura Azure que deseja monitorar</small>
                  </div>

                  <div className="form-group">
                    <label>Tenant ID (Directory ID): *</label>
                    <input
                      type="text"
                      value={azureConfig.tenant_id}
                      onChange={(e) => setAzureConfig({...azureConfig, tenant_id: e.target.value})}
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                      style={{ fontFamily: 'monospace' }}
                    />
                    <small>ID do diretório (Azure Active Directory)</small>
                  </div>

                  <div className="form-group">
                    <label>Client ID (Application ID): *</label>
                    <input
                      type="text"
                      value={azureConfig.client_id}
                      onChange={(e) => setAzureConfig({...azureConfig, client_id: e.target.value})}
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                      style={{ fontFamily: 'monospace' }}
                    />
                    <small>ID da aplicação registrada (App Registration)</small>
                  </div>

                  <div className="form-group">
                    <label>Client Secret: *</label>
                    <input
                      type="password"
                      value={azureConfig.client_secret}
                      onChange={(e) => setAzureConfig({...azureConfig, client_secret: e.target.value})}
                      placeholder="••••••••••••••••••••••••••••••••"
                      style={{ fontFamily: 'monospace' }}
                    />
                    <small>Secret gerado no App Registration (Certificates & secrets)</small>
                  </div>

                  <div className="form-group">
                    <label>Resource Group (Opcional):</label>
                    <input
                      type="text"
                      value={azureConfig.resource_group}
                      onChange={(e) => setAzureConfig({...azureConfig, resource_group: e.target.value})}
                      placeholder="my-resource-group"
                    />
                    <small>Deixe em branco para monitorar todos os resource groups da subscription</small>
                  </div>

                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginTop: '20px' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      💡 <strong>Dica:</strong> Todos os campos marcados com * são obrigatórios. 
                      Certifique-se de que o Service Principal tem o role "Monitoring Reader" atribuído.
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 3: Testar Conexão */}
              {azureWizardStep === 3 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#0078d4' }}>🔎 Testar Conexão Azure</h3>
                  
                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Credenciais Configuradas:</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold', width: '180px' }}>Subscription ID:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{azureConfig.subscription_id || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Tenant ID:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{azureConfig.tenant_id || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Client ID:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{azureConfig.client_id || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Client Secret:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{'•'.repeat(32)}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Resource Group:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{azureConfig.resource_group || '(todos)'}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <button
                    onClick={async () => {
                      alert('🔎 Teste de conexão Azure será implementado no backend.\n\nVerificará:\n✔ Autenticação com Azure AD\n✔ Permissões do Service Principal\n✔ Acesso à Subscription\n✔ Listagem de recursos disponíveis');
                    }}
                    style={{
                      width: '100%',
                      padding: '15px',
                      background: 'linear-gradient(135deg, #0078d4 0%, #00bcf2 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '15px',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      marginBottom: '15px'
                    }}
                  >
                    🔎 Testar Conexão com Azure
                  </button>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>⚠️ Possíveis erros:</strong><br/>
                      ● <strong>401 Unauthorized:</strong> Client Secret inválido ou expirado<br/>
                      ● <strong>403 Forbidden:</strong> Service Principal sem permissões adequadas<br/>
                      ● <strong>404 Not Found:</strong> Subscription ID incorreto<br/>
                      ● <strong>Timeout:</strong> Firewall bloqueando acesso ao Azure
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 4: Selecionar Recursos */}
              {azureWizardStep === 4 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#0078d4' }}>📪 Selecionar Recursos para Monitorar</h3>
                  
                  <div className="info-banner" style={{ background: '#e8f5e9', border: '1px solid #4caf50', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      ✔ Conexão estabelecida com sucesso! Selecione os recursos Azure que deseja monitorar.
                    </p>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '20px' }}>
                    {[
                      { type: 'vm', icon: '🖥️', name: 'Virtual Machines' },
                      { type: 'webapp', icon: '🌐', name: 'Web Apps' },
                      { type: 'sql', icon: '🗄️', name: 'SQL Databases' },
                      { type: 'storage', icon: '🧠', name: 'Storage Accounts' },
                      { type: 'aks', icon: '☸️', name: 'AKS Clusters' },
                      { type: 'function', icon: '⚡', name: 'Azure Functions' },
                      { type: 'backup', icon: '💾', name: 'Backup Vaults' },
                      { type: 'loadbalancer', icon: '⚖️', name: 'Load Balancers' }
                    ].map(resource => (
                      <button
                        key={resource.type}
                        onClick={() => {
                          const selected = azureConfig.selected_resources.includes(resource.type);
                          setAzureConfig({
                            ...azureConfig,
                            selected_resources: selected
                              ? azureConfig.selected_resources.filter(r => r !== resource.type)
                              : [...azureConfig.selected_resources, resource.type]
                          });
                        }}
                        style={{
                          padding: '15px',
                          background: azureConfig.selected_resources.includes(resource.type) 
                            ? 'linear-gradient(135deg, #0078d4 0%, #00bcf2 100%)' 
                            : '#f8f9fa',
                          color: azureConfig.selected_resources.includes(resource.type) ? 'white' : '#333',
                          border: azureConfig.selected_resources.includes(resource.type) ? 'none' : '2px solid #ddd',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          textAlign: 'center',
                          fontSize: '13px',
                          fontWeight: 'bold',
                          transition: 'all 0.2s'
                        }}
                      >
                        <div style={{ fontSize: '24px', marginBottom: '5px' }}>{resource.icon}</div>
                        <div>{resource.name}</div>
                        {azureConfig.selected_resources.includes(resource.type) && (
                          <div style={{ marginTop: '5px', fontSize: '16px' }}>✔</div>
                        )}
                      </button>
                    ))}
                  </div>

                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      💡 Selecionados: <strong>{azureConfig.selected_resources.length}</strong> tipo(s) de recurso.
                      Sensores serão criados automaticamente para cada recurso encontrado.
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer" style={{ display: 'flex', justifyContent: 'space-between' }}>
              <button 
                className="btn-secondary" 
                onClick={() => {
                  if (azureWizardStep > 1) {
                    setAzureWizardStep(azureWizardStep - 1);
                  } else {
                    setShowAzureWizard(false);
                  }
                }}
              >
                {azureWizardStep === 1 ? 'Cancelar' : '← Voltar'}
              </button>
              
              <button 
                className="btn-primary" 
                onClick={() => {
                  if (azureWizardStep < 4) {
                    // Validar campos obrigatórios no passo 2
                    if (azureWizardStep === 2) {
                      if (!azureConfig.subscription_id || !azureConfig.tenant_id || 
                          !azureConfig.client_id || !azureConfig.client_secret) {
                        alert('⚠️ Preencha todos os campos obrigatórios antes de continuar.');
                        return;
                      }
                    }
                    setAzureWizardStep(azureWizardStep + 1);
                  } else {
                    // Finalizar e criar sensores
                    alert(`✔ Configuração Azure concluída!\n\n${azureConfig.selected_resources.length} tipo(s) de recurso selecionado(s).\n\nOs sensores serão criados na Biblioteca de Sensores Independentes.`);
                    setShowAzureWizard(false);
                    setAzureWizardStep(1);
                    // Redirecionar para biblioteca com Azure pré-selecionado
                    window.location.hash = '#/sensor-library?type=azure';
                  }
                }}
                disabled={azureWizardStep === 4 && azureConfig.selected_resources.length === 0}
                style={{
                  opacity: (azureWizardStep === 4 && azureConfig.selected_resources.length === 0) ? 0.5 : 1,
                  cursor: (azureWizardStep === 4 && azureConfig.selected_resources.length === 0) ? 'not-allowed' : 'pointer'
                }}
              >
                {azureWizardStep === 4 ? '✔ Finalizar e Criar Sensores' : 'Próximo →'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Wizard SNMP Genérico - Adaptável para vários tipos */}
      {showSNMPWizard && (
        <div className="modal-overlay" onClick={() => setShowSNMPWizard(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h2>
                {currentWizardType === 'snmp' && '📡 Configurar SNMP Genérico'}
                {currentWizardType === 'ap' && '📶 Configurar Access Point'}
                {currentWizardType === 'temp' && '🌡️ Configurar Sensor de Temperatura'}
                {currentWizardType === 'storage' && '🧠 Configurar Storage/NAS'}
                {currentWizardType === 'printer' && '🖨️ Configurar Impressora'}
                {currentWizardType === 'ups' && '🔋 Configurar UPS/Nobreak'}
                {' - Passo '}{snmpWizardStep} de 3
              </h2>
              <button className="modal-close" onClick={() => setShowSNMPWizard(false)}>×</button>
            </div>

            <div className="modal-body">
              {/* Passo 1: Requisitos */}
              {snmpWizardStep === 1 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#667eea' }}>📏 Requisitos SNMP</h3>
                  
                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      <strong>ℹ️ Baseado em PRTG, SolarWinds, CheckMK e Zabbix</strong><br/>
                      SNMP (Simple Network Management Protocol) permite monitorar dispositivos de rede remotamente.
                    </p>
                  </div>

                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>🔧 Configuração no Dispositivo:</h4>
                    <ol style={{ lineHeight: '1.8', fontSize: '14px', paddingLeft: '20px' }}>
                      <li><strong>Habilitar SNMP</strong> no dispositivo (v1, v2c ou v3)</li>
                      <li><strong>Configurar Community String</strong> (padrão: "public" para leitura)</li>
                      <li><strong>Porta SNMP</strong>: 161/UDP (padrão)</li>
                      <li><strong>Permitir acesso</strong> do IP da probe no firewall</li>
                    </ol>

                    {currentWizardType === 'ap' && (
                      <div style={{ marginTop: '15px', padding: '12px', background: '#fff3cd', borderRadius: '6px' }}>
                        <strong>📶 Access Points WiFi - Métricas Detalhadas:</strong>
                        <div style={{ marginTop: '10px' }}>
                          <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#2196f3' }}>1. Status:</strong>
                            <ul style={{ marginTop: '4px', fontSize: '12px', marginLeft: '20px' }}>
                              <li>Online/Offline, Uptime, Reboots, Firmware version</li>
                            </ul>
                          </div>
                          <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#2196f3' }}>2. Carga:</strong>
                            <ul style={{ marginTop: '4px', fontSize: '12px', marginLeft: '20px' }}>
                              <li>CPU % e Memória %</li>
                              <li>Número de clientes conectados (2.4GHz + 5GHz)</li>
                              <li>Capacidade máxima vs atual</li>
                            </ul>
                          </div>
                          <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#2196f3' }}>3. Tráfego:</strong>
                            <ul style={{ marginTop: '4px', fontSize: '12px', marginLeft: '20px' }}>
                              <li>TX/RX bytes e pacotes por interface</li>
                              <li>Erros, Drops, Retransmissões</li>
                              <li>Throughput em Mbps</li>
                            </ul>
                          </div>
                          <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#2196f3' }}>4. Sinais:</strong>
                            <ul style={{ marginTop: '4px', fontSize: '12px', marginLeft: '20px' }}>
                              <li>RSSI médio (dBm) - força do sinal</li>
                              <li>SNR (Signal-to-Noise Ratio)</li>
                              <li>Qualidade do sinal (%)</li>
                              <li>Interferência e ruído</li>
                            </ul>
                          </div>
                          <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#2196f3' }}>5. Acesso:</strong>
                            <ul style={{ marginTop: '4px', fontSize: '12px', marginLeft: '20px' }}>
                              <li>SSIDs ativos e seus status</li>
                              <li>Autenticações bem-sucedidas/falhadas</li>
                              <li>Associações e desassociações</li>
                              <li>Eventos de roaming</li>
                            </ul>
                          </div>
                        </div>
                        <div style={{ marginTop: '12px', padding: '8px', background: '#e3f2fd', borderRadius: '4px' }}>
                          <strong>🔧 Configuração por Fabricante:</strong>
                          <ul style={{ marginTop: '5px', fontSize: '12px' }}>
                            <li><strong>Ubiquiti UniFi:</strong> Settings → Services → SNMP → Enable</li>
                            <li><strong>MikroTik:</strong> IP → SNMP → Communities → Add</li>
                            <li><strong>Cisco Aironet:</strong> configure terminal → snmp-server community public RO</li>
                            <li><strong>TP-Link EAP:</strong> Management → SNMP Settings → Enable v2c</li>
                            <li><strong>Aruba:</strong> Configuration → System → SNMP</li>
                          </ul>
                        </div>
                      </div>
                    )}

                    {currentWizardType === 'printer' && (
                      <div style={{ marginTop: '15px', padding: '12px', background: '#fff3cd', borderRadius: '6px' }}>
                        <strong>🖨️ Impressoras:</strong>
                        <ul style={{ marginTop: '8px', fontSize: '13px' }}>
                          <li>HP: Menu → Network → SNMP → Enable</li>
                          <li>Canon: Setup → Network → SNMP Settings</li>
                          <li>Epson: Network → SNMP → Enable</li>
                        </ul>
                      </div>
                    )}

                    {currentWizardType === 'ups' && (
                      <div style={{ marginTop: '15px', padding: '12px', background: '#fff3cd', borderRadius: '6px' }}>
                        <strong>🔋 UPS/Nobreak:</strong>
                        <ul style={{ marginTop: '8px', fontSize: '13px' }}>
                          <li>APC: Network → SNMP → Access Control</li>
                          <li>SMS: Web Interface → SNMP Settings</li>
                          <li>Requer Network Management Card em alguns modelos</li>
                        </ul>
                      </div>
                    )}
                  </div>

                  <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', border: '1px solid #4caf50' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>✔ Métricas Monitoradas:</strong><br/>
                      {currentWizardType === 'snmp' && 'Status, Uptime, Interfaces, Tráfego, CPU, Memória'}
                      {currentWizardType === 'ap' && 'Status, Carga (CPU/Mem/Clientes), Tráfego (TX/RX), Sinais (RSSI/SNR), Acesso (SSIDs/Auth)'}
                      {currentWizardType === 'temp' && 'Temperatura, Umidade, Alarmes'}
                      {currentWizardType === 'storage' && 'Espaço em disco, RAID status, Temperatura'}
                      {currentWizardType === 'printer' && 'Status, Níveis de toner, Papel, Total de páginas'}
                      {currentWizardType === 'ups' && 'Status, Bateria %, Tempo restante, Carga, Tensão'}
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 2: Configuração */}
              {snmpWizardStep === 2 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#667eea' }}>⚙️ Configuração do Sensor</h3>
                  
                  <div className="form-group">
                    <label>Probe Responsável: *</label>
                    <select 
                      value={snmpConfig.probe_id}
                      onChange={(e) => setSNMPConfig({...snmpConfig, probe_id: e.target.value})}
                    >
                      <option value="">-- Selecione uma probe --</option>
                      {probes.map(probe => (
                        <option key={probe.id} value={probe.id}>{probe.name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Nome do Sensor: *</label>
                    <input
                      type="text"
                      value={snmpConfig.name}
                      onChange={(e) => setSNMPConfig({...snmpConfig, name: e.target.value})}
                      placeholder={
                        currentWizardType === 'printer' ? 'Ex: Impressora-RH-HP4015' :
                        currentWizardType === 'ups' ? 'Ex: UPS-Datacenter-APC1500' :
                        currentWizardType === 'ap' ? 'Ex: AP-Sala-01-UniFi' :
                        'Ex: Switch-Core-01'
                      }
                    />
                  </div>

                  <div className="form-group">
                    <label>Endereço IP: *</label>
                    <input
                      type="text"
                      value={snmpConfig.ip_address}
                      onChange={(e) => setSNMPConfig({...snmpConfig, ip_address: e.target.value})}
                      placeholder="192.168.1.100"
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Versão SNMP:</label>
                      <select
                        value={snmpConfig.snmp_version}
                        onChange={(e) => setSNMPConfig({...snmpConfig, snmp_version: e.target.value})}
                      >
                        <option value="v1">SNMP v1</option>
                        <option value="v2c">SNMP v2c (recomendado)</option>
                        <option value="v3">SNMP v3 (mais seguro)</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Community String:</label>
                      <input
                        type="text"
                        value={snmpConfig.snmp_community}
                        onChange={(e) => setSNMPConfig({...snmpConfig, snmp_community: e.target.value})}
                        placeholder="public"
                      />
                    </div>

                    <div className="form-group">
                      <label>Porta SNMP:</label>
                      <input
                        type="number"
                        value={snmpConfig.snmp_port}
                        onChange={(e) => setSNMPConfig({...snmpConfig, snmp_port: e.target.value})}
                        placeholder="161"
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Descrição (Opcional):</label>
                    <textarea
                      value={snmpConfig.description}
                      onChange={(e) => setSNMPConfig({...snmpConfig, description: e.target.value})}
                      rows="2"
                      placeholder="Informações adicionais sobre o dispositivo..."
                    />
                  </div>
                </div>
              )}

              {/* Passo 3: Testar e Finalizar */}
              {snmpWizardStep === 3 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#667eea' }}>🔎 Testar Conexão SNMP</h3>
                  
                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Configuração:</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold', width: '150px' }}>Nome:</td>
                          <td>{snmpConfig.name || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>IP:</td>
                          <td style={{ fontFamily: 'monospace' }}>{snmpConfig.ip_address || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Versão:</td>
                          <td>{snmpConfig.snmp_version}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Community:</td>
                          <td>{snmpConfig.snmp_community}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Porta:</td>
                          <td>{snmpConfig.snmp_port}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <button
                    onClick={() => {
                      alert('🔎 Teste de conexão SNMP será implementado no backend.\n\nVerificará:\n✔ Conectividade de rede\n✔ Porta SNMP acessível\n✔ Community string válido\n✔ Resposta do dispositivo');
                    }}
                    style={{
                      width: '100%',
                      padding: '15px',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '15px',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      marginBottom: '15px'
                    }}
                  >
                    🔎 Testar Conexão SNMP
                  </button>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>⚠️ Troubleshooting:</strong><br/>
                      ● <strong>Timeout:</strong> Verifique firewall e conectividade<br/>
                      ● <strong>Auth Failed:</strong> Community string incorreto<br/>
                      ● <strong>No Response:</strong> SNMP não habilitado no dispositivo
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer" style={{ display: 'flex', justifyContent: 'space-between' }}>
              <button 
                className="btn-secondary" 
                onClick={() => {
                  if (snmpWizardStep > 1) {
                    setSNMPWizardStep(snmpWizardStep - 1);
                  } else {
                    setShowSNMPWizard(false);
                  }
                }}
              >
                {snmpWizardStep === 1 ? 'Cancelar' : '← Voltar'}
              </button>
              
              <button 
                className="btn-primary" 
                onClick={() => {
                  if (snmpWizardStep < 3) {
                    if (snmpWizardStep === 2) {
                      if (!snmpConfig.probe_id || !snmpConfig.name || !snmpConfig.ip_address) {
                        alert('⚠️ Preencha todos os campos obrigatórios.');
                        return;
                      }
                    }
                    setSNMPWizardStep(snmpWizardStep + 1);
                  } else {
                    alert(`✔ Sensor SNMP configurado!\n\nO sensor será criado na Biblioteca de Sensores Independentes.`);
                    setShowSNMPWizard(false);
                    setSNMPWizardStep(1);
                    window.location.hash = '#/sensor-library?type=snmp';
                  }
                }}
              >
                {snmpWizardStep === 3 ? '✔ Criar Sensor' : 'Próximo →'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Wizard HTTP/HTTPS */}
      {showHTTPWizard && (
        <div className="modal-overlay" onClick={() => setShowHTTPWizard(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h2>🌐 Configurar Monitoramento HTTP/HTTPS - Passo {httpWizardStep} de 3</h2>
              <button className="modal-close" onClick={() => setShowHTTPWizard(false)}>×</button>
            </div>

            <div className="modal-body">
              {/* Passo 1: Requisitos */}
              {httpWizardStep === 1 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#4facfe' }}>📏 Monitoramento HTTP/HTTPS</h3>
                  
                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      <strong>ℹ️ Monitore websites, APIs e endpoints</strong><br/>
                      Verifique disponibilidade, tempo de resposta e conteúdo de páginas web.
                    </p>
                  </div>

                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>✔ Verificações Disponíveis:</h4>
                    <ul style={{ lineHeight: '1.8', fontSize: '14px' }}>
                      <li><strong>Status Code:</strong> 200 (OK), 301 (Redirect), 404 (Not Found), 500 (Error)</li>
                      <li><strong>Tempo de Resposta:</strong> Latência em milissegundos</li>
                      <li><strong>Certificado SSL:</strong> Validade e expiração (HTTPS)</li>
                      <li><strong>Conteúdo:</strong> Busca por palavras-chave na página</li>
                      <li><strong>Redirecionamentos:</strong> Seguir ou não seguir redirects</li>
                    </ul>
                  </div>

                  <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', border: '1px solid #4caf50' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>📋 Autenticação Suportada:</strong><br/>
                      Basic Auth, Bearer Token, API Key, Custom Headers
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 2: Configuração */}
              {httpWizardStep === 2 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#4facfe' }}>⚙️ Configuração do Monitoramento</h3>
                  
                  <div className="form-group">
                    <label>Probe Responsável: *</label>
                    <select 
                      value={httpConfig.probe_id}
                      onChange={(e) => setHTTPConfig({...httpConfig, probe_id: e.target.value})}
                    >
                      <option value="">-- Selecione uma probe --</option>
                      {probes.map(probe => (
                        <option key={probe.id} value={probe.id}>{probe.name}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Nome do Sensor: *</label>
                    <input
                      type="text"
                      value={httpConfig.name}
                      onChange={(e) => setHTTPConfig({...httpConfig, name: e.target.value})}
                      placeholder="Ex: Site-Corporativo, API-Producao"
                    />
                  </div>

                  <div className="form-group">
                    <label>URL Completa: *</label>
                    <input
                      type="url"
                      value={httpConfig.url}
                      onChange={(e) => setHTTPConfig({...httpConfig, url: e.target.value})}
                      placeholder="https://example.com/api/health"
                    />
                    <small>Inclua http:// ou https://</small>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Método HTTP:</label>
                      <select
                        value={httpConfig.method}
                        onChange={(e) => setHTTPConfig({...httpConfig, method: e.target.value})}
                      >
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="HEAD">HEAD</option>
                        <option value="PUT">PUT</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Status Esperado:</label>
                      <input
                        type="number"
                        value={httpConfig.expected_status}
                        onChange={(e) => setHTTPConfig({...httpConfig, expected_status: e.target.value})}
                        placeholder="200"
                      />
                    </div>

                    <div className="form-group">
                      <label>Timeout (seg):</label>
                      <input
                        type="number"
                        value={httpConfig.timeout}
                        onChange={(e) => setHTTPConfig({...httpConfig, timeout: e.target.value})}
                        placeholder="10"
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={httpConfig.check_ssl}
                        onChange={(e) => setHTTPConfig({...httpConfig, check_ssl: e.target.checked})}
                      />
                      {' '}Verificar validade do certificado SSL (HTTPS)
                    </label>
                  </div>

                  <div className="form-group">
                    <label>Palavra-chave no conteúdo (Opcional):</label>
                    <input
                      type="text"
                      value={httpConfig.keyword}
                      onChange={(e) => setHTTPConfig({...httpConfig, keyword: e.target.value})}
                      placeholder="Ex: Welcome, Success, OK"
                    />
                    <small>Alerta se a palavra NÃO for encontrada na página</small>
                  </div>
                </div>
              )}

              {/* Passo 3: Testar */}
              {httpWizardStep === 3 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#4facfe' }}>🔎 Testar Conexão HTTP</h3>
                  
                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Configuração:</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold', width: '150px' }}>Nome:</td>
                          <td>{httpConfig.name || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>URL:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px', wordBreak: 'break-all' }}>{httpConfig.url || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Método:</td>
                          <td>{httpConfig.method}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Status Esperado:</td>
                          <td>{httpConfig.expected_status}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Verificar SSL:</td>
                          <td>{httpConfig.check_ssl ? 'Sim' : 'Não'}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <button
                    onClick={() => {
                      alert('🔎 Teste de conexão HTTP será implementado no backend.\n\nVerificará:\n✔ Conectividade com a URL\n✔ Status code retornado\n✔ Tempo de resposta\n✔ Certificado SSL (se HTTPS)\n✔ Palavra-chave (se configurada)');
                    }}
                    style={{
                      width: '100%',
                      padding: '15px',
                      background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '15px',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      marginBottom: '15px'
                    }}
                  >
                    🔎 Testar Conexão HTTP
                  </button>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>⚠️ Troubleshooting:</strong><br/>
                      ● <strong>Connection Refused:</strong> Servidor offline ou firewall bloqueando<br/>
                      ● <strong>SSL Error:</strong> Certificado inválido ou expirado<br/>
                      ● <strong>Timeout:</strong> Servidor lento ou não responde
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer" style={{ display: 'flex', justifyContent: 'space-between' }}>
              <button 
                className="btn-secondary" 
                onClick={() => {
                  if (httpWizardStep > 1) {
                    setHTTPWizardStep(httpWizardStep - 1);
                  } else {
                    setShowHTTPWizard(false);
                  }
                }}
              >
                {httpWizardStep === 1 ? 'Cancelar' : '← Voltar'}
              </button>
              
              <button 
                className="btn-primary" 
                onClick={async () => {
                  if (httpWizardStep < 3) {
                    if (httpWizardStep === 2) {
                      if (!httpConfig.probe_id || !httpConfig.name || !httpConfig.url) {
                        alert('⚠️ Preencha todos os campos obrigatórios.');
                        return;
                      }
                    }
                    setHTTPWizardStep(httpWizardStep + 1);
                  } else {
                    try {
                      await api.post('/sensors/standalone', {
                        probe_id: parseInt(httpConfig.probe_id),
                        name: httpConfig.name,
                        sensor_type: 'http',
                        category: 'network',
                        http_url: httpConfig.url,
                        http_method: httpConfig.method,
                        threshold_warning: httpConfig.threshold_warning,
                        threshold_critical: httpConfig.threshold_critical,
                        description: httpConfig.description || `Monitor HTTP: ${httpConfig.url}`
                      });
                      alert(`✔ Sensor HTTP "${httpConfig.name}" criado com sucesso!\n\nAcesse "Biblioteca de Sensores" para visualizá-lo.`);
                      setShowHTTPWizard(false);
                      setHTTPWizardStep(1);
                      setHTTPConfig({
                        probe_id: '',
                        name: '',
                        url: '',
                        method: 'GET',
                        expected_status: 200,
                        timeout: 10,
                        check_ssl: true,
                        keyword: '',
                        threshold_warning: 2000,
                        threshold_critical: 5000,
                        description: ''
                      });
                    } catch (error) {
                      alert('✖ Erro ao criar sensor: ' + (error.response?.data?.detail || error.message));
                    }
                  }
                }}
              >
                {httpWizardStep === 3 ? '✔ Criar Sensor' : 'Próximo →'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Wizard Kubernetes - Passo a Passo Completo */}
      {showK8sWizard && (
        <div className="modal-overlay" onClick={() => setShowK8sWizard(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px' }}>
            <div className="modal-header">
              <h2>☸️ Configurar Monitoramento Kubernetes - Passo {k8sWizardStep} de 4</h2>
              <button className="modal-close" onClick={() => setShowK8sWizard(false)}>×</button>
            </div>

            <div className="modal-body">
              {/* Passo 1: Requisitos e Instruções */}
              {k8sWizardStep === 1 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#326ce5' }}>📏 Requisitos para Monitoramento Kubernetes</h3>
                  
                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      <strong>ℹ️ Baseado em CheckMK, Prometheus e Grafana</strong><br/>
                      Monitore clusters Kubernetes completos com auto-discovery de pods, deployments e recursos.
                    </p>
                  </div>

                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0, color: '#333' }}>📋 Métodos de Autenticação Suportados</h4>
                    
                    <div style={{ marginBottom: '15px', padding: '12px', background: 'white', borderRadius: '6px', border: '1px solid #e0e0e0' }}>
                      <strong style={{ color: '#326ce5' }}>1. Kubeconfig File (Recomendado)</strong>
                      <ul style={{ marginTop: '8px', fontSize: '13px', lineHeight: '1.6' }}>
                        <li>Arquivo de configuração padrão do kubectl</li>
                        <li>Localização: <code>~/.kube/config</code></li>
                        <li>Contém certificados e credenciais</li>
                        <li>Suporta múltiplos clusters e contextos</li>
                      </ul>
                      <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px', fontFamily: 'monospace', fontSize: '11px' }}>
                        # Obter kubeconfig<br/>
                        kubectl config view --raw &gt; kubeconfig.yaml
                      </div>
                    </div>

                    <div style={{ marginBottom: '15px', padding: '12px', background: 'white', borderRadius: '6px', border: '1px solid #e0e0e0' }}>
                      <strong style={{ color: '#326ce5' }}>2. Service Account Token</strong>
                      <ul style={{ marginTop: '8px', fontSize: '13px', lineHeight: '1.6' }}>
                        <li>Criar Service Account com permissões de leitura</li>
                        <li>Extrair token do secret</li>
                        <li>Requer RBAC configurado</li>
                      </ul>
                      <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px', fontFamily: 'monospace', fontSize: '11px' }}>
                        # Criar Service Account<br/>
                        kubectl create serviceaccount coruja-monitor<br/>
                        kubectl create clusterrolebinding coruja-monitor --clusterrole=view --serviceaccount=default:coruja-monitor<br/>
                        <br/>
                        # Obter token<br/>
                        kubectl create token coruja-monitor
                      </div>
                    </div>

                    <div style={{ padding: '12px', background: 'white', borderRadius: '6px', border: '1px solid #e0e0e0' }}>
                      <strong style={{ color: '#326ce5' }}>3. Bearer Token</strong>
                      <ul style={{ marginTop: '8px', fontSize: '13px', lineHeight: '1.6' }}>
                        <li>Token de autenticação direto</li>
                        <li>Usado em clusters gerenciados (AKS, EKS, GKE)</li>
                        <li>Pode expirar periodicamente</li>
                      </ul>
                    </div>
                  </div>

                  <div style={{ background: '#fff3cd', padding: '15px', borderRadius: '8px', border: '1px solid #ffc107', marginBottom: '20px' }}>
                    <strong>🎯 Tipos de Cluster Suportados:</strong>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', marginTop: '10px' }}>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>☸️</div>
                        <strong>Vanilla K8s</strong>
                      </div>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>☁️</div>
                        <strong>Azure AKS</strong>
                      </div>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>☁️</div>
                        <strong>AWS EKS</strong>
                      </div>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>🌐</div>
                        <strong>Google GKE</strong>
                      </div>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>🔴</div>
                        <strong>OpenShift</strong>
                      </div>
                    </div>
                  </div>

                  <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', border: '1px solid #4caf50' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>✔ Recursos Monitorados Automaticamente:</strong><br/>
                      ● <strong>Cluster:</strong> Status geral, nodes disponíveis, capacidade total<br/>
                      ● <strong>Nodes:</strong> CPU, memória, disco, pods por node<br/>
                      ● <strong>Pods:</strong> Status, restarts, CPU/memória por pod<br/>
                      ● <strong>Deployments:</strong> Réplicas desejadas vs disponíveis<br/>
                      ● <strong>DaemonSets:</strong> Pods rodando vs esperados<br/>
                      ● <strong>StatefulSets:</strong> Status e réplicas<br/>
                      ● <strong>Services:</strong> Endpoints disponíveis<br/>
                      ● <strong>PersistentVolumes:</strong> Uso de armazenamento
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 2: Configuração do Cluster */}
              {k8sWizardStep === 2 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#326ce5' }}>⚙️ Configuração do Cluster</h3>
                  
                  <div className="form-group">
                    <label>Nome do Cluster: *</label>
                    <input
                      type="text"
                      value={k8sConfig.cluster_name}
                      onChange={(e) => setK8sConfig({...k8sConfig, cluster_name: e.target.value})}
                      placeholder="production-cluster"
                    />
                    <small>Nome identificador para este cluster</small>
                  </div>

                  <div className="form-group">
                    <label>Tipo de Cluster: *</label>
                    <select
                      value={k8sConfig.cluster_type}
                      onChange={(e) => setK8sConfig({...k8sConfig, cluster_type: e.target.value})}
                    >
                      <option value="vanilla">☸️ Vanilla Kubernetes</option>
                      <option value="aks">☁️ Azure AKS</option>
                      <option value="eks">☁️ AWS EKS</option>
                      <option value="gke">🌐 Google GKE</option>
                      <option value="openshift">🔴 Red Hat OpenShift</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>API Server Endpoint: *</label>
                    <input
                      type="text"
                      value={k8sConfig.api_endpoint}
                      onChange={(e) => setK8sConfig({...k8sConfig, api_endpoint: e.target.value})}
                      placeholder="https://cluster.example.com:6443"
                      style={{ fontFamily: 'monospace' }}
                    />
                    <small>URL do API server do Kubernetes</small>
                  </div>

                  <div className="form-group">
                    <label>Método de Autenticação: *</label>
                    <select
                      value={k8sConfig.auth_method}
                      onChange={(e) => setK8sConfig({...k8sConfig, auth_method: e.target.value})}
                    >
                      <option value="kubeconfig">📄 Kubeconfig File (Recomendado)</option>
                      <option value="service_account">🔑 Service Account Token</option>
                      <option value="token">🎫 Bearer Token</option>
                    </select>
                  </div>

                  {k8sConfig.auth_method === 'kubeconfig' && (
                    <div className="form-group">
                      <label>Conteúdo do Kubeconfig: *</label>
                      <textarea
                        value={k8sConfig.kubeconfig_content}
                        onChange={(e) => setK8sConfig({...k8sConfig, kubeconfig_content: e.target.value})}
                        placeholder="Cole aqui o conteúdo do arquivo kubeconfig..."
                        rows="8"
                        style={{ fontFamily: 'monospace', fontSize: '11px' }}
                      />
                      <small>Cole o conteúdo completo do arquivo ~/.kube/config</small>
                    </div>
                  )}

                  {k8sConfig.auth_method === 'service_account' && (
                    <>
                      <div className="form-group">
                        <label>Service Account Token: *</label>
                        <textarea
                          value={k8sConfig.service_account_token}
                          onChange={(e) => setK8sConfig({...k8sConfig, service_account_token: e.target.value})}
                          placeholder="eyJhbGciOiJSUzI1NiIsImtpZCI6..."
                          rows="4"
                          style={{ fontFamily: 'monospace', fontSize: '11px' }}
                        />
                        <small>Token do Service Account com permissões de leitura</small>
                      </div>
                      <div className="form-group">
                        <label>CA Certificate (Opcional):</label>
                        <textarea
                          value={k8sConfig.ca_cert}
                          onChange={(e) => setK8sConfig({...k8sConfig, ca_cert: e.target.value})}
                          placeholder="-----BEGIN CERTIFICATE-----..."
                          rows="4"
                          style={{ fontFamily: 'monospace', fontSize: '11px' }}
                        />
                        <small>Certificado CA do cluster (deixe em branco para usar o padrão do sistema)</small>
                      </div>
                    </>
                  )}

                  {k8sConfig.auth_method === 'token' && (
                    <div className="form-group">
                      <label>Bearer Token: *</label>
                      <textarea
                        value={k8sConfig.service_account_token}
                        onChange={(e) => setK8sConfig({...k8sConfig, service_account_token: e.target.value})}
                        placeholder="Token de autenticação..."
                        rows="3"
                        style={{ fontFamily: 'monospace', fontSize: '11px' }}
                      />
                      <small>Token de autenticação do cluster</small>
                    </div>
                  )}

                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginTop: '20px' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      💡 <strong>Dica:</strong> Para clusters gerenciados (AKS, EKS, GKE), use o comando CLI específico para obter as credenciais:<br/>
                      ● <strong>AKS:</strong> <code>az aks get-credentials --resource-group RG --name CLUSTER</code><br/>
                      ● <strong>EKS:</strong> <code>aws eks update-kubeconfig --name CLUSTER</code><br/>
                      ● <strong>GKE:</strong> <code>gcloud container clusters get-credentials CLUSTER</code>
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 3: Testar Conexão */}
              {k8sWizardStep === 3 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#326ce5' }}>🔎 Testar Conexão com Cluster</h3>
                  
                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Configuração do Cluster:</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold', width: '180px' }}>Nome:</td>
                          <td>{k8sConfig.cluster_name || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Tipo:</td>
                          <td>{k8sConfig.cluster_type === 'vanilla' ? '☸️ Vanilla Kubernetes' : 
                               k8sConfig.cluster_type === 'aks' ? '☁️ Azure AKS' :
                               k8sConfig.cluster_type === 'eks' ? '☁️ AWS EKS' :
                               k8sConfig.cluster_type === 'gke' ? '🌐 Google GKE' : '🔴 OpenShift'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>API Endpoint:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px', wordBreak: 'break-all' }}>{k8sConfig.api_endpoint || '(não informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Autenticação:</td>
                          <td>{k8sConfig.auth_method === 'kubeconfig' ? '📄 Kubeconfig' : 
                               k8sConfig.auth_method === 'service_account' ? '🔑 Service Account' : '🎫 Bearer Token'}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <button
                    onClick={async () => {
                      alert('🔎 Teste de conexão Kubernetes será implementado no backend.\n\nVerificará:\n✔ Conectividade com API Server\n✔ Autenticação válida\n✔ Permissões RBAC\n✔ Listagem de namespaces\n✔ Acesso aos recursos\n✔ Metrics Server disponível');
                    }}
                    style={{
                      width: '100%',
                      padding: '15px',
                      background: 'linear-gradient(135deg, #326ce5 0%, #5a9fd4 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '15px',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      marginBottom: '15px'
                    }}
                  >
                    🔎 Testar Conexão com Cluster
                  </button>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>⚠️ Possíveis erros:</strong><br/>
                      ● <strong>Connection Refused:</strong> API Server inacessível ou firewall bloqueando<br/>
                      ● <strong>401 Unauthorized:</strong> Credenciais inválidas ou expiradas<br/>
                      ● <strong>403 Forbidden:</strong> Service Account sem permissões RBAC adequadas<br/>
                      ● <strong>Certificate Error:</strong> CA certificate inválido ou não confiável<br/>
                      ● <strong>Metrics Server Not Found:</strong> Metrics Server não instalado no cluster
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 4: Selecionar Namespaces e Recursos */}
              {k8sWizardStep === 4 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#326ce5' }}>📪 Selecionar Recursos para Monitorar</h3>
                  
                  <div className="info-banner" style={{ background: '#e8f5e9', border: '1px solid #4caf50', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      ✔ Conexão estabelecida com sucesso! Configure quais recursos deseja monitorar.
                    </p>
                  </div>

                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={k8sConfig.monitor_all_namespaces}
                        onChange={(e) => setK8sConfig({...k8sConfig, monitor_all_namespaces: e.target.checked})}
                      />
                      {' '}Monitorar todos os namespaces
                    </label>
                    <small>Se desmarcado, você poderá selecionar namespaces específicos</small>
                  </div>

                  {!k8sConfig.monitor_all_namespaces && (
                    <div className="form-group">
                      <label>Namespaces Específicos:</label>
                      <input
                        type="text"
                        value={k8sConfig.namespaces.join(', ')}
                        onChange={(e) => setK8sConfig({...k8sConfig, namespaces: e.target.value.split(',').map(ns => ns.trim()).filter(ns => ns)})}
                        placeholder="default, production, staging"
                      />
                      <small>Separe múltiplos namespaces por vírgula</small>
                    </div>
                  )}

                  <h4 style={{ marginTop: '20px', marginBottom: '15px' }}>Tipos de Recursos:</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '20px' }}>
                    {[
                      { type: 'nodes', icon: '🖥️', name: 'Nodes', desc: 'CPU, memória, disco' },
                      { type: 'pods', icon: '📪', name: 'Pods', desc: 'Status, restarts, recursos' },
                      { type: 'deployments', icon: '🚀', name: 'Deployments', desc: 'Réplicas, rollouts' },
                      { type: 'daemonsets', icon: '⚙️', name: 'DaemonSets', desc: 'Pods por node' },
                      { type: 'statefulsets', icon: '🧠', name: 'StatefulSets', desc: 'Réplicas ordenadas' },
                      { type: 'services', icon: '🌐', name: 'Services', desc: 'Endpoints, portas' },
                      { type: 'ingress', icon: '🔀', name: 'Ingress', desc: 'Rotas HTTP/HTTPS' },
                      { type: 'pv', icon: '💾', name: 'Persistent Volumes', desc: 'Armazenamento' }
                    ].map(resource => (
                      <button
                        key={resource.type}
                        onClick={() => {
                          const selected = k8sConfig.selected_resources.includes(resource.type);
                          setK8sConfig({
                            ...k8sConfig,
                            selected_resources: selected
                              ? k8sConfig.selected_resources.filter(r => r !== resource.type)
                              : [...k8sConfig.selected_resources, resource.type]
                          });
                        }}
                        style={{
                          padding: '15px',
                          background: k8sConfig.selected_resources.includes(resource.type) 
                            ? 'linear-gradient(135deg, #326ce5 0%, #5a9fd4 100%)' 
                            : '#f8f9fa',
                          color: k8sConfig.selected_resources.includes(resource.type) ? 'white' : '#333',
                          border: k8sConfig.selected_resources.includes(resource.type) ? 'none' : '2px solid #ddd',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          textAlign: 'left',
                          fontSize: '13px',
                          transition: 'all 0.2s'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                          <span style={{ fontSize: '24px', marginRight: '8px' }}>{resource.icon}</span>
                          <strong>{resource.name}</strong>
                        </div>
                        <div style={{ fontSize: '11px', opacity: 0.9 }}>{resource.desc}</div>
                        {k8sConfig.selected_resources.includes(resource.type) && (
                          <div style={{ marginTop: '8px', fontSize: '16px', textAlign: 'center' }}>✔</div>
                        )}
                      </button>
                    ))}
                  </div>

                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      💡 Selecionados: <strong>{k8sConfig.selected_resources.length}</strong> tipo(s) de recurso.
                      {k8sConfig.monitor_all_namespaces ? ' Monitorando todos os namespaces.' : ` Monitorando ${k8sConfig.namespaces.length} namespace(s).`}
                      <br/><br/>
                      <strong>⏱️ Intervalo de coleta:</strong> Métricas atualizadas a cada 60 segundos (configurável).
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer" style={{ display: 'flex', justifyContent: 'space-between' }}>
              <button 
                className="btn-secondary" 
                onClick={() => {
                  if (k8sWizardStep > 1) {
                    setK8sWizardStep(k8sWizardStep - 1);
                  } else {
                    setShowK8sWizard(false);
                  }
                }}
              >
                {k8sWizardStep === 1 ? 'Cancelar' : '← Voltar'}
              </button>
              
              <button 
                className="btn-primary" 
                onClick={() => {
                  if (k8sWizardStep < 4) {
                    // Validar campos obrigatórios no passo 2
                    if (k8sWizardStep === 2) {
                      if (!k8sConfig.cluster_name || !k8sConfig.api_endpoint) {
                        alert('⚠️ Preencha o nome do cluster e o API endpoint.');
                        return;
                      }
                      if (k8sConfig.auth_method === 'kubeconfig' && !k8sConfig.kubeconfig_content) {
                        alert('⚠️ Cole o conteúdo do kubeconfig.');
                        return;
                      }
                      if ((k8sConfig.auth_method === 'service_account' || k8sConfig.auth_method === 'token') && !k8sConfig.service_account_token) {
                        alert('⚠️ Informe o token de autenticação.');
                        return;
                      }
                    }
                    setK8sWizardStep(k8sWizardStep + 1);
                  } else {
                    // Finalizar e criar sensores
                    const namespaceInfo = k8sConfig.monitor_all_namespaces ? 'todos os namespaces' : `${k8sConfig.namespaces.length} namespace(s)`;
                    alert(`✔ Configuração Kubernetes concluída!\n\nCluster: ${k8sConfig.cluster_name}\nRecursos: ${k8sConfig.selected_resources.length} tipo(s)\nNamespaces: ${namespaceInfo}\n\nOs sensores serão criados na Biblioteca de Sensores Independentes com auto-discovery ativado.`);
                    setShowK8sWizard(false);
                    setK8sWizardStep(1);
                    // Redirecionar para biblioteca com Kubernetes pré-selecionado
                    window.location.hash = '#/sensor-library?type=kubernetes';
                  }
                }}
                disabled={k8sWizardStep === 4 && k8sConfig.selected_resources.length === 0}
                style={{
                  opacity: (k8sWizardStep === 4 && k8sConfig.selected_resources.length === 0) ? 0.5 : 1,
                  cursor: (k8sWizardStep === 4 && k8sConfig.selected_resources.length === 0) ? 'not-allowed' : 'pointer'
                }}
              >
                {k8sWizardStep === 4 ? '✔ Finalizar e Criar Sensores' : 'Próximo →'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Servers;

