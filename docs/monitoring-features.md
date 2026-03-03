# Funcionalidades de Monitoramento Avançado

## Visão Geral
Sistema expandido para monitorar não apenas servidores Windows, mas também dispositivos de rede (switches, roteadores, firewalls) usando WMI ou SNMP.

## 1. Tipos de Dispositivos Suportados

### Servidores
- 🖥️ **Servidor** - Servidores Windows/Linux
- Protocolo: WMI (Windows) ou SNMP

### Dispositivos de Rede
- 🔀 **Switch** - Switches gerenciáveis
- 📡 **Roteador** - Roteadores
- 🔥 **Firewall** - Firewalls e appliances de segurança
- Protocolo: SNMP (v1, v2c, v3)

### Outros Dispositivos
- 🖨️ **Impressora** - Impressoras de rede
- 💾 **Storage** - Storages e NAS
- 🔋 **Nobreak** - UPS e nobreaks
- 📦 **Outro** - Qualquer dispositivo com SNMP

## 2. Protocolos de Monitoramento

### WMI (Windows Management Instrumentation)
- **Uso:** Servidores Windows
- **Porta:** 135 (RPC) + portas dinâmicas
- **Requisitos:**
  - Firewall deve permitir WMI/RPC
  - Credenciais de administrador
  - Serviço WMI ativo no servidor

**Sensores WMI:**
- CPU Usage
- Memory Usage
- Disk Usage
- Network Traffic
- Windows Services
- Hyper-V VMs
- System Uptime

### SNMP (Simple Network Management Protocol)
- **Uso:** Dispositivos de rede, impressoras, storages
- **Porta:** 161 (padrão)
- **Versões:**
  - **v1:** Básico, sem segurança
  - **v2c:** Recomendado, melhor performance
  - **v3:** Mais seguro, com autenticação e criptografia

**Configuração SNMP:**
```
Community String: public (leitura) / private (escrita)
Porta: 161
Versão: v2c (recomendado)
```

**Sensores SNMP:**
- Interface Status (up/down)
- Interface Traffic (in/out)
- CPU Usage
- Memory Usage
- Temperature
- Fan Speed
- Power Supply Status
- Custom OIDs

## 3. Classificação de Ambientes

### 🔴 Produção (Production)
- **Monitoramento:** 24 horas por dia, 7 dias por semana
- **Notificações:** Imediatas
- **Ligações:** SIM - Sistema liga em caso de sensor crítico
- **Uso:** Servidores e dispositivos críticos para o negócio

**Exemplo:**
- Servidor de banco de dados principal
- Firewall de borda
- Switch core do datacenter
- Servidor de aplicação em produção

### 🟡 Homologação (Staging)
- **Monitoramento:** Horário comercial (08:00 - 18:00)
- **Notificações:** Apenas em horário comercial
- **Ligações:** NÃO
- **Uso:** Ambiente de testes e homologação

**Exemplo:**
- Servidor de testes
- Ambiente de QA
- Servidor de staging

### 🟢 Desenvolvimento (Development)
- **Monitoramento:** Horário comercial (08:00 - 18:00)
- **Notificações:** Apenas em horário comercial
- **Ligações:** NÃO
- **Uso:** Ambiente de desenvolvimento

**Exemplo:**
- Servidor de desenvolvimento
- Máquinas de desenvolvedores
- Ambiente de sandbox

### ⚙️ Personalizado (Custom)
- **Monitoramento:** Horários definidos pelo usuário
- **Notificações:** Conforme horários configurados
- **Ligações:** Conforme configuração
- **Uso:** Casos específicos

**Exemplo:**
- Servidor de backup (monitorar apenas durante janela de backup)
- Servidor de relatórios (monitorar apenas em horário de geração)
- Dispositivo com manutenção programada

## 4. Integrações de Notificação

### 📞 Twilio (Ligações e SMS)
**Configuração:**
```json
{
  "enabled": true,
  "account_sid": "ACxxxxxxxxxxxxx",
  "auth_token": "your_auth_token",
  "from_number": "+5511999999999",
  "to_numbers": ["+5511888888888", "+5511777777777"]
}
```

**Quando liga:**
- Sensor crítico em ambiente de PRODUÇÃO
- Após 3 tentativas de notificação sem resposta
- Incidente não reconhecido em 5 minutos

### 💬 Microsoft Teams
**Configuração:**
```json
{
  "enabled": true,
  "webhook_url": "https://outlook.office.com/webhook/..."
}
```

**Mensagens enviadas:**
- Sensor crítico
- Sensor em aviso
- Sensor voltou ao normal
- Resumo diário de incidentes

### 📱 WhatsApp
**Configuração:**
```json
{
  "enabled": true,
  "api_key": "your_whatsapp_api_key",
  "phone_numbers": ["+5511999999999", "+5511888888888"]
}
```

**Mensagens enviadas:**
- Alertas críticos
- Resumo de incidentes
- Relatórios semanais

### 🤖 Telegram
**Configuração:**
```json
{
  "enabled": true,
  "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
  "chat_ids": ["-123456789", "-987654321"]
}
```

**Mensagens enviadas:**
- Alertas em tempo real
- Comandos interativos
- Status de servidores

## 5. Fluxo de Notificações

