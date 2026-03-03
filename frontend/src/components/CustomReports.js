import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './CustomReports.css';

function CustomReports() {
  const [activeTab, setActiveTab] = useState('templates'); // templates, my_reports
  const [templates, setTemplates] = useState([]);
  const [myReports, setMyReports] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  
  // Report Builder State
  const [reportName, setReportName] = useState('');
  const [reportDescription, setReportDescription] = useState('');
  const [filters, setFilters] = useState({});
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    loadTemplates();
    loadMyReports();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await api.get('/api/v1/custom-reports/templates');
      setTemplates(response.data);
    } catch (error) {
      console.error('Erro ao carregar templates:', error);
    }
  };

  const loadMyReports = async () => {
    try {
      const response = await api.get('/api/v1/custom-reports/');
      setMyReports(response.data);
    } catch (error) {
      console.error('Erro ao carregar meus relatórios:', error);
    }
  };

  const handleSelectTemplate = (template) => {
    setSelectedTemplate(template);
    setReportName(template.name);
    setReportDescription(template.description);
    setFilters(template.filters || {});
    setSelectedColumns(template.columns || []);
    setSortBy(template.sort_by || '');
    setSortOrder(template.sort_order || 'desc');
    setReportData(null);
  };

  const handleGenerateReport = async () => {
    if (!selectedTemplate) return;

    setLoading(true);
    try {
      // Se for um template, gerar diretamente
      if (selectedTemplate.id && !selectedTemplate.id.toString().match(/^\d+$/)) {
        // É um template pré-definido, usar endpoint específico
        const response = await api.post('/api/v1/custom-reports/generate-template', {
          template_id: selectedTemplate.id,
          filters: filters
        });
        setReportData(response.data);
      } else {
        // É um relatório salvo, usar endpoint de geração
        const response = await api.post(`/api/v1/custom-reports/${selectedTemplate.id}/generate`);
        setReportData(response.data);
      }
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
      alert('Erro ao gerar relatório: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSaveReport = async () => {
    if (!reportName) {
      alert('Por favor, informe um nome para o relatório');
      return;
    }

    try {
      const reportData = {
        name: reportName,
        description: reportDescription,
        report_type: selectedTemplate?.report_type || 'incidents',
        filters: filters,
        columns: selectedColumns,
        sort_by: sortBy,
        sort_order: sortOrder,
        is_public: false,
        is_favorite: false
      };

      await api.post('/api/v1/custom-reports/', reportData);
      alert('Relatório salvo com sucesso!');
      setShowSaveModal(false);
      loadMyReports();
    } catch (error) {
      console.error('Erro ao salvar relatório:', error);
      alert('Erro ao salvar relatório: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteReport = async (reportId) => {
    if (!window.confirm('Tem certeza que deseja excluir este relatório?')) {
      return;
    }

    try {
      await api.delete(`/api/v1/custom-reports/${reportId}`);
      alert('Relatório excluído com sucesso!');
      loadMyReports();
      if (selectedTemplate?.id === reportId) {
        setSelectedTemplate(null);
        setReportData(null);
      }
    } catch (error) {
      console.error('Erro ao excluir relatório:', error);
      alert('Erro ao excluir relatório: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleExport = () => {
    if (!reportData) return;

    // Exportar para CSV
    const rows = reportData.data?.rows || [];
    if (rows.length === 0) {
      alert('Nenhum dado para exportar');
      return;
    }

    const headers = Object.keys(rows[0]);
    const csvContent = [
      headers.join(','),
      ...rows.map(row => headers.map(h => `"${row[h] || ''}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${reportName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const renderFilterBuilder = () => {
    if (!selectedTemplate) return null;

    const reportType = selectedTemplate.report_type;

    return (
      <div className="builder-section">
        <h3>🔍 Filtros</h3>
        <div className="filter-grid">
          {/* Período */}
          <div className="filter-field">
            <label>Período</label>
            <select 
              value={filters.period || 'last_30_days'}
              onChange={(e) => setFilters({...filters, period: e.target.value})}
            >
              <option value="last_24_hours">Últimas 24 horas</option>
              <option value="last_7_days">Últimos 7 dias</option>
              <option value="last_30_days">Últimos 30 dias</option>
              <option value="last_90_days">Últimos 90 dias</option>
            </select>
          </div>

          {/* Ambiente (para relatórios de servidores) */}
          {(reportType === 'servers' || reportType === 'availability') && (
            <div className="filter-field">
              <label>Ambiente</label>
              <select 
                value={filters.environment || ''}
                onChange={(e) => setFilters({...filters, environment: e.target.value})}
              >
                <option value="">Todos</option>
                <option value="production">Produção</option>
                <option value="staging">Homologação</option>
                <option value="development">Desenvolvimento</option>
              </select>
            </div>
          )}

          {/* Severidade (para relatórios de incidentes) */}
          {reportType === 'incidents' && (
            <div className="filter-field">
              <label>Severidade</label>
              <select 
                value={filters.severity || ''}
                onChange={(e) => setFilters({...filters, severity: e.target.value})}
              >
                <option value="">Todas</option>
                <option value="critical">Crítico</option>
                <option value="warning">Aviso</option>
                <option value="info">Informação</option>
              </select>
            </div>
          )}

          {/* Status (para relatórios de incidentes) */}
          {reportType === 'incidents' && (
            <div className="filter-field">
              <label>Status</label>
              <select 
                value={filters.status || ''}
                onChange={(e) => setFilters({...filters, status: e.target.value})}
              >
                <option value="">Todos</option>
                <option value="open">Aberto</option>
                <option value="acknowledged">Reconhecido</option>
                <option value="resolved">Resolvido</option>
              </select>
            </div>
          )}

          {/* Limite de resultados */}
          <div className="filter-field">
            <label>Limite de Resultados</label>
            <select 
              value={filters.limit || 100}
              onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
            >
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="500">500</option>
            </select>
          </div>
        </div>
      </div>
    );
  };

  const renderColumnSelector = () => {
    if (!selectedTemplate) return null;

    const availableColumns = {
      incidents: [
        { id: 'created_at', label: 'Data/Hora' },
        { id: 'hostname', label: 'Servidor' },
        { id: 'ip_address', label: 'IP' },
        { id: 'sensor_name', label: 'Sensor' },
        { id: 'sensor_type', label: 'Tipo' },
        { id: 'severity', label: 'Severidade' },
        { id: 'status', label: 'Status' },
        { id: 'description', label: 'Descrição' },
        { id: 'resolution_time', label: 'Tempo de Resolução' },
        { id: 'age_hours', label: 'Idade' }
      ],
      servers: [
        { id: 'hostname', label: 'Hostname' },
        { id: 'ip_address', label: 'IP' },
        { id: 'os_type', label: 'Sistema Operacional' },
        { id: 'environment', label: 'Ambiente' },
        { id: 'device_type', label: 'Tipo de Dispositivo' },
        { id: 'is_active', label: 'Ativo' },
        { id: 'incidents_count', label: 'Total de Incidentes' }
      ],
      errors: [
        { id: 'error_type', label: 'Tipo de Erro' },
        { id: 'sensor_type', label: 'Tipo de Sensor' },
        { id: 'occurrence_count', label: 'Ocorrências' },
        { id: 'affected_servers', label: 'Servidores Afetados' },
        { id: 'first_seen', label: 'Primeira Ocorrência' },
        { id: 'last_seen', label: 'Última Ocorrência' }
      ]
    };

    const columns = availableColumns[selectedTemplate.report_type] || availableColumns.incidents;

    return (
      <div className="builder-section">
        <h3>📋 Colunas</h3>
        <div className="columns-selector">
          {columns.map(col => (
            <div
              key={col.id}
              className={`column-chip ${selectedColumns.includes(col.id) ? 'selected' : ''}`}
              onClick={() => {
                if (selectedColumns.includes(col.id)) {
                  setSelectedColumns(selectedColumns.filter(c => c !== col.id));
                } else {
                  setSelectedColumns([...selectedColumns, col.id]);
                }
              }}
            >
              {selectedColumns.includes(col.id) && '✓ '}
              {col.label}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderReportTable = () => {
    if (!reportData || !reportData.data) return null;

    const rows = reportData.data.rows || [];
    if (rows.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <h3>Nenhum dado encontrado</h3>
          <p>Tente ajustar os filtros do relatório</p>
        </div>
      );
    }

    const headers = selectedColumns.length > 0 
      ? selectedColumns 
      : Object.keys(rows[0]);

    return (
      <div className="report-preview">
        <div style={{marginBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div>
            <strong>{reportData.data.total_count}</strong> resultado(s) encontrado(s)
          </div>
          <div style={{fontSize: '12px', color: '#666'}}>
            Gerado em: {new Date(reportData.report.generated_at).toLocaleString('pt-BR')}
          </div>
        </div>
        
        <table className="report-table">
          <thead>
            <tr>
              {headers.map(header => (
                <th key={header}>{formatColumnName(header)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={idx}>
                {headers.map(header => (
                  <td key={header}>{formatCellValue(header, row[header])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const formatColumnName = (name) => {
    const names = {
      'created_at': 'Data/Hora',
      'hostname': 'Servidor',
      'ip_address': 'IP',
      'sensor_name': 'Sensor',
      'sensor_type': 'Tipo',
      'severity': 'Severidade',
      'status': 'Status',
      'description': 'Descrição',
      'resolution_time': 'Tempo de Resolução',
      'age_hours': 'Idade',
      'os_type': 'Sistema Operacional',
      'environment': 'Ambiente',
      'device_type': 'Tipo',
      'is_active': 'Ativo',
      'incidents_count': 'Incidentes',
      'error_type': 'Tipo de Erro',
      'occurrence_count': 'Ocorrências',
      'affected_servers': 'Servidores Afetados',
      'first_seen': 'Primeira Ocorrência',
      'last_seen': 'Última Ocorrência'
    };
    return names[name] || name;
  };

  const formatCellValue = (column, value) => {
    if (value === null || value === undefined) return '-';

    // Status badges
    if (column === 'severity') {
      return <span className={`status-badge ${value}`}>{value}</span>;
    }
    if (column === 'status') {
      return <span className={`status-badge ${value}`}>{value}</span>;
    }

    // Datas
    if (column.includes('_at') || column.includes('_seen')) {
      try {
        return new Date(value).toLocaleString('pt-BR');
      } catch {
        return value;
      }
    }

    // Booleanos
    if (typeof value === 'boolean') {
      return value ? '✓ Sim' : '✗ Não';
    }

    return value;
  };

  return (
    <div className="custom-reports-container">
      {/* Sidebar */}
      <div className="reports-sidebar">
        <h2>📊 Relatórios</h2>
        
        <div className="sidebar-tabs">
          <button 
            className={`sidebar-tab ${activeTab === 'templates' ? 'active' : ''}`}
            onClick={() => setActiveTab('templates')}
          >
            Templates
          </button>
          <button 
            className={`sidebar-tab ${activeTab === 'my_reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('my_reports')}
          >
            Meus Relatórios
          </button>
        </div>

        {activeTab === 'templates' && (
          <div>
            {templates.map(template => (
              <div
                key={template.id}
                className={`template-card ${selectedTemplate?.id === template.id ? 'active' : ''}`}
                onClick={() => handleSelectTemplate(template)}
              >
                <div className="template-header">
                  <span className="template-icon">{template.icon}</span>
                  <span className="template-title">{template.name}</span>
                </div>
                <div className="template-description">{template.description}</div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'my_reports' && (
          <div>
            {myReports.length === 0 ? (
              <div className="empty-state">
                <p>Nenhum relatório salvo</p>
              </div>
            ) : (
              myReports.map(report => (
                <div
                  key={report.id}
                  className={`template-card ${selectedTemplate?.id === report.id ? 'active' : ''}`}
                  onClick={() => handleSelectTemplate(report)}
                >
                  <div className="template-header">
                    <span className="template-icon">📄</span>
                    <span className="template-title">{report.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteReport(report.id);
                      }}
                      style={{marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px'}}
                    >
                      🗑️
                    </button>
                  </div>
                  {report.description && (
                    <div className="template-description">{report.description}</div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="reports-main">
        <div className="reports-toolbar">
          <div className="toolbar-left">
            <h1>{selectedTemplate ? selectedTemplate.name : 'Selecione um relatório'}</h1>
            {selectedTemplate && (
              <div className="toolbar-subtitle">{selectedTemplate.description}</div>
            )}
          </div>
          <div className="toolbar-actions">
            {selectedTemplate && (
              <>
                <button className="btn-toolbar primary" onClick={handleGenerateReport} disabled={loading}>
                  {loading ? '⏳ Gerando...' : '▶️ Gerar Relatório'}
                </button>
                {reportData && (
                  <>
                    <button className="btn-toolbar" onClick={handleExport}>
                      📥 Exportar CSV
                    </button>
                    <button className="btn-toolbar" onClick={() => setShowSaveModal(true)}>
                      💾 Salvar Relatório
                    </button>
                  </>
                )}
              </>
            )}
          </div>
        </div>

        <div className="report-builder">
          {selectedTemplate ? (
            <>
              {renderFilterBuilder()}
              {renderColumnSelector()}
              
              {loading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Gerando relatório...</p>
                </div>
              ) : (
                renderReportTable()
              )}
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <h3>Selecione um template ou relatório salvo</h3>
              <p>Escolha um template na barra lateral para começar</p>
            </div>
          )}
        </div>
      </div>

      {/* Save Modal */}
      {showSaveModal && (
        <div className="modal-overlay" onClick={() => setShowSaveModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>💾 Salvar Relatório</h2>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome do Relatório *</label>
                <input
                  type="text"
                  value={reportName}
                  onChange={(e) => setReportName(e.target.value)}
                  placeholder="Ex: Servidores Críticos - Produção"
                />
              </div>
              <div className="form-group">
                <label>Descrição</label>
                <textarea
                  value={reportDescription}
                  onChange={(e) => setReportDescription(e.target.value)}
                  placeholder="Descreva o objetivo deste relatório..."
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-modal" onClick={() => setShowSaveModal(false)}>
                Cancelar
              </button>
              <button className="btn-modal primary" onClick={handleSaveReport}>
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CustomReports;
