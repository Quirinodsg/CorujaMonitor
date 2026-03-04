# Guia de Reinstalação Limpa - Coruja Monitor

## 🎯 Objetivo

Excluir servidor atual e reinstalar do zero com configuração correta.

---

## 🚀 Passo a Passo

### 1. Execute o Script de Reinstalação

```bash
reinstalar_servidor_completo.bat
```

**O que o script faz:**
1. ✓ Exclui servidor DESKTOP-P9VGN04 e todos os sensores
2. ✓ Limpa métricas antigas (19.763 métricas)
3. ✓ Limpa incidentes de teste
4. ✓ Recria servidor com 7 sensores padrão
5. ✓ Configura probe_config.json corretamente

---

### 2. Inicie a Probe

```bash
iniciar_probe.bat
```

**Deixe a janela aberta!** A probe precisa rodar continuamente.

---

### 3. Aguarde 2-3 Minutos

A probe vai:
- Conectar à API
- Coletar métricas do sistema
- Enviar para o backend
- Sensores mudarão de "Desconhecido" para status real

---

### 4. Verifique no Navegador

1. Acesse http://localhost:3000
2. Faça Ctrl+Shift+R (hard refresh)
3. Vá em "Servidores"
4. Deve mostrar:
   - ✓ 1 servidor (DESKTOP-P9VGN04)
   - ✓ 7 sensores (PING, CPU, Memória, Disco C, Uptime, Network IN, Network OUT)
   - ✓ Status real (não "Desconhecido")

---

## 📊 Resultado Esperado

### Dashboard
```
🖥️ 1 Servidor
📊 7 Sensores
⚠️ 0 Incidentes Abertos
🔥 0 Críticos
```

### Status de Saúde
```
✅ 7 Saudável (ou conforme uso real)
⚠️ 0 Aviso
🔥 0 Crítico
✓ 0 Verificado pela TI
❓ 0 Desconhecido
```

### Sensores
```
Sistema (7):
  - PING
  - CPU
  - Memória
  - Disco C
  - Uptime
  - Network IN
  - Network OUT
```

---

## 🔧 Adicionar Sensores Docker (Opcional)

Após a instalação básica funcionar, você pode adicionar sensores Docker:

1. Vá em "Servidores"
2. Clique no servidor
3. Clique em "+ Adicionar Sensor"
4. Escolha template "Docker"
5. Configure e salve

---

## ⚠️ Importante

### Probe Precisa Rodar Continuamente

A probe coleta métricas a cada 60 segundos. Se você fechar a janela:
- ❌ Coleta para
- ❌ Sensores voltam para "Desconhecido"
- ❌ Dashboard não atualiza

### Solução: Deixar Rodando

**Opção 1**: Deixe a janela do CMD minimizada (não feche!)

**Opção 2**: Configure como serviço Windows (produção)
```bash
# Usar NSSM ou Task Scheduler
schtasks /create /tn "Coruja Probe" /tr "python C:\...\probe\probe_core.py" /sc onstart
```

---

## 🔍 Verificação Rápida

### Probe está rodando?
```bash
# Deve mostrar processo Python
tasklist | findstr python
```

### Métricas estão chegando?
```bash
# Deve retornar > 0 após 2 minutos
docker exec coruja-api python -c "from database import SessionLocal; from models import Metric; from datetime import datetime, timedelta; db = SessionLocal(); print(db.query(Metric).filter(Metric.timestamp >= datetime.utcnow() - timedelta(minutes=5)).count()); db.close()"
```

### Sensores estão OK?
```bash
# Acesse o navegador
http://localhost:3000
# Vá em Servidores > DESKTOP-P9VGN04
# Sensores devem mostrar valores reais
```

---

## 🎉 Sucesso!

Após seguir estes passos, você terá:

✅ Servidor limpo e funcionando
✅ 7 sensores padrão coletando métricas
✅ Dashboard atualizado em tempo real
✅ NOC mostrando disponibilidade correta
✅ Sistema pronto para adicionar mais sensores

---

## 📝 Próximos Passos (Opcional)

1. **Adicionar Sensores Docker**
   - Monitorar containers
   - Métricas por container
   - Status de containers

2. **Adicionar Sensores de Serviços**
   - Monitorar serviços Windows
   - Alertas de serviços parados
   - Auto-restart de serviços

3. **Configurar Notificações**
   - Email
   - Webhook
   - Integração com Service Desk

4. **Configurar Janelas de Manutenção**
   - Silenciar alertas durante manutenção
   - Agendar manutenções programadas

---

## 🆘 Troubleshooting

### Script falha?
- Verifique se Docker está rodando
- Verifique se API está acessível: `curl http://localhost:8000/health`

### Probe não conecta?
- Verifique probe_config.json
- Verifique token no banco de dados
- Verifique logs: `dir C:\...\probe\logs\`

### Sensores continuam "Desconhecido"?
- Verifique se probe está rodando
- Aguarde 2-3 minutos
- Faça Ctrl+Shift+R no navegador
- Verifique console do navegador (F12)

---

**Boa sorte com a reinstalação! 🚀**
