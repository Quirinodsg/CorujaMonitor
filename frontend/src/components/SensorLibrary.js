import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { sensorCategories, sensorTemplates } from '../data/sensorTemplates';
import './Management.css';
import './SensorGroups.css';

function SensorLibrary() {
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingSensor, setEditingSensor] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [probes, setProbes] = useState([]);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionTestResult, setConnectionTestResult] = useState(null);
  const [sensorMetrics, setSensorMetrics] = useState({});
  const [addSuccess, setAddSuccess] = useState(false);
  const [addError, setAddError] = useState('');
  const [networkDevices, setNetworkDevices] = useState([]);
  const [networkStatuses, setNetworkStatuses] = useState({});
  
  const [newSensor, setNewSensor] = useState({
    probe_id: '',
    name: '',
    sensor_type: 'snmp',
    category: 'snmp',
    ip_address: '',
    snmp_version: 'v2c',
    snmp_community: 'public',
    snmp_port: 161,
    snmp_oid: '',
    http_url: '',
    http_method: 'GET',
    azure_subscription_id: '',
    azure_tenant_id: '',
    azure_client_id: '',
    azure_client_secret: '',
    azure_resource_type: '',
    azure_resource_name: '',
    threshold_warning: 80,
    threshold_critical: 95,
    description: ''
  });

  useEffect(() => {
    loadSensors();
    loadProbes();
    loadNetworkDevices();
    
    // Verificar se há tipo pré-selecionado na URL
    const urlParams = new URLSearchParams(window.location.search);
    const typeParam = urlParams.get('type');
    if (typeParam) {
      setSelectedCategory(typeParam);
      // Abrir modal automaticamente se houver tipo
      setTimeout(() => setShowAddModal(true), 500);
    }
  }, []);

  const loadProbes = async () => {
    try {
      const response = await api.get('/probes');
      setProbes(response.data);
    } catch (error) {
      console.error('Erro ao carregar probes:', error);
    }
  };

  const loadSensors = async () => {
    try {
      // Carregar sensores independentes (sem server_id)
      const response = await api.get('/sensors/standalone');
      setSensors(response.data);
      setLoading(false);

      // Carregar métricas em batch para todos os sensores
      if (response.data.length > 0) {
        try {
          const ids = response.data.map(s => s.id).join(',');
          const metricsRes = await api.get(`/metrics/latest/batch?sensor_ids=${ids}`);
          setSensorMetrics(metricsRes.data);
        } catch (_) {}
      }
    } catch (error) {
      console.error('Erro ao carregar sensores:', error);
      setLoading(false);
    }
  };

  const loadNetworkDevices = async () => {
    try {
      const res = await api.get('/servers');
      const netTypes = ['switch', 'router', 'firewall', 'access_point', 'ap', 'ups', 'storage', 'gateway'];
      const devices = res.data.filter(s => netTypes.includes((s.device_type || '').toLowerCase()));
      setNetworkDevices(devices);
      if (devices.length > 0) {
        try {
          const statusRes = await api.get('/dashboard/network-assets-status?ids=' + devices.map(a => a.id).join(','));
          setNetworkStatuses(statusRes.data);
        } catch (_) {
          const fallback = {};
          devices.forEach(a => { fallback[a.id] = 'unknown'; });
          setNetworkStatuses(fallback);
        }
      }
    } catch (_) {}
  };

  const handleAddSensor = async () => {
    if (!newSensor.probe_id || !newSensor.name) {
      setAddError('Preencha os campos obrigatórios: Probe e Nome');
      return;
    }

    setAddError('');
    try {
      await api.post('/sensors/standalone', {
        probe_id: parseInt(newSensor.probe_id),
        name: newSensor.name,
        sensor_type: newSensor.sensor_type,
        category: newSensor.category,
        ip_address: newSensor.ip_address || null,
        snmp_version: newSensor.snmp_version || null,
        snmp_community: newSensor.snmp_community || null,
        snmp_port: newSensor.snmp_port ? parseInt(newSensor.snmp_port) : null,
        snmp_oid: newSensor.snmp_oid || null,
        http_url: newSensor.http_url || null,
        http_method: newSensor.http_method || null,
        azure_subscription_id: newSensor.azure_subscription_id || null,
        azure_tenant_id: newSensor.azure_tenant_id || null,
        azure_client_id: newSensor.azure_client_id || null,
        azure_client_secret: newSensor.azure_client_secret || null,
        azure_resource_type: newSensor.azure_resource_type || null,
        azure_resource_name: newSensor.azure_resource_name || null,
        threshold_warning: parseFloat(newSensor.threshold_warning),
        threshold_critical: parseFloat(newSensor.threshold_critical),
        description: newSensor.description || null
      });

      setAddSuccess(true);
      loadSensors();
      setTimeout(() => {
        setShowAddModal(false);
        setAddSuccess(false);
        resetForm();
      }, 1500);
    } catch (error) {
      console.error('Erro ao adicionar sensor:', error);
      setAddError('Erro ao adicionar sensor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleUpdateSensor = async () => {
    if (!editingSensor) return;

    try {
      await api.put(`/sensors/${editingSensor.id}`, {
        name: editingSensor.name,
        threshold_warning: parseFloat(editingSensor.threshold_warning),
        threshold_critical: parseFloat(editingSensor.threshold_critical),
        description: editingSensor.description
      });

      setShowEditModal(false);
      setEditingSensor(null);
      loadSensors();
      alert('Sensor atualizado com sucesso!');
    } catch (error) {
      console.error('Erro ao atualizar sensor:', error);
      alert('Erro ao atualizar sensor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteSensor = async (sensorId, sensorName) => {
    if (!window.confirm(`Tem certeza que deseja remover o sensor "${sensorName}"?`)) {
      return;
    }

    try {
      await api.delete(`/sensors/${sensorId}`);
      loadSensors();
      alert('Sensor removido com sucesso!');
    } catch (error) {
      console.error('Erro ao remover sensor:', error);
      alert('Erro ao remover sensor: ' + (error.response?.data?.detail || error.message));
    }
  };

  const resetForm = () => {
    setNewSensor({
      probe_id: '',
      name: '',
      sensor_type: 'snmp',
      category: 'snmp',
      ip_address: '',
      snmp_version: 'v2c',
      snmp_community: 'public',
      snmp_port: 161,
      snmp_oid: '',
      http_url: '',
      http_method: 'GET',
      azure_subscription_id: '',
      azure_tenant_id: '',
      azure_client_id: '',
      azure_client_secret: '',
      azure_resource_type: '',
      azure_resource_name: '',
      threshold_warning: 80,
      threshold_critical: 95,
      description: ''
    });
    setConnectionTestResult(null);
    setAddError('');
    setAddSuccess(false);
  };

  const handleTestConnection = async () => {
    setTestingConnection(true);
    setConnectionTestResult(null);

    try {
      let testData = {};

      // Preparar dados de teste baseado na categoria
      if (newSensor.category === 'azure') {
        if (!newSensor.azure_subscription_id || !newSensor.azure_tenant_id || 
            !newSensor.azure_client_id || !newSensor.azure_client_secret) {
          setConnectionTestResult({
            success: false,
            message: 'Preencha todas as credenciais Azure antes de testar'
          });
          setTestingConnection(false);
          return;
        }

        testData = {
          type: 'azure',
          subscription_id: newSensor.azure_subscription_id,
          tenant_id: newSensor.azure_tenant_id,
          client_id: newSensor.azure_client_id,
          client_secret: newSensor.azure_client_secret,
          resource_type: newSensor.azure_resource_type,
          resource_name: newSensor.azure_resource_name
        };
      } else if (newSensor.category === 'snmp' || newSensor.sensor_type === 'snmp') {
        if (!newSensor.ip_address) {
          setConnectionTestResult({
            success: false,
            message: 'Preencha o endereço IP antes de testar'
          });
          setTestingConnection(false);
          return;
        }

        testData = {
          type: 'snmp',
          ip_address: newSensor.ip_address,
          snmp_version: newSensor.snmp_version,
          snmp_community: newSensor.snmp_community,
          snmp_port: newSensor.snmp_port,
          snmp_oid: newSensor.snmp_oid || '1.3.6.1.2.1.1.1.0' // sysDescr
        };
      } else if (newSensor.category === 'network' && newSensor.http_url) {
        testData = {
          type: 'http',
          url: newSensor.http_url,
          method: newSensor.http_method
        };
      } else if (newSensor.category === 'cloud') {
        testData = {
          type: 'aws',
          // AWS credentials would go here
        };
      } else {
        setConnectionTestResult({
          success: false,
          message: 'Teste de conexão não disponível para esta categoria'
        });
        setTestingConnection(false);
        return;
      }

      // Chamar endpoint de teste
      const response = await api.post('/sensors/test-connection', testData);
      
      setConnectionTestResult({
        success: true,
        message: response.data.message || 'Conexão testada com sucesso!',
        details: response.data.details
      });

    } catch (error) {
      console.error('Erro ao testar conexão:', error);
      setConnectionTestResult({
        success: false,
        message: error.response?.data?.detail || 'Erro ao testar conexão. Verifique as credenciais.',
        error: error.response?.data?.error
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleTemplateSelect = (template) => {
    setNewSensor({
      ...newSensor,
      name: template.default_name,
      sensor_type: template.sensor_type,
      category: template.category || 'snmp',
      snmp_oid: template.snmp_oids ? Object.values(template.snmp_oids)[0] : '',
      threshold_warning: template.thresholds.warning,
      threshold_critical: template.thresholds.critical,
      description: template.description
    });
  };

  const filteredSensors = sensors.filter(sensor => {
    const matchesSearch = !searchTerm || sensor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (sensor.description && sensor.description.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesSearch;
  });

  // Agrupar sensores por categoria visual
  const sensorsByGroup = {
    sites: filteredSensors.filter(s => s.sensor_type === 'http' || s.sensor_type === 'https' || s.category === 'network'),
    energia: filteredSensors.filter(s => ['snmp_ups', 'ups', 'snmp'].includes(s.sensor_type) && (s.name || '').toLowerCase().match(/nobreak|ups|gerador|energia|battery|power/)),
    hvac: filteredSensors.filter(s => (s.name || '').toLowerCase().match(/ar.condicionado|hvac|temperatura|cooling|climate|chiller/)),
    outros: [],
  };
  // "Outros" = tudo que não caiu nas categorias acima
  const categorized = new Set([...sensorsByGroup.sites, ...sensorsByGroup.energia, ...sensorsByGroup.hvac].map(s => s.id));
  sensorsByGroup.outros = filteredSensors.filter(s => !categorized.has(s.id));

  // Filtro por categoria selecionada
  const showSection = (key) => selectedCategory === 'all' || selectedCategory === key;

  const getSensorIcon = (category) => {
    const icons = {
      snmp: '📡',
      azure: '☁️',
      http: '🌐',
      storage: '💿',
      network: '🌐',
      application: '📦',
      custom: '⚙️'
    };
    return icons[category] || '📊';
  };

  const renderSensorCard = (sensor, metric, statusColor, statusLabel, statusBg) => {
    const isHttp = sensor.sensor_type === 'http' || sensor.category === 'network';
    const isOnline = metric?.status === 'ok';
    return (
      <div key={sensor.id} className="sensor-card" style={{
        borderLeft: `4px solid ${statusColor}`,
        background: statusBg,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute', top: 8, right: 8,
          display: 'flex', gap: 4, alignItems: 'center', zIndex: 2
        }}>
          <button onClick={() => { setEditingSensor({ id: sensor.id, name: sensor.name, threshold_warning: sensor.threshold_warning || 80, threshold_critical: sensor.threshold_critical || 95, description: sensor.description || '' }); setShowEditModal(true); }}
            title="Editar" style={{ width: 26, height: 26, border: 'none', borderRadius: 5, background: '#f0f4ff', cursor: 'pointer', fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0 }}>✏️</button>
          <button onClick={() => handleDeleteSensor(sensor.id, sensor.name)}
            title="Remover" style={{ width: 26, height: 26, border: 'none', borderRadius: 5, background: '#fff0f0', color: '#ef4444', cursor: 'pointer', fontSize: 16, fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0 }}>×</button>
        </div>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, padding: '4px 10px', borderRadius: 20, background: statusColor, color: 'white', fontSize: 11, fontWeight: 700, marginBottom: 10 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'white', boxShadow: isOnline ? '0 0 6px white' : 'none' }} />
          {statusLabel}
        </div>
        <div className="sensor-header">
          <span style={{ fontSize: 20, flexShrink: 0 }}>{getSensorIcon(sensor.category)}</span>
          <h3>{sensor.name}</h3>
        </div>
        <div className="sensor-details" style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 8 }}>
          {isHttp && sensor.config?.http_url && <p style={{ wordBreak: 'break-all', fontSize: 12, color: '#818cf8' }}>🔗 {sensor.config.http_url}</p>}
          {sensor.config?.ip_address && <p>📍 {sensor.config.ip_address}</p>}
          {metric && (
            <p style={{ color: statusColor, fontWeight: 600 }}>
              {isHttp ? `⏱️ ${metric.value ? Math.round(metric.value) + ' ms' : '-'}` : `📊 ${metric.value?.toFixed(1) || '-'} ${metric.unit || ''}`}
            </p>
          )}
          {metric?.timestamp && <p style={{ fontSize: 11, color: 'var(--text-secondary)' }}>🕐 {new Date(metric.timestamp).toLocaleString('pt-BR')}</p>}
          {metric?.metadata && metric.metadata['Engetron temperatura'] && (
            <div style={{ marginTop: 6, padding: '6px 0', borderTop: '1px solid var(--border)', fontSize: 11, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3px 8px', color: 'var(--text-secondary)' }}>
              <span>🌡️ {metric.metadata['Engetron temperatura'].value}°C</span>
              {metric.metadata['Engetron bateria_autonomia'] && <span>🔋 {metric.metadata['Engetron bateria_autonomia'].value} min</span>}
              {metric.metadata['Engetron carga_max'] && <span>⚡ Carga: {metric.metadata['Engetron carga_max'].value}%</span>}
              {metric.metadata['Engetron bateria_tensao'] && <span>🔌 {metric.metadata['Engetron bateria_tensao'].value}V</span>}
              {metric.metadata['Engetron tensao_entrada_faseA'] && (
                <span style={{gridColumn:'1/-1', color: [metric.metadata['Engetron tensao_entrada_faseA'], metric.metadata['Engetron tensao_entrada_faseB'], metric.metadata['Engetron tensao_entrada_faseC']].some(f => f && f.value < 100) ? '#ef4444' : '#22c55e'}}>
                  📥 Entrada: {metric.metadata['Engetron tensao_entrada_faseA']?.value}V · {metric.metadata['Engetron tensao_entrada_faseB']?.value}V · {metric.metadata['Engetron tensao_entrada_faseC']?.value}V
                  {[metric.metadata['Engetron tensao_entrada_faseA'], metric.metadata['Engetron tensao_entrada_faseB'], metric.metadata['Engetron tensao_entrada_faseC']].some(f => f && f.value < 100) && ' ⚠️ QUEDA DE FASE'}
                </span>
              )}
              {metric.metadata['Engetron tensao_saida_faseA'] && (
                <span style={{gridColumn:'1/-1'}}>📤 Saída: {metric.metadata['Engetron tensao_saida_faseA']?.value}V · {metric.metadata['Engetron tensao_saida_faseB']?.value}V · {metric.metadata['Engetron tensao_saida_faseC']?.value}V</span>
              )}
            </div>
          )}
          {/* Printer details */}
          {metric?.metadata && metric.metadata['Printer toner'] && (
            <div style={{ marginTop: 6, padding: '6px 0', borderTop: '1px solid var(--border)', fontSize: 11, color: 'var(--text-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{ fontSize: 14, fontWeight: 700, color: metric.metadata['Printer toner'].value <= 10 ? '#ef4444' : metric.metadata['Printer toner'].value <= 20 ? '#f59e0b' : '#22c55e' }}>
                  🖨️ Toner: {metric.metadata['Printer toner'].value}%
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3px 8px' }}>
                {metric.metadata['Printer total_pages'] && <span>📄 {metric.metadata['Printer total_pages'].value.toLocaleString()} páginas</span>}
                {metric.metadata['Printer printer_status'] && <span>📊 {metric.metadata['Printer printer_status'].label}</span>}
                {metric.metadata['Printer model'] && <span style={{gridColumn:'1/-1'}}>🏷️ {metric.metadata['Printer model'].label}</span>}
              </div>
            </div>
          )}
          {/* Conflex HVAC details */}
          {metric?.metadata && metric.metadata['Conflex status'] && (
            <div style={{ marginTop: 6, padding: '6px 0', borderTop: '1px solid var(--border)', fontSize: 11, color: 'var(--text-secondary)' }}>
              {metric.metadata['Conflex temp_interna'] && (
                <div style={{ fontSize: 16, fontWeight: 700, color: metric.metadata['Conflex temp_interna'].value >= 26 ? '#ef4444' : '#22c55e', marginBottom: 4 }}>
                  🌡️ {metric.metadata['Conflex temp_interna'].value}°C
                  {metric.metadata['Conflex temp_interna'].value >= 26 && <span style={{fontSize:11, marginLeft:6}}>⚠️ ALTA</span>}
                </div>
              )}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '3px 8px' }}>
                {metric.metadata['Conflex alarme_temp_alta'] && <span style={{color: metric.metadata['Conflex alarme_temp_alta'].value === 1 ? '#ef4444' : '#22c55e'}}>🌡️ Temp: {metric.metadata['Conflex alarme_temp_alta'].value === 1 ? 'ALARME' : 'OK'}</span>}
                {metric.metadata['Conflex alarme_defeito'] && <span style={{color: metric.metadata['Conflex alarme_defeito'].value === 1 ? '#ef4444' : '#22c55e'}}>⚠️ Defeito: {metric.metadata['Conflex alarme_defeito'].value === 1 ? 'ALARME' : 'OK'}</span>}
                {metric.metadata['Conflex status_plc'] && <span style={{color: metric.metadata['Conflex status_plc'].value === 1 ? '#22c55e' : '#ef4444'}}>🔌 PLC: {metric.metadata['Conflex status_plc'].value === 1 ? 'ON' : 'OFF'}</span>}
                {metric.metadata['Conflex maquina_1'] && <span style={{color: metric.metadata['Conflex maquina_1'].value === 1 ? '#22c55e' : '#f59e0b'}}>❄️ Máq 1: {metric.metadata['Conflex maquina_1'].value === 1 ? 'ON' : 'OFF'}</span>}
                {metric.metadata['Conflex maquina_2'] && <span style={{color: metric.metadata['Conflex maquina_2'].value === 1 ? '#22c55e' : '#f59e0b'}}>❄️ Máq 2: {metric.metadata['Conflex maquina_2'].value === 1 ? 'ON' : 'OFF'}</span>}
                {metric.metadata['Conflex temp_retorno_maq1'] && <span>🔄 Máq1: {metric.metadata['Conflex temp_retorno_maq1'].value}°C</span>}
                {metric.metadata['Conflex temp_retorno_maq2'] && <span>🔄 Máq2: {metric.metadata['Conflex temp_retorno_maq2'].value}°C</span>}
                {metric.metadata['Conflex falha_rede'] && metric.metadata['Conflex falha_rede'].value === 0 && <span style={{color:'#ef4444', gridColumn:'1/-1'}}>🔴 FALHA REDE GERAL</span>}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return <div className="management-container">Carregando...</div>;
  }

  return (
    <div className="management-container">
      <div className="management-header">
        <h1>📚 Biblioteca de Sensores</h1>
        <button className="btn-add" onClick={() => setShowAddModal(true)}>
          + Adicionar Sensor
        </button>
      </div>

      <div className="info-banner" style={{ marginBottom: '20px' }}>
        <p>ℹ️ <strong>Biblioteca de Sensores Independentes</strong></p>
        <p>Adicione sensores que não estão vinculados a servidores específicos: Access Points, Ar-Condicionado, Nobreaks, Impressoras, Serviços Azure, Aplicações, etc.</p>
      </div>

      {/* ── Ativos de Rede ── */}
      {networkDevices.length > 0 && (selectedCategory === 'all' || selectedCategory === 'network_devices') && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            🔀 Ativos de Rede ({networkDevices.length})
          </h3>
          <div className="sensors-grid">
            {networkDevices.filter(d => !searchTerm || d.hostname?.toLowerCase().includes(searchTerm.toLowerCase()) || d.ip_address?.includes(searchTerm)).map(device => {
              const status = networkStatuses[device.id] || 'unknown';
              const statusColor = status === 'ok' ? '#10b981' : status === 'warning' ? '#f59e0b' : status === 'critical' ? '#ef4444' : '#6b7280';
              const statusLabel = status === 'ok' ? 'ONLINE' : status === 'warning' ? 'AVISO' : status === 'critical' ? 'CRÍTICO' : 'Aguardando';
              const statusBg = status === 'ok' ? '#10b98115' : status === 'warning' ? '#f59e0b15' : status === 'critical' ? '#ef444415' : '#6b728015';
              const dt = (device.device_type || 'other').toLowerCase();
              const deviceIcons = { switch: '🔀', router: '📡', firewall: '🔥', access_point: '📶', ap: '📶', ups: '🔋', storage: '🧠', gateway: '📡' };
              const deviceLabels = { switch: 'Switch', router: 'Router', firewall: 'Firewall', access_point: 'Access Point', ap: 'Access Point', ups: 'UPS/Nobreak', storage: 'Storage', gateway: 'Gateway' };
              return (
                <div key={'net-' + device.id} className="sensor-card" style={{
                  borderLeft: '4px solid ' + statusColor,
                  background: statusBg,
                  position: 'relative'
                }}>
                  <div style={{ position: 'absolute', top: 8, left: 10 }}>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 4,
                      padding: '2px 8px', borderRadius: 10, fontSize: 10, fontWeight: 700,
                      background: statusColor, color: '#fff'
                    }}>
                      <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#fff' }} />
                      {statusLabel}
                    </span>
                  </div>
                  <div style={{ position: 'absolute', top: 8, right: 10, fontSize: 11, color: 'var(--text-secondary)' }}>
                    {deviceLabels[dt] || dt}
                  </div>
                  <div style={{ marginTop: 28 }}>
                    <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>
                      {deviceIcons[dt] || '📦'} {device.hostname}
                    </div>
                    {device.ip_address && (
                      <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontFamily: 'monospace', marginTop: 4 }}>
                        {device.ip_address}
                      </div>
                    )}
                    {device.group_name && (
                      <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 4 }}>
                        📁 {device.group_name}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="filters-bar" style={{ display: 'flex', gap: '15px', marginBottom: '20px', alignItems: 'center' }}>
        <div className="form-group" style={{ flex: 1, margin: 0 }}>
          <input
            type="text"
            placeholder="🔍 Buscar sensores..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
          />
        </div>
        
        <div className="form-group" style={{ margin: 0 }}>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{ padding: '10px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--surface-1)', color: 'var(--text-primary)' }}
          >
            <option value="all">Todas as Categorias</option>
            <option value="sites">🌐 Sites</option>
            <option value="network_devices">🔀 Ativos de Rede</option>
            <option value="energia">⚡ Energia</option>
            <option value="hvac">❄️ Ar-Condicionado</option>
          </select>
        </div>
      </div>

      <div className="sensors-grid">
        {/* ── Sites Monitorados ── */}
        {showSection('sites') && sensorsByGroup.sites.length > 0 && (
          <div style={{ gridColumn: '1 / -1', marginBottom: 8 }}>
            <h3 style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              🌐 Sites Monitorados ({sensorsByGroup.sites.length})
            </h3>
          </div>
        )}
        {showSection('sites') && sensorsByGroup.sites.map(sensor => {
          const metric = sensorMetrics[String(sensor.id)];
          const isOnline = metric?.status === 'ok';
          const statusColor = !metric ? '#6b7280' : isOnline ? '#10b981' : '#ef4444';
          const statusLabel = !metric ? 'Aguardando' : isOnline ? 'ONLINE' : 'OFFLINE';
          const statusBg = !metric ? '#6b728015' : isOnline ? '#10b98115' : '#ef444415';
          return renderSensorCard(sensor, metric, statusColor, statusLabel, statusBg);
        })}

        {/* ── Energia (Nobreaks, Geradores) ── */}
        {showSection('energia') && sensorsByGroup.energia.length > 0 && (
          <div style={{ gridColumn: '1 / -1', marginBottom: 8, marginTop: 16 }}>
            <h3 style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              ⚡ Energia ({sensorsByGroup.energia.length})
              <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontWeight: 400 }}>Nobreaks, Geradores, UPS</span>
            </h3>
          </div>
        )}
        {showSection('energia') && sensorsByGroup.energia.map(sensor => {
          const metric = sensorMetrics[String(sensor.id)];
          const isOnline = metric?.status === 'ok';
          const statusColor = !metric ? '#6b7280' : isOnline ? '#10b981' : '#ef4444';
          const statusLabel = !metric ? 'Aguardando' : isOnline ? 'ONLINE' : 'OFFLINE';
          const statusBg = !metric ? '#6b728015' : isOnline ? '#10b98115' : '#ef444415';
          return renderSensorCard(sensor, metric, statusColor, statusLabel, statusBg);
        })}

        {/* ── Ar-Condicionado ── */}
        {showSection('hvac') && sensorsByGroup.hvac.length > 0 && (
          <div style={{ gridColumn: '1 / -1', marginBottom: 8, marginTop: 16 }}>
            <h3 style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              ❄️ Ar-Condicionado ({sensorsByGroup.hvac.length})
              <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontWeight: 400 }}>Climatização, Temperatura</span>
            </h3>
          </div>
        )}
        {showSection('hvac') && sensorsByGroup.hvac.map(sensor => {
          const metric = sensorMetrics[String(sensor.id)];
          const isOnline = metric?.status === 'ok';
          const statusColor = !metric ? '#6b7280' : isOnline ? '#10b981' : '#ef4444';
          const statusLabel = !metric ? 'Aguardando' : isOnline ? 'ONLINE' : 'OFFLINE';
          const statusBg = !metric ? '#6b728015' : isOnline ? '#10b98115' : '#ef444415';
          return renderSensorCard(sensor, metric, statusColor, statusLabel, statusBg);
        })}

        {/* ── Outros Sensores ── */}
        {showSection('all') && sensorsByGroup.outros.length > 0 && (sensorsByGroup.sites.length > 0 || sensorsByGroup.energia.length > 0 || sensorsByGroup.hvac.length > 0) && (
          <div style={{ gridColumn: '1 / -1', marginBottom: 8, marginTop: 16 }}>
            <h3 style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              📦 Outros Sensores ({sensorsByGroup.outros.length})
            </h3>
          </div>
        )}
        {(showSection('all') ? sensorsByGroup.outros : []).map(sensor => {
          const metric = sensorMetrics[String(sensor.id)];
          const isOnline = metric?.status === 'ok';
          const statusColor = !metric ? '#6b7280' : isOnline ? '#10b981' : '#ef4444';
          const statusLabel = !metric ? 'Aguardando' : isOnline ? 'ONLINE' : 'OFFLINE';
          const statusBg = !metric ? '#6b728015' : isOnline ? '#10b98115' : '#ef444415';
          return renderSensorCard(sensor, metric, statusColor, statusLabel, statusBg);
        })}

        {filteredSensors.length === 0 && networkDevices.length === 0 && (
          <div className="no-data" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px' }}>
            <p>Nenhum sensor encontrado</p>
            <p>Clique em "Adicionar Sensor" para começar</p>
          </div>
        )}
      </div>

      {/* Modal Adicionar Sensor */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <h2>📚 Adicionar Sensor à Biblioteca</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label>Probe Responsável: *</label>
                <select 
                  value={newSensor.probe_id}
                  onChange={(e) => setNewSensor({...newSensor, probe_id: e.target.value})}
                  required
                >
                  <option value="">-- Selecione uma probe --</option>
                  {probes.map(probe => (
                    <option key={probe.id} value={probe.id}>
                      {probe.name}
                    </option>
                  ))}
                </select>
                <small>A probe que irá coletar dados deste sensor</small>
              </div>

              <div className="form-group">
                <label>Categoria: *</label>
                <select
                  value={newSensor.category}
                  onChange={(e) => {
                    const cat = e.target.value;
                    const typeMap = { network: 'http', azure: 'azure', snmp: 'snmp', icmp: 'icmp' };
                    setNewSensor({...newSensor, category: cat, sensor_type: typeMap[cat] || cat});
                  }}
                >
                  {Object.entries(sensorCategories).map(([key, cat]) => (
                    <option key={key} value={key}>
                      {cat.icon} {cat.name}
                    </option>
                  ))}
                </select>
                <small>Tipo de dispositivo ou serviço</small>
              </div>
            </div>

            <div className="form-section">
              <h3>📋 Templates Rápidos</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px', marginBottom: '20px' }}>
                {sensorTemplates[newSensor.category]?.slice(0, 6).map(template => (
                  <button
                    key={template.id}
                    type="button"
                    onClick={() => handleTemplateSelect(template)}
                    style={{
                      padding: '10px',
                      border: '1px solid var(--border)',
                      borderRadius: '6px',
                      background: 'var(--surface-2)',
                      cursor: 'pointer',
                      textAlign: 'left',
                      color: 'var(--text-primary)',
                      transition: 'border-color 0.2s'
                    }}
                  >
                    <div style={{ fontSize: '20px', marginBottom: '5px' }}>{template.icon}</div>
                    <div style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-primary)' }}>{template.name}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Nome do Sensor: *</label>
                <input
                  type="text"
                  value={newSensor.name}
                  onChange={(e) => setNewSensor({...newSensor, name: e.target.value})}
                  required
                  placeholder="Ex: AP-Sala-01, AC-Datacenter, Azure-WebApp"
                />
              </div>

              <div className="form-group">
                <label>Endereço IP:</label>
                <input
                  type="text"
                  value={newSensor.ip_address}
                  onChange={(e) => setNewSensor({...newSensor, ip_address: e.target.value})}
                  placeholder="Ex: 192.168.1.100"
                />
                <small>Para sensores SNMP e HTTP</small>
              </div>
            </div>

            {/* Configurações SNMP */}
            {(newSensor.category === 'snmp' || newSensor.sensor_type === 'snmp') && (
              <div className="form-section">
                <h3>📡 Configurações SNMP</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label>Versão SNMP:</label>
                    <select
                      value={newSensor.snmp_version}
                      onChange={(e) => setNewSensor({...newSensor, snmp_version: e.target.value})}
                    >
                      <option value="v1">SNMP v1</option>
                      <option value="v2c">SNMP v2c</option>
                      <option value="v3">SNMP v3</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Community String:</label>
                    <input
                      type="text"
                      value={newSensor.snmp_community}
                      onChange={(e) => setNewSensor({...newSensor, snmp_community: e.target.value})}
                      placeholder="public"
                    />
                  </div>

                  <div className="form-group">
                    <label>Porta SNMP:</label>
                    <input
                      type="number"
                      value={newSensor.snmp_port}
                      onChange={(e) => setNewSensor({...newSensor, snmp_port: e.target.value})}
                      placeholder="161"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>OID SNMP:</label>
                  <input
                    type="text"
                    value={newSensor.snmp_oid}
                    onChange={(e) => setNewSensor({...newSensor, snmp_oid: e.target.value})}
                    placeholder="Ex: 1.3.6.1.4.1.9.9.13.1.3.1.3"
                  />
                  <small>OID específico para monitorar (deixe vazio para usar OID padrão no teste)</small>
                </div>

                {/* Botão de Teste de Conexão SNMP */}
                <div style={{ marginTop: '15px', marginBottom: '15px' }}>
                  <button
                    type="button"
                    onClick={handleTestConnection}
                    disabled={testingConnection || !newSensor.ip_address}
                    style={{
                      padding: '12px 24px',
                      background: (testingConnection || !newSensor.ip_address) ? '#ccc' : '#4caf50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: (testingConnection || !newSensor.ip_address) ? 'not-allowed' : 'pointer',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    {testingConnection ? '⏳ Testando...' : '🔌 Testar Conexão SNMP'}
                  </button>
                  
                  {connectionTestResult && (
                    <div style={{
                      marginTop: '12px',
                      padding: '12px',
                      borderRadius: '6px',
                      background: connectionTestResult.success ? '#d4edda' : '#f8d7da',
                      border: `1px solid ${connectionTestResult.success ? '#28a745' : '#dc3545'}`,
                      color: connectionTestResult.success ? '#155724' : '#721c24'
                    }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                        {connectionTestResult.success ? '✅ Sucesso!' : '❌ Falha'}
                      </div>
                      <div style={{ fontSize: '13px' }}>
                        {connectionTestResult.message}
                      </div>
                      {connectionTestResult.details && (
                        <div style={{ fontSize: '12px', marginTop: '8px', opacity: 0.8 }}>
                          <strong>Detalhes:</strong> {JSON.stringify(connectionTestResult.details, null, 2)}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Configurações Azure */}
            {newSensor.category === 'azure' && (
              <div className="form-section">
                <h3>☁️ Configurações Azure</h3>
                <div className="info-box" style={{ marginBottom: '15px', background: '#e3f2fd', padding: '12px', borderRadius: '6px', border: '1px solid #2196f3' }}>
                  <p style={{ margin: 0, fontSize: '13px' }}>
                    ℹ️ <strong>Como obter credenciais Azure:</strong>
                  </p>
                  <ol style={{ margin: '8px 0 0 20px', fontSize: '12px', lineHeight: '1.6' }}>
                    <li>Acesse o <strong>Azure Portal</strong></li>
                    <li>Vá em <strong>Azure Active Directory</strong> → <strong>App registrations</strong></li>
                    <li>Clique em <strong>New registration</strong></li>
                    <li>Copie o <strong>Application (client) ID</strong> e <strong>Directory (tenant) ID</strong></li>
                    <li>Em <strong>Certificates & secrets</strong>, crie um <strong>New client secret</strong></li>
                    <li>Em <strong>Subscriptions</strong>, copie o <strong>Subscription ID</strong></li>
                    <li>Dê permissões de <strong>Reader</strong> ao App Registration</li>
                  </ol>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Subscription ID: *</label>
                    <input
                      type="text"
                      value={newSensor.azure_subscription_id}
                      onChange={(e) => setNewSensor({...newSensor, azure_subscription_id: e.target.value})}
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    />
                    <small>ID da assinatura Azure</small>
                  </div>

                  <div className="form-group">
                    <label>Tenant ID: *</label>
                    <input
                      type="text"
                      value={newSensor.azure_tenant_id}
                      onChange={(e) => setNewSensor({...newSensor, azure_tenant_id: e.target.value})}
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    />
                    <small>ID do diretório (tenant)</small>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Client ID (Application ID): *</label>
                    <input
                      type="text"
                      value={newSensor.azure_client_id}
                      onChange={(e) => setNewSensor({...newSensor, azure_client_id: e.target.value})}
                      placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                    />
                    <small>ID da aplicação registrada</small>
                  </div>

                  <div className="form-group">
                    <label>Client Secret: *</label>
                    <input
                      type="password"
                      value={newSensor.azure_client_secret}
                      onChange={(e) => setNewSensor({...newSensor, azure_client_secret: e.target.value})}
                      placeholder="••••••••••••••••"
                    />
                    <small>Secret da aplicação</small>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Tipo de Recurso: *</label>
                    <select
                      value={newSensor.azure_resource_type}
                      onChange={(e) => setNewSensor({...newSensor, azure_resource_type: e.target.value})}
                    >
                      <option value="">-- Selecione --</option>
                      <option value="vm">Virtual Machine</option>
                      <option value="webapp">Web App</option>
                      <option value="sql">SQL Database</option>
                      <option value="storage">Storage Account</option>
                      <option value="aks">AKS Cluster</option>
                      <option value="function">Azure Function</option>
                      <option value="backup">Backup Vault</option>
                      <option value="loadbalancer">Load Balancer</option>
                      <option value="appgateway">Application Gateway</option>
                      <option value="cosmosdb">Cosmos DB</option>
                      <option value="redis">Redis Cache</option>
                      <option value="servicebus">Service Bus</option>
                      <option value="eventhub">Event Hub</option>
                      <option value="keyvault">Key Vault</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Nome do Recurso: *</label>
                    <input
                      type="text"
                      value={newSensor.azure_resource_name}
                      onChange={(e) => setNewSensor({...newSensor, azure_resource_name: e.target.value})}
                      placeholder="Ex: my-webapp, my-vm"
                    />
                    <small>Nome do recurso no Azure</small>
                  </div>
                </div>

                {/* Botão de Teste de Conexão Azure */}
                <div style={{ marginTop: '15px', marginBottom: '15px' }}>
                  <button
                    type="button"
                    onClick={handleTestConnection}
                    disabled={testingConnection}
                    style={{
                      padding: '12px 24px',
                      background: testingConnection ? '#ccc' : '#2196f3',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: testingConnection ? 'not-allowed' : 'pointer',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    {testingConnection ? '⏳ Testando...' : '🔌 Testar Conexão Azure'}
                  </button>
                  
                  {connectionTestResult && (
                    <div style={{
                      marginTop: '12px',
                      padding: '12px',
                      borderRadius: '6px',
                      background: connectionTestResult.success ? '#d4edda' : '#f8d7da',
                      border: `1px solid ${connectionTestResult.success ? '#28a745' : '#dc3545'}`,
                      color: connectionTestResult.success ? '#155724' : '#721c24'
                    }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                        {connectionTestResult.success ? '✅ Sucesso!' : '❌ Falha'}
                      </div>
                      <div style={{ fontSize: '13px' }}>
                        {connectionTestResult.message}
                      </div>
                      {connectionTestResult.details && (
                        <div style={{ fontSize: '12px', marginTop: '8px', opacity: 0.8 }}>
                          {JSON.stringify(connectionTestResult.details, null, 2)}
                        </div>
                      )}
                      {connectionTestResult.error && (
                        <div style={{ fontSize: '12px', marginTop: '8px', fontFamily: 'monospace', background: 'rgba(0,0,0,0.1)', padding: '8px', borderRadius: '4px' }}>
                          {connectionTestResult.error}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Configurações HTTP */}
            {newSensor.category === 'network' && (
              <div className="form-section">
                <h3>🌐 Configurações HTTP</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label>URL: *</label>
                    <input
                      type="text"
                      value={newSensor.http_url}
                      onChange={(e) => setNewSensor({...newSensor, http_url: e.target.value})}
                      placeholder="https://example.com"
                    />
                    <small>URL completa para monitorar</small>
                  </div>

                  <div className="form-group">
                    <label>Método HTTP:</label>
                    <select
                      value={newSensor.http_method}
                      onChange={(e) => setNewSensor({...newSensor, http_method: e.target.value})}
                    >
                      <option value="GET">GET</option>
                      <option value="POST">POST</option>
                      <option value="HEAD">HEAD</option>
                    </select>
                  </div>
                </div>

                {/* Botão de Teste de Conexão HTTP */}
                <div style={{ marginTop: '15px', marginBottom: '15px' }}>
                  <button
                    type="button"
                    onClick={handleTestConnection}
                    disabled={testingConnection || !newSensor.http_url}
                    style={{
                      padding: '12px 24px',
                      background: (testingConnection || !newSensor.http_url) ? '#ccc' : '#ff9800',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: (testingConnection || !newSensor.http_url) ? 'not-allowed' : 'pointer',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    {testingConnection ? '⏳ Testando...' : '🔌 Testar Conexão HTTP'}
                  </button>
                  
                  {connectionTestResult && (
                    <div style={{
                      marginTop: '12px',
                      padding: '12px',
                      borderRadius: '6px',
                      background: connectionTestResult.success ? '#d4edda' : '#f8d7da',
                      border: `1px solid ${connectionTestResult.success ? '#28a745' : '#dc3545'}`,
                      color: connectionTestResult.success ? '#155724' : '#721c24'
                    }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                        {connectionTestResult.success ? '✅ Sucesso!' : '❌ Falha'}
                      </div>
                      <div style={{ fontSize: '13px' }}>
                        {connectionTestResult.message}
                      </div>
                      {connectionTestResult.details && (
                        <div style={{ fontSize: '12px', marginTop: '8px', opacity: 0.8 }}>
                          <strong>Status Code:</strong> {connectionTestResult.details.status_code}<br/>
                          <strong>Tempo de Resposta:</strong> {connectionTestResult.details.response_time}ms
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="form-row">
              <div className="form-group">
                <label>Limite de Aviso (%):</label>
                <input
                  type="number"
                  value={newSensor.threshold_warning}
                  onChange={(e) => setNewSensor({...newSensor, threshold_warning: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Limite Crítico (%):</label>
                <input
                  type="number"
                  value={newSensor.threshold_critical}
                  onChange={(e) => setNewSensor({...newSensor, threshold_critical: e.target.value})}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Descrição:</label>
              <textarea
                value={newSensor.description}
                onChange={(e) => setNewSensor({...newSensor, description: e.target.value})}
                placeholder="Descrição opcional do sensor..."
                rows="3"
              />
            </div>

            <div className="modal-actions">
              {addError && (
                <div style={{ color: '#dc3545', fontSize: '13px', marginBottom: '8px', width: '100%' }}>
                  ❌ {addError}
                </div>
              )}
              {addSuccess && (
                <div style={{ color: '#28a745', fontSize: '13px', marginBottom: '8px', width: '100%' }}>
                  ✅ Sensor adicionado com sucesso!
                </div>
              )}
              <button className="btn-cancel" onClick={() => { setShowAddModal(false); resetForm(); setAddError(''); setAddSuccess(false); }}>
                Cancelar
              </button>
              <button className="btn-save" type="button" onClick={handleAddSensor} disabled={addSuccess}>
                Adicionar Sensor
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Editar Sensor */}
      {showEditModal && editingSensor && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Editar Sensor</h2>
            <div className="form-group">
              <label>Nome do Sensor:</label>
              <input
                type="text"
                value={editingSensor.name}
                onChange={(e) => setEditingSensor({...editingSensor, name: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Limite de Aviso (%):</label>
              <input
                type="number"
                value={editingSensor.threshold_warning}
                onChange={(e) => setEditingSensor({...editingSensor, threshold_warning: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Limite Crítico (%):</label>
              <input
                type="number"
                value={editingSensor.threshold_critical}
                onChange={(e) => setEditingSensor({...editingSensor, threshold_critical: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label>Descrição:</label>
              <textarea
                value={editingSensor.description}
                onChange={(e) => setEditingSensor({...editingSensor, description: e.target.value})}
                rows="3"
              />
            </div>
            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setShowEditModal(false)}>
                Cancelar
              </button>
              <button className="btn-save" onClick={handleUpdateSensor}>
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SensorLibrary;
