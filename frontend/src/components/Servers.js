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
  const [newGroup, setNewGroup] = useState({
    name: '',
    parent_id: null,
    description: '',
    icon: '≡ƒôü',
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
    // Se tamb├⌐m foi passado um sensor espec├¡fico, destac├í-lo ap├│s os sensores serem carregados
    if (selectedSensorId && sensors.length > 0) {
      console.log('≡ƒÄ» Navegando para sensor ID:', selectedSensorId, 'Total sensores:', sensors.length);
      
      // Encontrar o sensor e expandir seu grupo
      const sensor = sensors.find(s => s.id === selectedSensorId);
      if (sensor) {
        console.log('Γ£à Sensor encontrado:', sensor.name, 'Tipo:', sensor.sensor_type);
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
          console.log('≡ƒôé Expandindo grupo:', groupKey);
          setExpandedSensorGroups(prev => ({
            ...prev,
            [groupKey]: true
          }));
        }
      } else {
        console.log('Γ¥î Sensor N├âO encontrado! ID procurado:', selectedSensorId);
      }
      
      setHighlightedSensorId(selectedSensorId);
      
      // Rolar at├⌐ o sensor ap├│s um delay maior para garantir que o grupo foi expandido
      setTimeout(() => {
        const sensorElement = document.getElementById(`sensor-${selectedSensorId}`);
        if (sensorElement) {
          console.log('≡ƒô£ Rolando at├⌐ o sensor');
          sensorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          
          // Remover destaque ap├│s 3 segundos
          setTimeout(() => {
            setHighlightedSensorId(null);
          }, 3000);
        } else {
          console.log('Γ¥î Elemento DOM n├úo encontrado: sensor-' + selectedSensorId);
        }
      }, 800);
    } else {
      if (selectedSensorId) {
        console.log('ΓÅ│ Aguardando sensores... ID:', selectedSensorId, 'Sensores:', sensors.length);
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
        icon: '≡ƒôü',
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
    if (!window.confirm(`Tem certeza que deseja excluir o grupo "${groupName}"?\n\nOs servidores/sensores deste grupo ficar├úo sem grupo.`)) {
      return;
    }

    try {
      await api.delete(`/sensor-groups/${groupId}`);
      loadServerGroups();
      alert('Grupo exclu├¡do com sucesso!');
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
        icon: '≡ƒôü',
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
          console.error('Erro ao carregar m├⌐tricas em batch:', err);
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
      case 'ping': return '≡ƒôí';
      case 'cpu': return '≡ƒûÑ∩╕Å';
      case 'memory': return '≡ƒÆ╛';
      case 'disk': return '≡ƒÆ┐';
      case 'network': return '≡ƒîÉ';
      case 'service': return 'ΓÜÖ∩╕Å';
      case 'system': return 'ΓÅ▒∩╕Å';
      case 'hyperv': return '≡ƒû╝∩╕Å';
      case 'udm': return '≡ƒôí';
      case 'docker': return '≡ƒÉ│';
      case 'snmp': return '≡ƒîÉ';
      case 'snmp_uptime': return 'ΓÅ▒∩╕Å';
      case 'snmp_cpu': return '≡ƒûÑ∩╕Å';
      case 'snmp_memory': return '≡ƒÆ╛';
      case 'snmp_traffic': return '≡ƒôè';
      case 'snmp_interface': return '≡ƒöî';
      default: return '≡ƒôè';
    }
  };

  // Fun├º├úo para agrupar sensores por tipo
  const groupSensorsByType = (sensors) => {
    const groups = {
      system: {
        name: 'Sistema',
        icon: '≡ƒûÑ∩╕Å',
        sensors: [],
        priority: 1,
        color: '#4caf50'
      },
      docker: {
        name: 'Docker',
        icon: '≡ƒÉ│',
        sensors: [],
        priority: 2,
        color: '#2196f3',
        showSummary: true
      },
      services: {
        name: 'Servi├ºos',
        icon: 'ΓÜÖ∩╕Å',
        sensors: [],
        priority: 3,
        color: '#ff9800'
      },
      applications: {
        name: 'Aplica├º├╡es',
        icon: '≡ƒôª',
        sensors: [],
        priority: 4,
        color: '#9c27b0'
      },
      network: {
        name: 'Rede',
        icon: '≡ƒîÉ',
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
      
      // Se est├í expandindo, colapsa todos os outros
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
      
      // Se est├í colapsando, apenas colapsa este
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
            <div className="summary-icon">≡ƒôª</div>
            <div className="summary-value">{totalMetric.value || 0}</div>
            <div className="summary-label">Total</div>
          </div>
        )}
        {runningMetric && (
          <div className="summary-card">
            <div className="summary-icon">Γ£à</div>
            <div className="summary-value">{runningMetric.value || 0}</div>
            <div className="summary-label">Rodando</div>
          </div>
        )}
        {stoppedMetric && (
          <div className="summary-card">
            <div className="summary-icon">ΓÅ╕∩╕Å</div>
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
          <div className="summary-icon">≡ƒôè</div>
          <div className="summary-value">{total}</div>
          <div className="summary-label">Total</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">Γ£à</div>
          <div className="summary-value">{ok}</div>
          <div className="summary-label">OK</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">ΓÜá∩╕Å</div>
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
          <div className="summary-icon">≡ƒôè</div>
          <div className="summary-value">{total}</div>
          <div className="summary-label">Total</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">Γ£à</div>
          <div className="summary-value">{running}</div>
          <div className="summary-label">Rodando</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">ΓÅ╕∩╕Å</div>
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
          <div className="summary-icon">≡ƒôª</div>
          <div className="summary-value">{total}</div>
          <div className="summary-label">Total</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">Γ£à</div>
          <div className="summary-value">{active}</div>
          <div className="summary-label">Ativas</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">ΓÅ╕∩╕Å</div>
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
          <div className="summary-icon">≡ƒîÉ</div>
          <div className="summary-value">{total}</div>
          <div className="summary-label">Total</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">Γ£à</div>
          <div className="summary-value">{online}</div>
          <div className="summary-label">Online</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">Γ¥î</div>
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
        title={hasNote ? `├Ültima nota: ${sensor.last_note}\n\nPor: ${sensor.last_note_by_name || 'T├⌐cnico'}\nEm: ${sensor.last_note_at ? new Date(sensor.last_note_at).toLocaleString('pt-BR') : ''}` : ''}
      >
        <div className="sensor-card-actions">
          <button 
            className="sensor-action-btn"
            onClick={(e) => handleViewSensorDetails(sensor, e)}
            title="Ver detalhes e an├ílise da IA"
          >
            ≡ƒöì
          </button>
          <button 
            className="sensor-action-btn"
            onClick={(e) => handleOpenMoveSensorModal(sensor, e)}
            title="Mover para outra categoria"
          >
            ≡ƒôü
          </button>
          <button 
            className="sensor-action-btn"
            onClick={(e) => {
              e.stopPropagation();
              handleEditSensor(sensor);
            }}
            title="Editar sensor"
          >
            Γ£Å∩╕Å
          </button>
          <button 
            className="sensor-delete-btn"
            onClick={(e) => {
              e.stopPropagation();
              handleDeleteSensor(sensor.id, sensor.name);
            }}
            title="Remover sensor"
          >
            ├ù
          </button>
        </div>
        
        {isAcknowledged && (
          <div className="sensor-acknowledged-badge" title="Verificado pela TI - Alertas suprimidos">
            Γ£ô Verificado pela TI
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
              {isAcknowledged ? 'EM AN├üLISE' : metric.status.toUpperCase()}
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
            <>ΓÜá∩╕Å {sensor.threshold_warning || 100}ms | ≡ƒöÑ {sensor.threshold_critical || 200}ms</>
          ) : sensor.sensor_type === 'network' ? (
            <>ΓÜá∩╕Å {sensor.threshold_warning || 80}MB/s | ≡ƒöÑ {sensor.threshold_critical || 95}MB/s</>
          ) : (
            <>ΓÜá∩╕Å {sensor.threshold_warning || 80}% | ≡ƒöÑ {sensor.threshold_critical || 95}%</>
          )}
        </div>
        
        {hasNote && (
          <div className="sensor-last-note">
            <span className="note-icon">≡ƒô¥</span>
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
                  {statusCounts.ok > 0 && <span className="status-badge status-ok">ΓùÅ {statusCounts.ok}</span>}
                  {statusCounts.warning > 0 && <span className="status-badge status-warning">ΓùÅ {statusCounts.warning}</span>}
                  {statusCounts.critical > 0 && <span className="status-badge status-critical">ΓùÅ {statusCounts.critical}</span>}
                </span>
                <span className="group-toggle">{isExpanded ? 'Γû╝' : 'Γû╢'}</span>
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
          {/* Header compacto - s├│ ├¡cone e contador */}
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
                {statusCounts.ok > 0 && <span className="status-badge ok">Γ£ô {statusCounts.ok}</span>}
                {statusCounts.warning > 0 && <span className="status-badge warning">ΓÜá {statusCounts.warning}</span>}
                {statusCounts.critical > 0 && <span className="status-badge critical">≡ƒöÑ {statusCounts.critical}</span>}
              </div>
            )}
            
            <span className="category-toggle">{isExpanded ? 'Γû▓' : 'Γû╝'}</span>
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
        console.log('Sensor n├úo encontrado no banco, tentando desativar...');
        try {
          await api.put(`/sensors/${sensorId}`, { is_active: false });
          console.log('Sensor desativado com sucesso');
          loadSensors(selectedServer.id);
          alert('Sensor n├úo p├┤de ser deletado, mas foi desativado. Ele n├úo aparecer├í mais no dashboard.');
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
          // Requisi├º├úo foi feita mas sem resposta
          errorMessage = 'Sem resposta do servidor. Verifique se a API est├í rodando.';
        } else {
          // Erro ao configurar requisi├º├úo
          errorMessage = error.message;
        }
        
        alert('Erro ao remover sensor: ' + errorMessage);
      }
    }
  };

  const handleDeleteServer = async (serverId, serverName, e) => {
    e.stopPropagation(); // Prevent server selection
    
    if (!window.confirm(`ΓÜá∩╕Å ATEN├ç├âO: Tem certeza que deseja remover o servidor "${serverName}"?\n\nIsso ir├í remover:\n- O servidor\n- Todos os sensores\n- Todas as m├⌐tricas\n- Todos os incidentes\n\nEsta a├º├úo N├âO pode ser desfeita!`)) {
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
      alert('Preencha todos os campos obrigat├│rios');
      return;
    }

    // VALIDA├ç├âO: Hostname n├úo pode ser um IP (requisito para Kerberos)
    const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (ipPattern.test(newServer.hostname)) {
      alert('Γ¥î ERRO: Hostname n├úo pode ser um endere├ºo IP!\n\n' +
            'ΓÜá∩╕Å Para autentica├º├úo Kerberos funcionar, voc├¬ DEVE usar:\n' +
            'Γ£à Hostname completo (FQDN): SRVHVSPRD010.ad.techbiz.com.br\n' +
            'Γ£à Hostname curto: SRVHVSPRD010\n\n' +
            'Γ¥î N├âO use IP no campo Hostname: ' + newServer.hostname + '\n\n' +
            'O IP deve ser preenchido no campo "Endere├ºo IP" separadamente.');
      return;
    }

    // Valida├º├úo adicional: hostname deve ter pelo menos 3 caracteres
    if (newServer.hostname.length < 3) {
      alert('Γ¥î Hostname muito curto. Use o nome completo do servidor (ex: SRVHVSPRD010)');
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
      alert('Servidor adicionado com sucesso! A probe come├ºar├í a monitor├í-lo automaticamente.');
    } catch (error) {
      console.error('Erro ao adicionar servidor:', error);
      alert('Erro ao adicionar servidor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleAddSensor = async (sensorData) => {
    if (!selectedServer || !sensorData || !sensorData.name) {
      alert('Preencha todos os campos obrigat├│rios');
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
      console.error('Erro ao carregar servi├ºos:', error);
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
      alert('O sensor j├í est├í nesta categoria');
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
      'memory': 'Sistema (Mem├│ria)',
      'disk': 'Sistema (Disco)',
      'system': 'Sistema (Uptime)',
      'network': 'Sistema (Rede)',
      'docker': 'Docker',
      'service': 'Servi├ºos',
      'hyperv': 'Aplica├º├╡es (Hyper-V)',
      'kubernetes': 'Aplica├º├╡es (Kubernetes)',
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
              {isExpanded ? '≡ƒôé' : '≡ƒôü'}
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
              Γåö∩╕Å
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
              ≡ƒùæ∩╕Å
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
    
    // Adicionar pastas vazias que foram criadas (est├úo em expandedGroups mas n├úo t├¬m servidores)
    Object.keys(expandedGroups).forEach(groupName => {
      if (!grouped[groupName] && groupName.includes(' / ')) {
        // ├ë uma subpasta criada manualmente
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
            Γÿü∩╕Å Monitorar Servi├ºos
          </button>
        </div>
      </div>

      <button 
        className="sidebar-toggle-btn"
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        title={sidebarCollapsed ? "Mostrar Servidores" : "Ocultar Servidores"}
      >
        {sidebarCollapsed ? 'Γÿ░' : 'Γ£ò'}
      </button>

      <div className={`servers-layout ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="servers-list">
          <div className="servers-list-header">
            <h2>Servidores ({servers.length})</h2>
            <div className="view-toggle">
              <button 
                className={viewMode === 'tree' ? 'active' : ''}
                onClick={() => setViewMode('tree')}
                title="Visualiza├º├úo em ├ürvore"
              >
                ≡ƒî│
              </button>
              <button 
                className={viewMode === 'list' ? 'active' : ''}
                onClick={() => setViewMode('list')}
                title="Visualiza├º├úo em Lista"
              >
                ≡ƒôï
              </button>
            </div>
          </div>

          {/* Se├º├úo de Grupos Hier├írquicos - Colaps├ível */}
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
              <span>ΓÜÖ∩╕Å Gerenciar Grupos {serverGroups.length > 0 && `(${serverGroups.length})`}</span>
              <span style={{ fontSize: '10px' }}>{showGroupsSection ? 'Γû▓' : 'Γû╝'}</span>
            </button>

            {showGroupsSection && (
              <div style={{ background: '#fafafa' }}>
                {/* Bot├╡es de A├º├úo */}
                <div style={{ padding: '10px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => {
                      setNewGroup({
                        name: '',
                        parent_id: null,
                        description: '',
                        icon: '≡ƒôü',
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
                    Γ₧ò Grupo
                  </button>
                  {selectedGroup && (
                    <>
                      <button
                        onClick={() => {
                          setNewGroup({
                            name: '',
                            parent_id: selectedGroup.id,
                            description: '',
                            icon: '≡ƒôü',
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
                        Γ₧ò Subgrupo
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
                        Γ£ò
                      </button>
                    </>
                  )}
                </div>

                {/* ├ürvore de Grupos */}
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
                        {expandedGroups[groupName] ? '≡ƒôé' : '≡ƒôü'}
                      </span>
                      <span className="tree-label">{groupName}</span>
                      <span className="tree-count">({groupServers.length})</span>
                    </div>
                    <div style={{ display: 'flex', gap: '4px', marginLeft: '8px' }} onClick={(e) => e.stopPropagation()}>
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
                        Γ£Å∩╕Å
                      </button>
                      <button
                        className="btn-edit-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          const subfolderName = prompt(`Criar subpasta dentro de "${groupName}":`);
                          if (subfolderName) {
                            // Criar nome hier├írquico: "Pai / Filho"
                            const newGroupName = `${groupName} / ${subfolderName}`;
                            
                            // Perguntar se quer mover um servidor existente ou criar novo
                            const action = window.confirm(
                              `Subpasta "${newGroupName}" ser├í criada.\n\n` +
                              `Clique OK para mover um servidor existente para esta pasta.\n` +
                              `Clique CANCELAR para criar a pasta vazia (voc├¬ poder├í adicionar servidores depois).`
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
                                `1. Clique em Γ£Å∩╕Å em um servidor\n` +
                                `2. No campo "Grupo / Empresa", digite: ${newGroupName}\n` +
                                `3. Salve`
                              );
                            }
                          }
                        }}
                        title="Criar subpasta"
                        style={{ padding: '2px 6px', fontSize: '11px', background: '#4caf50', color: 'white' }}
                      >
                        Γ₧ò
                      </button>
                      <button
                        className="btn-delete-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (window.confirm(`Excluir pasta "${groupName}"?\n\nOs ${groupServers.length} servidor(es) ficar├úo sem pasta.`)) {
                            Promise.all(
                              groupServers.map(server => 
                                api.put(`/servers/${server.id}`, { group_name: null })
                              )
                            ).then(() => {
                              loadServers();
                              alert('Pasta exclu├¡da com sucesso!');
                            }).catch(err => {
                              console.error('Erro ao excluir pasta:', err);
                              alert('Erro ao excluir pasta');
                            });
                          }
                        }}
                        title="Excluir pasta"
                        style={{ padding: '2px 6px', fontSize: '11px' }}
                      >
                        ≡ƒùæ∩╕Å
                      </button>
                    </div>
                  </div>
                  {expandedGroups[groupName] && (
                    <div className="tree-group-content">
                      {groupServers.length > 0 ? (
                        groupServers.map(server => (
                          <div
                            key={server.id}
                            className={`tree-server ${selectedServer?.id === server.id ? 'selected' : ''}`}
                            onClick={() => setSelectedServer(server)}
                          >
                            <div className="server-info">
                              <h3>{server.hostname}</h3>
                              <p>{server.ip_address || 'IP n├úo dispon├¡vel'}</p>
                              {server.public_ip && <p className="public-ip">≡ƒîÉ {server.public_ip}</p>}
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
                                Γ£Å∩╕Å
                              </button>
                              <button 
                                className="btn-delete-small"
                                onClick={(e) => handleDeleteServer(server.id, server.hostname, e)}
                                title="Excluir servidor"
                              >
                                ≡ƒùæ∩╕Å
                              </button>
                              <div className={`server-status ${server.is_active ? 'active' : 'inactive'}`}>
                              {server.is_active ? 'ΓùÅ' : 'Γùï'}
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
                          ≡ƒô¡ Pasta vazia
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
                    <p>{server.ip_address || 'IP n├úo dispon├¡vel'}</p>
                    {server.public_ip && <p className="public-ip">≡ƒîÉ {server.public_ip}</p>}
                    <p className="server-os">{server.os_type} {server.os_version}</p>
                    {server.group_name && <p className="server-group">≡ƒôü {server.group_name}</p>}
                  </div>
                  <div className="server-actions">
                    <button 
                      className="btn-edit-small"
                      onClick={(e) => handleEditServer(server, e)}
                      title="Editar servidor"
                    >
                      Γ£Å∩╕Å
                    </button>
                    <button 
                      className="btn-delete-small"
                      onClick={(e) => handleDeleteServer(server.id, server.hostname, e)}
                      title="Excluir servidor"
                    >
                      ≡ƒùæ∩╕Å
                    </button>
                    <div className={`server-status ${server.is_active ? 'active' : 'inactive'}`}>
                      {server.is_active ? 'ΓùÅ' : 'Γùï'}
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
                      if (window.confirm('Deseja corrigir automaticamente as categorias de todos os sensores baseado no nome?\n\nExemplo: Sensores com "Docker" no nome ser├úo movidos para categoria Docker.')) {
                        try {
                          const response = await api.post('/sensors/fix-categories');
                          alert(`Γ£à Corre├º├úo conclu├¡da!\n\nTotal: ${response.data.total_sensors} sensores\nCorrigidos: ${response.data.fixed_count} sensores\n\nRecarregando...`);
                          loadSensors(selectedServer.id);
                        } catch (error) {
                          console.error('Erro ao corrigir categorias:', error);
                          alert('Erro ao corrigir categorias: ' + (error.response?.data?.detail || error.message));
                        }
                      }
                    }}
                    style={{ background: '#ff9800' }}
                  >
                    ≡ƒöº Corrigir Categorias
                  </button>
                  <button className="btn-add" onClick={handleOpenAddSensorModal}>
                    + Adicionar Sensor
                  </button>
                </div>
              </div>
              <div className="info-banner">
                <p>Γä╣∩╕Å <strong>Sensores Padr├úo:</strong> Ping, CPU, Mem├│ria, Disco, Uptime, Network IN, Network OUT</p>
                <p>Os sensores padr├úo s├úo criados automaticamente. Use "Adicionar Sensor" para monitorar servi├ºos Windows, discos adicionais ou criar sensores customizados.</p>
              </div>
              {renderMixedSensors()}
              {sensors.length === 0 && (
                <div className="no-data">
                  <p>Nenhum sensor configurado para este servidor</p>
                  <p>Os sensores padr├úo s├úo criados automaticamente. Clique em "Adicionar Sensor" para monitorar servi├ºos ou discos adicionais.</p>
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
                <label>Probe Respons├ível: *</label>
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
                <small>A probe que ir├í monitorar este dispositivo</small>
              </div>

              <div className="form-group">
                <label>Tipo de Dispositivo: *</label>
                <select
                  value={newServer.device_type}
                  onChange={(e) => setNewServer({...newServer, device_type: e.target.value})}
                >
                  <option value="server">≡ƒûÑ∩╕Å Servidor</option>
                  <option value="switch">≡ƒöÇ Switch</option>
                  <option value="router">≡ƒôí Roteador</option>
                  <option value="firewall">≡ƒöÑ Firewall</option>
                  <option value="printer">≡ƒû¿∩╕Å Impressora</option>
                  <option value="storage">≡ƒÆ╛ Storage</option>
                  <option value="ups">≡ƒöï Nobreak</option>
                  <option value="other">≡ƒôª Outro</option>
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
                <label>Endere├ºo IP: *</label>
                <input
                  type="text"
                  value={newServer.ip_address}
                  onChange={(e) => setNewServer({...newServer, ip_address: e.target.value})}
                  required
                  placeholder="Ex: 192.168.1.100"
                />
                <small>Endere├ºo IP do dispositivo na rede local</small>
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
                  placeholder="Ex: Empresa A, Datacenter SP, Produ├º├úo"
                  value={newServer.newGroupInput || ''}
                  onChange={(e) => setNewServer({...newServer, newGroupInput: e.target.value, group_name: e.target.value})}
                />
                <small>Digite um novo nome de grupo para criar</small>
              </div>
            </div>

            <div className="form-section">
              <h3>ΓÜÖ∩╕Å Protocolo de Monitoramento</h3>
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
                    <label>Vers├úo SNMP:</label>
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
                    <small>Porta padr├úo: 161</small>
                  </div>
                </div>
              )}
            </div>

            <div className="form-section">
              <h3>≡ƒÅ╖∩╕Å Classifica├º├úo de Ambiente</h3>
              <div className="form-group">
                <label>Ambiente: *</label>
                <select
                  value={newServer.environment}
                  onChange={(e) => setNewServer({...newServer, environment: e.target.value})}
                >
                  <option value="production">≡ƒö┤ Produ├º├úo (24x7 - Liga├º├╡es em caso de queda)</option>
                  <option value="staging">≡ƒƒí Homologa├º├úo (Hor├írio comercial 08-18h)</option>
                  <option value="development">≡ƒƒó Desenvolvimento (Hor├írio comercial 08-18h)</option>
                  <option value="custom">ΓÜÖ∩╕Å Personalizado (Definir hor├írios)</option>
                </select>
                <small>Define quando o sistema enviar├í notifica├º├╡es e liga├º├╡es</small>
              </div>

              {newServer.environment === 'custom' && (
                <div className="custom-schedule-info">
                  <p>Γä╣∩╕Å <strong>Hor├írio Personalizado:</strong></p>
                  <p>Voc├¬ poder├í configurar hor├írios espec├¡ficos ap├│s criar o servidor.</p>
                </div>
              )}
            </div>

            <div className="info-box">
              <p>Γä╣∩╕Å <strong>Importante:</strong></p>
              <ul>
                <li>O dispositivo deve estar acess├¡vel pela probe selecionada</li>
                <li><strong>WMI:</strong> Certifique-se que o firewall permite conex├╡es WMI/RPC</li>
                <li><strong>SNMP:</strong> Verifique se o SNMP est├í habilitado no dispositivo</li>
                <li><strong>Produ├º├úo:</strong> Sistema ligar├í 24x7 em caso de problemas cr├¡ticos</li>
                <li><strong>Homologa├º├úo/Dev:</strong> Notifica├º├╡es apenas em hor├írio comercial</li>
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
                placeholder="Ex: Empresa A, Datacenter SP, Produ├º├úo"
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
              <label>Tags (separadas por v├¡rgula):</label>
              <input
                type="text"
                placeholder="Ex: cr├¡tico, produ├º├úo, web-server"
                value={editingServer.tags ? editingServer.tags.join(', ') : ''}
                onChange={(e) => setEditingServer({
                  ...editingServer, 
                  tags: e.target.value.split(',').map(t => t.trim()).filter(t => t)
                })}
              />
              <small>Use tags para classificar por criticidade, fun├º├úo, etc</small>
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
              <small>Personalize o nome do sensor para facilitar identifica├º├úo</small>
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
                {editingSensor.sensor_type === 'ping' ? 'Alerta amarelo quando lat├¬ncia ultrapassar este valor' :
                 editingSensor.sensor_type === 'network' ? 'Alerta amarelo quando tr├ífego ultrapassar este valor' :
                 'Alerta amarelo quando ultrapassar este valor'}
              </small>
            </div>
            <div className="form-group">
              <label>
                Limite Cr├¡tico 
                {editingSensor.sensor_type === 'ping' ? ' (ms)' : 
                 editingSensor.sensor_type === 'network' ? ' (MB/s)' : ' (%)'}:
              </label>
              <input
                type="number"
                value={editingSensor.threshold_critical}
                onChange={(e) => setEditingSensor({...editingSensor, threshold_critical: e.target.value})}
              />
              <small>
                {editingSensor.sensor_type === 'ping' ? 'Alerta vermelho quando lat├¬ncia ultrapassar este valor' :
                 editingSensor.sensor_type === 'network' ? 'Alerta vermelho quando tr├ífego ultrapassar este valor' :
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
            <h2>≡ƒôü Mover Sensor para Outra Categoria</h2>
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
                  <option value="ping">≡ƒôí Ping</option>
                  <option value="cpu">≡ƒûÑ∩╕Å CPU</option>
                  <option value="memory">≡ƒÆ╛ Mem├│ria</option>
                  <option value="disk">≡ƒÆ┐ Disco</option>
                  <option value="system">ΓÅ▒∩╕Å Uptime</option>
                  <option value="network">≡ƒîÉ Rede</option>
                </optgroup>
                <optgroup label="Docker">
                  <option value="docker">≡ƒÉ│ Docker</option>
                </optgroup>
                <optgroup label="Servi├ºos">
                  <option value="service">ΓÜÖ∩╕Å Servi├ºo Windows</option>
                </optgroup>
                <optgroup label="Aplica├º├╡es">
                  <option value="hyperv">≡ƒû╝∩╕Å Hyper-V</option>
                  <option value="kubernetes">Γÿ╕∩╕Å Kubernetes</option>
                </optgroup>
                <optgroup label="Rede">
                  <option value="http">≡ƒîÉ HTTP</option>
                  <option value="port">≡ƒöî Porta</option>
                  <option value="dns">≡ƒöì DNS</option>
                  <option value="ssl">≡ƒöÆ SSL</option>
                  <option value="snmp">≡ƒôè SNMP</option>
                </optgroup>
              </select>
              <small>O sensor ser├í movido para a categoria selecionada e aparecer├í no card correspondente</small>
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
              <h2>≡ƒöì Detalhes do Sensor: {selectedSensorDetails.name}</h2>
              <button className="btn-close" onClick={() => setShowSensorDetailsModal(false)}>├ù</button>
            </div>

            <div className="sensor-details-content">
              {/* AI Analysis Section */}
              <div className="ai-analysis-section">
                <h3>≡ƒñû An├ílise da IA</h3>
                {loadingAnalysis ? (
                  <div className="loading-analysis">Analisando sensor...</div>
                ) : aiAnalysis ? (
                  <div className="ai-analysis-content">
                    <div className="root-cause">
                      <h4>Causa Raiz:</h4>
                      <p>{aiAnalysis.root_cause}</p>
                      <div className="confidence-badge">
                        Confian├ºa: {(aiAnalysis.confidence * 100).toFixed(0)}%
                      </div>
                    </div>

                    <div className="evidence">
                      <h4>Evid├¬ncias:</h4>
                      <ul>
                        {aiAnalysis.evidence.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="suggested-actions">
                      <h4>≡ƒÆí A├º├╡es Sugeridas:</h4>
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
                        <strong>Auto-remedia├º├úo dispon├¡vel:</strong> 
                        {aiAnalysis.auto_remediation_available ? ' Γ£à Sim' : ' Γ¥î N├úo'}
                      </div>
                      <div className="info-item">
                        <strong>Tempo estimado de resolu├º├úo:</strong> {aiAnalysis.estimated_resolution_time}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="no-analysis">An├ílise n├úo dispon├¡vel</div>
                )}
              </div>

              {/* Technician Notes Section */}
              <div className="technician-notes-section">
                <h3>≡ƒô¥ Notas do T├⌐cnico</h3>
                
                <div className="add-note-form">
                  <div className="form-group">
                    <label>Status de Verifica├º├úo:</label>
                    <select 
                      value={newNote.status}
                      onChange={(e) => setNewNote({...newNote, status: e.target.value})}
                    >
                      <option value="pending">ΓÅ│ Pendente</option>
                      <option value="in_analysis">≡ƒöì Em An├ílise</option>
                      <option value="verified">Γ£à Verificado</option>
                      <option value="resolved">≡ƒÄë Resolvido</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Nota:</label>
                    <textarea
                      value={newNote.note}
                      onChange={(e) => setNewNote({...newNote, note: e.target.value})}
                      placeholder="Descreva as a├º├╡es tomadas, observa├º├╡es ou pr├│ximos passos..."
                      rows="4"
                    />
                  </div>
                  <button className="btn-primary" onClick={handleAddNote}>
                    Adicionar Nota
                  </button>
                </div>

                <div className="notes-history">
                  <h4>Hist├│rico de Notas:</h4>
                  {sensorNotes.length > 0 ? (
                    <div className="notes-list">
                      {sensorNotes.map(note => (
                        <div key={note.id} className="note-card">
                          <div className="note-header">
                            <span className="note-author">{note.user_name || 'Usu├írio'}</span>
                            <span className="note-date">
                              {new Date(note.created_at).toLocaleString('pt-BR')}
                            </span>
                          </div>
                          <div className="note-status">
                            Status: {
                              note.status === 'pending' ? 'ΓÅ│ Pendente' :
                              note.status === 'in_analysis' ? '≡ƒöì Em An├ílise' :
                              note.status === 'verified' ? 'Γ£à Verificado' :
                              '≡ƒÄë Resolvido'
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
              <h2>{newGroup.parent_id ? 'Γ₧ò Criar Subgrupo' : 'Γ₧ò Criar Grupo Raiz'}</h2>
              <button className="modal-close" onClick={() => setShowCreateGroupModal(false)}>├ù</button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Nome do Grupo: *</label>
                <input
                  type="text"
                  value={newGroup.name}
                  onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                  placeholder="Ex: Produ├º├úo, Datacenter SP, Clientes"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Descri├º├úo:</label>
                <textarea
                  value={newGroup.description}
                  onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
                  placeholder="Descri├º├úo opcional do grupo"
                  rows="3"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>├ìcone:</label>
                  <select
                    value={newGroup.icon}
                    onChange={(e) => setNewGroup({...newGroup, icon: e.target.value})}
                  >
                    <option value="≡ƒôü">≡ƒôü Pasta</option>
                    <option value="≡ƒÅó">≡ƒÅó Empresa</option>
                    <option value="≡ƒÅ¡">≡ƒÅ¡ F├íbrica</option>
                    <option value="≡ƒÅ¬">≡ƒÅ¬ Loja</option>
                    <option value="≡ƒÅÑ">≡ƒÅÑ Hospital</option>
                    <option value="≡ƒÅ½">≡ƒÅ½ Escola</option>
                    <option value="≡ƒîÉ">≡ƒîÉ Rede</option>
                    <option value="Γÿü∩╕Å">Γÿü∩╕Å Nuvem</option>
                    <option value="≡ƒûÑ∩╕Å">≡ƒûÑ∩╕Å Servidores</option>
                    <option value="≡ƒôè">≡ƒôè Monitoramento</option>
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
                  <p>Γä╣∩╕Å Este ser├í um subgrupo dentro de: <strong>{serverGroups.find(g => g.id === newGroup.parent_id)?.name}</strong></p>
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
              <h2>Γåö∩╕Å Mover Grupo</h2>
              <button className="modal-close" onClick={() => setShowMoveGroupModal(false)}>├ù</button>
            </div>

            <div className="modal-body">
              <div className="info-banner" style={{ marginBottom: '20px' }}>
                <p><strong>Grupo:</strong> {selectedGroup.icon} {selectedGroup.name}</p>
                <p><strong>Posi├º├úo Atual:</strong> {selectedGroup.parent_id ? 'Subgrupo' : 'Raiz'}</p>
              </div>

              <div className="form-group">
                <label>Mover para:</label>
                <select
                  value={newGroup.parent_id || ''}
                  onChange={(e) => setNewGroup({...newGroup, parent_id: e.target.value ? parseInt(e.target.value) : null})}
                >
                  <option value="">≡ƒôü Raiz (sem pai)</option>
                  {serverGroups
                    .filter(g => g.id !== selectedGroup.id) // N├úo pode mover para si mesmo
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

      {/* Modal Monitorar Servi├ºos */}
      {showMonitorServicesModal && (
        <div className="modal-overlay" onClick={() => setShowMonitorServicesModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '900px', maxHeight: '90vh', overflow: 'auto' }}>
            <div className="modal-header">
              <h2>Γÿü∩╕Å Monitorar Servi├ºos e Dispositivos</h2>
              <button className="modal-close" onClick={() => setShowMonitorServicesModal(false)}>├ù</button>
            </div>

            <div className="modal-body">
              <p style={{ marginBottom: '20px', color: '#666', fontSize: '15px' }}>
                Escolha o tipo de dispositivo ou servi├ºo que deseja monitorar. Todos abrem na Biblioteca de Sensores Independentes.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '15px' }}>
                {/* SNMP Gen├⌐rico */}
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>≡ƒôí</div>
                  <div>SNMP Gen├⌐rico</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>≡ƒô╢</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>Γÿü∩╕Å</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>≡ƒîí∩╕Å</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>≡ƒîÉ</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>≡ƒÆ╛</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>≡ƒùä∩╕Å</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>≡ƒû¿∩╕Å</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>≡ƒöï</div>
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
                  <div style={{ fontSize: '28px', marginBottom: '8px' }}>Γÿ╕∩╕Å</div>
                  <div>Kubernetes</div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '5px', fontWeight: 'normal' }}>
                    Clusters, Pods, Deployments
                  </div>
                </button>
              </div>

              <div className="info-banner" style={{ marginTop: '20px' }}>
                <p>≡ƒÆí <strong>Dica:</strong> Todos os tipos abrem na Biblioteca de Sensores Independentes com o tipo pr├⌐-selecionado para facilitar a configura├º├úo.</p>
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
              <h2>Γÿü∩╕Å Configurar Monitoramento Azure - Passo {azureWizardStep} de 4</h2>
              <button className="modal-close" onClick={() => setShowAzureWizard(false)}>├ù</button>
            </div>

            <div className="modal-body">
              {/* Passo 1: Requisitos e Instru├º├╡es */}
              {azureWizardStep === 1 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#0078d4' }}>≡ƒôï Requisitos para Monitoramento Azure</h3>
                  
                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      <strong>Γä╣∩╕Å Baseado nas melhores pr├íticas do PRTG, SolarWinds e Zabbix</strong><br/>
                      Para monitorar recursos Azure, voc├¬ precisa criar um Service Principal (App Registration) com permiss├╡es adequadas.
                    </p>
                  </div>

                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0, color: '#333' }}>≡ƒöÉ Passo a Passo - Azure Portal</h4>
                    <ol style={{ lineHeight: '1.8', fontSize: '14px', paddingLeft: '20px' }}>
                      <li>
                        <strong>Acesse o Azure Portal:</strong> <a href="https://portal.azure.com" target="_blank" rel="noopener noreferrer">portal.azure.com</a>
                      </li>
                      <li>
                        <strong>Criar App Registration:</strong>
                        <ul style={{ marginTop: '8px' }}>
                          <li>V├í em <code>Azure Active Directory</code> ΓåÆ <code>App registrations</code></li>
                          <li>Clique em <code>+ New registration</code></li>
                          <li>Nome: "Coruja Monitor" (ou nome de sua prefer├¬ncia)</li>
                          <li>Supported account types: "Single tenant"</li>
                          <li>Redirect URI: Deixe em branco</li>
                          <li>Clique em <code>Register</code></li>
                        </ul>
                      </li>
                      <li>
                        <strong>Copiar IDs necess├írios:</strong>
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
                          <li><strong>ΓÜá∩╕Å IMPORTANTE:</strong> Copie o <strong>Value</strong> imediatamente (n├úo ser├í mostrado novamente!)</li>
                        </ul>
                      </li>
                      <li>
                        <strong>Obter Subscription ID:</strong>
                        <ul style={{ marginTop: '8px' }}>
                          <li>V├í em <code>Subscriptions</code> no menu principal</li>
                          <li>Copie o <strong>Subscription ID</strong> da assinatura que deseja monitorar</li>
                        </ul>
                      </li>
                      <li>
                        <strong>Atribuir Permiss├╡es (CR├ìTICO):</strong>
                        <ul style={{ marginTop: '8px' }}>
                          <li>V├í em <code>Subscriptions</code> ΓåÆ Selecione sua assinatura</li>
                          <li>Clique em <code>Access control (IAM)</code></li>
                          <li>Clique em <code>+ Add</code> ΓåÆ <code>Add role assignment</code></li>
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
                      <strong>ΓÜá∩╕Å Seguran├ºa:</strong> O role "Monitoring Reader" fornece acesso somente leitura ├ás m├⌐tricas.
                      Nunca use roles com permiss├╡es de escrita (Contributor, Owner) para monitoramento.
                    </p>
                  </div>

                  <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', border: '1px solid #4caf50' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>Γ£à Recursos que podem ser monitorados:</strong><br/>
                      Virtual Machines, Storage Accounts, SQL Databases, Web Apps, Function Apps, AKS Clusters, 
                      Load Balancers, Application Gateways, Cosmos DB, Redis Cache, Service Bus, Event Hubs, Key Vaults, Backups
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 2: Inserir Credenciais */}
              {azureWizardStep === 2 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#0078d4' }}>≡ƒöæ Credenciais Azure</h3>
                  
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
                    <small>ID do diret├│rio (Azure Active Directory)</small>
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
                    <small>ID da aplica├º├úo registrada (App Registration)</small>
                  </div>

                  <div className="form-group">
                    <label>Client Secret: *</label>
                    <input
                      type="password"
                      value={azureConfig.client_secret}
                      onChange={(e) => setAzureConfig({...azureConfig, client_secret: e.target.value})}
                      placeholder="ΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇó"
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
                      ≡ƒÆí <strong>Dica:</strong> Todos os campos marcados com * s├úo obrigat├│rios. 
                      Certifique-se de que o Service Principal tem o role "Monitoring Reader" atribu├¡do.
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 3: Testar Conex├úo */}
              {azureWizardStep === 3 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#0078d4' }}>≡ƒöî Testar Conex├úo Azure</h3>
                  
                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Credenciais Configuradas:</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold', width: '180px' }}>Subscription ID:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{azureConfig.subscription_id || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Tenant ID:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{azureConfig.tenant_id || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Client ID:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{azureConfig.client_id || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Client Secret:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{'ΓÇó'.repeat(32)}</td>
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
                      alert('≡ƒöî Teste de conex├úo Azure ser├í implementado no backend.\n\nVerificar├í:\nΓ£ô Autentica├º├úo com Azure AD\nΓ£ô Permiss├╡es do Service Principal\nΓ£ô Acesso ├á Subscription\nΓ£ô Listagem de recursos dispon├¡veis');
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
                    ≡ƒöî Testar Conex├úo com Azure
                  </button>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>ΓÜá∩╕Å Poss├¡veis erros:</strong><br/>
                      ΓÇó <strong>401 Unauthorized:</strong> Client Secret inv├ílido ou expirado<br/>
                      ΓÇó <strong>403 Forbidden:</strong> Service Principal sem permiss├╡es adequadas<br/>
                      ΓÇó <strong>404 Not Found:</strong> Subscription ID incorreto<br/>
                      ΓÇó <strong>Timeout:</strong> Firewall bloqueando acesso ao Azure
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 4: Selecionar Recursos */}
              {azureWizardStep === 4 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#0078d4' }}>≡ƒôª Selecionar Recursos para Monitorar</h3>
                  
                  <div className="info-banner" style={{ background: '#e8f5e9', border: '1px solid #4caf50', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      Γ£à Conex├úo estabelecida com sucesso! Selecione os recursos Azure que deseja monitorar.
                    </p>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '20px' }}>
                    {[
                      { type: 'vm', icon: '≡ƒûÑ∩╕Å', name: 'Virtual Machines' },
                      { type: 'webapp', icon: '≡ƒîÉ', name: 'Web Apps' },
                      { type: 'sql', icon: '≡ƒùä∩╕Å', name: 'SQL Databases' },
                      { type: 'storage', icon: '≡ƒÆ╛', name: 'Storage Accounts' },
                      { type: 'aks', icon: 'Γÿ╕∩╕Å', name: 'AKS Clusters' },
                      { type: 'function', icon: 'ΓÜí', name: 'Azure Functions' },
                      { type: 'backup', icon: '≡ƒÆ╝', name: 'Backup Vaults' },
                      { type: 'loadbalancer', icon: 'ΓÜû∩╕Å', name: 'Load Balancers' }
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
                          <div style={{ marginTop: '5px', fontSize: '16px' }}>Γ£ô</div>
                        )}
                      </button>
                    ))}
                  </div>

                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      ≡ƒÆí Selecionados: <strong>{azureConfig.selected_resources.length}</strong> tipo(s) de recurso.
                      Sensores ser├úo criados automaticamente para cada recurso encontrado.
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
                {azureWizardStep === 1 ? 'Cancelar' : 'ΓåÉ Voltar'}
              </button>
              
              <button 
                className="btn-primary" 
                onClick={() => {
                  if (azureWizardStep < 4) {
                    // Validar campos obrigat├│rios no passo 2
                    if (azureWizardStep === 2) {
                      if (!azureConfig.subscription_id || !azureConfig.tenant_id || 
                          !azureConfig.client_id || !azureConfig.client_secret) {
                        alert('ΓÜá∩╕Å Preencha todos os campos obrigat├│rios antes de continuar.');
                        return;
                      }
                    }
                    setAzureWizardStep(azureWizardStep + 1);
                  } else {
                    // Finalizar e criar sensores
                    alert(`Γ£à Configura├º├úo Azure conclu├¡da!\n\n${azureConfig.selected_resources.length} tipo(s) de recurso selecionado(s).\n\nOs sensores ser├úo criados na Biblioteca de Sensores Independentes.`);
                    setShowAzureWizard(false);
                    setAzureWizardStep(1);
                    // Redirecionar para biblioteca com Azure pr├⌐-selecionado
                    window.location.hash = '#/sensor-library?type=azure';
                  }
                }}
                disabled={azureWizardStep === 4 && azureConfig.selected_resources.length === 0}
                style={{
                  opacity: (azureWizardStep === 4 && azureConfig.selected_resources.length === 0) ? 0.5 : 1,
                  cursor: (azureWizardStep === 4 && azureConfig.selected_resources.length === 0) ? 'not-allowed' : 'pointer'
                }}
              >
                {azureWizardStep === 4 ? 'Γ£ô Finalizar e Criar Sensores' : 'Pr├│ximo ΓåÆ'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Wizard SNMP Gen├⌐rico - Adapt├ível para v├írios tipos */}
      {showSNMPWizard && (
        <div className="modal-overlay" onClick={() => setShowSNMPWizard(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h2>
                {currentWizardType === 'snmp' && '≡ƒôí Configurar SNMP Gen├⌐rico'}
                {currentWizardType === 'ap' && '≡ƒô╢ Configurar Access Point'}
                {currentWizardType === 'temp' && '≡ƒîí∩╕Å Configurar Sensor de Temperatura'}
                {currentWizardType === 'storage' && '≡ƒÆ╛ Configurar Storage/NAS'}
                {currentWizardType === 'printer' && '≡ƒû¿∩╕Å Configurar Impressora'}
                {currentWizardType === 'ups' && '≡ƒöï Configurar UPS/Nobreak'}
                {' - Passo '}{snmpWizardStep} de 3
              </h2>
              <button className="modal-close" onClick={() => setShowSNMPWizard(false)}>├ù</button>
            </div>

            <div className="modal-body">
              {/* Passo 1: Requisitos */}
              {snmpWizardStep === 1 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#667eea' }}>≡ƒôï Requisitos SNMP</h3>
                  
                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      <strong>Γä╣∩╕Å Baseado em PRTG, SolarWinds, CheckMK e Zabbix</strong><br/>
                      SNMP (Simple Network Management Protocol) permite monitorar dispositivos de rede remotamente.
                    </p>
                  </div>

                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>≡ƒöº Configura├º├úo no Dispositivo:</h4>
                    <ol style={{ lineHeight: '1.8', fontSize: '14px', paddingLeft: '20px' }}>
                      <li><strong>Habilitar SNMP</strong> no dispositivo (v1, v2c ou v3)</li>
                      <li><strong>Configurar Community String</strong> (padr├úo: "public" para leitura)</li>
                      <li><strong>Porta SNMP</strong>: 161/UDP (padr├úo)</li>
                      <li><strong>Permitir acesso</strong> do IP da probe no firewall</li>
                    </ol>

                    {currentWizardType === 'ap' && (
                      <div style={{ marginTop: '15px', padding: '12px', background: '#fff3cd', borderRadius: '6px' }}>
                        <strong>≡ƒô╢ Access Points WiFi - M├⌐tricas Detalhadas:</strong>
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
                              <li>CPU % e Mem├│ria %</li>
                              <li>N├║mero de clientes conectados (2.4GHz + 5GHz)</li>
                              <li>Capacidade m├íxima vs atual</li>
                            </ul>
                          </div>
                          <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#2196f3' }}>3. Tr├ífego:</strong>
                            <ul style={{ marginTop: '4px', fontSize: '12px', marginLeft: '20px' }}>
                              <li>TX/RX bytes e pacotes por interface</li>
                              <li>Erros, Drops, Retransmiss├╡es</li>
                              <li>Throughput em Mbps</li>
                            </ul>
                          </div>
                          <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#2196f3' }}>4. Sinais:</strong>
                            <ul style={{ marginTop: '4px', fontSize: '12px', marginLeft: '20px' }}>
                              <li>RSSI m├⌐dio (dBm) - for├ºa do sinal</li>
                              <li>SNR (Signal-to-Noise Ratio)</li>
                              <li>Qualidade do sinal (%)</li>
                              <li>Interfer├¬ncia e ru├¡do</li>
                            </ul>
                          </div>
                          <div style={{ marginBottom: '8px' }}>
                            <strong style={{ color: '#2196f3' }}>5. Acesso:</strong>
                            <ul style={{ marginTop: '4px', fontSize: '12px', marginLeft: '20px' }}>
                              <li>SSIDs ativos e seus status</li>
                              <li>Autentica├º├╡es bem-sucedidas/falhadas</li>
                              <li>Associa├º├╡es e desassocia├º├╡es</li>
                              <li>Eventos de roaming</li>
                            </ul>
                          </div>
                        </div>
                        <div style={{ marginTop: '12px', padding: '8px', background: '#e3f2fd', borderRadius: '4px' }}>
                          <strong>≡ƒöº Configura├º├úo por Fabricante:</strong>
                          <ul style={{ marginTop: '5px', fontSize: '12px' }}>
                            <li><strong>Ubiquiti UniFi:</strong> Settings ΓåÆ Services ΓåÆ SNMP ΓåÆ Enable</li>
                            <li><strong>MikroTik:</strong> IP ΓåÆ SNMP ΓåÆ Communities ΓåÆ Add</li>
                            <li><strong>Cisco Aironet:</strong> configure terminal ΓåÆ snmp-server community public RO</li>
                            <li><strong>TP-Link EAP:</strong> Management ΓåÆ SNMP Settings ΓåÆ Enable v2c</li>
                            <li><strong>Aruba:</strong> Configuration ΓåÆ System ΓåÆ SNMP</li>
                          </ul>
                        </div>
                      </div>
                    )}

                    {currentWizardType === 'printer' && (
                      <div style={{ marginTop: '15px', padding: '12px', background: '#fff3cd', borderRadius: '6px' }}>
                        <strong>≡ƒû¿∩╕Å Impressoras:</strong>
                        <ul style={{ marginTop: '8px', fontSize: '13px' }}>
                          <li>HP: Menu ΓåÆ Network ΓåÆ SNMP ΓåÆ Enable</li>
                          <li>Canon: Setup ΓåÆ Network ΓåÆ SNMP Settings</li>
                          <li>Epson: Network ΓåÆ SNMP ΓåÆ Enable</li>
                        </ul>
                      </div>
                    )}

                    {currentWizardType === 'ups' && (
                      <div style={{ marginTop: '15px', padding: '12px', background: '#fff3cd', borderRadius: '6px' }}>
                        <strong>≡ƒöï UPS/Nobreak:</strong>
                        <ul style={{ marginTop: '8px', fontSize: '13px' }}>
                          <li>APC: Network ΓåÆ SNMP ΓåÆ Access Control</li>
                          <li>SMS: Web Interface ΓåÆ SNMP Settings</li>
                          <li>Requer Network Management Card em alguns modelos</li>
                        </ul>
                      </div>
                    )}
                  </div>

                  <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', border: '1px solid #4caf50' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>Γ£à M├⌐tricas Monitoradas:</strong><br/>
                      {currentWizardType === 'snmp' && 'Status, Uptime, Interfaces, Tr├ífego, CPU, Mem├│ria'}
                      {currentWizardType === 'ap' && 'Status, Carga (CPU/Mem/Clientes), Tr├ífego (TX/RX), Sinais (RSSI/SNR), Acesso (SSIDs/Auth)'}
                      {currentWizardType === 'temp' && 'Temperatura, Umidade, Alarmes'}
                      {currentWizardType === 'storage' && 'Espa├ºo em disco, RAID status, Temperatura'}
                      {currentWizardType === 'printer' && 'Status, N├¡veis de toner, Papel, Total de p├íginas'}
                      {currentWizardType === 'ups' && 'Status, Bateria %, Tempo restante, Carga, Tens├úo'}
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 2: Configura├º├úo */}
              {snmpWizardStep === 2 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#667eea' }}>ΓÜÖ∩╕Å Configura├º├úo do Sensor</h3>
                  
                  <div className="form-group">
                    <label>Probe Respons├ível: *</label>
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
                    <label>Endere├ºo IP: *</label>
                    <input
                      type="text"
                      value={snmpConfig.ip_address}
                      onChange={(e) => setSNMPConfig({...snmpConfig, ip_address: e.target.value})}
                      placeholder="192.168.1.100"
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Vers├úo SNMP:</label>
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
                    <label>Descri├º├úo (Opcional):</label>
                    <textarea
                      value={snmpConfig.description}
                      onChange={(e) => setSNMPConfig({...snmpConfig, description: e.target.value})}
                      rows="2"
                      placeholder="Informa├º├╡es adicionais sobre o dispositivo..."
                    />
                  </div>
                </div>
              )}

              {/* Passo 3: Testar e Finalizar */}
              {snmpWizardStep === 3 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#667eea' }}>≡ƒöî Testar Conex├úo SNMP</h3>
                  
                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Configura├º├úo:</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold', width: '150px' }}>Nome:</td>
                          <td>{snmpConfig.name || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>IP:</td>
                          <td style={{ fontFamily: 'monospace' }}>{snmpConfig.ip_address || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Vers├úo:</td>
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
                      alert('≡ƒöî Teste de conex├úo SNMP ser├í implementado no backend.\n\nVerificar├í:\nΓ£ô Conectividade de rede\nΓ£ô Porta SNMP acess├¡vel\nΓ£ô Community string v├ílido\nΓ£ô Resposta do dispositivo');
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
                    ≡ƒöî Testar Conex├úo SNMP
                  </button>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>ΓÜá∩╕Å Troubleshooting:</strong><br/>
                      ΓÇó <strong>Timeout:</strong> Verifique firewall e conectividade<br/>
                      ΓÇó <strong>Auth Failed:</strong> Community string incorreto<br/>
                      ΓÇó <strong>No Response:</strong> SNMP n├úo habilitado no dispositivo
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
                {snmpWizardStep === 1 ? 'Cancelar' : 'ΓåÉ Voltar'}
              </button>
              
              <button 
                className="btn-primary" 
                onClick={() => {
                  if (snmpWizardStep < 3) {
                    if (snmpWizardStep === 2) {
                      if (!snmpConfig.probe_id || !snmpConfig.name || !snmpConfig.ip_address) {
                        alert('ΓÜá∩╕Å Preencha todos os campos obrigat├│rios.');
                        return;
                      }
                    }
                    setSNMPWizardStep(snmpWizardStep + 1);
                  } else {
                    alert(`Γ£à Sensor SNMP configurado!\n\nO sensor ser├í criado na Biblioteca de Sensores Independentes.`);
                    setShowSNMPWizard(false);
                    setSNMPWizardStep(1);
                    window.location.hash = '#/sensor-library?type=snmp';
                  }
                }}
              >
                {snmpWizardStep === 3 ? 'Γ£ô Criar Sensor' : 'Pr├│ximo ΓåÆ'}
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
              <h2>≡ƒîÉ Configurar Monitoramento HTTP/HTTPS - Passo {httpWizardStep} de 3</h2>
              <button className="modal-close" onClick={() => setShowHTTPWizard(false)}>├ù</button>
            </div>

            <div className="modal-body">
              {/* Passo 1: Requisitos */}
              {httpWizardStep === 1 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#4facfe' }}>≡ƒôï Monitoramento HTTP/HTTPS</h3>
                  
                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      <strong>Γä╣∩╕Å Monitore websites, APIs e endpoints</strong><br/>
                      Verifique disponibilidade, tempo de resposta e conte├║do de p├íginas web.
                    </p>
                  </div>

                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Γ£à Verifica├º├╡es Dispon├¡veis:</h4>
                    <ul style={{ lineHeight: '1.8', fontSize: '14px' }}>
                      <li><strong>Status Code:</strong> 200 (OK), 301 (Redirect), 404 (Not Found), 500 (Error)</li>
                      <li><strong>Tempo de Resposta:</strong> Lat├¬ncia em milissegundos</li>
                      <li><strong>Certificado SSL:</strong> Validade e expira├º├úo (HTTPS)</li>
                      <li><strong>Conte├║do:</strong> Busca por palavras-chave na p├ígina</li>
                      <li><strong>Redirecionamentos:</strong> Seguir ou n├úo seguir redirects</li>
                    </ul>
                  </div>

                  <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', border: '1px solid #4caf50' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>≡ƒöÉ Autentica├º├úo Suportada:</strong><br/>
                      Basic Auth, Bearer Token, API Key, Custom Headers
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 2: Configura├º├úo */}
              {httpWizardStep === 2 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#4facfe' }}>ΓÜÖ∩╕Å Configura├º├úo do Monitoramento</h3>
                  
                  <div className="form-group">
                    <label>Probe Respons├ível: *</label>
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
                      <label>M├⌐todo HTTP:</label>
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
                    <label>Palavra-chave no conte├║do (Opcional):</label>
                    <input
                      type="text"
                      value={httpConfig.keyword}
                      onChange={(e) => setHTTPConfig({...httpConfig, keyword: e.target.value})}
                      placeholder="Ex: Welcome, Success, OK"
                    />
                    <small>Alerta se a palavra N├âO for encontrada na p├ígina</small>
                  </div>
                </div>
              )}

              {/* Passo 3: Testar */}
              {httpWizardStep === 3 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#4facfe' }}>≡ƒöî Testar Conex├úo HTTP</h3>
                  
                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Configura├º├úo:</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold', width: '150px' }}>Nome:</td>
                          <td>{httpConfig.name || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>URL:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px', wordBreak: 'break-all' }}>{httpConfig.url || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>M├⌐todo:</td>
                          <td>{httpConfig.method}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Status Esperado:</td>
                          <td>{httpConfig.expected_status}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Verificar SSL:</td>
                          <td>{httpConfig.check_ssl ? 'Sim' : 'N├úo'}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <button
                    onClick={() => {
                      alert('≡ƒöî Teste de conex├úo HTTP ser├í implementado no backend.\n\nVerificar├í:\nΓ£ô Conectividade com a URL\nΓ£ô Status code retornado\nΓ£ô Tempo de resposta\nΓ£ô Certificado SSL (se HTTPS)\nΓ£ô Palavra-chave (se configurada)');
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
                    ≡ƒöî Testar Conex├úo HTTP
                  </button>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>ΓÜá∩╕Å Troubleshooting:</strong><br/>
                      ΓÇó <strong>Connection Refused:</strong> Servidor offline ou firewall bloqueando<br/>
                      ΓÇó <strong>SSL Error:</strong> Certificado inv├ílido ou expirado<br/>
                      ΓÇó <strong>Timeout:</strong> Servidor lento ou n├úo responde
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
                {httpWizardStep === 1 ? 'Cancelar' : 'ΓåÉ Voltar'}
              </button>
              
              <button 
                className="btn-primary" 
                onClick={async () => {
                  if (httpWizardStep < 3) {
                    if (httpWizardStep === 2) {
                      if (!httpConfig.probe_id || !httpConfig.name || !httpConfig.url) {
                        alert('ΓÜá∩╕Å Preencha todos os campos obrigat├│rios.');
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
                      alert(`Γ£à Sensor HTTP "${httpConfig.name}" criado com sucesso!\n\nAcesse "Biblioteca de Sensores" para visualiz├í-lo.`);
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
                      alert('Γ¥î Erro ao criar sensor: ' + (error.response?.data?.detail || error.message));
                    }
                  }
                }}
              >
                {httpWizardStep === 3 ? 'Γ£ô Criar Sensor' : 'Pr├│ximo ΓåÆ'}
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
              <h2>Γÿ╕∩╕Å Configurar Monitoramento Kubernetes - Passo {k8sWizardStep} de 4</h2>
              <button className="modal-close" onClick={() => setShowK8sWizard(false)}>├ù</button>
            </div>

            <div className="modal-body">
              {/* Passo 1: Requisitos e Instru├º├╡es */}
              {k8sWizardStep === 1 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#326ce5' }}>≡ƒôï Requisitos para Monitoramento Kubernetes</h3>
                  
                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6' }}>
                      <strong>Γä╣∩╕Å Baseado em CheckMK, Prometheus e Grafana</strong><br/>
                      Monitore clusters Kubernetes completos com auto-discovery de pods, deployments e recursos.
                    </p>
                  </div>

                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0, color: '#333' }}>≡ƒöÉ M├⌐todos de Autentica├º├úo Suportados</h4>
                    
                    <div style={{ marginBottom: '15px', padding: '12px', background: 'white', borderRadius: '6px', border: '1px solid #e0e0e0' }}>
                      <strong style={{ color: '#326ce5' }}>1. Kubeconfig File (Recomendado)</strong>
                      <ul style={{ marginTop: '8px', fontSize: '13px', lineHeight: '1.6' }}>
                        <li>Arquivo de configura├º├úo padr├úo do kubectl</li>
                        <li>Localiza├º├úo: <code>~/.kube/config</code></li>
                        <li>Cont├⌐m certificados e credenciais</li>
                        <li>Suporta m├║ltiplos clusters e contextos</li>
                      </ul>
                      <div style={{ marginTop: '8px', padding: '8px', background: '#f5f5f5', borderRadius: '4px', fontFamily: 'monospace', fontSize: '11px' }}>
                        # Obter kubeconfig<br/>
                        kubectl config view --raw &gt; kubeconfig.yaml
                      </div>
                    </div>

                    <div style={{ marginBottom: '15px', padding: '12px', background: 'white', borderRadius: '6px', border: '1px solid #e0e0e0' }}>
                      <strong style={{ color: '#326ce5' }}>2. Service Account Token</strong>
                      <ul style={{ marginTop: '8px', fontSize: '13px', lineHeight: '1.6' }}>
                        <li>Criar Service Account com permiss├╡es de leitura</li>
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
                        <li>Token de autentica├º├úo direto</li>
                        <li>Usado em clusters gerenciados (AKS, EKS, GKE)</li>
                        <li>Pode expirar periodicamente</li>
                      </ul>
                    </div>
                  </div>

                  <div style={{ background: '#fff3cd', padding: '15px', borderRadius: '8px', border: '1px solid #ffc107', marginBottom: '20px' }}>
                    <strong>≡ƒÄ» Tipos de Cluster Suportados:</strong>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', marginTop: '10px' }}>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>Γÿ╕∩╕Å</div>
                        <strong>Vanilla K8s</strong>
                      </div>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>Γÿü∩╕Å</div>
                        <strong>Azure AKS</strong>
                      </div>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>≡ƒƒá</div>
                        <strong>AWS EKS</strong>
                      </div>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>≡ƒö╡</div>
                        <strong>Google GKE</strong>
                      </div>
                      <div style={{ padding: '8px', background: 'white', borderRadius: '4px', textAlign: 'center', fontSize: '12px' }}>
                        <div style={{ fontSize: '20px', marginBottom: '4px' }}>≡ƒö┤</div>
                        <strong>OpenShift</strong>
                      </div>
                    </div>
                  </div>

                  <div style={{ background: '#e8f5e9', padding: '15px', borderRadius: '8px', border: '1px solid #4caf50' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>Γ£à Recursos Monitorados Automaticamente:</strong><br/>
                      ΓÇó <strong>Cluster:</strong> Status geral, nodes dispon├¡veis, capacidade total<br/>
                      ΓÇó <strong>Nodes:</strong> CPU, mem├│ria, disco, pods por node<br/>
                      ΓÇó <strong>Pods:</strong> Status, restarts, CPU/mem├│ria por pod<br/>
                      ΓÇó <strong>Deployments:</strong> R├⌐plicas desejadas vs dispon├¡veis<br/>
                      ΓÇó <strong>DaemonSets:</strong> Pods rodando vs esperados<br/>
                      ΓÇó <strong>StatefulSets:</strong> Status e r├⌐plicas<br/>
                      ΓÇó <strong>Services:</strong> Endpoints dispon├¡veis<br/>
                      ΓÇó <strong>PersistentVolumes:</strong> Uso de armazenamento
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 2: Configura├º├úo do Cluster */}
              {k8sWizardStep === 2 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#326ce5' }}>ΓÜÖ∩╕Å Configura├º├úo do Cluster</h3>
                  
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
                      <option value="vanilla">Γÿ╕∩╕Å Vanilla Kubernetes</option>
                      <option value="aks">Γÿü∩╕Å Azure AKS</option>
                      <option value="eks">≡ƒƒá AWS EKS</option>
                      <option value="gke">≡ƒö╡ Google GKE</option>
                      <option value="openshift">≡ƒö┤ Red Hat OpenShift</option>
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
                    <label>M├⌐todo de Autentica├º├úo: *</label>
                    <select
                      value={k8sConfig.auth_method}
                      onChange={(e) => setK8sConfig({...k8sConfig, auth_method: e.target.value})}
                    >
                      <option value="kubeconfig">≡ƒôä Kubeconfig File (Recomendado)</option>
                      <option value="service_account">≡ƒöæ Service Account Token</option>
                      <option value="token">≡ƒÄ½ Bearer Token</option>
                    </select>
                  </div>

                  {k8sConfig.auth_method === 'kubeconfig' && (
                    <div className="form-group">
                      <label>Conte├║do do Kubeconfig: *</label>
                      <textarea
                        value={k8sConfig.kubeconfig_content}
                        onChange={(e) => setK8sConfig({...k8sConfig, kubeconfig_content: e.target.value})}
                        placeholder="Cole aqui o conte├║do do arquivo kubeconfig..."
                        rows="8"
                        style={{ fontFamily: 'monospace', fontSize: '11px' }}
                      />
                      <small>Cole o conte├║do completo do arquivo ~/.kube/config</small>
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
                        <small>Token do Service Account com permiss├╡es de leitura</small>
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
                        <small>Certificado CA do cluster (deixe em branco para usar o padr├úo do sistema)</small>
                      </div>
                    </>
                  )}

                  {k8sConfig.auth_method === 'token' && (
                    <div className="form-group">
                      <label>Bearer Token: *</label>
                      <textarea
                        value={k8sConfig.service_account_token}
                        onChange={(e) => setK8sConfig({...k8sConfig, service_account_token: e.target.value})}
                        placeholder="Token de autentica├º├úo..."
                        rows="3"
                        style={{ fontFamily: 'monospace', fontSize: '11px' }}
                      />
                      <small>Token de autentica├º├úo do cluster</small>
                    </div>
                  )}

                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3', marginTop: '20px' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      ≡ƒÆí <strong>Dica:</strong> Para clusters gerenciados (AKS, EKS, GKE), use o comando CLI espec├¡fico para obter as credenciais:<br/>
                      ΓÇó <strong>AKS:</strong> <code>az aks get-credentials --resource-group RG --name CLUSTER</code><br/>
                      ΓÇó <strong>EKS:</strong> <code>aws eks update-kubeconfig --name CLUSTER</code><br/>
                      ΓÇó <strong>GKE:</strong> <code>gcloud container clusters get-credentials CLUSTER</code>
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 3: Testar Conex├úo */}
              {k8sWizardStep === 3 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#326ce5' }}>≡ƒöî Testar Conex├úo com Cluster</h3>
                  
                  <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
                    <h4 style={{ marginTop: 0 }}>Configura├º├úo do Cluster:</h4>
                    <table style={{ width: '100%', fontSize: '13px' }}>
                      <tbody>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold', width: '180px' }}>Nome:</td>
                          <td>{k8sConfig.cluster_name || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Tipo:</td>
                          <td>{k8sConfig.cluster_type === 'vanilla' ? 'Γÿ╕∩╕Å Vanilla Kubernetes' : 
                               k8sConfig.cluster_type === 'aks' ? 'Γÿü∩╕Å Azure AKS' :
                               k8sConfig.cluster_type === 'eks' ? '≡ƒƒá AWS EKS' :
                               k8sConfig.cluster_type === 'gke' ? '≡ƒö╡ Google GKE' : '≡ƒö┤ OpenShift'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>API Endpoint:</td>
                          <td style={{ fontFamily: 'monospace', fontSize: '12px', wordBreak: 'break-all' }}>{k8sConfig.api_endpoint || '(n├úo informado)'}</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '8px 0', fontWeight: 'bold' }}>Autentica├º├úo:</td>
                          <td>{k8sConfig.auth_method === 'kubeconfig' ? '≡ƒôä Kubeconfig' : 
                               k8sConfig.auth_method === 'service_account' ? '≡ƒöæ Service Account' : '≡ƒÄ½ Bearer Token'}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <button
                    onClick={async () => {
                      alert('≡ƒöî Teste de conex├úo Kubernetes ser├í implementado no backend.\n\nVerificar├í:\nΓ£ô Conectividade com API Server\nΓ£ô Autentica├º├úo v├ílida\nΓ£ô Permiss├╡es RBAC\nΓ£ô Listagem de namespaces\nΓ£ô Acesso aos recursos\nΓ£ô Metrics Server dispon├¡vel');
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
                    ≡ƒöî Testar Conex├úo com Cluster
                  </button>

                  <div className="info-banner" style={{ background: '#fff3cd', border: '1px solid #ffc107' }}>
                    <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.6' }}>
                      <strong>ΓÜá∩╕Å Poss├¡veis erros:</strong><br/>
                      ΓÇó <strong>Connection Refused:</strong> API Server inacess├¡vel ou firewall bloqueando<br/>
                      ΓÇó <strong>401 Unauthorized:</strong> Credenciais inv├ílidas ou expiradas<br/>
                      ΓÇó <strong>403 Forbidden:</strong> Service Account sem permiss├╡es RBAC adequadas<br/>
                      ΓÇó <strong>Certificate Error:</strong> CA certificate inv├ílido ou n├úo confi├ível<br/>
                      ΓÇó <strong>Metrics Server Not Found:</strong> Metrics Server n├úo instalado no cluster
                    </p>
                  </div>
                </div>
              )}

              {/* Passo 4: Selecionar Namespaces e Recursos */}
              {k8sWizardStep === 4 && (
                <div>
                  <h3 style={{ marginBottom: '15px', color: '#326ce5' }}>≡ƒôª Selecionar Recursos para Monitorar</h3>
                  
                  <div className="info-banner" style={{ background: '#e8f5e9', border: '1px solid #4caf50', marginBottom: '20px' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      Γ£à Conex├úo estabelecida com sucesso! Configure quais recursos deseja monitorar.
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
                    <small>Se desmarcado, voc├¬ poder├í selecionar namespaces espec├¡ficos</small>
                  </div>

                  {!k8sConfig.monitor_all_namespaces && (
                    <div className="form-group">
                      <label>Namespaces Espec├¡ficos:</label>
                      <input
                        type="text"
                        value={k8sConfig.namespaces.join(', ')}
                        onChange={(e) => setK8sConfig({...k8sConfig, namespaces: e.target.value.split(',').map(ns => ns.trim()).filter(ns => ns)})}
                        placeholder="default, production, staging"
                      />
                      <small>Separe m├║ltiplos namespaces por v├¡rgula</small>
                    </div>
                  )}

                  <h4 style={{ marginTop: '20px', marginBottom: '15px' }}>Tipos de Recursos:</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '20px' }}>
                    {[
                      { type: 'nodes', icon: '≡ƒûÑ∩╕Å', name: 'Nodes', desc: 'CPU, mem├│ria, disco' },
                      { type: 'pods', icon: '≡ƒôª', name: 'Pods', desc: 'Status, restarts, recursos' },
                      { type: 'deployments', icon: '≡ƒÜÇ', name: 'Deployments', desc: 'R├⌐plicas, rollouts' },
                      { type: 'daemonsets', icon: '≡ƒæÑ', name: 'DaemonSets', desc: 'Pods por node' },
                      { type: 'statefulsets', icon: '≡ƒÆ╛', name: 'StatefulSets', desc: 'R├⌐plicas ordenadas' },
                      { type: 'services', icon: '≡ƒîÉ', name: 'Services', desc: 'Endpoints, portas' },
                      { type: 'ingress', icon: '≡ƒÜ¬', name: 'Ingress', desc: 'Rotas HTTP/HTTPS' },
                      { type: 'pv', icon: '≡ƒÆ┐', name: 'Persistent Volumes', desc: 'Armazenamento' }
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
                          <div style={{ marginTop: '8px', fontSize: '16px', textAlign: 'center' }}>Γ£ô</div>
                        )}
                      </button>
                    ))}
                  </div>

                  <div className="info-banner" style={{ background: '#e3f2fd', border: '1px solid #2196f3' }}>
                    <p style={{ margin: 0, fontSize: '13px' }}>
                      ≡ƒÆí Selecionados: <strong>{k8sConfig.selected_resources.length}</strong> tipo(s) de recurso.
                      {k8sConfig.monitor_all_namespaces ? ' Monitorando todos os namespaces.' : ` Monitorando ${k8sConfig.namespaces.length} namespace(s).`}
                      <br/><br/>
                      <strong>ΓÅ▒∩╕Å Intervalo de coleta:</strong> M├⌐tricas atualizadas a cada 60 segundos (configur├ível).
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
                {k8sWizardStep === 1 ? 'Cancelar' : 'ΓåÉ Voltar'}
              </button>
              
              <button 
                className="btn-primary" 
                onClick={() => {
                  if (k8sWizardStep < 4) {
                    // Validar campos obrigat├│rios no passo 2
                    if (k8sWizardStep === 2) {
                      if (!k8sConfig.cluster_name || !k8sConfig.api_endpoint) {
                        alert('ΓÜá∩╕Å Preencha o nome do cluster e o API endpoint.');
                        return;
                      }
                      if (k8sConfig.auth_method === 'kubeconfig' && !k8sConfig.kubeconfig_content) {
                        alert('ΓÜá∩╕Å Cole o conte├║do do kubeconfig.');
                        return;
                      }
                      if ((k8sConfig.auth_method === 'service_account' || k8sConfig.auth_method === 'token') && !k8sConfig.service_account_token) {
                        alert('ΓÜá∩╕Å Informe o token de autentica├º├úo.');
                        return;
                      }
                    }
                    setK8sWizardStep(k8sWizardStep + 1);
                  } else {
                    // Finalizar e criar sensores
                    const namespaceInfo = k8sConfig.monitor_all_namespaces ? 'todos os namespaces' : `${k8sConfig.namespaces.length} namespace(s)`;
                    alert(`Γ£à Configura├º├úo Kubernetes conclu├¡da!\n\nCluster: ${k8sConfig.cluster_name}\nRecursos: ${k8sConfig.selected_resources.length} tipo(s)\nNamespaces: ${namespaceInfo}\n\nOs sensores ser├úo criados na Biblioteca de Sensores Independentes com auto-discovery ativado.`);
                    setShowK8sWizard(false);
                    setK8sWizardStep(1);
                    // Redirecionar para biblioteca com Kubernetes pr├⌐-selecionado
                    window.location.hash = '#/sensor-library?type=kubernetes';
                  }
                }}
                disabled={k8sWizardStep === 4 && k8sConfig.selected_resources.length === 0}
                style={{
                  opacity: (k8sWizardStep === 4 && k8sConfig.selected_resources.length === 0) ? 0.5 : 1,
                  cursor: (k8sWizardStep === 4 && k8sConfig.selected_resources.length === 0) ? 'not-allowed' : 'pointer'
                }}
              >
                {k8sWizardStep === 4 ? 'Γ£ô Finalizar e Criar Sensores' : 'Pr├│ximo ΓåÆ'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Servers;

