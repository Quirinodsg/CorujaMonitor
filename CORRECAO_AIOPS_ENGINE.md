# Correção: AIOps Engine Not Available

## Data: 18/02/2026

## Problema

Ao tentar usar as funcionalidades AIOps no frontend, o erro "AIOps Engine not available" era retornado pela API.

**Causa**: O módulo `aiops_engine.py` estava na pasta `ai-agent/` mas o container da API não tinha acesso a ele, causando falha no import.

## Solução Implementada

### Abordagem: Inline Engine

Em vez de tentar importar o módulo externo, implementei o `AIOpsEngine` diretamente dentro do arquivo `api/routers/aiops.py` através de uma função `get_aiops_engine()`.

### Mudanças Realizadas

**Arquivo**: `api/routers/aiops.py`

**Antes**:
```python
# Tentava importar de módulo externo
sys.path.append(os.path.join(os.path.dirname(__file__), '../../ai-agent'))
from aiops_engine import AIOpsEngine
```

**Depois**:
```python
# Define engine inline
def get_aiops_engine():
    """Get AIOps Engine instance"""
    class AIOpsEngine:
        def __init__(self):
            self.anomaly_threshold = 2.5
            self.correlation_window = 300
            self.min_samples_for_baseline = 20
        
        async def detect_anomalies(...):
            # Implementação completa
        
        async def correlate_events(...):
            # Implementação completa
        
        async def analyze_root_cause(...):
            # Implementação completa
        
        async def create_action_plan(...):
            # Implementação completa
    
    return AIOpsEngine()
```

### Funcionalidades Mantidas

Todas as funcionalidades do AIOps foram mantidas:

1. **Detecção de Anomalias**:
   - Análise estatística (Z-score)
   - Threshold de 2.5 desvios padrão
   - Cálculo de confiança
   - Recomendações por tipo de sensor

2. **Correlação de Eventos**:
   - Correlação temporal (janela de 5 minutos)
   - Agrupamento de incidentes
   - Identificação de padrões
   - Análise de servidores afetados

3. **Análise de Causa Raiz**:
   - Análise de sintomas
   - Reconstrução de timeline
   - Identificação de causa raiz por tipo
   - Fatores contribuintes

4. **Planos de Ação**:
   - Ações imediatas (1-5 min)
   - Ações de curto prazo (5-30 min)
   - Ações de longo prazo (horas/dias)
   - Comandos PowerShell prontos
   - Indicadores de automação e risco

### Vantagens da Solução

1. **Sem Dependências Externas**: Não precisa de módulos externos
2. **Portabilidade**: Funciona em qualquer ambiente
3. **Simplicidade**: Tudo em um único arquivo
4. **Manutenibilidade**: Fácil de debugar e modificar
5. **Performance**: Sem overhead de imports

### Desvantagens

1. **Código Duplicado**: Se precisar usar em outro lugar, terá duplicação
2. **Tamanho do Arquivo**: O arquivo `aiops.py` ficou maior
3. **Separação de Concerns**: Lógica de negócio misturada com API

## Testes Realizados

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/aiops/health
```

**Resultado**:
```json
{
  "status": "healthy",
  "engine": "AIOps Engine v1.0 (Inline)",
  "capabilities": [
    "anomaly_detection",
    "event_correlation",
    "root_cause_analysis",
    "action_planning"
  ]
}
```

### 2. Detecção de Anomalias
- ✅ Endpoint funcional
- ✅ Análise estatística funcionando
- ✅ Recomendações sendo geradas
- ✅ Frontend recebendo dados corretamente

### 3. Correlação de Eventos
- ✅ Agrupamento temporal funcionando
- ✅ Identificação de padrões
- ✅ Análise de servidores afetados

### 4. RCA e Planos de Ação
- ✅ Análise de causa raiz funcionando
- ✅ Timeline sendo gerada
- ✅ Planos de ação estruturados

## Melhorias Futuras

### Opção 1: Mover para Módulo Compartilhado
Criar um módulo Python compartilhado dentro do container:
```
api/
  lib/
    aiops_engine.py
  routers/
    aiops.py (importa de lib)
```

### Opção 2: Microserviço Separado
Criar um microserviço dedicado para AIOps:
```
aiops-service/
  main.py
  engine.py
  
api/
  routers/
    aiops.py (chama microserviço via HTTP)
```

### Opção 3: Biblioteca Python Instalável
Criar um pacote Python instalável:
```bash
pip install coruja-aiops
```

## Comandos Úteis

```bash
# Reiniciar API
docker-compose restart api

# Ver logs
docker logs coruja-api --tail 50

# Testar health
curl http://localhost:8000/api/v1/aiops/health

# Testar detecção de anomalias
curl -X POST http://localhost:8000/api/v1/aiops/anomaly-detection \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": 1, "lookback_hours": 24}'
```

## Conclusão

O problema foi resolvido implementando o AIOps Engine diretamente no arquivo da API. Todas as funcionalidades estão operacionais e o sistema está pronto para uso.

**Status**: ✅ CORRIGIDO E FUNCIONAL
**Versão**: 1.0.1
**Data**: 18/02/2026
