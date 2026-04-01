# Solução: Sensores Mostrando "Desconhecido"

## 🔍 Problema Identificado

**Sintoma**: Todos os 28 sensores aparecem na lista, mas mostram status "Desconhecido" (28 Desconhecido, 0 OK, 0 Aviso, 0 Crítico).

## 📊 Diagnóstico

### Dados no Banco
```
Total de métricas: 19.763
Métricas últimas 24h: 9.087
Métricas mais recentes:
  - Sensor 66 (Disco C): 97.0% - CRITICAL (13:12:09) [TESTE]
  - Sensor 64 (CPU): 96.0% - CRITICAL (12:56:26) [TESTE]
  - Sensor 65 (Memória): 96.0% - CRITICAL (12:37:51) [TESTE]
  - Sensor 69 (Network OUT): 320166.0 - OK (10:55:47)
  - Sensor 68 (Network IN): 20766025.0 - OK (10:55:47)
```

### Causa Raiz
**A probe não está rodando!**

As últimas métricas reais (não simuladas) são de 10:55:47 (mais de 2 horas atrás). A probe precisa estar rodando continuamente para coletar métricas a cada 60 segundos.

---

## ✅ Solução

### 1. Iniciar a Probe

Execute o script criado:
```bash
iniciar_probe.bat
```

Ou manualmente:
```bash
cd "C:\Users\user\OneDrive - EmpresaXPTO Ltda\Desktop\Coruja Monitor\probe"
python probe_core.py
```

### 2. Verificar Coleta

A probe deve mostrar no console:
```
✓ Conectado à API: http://localhost:8000
✓ Probe autenticada: Quirino-Matriz
✓ Coletando métricas a cada 60 segundos...

[2026-02-20 10:55:47] Coletando métricas do servidor DESKTOP-P9VGN04...
  ✓ CPU: 15.2%
  ✓ Memória: 45.8%
  ✓ Disco C: 67.3%
  ✓ Docker: 21 containers
  ...
```

### 3. Aguardar Atualização

Após 1-2 minutos, os sensores devem mudar de "Desconhecido" para seus status reais (OK, Aviso, Crítico).

---

## 🔧 Configuração da Probe

### Arquivo: probe_config.json
```json
{
  "api_url": "http://localhost:8000",
  "probe_token": "W_YxHARNTlE3G8bxoXhWt0FknTPysGnKFX_visaP_G4",
  "collection_interval": 60,
  "log_level": "INFO"
}
```

### Localização
```
C:\Users\user\OneDrive - EmpresaXPTO Ltda\Desktop\Coruja Monitor\probe\
```

---

## 🚀 Manter Probe Rodando

### Opção 1: Janela do CMD Aberta
- Execute `iniciar_probe.bat`
- Deixe a janela aberta
- Minimize (não feche!)

### Opção 2: Tarefa Agendada (Recomendado)
```batch
# Criar tarefa que inicia com Windows
schtasks /create /tn "Coruja Probe" /tr "C:\...\probe\probe_core.py" /sc onstart /ru SYSTEM
```

### Opção 3: Serviço Windows (Produção)
- Usar NSSM (Non-Sucking Service Manager)
- Instalar probe como serviço
- Inicia automaticamente com Windows

---

## 📈 Comportamento Esperado

### Após Iniciar Probe

**Imediatamente**:
- Probe conecta à API
- Envia heartbeat
- Inicia coleta de métricas

**Após 1 minuto**:
- Primeira coleta completa
- Métricas enviadas para API
- Sensores mudam de "Desconhecido" para status real

**Após 2-3 minutos**:
- Dashboard atualizado
- Contadores corretos (25 OK, 0 Aviso, 3 Crítico)
- NOC mostra disponibilidade real

---

## 🔍 Troubleshooting

### Probe não conecta?
```bash
# Verificar se API está rodando
curl http://localhost:8000/health

# Verificar token
# Token deve estar em probe_config.json E no banco de dados
```

### Métricas não aparecem?
```bash
# Verificar logs da probe
dir C:\...\probe\logs\

# Verificar logs da API
docker logs coruja-api --tail 50

# Verificar se métricas estão chegando
docker exec coruja-api python -c "from database import SessionLocal; from models import Metric; from datetime import datetime, timedelta; db = SessionLocal(); print(db.query(Metric).filter(Metric.timestamp >= datetime.utcnow() - timedelta(minutes=5)).count()); db.close()"
```

### Sensores continuam "Desconhecido"?
1. Verificar se probe está rodando
2. Aguardar 2-3 minutos
3. Fazer Ctrl+Shift+R no navegador
4. Verificar console do navegador (F12)

---

## 📝 Status Atual

### ✅ Funcionando
- Dashboard mostra 1 servidor, 28 sensores
- NOC mostra empresa TENSO
- Sensores aparecem na lista
- Empresas mostram probes

### ⚠️ Pendente
- **Iniciar probe** para coletar métricas
- Aguardar sensores mudarem de "Desconhecido" para status real

---

## 🎯 Próximos Passos

1. **Execute `iniciar_probe.bat`** agora
2. Aguarde 2-3 minutos
3. Recarregue o navegador (Ctrl+Shift+R)
4. Verifique se sensores mostram status correto
5. Opcional: Configure probe como serviço Windows

---

## 💡 Dica Importante

**A probe precisa estar SEMPRE rodando** para coletar métricas continuamente. Se você fechar a janela do CMD, a coleta para e os sensores voltam para "Desconhecido" após alguns minutos.

Para produção, configure a probe como serviço Windows para iniciar automaticamente.

---

## 📞 Verificação Rápida

Execute este comando para ver se há métricas recentes:
```bash
docker exec coruja-api python -c "from database import SessionLocal; from models import Metric; from datetime import datetime, timedelta; db = SessionLocal(); recent = db.query(Metric).filter(Metric.timestamp >= datetime.utcnow() - timedelta(minutes=5)).count(); print(f'Métricas últimos 5 min: {recent}'); db.close()"
```

Se retornar 0, a probe não está rodando.
Se retornar > 0, a probe está coletando!
