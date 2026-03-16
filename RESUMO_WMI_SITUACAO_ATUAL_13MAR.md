# Resumo WMI - Situação Atual (13/MAR/2026)

## ✅ RESOLVIDO

### 1. Sistema de Credenciais Centralizadas
- ✅ Tabela `credentials` criada no banco
- ✅ API `/resolve` retornando campos corretos (`wmi_username`, `wmi_password`, `wmi_domain`)
- ✅ Probe reconhecendo credencial: `🔐 Usando credencial: Techbiz (Nível: tenant)`
- ✅ Credencial WMI "Techbiz" configurada (ID: 2, Usuário: coruja.monitor, Domínio: Techbiz)

### 2. Diagnóstico Completo
- ✅ Confirmado: `wmic.exe` NÃO existe no Windows (deprecado)
- ✅ Confirmado: Porta 5985 (WinRM) ABERTA no servidor 192.168.31.110
- ✅ Identificado: PowerShell Remoting bloqueado (Access Denied)

## ❌ PENDENTE

### 1. Habilitar WinRM no Servidor Remoto (192.168.31.110)
**Executar no servidor 192.168.31.110 (PowerShell como Admin):**

```powershell
# Habilitar PowerShell Remoting
Enable-PSRemoting -Force

# Configurar TrustedHosts
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.31.162" -Force

# Reiniciar WinRM
Restart-Service WinRM
```

### 2. Atualizar Collector WMI para usar PowerShell
**Arquivo:** `probe/collectors/wmi_remote_collector.py`

**Ação:** Substituir implementação wmic por PowerShell Remoting

**Arquivo pronto:** `probe/collectors/wmi_remote_collector_powershell.py`

**Comando para aplicar:**
```powershell
Copy-Item probe\collectors\wmi_remote_collector_powershell.py probe\collectors\wmi_remote_collector.py -Force
```

## 📋 PRÓXIMOS PASSOS

1. **Habilitar WinRM no 192.168.31.110** (arquivo: `HABILITAR_WINRM_192.168.31.110_AGORA.txt`)
2. **Testar conexão PowerShell** do SRVSONDA001 para 192.168.31.110
3. **Atualizar collector** para usar PowerShell em vez de wmic
4. **Reiniciar probe** e verificar coleta de métricas WMI

## 🔧 ARQUITETURA ATUAL

```
┌─────────────────────────────────────────────────────────────┐
│ SERVIDOR LINUX (192.168.31.161)                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ API (Docker)                                            │ │
│ │ - Endpoint /credentials/resolve                         │ │
│ │ - Retorna: wmi_username, wmi_password, wmi_domain      │ │
│ │ - Descriptografa senhas automaticamente                │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ HTTPS
                            │
┌─────────────────────────────────────────────────────────────┐
│ PROBE WINDOWS (SRVSONDA001 - 192.168.31.162)               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ probe_core.py                                           │ │
│ │ - Busca credencial via API                              │ │
│ │ - ✅ Recebe: wmi_username, wmi_password, wmi_domain    │ │
│ │ - Chama WMIRemoteCollector                              │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ wmi_remote_collector.py                                 │ │
│ │ - ❌ Tentando usar wmic.exe (não existe)               │ │
│ │ - ⏳ Precisa usar PowerShell Remoting                  │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WinRM (5985)
                            │ ❌ Access Denied
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ SERVIDOR WINDOWS (SRVHVSPRD010 - 192.168.31.110)           │
│ - WinRM rodando (porta 5985 aberta)                        │
│ - ❌ PowerShell Remoting não habilitado                    │
│ - ⏳ Precisa: Enable-PSRemoting -Force                     │
└─────────────────────────────────────────────────────────────┘
```

## 📊 MÉTRICAS COLETADAS (Quando funcionar)

- ✅ CPU Usage (%)
- ✅ Memory Usage (%)
- ✅ Disk Usage (% por drive)
- ✅ Uptime (dias)
- ✅ Network In/Out (Mbps)

## 🎯 OBJETIVO FINAL

Sistema de monitoramento WMI agentless (sem agente) funcionando igual ao PRTG:
- Credenciais centralizadas no banco
- Herança: Servidor → Grupo → Empresa
- Coleta via PowerShell Remoting (WinRM)
- Métricas em tempo real no dashboard

## 📝 COMMITS REALIZADOS

1. `d974f45` - fix: Corrigir nomes de campos WMI no endpoint /resolve
2. `ccb5ab5` - fix: Corrigir schema WMI password (wmi_password vs wmi_password_encrypted)

## 🔗 ARQUIVOS IMPORTANTES

- `api/routers/credentials.py` - Endpoint /resolve (✅ corrigido)
- `probe/probe_core.py` - Busca credenciais (✅ funcionando)
- `probe/collectors/wmi_remote_collector.py` - Coleta WMI (❌ precisa atualizar)
- `probe/collectors/wmi_remote_collector_powershell.py` - Versão PowerShell (✅ pronta)
- `HABILITAR_WINRM_192.168.31.110_AGORA.txt` - Instruções WinRM

---

**Data:** 13/MAR/2026 17:30  
**Status:** 80% completo - Falta apenas habilitar WinRM e atualizar collector
