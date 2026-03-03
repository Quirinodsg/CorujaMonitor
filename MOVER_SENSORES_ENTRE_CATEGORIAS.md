# ✅ Mover Sensores Entre Categorias - IMPLEMENTADO

## 🎯 Status: CONCLUÍDO

Data: 19/02/2026 14:35

## 📋 Funcionalidade Implementada

### Problema Resolvido
- Sensores de rede não apareciam na categoria "Rede"
- Sensores Docker não apareciam na categoria "Docker"
- Sensores classificados incorretamente

### Solução
Botão "Mover para..." que permite reclassificar sensores entre categorias

## 🔧 Implementação

### Backend (API)

#### api/routers/sensors.py

**1. Adicionado campo `sensor_type` ao SensorUpdate:**
```python
class SensorUpdate(BaseModel):
    name: Optional[str] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    sensor_type: Optional[str] = None  # ✅ NOVO: Para mover entre categorias
```

**2. Atualização do sensor_type no endpoint PUT:**
```python
# Update sensor_type (for moving between categories)
if sensor_update.sensor_type is not None:
    sensor.sensor_type = sensor_update.sensor_type
```

### Frontend (Servers.js)

**1. Novos Estados:**
```javascript
const [showMoveSensorModal, setShowMoveSensorModal] = useState(false);
const [movingSensor, setMovingSensor] = useState(null);
const [targetCategory, setTargetCategory] = useState('');
```

**2. Funções Implementadas:**

