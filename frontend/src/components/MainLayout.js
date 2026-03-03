import React, { useState } from 'react';
import Sidebar from './Sidebar';
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
import AdvancedDashboard from './AdvancedDashboard';
// import ServersGrouped from './ServersGrouped'; // Temporariamente desabilitado - arquivo incompleto
import AutoRemediation from './AutoRemediation';
import MetricsViewer from './MetricsViewer';
import './MainLayout.css';

function MainLayout({ user, onLogout }) {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedServerId, setSelectedServerId] = useState(null);
  const [selectedSensorId, setSelectedSensorId] = useState(null);
  const [sensorFilter, setSensorFilter] = useState('all');
  const [nocMode, setNocMode] = useState(false);

  const handleNavigate = (page, filter = null) => {
    setCurrentPage(page);
    if (filter) {
      setSensorFilter(filter);
    } else {
      setSensorFilter('all');
    }
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
        return <AIOps />;
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
      case 'advanced-dashboard':
        return <AdvancedDashboard user={user} onNavigate={handleNavigate} />;
      case 'servers-grouped':
        // Temporariamente desabilitado - arquivo ServersGrouped.js incompleto
        return <Servers />; // Fallback para Servers normal
      case 'auto-remediation':
        return <AutoRemediation />;
      case 'metrics-viewer':
        return <MetricsViewer />;
      case 'users':
        return <Users />;
      case 'settings':
        return <Settings onNavigate={handleNavigate} />;
      default:
        return <Dashboard user={user} onLogout={onLogout} onNavigate={handleNavigate} onEnterNOC={() => setNocMode(true)} />;
    }
  };

  if (nocMode) {
    return <NOCMode onExit={() => setNocMode(false)} />;
  }

  return (
    <div className="main-layout">
      <Sidebar currentPage={currentPage} onNavigate={(page) => handleNavigate(page)} />
      <div className="main-content">
        <div className="top-bar">
          <div className="top-bar-left">
            <img src="/coruja-logo.png" alt="Coruja Monitor" className="header-logo" />
            <h2>{user.full_name}</h2>
          </div>
          <button onClick={onLogout} className="logout-btn">Sair</button>
        </div>
        <div className="page-content">
          {renderPage()}
        </div>
      </div>
    </div>
  );
}

export default MainLayout;
