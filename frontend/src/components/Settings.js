import React, { useState, useEffect } from 'react';
import api from '../services/api';
import ThresholdConfig from './ThresholdConfig';
import SecurityMonitor from './SecurityMonitor';
import MFASetup from './MFASetup';
import SystemReset from './SystemReset';
import Credentials from './Credentials';
import TestTools from './TestTools';
import DefaultSensorProfiles from './DefaultSensorProfiles';
import './Management.css';
import './Settings.css';

function Settings({ onNavigate }) {
  const [activeTab, setActiveTab] = useState('appearance');
  const [notificationConfig, setNotificationConfig] = useState({
    email: { enabled: false, smtp_server: '', smtp_port: 587, smtp_user: '', smtp_password: '', from_email: '', to_emails: [], use_tls: true },
    twilio: { enabled: false, account_sid: '', auth_token: '', from_number: '', to_numbers: [] },
    teams: { enabled: false, webhook_url: '' },
    whatsapp: { enabled: false, account_sid: '', auth_token: '', from_number: '', phone_numbers: [] },
    telegram: { enabled: false, bot_token: '', chat_ids: [] },
    topdesk: { enabled: false, url: '', username: '', password: '', operator_group: '', category: '', subcategory: '' },
    glpi: { enabled: false, url: '', app_token: '', user_token: '', entity_id: '', category_id: '', urgency: 4, impact: 3 },
    zammad: { enabled: false, url: '', api_token: '', group_id: '', customer_id: '', priority: 2, tags: 'monitoramento,automatico' },
    dynamics365: { enabled: false, url: '', tenant_id: '', client_id: '', client_secret: '', resource: '', api_version: '9.2', incident_type: 'incident', priority: 2, owner_id: '' },
    kiro_conecta: { enabled: false, url: 'http://conecta.techbiz.com.br:8000', frontend_url: 'http://conecta.techbiz.com.br:5173', user_email: '', category: 'Monitoramento', subcategory: 'Alerta Automatico' }
  });
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  // Security/Authentication settings state
  const [authConfig, setAuthConfig] = useState({
    ldap: { enabled: false, server: '', port: 389, use_ssl: false, base_dn: '', bind_dn: '', bind_password: '', user_filter: '(uid={username})', group_filter: '', admin_group: '', user_group: '', viewer_group: '' },
    saml: { enabled: false, entity_id: '', sso_url: '', slo_url: '', x509_cert: '', attribute_mapping: { email: 'email', name: 'name', role: 'role' } },
    oauth2: { enabled: false, provider: 'generic', client_id: '', client_secret: '', authorization_url: '', token_url: '', userinfo_url: '', scope: 'openid profile email', attribute_mapping: { email: 'email', name: 'name', role: 'role' } },
    azure_ad: { enabled: false, tenant_id: '', client_id: '', client_secret: '', redirect_uri: '', admin_group_id: '', user_group_id: '', viewer_group_id: '' },
    google: { enabled: false, client_id: '', client_secret: '', redirect_uri: '', hosted_domain: '', admin_group: '', user_group: '', viewer_group: '' },
    okta: { enabled: false, domain: '', client_id: '', client_secret: '', redirect_uri: '', admin_group: '', user_group: '', viewer_group: '' },
    mfa: { enabled: false, method: 'totp', issuer: 'CorujaMonitor', enforce_for_admins: true, enforce_for_all: false },
    password_policy: { min_length: 8, require_uppercase: true, require_lowercase: true, require_numbers: true, require_special: true, expiry_days: 90, prevent_reuse: 5 },
    session: { timeout_minutes: 480, max_concurrent_sessions: 3, remember_me_days: 30 }
  });
  
  // Admin tools state
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [actionInProgress, setActionInProgress] = useState(false);
  const [actionModal, setActionModal] = useState({ show: false, title: '', message: '', progress: [] });
  const [showSystemReset, setShowSystemReset] = useState(false);

  // Backup state
  const [backups, setBackups] = useState([]);
  const [loadingBackups, setLoadingBackups] = useState(false);
  const [creatingBackup, setCreatingBackup] = useState(false);
  const [restoringBackup, setRestoringBackup] = useState(false);

  // Advanced settings state
  const [advancedSettings, setAdvancedSettings] = useState({
    dataRetention: {
      metricsHistory: 90,
      incidentsHistory: 180
    },
    collectionIntervals: {
      defaultInterval: 60,
      fastInterval: 30
    },
    thresholds: {
      cpuWarning: 80,
      cpuCritical: 95,
      memoryWarning: 80,
      memoryCritical: 95,
      diskWarning: 80,
      diskCritical: 95
    },
    autoDiscovery: {
      snmpEnabled: true,
      autoCreateSensors: true,
      autoRemediation: false
    },
    performance: {
      maxSensorsPerProbe: 1000,
      collectionThreads: 10
    }
  });

  // Appearance settings state
  const [appearanceSettings, setAppearanceSettings] = useState({
    darkMode: false,
    compactMode: false,
    fontSize: 'medium',
    colorScheme: 'blue'
  });

  useEffect(() => {
    loadSettings();
  }, []);

  useEffect(() => {
    // Carregar backups quando a aba backup estiver ativa
    if (activeTab === 'backup') {
      loadBackups();
    }
  }, [activeTab]);

  const loadBackups = async () => {
    setLoadingBackups(true);
    try {
      const response = await api.get('/backup/list');
      setBackups(response.data.backups);
    } catch (error) {
      console.error('Erro ao carregar backups:', error);
      alert('Erro ao carregar lista de backups');
    } finally {
      setLoadingBackups(false);
    }
  };

  const createBackup = async () => {
    if (!window.confirm('Deseja criar um novo backup do banco de dados?')) return;
    
    setCreatingBackup(true);
    try {
      const response = await api.post('/backup/create');
      alert(response.data.message);
      loadBackups();
    } catch (error) {
      console.error('Erro ao criar backup:', error);
      alert('Erro ao criar backup: ' + (error.response?.data?.detail || error.message));
    } finally {
      setCreatingBackup(false);
    }
  };

  const restoreBackup = async (filename) => {
    if (!window.confirm(`⚠️ ATENÇÃO: Restaurar o backup "${filename}" irá SUBSTITUIR todos os dados atuais do banco de dados!\n\nEsta ação NÃO pode ser desfeita!\n\nDeseja continuar?`)) return;
    
    setRestoringBackup(true);
    try {
      const response = await api.post(`/backup/restore/${filename}`);
      alert(response.data.message + '\n\nA página será recarregada em 3 segundos...');
      setTimeout(() => window.location.reload(), 3000);
    } catch (error) {
      console.error('Erro ao restaurar backup:', error);
      alert('Erro ao restaurar backup: ' + (error.response?.data?.detail || error.message));
    } finally {
      setRestoringBackup(false);
    }
  };

  const downloadBackup = (filename) => {
    window.open(`/backup/download/${filename}`, '_blank');
  };

  const deleteBackup = async (filename) => {
    if (!window.confirm(`Deseja deletar o backup "${filename}"?`)) return;
    
    try {
      const response = await api.delete(`/backup/delete/${filename}`);
      alert(response.data.message);
      loadBackups();
    } catch (error) {
      console.error('Erro ao deletar backup:', error);
      alert('Erro ao deletar backup: ' + (error.response?.data?.detail || error.message));
    }
  };

  const loadSettings = async () => {
    try {
      // Load notification config
      const notifResponse = await api.get('/notifications/config');
      if (notifResponse.data.notification_config) {
        setNotificationConfig({
          email: notifResponse.data.notification_config.email || { enabled: false, smtp_server: '', smtp_port: 587, smtp_user: '', smtp_password: '', from_email: '', to_emails: [], use_tls: true },
          twilio: notifResponse.data.notification_config.twilio || { enabled: false, account_sid: '', auth_token: '', from_number: '', to_numbers: [] },
          teams: notifResponse.data.notification_config.teams || { enabled: false, webhook_url: '' },
          whatsapp: notifResponse.data.notification_config.whatsapp || { enabled: false, account_sid: '', auth_token: '', from_number: '', phone_numbers: [] },
          telegram: notifResponse.data.notification_config.telegram || { enabled: false, bot_token: '', chat_ids: [] },
          topdesk: notifResponse.data.notification_config.topdesk || { enabled: false, url: '', username: '', password: '', operator_group: '', category: '', subcategory: '' },
          glpi: notifResponse.data.notification_config.glpi || { enabled: false, url: '', app_token: '', user_token: '', entity_id: '', category_id: '', urgency: 4, impact: 3 },
          zammad: notifResponse.data.notification_config.zammad || { enabled: false, url: '', api_token: '', group_id: '', customer_id: '', priority: 2, tags: 'monitoramento,automatico' },
          dynamics365: notifResponse.data.notification_config.dynamics365 || { enabled: false, url: '', tenant_id: '', client_id: '', client_secret: '', resource: '', api_version: '9.2', incident_type: 'incident', priority: 2, owner_id: '' },
          kiro_conecta: notifResponse.data.notification_config.kiro_conecta || { enabled: false, url: 'http://conecta.techbiz.com.br:8000', frontend_url: 'http://conecta.techbiz.com.br:5173', user_email: '', category: 'Monitoramento', subcategory: 'Alerta Automatico' }
        });
      }

      // Load users
      const usersResponse = await api.get('/users');
      setUsers(usersResponse.data);
      
      // Load maintenance mode status
      const maintenanceResponse = await api.get('/admin/maintenance-mode/status');
      setMaintenanceMode(maintenanceResponse.data.enabled || false);

      // Load advanced settings from localStorage
      const savedAdvanced = localStorage.getItem('coruja_advanced_settings');
      if (savedAdvanced) {
        setAdvancedSettings(JSON.parse(savedAdvanced));
      }

      // Load appearance settings from localStorage
      const savedAppearance = localStorage.getItem('coruja_appearance_settings');
      if (savedAppearance) {
        const appearance = JSON.parse(savedAppearance);
        setAppearanceSettings(appearance);
        // Apply dark mode immediately
        if (appearance.darkMode) {
          document.body.classList.add('dark-mode');
        }
      }

      // Load authentication/security config
      try {
        const authResponse = await api.get('/auth-config');
        if (authResponse.data) {
          setAuthConfig({
            ldap: authResponse.data.ldap || authConfig.ldap,
            saml: authResponse.data.saml || authConfig.saml,
            oauth2: authResponse.data.oauth2 || authConfig.oauth2,
            azure_ad: authResponse.data.azure_ad || authConfig.azure_ad,
            google: authResponse.data.google || authConfig.google,
            okta: authResponse.data.okta || authConfig.okta,
            mfa: authResponse.data.mfa || authConfig.mfa,
            password_policy: authResponse.data.password_policy || authConfig.password_policy,
            session: authResponse.data.session || authConfig.session
          });
        }
      } catch (error) {
        console.log('Auth config not found or error loading:', error);
      }
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
    } finally {
      setLoading(false);
    }
  };

  const showActionModal = (title, message) => {
    setActionModal({ show: true, title, message, progress: [message] });
  };

  const addProgressMessage = (message) => {
    setActionModal(prev => ({
      ...prev,
      progress: [...prev.progress, message]
    }));
  };

  const closeActionModal = () => {
    setActionModal({ show: false, title: '', message: '', progress: [] });
    setActionInProgress(false);
  };

  const handleToggleMaintenanceMode = async () => {
    if (actionInProgress) return;
    
    setActionInProgress(true);
    const newMode = !maintenanceMode;
    
    showActionModal(
      newMode ? 'Ativando Modo Manutenção' : 'Desativando Modo Manutenção',
      newMode ? 'Colocando sistema em manutenção...' : 'Reativando sistema...'
    );
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      addProgressMessage('Verificando permissões...');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      const response = await api.post('/admin/maintenance-mode', {
        enabled: newMode,
        message: 'Sistema em manutenção. Voltamos em breve.'
      });
      
      addProgressMessage(response.data.message);
      setMaintenanceMode(newMode);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      addProgressMessage('✅ Concluído!');
      
      setTimeout(closeActionModal, 2000);
    } catch (error) {
      addProgressMessage('❌ Erro: ' + (error.response?.data?.detail || error.message));
      setTimeout(closeActionModal, 3000);
    }
  };

  const handleResetProbes = async () => {
    if (actionInProgress) return;
    if (!window.confirm('Deseja realmente resetar todas as probes? Elas precisarão reconectar.')) return;
    
    setActionInProgress(true);
    showActionModal('Reset de Probes', 'Iniciando reset de probes...');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      addProgressMessage('Buscando probes ativas...');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      addProgressMessage('Limpando heartbeats...');
      
      const response = await api.post('/admin/reset-probes');
      
      addProgressMessage(response.data.message);
      addProgressMessage('✅ Probes resetadas! Aguarde reconexão...');
      
      setTimeout(closeActionModal, 3000);
    } catch (error) {
      addProgressMessage('❌ Erro: ' + (error.response?.data?.detail || error.message));
      setTimeout(closeActionModal, 3000);
    }
  };

  const handleRestartSystem = async () => {
    if (actionInProgress) return;
    if (!window.confirm('Deseja realmente reiniciar o sistema? Haverá downtime de 30-60 segundos.')) return;
    
    setActionInProgress(true);
    showActionModal('Reiniciando Sistema', 'Preparando para reiniciar...');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      addProgressMessage('Salvando estado atual...');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      addProgressMessage('Agendando reinício dos containers...');
      
      const response = await api.post('/admin/restart-system');
      
      addProgressMessage(response.data.message);
      addProgressMessage('⏳ Sistema reiniciando...');
      addProgressMessage('Aguarde 30-60 segundos e recarregue a página.');
      
      setTimeout(() => {
        addProgressMessage('✅ Você pode recarregar a página agora!');
      }, 30000);
    } catch (error) {
      addProgressMessage('❌ Erro: ' + (error.response?.data?.detail || error.message));
      setTimeout(closeActionModal, 3000);
    }
  };

  const handleBackupDatabase = async () => {
    if (actionInProgress) return;
    
    setActionInProgress(true);
    showActionModal('Backup do Banco de Dados', 'Iniciando backup...');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      addProgressMessage('Conectando ao PostgreSQL...');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      addProgressMessage('Executando pg_dump...');
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      addProgressMessage('Exportando dados...');
      
      const response = await api.post('/admin/backup-database');
      
      addProgressMessage(`✅ Backup criado: ${response.data.backup_file}`);
      addProgressMessage(`Tamanho: ${response.data.size_mb} MB`);
      
      setTimeout(closeActionModal, 3000);
    } catch (error) {
      addProgressMessage('❌ Erro: ' + (error.response?.data?.detail || error.message));
      setTimeout(closeActionModal, 3000);
    }
  };

  const handleClearCache = async () => {
    if (actionInProgress) return;
    if (!window.confirm('Deseja limpar todo o cache do Redis?')) return;
    
    setActionInProgress(true);
    showActionModal('Limpando Cache', 'Conectando ao Redis...');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      addProgressMessage('Executando FLUSHDB...');
      
      const response = await api.post('/admin/clear-cache');
      
      addProgressMessage(response.data.message);
      addProgressMessage('✅ Cache limpo com sucesso!');
      
      setTimeout(closeActionModal, 2000);
    } catch (error) {
      addProgressMessage('❌ Erro: ' + (error.response?.data?.detail || error.message));
      setTimeout(closeActionModal, 3000);
    }
  };

  const handleViewLogs = async () => {
    if (actionInProgress) return;
    
    setActionInProgress(true);
    showActionModal('Logs do Sistema', 'Carregando logs da API...');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      const response = await api.get('/admin/logs?service=api&lines=50');
      
      addProgressMessage('✅ Logs carregados!');
      addProgressMessage('');
      addProgressMessage('--- ÚLTIMAS 50 LINHAS ---');
      
      const logs = response.data.logs.split('\n');
      logs.slice(-50).forEach(line => {
        if (line.trim()) addProgressMessage(line);
      });
      
    } catch (error) {
      addProgressMessage('❌ Erro: ' + (error.response?.data?.detail || error.message));
      setTimeout(closeActionModal, 3000);
    }
  };

  const handleSaveNotifications = async () => {
    setSaving(true);
    try {
      await api.put('/notifications/config', notificationConfig);
      alert('Configurações de notificação salvas com sucesso!');
    } catch (error) {
      alert('Erro ao salvar configurações: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async (channel) => {
    // Verificar se a configuração está ativada localmente
    const channelConfig = notificationConfig[channel];
    if (!channelConfig || !channelConfig.enabled) {
      alert(`⚠️ Atenção!\n\nVocê precisa primeiro:\n1. Marcar "${channel}" como "Ativado"\n2. Preencher os campos obrigatórios\n3. Clicar em "Salvar Configurações"\n4. Depois clicar em "Testar Integração"`);
      return;
    }
    
    // Verificar campos obrigatórios do TOPdesk
    if (channel === 'topdesk') {
      if (!channelConfig.url || !channelConfig.username || !channelConfig.password) {
        alert(`⚠️ Campos obrigatórios não preenchidos!\n\nPara TOPdesk você precisa preencher:\n✓ URL do TOPdesk\n✓ Usuário (Login)\n✓ Senha\n\nDepois clique em "Salvar Configurações" antes de testar.`);
        return;
      }
    }
    
    try {
      const response = await api.post(`/notifications/test/${channel}`);
      alert(`✅ Sucesso!\n\n${response.data.message || `Notificação de teste enviada via ${channel}!`}`);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      
      // Verificar se é erro de configuração não salva
      if (errorMsg.includes('not found') || errorMsg.includes('not configured') || errorMsg.includes('Configuration not found')) {
        alert(`⚠️ Configuração não encontrada no servidor!\n\nVocê JÁ PREENCHEU os campos, mas ainda não salvou.\n\nPróximo passo:\n1. Role a página até o FINAL\n2. Clique no botão "💾 Salvar Configurações"\n3. Aguarde a mensagem de sucesso\n4. Depois volte aqui e clique em "Testar Integração"`);
      } else if (errorMsg.includes('authentication') || errorMsg.includes('credentials') || errorMsg.includes('401') || errorMsg.includes('403')) {
        alert(`❌ Erro de Autenticação!\n\nUsuário ou senha incorretos.\n\nVerifique:\n✓ URL: ${channelConfig.url}\n✓ Usuário: ${channelConfig.username}\n✓ Senha está correta?\n\nCorreção:\n1. Verifique as credenciais\n2. Clique em "Salvar Configurações"\n3. Teste novamente`);
      } else if (errorMsg.includes('connection') || errorMsg.includes('timeout') || errorMsg.includes('network')) {
        const serviceName = channel === 'kiro_conecta' ? 'Conecta' : channel === 'topdesk' ? 'TOPdesk' : channel;
        alert(`❌ Erro de Conexão!\n\nNão foi possível conectar ao ${serviceName}.\n\nVerifique:\n✓ URL está correta? ${channelConfig.url}\n✓ O servidor está acessível a partir do container Docker?\n✓ DNS resolve dentro do Docker?\n✓ Firewall bloqueando?\n\nErro: ${errorMsg}`);
      } else {
        alert(`❌ Erro ao testar ${channel}:\n\n${errorMsg}\n\nSe o erro persistir, verifique os logs do sistema.`);
      }
    }
  };

  const handleSaveAdvancedSettings = () => {
    localStorage.setItem('coruja_advanced_settings', JSON.stringify(advancedSettings));
    alert('Configurações avançadas salvas com sucesso!');
  };

  const handleSaveAppearanceSettings = () => {
    localStorage.setItem('coruja_appearance_settings', JSON.stringify(appearanceSettings));
    
    // Dark mode is always on — never remove it
    document.body.classList.add('dark-mode');
    
    alert('Configurações de aparência salvas com sucesso!');
  };

  const handleSaveAuthConfig = async () => {
    setSaving(true);
    try {
      await api.put('/auth-config', authConfig);
      alert('Configurações de segurança salvas com sucesso!');
    } catch (error) {
      alert('Erro ao salvar configurações de segurança: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  const handleTestAuthConfig = async (provider) => {
    try {
      const response = await api.post(`/auth-config/test/${provider}`);
      alert(`✅ Teste bem-sucedido!\n\n${response.data.message || `Conexão com ${provider} funcionando corretamente.`}`);
    } catch (error) {
      alert(`❌ Erro ao testar ${provider}:\n\n${error.response?.data?.detail || error.message}`);
    }
  };

  const renderNotifications = () => (
    <div className="settings-section">
      <h2>📢 Integrações e Notificações</h2>
      <p className="section-description">
        Configure canais de notificação para alertas críticos e integrações com sistemas de Service Desk.
        Ambientes de PRODUÇÃO podem acionar ligações automáticas e criar chamados automaticamente.
      </p>

      {/* Email */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">📧</span>
            <h3>E-mail (SMTP)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.email.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                email: { ...notificationConfig.email, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.email.enabled && (
          <div className="integration-config">
            <div className="form-row">
              <div className="form-group">
                <label>Servidor SMTP:</label>
                <input
                  type="text"
                  value={notificationConfig.email.smtp_server}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    email: { ...notificationConfig.email, smtp_server: e.target.value }
                  })}
                  placeholder="smtp.gmail.com"
                />
                <small>Servidor SMTP para envio de e-mails</small>
              </div>
              <div className="form-group">
                <label>Porta SMTP:</label>
                <input
                  type="number"
                  value={notificationConfig.email.smtp_port}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    email: { ...notificationConfig.email, smtp_port: parseInt(e.target.value) }
                  })}
                  placeholder="587"
                />
                <small>Porta padrão: 587 (TLS) ou 465 (SSL)</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Usuário SMTP:</label>
                <input
                  type="text"
                  value={notificationConfig.email.smtp_user}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    email: { ...notificationConfig.email, smtp_user: e.target.value }
                  })}
                  placeholder="monitor@empresa.com"
                />
              </div>
              <div className="form-group">
                <label>Senha SMTP:</label>
                <input
                  type="password"
                  value={notificationConfig.email.smtp_password}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    email: { ...notificationConfig.email, smtp_password: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>E-mail de Origem:</label>
                <input
                  type="email"
                  value={notificationConfig.email.from_email}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    email: { ...notificationConfig.email, from_email: e.target.value }
                  })}
                  placeholder="coruja-monitor@empresa.com"
                />
                <small>E-mail que aparecerá como remetente</small>
              </div>
              <div className="form-group">
                <label>E-mails de Destino (separados por vírgula):</label>
                <input
                  type="text"
                  value={notificationConfig.email.to_emails?.join(', ') || ''}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    email: { 
                      ...notificationConfig.email, 
                      to_emails: e.target.value.split(',').map(n => n.trim()).filter(n => n)
                    }
                  })}
                  placeholder="ti@empresa.com, suporte@empresa.com"
                />
                <small>E-mails que receberão os alertas</small>
              </div>
            </div>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={notificationConfig.email.use_tls}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    email: { ...notificationConfig.email, use_tls: e.target.checked }
                  })}
                />
                Usar TLS/STARTTLS (recomendado)
              </label>
              <small>Desmarque apenas se usar SSL na porta 465</small>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('email')}>
              Testar E-mail
            </button>
          </div>
        )}
      </div>

      {/* Twilio */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">📞</span>
            <h3>Twilio (Ligações e SMS)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.twilio.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                twilio: { ...notificationConfig.twilio, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.twilio.enabled && (
          <div className="integration-config">
            <div className="form-row">
              <div className="form-group">
                <label>Account SID:</label>
                <input
                  type="text"
                  value={notificationConfig.twilio.account_sid}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    twilio: { ...notificationConfig.twilio, account_sid: e.target.value }
                  })}
                  placeholder="ACxxxxxxxxxxxxx"
                />
              </div>
              <div className="form-group">
                <label>Auth Token:</label>
                <input
                  type="password"
                  value={notificationConfig.twilio.auth_token}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    twilio: { ...notificationConfig.twilio, auth_token: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Número de Origem:</label>
                <input
                  type="text"
                  value={notificationConfig.twilio.from_number}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    twilio: { ...notificationConfig.twilio, from_number: e.target.value }
                  })}
                  placeholder="+5511999999999"
                />
              </div>
              <div className="form-group">
                <label>Números de Destino (separados por vírgula):</label>
                <input
                  type="text"
                  value={notificationConfig.twilio.to_numbers?.join(', ') || ''}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    twilio: { 
                      ...notificationConfig.twilio, 
                      to_numbers: e.target.value.split(',').map(n => n.trim()).filter(n => n)
                    }
                  })}
                  placeholder="+5511888888888, +5511777777777"
                />
              </div>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('twilio')}>
              Testar Ligação
            </button>
          </div>
        )}
      </div>

      {/* Teams */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">💬</span>
            <h3>Microsoft Teams</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.teams.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                teams: { ...notificationConfig.teams, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.teams.enabled && (
          <div className="integration-config">
            <div className="form-group">
              <label>Webhook URL:</label>
              <input
                type="text"
                value={notificationConfig.teams.webhook_url}
                onChange={(e) => setNotificationConfig({
                  ...notificationConfig,
                  teams: { ...notificationConfig.teams, webhook_url: e.target.value }
                })}
                placeholder="https://outlook.office.com/webhook/..."
              />
              <small>Configure um Incoming Webhook no seu canal do Teams</small>
            </div>
            <div className="info-box" style={{ marginBottom: '10px', background: '#fff3cd', border: '1px solid #ffc107', padding: '10px', borderRadius: '5px' }}>
              <p style={{ margin: 0, color: '#856404', fontSize: '13px' }}>
                ⚠️ <strong>Importante:</strong> Clique em "Salvar Configurações" no final da página antes de testar!
              </p>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('teams')}>
              Testar Mensagem
            </button>
          </div>
        )}
      </div>

      {/* WhatsApp */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">📱</span>
            <h3>WhatsApp (via Twilio)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.whatsapp.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                whatsapp: { ...notificationConfig.whatsapp, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.whatsapp.enabled && (
          <div className="integration-config">
            <div className="form-row">
              <div className="form-group">
                <label>Account SID (Twilio):</label>
                <input
                  type="text"
                  value={notificationConfig.whatsapp.account_sid || ''}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    whatsapp: { ...notificationConfig.whatsapp, account_sid: e.target.value }
                  })}
                  placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                />
              </div>
              <div className="form-group">
                <label>Auth Token (Twilio):</label>
                <input
                  type="password"
                  value={notificationConfig.whatsapp.auth_token || ''}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    whatsapp: { ...notificationConfig.whatsapp, auth_token: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Número de Origem (Twilio WhatsApp):</label>
                <input
                  type="text"
                  value={notificationConfig.whatsapp.from_number || ''}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    whatsapp: { ...notificationConfig.whatsapp, from_number: e.target.value }
                  })}
                  placeholder="+14155238886"
                />
              </div>
              <div className="form-group">
                <label>Números Destino (separados por vírgula):</label>
                <input
                  type="text"
                  value={notificationConfig.whatsapp.phone_numbers?.join(', ') || ''}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    whatsapp: { 
                      ...notificationConfig.whatsapp, 
                      phone_numbers: e.target.value.split(',').map(n => n.trim()).filter(n => n)
                    }
                  })}
                  placeholder="+5531991888803, +5531999999999"
                />
              </div>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('whatsapp')}>
              Testar Mensagem
            </button>
          </div>
        )}
      </div>

      {/* Telegram */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🤖</span>
            <h3>Telegram</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.telegram.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                telegram: { ...notificationConfig.telegram, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.telegram.enabled && (
          <div className="integration-config">
            <div className="form-row">
              <div className="form-group">
                <label>Bot Token:</label>
                <input
                  type="password"
                  value={notificationConfig.telegram.bot_token}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    telegram: { ...notificationConfig.telegram, bot_token: e.target.value }
                  })}
                  placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                />
                <small>Crie um bot com @BotFather no Telegram</small>
              </div>
              <div className="form-group">
                <label>Chat IDs (separados por vírgula):</label>
                <input
                  type="text"
                  value={notificationConfig.telegram.chat_ids?.join(', ') || ''}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    telegram: { 
                      ...notificationConfig.telegram, 
                      chat_ids: e.target.value.split(',').map(n => n.trim()).filter(n => n)
                    }
                  })}
                  placeholder="-123456789, -987654321"
                />
                <small>Use @userinfobot para descobrir seu Chat ID</small>
              </div>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('telegram')}>
              Testar Mensagem
            </button>
          </div>
        )}
      </div>

      {/* TOPdesk */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🎫</span>
            <h3>TOPdesk (Service Desk)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.topdesk.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                topdesk: { ...notificationConfig.topdesk, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.topdesk.enabled && (
          <div className="integration-config">
            <div className="info-box" style={{ marginBottom: '15px', background: '#fff3cd', border: '1px solid #ffc107', padding: '12px', borderRadius: '5px' }}>
              <p style={{ margin: 0, color: '#856404', fontSize: '13px', fontWeight: 'bold' }}>
                ⚠️ IMPORTANTE: Após preencher os campos, role até o FINAL da página e clique em "💾 Salvar Configurações" antes de testar!
              </p>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>URL do TOPdesk: <span style={{color: 'red'}}>*</span></label>
                <input
                  type="text"
                  value={notificationConfig.topdesk.url}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    topdesk: { ...notificationConfig.topdesk, url: e.target.value }
                  })}
                  placeholder="https://empresa.topdesk.net"
                />
                <small>URL base da sua instância TOPdesk (exemplo: https://empresa.topdesk.net)</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Usuário (Login): <span style={{color: 'red'}}>*</span></label>
                <input
                  type="text"
                  value={notificationConfig.topdesk.username}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    topdesk: { ...notificationConfig.topdesk, username: e.target.value }
                  })}
                  placeholder="coruja.monitor"
                />
                <small>Login do usuário no TOPdesk</small>
              </div>
              <div className="form-group">
                <label>Senha: <span style={{color: 'red'}}>*</span></label>
                <input
                  type="password"
                  value={notificationConfig.topdesk.password}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    topdesk: { ...notificationConfig.topdesk, password: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
                <small>Senha do usuário</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Grupo de Operadores:</label>
                <input
                  type="text"
                  value={notificationConfig.topdesk.operator_group}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    topdesk: { ...notificationConfig.topdesk, operator_group: e.target.value }
                  })}
                  placeholder="Infraestrutura"
                />
                <small>Grupo que receberá os chamados (opcional)</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Categoria:</label>
                <input
                  type="text"
                  value={notificationConfig.topdesk.category}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    topdesk: { ...notificationConfig.topdesk, category: e.target.value }
                  })}
                  placeholder="Infraestrutura"
                />
                <small>Categoria do chamado (opcional)</small>
              </div>
              <div className="form-group">
                <label>Subcategoria:</label>
                <input
                  type="text"
                  value={notificationConfig.topdesk.subcategory}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    topdesk: { ...notificationConfig.topdesk, subcategory: e.target.value }
                  })}
                  placeholder="Monitoramento"
                />
                <small>Subcategoria do chamado (opcional)</small>
              </div>
            </div>
            <div className="info-box" style={{ marginBottom: '10px', background: '#d1ecf1', border: '1px solid #0c5460', padding: '10px', borderRadius: '5px' }}>
              <p style={{ margin: 0, color: '#0c5460', fontSize: '12px' }}>
                <strong>Passo a passo:</strong><br/>
                1️⃣ Preencha URL, Usuário e Senha (campos obrigatórios *)<br/>
                2️⃣ Role até o FINAL da página<br/>
                3️⃣ Clique em "💾 Salvar Configurações"<br/>
                4️⃣ Volte aqui e clique em "Testar Criação de Chamado"
              </p>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('topdesk')}>
              Testar Criação de Chamado
            </button>
          </div>
        )}
      </div>

      {/* GLPI */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🎟️</span>
            <h3>GLPI (Service Management)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.glpi.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                glpi: { ...notificationConfig.glpi, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.glpi.enabled && (
          <div className="integration-config">
            <div className="form-row">
              <div className="form-group">
                <label>URL do GLPI:</label>
                <input
                  type="text"
                  value={notificationConfig.glpi.url}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    glpi: { ...notificationConfig.glpi, url: e.target.value }
                  })}
                  placeholder="https://glpi.empresa.com"
                />
                <small>URL base da sua instância GLPI</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>App Token:</label>
                <input
                  type="password"
                  value={notificationConfig.glpi.app_token}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    glpi: { ...notificationConfig.glpi, app_token: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
                <small>Token da aplicação (Setup > Geral > API)</small>
              </div>
              <div className="form-group">
                <label>User Token:</label>
                <input
                  type="password"
                  value={notificationConfig.glpi.user_token}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    glpi: { ...notificationConfig.glpi, user_token: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
                <small>Token do usuário (Meu Perfil > Configurações Remotas)</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>ID da Entidade:</label>
                <input
                  type="number"
                  value={notificationConfig.glpi.entity_id}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    glpi: { ...notificationConfig.glpi, entity_id: e.target.value }
                  })}
                  placeholder="0"
                />
                <small>ID da entidade (0 = Entidade raiz)</small>
              </div>
              <div className="form-group">
                <label>ID da Categoria:</label>
                <input
                  type="number"
                  value={notificationConfig.glpi.category_id}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    glpi: { ...notificationConfig.glpi, category_id: e.target.value }
                  })}
                  placeholder="1"
                />
                <small>ID da categoria de chamado</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Urgência:</label>
                <select
                  value={notificationConfig.glpi.urgency}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    glpi: { ...notificationConfig.glpi, urgency: parseInt(e.target.value) }
                  })}
                >
                  <option value="5">Muito Alta</option>
                  <option value="4">Alta</option>
                  <option value="3">Média</option>
                  <option value="2">Baixa</option>
                  <option value="1">Muito Baixa</option>
                </select>
              </div>
              <div className="form-group">
                <label>Impacto:</label>
                <select
                  value={notificationConfig.glpi.impact}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    glpi: { ...notificationConfig.glpi, impact: parseInt(e.target.value) }
                  })}
                >
                  <option value="5">Muito Alto</option>
                  <option value="4">Alto</option>
                  <option value="3">Médio</option>
                  <option value="2">Baixo</option>
                  <option value="1">Muito Baixo</option>
                </select>
              </div>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('glpi')}>
              Testar Criação de Ticket
            </button>
          </div>
        )}
      </div>

      {/* Zammad */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🎫</span>
            <h3>Zammad (Help Desk)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.zammad.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                zammad: { ...notificationConfig.zammad, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.zammad.enabled && (
          <div className="integration-config">
            <div className="form-row">
              <div className="form-group">
                <label>URL do Zammad:</label>
                <input
                  type="text"
                  value={notificationConfig.zammad.url}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    zammad: { ...notificationConfig.zammad, url: e.target.value }
                  })}
                  placeholder="https://zammad.empresa.com"
                />
                <small>URL base da sua instância Zammad</small>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Token de API:</label>
                <input
                  type="password"
                  value={notificationConfig.zammad.api_token}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    zammad: { ...notificationConfig.zammad, api_token: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
                <small>Token HTTP gerado em Perfil > Token Access</small>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>ID do Grupo:</label>
                <input
                  type="number"
                  value={notificationConfig.zammad.group_id}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    zammad: { ...notificationConfig.zammad, group_id: e.target.value }
                  })}
                  placeholder="1"
                />
                <small>ID do grupo que receberá os tickets (ex: 3)</small>
              </div>

              <div className="form-group">
                <label>ID do Cliente:</label>
                <input
                  type="number"
                  value={notificationConfig.zammad.customer_id}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    zammad: { ...notificationConfig.zammad, customer_id: e.target.value }
                  })}
                  placeholder="1"
                />
                <small>ID do usuário que criará os tickets (ex: 5)</small>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Prioridade:</label>
                <select
                  value={notificationConfig.zammad.priority}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    zammad: { ...notificationConfig.zammad, priority: parseInt(e.target.value) }
                  })}
                >
                  <option value="3">3 - Alta (Crítico)</option>
                  <option value="2">2 - Normal (Padrão)</option>
                  <option value="1">1 - Baixa</option>
                </select>
              </div>

              <div className="form-group">
                <label>Tags (separadas por vírgula):</label>
                <input
                  type="text"
                  value={notificationConfig.zammad.tags}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    zammad: { ...notificationConfig.zammad, tags: e.target.value }
                  })}
                  placeholder="monitoramento,automatico"
                />
                <small>Tags para identificar tickets automáticos</small>
              </div>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('zammad')}>
              Testar Criação de Ticket
            </button>
          </div>
        )}
      </div>

      {/* Microsoft Dynamics 365 */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🏢</span>
            <h3>Microsoft Dynamics 365 CRM</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.dynamics365.enabled}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                dynamics365: { ...notificationConfig.dynamics365, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {notificationConfig.dynamics365.enabled && (
          <div className="integration-config">
            <div className="info-box" style={{ marginBottom: '15px', background: '#d1ecf1', border: '1px solid #0c5460', padding: '12px', borderRadius: '5px' }}>
              <p style={{ margin: 0, color: '#0c5460', fontSize: '13px' }}>
                <strong>ℹ️ Pré-requisitos:</strong><br/>
                1. Aplicativo registrado no Azure AD<br/>
                2. Permissões: Dynamics CRM API access<br/>
                3. Application User criado no Dynamics 365<br/>
                4. Consulte: docs/integracoes-dynamics365-twilio-whatsapp.md
              </p>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>URL do Dynamics 365: <span style={{color: 'red'}}>*</span></label>
                <input
                  type="text"
                  value={notificationConfig.dynamics365.url}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, url: e.target.value }
                  })}
                  placeholder="https://suaempresa.crm2.dynamics.com"
                />
                <small>URL da sua instância Dynamics 365</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Azure AD Tenant ID: <span style={{color: 'red'}}>*</span></label>
                <input
                  type="text"
                  value={notificationConfig.dynamics365.tenant_id}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, tenant_id: e.target.value }
                  })}
                  placeholder="12345678-1234-1234-1234-123456789012"
                />
                <small>Directory (tenant) ID do Azure AD</small>
              </div>
              <div className="form-group">
                <label>Client ID: <span style={{color: 'red'}}>*</span></label>
                <input
                  type="text"
                  value={notificationConfig.dynamics365.client_id}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, client_id: e.target.value }
                  })}
                  placeholder="87654321-4321-4321-4321-210987654321"
                />
                <small>Application (client) ID do Azure AD</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Client Secret: <span style={{color: 'red'}}>*</span></label>
                <input
                  type="password"
                  value={notificationConfig.dynamics365.client_secret}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, client_secret: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
                <small>Client secret do aplicativo Azure AD</small>
              </div>
              <div className="form-group">
                <label>Resource URL:</label>
                <input
                  type="text"
                  value={notificationConfig.dynamics365.resource}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, resource: e.target.value }
                  })}
                  placeholder="https://suaempresa.crm2.dynamics.com"
                />
                <small>Geralmente igual à URL (deixe vazio para usar URL)</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Versão da API:</label>
                <input
                  type="text"
                  value={notificationConfig.dynamics365.api_version}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, api_version: e.target.value }
                  })}
                  placeholder="9.2"
                />
                <small>Versão da Web API (padrão: 9.2)</small>
              </div>
              <div className="form-group">
                <label>Tipo de Entidade:</label>
                <select
                  value={notificationConfig.dynamics365.incident_type}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, incident_type: e.target.value }
                  })}
                >
                  <option value="incident">Incident (Case)</option>
                  <option value="msdyn_workorder">Work Order (Field Service)</option>
                </select>
                <small>Tipo de registro a ser criado</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Prioridade Padrão:</label>
                <select
                  value={notificationConfig.dynamics365.priority}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, priority: parseInt(e.target.value) }
                  })}
                >
                  <option value="1">1 - Alta</option>
                  <option value="2">2 - Normal</option>
                  <option value="3">3 - Baixa</option>
                </select>
                <small>Prioridade para alertas de warning</small>
              </div>
              <div className="form-group">
                <label>Owner ID (opcional):</label>
                <input
                  type="text"
                  value={notificationConfig.dynamics365.owner_id}
                  onChange={(e) => setNotificationConfig({
                    ...notificationConfig,
                    dynamics365: { ...notificationConfig.dynamics365, owner_id: e.target.value }
                  })}
                  placeholder="12345678-1234-1234-1234-123456789012"
                />
                <small>GUID do usuário proprietário (opcional)</small>
              </div>
            </div>
            <div className="info-box" style={{ marginBottom: '10px', background: '#fff3cd', border: '1px solid #ffc107', padding: '10px', borderRadius: '5px' }}>
              <p style={{ margin: 0, color: '#856404', fontSize: '12px' }}>
                <strong>⚠️ Lembre-se:</strong> Salve as configurações antes de testar!
              </p>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('dynamics365')}>
              Testar Criação de Incidente
            </button>
          </div>
        )}
      </div>

      {/* Conecta (Sistema de Chamados) */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🎫</span>
            <h3>Conecta (Sistema de Chamados)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={notificationConfig.kiro_conecta?.enabled || false}
              onChange={(e) => setNotificationConfig({
                ...notificationConfig,
                kiro_conecta: { ...notificationConfig.kiro_conecta, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        {notificationConfig.kiro_conecta?.enabled && (
          <div className="integration-config">
            <div style={{ marginBottom: 16, padding: 12, background: '#1e293b', borderRadius: 8, fontSize: 13, color: '#94a3b8' }}>
              <p style={{ margin: 0 }}>📋 Abertura automática de chamados no Conecta quando incidentes são criados.</p>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>URL da API:</label>
                <input type="text" value={notificationConfig.kiro_conecta?.url || ''} onChange={(e) => setNotificationConfig({...notificationConfig, kiro_conecta: { ...notificationConfig.kiro_conecta, url: e.target.value }})} placeholder="http://conecta.techbiz.com.br:8000" />
              </div>
              <div className="form-group">
                <label>URL do Frontend:</label>
                <input type="text" value={notificationConfig.kiro_conecta?.frontend_url || ''} onChange={(e) => setNotificationConfig({...notificationConfig, kiro_conecta: { ...notificationConfig.kiro_conecta, frontend_url: e.target.value }})} placeholder="http://conecta.techbiz.com.br:5173" />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>E-mail do Solicitante:</label>
                <input type="email" value={notificationConfig.kiro_conecta?.user_email || ''} onChange={(e) => setNotificationConfig({...notificationConfig, kiro_conecta: { ...notificationConfig.kiro_conecta, user_email: e.target.value }})} placeholder="coruja.monitor@techbiz.com.br" />
                <small>Deve existir como usuário no Conecta</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Categoria:</label>
                <input type="text" value={notificationConfig.kiro_conecta?.category || ''} onChange={(e) => setNotificationConfig({...notificationConfig, kiro_conecta: { ...notificationConfig.kiro_conecta, category: e.target.value }})} placeholder="Monitoramento" />
              </div>
              <div className="form-group">
                <label>Subcategoria:</label>
                <input type="text" value={notificationConfig.kiro_conecta?.subcategory || ''} onChange={(e) => setNotificationConfig({...notificationConfig, kiro_conecta: { ...notificationConfig.kiro_conecta, subcategory: e.target.value }})} placeholder="Alerta Automatico" />
              </div>
            </div>
            <button className="btn-test" onClick={() => handleTestNotification('kiro_conecta')} style={{ marginTop: 12, marginBottom: 8 }}>
              🎫 Testar Abertura de Chamado
            </button>
          </div>
        )}
      </div>

      <div className="settings-actions">
        <button className="btn-primary" onClick={handleSaveNotifications} disabled={saving}>
          {saving ? 'Salvando...' : 'Salvar Configurações'}
        </button>
      </div>
    </div>
  );


  const renderUsers = () => (
    <div className="settings-section">
      <h2>👥 Gerenciamento de Usuários</h2>
      <p className="section-description">
        Gerencie usuários, permissões e perfis de acesso do sistema.
      </p>
      <div className="redirect-card">
        <div className="redirect-icon">👥</div>
        <h3>Usuários</h3>
        <p>Crie, edite e gerencie usuários e suas permissões</p>
        <button className="btn-primary" onClick={() => onNavigate('users')}>
          Ir para Gerenciamento de Usuários
        </button>
      </div>
    </div>
  );

  const renderSecurity = () => (
    <div className="settings-section">
      <h2>🔐 Segurança e Autenticação</h2>
      <p className="section-description">
        Configure métodos de autenticação enterprise, políticas de senha, MFA e gerenciamento de sessões.
        Compatível com LGPD e ISO 27001.
      </p>

      {/* Security Monitor Component */}
      <SecurityMonitor />

      {/* MFA Setup Component */}
      <div style={{ marginTop: '30px' }}>
        <MFASetup />
      </div>

      <div className="info-banner" style={{ marginBottom: '20px', background: '#e3f2fd', padding: '15px', borderRadius: '8px', border: '1px solid #2196f3' }}>
        <p style={{ margin: 0, color: '#1976d2' }}>
          ℹ️ <strong>Nota:</strong> As configurações de autenticação enterprise requerem configuração adicional no backend.
          Consulte a documentação em <code>docs/LGPD_COMPLIANCE.md</code> e <code>docs/ISO27001_COMPLIANCE.md</code> para mais detalhes.
        </p>
      </div>

      {/* LDAP / Active Directory */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🏢</span>
            <h3>LDAP / Active Directory</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={authConfig.ldap.enabled}
              onChange={(e) => setAuthConfig({
                ...authConfig,
                ldap: { ...authConfig.ldap, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {authConfig.ldap.enabled && (
          <div className="integration-config">
            <div className="form-row">
              <div className="form-group">
                <label>Servidor LDAP:</label>
                <input
                  type="text"
                  value={authConfig.ldap.server}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, server: e.target.value }
                  })}
                  placeholder="ldap.empresa.com ou 192.168.1.10"
                />
                <small>Endereço do servidor LDAP/AD</small>
              </div>
              <div className="form-group">
                <label>Porta:</label>
                <input
                  type="number"
                  value={authConfig.ldap.port}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, port: parseInt(e.target.value) }
                  })}
                  placeholder="389"
                />
                <small>389 (LDAP) ou 636 (LDAPS)</small>
              </div>
            </div>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={authConfig.ldap.use_ssl}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, use_ssl: e.target.checked }
                  })}
                />
                Usar SSL/TLS (LDAPS)
              </label>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Base DN:</label>
                <input
                  type="text"
                  value={authConfig.ldap.base_dn}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, base_dn: e.target.value }
                  })}
                  placeholder="dc=empresa,dc=com"
                />
                <small>Distinguished Name base para busca</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Bind DN (usuário de serviço):</label>
                <input
                  type="text"
                  value={authConfig.ldap.bind_dn}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, bind_dn: e.target.value }
                  })}
                  placeholder="cn=admin,dc=empresa,dc=com"
                />
                <small>Usuário para conectar ao LDAP</small>
              </div>
              <div className="form-group">
                <label>Senha do Bind:</label>
                <input
                  type="password"
                  value={authConfig.ldap.bind_password}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, bind_password: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Filtro de Usuário:</label>
                <input
                  type="text"
                  value={authConfig.ldap.user_filter}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, user_filter: e.target.value }
                  })}
                  placeholder="(uid={username})"
                />
                <small>Filtro LDAP para buscar usuários</small>
              </div>
              <div className="form-group">
                <label>Filtro de Grupo (opcional):</label>
                <input
                  type="text"
                  value={authConfig.ldap.group_filter}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, group_filter: e.target.value }
                  })}
                  placeholder="(memberOf=cn=coruja,ou=groups,dc=empresa,dc=com)"
                />
                <small>Filtro para restringir acesso por grupo</small>
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Grupo Admin:</label>
                <input
                  type="text"
                  value={authConfig.ldap.admin_group}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, admin_group: e.target.value }
                  })}
                  placeholder="cn=coruja-admins,ou=groups,dc=empresa,dc=com"
                />
                <small>Membros terão role admin</small>
              </div>
              <div className="form-group">
                <label>Grupo User:</label>
                <input
                  type="text"
                  value={authConfig.ldap.user_group}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    ldap: { ...authConfig.ldap, user_group: e.target.value }
                  })}
                  placeholder="cn=coruja-users,ou=groups,dc=empresa,dc=com"
                />
                <small>Membros terão role user</small>
              </div>
            </div>
            <div className="form-group">
              <label>Grupo Viewer:</label>
              <input
                type="text"
                value={authConfig.ldap.viewer_group}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  ldap: { ...authConfig.ldap, viewer_group: e.target.value }
                })}
                placeholder="cn=coruja-viewers,ou=groups,dc=empresa,dc=com"
              />
              <small>Membros terão role viewer</small>
            </div>
            <button className="btn-test" onClick={() => handleTestAuthConfig('ldap')}>
              Testar Conexão LDAP
            </button>
          </div>
        )}
      </div>

      {/* Azure AD (Entra ID) */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">☁️</span>
            <h3>Azure AD (Microsoft Entra ID)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={authConfig.azure_ad.enabled}
              onChange={(e) => setAuthConfig({
                ...authConfig,
                azure_ad: { ...authConfig.azure_ad, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {authConfig.azure_ad.enabled && (
          <div className="integration-config">
            <div className="form-row">
              <div className="form-group">
                <label>Tenant ID:</label>
                <input
                  type="text"
                  value={authConfig.azure_ad.tenant_id}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    azure_ad: { ...authConfig.azure_ad, tenant_id: e.target.value }
                  })}
                  placeholder="12345678-1234-1234-1234-123456789012"
                />
              </div>
              <div className="form-group">
                <label>Client ID:</label>
                <input
                  type="text"
                  value={authConfig.azure_ad.client_id}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    azure_ad: { ...authConfig.azure_ad, client_id: e.target.value }
                  })}
                  placeholder="87654321-4321-4321-4321-210987654321"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Client Secret:</label>
                <input
                  type="password"
                  value={authConfig.azure_ad.client_secret}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    azure_ad: { ...authConfig.azure_ad, client_secret: e.target.value }
                  })}
                  placeholder="••••••••••••••••"
                />
              </div>
              <div className="form-group">
                <label>Redirect URI:</label>
                <input
                  type="text"
                  value={authConfig.azure_ad.redirect_uri}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    azure_ad: { ...authConfig.azure_ad, redirect_uri: e.target.value }
                  })}
                  placeholder="https://coruja.empresa.com/auth/azure/callback"
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>ID do Grupo Admin (opcional):</label>
                <input
                  type="text"
                  value={authConfig.azure_ad.admin_group_id}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    azure_ad: { ...authConfig.azure_ad, admin_group_id: e.target.value }
                  })}
                  placeholder="11111111-1111-1111-1111-111111111111"
                />
              </div>
              <div className="form-group">
                <label>ID do Grupo User (opcional):</label>
                <input
                  type="text"
                  value={authConfig.azure_ad.user_group_id}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    azure_ad: { ...authConfig.azure_ad, user_group_id: e.target.value }
                  })}
                  placeholder="22222222-2222-2222-2222-222222222222"
                />
              </div>
            </div>
            <button className="btn-test" onClick={() => handleTestAuthConfig('azure_ad')}>
              Testar Azure AD
            </button>
          </div>
        )}
      </div>

      {/* MFA / 2FA */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🔒</span>
            <h3>Autenticação Multi-Fator (MFA/2FA)</h3>
          </div>
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={authConfig.mfa.enabled}
              onChange={(e) => setAuthConfig({
                ...authConfig,
                mfa: { ...authConfig.mfa, enabled: e.target.checked }
              })}
            />
            <span className="toggle-slider"></span>
          </label>
        </div>
        
        {authConfig.mfa.enabled && (
          <div className="integration-config">
            <div className="form-group">
              <label>Método MFA:</label>
              <select
                value={authConfig.mfa.method}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  mfa: { ...authConfig.mfa, method: e.target.value }
                })}
              >
                <option value="totp">TOTP (Google Authenticator, Authy)</option>
                <option value="sms">SMS</option>
                <option value="email">E-mail</option>
              </select>
            </div>
            <div className="form-group">
              <label>Issuer (para TOTP):</label>
              <input
                type="text"
                value={authConfig.mfa.issuer}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  mfa: { ...authConfig.mfa, issuer: e.target.value }
                })}
                placeholder="CorujaMonitor"
              />
              <small>Nome que aparecerá no app autenticador</small>
            </div>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={authConfig.mfa.enforce_for_admins}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    mfa: { ...authConfig.mfa, enforce_for_admins: e.target.checked }
                  })}
                />
                Obrigatório para Administradores
              </label>
            </div>
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={authConfig.mfa.enforce_for_all}
                  onChange={(e) => setAuthConfig({
                    ...authConfig,
                    mfa: { ...authConfig.mfa, enforce_for_all: e.target.checked }
                  })}
                />
                Obrigatório para Todos os Usuários
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Política de Senha */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">🔑</span>
            <h3>Política de Senha</h3>
          </div>
        </div>
        
        <div className="integration-config" style={{ display: 'block' }}>
          <div className="form-row">
            <div className="form-group">
              <label>Comprimento Mínimo:</label>
              <input
                type="number"
                value={authConfig.password_policy.min_length}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  password_policy: { ...authConfig.password_policy, min_length: parseInt(e.target.value) }
                })}
                min="6"
                max="32"
              />
            </div>
            <div className="form-group">
              <label>Expiração (dias):</label>
              <input
                type="number"
                value={authConfig.password_policy.expiry_days}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  password_policy: { ...authConfig.password_policy, expiry_days: parseInt(e.target.value) }
                })}
                min="0"
                max="365"
              />
              <small>0 = nunca expira</small>
            </div>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={authConfig.password_policy.require_uppercase}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  password_policy: { ...authConfig.password_policy, require_uppercase: e.target.checked }
                })}
              />
              Exigir Letras Maiúsculas
            </label>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={authConfig.password_policy.require_lowercase}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  password_policy: { ...authConfig.password_policy, require_lowercase: e.target.checked }
                })}
              />
              Exigir Letras Minúsculas
            </label>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={authConfig.password_policy.require_numbers}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  password_policy: { ...authConfig.password_policy, require_numbers: e.target.checked }
                })}
              />
              Exigir Números
            </label>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={authConfig.password_policy.require_special}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  password_policy: { ...authConfig.password_policy, require_special: e.target.checked }
                })}
              />
              Exigir Caracteres Especiais (!@#$%^&*)
            </label>
          </div>
          <div className="form-group">
            <label>Prevenir Reutilização (últimas N senhas):</label>
            <input
              type="number"
              value={authConfig.password_policy.prevent_reuse}
              onChange={(e) => setAuthConfig({
                ...authConfig,
                password_policy: { ...authConfig.password_policy, prevent_reuse: parseInt(e.target.value) }
              })}
              min="0"
              max="24"
            />
            <small>0 = permitir reutilização</small>
          </div>
        </div>
      </div>

      {/* Gerenciamento de Sessões */}
      <div className="integration-card">
        <div className="integration-header">
          <div className="integration-title">
            <span className="integration-icon">⏱️</span>
            <h3>Gerenciamento de Sessões</h3>
          </div>
        </div>
        
        <div className="integration-config" style={{ display: 'block' }}>
          <div className="form-row">
            <div className="form-group">
              <label>Timeout de Sessão (minutos):</label>
              <input
                type="number"
                value={authConfig.session.timeout_minutes}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  session: { ...authConfig.session, timeout_minutes: parseInt(e.target.value) }
                })}
                min="5"
                max="1440"
              />
              <small>Tempo de inatividade antes de logout automático</small>
            </div>
            <div className="form-group">
              <label>Sessões Simultâneas Máximas:</label>
              <input
                type="number"
                value={authConfig.session.max_concurrent_sessions}
                onChange={(e) => setAuthConfig({
                  ...authConfig,
                  session: { ...authConfig.session, max_concurrent_sessions: parseInt(e.target.value) }
                })}
                min="1"
                max="10"
              />
              <small>Número máximo de logins simultâneos por usuário</small>
            </div>
          </div>
          <div className="form-group">
            <label>Duração "Lembrar-me" (dias):</label>
            <input
              type="number"
              value={authConfig.session.remember_me_days}
              onChange={(e) => setAuthConfig({
                ...authConfig,
                session: { ...authConfig.session, remember_me_days: parseInt(e.target.value) }
              })}
              min="1"
              max="90"
            />
            <small>Quanto tempo manter sessão com "Lembrar-me" marcado</small>
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <button className="btn-primary" onClick={handleSaveAuthConfig} disabled={saving}>
          {saving ? 'Salvando...' : '💾 Salvar Configurações de Segurança'}
        </button>
      </div>
    </div>
  );

  const renderAppearance = () => (
    <div className="settings-section">
      <h2>🎨 Aparência</h2>
      <p className="section-description">
        Personalize a aparência e o tema da interface
      </p>

      <div className="advanced-settings">
        {/* Dark Mode */}
        <div className="setting-group">
          <h3>🌙 Modo Escuro</h3>
          <div className="form-group">
            <label className="toggle-switch-large">
              <span className="toggle-label">
                {appearanceSettings.darkMode ? 'Modo Escuro Ativado' : 'Modo Claro Ativado'}
              </span>
              <input 
                type="checkbox" 
                checked={appearanceSettings.darkMode}
                onChange={(e) => setAppearanceSettings({
                  ...appearanceSettings,
                  darkMode: e.target.checked
                })}
              />
              <span className="toggle-slider-large"></span>
            </label>
            <small>Reduz o cansaço visual em ambientes com pouca luz</small>
          </div>
        </div>

        {/* Compact Mode */}
        <div className="setting-group">
          <h3>📐 Densidade da Interface</h3>
          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={appearanceSettings.compactMode}
                onChange={(e) => setAppearanceSettings({
                  ...appearanceSettings,
                  compactMode: e.target.checked
                })}
              />
              Modo Compacto
            </label>
            <small>Reduz espaçamentos para mostrar mais informações na tela</small>
          </div>
        </div>

        {/* Font Size */}
        <div className="setting-group">
          <h3>🔤 Tamanho da Fonte</h3>
          <div className="form-group">
            <label>Tamanho do Texto:</label>
            <select 
              value={appearanceSettings.fontSize}
              onChange={(e) => setAppearanceSettings({
                ...appearanceSettings,
                fontSize: e.target.value
              })}
            >
              <option value="small">Pequeno</option>
              <option value="medium">Médio (Padrão)</option>
              <option value="large">Grande</option>
              <option value="xlarge">Muito Grande</option>
            </select>
            <small>Ajuste o tamanho do texto para melhor legibilidade</small>
          </div>
        </div>

        {/* Color Scheme */}
        <div className="setting-group">
          <h3>🎨 Esquema de Cores</h3>
          <div className="form-group">
            <label>Cor Principal:</label>
            <div className="color-scheme-options">
              <label className="color-option">
                <input 
                  type="radio" 
                  name="colorScheme" 
                  value="blue"
                  checked={appearanceSettings.colorScheme === 'blue'}
                  onChange={(e) => setAppearanceSettings({
                    ...appearanceSettings,
                    colorScheme: e.target.value
                  })}
                />
                <span className="color-preview" style={{background: '#2196f3'}}></span>
                <span>Azul (Padrão)</span>
              </label>
              <label className="color-option">
                <input 
                  type="radio" 
                  name="colorScheme" 
                  value="green"
                  checked={appearanceSettings.colorScheme === 'green'}
                  onChange={(e) => setAppearanceSettings({
                    ...appearanceSettings,
                    colorScheme: e.target.value
                  })}
                />
                <span className="color-preview" style={{background: '#4caf50'}}></span>
                <span>Verde</span>
              </label>
              <label className="color-option">
                <input 
                  type="radio" 
                  name="colorScheme" 
                  value="purple"
                  checked={appearanceSettings.colorScheme === 'purple'}
                  onChange={(e) => setAppearanceSettings({
                    ...appearanceSettings,
                    colorScheme: e.target.value
                  })}
                />
                <span className="color-preview" style={{background: '#9c27b0'}}></span>
                <span>Roxo</span>
              </label>
              <label className="color-option">
                <input 
                  type="radio" 
                  name="colorScheme" 
                  value="orange"
                  checked={appearanceSettings.colorScheme === 'orange'}
                  onChange={(e) => setAppearanceSettings({
                    ...appearanceSettings,
                    colorScheme: e.target.value
                  })}
                />
                <span className="color-preview" style={{background: '#ff9800'}}></span>
                <span>Laranja</span>
              </label>
            </div>
            <small>Escolha a cor principal da interface</small>
          </div>
        </div>

        {/* Preview */}
        <div className="setting-group">
          <h3>👁️ Pré-visualização</h3>
          <div className="appearance-preview">
            <div className={`preview-card ${appearanceSettings.darkMode ? 'dark' : 'light'}`}>
              <div className="preview-header">
                <h4>Exemplo de Card</h4>
                <span className="preview-badge">Status</span>
              </div>
              <p>Este é um exemplo de como a interface ficará com as configurações selecionadas.</p>
              <button className="preview-button">Botão de Exemplo</button>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <button className="btn-primary" onClick={handleSaveAppearanceSettings}>
          Salvar Configurações de Aparência
        </button>
        <button className="btn-secondary" onClick={() => {
          setAppearanceSettings({
            darkMode: false,
            compactMode: false,
            fontSize: 'medium',
            colorScheme: 'blue'
          });
        }}>
          Restaurar Padrões
        </button>
      </div>
    </div>
  );

  const renderAdminTools = () => {
    if (showSystemReset) {
      return (
        <div className="settings-section">
          <button 
            className="btn-secondary"
            onClick={() => setShowSystemReset(false)}
            style={{ marginBottom: '20px' }}
          >
            ← Voltar para Ferramentas Admin
          </button>
          <SystemReset />
        </div>
      );
    }

    return (
    <div className="settings-section">
      <h2>🔧 Ferramentas Administrativas</h2>
      <p className="section-description">
        Ferramentas para manutenção e gerenciamento do sistema
      </p>

      <div className="admin-tools-grid">
        {/* Reset do Sistema */}
        <div className="admin-tool-card">
          <div className="tool-icon">🔄</div>
          <h3>Reset do Sistema</h3>
          <p>Apague TODOS os dados: empresas, probes, servidores, sensores, métricas</p>
          <div className="tool-status">
            <strong style={{ color: '#dc3545' }}>⚠️ AÇÃO IRREVERSÍVEL</strong>
          </div>
          <button 
            className="btn-danger"
            onClick={() => setShowSystemReset(true)}
          >
            🗑️ Reset Completo
          </button>
        </div>

        {/* Modo Manutenção */}
        <div className="admin-tool-card">
          <div className="tool-icon">🚧</div>
          <h3>Modo Manutenção</h3>
          <p>Coloque o sistema em modo manutenção para realizar atualizações</p>
          <div className="tool-status">
            Status: <strong>{maintenanceMode ? '🔴 Ativo' : '🟢 Normal'}</strong>
          </div>
          <button 
            className={maintenanceMode ? "btn-success" : "btn-warning"}
            onClick={handleToggleMaintenanceMode}
            disabled={actionInProgress}
          >
            {maintenanceMode ? 'Desativar Manutenção' : 'Ativar Manutenção'}
          </button>
        </div>

        {/* Reset Probes */}
        <div className="admin-tool-card">
          <div className="tool-icon">🔄</div>
          <h3>Reset de Probes</h3>
          <p>Reinicie todas as probes conectadas ao sistema</p>
          <button 
            className="btn-secondary"
            onClick={handleResetProbes}
            disabled={actionInProgress}
          >
            Reset Todas as Probes
          </button>
        </div>

        {/* Restart Sistema */}
        <div className="admin-tool-card">
          <div className="tool-icon">⚡</div>
          <h3>Restart do Sistema</h3>
          <p>Reinicie todos os serviços do Coruja Monitor</p>
          <button 
            className="btn-danger"
            onClick={handleRestartSystem}
            disabled={actionInProgress}
          >
            Reiniciar Sistema
          </button>
        </div>

        {/* Backup Database */}
        <div className="admin-tool-card">
          <div className="tool-icon">💾</div>
          <h3>Backup do Banco</h3>
          <p>Faça backup do banco de dados PostgreSQL</p>
          <button 
            className="btn-primary"
            onClick={handleBackupDatabase}
            disabled={actionInProgress}
          >
            Criar Backup
          </button>
        </div>

        {/* Limpar Cache */}
        <div className="admin-tool-card">
          <div className="tool-icon">🗑️</div>
          <h3>Limpar Cache</h3>
          <p>Limpe o cache do Redis</p>
          <button 
            className="btn-secondary"
            onClick={handleClearCache}
            disabled={actionInProgress}
          >
            Limpar Cache
          </button>
        </div>

        {/* Logs do Sistema */}
        <div className="admin-tool-card">
          <div className="tool-icon">📋</div>
          <h3>Logs do Sistema</h3>
          <p>Visualize logs dos serviços</p>
          <button 
            className="btn-primary"
            onClick={handleViewLogs}
            disabled={actionInProgress}
          >
            Ver Logs
          </button>
        </div>
      </div>
    </div>
    );
  };

  const renderBackup = () => {
    return (
      <div className="settings-section">
        <h2>💾 Backup & Restore</h2>
        
        <div className="info-banner" style={{ marginBottom: '20px' }}>
          <p>ℹ️ <strong>Backup Automático:</strong> O sistema cria backups automaticamente 5 vezes ao dia (0h, 5h, 10h, 15h, 20h)</p>
          <p>Os últimos 30 backups são mantidos automaticamente. Backups mais antigos são removidos.</p>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <button
            onClick={createBackup}
            disabled={creatingBackup}
            style={{
              padding: '12px 24px',
              background: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: creatingBackup ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            {creatingBackup ? '⏳ Criando Backup...' : '➕ Criar Backup Agora'}
          </button>
          <button
            onClick={loadBackups}
            disabled={loadingBackups}
            style={{
              padding: '12px 24px',
              background: '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loadingBackups ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              marginLeft: '10px'
            }}
          >
            {loadingBackups ? '⏳ Carregando...' : '🔄 Atualizar Lista'}
          </button>
        </div>

        {loadingBackups ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>⏳ Carregando backups...</p>
          </div>
        ) : backups.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', background: '#f5f5f5', borderRadius: '8px' }}>
            <p>📦 Nenhum backup encontrado</p>
            <p style={{ fontSize: '14px', color: '#666' }}>Clique em "Criar Backup Agora" para criar o primeiro backup</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>📅 Data/Hora</th>
                  <th style={{ padding: '12px', textAlign: 'left' }}>📁 Arquivo</th>
                  <th style={{ padding: '12px', textAlign: 'right' }}>💾 Tamanho</th>
                  <th style={{ padding: '12px', textAlign: 'center' }}>⚡ Ações</th>
                </tr>
              </thead>
              <tbody>
                {backups.map((backup, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '12px' }}>
                      {new Date(backup.created_at).toLocaleString('pt-BR')}
                    </td>
                    <td style={{ padding: '12px', fontFamily: 'monospace', fontSize: '13px' }}>
                      {backup.filename}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      {backup.size_mb} MB
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <button
                        onClick={() => restoreBackup(backup.filename)}
                        disabled={restoringBackup}
                        style={{
                          padding: '6px 12px',
                          background: '#ff9800',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: restoringBackup ? 'not-allowed' : 'pointer',
                          marginRight: '5px',
                          fontSize: '13px'
                        }}
                        title="Restaurar este backup"
                      >
                        ↩️ Restaurar
                      </button>
                      <button
                        onClick={() => downloadBackup(backup.filename)}
                        style={{
                          padding: '6px 12px',
                          background: '#2196f3',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          marginRight: '5px',
                          fontSize: '13px'
                        }}
                        title="Baixar backup"
                      >
                        ⬇️ Download
                      </button>
                      <button
                        onClick={() => deleteBackup(backup.filename)}
                        style={{
                          padding: '6px 12px',
                          background: '#f44336',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '13px'
                        }}
                        title="Deletar backup"
                      >
                        🗑️ Deletar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {restoringBackup && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999
          }}>
            <div style={{
              background: 'white',
              padding: '40px',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <h3>⏳ Restaurando Backup...</h3>
              <p>Por favor, aguarde. Não feche esta janela.</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderAdvanced = () => (
    <div className="settings-section">
      <h2>⚙️ Configurações Avançadas</h2>
      <p className="section-description">
        Configurações avançadas inspiradas em Zabbix e PRTG
      </p>

      <div className="advanced-settings">
        {/* Data Retention */}
        <div className="setting-group">
          <h3>📊 Retenção de Dados</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Histórico de Métricas (dias):</label>
              <input 
                type="number" 
                value={advancedSettings.dataRetention.metricsHistory}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  dataRetention: { ...advancedSettings.dataRetention, metricsHistory: parseInt(e.target.value) }
                })}
                min="7" 
                max="365" 
              />
              <small>Quanto tempo manter métricas históricas</small>
            </div>
            <div className="form-group">
              <label>Histórico de Incidentes (dias):</label>
              <input 
                type="number" 
                value={advancedSettings.dataRetention.incidentsHistory}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  dataRetention: { ...advancedSettings.dataRetention, incidentsHistory: parseInt(e.target.value) }
                })}
                min="30" 
                max="730" 
              />
              <small>Quanto tempo manter incidentes resolvidos</small>
            </div>
          </div>
        </div>

        {/* Collection Intervals */}
        <div className="setting-group">
          <h3>⏱️ Intervalos de Coleta</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Intervalo Padrão (segundos):</label>
              <input 
                type="number" 
                value={advancedSettings.collectionIntervals.defaultInterval}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  collectionIntervals: { ...advancedSettings.collectionIntervals, defaultInterval: parseInt(e.target.value) }
                })}
                min="10" 
                max="3600" 
              />
              <small>Frequência de coleta de métricas</small>
            </div>
            <div className="form-group">
              <label>Intervalo Rápido (segundos):</label>
              <input 
                type="number" 
                value={advancedSettings.collectionIntervals.fastInterval}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  collectionIntervals: { ...advancedSettings.collectionIntervals, fastInterval: parseInt(e.target.value) }
                })}
                min="5" 
                max="300" 
              />
              <small>Para sensores críticos</small>
            </div>
          </div>
        </div>

        {/* Thresholds Globais */}
        <div className="setting-group">
          <h3>🎯 Thresholds Globais</h3>
          <div className="form-row">
            <div className="form-group">
              <label>CPU Warning (%):</label>
              <input 
                type="number" 
                value={advancedSettings.thresholds.cpuWarning}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  thresholds: { ...advancedSettings.thresholds, cpuWarning: parseInt(e.target.value) }
                })}
                min="50" 
                max="95" 
              />
            </div>
            <div className="form-group">
              <label>CPU Critical (%):</label>
              <input 
                type="number" 
                value={advancedSettings.thresholds.cpuCritical}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  thresholds: { ...advancedSettings.thresholds, cpuCritical: parseInt(e.target.value) }
                })}
                min="80" 
                max="100" 
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Memória Warning (%):</label>
              <input 
                type="number" 
                value={advancedSettings.thresholds.memoryWarning}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  thresholds: { ...advancedSettings.thresholds, memoryWarning: parseInt(e.target.value) }
                })}
                min="50" 
                max="95" 
              />
            </div>
            <div className="form-group">
              <label>Memória Critical (%):</label>
              <input 
                type="number" 
                value={advancedSettings.thresholds.memoryCritical}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  thresholds: { ...advancedSettings.thresholds, memoryCritical: parseInt(e.target.value) }
                })}
                min="80" 
                max="100" 
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Disco Warning (%):</label>
              <input 
                type="number" 
                value={advancedSettings.thresholds.diskWarning}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  thresholds: { ...advancedSettings.thresholds, diskWarning: parseInt(e.target.value) }
                })}
                min="50" 
                max="95" 
              />
            </div>
            <div className="form-group">
              <label>Disco Critical (%):</label>
              <input 
                type="number" 
                value={advancedSettings.thresholds.diskCritical}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  thresholds: { ...advancedSettings.thresholds, diskCritical: parseInt(e.target.value) }
                })}
                min="80" 
                max="100" 
              />
            </div>
          </div>
        </div>

        {/* Auto-Discovery */}
        <div className="setting-group">
          <h3>🔍 Auto-Discovery</h3>
          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={advancedSettings.autoDiscovery.snmpEnabled}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  autoDiscovery: { ...advancedSettings.autoDiscovery, snmpEnabled: e.target.checked }
                })}
              />
              Habilitar auto-discovery de dispositivos SNMP
            </label>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={advancedSettings.autoDiscovery.autoCreateSensors}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  autoDiscovery: { ...advancedSettings.autoDiscovery, autoCreateSensors: e.target.checked }
                })}
              />
              Criar sensores automaticamente para novos servidores
            </label>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={advancedSettings.autoDiscovery.autoRemediation}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  autoDiscovery: { ...advancedSettings.autoDiscovery, autoRemediation: e.target.checked }
                })}
              />
              Auto-remediação pela IA para problemas conhecidos
            </label>
            <small>A IA tentará resolver automaticamente problemas comuns</small>
          </div>
        </div>

        {/* Performance */}
        <div className="setting-group">
          <h3>⚡ Performance</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Máximo de Sensores por Probe:</label>
              <input 
                type="number" 
                value={advancedSettings.performance.maxSensorsPerProbe}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  performance: { ...advancedSettings.performance, maxSensorsPerProbe: parseInt(e.target.value) }
                })}
                min="100" 
                max="10000" 
              />
              <small>Limite de sensores por probe</small>
            </div>
            <div className="form-group">
              <label>Threads de Coleta:</label>
              <input 
                type="number" 
                value={advancedSettings.performance.collectionThreads}
                onChange={(e) => setAdvancedSettings({
                  ...advancedSettings,
                  performance: { ...advancedSettings.performance, collectionThreads: parseInt(e.target.value) }
                })}
                min="1" 
                max="50" 
              />
              <small>Threads paralelas para coleta</small>
            </div>
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <button className="btn-primary" onClick={handleSaveAdvancedSettings}>
          Salvar Configurações Avançadas
        </button>
      </div>
    </div>
  );

  if (loading) return <div className="loading">Carregando configurações...</div>;

  return (
    <div className="settings-page">
      {/* Modal de Progresso */}
      {actionModal.show && (
        <div className="modal-overlay" onClick={(e) => {
          if (e.target.className === 'modal-overlay' && !actionInProgress) {
            closeActionModal();
          }
        }}>
          <div className="modal-content action-modal">
            <div className="modal-header-admin">
              <h2>{actionModal.title}</h2>
              {!actionInProgress && (
                <button className="modal-close-btn" onClick={closeActionModal}>✕</button>
              )}
            </div>
            <div className="progress-log">
              {actionModal.progress.map((msg, index) => (
                <div key={index} className="progress-line">
                  {msg}
                </div>
              ))}
            </div>
            <div className="modal-footer-admin">
              {!actionInProgress && (
                <button className="btn-primary btn-close-modal" onClick={closeActionModal}>
                  Fechar
                </button>
              )}
              {actionInProgress && (
                <div className="action-spinner">
                  <div className="spinner-small"></div>
                  <span>Processando...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="settings-header">
        <h1>⚙️ Configurações</h1>
        <p>Gerencie configurações do sistema, integrações e ferramentas administrativas</p>
      </div>

      <div className="settings-tabs">
        <button 
          className={`tab ${activeTab === 'appearance' ? 'active' : ''}`}
          onClick={() => setActiveTab('appearance')}
        >
          🎨 Aparência
        </button>
        <button 
          className={`tab ${activeTab === 'sensor-profiles' ? 'active' : ''}`}
          onClick={() => setActiveTab('sensor-profiles')}
        >
          📡 Sensores Padrão
        </button>
        <button 
          className={`tab ${activeTab === 'thresholds' ? 'active' : ''}`}
          onClick={() => setActiveTab('thresholds')}
        >
          ⏱️ Thresholds
        </button>
        <button 
          className={`tab ${activeTab === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('notifications')}
        >
          📢 Notificações
        </button>
        <button 
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👥 Usuários
        </button>
        <button 
          className={`tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          🔐 Segurança
        </button>
        <button 
          className={`tab ${activeTab === 'credentials' ? 'active' : ''}`}
          onClick={() => setActiveTab('credentials')}
        >
          🔑 Credenciais
        </button>
        <button 
          className={`tab ${activeTab === 'tests' ? 'active' : ''}`}
          onClick={() => setActiveTab('tests')}
        >
          🧪 Testes de Sensores
        </button>
        <button 
          className={`tab ${activeTab === 'backup' ? 'active' : ''}`}
          onClick={() => setActiveTab('backup')}
        >
          💾 Backup & Restore
        </button>
        <button 
          className={`tab ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin')}
        >
          🔧 Ferramentas Admin
        </button>
        <button 
          className={`tab ${activeTab === 'advanced' ? 'active' : ''}`}
          onClick={() => setActiveTab('advanced')}
        >
          ⚙️ Avançado
        </button>
      </div>

      <div className="settings-content">
        {activeTab === 'appearance' && renderAppearance()}
        {activeTab === 'sensor-profiles' && <DefaultSensorProfiles />}
        {activeTab === 'thresholds' && <ThresholdConfig />}
        {activeTab === 'notifications' && renderNotifications()}
        {activeTab === 'users' && renderUsers()}
        {activeTab === 'security' && renderSecurity()}
        {activeTab === 'credentials' && <Credentials />}
        {activeTab === 'tests' && <TestTools />}
        {activeTab === 'backup' && renderBackup()}
        {activeTab === 'admin' && renderAdminTools()}
        {activeTab === 'advanced' && renderAdvanced()}
      </div>
    </div>
  );
}

export default Settings;
