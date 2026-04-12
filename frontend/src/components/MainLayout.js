import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import Dashboard from './Dashboard';
import Companies from './Companies';
import Servers from './Servers';
import Sensors from './Sensors';
import SensorLibrary from './SensorLibrary';
import Incidents from './Incidents';
import Reports from './Reports';
import Users from './Users';
import Settings from './Settings';
import MaintenanceWindows from './MaintenanceWindows';
import AIOps from './AIOps';
import NOCMode from './NOCMode';
import TestTools from './TestTools';
import KnowledgeBase from './KnowledgeBase';
import AIActivities from './AIActivities';
import KubernetesDashboard from './KubernetesDashboard';
import CustomReports from './CustomReports';
import ThresholdConfig from './ThresholdConfig';
import Probes from './Probes';
import NOCRealTime from './NOCRealTime';
import NOCDatacenter from './NOCDatacenter';
import AdvancedDashboard from './AdvancedDashboard';
import AutoRemediation from './AutoRemediation';
import MetricsViewer from './MetricsViewer';
import ProbeNodes from './ProbeNodes';
import EventTimeline from './EventTimeline';
import SystemHealth from './SystemHealth';
import Discovery from './Discovery';
import ObservabilityDashboard from './ObservabilityDashboard';
import TopologyView from './TopologyView';
import IntelligentAlerts from './IntelligentAlerts';
import AIOpsV3 from './AIOpsV3';
import AdvancedMetrics from './AdvancedMetrics';
import EventsTimeline from './EventsTimeline';
import ServiceMap from './ServiceMap';
import Predictions from './Predictions';
import AuditLogView from './AuditLogView';
import ServiceMonitor from './ServiceMonitor';
import HyperVDashboard from './HyperVDashboard';
import EscalationConfig from './EscalationConfig';
import '../styles/design-system.css';
import './MainLayout.css';

