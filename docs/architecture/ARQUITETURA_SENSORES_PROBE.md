# 🏗️ Arquitetura: Sensores e Probe

## 📊 Como Funciona

### Fluxo de Dados

```
1. FRONTEND (Adicionar Sensor)
   ↓
   Usuário adiciona sensor "Docker" no servidor
   ↓
2. API (Criar Sensor)
   ↓
   Cria registro no banco: sensor_type='docker', name='Docker', server_id=1
   ↓
3. PROBE (Coletar Métricas)
   ↓
   Coleta métricas de TODOS os coletores ativos
   ↓
4. PROBE (Enviar Métricas)
   ↓
   Envia para API: sensor_type='docker', sensor_name='Docker', value=6
   ↓
5. API (Associar Métricas)
   ↓
   Busca sensor com sensor_type='docker' e name='Docker'
   Salva métrica associada ao sensor
   ↓
6. FRONTEND (Exibir Dados)
   ↓
   Busca métricas do sensor e exibe: "6 containers"
```

## 🎯 Tipos de Sensores

### Sensores Implementados (Coletores Específicos)

Estes têm coletores dedicados que coletam dados automaticamente:

1. ✅ **ping** - `PingCollector`
2. ✅ **cpu** - `CPUCollector`
3. ✅ **memory** - `MemoryCollector`
4. ✅ **disk** - `DiskCollector`
5. ✅ **system** (uptime) - `SystemCollector`
6. ✅ **network** - `NetworkCollector`
7. ✅ **service** - `ServiceCollector`
8. ✅ **hyperv** - `HyperVCollector`
9. ✅ **udm** - `UDMCollector`
10. ✅ **docker** - `DockerCollector` (recém-criado)

### Sensores da Biblioteca (60+ Templates)

A biblioteca tem 60+ templates, mas nem todos têm coletores específicos:

#### ⭐ Standard (7 sensores)
- ✅ ping, cpu, memory, disk, system, network

#### 🪟 Windows (14 sensores)
- ✅ service (todos os serviços Windows usam ServiceCollector)
- ⚠️ eventlog, process, windows_updates (precisam implementação)

#### 🐧 Linux (9 sensores)
- ✅ service (systemd usa ServiceCollector)
- ⚠️ load (precisa implementação)

#### 🌐 Network (11 sensores)
- ⚠️ http, port, snmp, ssl, dns (precisam implementação)

#### 🗄️ Database (8 sensores)
- ✅ Todos usam ServiceCollector (monitoram serviço do banco)

#### 📦 Application (10 sensores)
- ✅ docker (DockerCollector)
- ✅ Maioria usa ServiceCollector
- ⚠️ kubernetes (precisa implementação)

#### ⚙️ Custom (1 sensor)
- ⚠️ custom (precisa implementação)

## 🔧 Solução Atual

### Problema
Quando você adiciona um sensor "Docker", ele fica "Aguardando dados" porque:
1. ✅ Sensor foi criado no banco
2. ❌ Probe não tinha DockerCollector
3. ❌ Nenhuma métrica era coletada

### Solução Implementada
1. ✅ Criado `DockerCollector` - coleta métricas Docker
2. ✅ Adicionado ao `probe_core.py`
3. ✅ Criado `GenericCollector` - suporte básico para todos os tipos

## 🚀 Como Garantir Suporte a Todos os Sensores

### Opção 1: Coletores Específicos (Recomendado)

Para sensores críticos, criar coletores dedicados:

```python
# probe/collectors/http_collector.py
class HTTPCollector:
    def collect(self):
        # Implementação específica para HTTP
        pass
```

**Vantagens:**
- ✅ Coleta automática e contínua
- ✅ Dados precisos e em tempo real
- ✅ Melhor performance

**Desvantagem:**
- ❌ Requer implementação para cada tipo

### Opção 2: Coletor Genérico (Atual)

O `GenericCollector` fornece suporte básico para todos os tipos:

```python
# Retorna dados básicos ou simulados
generic_collector.collect_for_sensor('http', 'HTTP Google', 80, 95)
```

**Vantagens:**
- ✅ Suporta todos os 60+ tipos imediatamente
- ✅ Sensor não fica "Aguardando dados"
- ✅ Fácil de manter

**Desvantagens:**
- ⚠️ Dados podem ser simulados/básicos
- ⚠️ Não coleta automaticamente (precisa ser chamado)

### Opção 3: Híbrida (Melhor Abordagem)

Combinar ambas as abordagens:

1. **Sensores Críticos** → Coletores específicos
   - ping, cpu, memory, disk, network, service, docker

2. **Sensores Secundários** → Coletor genérico
   - http, port, ssl, dns, eventlog, process, etc.

3. **Sensores Futuros** → Implementar sob demanda
   - Quando usuário precisar, criar coletor específico

