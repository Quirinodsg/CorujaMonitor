# Arquitetura Enterprise de Monitoramento - Coruja Monitor

## Análise de Protocolos (antes vs depois)

| Protocolo | Antes | Depois |
|-----------|-------|--------|
| ICMP Ping | Básico (1 pacote, sem packet loss) | Completo: count, latency, packet_loss, retry, timeout |
| WMI | WMINativeCollector simples | WMIEngine + SmartCollector + ConnectionPool |
| WQL Queries | Atributos Python (lento) | WQL direto: Win32_Processor, Win32_OperatingSystem, etc. |
| RPC | Implícito no WMI | RPCFirewallValidator: valida porta 135 + faixa 49152-65535 |
| Remote Registry | Não existia | RemoteRegistryCollector via winreg |
| TCP Port Check | Não existia | TCPPortSensor com latência e retry |

---

## Componentes Criados

### probe/collectors/
- `icmp_sensor.py` — ICMP completo: count, latency_ms, packet_loss_percent, min/avg/max, retry
- `tcp_port_sensor.py` — TCP port check + RPCFirewallValidator (porta 135 + dinâmicas)
- `registry_collector.py` — Remote Registry: OS info, service status, Perflib counters

### probe/engine/
- `wmi_engine.py` — WQL queries padrão (CPU, Memory, Disk, Service, Process, OS)
- `wmi_pool.py` — Connection Pool: max 3 conexões/host, reuse, idle timeout 5min
- `smart_collector.py` — Motor inteligente: PerfCounter → WQL → Registry
- `sensor_engine.py` — Arquitetura de sensores: id, type, target, interval, timeout, retries
- `scheduler.py` — Scheduler central: 30s/60s/300s, retry backoff, proteção overload
- `thread_pool.py` — Worker pool: 10 workers paralelos, stats, timeout por tarefa

---

## Motor Inteligente (item 13) - Por que é 5x mais rápido

O PRTG usa Win32_PerfFormattedData em vez de Win32_Processor porque:

```
Win32_Processor.LoadPercentage     → instancia objeto WMI completo → ~200-500ms
Win32_PerfFormattedData_PerfOS_Processor → lê PDH diretamente → ~20-50ms
```

O SmartCollector implementa esta hierarquia:

```python
# 1. Tenta PerfCounter (mais rápido - PDH direto)
SELECT PercentProcessorTime FROM Win32_PerfFormattedData_PerfOS_Processor WHERE Name='_Total'

# 2. Fallback: WQL padrão
SELECT LoadPercentage FROM Win32_Processor

# 3. Fallback final: Remote Registry (sem WMI)
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Perflib
```

O método usado fica registrado em `metadata.collection_method` para diagnóstico.

---

## WQL Queries Implementadas

```sql
-- CPU (PerfCounter - mais rápido)
SELECT PercentProcessorTime FROM Win32_PerfFormattedData_PerfOS_Processor WHERE Name='_Total'

-- CPU (WQL padrão - fallback)
SELECT LoadPercentage FROM Win32_Processor

-- Memória
SELECT FreePhysicalMemory,TotalVisibleMemorySize FROM Win32_OperatingSystem

-- Disco (apenas locais, DriveType=3)
SELECT DeviceID,FreeSpace,Size,VolumeName FROM Win32_LogicalDisk WHERE DriveType=3

-- Serviços (apenas Auto start)
SELECT Name,State,StartMode,DisplayName FROM Win32_Service WHERE StartMode='Auto'

-- Processos (top 10 por memória)
SELECT Name,ProcessId,WorkingSetSize FROM Win32_Process
```

---

## Connection Pool WMI

```
Host: SRVHVSPRD010.ad.empresaxpto.com.br
  ├── Conexão 1 [em uso]     → coletando CPU
  ├── Conexão 2 [ociosa]     → disponível
  └── Conexão 3 [ociosa]     → disponível (max=3)

Idle timeout: 300s → fecha automaticamente
Cleanup: a cada 60s remove conexões expiradas
```

Evita criar nova conexão WMI a cada ciclo de coleta, que é o principal causador de sobrecarga no `wmiprvse.exe`.

---

## Scheduler - Intervalos e Proteções

```
Sensores por intervalo:
  30s  → ICMP Ping, TCP Port (checks rápidos)
  60s  → CPU, Memory, Disk (padrão)
  300s → Services, Processes (pesados)

Proteções:
  max_sensors_per_host:    10
  max_concurrent_sensors:  20
  max_wmi_queries_per_host: 5
  max_rpc_connections:      3

Retry com backoff exponencial:
  1ª falha → retry em 30s
  2ª falha → retry em 60s
  3ª falha → retry em 120s
  máximo   → 300s
```

---

## Fluxo RPC/WMI

```
Probe (SRVSONDA001)
    │
    ├─ TCP 135 → RPC Endpoint Mapper (SRVHVSPRD010)
    │               │
    │               └─ Retorna porta dinâmica (ex: 49155)
    │
    └─ TCP 49155 → WMI Service (wmiprvse.exe)
                      │
                      ├─ Win32_PerfFormattedData (PDH) ← mais rápido
                      ├─ Win32_Processor              ← fallback
                      ├─ Win32_OperatingSystem
                      └─ Win32_LogicalDisk
```

---

## Tipos de Sensores Disponíveis

| Tipo | Descrição | Intervalo Recomendado |
|------|-----------|----------------------|
| `icmp_ping` | Latência, packet loss, retry | 30s |
| `tcp_port` | Conectividade TCP + latência | 30s |
| `wmi_cpu` | CPU via PerfCounter/WQL | 60s |
| `wmi_memory` | Memória via Win32_OperatingSystem | 60s |
| `wmi_disk` | Discos locais via Win32_LogicalDisk | 60s |
| `wmi_service` | Status de serviços Windows | 300s |
| `wmi_process` | Top processos por memória | 300s |
| `registry_perf` | OS info via Remote Registry | 300s |

---

## Logging Implementado

Cada componente loga:
- `sensor execution` → tempo de execução, status, valor
- `wmi queries` → WQL executada, tempo em ms
- `rpc connections` → porta 135, portas dinâmicas
- `authentication` → usuário, domínio, método (Kerberos/NTLM)
- `timeouts` → tentativa, backoff, próxima execução
- `errors` → stack trace completo, contagem de erros consecutivos

---

## Problemas Encontrados na Análise

1. `WMINativeCollector` criava nova conexão WMI a cada ciclo → substituído por pool
2. `PingCollector` usava apenas 1 pacote sem packet loss → substituído por `ICMPSensor`
3. Não havia validação de firewall RPC antes de tentar WMI → adicionado `RPCFirewallValidator`
4. Sem Remote Registry como fallback → adicionado `RemoteRegistryCollector`
5. Sem scheduler central → sensores executavam no loop principal sem controle de concorrência
6. `CoInitializeSecurity` chamado a cada conexão → movido para inicialização do pool

---

Data: 16/03/2026 | Coruja Monitor Enterprise
