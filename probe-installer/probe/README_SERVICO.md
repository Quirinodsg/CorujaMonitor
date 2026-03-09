# 🔄 Probe com Auto-Start - Problema Resolvido!

## ✅ O Que Foi Corrigido

**ANTES**: Probe parava quando a máquina era desligada e não voltava automaticamente

**AGORA**: Probe inicia automaticamente quando a máquina ligar! 🎉

## 🚀 Como Funciona

A probe agora pode ser instalada como:

### 1️⃣ Tarefa Agendada (Task Scheduler) - Recomendado

- ✅ Nativo do Windows
- ✅ Não requer downloads adicionais
- ✅ Inicia 30 segundos após o boot
- ✅ Reinicia automaticamente se falhar (3 tentativas)
- ✅ Funciona em todas as versões do Windows

### 2️⃣ Serviço Windows (NSSM) - Avançado

- ✅ Inicia antes do login do usuário
- ✅ Mais robusto para servidores
- ⚠️ Requer download do NSSM

## 📦 Instalação

### Opção A: Instalação Completa (Recomendado)

Execute como **Administrador**:

```batch
install.bat
```

No final, escolha **S** para instalar como serviço automaticamente.

### Opção B: Apenas Instalar Serviço

Se já configurou a probe antes:

```batch
install_service.bat
```

## 🎮 Comandos Rápidos

### Verificar Status

```batch
# Task Scheduler
schtasks /query /tn "CorujaMonitorProbe"

# Serviço Windows
nssm status CorujaProbe
```

### Iniciar/Parar

```batch
# Task Scheduler
schtasks /run /tn "CorujaMonitorProbe"
taskkill /f /im python.exe

# Serviço Windows
nssm start CorujaProbe
nssm stop CorujaProbe
```

### Ver Logs

```batch
type logs\probe.log
```

### Desinstalar

```batch
uninstall_service.bat
```

## 📚 Documentação Completa

- **GUIA_INSTALACAO_SERVICO.md** - Guia detalhado com troubleshooting
- **INSTALACAO.md** - Instalação geral da probe
- **README.md** - Visão geral do projeto

## ✨ Benefícios

✅ **Confiabilidade**: Probe sempre rodando  
✅ **Automação**: Sem intervenção manual  
✅ **Recuperação**: Reinicia automaticamente em caso de falha  
✅ **Monitoramento 24/7**: Coleta contínua de métricas  

## 🔧 Arquivos Criados

- `install_service.bat` - Instala probe como serviço
- `uninstall_service.bat` - Remove serviço
- `GUIA_INSTALACAO_SERVICO.md` - Documentação completa

## 🎯 Casos de Uso

### Servidor de Produção

```batch
# Instalar como serviço Windows (NSSM)
install_service.bat
# Escolha opção 2
```

### Estação de Trabalho

```batch
# Instalar como tarefa agendada
install_service.bat
# Escolha opção 1
```

### Desenvolvimento/Teste

```batch
# Executar manualmente
python probe_core.py
```

## ⚡ Quick Start

```batch
# 1. Configurar probe
install.bat

# 2. Instalar como serviço
install_service.bat

# 3. Verificar
schtasks /query /tn "CorujaMonitorProbe"

# 4. Ver logs
type logs\probe.log

# 5. Reiniciar máquina para testar
shutdown /r /t 60
```

## 🆘 Problemas Comuns

### Probe não inicia após reboot

1. Verificar se serviço está instalado:
   ```batch
   schtasks /query /tn "CorujaMonitorProbe"
   ```

2. Ver logs:
   ```batch
   type logs\probe.log
   ```

3. Testar manualmente:
   ```batch
   python probe_core.py
   ```

### Erro de permissão

Execute como **Administrador**:
- Botão direito → "Executar como administrador"

### Python não encontrado

1. Instalar Python 3.8+: https://www.python.org/downloads/
2. Marcar "Add Python to PATH" durante instalação
3. Reiniciar terminal

## 📊 Monitoramento

Após instalação, verifique no dashboard Coruja:

1. Acesse: http://SEU_IP:3000
2. Vá em: Gerenciamento → Probes
3. Verifique se a probe aparece como "Online"
4. Veja as métricas sendo coletadas

## 🔄 Atualização

Para atualizar a probe:

```batch
# 1. Parar serviço
uninstall_service.bat

# 2. Atualizar arquivos
git pull
# ou copiar novos arquivos

# 3. Reinstalar serviço
install_service.bat
```

## 💡 Dicas

- Use **Task Scheduler** para estações de trabalho
- Use **Serviço Windows** para servidores
- Mantenha logs em `logs/probe.log`
- Configure `collection_interval` conforme necessidade
- Teste após instalação reiniciando a máquina

---

**Problema Resolvido**: ✅ Probe agora inicia automaticamente!  
**Data**: 04/03/2026  
**Versão**: 1.0
