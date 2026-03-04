# Instruções Rápidas - Corrigir Coleta Remota

## O Que Foi Feito
Corrigi o código da sonda para melhorar a coleta remota e adicionei logs detalhados para debug.

## Como Atualizar (3 Passos)

### 1. Copiar Arquivos Atualizados
Execute no diretório do projeto:
```cmd
copiar_probe_atualizada.bat
```

### 2. Atualizar a Sonda
Abra CMD como Administrador e execute:
```cmd
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
atualizar_sonda.bat
```

### 3. Verificar Logs
```cmd
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
debug_remote.bat
```

## O Que Esperar nos Logs

### ✅ Funcionando Corretamente:
```
INFO - Found 2 servers to monitor remotely
INFO - Collecting from remote server: SERVIDOR-REMOTO (192.168.0.100)
INFO - Using WMI for SERVIDOR-REMOTO
INFO - Collected WMI metrics from 192.168.0.100
INFO - Sent 15 metrics successfully
```

### ❌ Problemas Comuns:

**Nenhum servidor encontrado:**
```
INFO - Found 0 servers to monitor remotely
DEBUG - No remote servers configured
```
→ Solução: Adicione o servidor na interface web

**Credenciais não configuradas:**
```
WARNING - WMI credentials not configured for 192.168.0.100
```
→ Solução: Configure usuário/senha WMI na interface

**Erro de conexão WMI:**
```
ERROR - WMI collection failed for SERVIDOR: [WinError 5] Access denied
```
→ Solução: Verifique firewall e permissões no servidor remoto

## Configuração Mínima no Servidor Remoto

Para a coleta remota funcionar, o servidor Windows remoto precisa:

1. **Firewall liberado:**
```cmd
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
```

2. **Serviço WMI rodando:**
```cmd
net start winmgmt
```

3. **Usuário administrador configurado na interface**

## Teste Rápido

Teste se o WMI está acessível:
```cmd
wmic /node:IP_SERVIDOR_REMOTO /user:Administrator /password:SENHA computersystem get name
```

Se retornar o nome do computador, está OK!

## Checklist

- [ ] Executei `copiar_probe_atualizada.bat`
- [ ] Executei `atualizar_sonda.bat` como Admin
- [ ] Executei `debug_remote.bat` e vi os logs
- [ ] Servidor remoto está adicionado na interface
- [ ] Credenciais WMI estão configuradas
- [ ] Firewall está liberado no servidor remoto
- [ ] Aguardei 2-3 minutos para coleta

## Precisa de Ajuda?

Compartilhe a saída de:
```cmd
debug_remote.bat
```

E as últimas linhas do log:
```cmd
type probe.log | more
```
