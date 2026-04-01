# 🎯 INSTRUÇÕES FINAIS - Execute Manualmente

## Situação Atual

Há uma probe rodando em outro diretório que está poluindo os logs:
```
C:\Users\user\OneDrive - EmpresaXPTO Ltda\Desktop\Coruja Monitor\probe\
```

Esta probe está tentando conectar no IP antigo (192.168.30.189) e precisa ser parada.

---

## ✅ PASSO A PASSO (Execute Agora)

### 1. Pare a Probe Antiga

Encontre o terminal/janela onde a probe está rodando e pressione `Ctrl+C` para pará-la.

Ou execute este comando para matar todos os processos Python:

```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### 2. Feche os Incidentes Resolvidos

Abra um novo terminal PowerShell neste diretório e execute:

```powershell
docker-compose exec api python fechar_incidentes_resolvidos.py
```

**Saída esperada:**
```
📋 Encontrados X incidentes ativos
✅ Fechando incidente Y:
   Sensor: PING
   Servidor: DESKTOP-P9VGN04
   Status atual: ok
   ✅ Incidente fechado!
```

### 3. Reinicie o Worker

```powershell
docker-compose restart worker
```

### 4. Reinicie a API

```powershell
docker-compose restart api
```

### 5. Aguarde os Serviços Iniciarem

```powershell
Start-Sleep -Seconds 10
```

### 6. Inicie a Probe Correta

Execute a probe DESTE diretório (não do OneDrive):

```powershell
.\iniciar_probe.bat
```

---

## 📊 Validação

Após executar todos os passos:

### 1. Verifique a Interface Web

- Acesse: http://192.168.0.41:3000
- Dashboard deve mostrar: "✅ 0 Incidentes Abertos"
- Incidente de PING deve estar "Resolvido"

### 2. Verifique o NOC

- Acesse: Modo NOC
- Servidor DESKTOP-P9VGN04 deve estar visível
- Status: OK (verde)
- IP: 192.168.0.41

### 3. Verifique os Logs da Probe

No terminal onde a probe está rodando, você deve ver:

```
✅ Sent 372 metrics successfully
📡 Heartbeat sent successfully
```

E NÃO deve ver:
```
❌ Error sending metrics
❌ Error sending heartbeat
```

### 4. Verifique o IP de Conexão

Nos logs da probe, confirme que está conectando em:
```
http://192.168.0.41:8000
```

E NÃO em:
```
http://192.168.30.189:8000
```

---

## 🔍 Diagnóstico de Problemas

### Problema: Probe ainda conecta no IP antigo

**Causa**: Probe errada rodando (do OneDrive)

**Solução**:
1. Mate TODOS os processos Python: `Get-Process python | Stop-Process -Force`
2. Navegue para: `C:\Users\user\Coruja Monitor`
3. Execute: `.\iniciar_probe.bat`

### Problema: Incidente não fecha

**Causa**: Script não executou ou sensor ainda com problema

**Solução**:
1. Verifique se sensor PING está OK na interface
2. Execute novamente: `docker-compose exec api python fechar_incidentes_resolvidos.py`
3. Aguarde 60 segundos para worker processar

### Problema: Servidor não aparece no NOC

**Causa**: API não reiniciou ou servidor inativo

**Solução**:
1. Reinicie API: `docker-compose restart api`
2. Verifique se servidor está ativo no banco
3. Aguarde 10 segundos e recarregue a página

---

## 🎓 O Que Foi Corrigido

### 1. Auto-Resolução de Incidentes Reconhecidos
- Worker agora fecha incidentes com status 'open' OU 'acknowledged'
- Verifica a cada 60 segundos
- Adiciona nota automática de resolução

### 2. NOC Mostra Todos os Servidores
- Não depende mais de ter incidentes ativos
- Calcula disponibilidade real (últimas 24h)
- Status baseado em múltiplas fontes

### 3. Atualização Automática de IP
- Probe detecta IP local e público
- Envia nos metadados das métricas
- API atualiza automaticamente quando muda

### 4. Script Manual de Correção
- Fecha incidentes já resolvidos
- Útil para correções pontuais
- Verifica última métrica antes de fechar

---

## 📁 Arquivos Importantes

### Configuração da Probe
```
C:\Users\user\Coruja Monitor\probe\probe_config.json
```

Deve conter:
```json
{
  "api_url": "http://192.168.0.41:8000",
  ...
}
```

### Script de Inicialização
```
C:\Users\user\Coruja Monitor\iniciar_probe.bat
```

### Script de Correção
```
C:\Users\user\Coruja Monitor\api\fechar_incidentes_resolvidos.py
```

---

## 🚀 Teste Final

Após tudo funcionando, faça um teste completo:

1. **Crie um incidente de teste**:
   - Altere threshold de CPU para 1%
   - Aguarde incidente ser criado
   - Reconheça o incidente

2. **Volte o threshold ao normal**:
   - Altere threshold de CPU para 90%
   - Aguarde até 60 segundos

3. **Valide auto-resolução**:
   - Incidente deve fechar automaticamente
   - Status deve mudar para "Resolvido"
   - Nota: "Auto-resolvido: sensor voltou ao normal"

---

## 📞 Resumo dos Comandos

Execute na ordem:

```powershell
# 1. Parar probe antiga
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Fechar incidentes
docker-compose exec api python fechar_incidentes_resolvidos.py

# 3. Reiniciar worker
docker-compose restart worker

# 4. Reiniciar API
docker-compose restart api

# 5. Aguardar
Start-Sleep -Seconds 10

# 6. Iniciar probe correta
.\iniciar_probe.bat
```

---

**Status**: Aguardando execução manual dos comandos

**Próximo Passo**: Execute os comandos acima na ordem
