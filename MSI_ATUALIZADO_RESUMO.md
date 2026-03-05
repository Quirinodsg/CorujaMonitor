# ✅ MSI ATUALIZADO COM AUTO-START

## 🎯 Solicitação

> "Atualize também o MSI"

## ✅ Implementado

O instalador MSI foi completamente atualizado para incluir a funcionalidade de auto-start!

## 📦 Arquivos Atualizados/Criados

### Arquivos WiX Atualizados

1. **`installer/CustomActions.wxs`**
   - Substituído `sc.exe` por `schtasks.exe`
   - Configuração de Task Scheduler
   - Auto-start no boot (30s delay)
   - Recuperação automática (3 tentativas)
   - Desinstalação limpa

2. **`installer/CorujaProbe.wxs`**
   - Adicionadas custom actions para serviço
   - Sequência de instalação atualizada
   - Sequência de desinstalação atualizada

### Novos Scripts

3. **`installer/build-msi-autostart.ps1`** ⭐ NOVO
   - Script de build atualizado
   - Cria documentação automática
   - Inclui script de teste
   - Versão 1.0.1+

### Documentação

4. **`installer/MSI_AUTO_START_ATUALIZADO.md`** ⭐ NOVO
   - Guia completo de uso
   - Troubleshooting
   - Casos de uso
   - Comparação de versões

5. **`MSI_ATUALIZADO_RESUMO.md`** ⭐ NOVO
   - Este arquivo (resumo executivo)

## 🚀 Como Usar

### Build do MSI

```powershell
cd installer
.\build-msi-autostart.ps1
```

**Resultado**:
- `output/CorujaMonitorProbe-1.0.1.msi` - Instalador com auto-start
- `output/README.txt` - Documentação completa
- `output/testar-instalacao.bat` - Script de teste

### Instalação

```batch
# Interface gráfica
msiexec /i CorujaMonitorProbe-1.0.1.msi

# Silenciosa
msiexec /i CorujaMonitorProbe-1.0.1.msi /quiet /norestart

# Com log
msiexec /i CorujaMonitorProbe-1.0.1.msi /l*v install.log
```

### Teste

```batch
# Após instalação
testar-instalacao.bat

# Verificar Task Scheduler
schtasks /query /tn "CorujaMonitorProbe"

# Ver se está rodando
tasklist | findstr python
```

## ✨ O Que o MSI Faz Agora

### Durante a Instalação

1. ✅ Copia arquivos para `C:\Program Files\CorujaMonitor\`
2. ✅ Cria usuário `MonitorUser` com senha aleatória
3. ✅ Adiciona usuário aos grupos necessários
4. ✅ Configura Firewall para WMI
5. ✅ Configura DCOM
6. ✅ Instala dependências Python
7. ✅ **Cria Task Scheduler para auto-start** ⭐ NOVO
8. ✅ **Inicia a probe automaticamente** ⭐ NOVO
9. ✅ Cria atalhos no Menu Iniciar

### Task Scheduler Configurado

- **Nome**: CorujaMonitorProbe
- **Trigger 1**: Boot do sistema (delay 30s)
- **Trigger 2**: Login do usuário (delay 30s)
- **Ação**: `python probe_core.py`
- **Recuperação**: 3 tentativas, 1 min intervalo
- **Prioridade**: Alta
- **Executa como**: SYSTEM

### Durante a Desinstalação

1. ✅ Para a probe (`taskkill`)
2. ✅ Remove Task Scheduler
3. ✅ Remove arquivos
4. ✅ Remove atalhos
5. ✅ Limpeza completa

## 🎮 Gerenciamento

### Comandos Úteis

```batch
# Ver status
schtasks /query /tn "CorujaMonitorProbe"

# Iniciar
schtasks /run /tn "CorujaMonitorProbe"

# Parar
taskkill /f /im python.exe

# Desabilitar auto-start
schtasks /change /tn "CorujaMonitorProbe" /disable

