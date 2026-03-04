# Guia de Atualização da Sonda - Versão Agentless

## ❓ Preciso Atualizar?

**SIM!** A sonda antiga só coleta dados da máquina local. A nova versão coleta de múltiplos servidores remotos (estilo PRTG).

## 📍 Onde Está a Sonda?

A sonda está instalada na máquina onde você executou `install_service.bat`.

**Verificar**:
```cmd
# Abrir CMD como Administrador
sc query "Coruja Probe"
```

Se mostrar "RUNNING", a sonda está instalada nesta máquina.

---

## 🚀 Opção 1: Atualização Automática (Recomendado)

### Passo 1: Copiar Arquivos Novos

**Na máquina onde a sonda está instalada**:

1. Copiar a pasta `probe` atualizada para substituir a antiga
2. Ou copiar apenas o arquivo `probe_core.py` atualizado

**Exemplo**:
```cmd
# Se a sonda está em C:\Coruja\probe\
# Copiar probe_core.py novo para lá
copy "C:\Users\seu_usuario\Coruja Monitor\probe\probe_core.py" "C:\Coruja\probe\probe_core.py"
```

### Passo 2: Executar Script de Atualização

```cmd
cd C:\Coruja\probe
atualizar_sonda.bat
```

O script irá:
1. ✅ Parar o serviço
2. ✅ Atualizar arquivos
3. ✅ Reinstalar serviço
4. ✅ Iniciar serviço

### Passo 3: Verificar

```cmd
verificar_status.bat
```

Deve mostrar:
```
✅ Serviço Coruja Probe está RODANDO
✅ Conectado à API
✅ Versão: Agentless (PRTG-style)
```

---

## 🔧 Opção 2: Atualização Manual

### Passo 1: Parar Serviço

```cmd
cd C:\Coruja\probe
uninstall_service.bat
```

### Passo 2: Substituir Arquivos

Copiar os arquivos novos:
- `probe_core.py` (principal - com coleta remota)
- `collectors/wmi_remote_collector.py` (novo)
- `atualizar_sonda.bat` (novo)

### Passo 3: Reinstalar Serviço

```cmd
install_service.bat
```

### Passo 4: Verificar

```cmd
verificar_status.bat
```

---

## 📋 Arquivos Modificados

### Arquivos Principais

1. **`probe_core.py`** ⭐ PRINCIPAL
   - Adicionado método `_collect_remote_servers()`
   - Adicionado método `_collect_wmi_remote()`
   - Adicionado método `_collect_snmp_remote()`
   - Adicionado método `_collect_ping_only()`

2. **`collectors/wmi_remote_collector.py`** ⭐ NOVO
   - Coletor WMI remoto
   - Coleta CPU, Memória, Disco, Serviços via WMI

3. **`atualizar_sonda.bat`** ⭐ NOVO
   - Script de atualização automática

### Arquivos Não Modificados

Estes arquivos **NÃO precisam** ser atualizados:
- `config.py`
- `probe_config.json`
- `collectors/cpu_collector.py`
- `collectors/memory_collector.py`
- `collectors/disk_collector.py`
- `collectors/network_collector.py`
- `collectors/service_collector.py`
- Outros collectors

---

## 🧪 Testar Atualização

### 1. Verificar Serviço

```cmd
sc query "Coruja Probe"
```

Deve mostrar: `STATE: 4 RUNNING`

### 2. Verificar Logs

```cmd
cd C:\Coruja\probe
type probe.log | findstr "remote"
```

Deve mostrar:
```
INFO - Fetching remote servers from API
INFO - Collected WMI metrics from 192.168.0.100
INFO - PING 192.168.0.101: OK (12ms)
```

### 3. Verificar na Interface Web

1. Adicionar um servidor com credenciais WMI
2. Aguardar 1-2 minutos
3. Ver dados aparecerem automaticamente

---

## ❌ Troubleshooting

### Problema: Serviço não inicia

**Erro**: "O serviço não pôde ser iniciado"

**Solução**:
```cmd
# Verificar logs
type probe.log

# Reinstalar
uninstall_service.bat
install_service.bat
```

### Problema: Sem coleta remota

**Sintoma**: Só coleta dados da máquina local

**Verificar**:
1. Arquivo `probe_core.py` foi atualizado?
2. Serviço foi reiniciado?
3. Servidores foram adicionados na interface web?

**Solução**:
```cmd
# Verificar versão do arquivo
findstr "_collect_remote_servers" probe_core.py
# Deve encontrar a função
```

### Problema: "Module not found: wmi_remote_collector"

**Causa**: Arquivo `collectors/wmi_remote_collector.py` não foi copiado

**Solução**:
```cmd
# Copiar arquivo
copy "caminho\origem\collectors\wmi_remote_collector.py" "C:\Coruja\probe\collectors\"

# Reiniciar serviço
net stop "Coruja Probe"
net start "Coruja Probe"
```

---

## 📊 Comparação: Antes vs Depois

### Antes da Atualização

```
Sonda → Coleta apenas da máquina local
     → Envia para API
     → 1 servidor monitorado
```

### Depois da Atualização

```
Sonda → Coleta da máquina local
     → Busca lista de servidores da API
     → Coleta de servidores remotos via WMI/SNMP/PING
     → Envia tudo para API
     → N servidores monitorados
```

---

## 🎯 Resumo

### ✅ O Que Fazer

1. **Copiar** `probe_core.py` atualizado
2. **Copiar** `collectors/wmi_remote_collector.py` (novo)
3. **Executar** `atualizar_sonda.bat`
4. **Verificar** `verificar_status.bat`
5. **Adicionar** servidores na interface web
6. **Aguardar** 1-2 minutos
7. **Ver** dados aparecerem

### ⏱️ Tempo Estimado

- Atualização: **2 minutos**
- Downtime: **30 segundos** (enquanto reinstala serviço)
- Primeira coleta remota: **1-2 minutos**

### 🔄 Frequência de Atualização

- **Não precisa** atualizar novamente
- Esta é a versão final com coleta remota
- Futuras atualizações serão opcionais (novos recursos)

---

## 📞 Suporte

Se tiver problemas:

1. Verificar logs: `type probe.log`
2. Verificar serviço: `sc query "Coruja Probe"`
3. Testar manualmente: `python probe_core.py`

---

**Data**: 13/02/2026
**Versão**: Agentless (PRTG-style)
**Status**: Pronto para atualização
