import React, { useState, useEffect } from 'react';
import api from '../services/api';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import './Management.css';
import './Reports.css';

function Reports() {
  const [activeTab, setActiveTab] = useState('standard'); // standard, custom
  const [templates, setTemplates] = useState([]);
  const [customTemplates, setCustomTemplates] = useState([]);
  const [myReports, setMyReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Custom Reports State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingReport, setEditingReport] = useState(null);
  const [reportName, setReportName] = useState('');
  const [reportDescription, setReportDescription] = useState('');
  const [reportType, setReportType] = useState('incidents');
  const [filters, setFilters] = useState({});
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    loadTemplates();
    loadCustomTemplates();
    loadMyReports();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await api.get('/api/v1/reports/templates');
      setTemplates(response.data);
    } catch (error) {
      console.error('Erro ao carregar templates:', error);
    }
  };

  const loadCustomTemplates = async () => {
    try {
      console.log('Carregando templates personalizados...');
      const response = await api.get('/api/v1/custom-reports/templates');
      console.log('Templates personalizados carregados:', response.data);
      setCustomTemplates(response.data);
    } catch (error) {
      console.error('Erro ao carregar templates personalizados:', error);
      console.error('Detalhes do erro:', error.response?.data);
    }
  };

  const loadMyReports = async () => {
    try {
      console.log('Carregando meus relatórios...');
      const response = await api.get('/api/v1/custom-reports/');
      console.log('Meus relatórios carregados:', response.data);
      setMyReports(response.data);
    } catch (error) {
      console.error('Erro ao carregar meus relatórios:', error);
      console.error('Detalhes do erro:', error.response?.data);
    }
  };

  const handlePrint = () => {
    // Adicionar classe para impressão
    document.body.classList.add('printing-report');
    
    // Imprimir
    window.print();
    
    // Remover classe após impressão
    setTimeout(() => {
      document.body.classList.remove('printing-report');
    }, 1000);
  };

  const generateReport = async (templateId) => {
    setLoading(true);
    setSelectedReport(templateId);
    setReportData(null);

    try {
      let response;
      
      if (templateId.startsWith('availability_')) {
        const period = templateId.replace('availability_', '');
        response = await api.get(`/api/v1/reports/generate/availability/${period}`);
      } else if (templateId.startsWith('problems_')) {
        const period = templateId.replace('problems_', '');
        response = await api.get(`/api/v1/reports/generate/problems/${period}`);
      } else if (templateId.startsWith('ai_resolution_')) {
        const period = templateId.replace('ai_resolution_', '');
        response = await api.get(`/api/v1/reports/generate/ai-resolution/${period}`);
      } else if (templateId === 'cpu_utilization_monthly') {
        response = await api.get('/api/v1/reports/generate/cpu-utilization/monthly');
      } else if (templateId === 'memory_utilization_monthly') {
        response = await api.get('/api/v1/reports/generate/memory-utilization/monthly');
      }

      setReportData(response.data);
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
      alert('Erro ao gerar relatório: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCustomTemplate = async (template) => {
    setSelectedReport(template.id);
    setReportName(template.name);
    setReportDescription(template.description || '');
    setFilters(template.filters || {});
    setSelectedColumns(template.columns || []);
    setReportData(null);
    
    // Gerar automaticamente o relatório
    setLoading(true);
    try {
      // Se for um relatório salvo (ID numérico), usar endpoint de geração
      if (typeof template.id === 'number') {
        const response = await api.post(`/api/v1/custom-reports/${template.id}/generate`);
        setReportData(response.data);
      } else {
        // É um template, gerar com filtros atuais
        const response = await api.post('/api/v1/custom-reports/generate-template', {
          template_id: template.id,
          filters: template.filters || {}
        });
        setReportData(response.data);
      }
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
      alert('Erro ao gerar relatório: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCustomReport = async () => {
    if (!selectedReport) return;

    setLoading(true);
    try {
      // Se for um relatório salvo (ID numérico), usar endpoint de geração
      if (typeof selectedReport === 'number') {
        const response = await api.post(`/api/v1/custom-reports/${selectedReport}/generate`);
        setReportData(response.data);
      } else {
        // É um template, gerar com filtros atuais
        const response = await api.post('/api/v1/custom-reports/generate-template', {
          template_id: selectedReport,
          filters: filters
        });
        setReportData(response.data);
      }
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
      alert('Erro ao gerar relatório: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCreateModal = (template = null) => {
    if (template) {
      // Criar baseado em template
      setReportName(template.name + ' - Cópia');
      setReportDescription(template.description || '');
      setReportType(template.report_type);
      setFilters(template.filters || {});
      setSelectedColumns(template.columns || []);
      setSortBy(template.sort_by || '');
      setSortOrder(template.sort_order || 'desc');
    } else {
      // Criar do zero
      setReportName('');
      setReportDescription('');
      setReportType('incidents');
      setFilters({});
      setSelectedColumns([]);
      setSortBy('');
      setSortOrder('desc');
    }
    setShowCreateModal(true);
  };

  const handleOpenEditModal = (report) => {
    setEditingReport(report);
    setReportName(report.name);
    setReportDescription(report.description || '');
    setReportType(report.report_type);
    setFilters(report.filters || {});
    setSelectedColumns(report.columns || []);
    setSortBy(report.sort_by || '');
    setSortOrder(report.sort_order || 'desc');
    setShowEditModal(true);
  };

  const handleSaveCustomReport = async () => {
    if (!reportName) {
      alert('Por favor, informe um nome para o relatório');
      return;
    }

    try {
      const reportData = {
        name: reportName,
        description: reportDescription,
        report_type: reportType,
        filters: filters,
        columns: selectedColumns.length > 0 ? selectedColumns : getDefaultColumns(reportType),
        sort_by: sortBy,
        sort_order: sortOrder,
        is_public: false,
        is_favorite: false
      };

      if (editingReport) {
        // Atualizar relatório existente
        await api.put(`/api/v1/custom-reports/${editingReport.id}`, reportData);
        alert('Relatório atualizado com sucesso!');
        setShowEditModal(false);
      } else {
        // Criar novo relatório
        await api.post('/api/v1/custom-reports/', reportData);
        alert('Relatório criado com sucesso!');
        setShowCreateModal(false);
      }
      
      loadMyReports();
      setEditingReport(null);
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
      if (selectedReport === reportId) {
        setSelectedReport(null);
        setReportData(null);
      }
    } catch (error) {
      console.error('Erro ao excluir relatório:', error);
      alert('Erro ao excluir relatório: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getDefaultColumns = (type) => {
    const columnsByType = {
      incidents: ['created_at', 'hostname', 'sensor_name', 'severity', 'status', 'description'],
      servers: ['hostname', 'ip_address', 'os_type', 'environment', 'incidents_count'],
      errors: ['error_type', 'occurrence_count', 'affected_servers', 'first_seen', 'last_seen'],
      availability: ['hostname', 'ip_address', 'uptime_percentage', 'downtime_hours'],
      performance: ['hostname', 'cpu_avg', 'memory_avg', 'disk_usage']
    };
    return columnsByType[type] || [];
  };

  const getAvailableColumns = (type) => {
    const columnsByType = {
      incidents: [
        { value: 'created_at', label: 'Data/Hora' },
        { value: 'hostname', label: 'Servidor' },
        { value: 'ip_address', label: 'IP' },
        { value: 'sensor_name', label: 'Sensor' },
        { value: 'sensor_type', label: 'Tipo de Sensor' },
        { value: 'severity', label: 'Severidade' },
        { value: 'status', label: 'Status' },
        { value: 'description', label: 'Descrição' },
        { value: 'resolution_time', label: 'Tempo de Resolução' },
        { value: 'age_hours', label: 'Idade' }
      ],
      servers: [
        { value: 'hostname', label: 'Servidor' },
        { value: 'ip_address', label: 'IP' },
        { value: 'os_type', label: 'Sistema Operacional' },
        { value: 'environment', label: 'Ambiente' },
        { value: 'device_type', label: 'Tipo' },
        { value: 'is_active', label: 'Ativo' },
        { value: 'incidents_count', label: 'Incidentes' }
      ],
      errors: [
        { value: 'error_type', label: 'Tipo de Erro' },
        { value: 'sensor_type', label: 'Tipo de Sensor' },
        { value: 'occurrence_count', label: 'Ocorrências' },
        { value: 'affected_servers', label: 'Servidores Afetados' },
        { value: 'first_seen', label: 'Primeira Ocorrência' },
        { value: 'last_seen', label: 'Última Ocorrência' }
      ]
    };
    return columnsByType[type] || columnsByType.incidents;
  };

  const handleExportCSV = () => {
    if (!reportData || !reportData.data) return;

    const rows = reportData.data.rows || [];
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

  const renderAvailabilityReport = (data) => (
    <div className="report-content">
      <h3>Relatório de Disponibilidade - {data.period}</h3>
      <div className="report-summary">
        <div className="summary-card">
          <h4>Período</h4>
          <p>{data.start_date} até {data.end_date}</p>
        </div>
        <div className="summary-card">
          <h4>Total de Servidores</h4>
          <p className="big-number">{data.total_servers}</p>
        </div>
        <div className="summary-card">
          <h4>Disponibilidade Média</h4>
          <p className="big-number success">{data.availability_percentage}%</p>
        </div>
        <div className="summary-card">
          <h4>Tempo de Inatividade</h4>
          <p className="big-number warning">{data.total_downtime_hours}h</p>
        </div>
      </div>

      <h4>Detalhes por Servidor</h4>
      <table className="report-table">
        <thead>
          <tr>
            <th>Hostname</th>
            <th>IP</th>
            <th>Disponibilidade</th>
            <th>Incidentes</th>
          </tr>
        </thead>
        <tbody>
          {data.servers_detail.map((server, idx) => (
            <tr key={idx}>
              <td>{server.hostname}</td>
              <td>{server.ip_address}</td>
              <td>
                <span className={server.availability >= 99 ? 'status-ok' : server.availability >= 95 ? 'status-warning' : 'status-critical'}>
                  {server.availability}%
                </span>
              </td>
              <td>{server.incidents}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderProblemsReport = (data) => (
    <div className="report-content">
      <h3>Máquinas com Mais Problemas - {data.period}</h3>
      
      {data.servers_with_most_problems.length === 0 ? (
        <div className="no-data">
          <p>✅ Nenhum incidente registrado no período</p>
        </div>
      ) : (
        <table className="report-table">
          <thead>
            <tr>
              <th>Posição</th>
              <th>Hostname</th>
              <th>IP</th>
              <th>Total de Incidentes</th>
              <th>Críticos</th>
              <th>Avisos</th>
            </tr>
          </thead>
          <tbody>
            {data.servers_with_most_problems.map((server, idx) => (
              <tr key={idx}>
                <td>
                  <span className="rank-badge">{idx + 1}º</span>
                </td>
                <td>{server.hostname}</td>
                <td>{server.ip_address}</td>
                <td className="big-number">{server.total_incidents}</td>
                <td>
                  <span className="status-critical">{server.critical_incidents}</span>
                </td>
                <td>
                  <span className="status-warning">{server.warning_incidents}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );

  const renderAIResolutionReport = (data) => (
    <div className="report-content">
      <h3>Resoluções por IA - {data.period}</h3>
      <div className="report-summary">
        <div className="summary-card">
          <h4>Total de Incidentes</h4>
          <p className="big-number">{data.total_incidents}</p>
        </div>
        <div className="summary-card">
          <h4>Resolvidos pela IA</h4>
          <p className="big-number success">{data.ai_resolved}</p>
        </div>
        <div className="summary-card">
          <h4>Taxa de Resolução IA</h4>
          <p className="big-number success">{data.ai_resolution_rate}%</p>
        </div>
        <div className="summary-card">
          <h4>Resolvidos Manualmente</h4>
          <p className="big-number">{data.manual_resolved}</p>
        </div>
      </div>

      <div className="ai-insights">
        <h4>💡 Insights</h4>
        <ul>
          <li>
            A IA resolveu automaticamente {data.ai_resolved} de {data.total_incidents} incidentes ({data.ai_resolution_rate}%)
          </li>
          <li>
            Economia estimada: {Math.round(data.ai_resolved * 0.5)} horas de trabalho manual
          </li>
          <li>
            {data.ai_resolution_rate >= 50 
              ? '✅ Excelente taxa de automação!' 
              : data.ai_resolution_rate >= 25
              ? '⚠️ Taxa de automação moderada'
              : '🔴 Taxa de automação baixa - considere ajustar as regras de auto-resolução'}
          </li>
        </ul>
      </div>
    </div>
  );

  const renderCPUUtilizationReport = (data) => (
    <div className="report-content executive-report">
      <div className="executive-header">
        <div className="company-logo">🦉 Coruja Monitor</div>
        <div className="report-title">
          <h2>Relatório Executivo</h2>
          <h3>Utilização de CPU - {data.period}</h3>
          <p className="report-date">Gerado em: {new Date().toLocaleDateString('pt-BR')}</p>
        </div>
      </div>

      <div className="executive-summary">
        <h3>📊 Resumo Executivo</h3>
        <div className="summary-grid">
          <div className="summary-card highlight">
            <div className="card-icon">💻</div>
            <div className="card-content">
              <h4>Utilização Média</h4>
              <p className="big-number">{data.average_utilization}%</p>
              <small>Média geral do período</small>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">📈</div>
            <div className="card-content">
              <h4>Pico Máximo</h4>
              <p className="big-number warning">{data.peak_utilization}%</p>
              <small>Maior utilização registrada</small>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">📉</div>
            <div className="card-content">
              <h4>Utilização Mínima</h4>
              <p className="big-number success">{data.min_utilization}%</p>
              <small>Menor utilização registrada</small>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">🖥️</div>
            <div className="card-content">
              <h4>Servidores Analisados</h4>
              <p className="big-number">{data.total_servers}</p>
              <small>Total no período</small>
            </div>
          </div>
        </div>
      </div>

      <div className="chart-section">
        <h3>📈 Evolução da Utilização de CPU</h3>
        <div className="chart-container">
          <CPUChart data={data.daily_data} />
        </div>
      </div>

      <div className="sizing-analysis">
        <h3>💡 Análise de Dimensionamento</h3>
        <div className="analysis-grid">
          {data.servers_analysis.map((server, idx) => (
            <div key={idx} className={`analysis-card ${server.recommendation_type}`}>
              <div className="server-info">
                <h4>{server.hostname}</h4>
                <p className="server-ip">{server.ip_address}</p>
              </div>
              <div className="utilization-bar">
                <div className="bar-fill" style={{width: `${server.avg_utilization}%`, backgroundColor: getUtilizationColor(server.avg_utilization)}}></div>
                <span className="bar-label">{server.avg_utilization}%</span>
              </div>
              <div className="recommendation">
                <span className="recommendation-icon">{getRecommendationIcon(server.recommendation_type)}</span>
                <div className="recommendation-text">
                  <strong>{server.recommendation_title}</strong>
                  <p>{server.recommendation_detail}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="recommendations-section">
        <h3>🎯 Recomendações Estratégicas</h3>
        <div className="recommendations-list">
          {data.strategic_recommendations.map((rec, idx) => (
            <div key={idx} className={`recommendation-item ${rec.priority}`}>
              <div className="rec-priority">{rec.priority.toUpperCase()}</div>
              <div className="rec-content">
                <h4>{rec.title}</h4>
                <p>{rec.description}</p>
                <div className="rec-impact">
                  <strong>Impacto:</strong> {rec.impact}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="cost-analysis">
        <h3>💰 Análise de Custos</h3>
        <div className="cost-grid">
          <div className="cost-card">
            <h4>Economia Potencial</h4>
            <p className="cost-value success">R$ {data.potential_savings.toLocaleString('pt-BR')}/mês</p>
            <small>Redimensionando servidores sobredimensionados</small>
          </div>
          <div className="cost-card">
            <h4>Investimento Necessário</h4>
            <p className="cost-value warning">R$ {data.required_investment.toLocaleString('pt-BR')}</p>
            <small>Para servidores subdimensionados</small>
          </div>
          <div className="cost-card">
            <h4>ROI Estimado</h4>
            <p className="cost-value">{data.roi_months} meses</p>
            <small>Retorno sobre investimento</small>
          </div>
        </div>
      </div>

      {data.cloud_costs && (
        <div className="cloud-costs-section">
          <h4>☁️ Comparação de Custos em Nuvem</h4>
          <p className="section-description">
            Estimativa de custos mensais para hospedar esta infraestrutura em diferentes provedores de nuvem
          </p>
          
          <div className="cloud-providers-grid">
            <div className="cloud-provider-card azure">
              <div className="provider-header">
                <span className="provider-icon">☁️</span>
                <h5>Microsoft Azure</h5>
              </div>
              <div className="provider-details">
                <div className="detail-row">
                  <span>Tamanho Recomendado:</span>
                  <strong>{data.cloud_costs.costs_by_provider.azure.recommended_size.toUpperCase()}</strong>
                </div>
                <div className="detail-row">
                  <span>CPU / RAM:</span>
                  <strong>{data.cloud_costs.costs_by_provider.azure.cpu_cores} cores / {data.cloud_costs.costs_by_provider.azure.ram_gb} GB</strong>
                </div>
                <div className="detail-row highlight">
                  <span>Custo Mensal:</span>
                  <strong>R$ {data.cloud_costs.costs_by_provider.azure.monthly_cost_brl.toLocaleString('pt-BR')}</strong>
                </div>
                <div className="detail-row">
                  <span>Custo Anual:</span>
                  <strong>R$ {data.cloud_costs.costs_by_provider.azure.annual_cost_brl.toLocaleString('pt-BR')}</strong>
                </div>
              </div>
            </div>

            <div className="cloud-provider-card aws">
              <div className="provider-header">
                <span className="provider-icon">🟠</span>
                <h5>Amazon AWS</h5>
              </div>
              <div className="provider-details">
                <div className="detail-row">
                  <span>Tamanho Recomendado:</span>
                  <strong>{data.cloud_costs.costs_by_provider.aws.recommended_size.toUpperCase()}</strong>
                </div>
                <div className="detail-row">
                  <span>CPU / RAM:</span>
                  <strong>{data.cloud_costs.costs_by_provider.aws.cpu_cores} cores / {data.cloud_costs.costs_by_provider.aws.ram_gb} GB</strong>
                </div>
                <div className="detail-row highlight">
                  <span>Custo Mensal:</span>
                  <strong>R$ {data.cloud_costs.costs_by_provider.aws.monthly_cost_brl.toLocaleString('pt-BR')}</strong>
                </div>
                <div className="detail-row">
                  <span>Custo Anual:</span>
                  <strong>R$ {data.cloud_costs.costs_by_provider.aws.annual_cost_brl.toLocaleString('pt-BR')}</strong>
                </div>
              </div>
            </div>

            <div className="cloud-provider-card gcp">
              <div className="provider-header">
                <span className="provider-icon">🔵</span>
                <h5>Google Cloud (GCP)</h5>
              </div>
              <div className="provider-details">
                <div className="detail-row">
                  <span>Tamanho Recomendado:</span>
                  <strong>{data.cloud_costs.costs_by_provider.gcp.recommended_size.toUpperCase()}</strong>
                </div>
                <div className="detail-row">
                  <span>CPU / RAM:</span>
                  <strong>{data.cloud_costs.costs_by_provider.gcp.cpu_cores} cores / {data.cloud_costs.costs_by_provider.gcp.ram_gb} GB</strong>
                </div>
                <div className="detail-row highlight">
                  <span>Custo Mensal:</span>
                  <strong>R$ {data.cloud_costs.costs_by_provider.gcp.monthly_cost_brl.toLocaleString('pt-BR')}</strong>
                </div>
                <div className="detail-row">
                  <span>Custo Anual:</span>
                  <strong>R$ {data.cloud_costs.costs_by_provider.gcp.annual_cost_brl.toLocaleString('pt-BR')}</strong>
                </div>
              </div>
            </div>

            <div className="cloud-provider-card hyperv">
              <div className="provider-header">
                <span className="provider-icon">🖥️</span>
                <h5>Hyper-V (On-Premise)</h5>
              </div>
              <div className="provider-details">
                <div className="detail-row">
                  <span>Tamanho Recomendado:</span>
                  <strong>{data.cloud_costs.costs_by_provider.hyperv.recommended_size.toUpperCase()}</strong>
                </div>
                <div className="detail-row">
                  <span>CPU / RAM:</span>
                  <strong>{data.cloud_costs.costs_by_provider.hyperv.cpu_cores} cores / {data.cloud_costs.costs_by_provider.hyperv.ram_gb} GB</strong>
                </div>
                <div className="detail-row highlight">
                  <span>Custo Mensal:</span>
                  <strong>R$ {data.cloud_costs.costs_by_provider.hyperv.monthly_cost_brl.toLocaleString('pt-BR')}</strong>
                </div>
                <div className="detail-row">
                  <span>Custo Anual:</span>
                  <strong>R$ {data.cloud_costs.costs_by_provider.hyperv.annual_cost_brl.toLocaleString('pt-BR')}</strong>
                </div>
              </div>
            </div>
          </div>

          <div className="cost-comparison">
            <div className="comparison-card best">
              <h5>💚 MELHOR CUSTO-BENEFÍCIO</h5>
              <div className="provider-name">{data.cloud_costs.cheapest_provider.toUpperCase()}</div>
              <div className="cost-value">R$ {data.cloud_costs.cheapest_cost.toLocaleString('pt-BR')}/mês</div>
              <small>Opção mais econômica</small>
            </div>
            
            <div className="comparison-card savings">
              <h5>💰 ECONOMIA POTENCIAL</h5>
              <div className="cost-value success">R$ {data.cloud_costs.potential_savings.toLocaleString('pt-BR')}/mês</div>
              <div className="savings-text">
                Escolhendo {data.cloud_costs.cheapest_provider.toUpperCase()} ao invés de {data.cloud_costs.most_expensive_provider.toUpperCase()}
              </div>
              <small>Economia anual: R$ {(data.cloud_costs.potential_savings * 12).toLocaleString('pt-BR')}</small>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderMemoryUtilizationReport = (data) => (
    <div className="report-content executive-report">
      <div className="executive-header">
        <div className="company-logo">🦉 Coruja Monitor</div>
        <div className="report-title">
          <h2>Relatório Executivo</h2>
          <h3>Utilização de Memória - {data.period}</h3>
          <p className="report-date">Gerado em: {new Date().toLocaleDateString('pt-BR')}</p>
        </div>
      </div>

      <div className="executive-summary">
        <h3>📊 Resumo Executivo</h3>
        <div className="summary-grid">
          <div className="summary-card highlight">
            <div className="card-icon">💾</div>
            <div className="card-content">
              <h4>Utilização Média</h4>
              <p className="big-number">{data.average_utilization}%</p>
              <small>Média geral do período</small>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">📈</div>
            <div className="card-content">
              <h4>Pico Máximo</h4>
              <p className="big-number warning">{data.peak_utilization}%</p>
              <small>Maior utilização registrada</small>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">📉</div>
            <div className="card-content">
              <h4>Utilização Mínima</h4>
              <p className="big-number success">{data.min_utilization}%</p>
              <small>Menor utilização registrada</small>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">🖥️</div>
            <div className="card-content">
              <h4>Servidores Analisados</h4>
              <p className="big-number">{data.total_servers}</p>
              <small>Total no período</small>
            </div>
          </div>
        </div>
      </div>

      <div className="chart-section">
        <h3>📈 Evolução da Utilização de Memória</h3>
        <div className="chart-container">
          <MemoryChart data={data.daily_data} />
        </div>
      </div>

      <div className="sizing-analysis">
        <h3>💡 Análise de Dimensionamento</h3>
        <div className="analysis-grid">
          {data.servers_analysis.map((server, idx) => (
            <div key={idx} className={`analysis-card ${server.recommendation_type}`}>
              <div className="server-info">
                <h4>{server.hostname}</h4>
                <p className="server-ip">{server.ip_address}</p>
              </div>
              <div className="utilization-bar">
                <div className="bar-fill" style={{width: `${server.avg_utilization}%`, backgroundColor: getUtilizationColor(server.avg_utilization)}}></div>
                <span className="bar-label">{server.avg_utilization}%</span>
              </div>
              <div className="recommendation">
                <span className="recommendation-icon">{getRecommendationIcon(server.recommendation_type)}</span>
                <div className="recommendation-text">
                  <strong>{server.recommendation_title}</strong>
                  <p>{server.recommendation_detail}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="recommendations-section">
        <h3>🎯 Recomendações Estratégicas</h3>
        <div className="recommendations-list">
          {data.strategic_recommendations.map((rec, idx) => (
            <div key={idx} className={`recommendation-item ${rec.priority}`}>
              <div className="rec-priority">{rec.priority.toUpperCase()}</div>
              <div className="rec-content">
                <h4>{rec.title}</h4>
                <p>{rec.description}</p>
                <div className="rec-impact">
                  <strong>Impacto:</strong> {rec.impact}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="cost-analysis">
        <h3>💰 Análise de Custos</h3>
        <div className="cost-grid">
          <div className="cost-card">
            <h4>Economia Potencial</h4>
            <p className="cost-value success">R$ {data.potential_savings.toLocaleString('pt-BR')}/mês</p>
            <small>Redimensionando servidores sobredimensionados</small>
          </div>
          <div className="cost-card">
            <h4>Investimento Necessário</h4>
            <p className="cost-value warning">R$ {data.required_investment.toLocaleString('pt-BR')}</p>
            <small>Para servidores subdimensionados</small>
          </div>
          <div className="cost-card">
            <h4>ROI Estimado</h4>
            <p className="cost-value">{data.roi_months} meses</p>
            <small>Retorno sobre investimento</small>
          </div>
        </div>
      </div>
    </div>
  );

  const getUtilizationColor = (utilization) => {
    if (utilization < 30) return '#4caf50'; // Verde - Subutilizado
    if (utilization < 70) return '#2196f3'; // Azul - Ideal
    if (utilization < 85) return '#ff9800'; // Laranja - Alto
    return '#f44336'; // Vermelho - Crítico
  };

  const getRecommendationIcon = (type) => {
    switch(type) {
      case 'downsize': return '📉';
      case 'upsize': return '📈';
      case 'optimal': return '✅';
      default: return '📊';
    }
  };

  // Componentes de gráfico modernos usando Recharts (estilo Grafana)
  const CPUChart = ({ data }) => {
    if (!data || data.length === 0) {
      return <div className="no-data">Sem dados disponíveis</div>;
    }

    // Formatar dados para Recharts
    const chartData = data.map((point, index) => ({
      day: `Dia ${index + 1}`,
      cpu: point.value,
      threshold_warning: 80,
      threshold_critical: 95
    }));

    const CustomTooltip = ({ active, payload }) => {
      if (active && payload && payload.length) {
        return (
          <div className="custom-tooltip">
            <p className="label">{payload[0].payload.day}</p>
            <p className="value" style={{color: '#2196f3'}}>
              CPU: {payload[0].value.toFixed(1)}%
            </p>
          </div>
        );
      }
      return null;
    };

    return (
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2196f3" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#2196f3" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="day" 
            stroke="#666"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#666"
            style={{ fontSize: '12px' }}
            domain={[0, 100]}
            label={{ value: 'Utilização (%)', angle: -90, position: 'insideLeft', style: { fontSize: '12px' } }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontSize: '12px' }}
            iconType="line"
          />
          <ReferenceLine 
            y={80} 
            stroke="#ff9800" 
            strokeDasharray="5 5" 
            label={{ value: 'Aviso (80%)', position: 'right', fill: '#ff9800', fontSize: 11 }}
          />
          <ReferenceLine 
            y={95} 
            stroke="#f44336" 
            strokeDasharray="5 5" 
            label={{ value: 'Crítico (95%)', position: 'right', fill: '#f44336', fontSize: 11 }}
          />
          <Area 
            type="monotone" 
            dataKey="cpu" 
            stroke="#2196f3" 
            strokeWidth={3}
            fillOpacity={1} 
            fill="url(#colorCpu)" 
            name="CPU (%)"
            animationDuration={1000}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  };

  const MemoryChart = ({ data }) => {
    if (!data || data.length === 0) {
      return <div className="no-data">Sem dados disponíveis</div>;
    }

    const chartData = data.map((point, index) => ({
      day: `Dia ${index + 1}`,
      memory: point.value,
      threshold_warning: 80,
      threshold_critical: 95
    }));

    const CustomTooltip = ({ active, payload }) => {
      if (active && payload && payload.length) {
        return (
          <div className="custom-tooltip">
            <p className="label">{payload[0].payload.day}</p>
            <p className="value" style={{color: '#9c27b0'}}>
              Memória: {payload[0].value.toFixed(1)}%
            </p>
          </div>
        );
      }
      return null;
    };

    return (
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#9c27b0" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#9c27b0" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="day" 
            stroke="#666"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#666"
            style={{ fontSize: '12px' }}
            domain={[0, 100]}
            label={{ value: 'Utilização (%)', angle: -90, position: 'insideLeft', style: { fontSize: '12px' } }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontSize: '12px' }}
            iconType="line"
          />
          <ReferenceLine 
            y={80} 
            stroke="#ff9800" 
            strokeDasharray="5 5" 
            label={{ value: 'Aviso (80%)', position: 'right', fill: '#ff9800', fontSize: 11 }}
          />
          <ReferenceLine 
            y={95} 
            stroke="#f44336" 
            strokeDasharray="5 5" 
            label={{ value: 'Crítico (95%)', position: 'right', fill: '#f44336', fontSize: 11 }}
          />
          <Area 
            type="monotone" 
            dataKey="memory" 
            stroke="#9c27b0" 
            strokeWidth={3}
            fillOpacity={1} 
            fill="url(#colorMemory)" 
            name="Memória (%)"
            animationDuration={1000}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  };

  const renderReport = () => {
    if (!reportData) return null;

    // Relatórios personalizados
    if (reportData.data && reportData.data.rows) {
      return renderCustomReport(reportData);
    }

    // Relatórios padrão
    if (selectedReport.startsWith('availability_')) {
      return renderAvailabilityReport(reportData);
    } else if (selectedReport.startsWith('problems_')) {
      return renderProblemsReport(reportData);
    } else if (selectedReport.startsWith('ai_resolution_')) {
      return renderAIResolutionReport(reportData);
    } else if (selectedReport === 'cpu_utilization_monthly') {
      return renderCPUUtilizationReport(reportData);
    } else if (selectedReport === 'memory_utilization_monthly') {
      return renderMemoryUtilizationReport(reportData);
    }
  };

  const renderCustomReport = (data) => {
    const rows = data.data.rows || [];
    if (rows.length === 0) {
      return (
        <div className="no-data">
          <p>📊 Nenhum dado encontrado</p>
          <p>Tente ajustar os filtros do relatório</p>
        </div>
      );
    }

    const headers = selectedColumns.length > 0 ? selectedColumns : Object.keys(rows[0]);

    return (
      <div className="report-content">
        <h3>{reportName}</h3>
        {reportDescription && <p>{reportDescription}</p>}
        
        <div style={{marginBottom: '15px'}}>
          <strong>{data.data.total_count}</strong> resultado(s) encontrado(s)
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
    <div className="management-container">
      <div className="management-header">
        <h1>📈 Relatórios</h1>
        <button 
          className="btn-primary"
          onClick={() => handleOpenCreateModal()}
          style={{marginLeft: 'auto'}}
        >
          ➕ Criar Relatório Personalizado
        </button>
      </div>

      <div className="reports-layout">
        <div className="templates-sidebar">
          <h2>Templates Disponíveis</h2>
          
          <div className="template-group">
            <h3>📊 Disponibilidade</h3>
            {templates.filter(t => t.id.startsWith('availability_')).map(template => (
              <button
                key={template.id}
                className={`template-btn ${selectedReport === template.id ? 'active' : ''}`}
                onClick={() => generateReport(template.id)}
                disabled={loading}
              >
                <div className="template-name">{template.name}</div>
                <div className="template-desc">{template.description}</div>
              </button>
            ))}
          </div>

          <div className="template-group">
            <h3>⚠️ Problemas</h3>
            {templates.filter(t => t.id.startsWith('problems_')).map(template => (
              <button
                key={template.id}
                className={`template-btn ${selectedReport === template.id ? 'active' : ''}`}
                onClick={() => generateReport(template.id)}
                disabled={loading}
              >
                <div className="template-name">{template.name}</div>
                <div className="template-desc">{template.description}</div>
              </button>
            ))}
          </div>

          <div className="template-group">
            <h3>🤖 Resoluções IA</h3>
            {templates.filter(t => t.id.startsWith('ai_resolution_')).map(template => (
              <button
                key={template.id}
                className={`template-btn ${selectedReport === template.id ? 'active' : ''}`}
                onClick={() => generateReport(template.id)}
                disabled={loading}
              >
                <div className="template-name">{template.name}</div>
                <div className="template-desc">{template.description}</div>
              </button>
            ))}
          </div>

          <div className="template-group">
            <h3>💻 Utilização de Recursos</h3>
            <button
              className={`template-btn ${selectedReport === 'cpu_utilization_monthly' ? 'active' : ''}`}
              onClick={() => generateReport('cpu_utilization_monthly')}
              disabled={loading}
            >
              <div className="template-name">Utilização de CPU Mensal</div>
              <div className="template-desc">Análise de dimensionamento de CPU</div>
            </button>
            <button
              className={`template-btn ${selectedReport === 'memory_utilization_monthly' ? 'active' : ''}`}
              onClick={() => generateReport('memory_utilization_monthly')}
              disabled={loading}
            >
              <div className="template-name">Utilização de Memória Mensal</div>
              <div className="template-desc">Análise de dimensionamento de Memória</div>
            </button>
          </div>

          {myReports.length > 0 && (
            <div className="template-group">
              <h3>📊 Meus Relatórios Personalizados</h3>
              {myReports.map(report => (
                <div key={report.id} className="custom-report-item">
                  <button
                    className={`template-btn ${selectedReport === report.id ? 'active' : ''}`}
                    onClick={() => handleSelectCustomTemplate(report)}
                    disabled={loading}
                  >
                    <div className="template-name">📄 {report.name}</div>
                    {report.description && (
                      <div className="template-desc">{report.description}</div>
                    )}
                  </button>
                  <div className="report-actions-compact">
                    <button
                      className="btn-action-compact btn-edit"
                      onClick={(e) => { e.stopPropagation(); handleOpenEditModal(report); }}
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button
                      className="btn-action-compact btn-delete"
                      onClick={(e) => { e.stopPropagation(); handleDeleteReport(report.id); }}
                      title="Excluir"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {myReports.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3>Nenhum relatório criado</h3>
              <p>Clique no botão acima para criar seu primeiro relatório personalizado</p>
            </div>
          )}
        </div>

        <div className="report-viewer">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Gerando relatório...</p>
            </div>
          ) : reportData ? (
            <>
              <div className="report-header-actions no-print">
                <div className="report-info">
                  <h2>{reportName}</h2>
                  {reportDescription && <p className="report-subtitle">{reportDescription}</p>}
                </div>
                <div className="report-actions-buttons">
                  {typeof selectedReport === 'number' && (
                    <>
                      <button className="btn-action-header btn-edit-header" onClick={() => {
                        const report = myReports.find(r => r.id === selectedReport);
                        if (report) handleOpenEditModal(report);
                      }}>
                        ✏️ Editar
                      </button>
                      <button className="btn-action-header btn-delete-header" onClick={() => handleDeleteReport(selectedReport)}>
                        🗑️ Excluir
                      </button>
                    </>
                  )}
                  <button className="btn-action-header btn-print" onClick={handlePrint}>
                    🖨️ Imprimir
                  </button>
                </div>
              </div>
              {renderReport()}
            </>
          ) : (
            <div className="no-selection">
              <div className="empty-icon-large">📊</div>
              <h2>Bem-vindo aos Relatórios Personalizados</h2>
              <p>Crie relatórios customizados com as informações que você precisa</p>
              <button className="btn-create-large" onClick={() => handleOpenCreateModal()}>
                ➕ Criar Meu Primeiro Relatório
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Criação/Edição de Relatório */}
      {(showCreateModal || showEditModal) && (
        <div className="modal-overlay" onClick={() => { setShowCreateModal(false); setShowEditModal(false); }}>
          <div className="modal-content custom-report-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingReport ? '✏️ Editar Relatório' : '➕ Criar Relatório Personalizado'}</h2>
              <button className="modal-close" onClick={() => { setShowCreateModal(false); setShowEditModal(false); }}>✕</button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Nome do Relatório *</label>
                <input
                  type="text"
                  value={reportName}
                  onChange={(e) => setReportName(e.target.value)}
                  placeholder="Ex: Servidores Críticos de Produção"
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label>Descrição</label>
                <textarea
                  value={reportDescription}
                  onChange={(e) => setReportDescription(e.target.value)}
                  placeholder="Descreva o objetivo deste relatório..."
                  className="form-control"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>Tipo de Relatório *</label>
                <select
                  value={reportType}
                  onChange={(e) => {
                    setReportType(e.target.value);
                    setSelectedColumns(getDefaultColumns(e.target.value));
                  }}
                  className="form-control"
                >
                  <option value="incidents">📋 Incidentes</option>
                  <option value="servers">🖥️ Servidores</option>
                  <option value="errors">❌ Erros</option>
                  <option value="availability">📊 Disponibilidade</option>
                  <option value="performance">⚡ Performance</option>
                </select>
              </div>

              <div className="form-group">
                <label>Colunas a Exibir</label>
                <div className="columns-selector">
                  {getAvailableColumns(reportType).map(col => (
                    <label key={col.value} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={selectedColumns.includes(col.value)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedColumns([...selectedColumns, col.value]);
                          } else {
                            setSelectedColumns(selectedColumns.filter(c => c !== col.value));
                          }
                        }}
                      />
                      {col.label}
                    </label>
                  ))}
                </div>
              </div>

              {reportType === 'incidents' && (
                <div className="form-group">
                  <label>Filtros</label>
                  <div className="filters-grid">
                    <div>
                      <label>Período</label>
                      <select
                        value={filters.period || ''}
                        onChange={(e) => setFilters({...filters, period: e.target.value})}
                        className="form-control"
                      >
                        <option value="">Todos</option>
                        <option value="last_24_hours">Últimas 24 horas</option>
                        <option value="last_7_days">Últimos 7 dias</option>
                        <option value="last_30_days">Últimos 30 dias</option>
                        <option value="last_90_days">Últimos 90 dias</option>
                      </select>
                    </div>
                    <div>
                      <label>Severidade</label>
                      <select
                        value={filters.severity || ''}
                        onChange={(e) => setFilters({...filters, severity: e.target.value})}
                        className="form-control"
                      >
                        <option value="">Todas</option>
                        <option value="critical">Crítico</option>
                        <option value="warning">Aviso</option>
                        <option value="info">Informação</option>
                      </select>
                    </div>
                    <div>
                      <label>Status</label>
                      <select
                        value={filters.status || ''}
                        onChange={(e) => setFilters({...filters, status: e.target.value})}
                        className="form-control"
                      >
                        <option value="">Todos</option>
                        <option value="open">Aberto</option>
                        <option value="acknowledged">Reconhecido</option>
                        <option value="resolved">Resolvido</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {reportType === 'servers' && (
                <div className="form-group">
                  <label>Filtros</label>
                  <div className="filters-grid">
                    <div>
                      <label>Ambiente</label>
                      <select
                        value={filters.environment || ''}
                        onChange={(e) => setFilters({...filters, environment: e.target.value})}
                        className="form-control"
                      >
                        <option value="">Todos</option>
                        <option value="production">Produção</option>
                        <option value="staging">Homologação</option>
                        <option value="development">Desenvolvimento</option>
                      </select>
                    </div>
                    <div>
                      <label>Status</label>
                      <select
                        value={filters.is_active !== undefined ? filters.is_active.toString() : ''}
                        onChange={(e) => setFilters({...filters, is_active: e.target.value === 'true'})}
                        className="form-control"
                      >
                        <option value="">Todos</option>
                        <option value="true">Ativos</option>
                        <option value="false">Inativos</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              <div className="form-group">
                <label>Ordenação</label>
                <div className="sort-grid">
                  <div>
                    <label>Ordenar por</label>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="form-control"
                    >
                      <option value="">Padrão</option>
                      {getAvailableColumns(reportType).map(col => (
                        <option key={col.value} value={col.value}>{col.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label>Ordem</label>
                    <select
                      value={sortOrder}
                      onChange={(e) => setSortOrder(e.target.value)}
                      className="form-control"
                    >
                      <option value="desc">Decrescente</option>
                      <option value="asc">Crescente</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="btn-secondary" 
                onClick={() => { setShowCreateModal(false); setShowEditModal(false); }}
              >
                Cancelar
              </button>
              <button 
                className="btn-primary" 
                onClick={handleSaveCustomReport}
              >
                {editingReport ? 'Atualizar' : 'Criar'} Relatório
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Reports;
