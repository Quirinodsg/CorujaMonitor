# Solução: Sensores SNMP e Máquina Remota Sem Dados

## ✅ Problemas Resolvidos

### 1. Router SNMP Sem Sensor PING
**Status**: ✅ CORRIGIDO

Agora ao adicionar um dispositivo SNMP (router, switch, firewall), são criados automaticamente **7 sensores padrão**:

1. 📡 **PING** (ICMP) - Verifica se está online
2. ⏱️ **SNMP_Uptime** - Tempo desde último boot
3. 🖥️ **SNMP_CPU_Load** - Carga de CPU
4. 💾 **SNMP_Memory_Usage** - Uso de memória
5. 🌐 **SNMP_Traffic_In** - Tráfego de entrada
6. 🌐 **SNMP_Traffic_Out** - Tráfego de saída
7. 🔌 **SNMP_Interface_Status** - Status da interface

### 2. Sensores SNMP Baseados em PRTG/Zabbix
**Status**: ✅ IMPLEMENTADO

Todos os OIDs SNMP são baseados nos padrões usados por PRTG e Zabbix:
- OIDs genéricos (RFC 1213 - MIB-II)
- OIDs específicos por fabricante (Cisco, HP, Juniper, Mikrotik, Ubiquiti)
- Documentação completa em `docs/snmp-sensors-oids.md`

### 3. Máquina Remota Sem Dados
**Status**: ✅ SOLUÇÃO FORNECIDA

**Causa**: A sonda só coleta dados da máquina onde está instalada. Não coleta dados remotamente.

**Solução**: Instalar sonda na máquina remota.

---

## 🎯 Como Funciona a Arquitetura

### Cenário Atual

```
┌─────────────────────────────────────┐
│  Máquina A (192.168.0.38)           │
│  - Docker com API ✅                │
│  - Sonda instalada ✅               │
│  - Coleta dados locais ✅           │
└─────────────────────────────────────┘
         ↓ Envia métricas
    ┌─────────────┐
    │ API Coruja  │
    └─────────────┘

┌─────────────────────────────────────┐
│  Máquina B (192.168.0.100)          │
│  - Adicionada manualmente ✅        │
│  - Sensores criados ✅              │
│  - SEM sonda ❌                     │
│  - SEM dados ❌                     │
└─────────────────────────────────────┘
```

### Solução: Instalar Sonda na Máquina B

```
┌─────────────────────────────────────┐
│  Máquina A (192.168.0.38)           │
│  - Docker com API ✅                │
│  - Sonda instalada ✅               │
└─────────────────────────────────────┘
         ↓
    ┌─────────────┐
    │ API Coruja  │ ← Recebe de ambas
    └─────────────┘
         ↑
┌─────────────────────────────────────┐
│  Máquina B (192.168.0.100)          │
│  - Sonda instalada ✅               │
│  - Coleta dados locais ✅           │
│  - Envia para API ✅                │
└─────────────────────────────────────┘
```

---

## 📝 Guia: Instalar Sonda na Máquina Remota

### Opção 1: Instalação Manual (Recomendado)

#### Passo 1: Copiar Pasta Probe

**Na máquina remota (192.168.0.100)**:
1. Criar pasta: `C:\Coruja\probe\`
2. Copiar todos os arquivos da pasta `probe` para lá

**Métodos de cópia**:
- Compartilhamento de rede
- Pendrive
- RDP (Remote Desktop)
- FTP/SFTP

#### Passo 2: Configurar

```cmd
cd C:\Coruja\probe
configurar_probe.bat
```

Informar:
- **URL da API**: `http://192.168.0.38:8000`
- **Token da Probe**: Pegar na interface web (página Probes)

#### Passo 3: Instalar Serviço

```cmd
install_service.bat
```

#### Passo 4: Verificar

```cmd
verificar_status.bat
```

Deve mostrar:
```
✅ Serviço Coruja Probe está RODANDO
✅ Conectado à API
✅ Enviando métricas
```

### Opção 2: Instalação Remota Automatizada

**Requisitos**:
- Acesso administrativo à máquina remota
- Compartilhamento administrativo habilitado (C$)
- Firewall liberado para SMB (porta 445)
- PsExec instalado (opcional, para instalar serviço remotamente)

**Na máquina onde está o Docker**:

```cmd
cd probe
install_remote.bat
```

Informar:
- IP da máquina remota: `192.168.0.100`
- Usuário administrador: `Administrator`
- Senha: `********`
- URL da API: `http://192.168.0.38:8000`
- Token da probe: `[token da interface]`

