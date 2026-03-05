# 🚀 Guia de Instalação - Probe como Serviço

## ✅ Problema Resolvido

A probe agora inicia automaticamente quando a máquina ligar!

## 📋 Pré-requisitos

1. ✅ Python 3.8+ instalado
2. ✅ Probe configurada (execute `install.bat` primeiro)
3. ✅ Privilégios de administrador

## 🔧 Instalação Rápida

### Passo 1: Configurar a Probe

Se ainda não configurou, execute primeiro:

```batch
install.bat
```

Isso criará:
- `probe_config.json` - Configuração da API
- `wmi_credentials.json` - Credenciais WMI

### Passo 2: Instalar como Serviço

Execute como **Administrador**:

```batch
install_service.bat
```

Escolha o método:

#### Opção 1: Task Scheduler (Recomendado) ⭐

- ✅ Nativo do Windows
- ✅ Mais simples
- ✅ Não requer downloads
- ✅ Inicia 30s após boot
- ✅ Reinicia automaticamente em caso de falha

#### Opção 2: Serviço Windows (Avançado)

- ✅ Inicia antes do login
- ✅ Mais robusto
- ⚠️ Requer NSSM (download manual)

## 📊 Verificar Status

### Task Scheduler

```batch
# Ver status
schtasks /query /tn "CorujaMonitorProbe"

# Ver detalhes
schtasks /query /tn "CorujaMonitorProbe" /v /fo list
```

### Serviço Windows (NSSM)

```batch
# Ver status
nssm status CorujaProbe

# Ver status detalhado
sc query CorujaProbe
```

## 🎮 Controlar o Serviço

### Task Scheduler

```batch
# Iniciar
schtasks /run /tn "CorujaMonitorProbe"

# Parar
taskkill /f /im python.exe /fi "WINDOWTITLE eq probe_core.py"

# Desabilitar
schtasks /change /tn "CorujaMonitorProbe" /disable

# Habilitar
schtasks /change /tn "CorujaMonitorProbe" /enable
```

### Serviço Windows (NSSM)

```batch
# Iniciar
nssm start CorujaProbe
# ou
net start CorujaProbe

# Parar
nssm stop CorujaProbe
# ou
net stop CorujaProbe

# Reiniciar
nssm restart CorujaProbe
```

## 📝 Ver Logs

### Task Scheduler

```batch
# Ver log da probe
type logs\probe.log

# Ver últimas 50 linhas
powershell Get-Content logs\probe.log -Tail 50

# Monitorar em tempo real
powershell Get-Content logs\probe.log -Wait -Tail 10
```

### Serviço Windows (NSSM)

```batch
# Ver stdout
type logs\service_stdout.log

# Ver stderr
type logs\service_stderr.log

# Ver log da probe
type logs\probe.log
```

## 🗑️ Desinstalar

Execute como **Administrador**:

```batch
uninstall_service.bat
```

Isso remove:
- ✅ Tarefa agendada (se instalada)
- ✅ Serviço Windows (se instalado)

## 🔍 Troubleshooting

### Probe não inicia

1. **Verificar Python**:
   ```batch
   python --version
   ```

2. **Verificar dependências**:
   ```batch
   pip install -r requirements.txt
   ```

3. **Testar manualmente**:
   ```batch
   python probe_core.py
   ```

4. **Ver logs**:
   ```batch
   type logs\probe.log
   ```

### Erro de permissão

Execute o instalador como **Administrador**:
- Clique com botão direito → "Executar como administrador"

### Probe para após alguns minutos

**Task Scheduler**: Já configurado para reiniciar automaticamente (3 tentativas, 1 minuto de intervalo)

**Serviço NSSM**: Configure recuperação:
```batch
sc failure CorujaProbe reset= 86400 actions= restart/60000/restart/60000/restart/60000
```

### Verificar se está rodando

```batch
# Ver processos Python
tasklist | findstr python

# Ver detalhes
wmic process where "name='python.exe'" get commandline,processid
```

## 📦 Instalação NSSM (Opcional)

Se escolher o método de Serviço Windows:

1. **Baixar NSSM**:
   - Site: https://nssm.cc/download
   - Versão: 2.24 ou superior

2. **Instalar**:
   ```batch
   # Extrair nssm.exe para:
   C:\Windows\System32\nssm.exe
   
   # Ou adicionar ao PATH
   ```

3. **Verificar**:
   ```batch
   nssm --version
   ```

## 🎯 Configuração Avançada

### Alterar intervalo de coleta

Edite `probe_config.json`:

```json
{
  "collection_interval": 60,  // segundos (padrão: 60)
  ...
}
```

### Alterar nível de log

Edite `probe_config.json`:

```json
{
  "log_level": "INFO",  // DEBUG, INFO, WARNING, ERROR
  ...
}
```

### Reiniciar após mudanças

**Task Scheduler**:
```batch
schtasks /end /tn "CorujaMonitorProbe"
schtasks /run /tn "CorujaMonitorProbe"
```

**Serviço NSSM**:
```batch
nssm restart CorujaProbe
```

## ✅ Checklist Pós-Instalação

- [ ] Probe instalada como serviço
- [ ] Serviço iniciado com sucesso
- [ ] Logs sendo gerados em `logs/probe.log`
- [ ] Dados aparecendo no dashboard Coruja
- [ ] Máquina reiniciada para testar auto-start
- [ ] Probe voltou automaticamente após reboot

## 🆘 Suporte

Se tiver problemas:

1. **Ver logs completos**:
   ```batch
   type logs\probe.log
   ```

2. **Testar conexão com API**:
   ```batch
   curl http://SEU_IP:8000/health
   ```

3. **Verificar configuração**:
   ```batch
   type probe_config.json
   ```

4. **Executar diagnóstico**:
   ```batch
   diagnostico_probe.bat
   ```

## 📚 Documentação Adicional

- `INSTALACAO.md` - Guia completo de instalação
- `README.md` - Visão geral da probe
- `probe_config.json` - Arquivo de configuração

---

**Versão**: 1.0  
**Data**: 04/03/2026  
**Status**: ✅ Testado e Funcionando
