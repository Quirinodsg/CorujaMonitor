# Funcionalidade da IA no Coruja Monitor

## Visão Geral
A IA do Coruja Monitor analisa automaticamente sensores críticos para identificar causas raiz e sugerir soluções.

## Como Funciona

### 1. Detecção Automática
- Quando um sensor entra em estado CRITICAL
- Sistema cria automaticamente um Incidente
- IA é acionada para análise

### 2. Análise de Causa Raiz
A IA analisa:
- **Histórico de métricas** (últimas 24h)
- **Padrões de comportamento**
- **Correlação com outros sensores**
- **Eventos do sistema**

### 3. Identificação de Causas Comuns

#### CPU Alta
- Processos consumindo recursos
- Falta de recursos do sistema
- Malware ou vírus
- Aplicações mal otimizadas

#### Memória Alta
- Memory leak em aplicações
- Muitos processos rodando
- Cache excessivo
- Falta de RAM física

#### Disco Cheio
- Logs não rotacionados
- Arquivos temporários acumulados
- Backups antigos
- Crescimento de banco de dados

#### Serviço Offline
- Falha na aplicação
- Dependências não disponíveis
- Falta de recursos
- Erro de configuração

#### Ping Alto/Timeout
- Problemas de rede
- Firewall bloqueando
- Servidor sobrecarregado
- Rota de rede com problemas

### 4. Sugestões de Solução
Para cada causa identificada, a IA sugere:
- **Ações imediatas** (restart de serviço, limpeza de disco)
- **Ações preventivas** (aumentar recursos, otimizar configuração)
- **Comandos específicos** (scripts PowerShell/Bash)

### 5. Auto-Remediação (Opcional)
Para casos simples, a IA pode:
- Reiniciar serviços automaticamente
- Limpar arquivos temporários
- Liberar cache
- Executar scripts de correção

## Exemplo de Análise

```json
{
  "sensor": "cpu_usage",
  "status": "critical",
  "value": 98.5,
  "ai_analysis": {
    "root_cause": "Processo 'backup.exe' consumindo 85% da CPU",
    "confidence": 0.95,
    "evidence": [
      "CPU usage spike started at 02:00 AM",
      "Correlates with scheduled backup time",
      "Process 'backup.exe' PID 1234 using 85% CPU"
    ],
    "suggested_actions": [
      {
        "priority": "high",
        "action": "Reschedule backup to off-peak hours",
        "command": "schtasks /change /tn 'Backup' /st 22:00"
      },
      {
        "priority": "medium",
        "action": "Optimize backup process",
        "command": "backup.exe --low-priority --incremental"
      }
    ],
    "auto_remediation_available": false,
    "estimated_resolution_time": "5 minutes"
  }
}
```

## Integração com Interface

### No Card do Sensor
```
📊 CPU Usage: 98.5% 🔥 CRITICAL

🤖 Análise da IA:
Causa: Processo 'backup.exe' consumindo 85% da CPU
Confiança: 95%

💡 Sugestões:
1. Reagendar backup para horário de menor uso
2. Otimizar processo de backup

✅ Ação Automática Disponível: Não
⏱️ Tempo Estimado de Resolução: 5 minutos
```

### Notas do Técnico
```
📝 Nota do Técnico (João Silva - 12/02/2026 15:30)
Status: ✅ Verificado e Resolvido

"Reagendei o backup para 22:00. Também configurei o processo
para rodar com prioridade baixa. Monitorando por 24h."

Ações Tomadas:
- Alterado horário do backup
- Configurado prioridade baixa
- Adicionado monitoramento extra
```

## Implementação Técnica

### Backend (Python)
```python
# ai-agent/ai_engine.py
class AIEngine:
    def analyze_critical_sensor(self, sensor_id, metrics_history):
        # 1. Coletar dados históricos
        # 2. Identificar padrões anormais
        # 3. Correlacionar com outros sensores
        # 4. Buscar causas conhecidas
        # 5. Gerar sugestões
        # 6. Calcular confiança
        pass
    
    def suggest_remediation(self, root_cause):
        # Retorna ações sugeridas baseadas na causa
        pass
```

### Frontend (React)
```javascript
// Componente SensorDetails
<div className="ai-analysis">
  <h4>🤖 Análise da IA</h4>
  <div className="root-cause">
    <strong>Causa Raiz:</strong> {analysis.root_cause}
    <span className="confidence">{analysis.confidence * 100}%</span>
  </div>
  <div className="suggestions">
    {analysis.suggested_actions.map(action => (
      <ActionCard action={action} />
    ))}
  </div>
</div>

<div className="technician-notes">
  <h4>📝 Notas do Técnico</h4>
  <textarea placeholder="Adicione suas observações..." />
  <select>
    <option>Em Análise</option>
    <option>Verificado</option>
    <option>Resolvido</option>
  </select>
  <button>Salvar Nota</button>
</div>
```

## Próximos Passos

1. ✅ Criar modelo de dados para análises da IA
2. ✅ Implementar engine de análise básico
3. ✅ Adicionar interface para notas técnicas
4. ⏳ Treinar IA com casos reais
5. ⏳ Implementar auto-remediação
6. ⏳ Dashboard de efetividade da IA