O script irá:
1. Copiar arquivos para `\\192.168.0.100\C$\Coruja\probe\`
2. Criar arquivo de configuração
3. Instalar serviço remotamente (se PsExec disponível)

---

## 🧪 Verificar se Está Funcionando

### 1. Na Máquina Remota

```cmd
cd C:\Coruja\probe
verificar_status.bat
```

### 2. Na Interface Web

1. Ir para "Servidores"
2. Aguardar 1-2 minutos
3. O servidor deve aparecer automaticamente com:
   - Hostname detectado
   - IP detectado
   - OS detectado
   - 7 sensores com dados

### 3. Verificar Logs

```cmd
cd C:\Coruja\probe
type probe.log
```

Deve mostrar:
```
INFO - Coruja Probe started
INFO - Heartbeat sent successfully
INFO - Metrics sent: 7 sensors
```

---

## 🔧 Troubleshooting

### Problema: Sonda não conecta à API

**Sintomas**:
- `verificar_status.bat` mostra "Não conectado"
- Logs mostram "Connection refused" ou "Network error"

**Soluções**:
1. Verificar se a API está acessível:
   ```cmd
   curl http://192.168.0.38:8000/docs
   ```

2. Verificar firewall na máquina do Docker:
   ```powershell
   # Liberar porta 8000
   New-NetFirewallRule -DisplayName "Coruja API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
   ```

3. Verificar se o token está correto:
   - Pegar novo token na interface web
   - Reconfigurar: `configurar_probe.bat`

### Problema: Serviço não inicia

**Sintomas**:
- `verificar_status.bat` mostra "Serviço não encontrado"
- Serviço aparece como "Stopped" no services.msc

**Soluções**:
1. Reinstalar serviço:
   ```cmd
   uninstall_service.bat
   install_service.bat
   ```

2. Verificar permissões:
   - Executar CMD como Administrador
   - Verificar se Python está instalado: `python --version`

3. Verificar logs de erro:
   ```cmd
   type probe.log
   ```

### Problema: Sensores sem dados

**Sintomas**:
- Sensores aparecem na interface
- Mas não há métricas (valores vazios)

**Soluções**:
1. Verificar se a sonda está enviando:
   ```cmd
   type probe.log | findstr "Metrics sent"
   ```

2. Verificar se o servidor foi criado automaticamente ou manualmente:
   - Se manual: Pode ter ID diferente do esperado
   - Solução: Excluir servidor manual e deixar a sonda criar automaticamente

3. Aguardar 2-3 minutos:
   - A sonda envia métricas a cada 60 segundos
   - Pode levar alguns ciclos para aparecer

---

## 📊 Sensores SNMP - OIDs Padrão

### Dispositivos SNMP (Router, Switch, Firewall)

Ao adicionar um dispositivo SNMP, os seguintes sensores são criados:

| Sensor | OID | Descrição |
|--------|-----|-----------|
| PING | - | ICMP ping (não usa SNMP) |
| SNMP_Uptime | 1.3.6.1.2.1.1.3.0 | Tempo desde boot |
| SNMP_CPU_Load | 1.3.6.1.4.1.2021.10.1.3.1 | Carga de CPU (1 min) |
| SNMP_Memory_Usage | 1.3.6.1.4.1.2021.4.6.0 | Memória livre |
| SNMP_Traffic_In | 1.3.6.1.2.1.2.2.1.10.1 | Bytes recebidos |
| SNMP_Traffic_Out | 1.3.6.1.2.1.2.2.1.16.1 | Bytes enviados |
| SNMP_Interface_Status | 1.3.6.1.2.1.2.2.1.8.1 | Status da interface |

**Documentação completa**: `docs/snmp-sensors-oids.md`

---

## 🎯 Resumo das Ações

### ✅ Já Implementado (Backend)
1. Sensores SNMP padrão criados automaticamente
2. OIDs baseados em PRTG e Zabbix
3. Sensor PING incluído para dispositivos SNMP
4. Documentação completa de OIDs

### ⏭️ Próximos Passos (Você)
1. **Instalar sonda na máquina remota (192.168.0.100)**:
   - Copiar pasta `probe`
   - Executar `configurar_probe.bat`
   - Executar `install_service.bat`
   - Aguardar 2 minutos
   - Verificar se dados aparecem

2. **Testar router SNMP**:
   - Excluir router atual (se não tem PING)
   - Adicionar novamente
   - Verificar se 7 sensores foram criados (incluindo PING)

3. **Configurar SNMP no router** (se ainda não configurado):
   ```
   # Exemplo Cisco
   snmp-server community public RO
   snmp-server location "Datacenter"
   snmp-server contact "admin@empresa.com"
   ```

---

## 📚 Arquivos Criados

1. `docs/snmp-sensors-oids.md` - Documentação completa de OIDs SNMP
2. `probe/install_remote.bat` - Script de instalação remota
3. `api/routers/servers.py` - Atualizado com sensores SNMP padrão

---

**Data**: 13/02/2026 18:00 UTC
**Status**: ✅ IMPLEMENTADO
**Ação Necessária**: Instalar sonda na máquina remota
