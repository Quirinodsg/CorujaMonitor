import React, { useState, useEffect } from 'react';
import { 
  sensorCategories, 
  getTemplatesByCategory,
  getRecommendedTemplates 
} from '../data/sensorTemplates';
import './AddSensorModal.css';

function AddSensorModal({ 
  show, 
  onClose, 
  onAdd, 
  server,
  availableServices,
  availableDisks,
  loadingServices,
  loadingDisks 
}) {
  const [step, setStep] = useState(1); // 1: Category, 2: Template, 3: Configure
  const [selectedCategory, setSelectedCategory] = useState('standard');
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [sensorConfig, setSensorConfig] = useState({
    name: '',
    threshold_warning: 80,
    threshold_critical: 95,
    service_name: '',
    disk_name: '',
    custom_target: ''
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (show) {
      // Reset to recommended templates on open
      setStep(1);
      setSelectedCategory('standard');
      setSelectedTemplate(null);
      setSearchTerm('');
    }
  }, [show]);

  if (!show) return null;

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    setStep(2);
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    
    // Set default configuration based on template
    const defaultName = template.default_name || template.name;
    
    setSensorConfig({
      name: defaultName,
      threshold_warning: template.thresholds.warning,
      threshold_critical: template.thresholds.critical,
      service_name: '',
      disk_name: '',
      custom_target: ''
    });
    
    setStep(3);
  };

  const handleServiceSelect = (service) => {
    setSensorConfig({
      ...sensorConfig,
      service_name: service.name,
      name: `service_${service.name}`
    });
  };

  const handleDiskSelect = (disk) => {
    const formattedDisk = disk.name.replace(':', '');
    setSensorConfig({
      ...sensorConfig,
      disk_name: disk.name,
      name: `disk_${formattedDisk}`
    });
  };

  const handleAdd = () => {
    if (!selectedTemplate) return;

    const sensorData = {
      sensor_type: selectedTemplate.sensor_type,
      name: sensorConfig.name,
      threshold_warning: parseFloat(sensorConfig.threshold_warning),
      threshold_critical: parseFloat(sensorConfig.threshold_critical)
    };

    onAdd(sensorData);
    onClose();
  };

  const renderStep1 = () => {
    const recommended = getRecommendedTemplates();
    
    return (
      <div className="add-sensor-step">
        <h3>📚 Biblioteca de Sensores</h3>
        <p className="step-description">Escolha uma categoria ou selecione um sensor recomendado</p>

        {/* Recommended Sensors */}
        <div className="recommended-section">
          <h4>⭐ Sensores Recomendados</h4>
          <div className="sensor-templates-grid">
            {recommended.map(template => (
              <div
                key={template.id}
                className="sensor-template-card recommended"
                onClick={() => handleTemplateSelect(template)}
              >
                <div className="template-icon">{template.icon}</div>
                <div className="template-name">{template.name}</div>
                <div className="template-description">{template.description}</div>
                {template.auto_created && (
                  <div className="auto-badge">Auto-criado</div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Categories */}
        <div className="categories-section">
          <h4>📂 Categorias</h4>
          <div className="categories-grid">
            {Object.entries(sensorCategories).map(([key, category]) => (
              <div
                key={key}
                className="category-card"
                onClick={() => handleCategorySelect(key)}
              >
                <div className="category-icon">{category.icon}</div>
                <div className="category-name">{category.name}</div>
                <div className="category-description">{category.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderStep2 = () => {
    const templates = getTemplatesByCategory(selectedCategory);
    const category = sensorCategories[selectedCategory];

    return (
      <div className="add-sensor-step">
        <button className="btn-back" onClick={() => setStep(1)}>
          ← Voltar
        </button>
        
        <h3>{category.icon} {category.name}</h3>
        <p className="step-description">{category.description}</p>

        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="🔍 Buscar sensor..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Templates */}
        <div className="sensor-templates-grid">
          {templates
            .filter(t => 
              t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
              t.description.toLowerCase().includes(searchTerm.toLowerCase())
            )
            .map(template => (
              <div
                key={template.id}
                className="sensor-template-card"
                onClick={() => handleTemplateSelect(template)}
              >
                <div className="template-icon">{template.icon}</div>
                <div className="template-name">{template.name}</div>
                <div className="template-description">{template.description}</div>
                {template.requires_discovery && (
                  <div className="discovery-badge">Requer descoberta</div>
                )}
              </div>
            ))}
        </div>
      </div>
    );
  };

  const renderStep3 = () => {
    if (!selectedTemplate) return null;

    return (
      <div className="add-sensor-step">
        <button className="btn-back" onClick={() => setStep(2)}>
          ← Voltar
        </button>

        <h3>{selectedTemplate.icon} Configurar: {selectedTemplate.name}</h3>
        <p className="step-description">{selectedTemplate.description}</p>

        <div className="sensor-config-form">
          {/* Discovery Section */}
          {selectedTemplate.requires_discovery && selectedTemplate.discovery_type === 'services' && (
            <div className="form-group">
              <label>Serviço Windows: *</label>
              {loadingServices ? (
                <div className="loading-discovery">🔄 Descobrindo serviços...</div>
              ) : (
                <select
                  value={sensorConfig.service_name}
                  onChange={(e) => {
                    const service = availableServices.find(s => s.name === e.target.value);
                    if (service) handleServiceSelect(service);
                  }}
                  required
                >
                  <option value="">-- Selecione um serviço --</option>
                  {availableServices.map(service => (
                    <option key={service.name} value={service.name}>
                      {service.display_name} ({service.name})
                      {service.status && ` - ${service.status}`}
                    </option>
                  ))}
                </select>
              )}
              <small>Serviços descobertos em tempo real no servidor</small>
            </div>
          )}

          {selectedTemplate.requires_discovery && selectedTemplate.discovery_type === 'disks' && (
            <div className="form-group">
              <label>Disco: *</label>
              {loadingDisks ? (
                <div className="loading-discovery">🔄 Descobrindo discos...</div>
              ) : (
                <select
                  value={sensorConfig.disk_name}
                  onChange={(e) => {
                    const disk = availableDisks.find(d => d.name === e.target.value);
                    if (disk) handleDiskSelect(disk);
                  }}
                  required
                >
                  <option value="">-- Selecione um disco --</option>
                  {availableDisks.map(disk => (
                    <option key={disk.name} value={disk.name}>
                      {disk.display_name}
                      {disk.total_gb && ` - ${disk.total_gb}GB (${disk.percent_used}% usado)`}
                    </option>
                  ))}
                </select>
              )}
              <small>Discos descobertos em tempo real no servidor</small>
            </div>
          )}

          {/* Name */}
          <div className="form-group">
            <label>Nome do Sensor: *</label>
            <input
              type="text"
              value={sensorConfig.name}
              onChange={(e) => setSensorConfig({...sensorConfig, name: e.target.value})}
              placeholder={`Ex: ${selectedTemplate.default_name || selectedTemplate.name}`}
              required
            />
            <small>Nome que aparecerá no dashboard</small>
          </div>

          {/* Thresholds */}
          <div className="form-row">
            <div className="form-group">
              <label>⚠️ Limite de Aviso:</label>
              <input
                type="number"
                value={sensorConfig.threshold_warning}
                onChange={(e) => setSensorConfig({...sensorConfig, threshold_warning: e.target.value})}
                min="0"
                max="100"
              />
              <small>{selectedTemplate.thresholds.unit}</small>
            </div>

            <div className="form-group">
              <label>🔥 Limite Crítico:</label>
              <input
                type="number"
                value={sensorConfig.threshold_critical}
                onChange={(e) => setSensorConfig({...sensorConfig, threshold_critical: e.target.value})}
                min="0"
                max="100"
              />
              <small>{selectedTemplate.thresholds.unit}</small>
            </div>
          </div>

          {/* Actions */}
          <div className="modal-actions">
            <button className="btn-cancel" onClick={onClose}>
              Cancelar
            </button>
            <button 
              className="btn-add" 
              onClick={handleAdd}
              disabled={
                !sensorConfig.name || 
                sensorConfig.name.trim() === ''
              }
              title={
                !sensorConfig.name || sensorConfig.name.trim() === '' 
                  ? 'Preencha o nome do sensor' 
                  : 'Adicionar sensor'
              }
            >
              ✓ Adicionar Sensor
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-add-sensor" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        {/* Progress Indicator */}
        <div className="progress-steps">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
            <div className="step-number">1</div>
            <div className="step-label">Categoria</div>
          </div>
          <div className="progress-line"></div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
            <div className="step-number">2</div>
            <div className="step-label">Template</div>
          </div>
          <div className="progress-line"></div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
            <div className="step-number">3</div>
            <div className="step-label">Configurar</div>
          </div>
        </div>

        {/* Content */}
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}
      </div>
    </div>
  );
}

export default AddSensorModal;