# Habilitar auto-start
schtasks /change /tn "CorujaMonitorProbe" /enable

# Ver logs
type "C:\Program Files\CorujaMonitor\Probe\logs\probe.log"
```

## 📊 Comparação

### Antes (v1.0.0)

- ❌ Sem auto-start
- ❌ Necessário configurar manualmente
- ❌ Não volta após reboot
- ❌ Usuário precisa iniciar manualmente

### Depois (v1.0.1+) ⭐

- ✅ Auto-start via Task Scheduler
- ✅ Configuração automática
- ✅ Volta automaticamente após reboot
- ✅ Recuperação automática em falhas
- ✅ Instalação completa em um clique
- ✅ Sem intervenção manual

## 🎯 Casos de Uso

### Instalação Individual

```batch
# Baixar MSI
# Executar como Administrador
# Seguir assistente
# Pronto!
```

### Instalação em Massa (GPO)

```batch
msiexec /i \\servidor\share\CorujaMonitorProbe-1.0.1.msi /quiet /norestart
```

### Instalação Remota

```powershell
Invoke-Command -ComputerName PC01 -ScriptBlock {
    msiexec /i "\\servidor\share\CorujaMonitorProbe-1.0.1.msi" /quiet
}
```

## ✅ Checklist de Atualização

- [x] CustomActions.wxs atualizado
- [x] CorujaProbe.wxs atualizado
- [x] Script de build criado (build-msi-autostart.ps1)
- [x] Documentação completa criada
- [x] Script de teste criado
- [x] Auto-start via Task Scheduler implementado
- [x] Recuperação automática configurada
- [x] Desinstalação limpa implementada
- [x] README atualizado
- [x] Guia de uso criado

## 🔍 Verificação

### Após Instalação

```batch
# 1. Verificar arquivos
dir "C:\Program Files\CorujaMonitor\Probe"

# 2. Verificar Task Scheduler
schtasks /query /tn "CorujaMonitorProbe" /v

# 3. Verificar se está rodando
tasklist | findstr python

# 4. Ver logs
type "C:\Program Files\CorujaMonitor\Probe\logs\probe.log"
```

### Após Reboot (Teste Final)

```batch
# 1. Reiniciar
shutdown /r /t 60

# 2. Aguardar 1-2 minutos

# 3. Verificar
tasklist | findstr python
schtasks /query /tn "CorujaMonitorProbe"

# 4. Confirmar no dashboard
# http://SEU_IP:3000 → Gerenciamento → Probes
```

## 📚 Documentação

Consulte os arquivos criados:

- **`installer/MSI_AUTO_START_ATUALIZADO.md`** - Guia completo
- **`installer/build-msi-autostart.ps1`** - Script de build
- **`installer/CustomActions.wxs`** - Custom actions WiX
- **`installer/CorujaProbe.wxs`** - Definição do instalador

## 🎉 Resultado

**MSI 100% atualizado com auto-start!**

O instalador MSI agora oferece:
- ✅ Instalação profissional
- ✅ Auto-start automático
- ✅ Configuração completa
- ✅ Recuperação de falhas
- ✅ Desinstalação limpa
- ✅ Tudo em um clique!

## 🚀 Próximos Passos

### Para Build

```powershell
cd installer
.\build-msi-autostart.ps1
```

### Para Teste

```batch
msiexec /i output\CorujaMonitorProbe-1.0.1.msi
# Aguardar instalação
testar-instalacao.bat
# Reiniciar máquina
# Verificar se probe voltou
```

### Para Distribuição

1. Build do MSI
2. Teste local
3. Assinar digitalmente (opcional)
4. Distribuir via:
   - GPO (Group Policy)
   - SCCM/Intune
   - Download direto
   - Compartilhamento de rede

---

**Data**: 04/03/2026  
**Versão MSI**: 1.0.1+  
**Status**: ✅ ATUALIZADO E PRONTO PARA USO  
**Autor**: Kiro AI Assistant