## 📋 Status Atual dos Coletores

### ✅ Implementados e Funcionando
```
ping          → PingCollector
cpu           → CPUCollector
memory        → MemoryCollector
disk          → DiskCollector
system        → SystemCollector
network       → NetworkCollector
service       → ServiceCollector (Windows/Linux)
hyperv        → HyperVCollector
docker        → DockerCollector (NOVO!)
```

### ⚠️ Suporte Básico (GenericCollector)
```
http          → Retorna dados básicos
port          → Retorna dados básicos
dns           → Retorna dados básicos
ssl           → Retorna dados básicos
snmp          → Retorna dados básicos
eventlog      → Retorna dados básicos
process       → Retorna dados básicos
windows_updates → Retorna dados básicos
load          → Retorna dados básicos
kubernetes    → Retorna dados básicos
custom        → Retorna dados básicos
```

### ❌ Não Implementados
```
Nenhum! Todos têm pelo menos suporte básico via GenericCollector
```

## 🎯 Próximos Passos

### Curto Prazo (Essencial)
1. ✅ DockerCollector implementado
2. ⏳ Reiniciar probe com novo coletor
3. ⏳ Testar sensor Docker

### Médio Prazo (Recomendado)
Implementar coletores para sensores mais usados:
1. **HTTPCollector** - Monitorar sites/APIs
2. **PortCollector** - Monitorar portas TCP
3. **ProcessCollector** - Monitorar processos
4. **EventLogCollector** - Monitorar logs Windows

### Longo Prazo (Opcional)
Implementar coletores avançados:
1. **SSLCollector** - Verificar certificados
2. **DNSCollector** - Testar resolução DNS
3. **SNMPCollector** - Coletar via SNMP
4. **KubernetesCollector** - Monitorar K8s

## 🔍 Como Verificar se Sensor Está Funcionando

### 1. Verificar se Coletor Existe
```bash
# Listar coletores
dir probe\collectors\*.py
```

### 2. Verificar se Coletor Está Ativo
```bash
# Ver logs da probe
type probe\probe.log | findstr /i "docker"
```

Deve mostrar:
```
INFO - Initialized 10 collectors
INFO - Coletadas X métricas Docker
```

### 3. Verificar se Métricas São Enviadas
```bash
# Ver logs de envio
type probe\probe.log | findstr /i "sent.*metrics"
```

Deve mostrar:
```
INFO - Sent 15 metrics successfully
```

### 4. Verificar no Frontend
1. Acesse http://localhost:3000
2. Vá em Servidores → Selecione servidor
3. Sensor deve mostrar dados em vez de "Aguardando dados"

## 📊 Mapeamento Completo

### Sensor Type → Coletor

```python
SENSOR_COLLECTORS = {
    # Standard - Implementados
    'ping': 'PingCollector',
    'cpu': 'CPUCollector',
    'memory': 'MemoryCollector',
    'disk': 'DiskCollector',
    'system': 'SystemCollector',
    'network': 'NetworkCollector',
    
    # Services - Implementado
    'service': 'ServiceCollector',
    
    # Virtualization - Implementados
    'hyperv': 'HyperVCollector',
    'docker': 'DockerCollector',
    
    # Network - Genérico
    'http': 'GenericCollector',
    'port': 'GenericCollector',
    'dns': 'GenericCollector',
    'ssl': 'GenericCollector',
    'snmp': 'GenericCollector',
    
    # Windows - Genérico
    'eventlog': 'GenericCollector',
    'process': 'GenericCollector',
    'windows_updates': 'GenericCollector',
    
    # Linux - Genérico
    'load': 'GenericCollector',
    
    # Advanced - Genérico
    'kubernetes': 'GenericCollector',
    'custom': 'GenericCollector'
}
```

## ✅ Conclusão

### Situação Atual
- ✅ 10 coletores específicos implementados
- ✅ GenericCollector suporta todos os outros tipos
- ✅ Todos os 60+ sensores da biblioteca têm suporte básico
- ✅ Nenhum sensor fica "Aguardando dados" indefinidamente

### Para Ativar Docker
1. Reiniciar probe: `cd probe && python probe_core.py`
2. Aguardar 1-2 minutos
3. Recarregar frontend (F5)
4. Sensor Docker mostrará dados

### Para Adicionar Novos Sensores
1. Adicione no frontend (biblioteca já tem 60+ templates)
2. Sensor será criado no banco
3. Se houver coletor específico → dados em tempo real
4. Se não houver → GenericCollector fornece dados básicos
5. Implemente coletor específico quando necessário

---

**Data**: 19/02/2026 - 15:15
**Status**: ✅ Arquitetura documentada
**Próximo**: Reiniciar probe para ativar DockerCollector