function MainLayout({ user, onLogout }) {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedServerId, setSelectedServerId] = useState(null);
  const [selectedSensorId, setSelectedSensorId] = useState(null);
  const [sensorFilter, setSensorFilter] = useState('all');
  const [nocMode, setNocMode] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [systemStatus, setSystemStatus] = useState('ok');
  const [alertCount, setAlertCount] = useState(0);

  // Poll system status for topbar indicator
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const token = localStorage.getItem('token');
        const [healthRes, alertsRes] = await Promise.allSettled([
          fetch('/api/v1/dashboard/health-summary', { headers: { Authorization: `Bearer ${token}` } }),
          fetch('/api/v1/alerts/intelligent?status=open&limit=1', { headers: { Authorization: `Bearer ${token}` } }),
        ]);
        if (healthRes.status === 'fulfilled' && healthRes.value.ok) {
          const d = await healthRes.value.json();
          const critical = d.critical || 0;
          const warning = d.warning || 0;
          setSystemStatus(critical > 0 ? 'critical' : warning > 0 ? 'warning' : 'ok');
        }
        if (alertsRes.status === 'fulfilled' && alertsRes.value.ok) {
          const d = await alertsRes.value.json();
          const count = d.total ?? (Array.isArray(d.alerts) ? d.alerts.length : (Array.isArray(d) ? d.length : 0));
          setAlertCount(count);
        } else {
          setAlertCount(0);
        }
      } catch (_) {}
    };
    fetchStatus();
    const t = setInterval(() => {
      // Não atualizar quando modal está aberto (evita fechar modais)
      if (document.querySelector('.modal-overlay')) return;
      fetchStatus();
    }, 30000);
    return () => clearInterval(t);
  }, []);

  const handleNavigate = (page, filter = null) => {
    setCurrentPage(page);
    setSensorFilter(filter || 'all');
  };

  const handleNavigateToServer = (serverId, sensorId = null) => {
    setSelectedServerId(serverId);
    setSelectedSensorId(sensorId);
    setCurrentPage('servers');
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard user={user} onLogout={onLogout} onNavigate={handleNavigate} onEnterNOC={() => setNocMode(true)} />;
      case 'companies':
        return <Companies onNavigate={handleNavigate} />;
      case 'servers':
        return <Servers selectedServerId={selectedServerId} selectedSensorId={selectedSensorId} />;
      case 'sensors':
        return <Sensors onNavigateToServer={handleNavigateToServer} initialFilter={sensorFilter} />;
      case 'sensor-library':
        return <SensorLibrary />;
      case 'incidents':
        return <Incidents onNavigateToServer={handleNavigateToServer} onNavigate={handleNavigate} />;
      case 'knowledge-base':
        return <KnowledgeBase />;
      case 'ai-activities':
        return <AIActivities />;
      case 'maintenance':
        return <MaintenanceWindows />;
      case 'aiops':
        return <AIOpsV3 />;
      case 'kubernetes':
        return <KubernetesDashboard />;
      case 'reports':
        return <Reports />;
      case 'test-tools':
        return <TestTools />;
      case 'custom-reports':
        return <CustomReports />;
      case 'threshold-config':
        return <ThresholdConfig />;
      case 'probes':
        return <Probes />;
      case 'noc-realtime':
        return <NOCRealTime onExit={() => setCurrentPage('dashboard')} />;
      case 'noc-datacenter':
        return <NOCDatacenter onExit={() => setCurrentPage('dashboard')} />;
      case 'advanced-dashboard':
        return <AdvancedDashboard user={user} onNavigate={handleNavigate} />;
      case 'servers-grouped':
        return <Servers />;
      case 'auto-remediation':
        return <AutoRemediation />;
      case 'metrics-viewer':
        return <MetricsViewer />;
      case 'probe-nodes':
        return <ProbeNodes onNavigate={handleNavigate} />;
      case 'event-timeline':
        return <EventTimeline onNavigate={handleNavigate} />;
      case 'system-health':
        return <SystemHealth onNavigate={handleNavigate} />;
      case 'discovery':
        return <Discovery />;
      case 'observability':
        return <ObservabilityDashboard />;
      case 'topology':
        return <TopologyView />;
      case 'intelligent-alerts':
        return <IntelligentAlerts />;
      case 'aiops-v3':
        return <AIOpsV3 />;
      case 'advanced-metrics':
        return <AdvancedMetrics />;
      case 'events-timeline':
        return <EventsTimeline />;
      case 'service-map':
        return <ServiceMap />;
      case 'predictions':
        return <Predictions />;
      case 'audit-log':
        return <AuditLogView />;
      case 'service-monitor':
        return <ServiceMonitor />;
      case 'hyperv':
        return <HyperVDashboard />;
      case 'escalation':
        return <EscalationConfig />;
      case 'users':
        return <Users />;
      case 'settings':
        return <Settings onNavigate={handleNavigate} />;
      default:
        return <Dashboard user={user} onLogout={onLogout} onNavigate={handleNavigate} onEnterNOC={() => setNocMode(true)} />;
    }
  };

  if (nocMode || currentPage === 'noc-realtime' || currentPage === 'noc-datacenter') {
    return (
      currentPage === 'noc-realtime'
        ? <NOCRealTime onExit={() => setCurrentPage('dashboard')} />
        : currentPage === 'noc-datacenter'
        ? <NOCDatacenter onExit={() => setCurrentPage('dashboard')} />
        : <NOCMode onExit={() => setNocMode(false)} />
    );
  }

  return (
    <div className="main-layout">
      <Sidebar
        currentPage={currentPage}
        onNavigate={handleNavigate}
        user={user}
        onLogout={onLogout}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(c => !c)}
        alertCount={alertCount}
      />
      <div className={`main-content${sidebarCollapsed ? ' sidebar-collapsed' : ''}`}>
        <Topbar
          currentPage={currentPage}
          systemStatus={systemStatus}
          alertCount={alertCount}
          onNavigate={handleNavigate}
        />
        <div className="page-content">
          {renderPage()}
        </div>
      </div>
    </div>
  );
}

export default MainLayout;