### Sensor OK → Warning
1. Notificação via Teams/Telegram
2. Registro no log de incidentes
3. Aguarda 5 minutos

### Sensor Warning → Critical
1. **Produção:**
   - Notificação imediata via todas as integrações
   - Aguarda 2 minutos
   - Se não reconhecido: Liga via Twilio
   - Continua ligando a cada 5 minutos até reconhecimento

2. **Homologação/Dev:**
   - Notificação via Teams/Telegram (apenas em horário comercial)
   - Sem ligações

3. **Custom:**
   - Conforme horários configurados

### Sensor Critical → OK
1. Notificação de resolução
2. Fecha incidente automaticamente
3. Registra tempo de downtime
4. Atualiza SLA

## 6. Exemplos de Uso

### Exemplo 1: Adicionar Switch Core
```
Tipo: Switch
Hostname: SWITCH-CORE-01
IP: 192.168.1.1
Protocolo: SNMP
Versão SNMP: v2c
Community: public
Porta: 161
Ambiente: Produção
```

**Sensores criados automaticamente:**
- Interface GigabitEthernet 1/0/1 (Status)
- Interface GigabitEthernet 1/0/1 (Traffic IN)
- Interface GigabitEthernet 1/0/1 (Traffic OUT)
- CPU Usage
- Memory Usage
- Temperature

### Exemplo 2: Adicionar Servidor de Backup
```
Tipo: Servidor
Hostname: BACKUP-SRV-01
IP: 192.168.1.50
Protocolo: WMI
Ambiente: Personalizado
Horário: 22:00 - 06:00 (apenas durante backup)
```

**Sensores criados:**
- CPU Usage
- Memory Usage
- Disk C: Usage
- Backup Service Status
- Network Traffic

### Exemplo 3: Adicionar Firewall
```
Tipo: Firewall
Hostname: FW-EDGE-01
IP: 192.168.1.254
Protocolo: SNMP
Versão SNMP: v3 (mais seguro)
Ambiente: Produção
```

**Sensores criados:**
- Interface WAN (Status)
- Interface LAN (Status)
- CPU Usage
- Memory Usage
- Active Connections
- Blocked Connections

## 7. Configuração no Frontend

### Adicionar Dispositivo
1. Vá para "🖥️ Servidores"
2. Clique em "+ Adicionar Servidor"
3. Preencha:
   - Probe responsável
   - Tipo de dispositivo
   - Nome/Hostname
   - Endereço IP
   - Protocolo (WMI ou SNMP)
   - Se SNMP: versão, community, porta
   - Ambiente (Produção/Homologação/Dev/Custom)
4. Clique em "Adicionar Dispositivo"

### Configurar Notificações
1. Vá para "🏢 Empresas"
2. Clique em "Editar" na empresa
3. Aba "Notificações"
4. Configure cada integração:
   - Twilio (ligações)
   - Teams (mensagens)
   - WhatsApp (mensagens)
   - Telegram (bot)
5. Teste cada integração
6. Salve as configurações

## 8. Boas Práticas

### Classificação de Ambientes
- ✅ Use "Produção" apenas para dispositivos críticos
- ✅ Configure ligações apenas para o necessário
- ✅ Use "Homologação" para ambientes de teste
- ✅ Use "Custom" para casos específicos

### Protocolos
- ✅ Use WMI para servidores Windows
- ✅ Use SNMP v2c para dispositivos de rede (melhor compatibilidade)
- ✅ Use SNMP v3 para ambientes que exigem segurança
- ✅ Mantenha community strings seguros (não use "public" em produção)

### Notificações
- ✅ Configure múltiplos canais de notificação
- ✅ Teste todas as integrações antes de colocar em produção
- ✅ Defina números de telefone de plantão para ligações
- ✅ Configure grupos no Teams/Telegram para diferentes equipes

### Monitoramento
- ✅ Ajuste thresholds conforme o dispositivo
- ✅ Monitore interfaces críticas em switches
- ✅ Configure alertas de temperatura em equipamentos
- ✅ Monitore uso de CPU/Memória em firewalls

## 9. Troubleshooting

### SNMP não funciona
```bash
# Testar SNMP do servidor
snmpwalk -v2c -c public 192.168.1.1

# Verificar se porta está aberta
Test-NetConnection -ComputerName 192.168.1.1 -Port 161

# Verificar community string
# Deve estar configurado no dispositivo
```

### WMI não funciona
```bash
# Testar WMI
Test-WmiConnection -ComputerName SERVER-01

# Verificar firewall
Get-NetFirewallRule -DisplayName "*WMI*"

# Verificar serviço WMI
Get-Service -Name Winmgmt
```

### Notificações não chegam
1. Verificar configuração em "Empresas"
2. Testar integração individualmente
3. Verificar logs da API
4. Verificar se ambiente está correto (Produção/Homologação)
5. Verificar horário (se Homologação/Dev, só notifica em horário comercial)

## 10. Próximos Passos

- [ ] Implementar coleta SNMP na probe
- [ ] Adicionar mais OIDs padrão para dispositivos comuns
- [ ] Implementar envio real de notificações (Twilio, Teams, etc.)
- [ ] Adicionar dashboard específico para dispositivos de rede
- [ ] Implementar auto-discovery de dispositivos SNMP
- [ ] Adicionar templates de sensores por tipo de dispositivo
