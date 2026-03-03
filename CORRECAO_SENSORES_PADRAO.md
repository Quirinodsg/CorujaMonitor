# Correção dos Sensores Padrão

## Problemas Identificados

1. ❌ Sensores de serviço sendo criados automaticamente (W3SVC, MSSQLSERVER, MSSQL$SQLEXPRESS)
2. ❌ Sensor de PING não estava sendo criado
3. ❌ Ordem dos sensores não estava padronizada
4. ❌ Nomes dos sensores em inglês (cpu_usage, memory_usage, etc.)

## Correções Aplicadas

### 1. Sensor de PING Adicionado

Criado novo collector: `probe/collectors/ping_collector.py`
- Faz ping para 8.8.8.8 (Google DNS)
- Mede latência em milissegundos
- Status: OK (<200ms), Warning (>200ms), Critical (offline)

### 2. Ordem dos Sensores Padronizada

Ordem agora é:
1. **Ping** - Conectividade de rede
2. **CPU** - Uso do processador
3. **Memória** - Uso de RAM
4. **Disco** - Uso de espaço (ex: Disco C)
5. **Uptime** - Tempo ligado
6. **Network IN** - Tráfego de entrada
7. **Network OUT** - Tráfego de saída

### 3. Sensores de Serviço Removidos

Os sensores de serviço (W3SVC, MSSQLSERVER, etc.) foram removidos dos sensores padrão.
- Não serão mais criados automaticamente
- Podem ser adicionados manualmente se necessário

### 4. Nomes dos Sensores Atualizados

| Antes | Depois |
|-------|--------|
| cpu_usage | CPU |
| memory_usage | Memória |
| disk_C_ | Disco C |
| uptime | Uptime |
| network_in | Network IN |
| network_out | Network OUT |
| (não existia) | Ping |

## Arquivos Modificados

### Novos Arquivos
- `probe/collectors/ping_collector.py` - Coletor de PING

### Arquivos Modificados
- `probe/probe_core.py` - Ordem dos collectors e importação do PingCollector
- `probe/collectors/cpu_collector.py` - Nome: "cpu_usage" → "CPU"
- `probe/collectors/memory_collector.py` - Nome: "memory_usage" → "Memória"
- `probe/collectors/disk_collector.py` - Nome: "disk_C_" → "Disco C"
- `probe/collectors/system_collector.py` - Nome: "uptime" → "Uptime"
- `probe/collectors/network_collector.py` - Nomes: "network_in" → "Network IN", "network_out" → "Network OUT"
- `probe/config.py` - Lista de serviços monitorados vazia por padrão
- `probe/corrigir_url.bat` - Remove serviços da configuração
- `probe/atualizar_sensores.bat` - Novo script para atualizar configuração

## Como Aplicar as Correções

### Opção 1: Script Automático (RECOMENDADO)

Execute como Administrador:
```batch
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
atualizar_sensores.bat
```

Este script vai:
1. Parar o serviço
2. Atualizar a configuração (remover serviços monitorados)
3. Reiniciar o serviço
4. Novos sensores serão criados automaticamente

### Opção 2: Reinstalar a Probe

Se preferir começar do zero:
```batch
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
uninstall_service.bat
setup_wizard.bat
```

## Limpeza Manual Necessária

Após aplicar as correções, você precisa **excluir manualmente** os sensores antigos no dashboard:

1. Acesse http://localhost:3000
2. Vá em "Servidores"
3. Clique no seu servidor
4. Exclua os sensores antigos:
   - ❌ service_W3SVC
   - ❌ service_MSSQLSERVER
   - ❌ service_MSSQL$SQLEXPRESS
   - ❌ cpu_usage (se existir)
   - ❌ memory_usage (se existir)
   - ❌ disk_C_ (se existir)
   - ❌ uptime (minúsculo, se existir)
   - ❌ network_in (minúsculo, se existir)
   - ❌ network_out (minúsculo, se existir)

4. Aguarde 1-2 minutos
5. Os novos sensores aparecerão automaticamente:
   - ✅ Ping
   - ✅ CPU
   - ✅ Memória
   - ✅ Disco C
   - ✅ Uptime
   - ✅ Network IN
   - ✅ Network OUT

## Resultado Final

Após a correção, você terá:

```
📡 Sensores Padrão (7 sensores)
├─ 🌐 Ping (8.8.8.8) - 12ms - OK
├─ 🖥️ CPU - 17.0% - OK
├─ 💾 Memória - 48.3% - OK
├─ 💿 Disco C - 34.0% - OK
├─ ⏱️ Uptime - 1d 0h 54m - OK
├─ 🌐 Network IN - 3.73 MB/s - OK
└─ 🌐 Network OUT - 0.37 MB/s - OK
```

## Monitoramento de Serviços (Opcional)

Se você quiser monitorar serviços específicos:

1. Edite `probe_config.json`
2. Adicione os serviços desejados:
```json
{
  "monitored_services": [
    "W3SVC",
    "MSSQLSERVER"
  ]
}
```
3. Reinicie o serviço: `net stop CorujaProbe && net start CorujaProbe`

## Verificação

Para verificar se está funcionando:

```batch
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
type probe.log
```

Procure por linhas como:
```
Initialized 8 collectors
Collected metrics from PingCollector
Sent X metrics successfully
```

## Status

✅ Sensor de PING criado
✅ Ordem dos sensores padronizada
✅ Nomes dos sensores atualizados
✅ Sensores de serviço removidos dos padrões
✅ Scripts de atualização criados
⏳ Aguardando você executar `atualizar_sensores.bat`
