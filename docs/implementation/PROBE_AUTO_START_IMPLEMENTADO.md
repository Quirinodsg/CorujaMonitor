# Probe com Início Automático - IMPLEMENTADO ✅

## 📅 Data: 24 de Fevereiro de 2026

## 🎯 Objetivo

Criar instalador que inicia a probe automaticamente após instalação e configura para iniciar com o Windows, eliminando a necessidade de deixar janela aberta.

---

## ✅ O Que Foi Implementado

### 1. Instalador Completo com Serviço
**Arquivo**: `probe/install_completo_com_servico.bat`

**Funcionalidades**:
- ✅ Detecta usuário atual automaticamente
- ✅ Configura Firewall, DCOM e WMI
- ✅ Cria arquivos de configuração (probe_config.json, wmi_credentials.json)
- ✅ Verifica instalação do Python
- ✅ Instala dependências Python automaticamente
- ✅ Cria tarefa agendada do Windows (schtasks)
- ✅ Inicia probe imediatamente em segundo plano
- ✅ Probe inicia automaticamente com o Windows

**Como funciona**:
1. Usuário executa como administrador
2. Instalador detecta usuário e hostname
3. Solicita apenas a senha do usuário
4. Configura tudo automaticamente
5. Cria tarefa agendada: `CorujaProbe`
6. Inicia probe com `start /MIN python probe_core.py`
7. Probe roda em segundo plano

**Tarefa Agendada**:
- Nome: `CorujaProbe`
- Trigger: Iniciar com o sistema (onstart)
- Comando: `python C:\Coruja Monitor\probe\probe_core.py`
- Usuário: SYSTEM
- Privilégio: HIGHEST

---

### 2. Script de Verificação
**Arquivo**: `probe/verificar_instalacao.bat`

**Funcionalidades**:
- ✅ Verifica arquivos de configuração
- ✅ Verifica instalação do Python
- ✅ Verifica dependências instaladas
- ✅ Verifica tarefa agendada criada
- ✅ Verifica se probe está rodando
- ✅ Mostra últimas 20 linhas do log
- ✅ Fornece resumo e próximos passos

**Como usar**:
```bash
cd C:\Coruja Monitor\probe
verificar_instalacao.bat
```

---

### 3. Documentação Atualizada
**Arquivo**: `COMO_INSTALAR_NOVA_PROBE.md`

**Atualizações**:
- ✅ Seção sobre instalador com auto-start
- ✅ Comparação entre instaladores
- ✅ Instruções de gerenciamento da probe
- ✅ Comandos para habilitar/desabilitar auto-start
- ✅ Troubleshooting expandido
- ✅ Checklist atualizado

---

## 🔧 Detalhes Técnicos

### Tarefa Agendada Windows

**Criação**:
```batch
schtasks /create /tn "CorujaProbe" /tr "python probe_core.py" /sc onstart /ru SYSTEM /rl HIGHEST /f
```

**Verificação**:
```batch
schtasks /query /tn "CorujaProbe"
```

**Remoção**:
```batch
schtasks /delete /tn "CorujaProbe" /f
```

### Início em Segundo Plano

**Comando**:
```batch
start "Coruja Probe" /MIN python probe_core.py
```

**Parâmetros**:
- `start` - Inicia novo processo
- `"Coruja Probe"` - Título da janela
- `/MIN` - Inicia minimizado
- `python probe_core.py` - Comando a executar

### Verificação de Execução

**Ver processos Python**:
```batch
tasklist | findstr python
```

**Ver janela minimizada**:
- Procurar "Coruja Probe" na barra de tarefas

---

## 📋 Fluxo de Instalação

### Passo a Passo Automático

1. **Verificar Admin**
   - Verifica se está rodando como administrador
   - Falha se não tiver privilégios

2. **Detectar Usuário**
   - Detecta `%USERNAME%` automaticamente
   - Detecta `%HOSTNAME%` automaticamente

3. **Solicitar Senha**
   - Pede apenas a senha do usuário atual
   - Mais rápido que criar novo usuário

4. **Configurar Firewall**
   - Habilita regras WMI
   - Adiciona portas TCP necessárias

5. **Configurar DCOM**
   - Habilita DCOM
   - Configura níveis de autenticação

6. **Configurar WMI**
   - Ajusta permissões WMI
   - Configura namespace root

7. **Criar Credenciais**
   - Cria `wmi_credentials.json`
   - Formato: hostname → username/password/domain

8. **Configurar Probe**
   - Solicita IP do servidor
   - Solicita token da probe
   - Cria `probe_config.json`

9. **Verificar Python**
   - Verifica se Python está instalado
   - Mostra aviso se não encontrado

10. **Instalar Dependências**
    - Executa `pip install -r requirements.txt`
    - Instala: psutil, httpx, pywin32, etc

11. **Criar Serviço**
    - Cria tarefa agendada Windows
    - Configura para iniciar com sistema

12. **Iniciar Probe**
    - Inicia probe em segundo plano
    - Verifica se iniciou corretamente

---

## 🎯 Vantagens

### Antes (Instalador Manual)
❌ Precisava deixar janela CMD aberta  
❌ Probe parava ao fechar janela  
❌ Não iniciava automaticamente  
❌ Precisava iniciar manualmente após reboot  
❌ Menos profissional  

### Agora (Instalador com Serviço)
✅ Probe roda em segundo plano  
✅ Não precisa deixar janela aberta  
✅ Inicia automaticamente com Windows  
✅ Reinicia automaticamente após reboot  
✅ Mais profissional e confiável  
✅ Gerenciamento via schtasks  

---

## 📊 Comparação de Instaladores

| Instalador | Auto-Start | Segundo Plano | Detecta User | Velocidade |
|------------|-----------|---------------|--------------|------------|
| `install_completo_com_servico.bat` | ✅ | ✅ | ✅ | Médio |
| `install_usuario_atual.bat` | ❌ | ❌ | ✅ | Rápido |
| `install_sem_usuario.bat` | ❌ | ❌ | ❌ | Muito Rápido |
| `INSTALAR_AQUI.bat` (menu) | ❌ | ❌ | Depende | Lento |

**Recomendação**: Use `install_completo_com_servico.bat` para instalação profissional.

---

## 🔍 Comandos de Gerenciamento

### Ver Status da Probe

```batch
# Ver se está rodando
tasklist | findstr python

# Ver tarefa agendada
schtasks /query /tn "CorujaProbe" /fo LIST

# Ver log
type probe.log

# Ver últimas 20 linhas do log
powershell -Command "Get-Content probe.log -Tail 20"
```

### Controlar Probe

```batch
# Iniciar manualmente
start_probe.bat

# Parar probe
taskkill /F /IM python.exe

# Reiniciar probe
taskkill /F /IM python.exe
start_probe.bat
```

### Gerenciar Auto-Start

```batch
# Desabilitar auto-start
schtasks /delete /tn "CorujaProbe" /f

# Habilitar auto-start novamente
schtasks /create /tn "CorujaProbe" /tr "python C:\Coruja Monitor\probe\probe_core.py" /sc onstart /ru SYSTEM /rl HIGHEST /f

# Verificar status
schtasks /query /tn "CorujaProbe"
```

---

## 🧪 Testes Necessários

### Teste 1: Instalação Completa
- [ ] Executar `install_completo_com_servico.bat` como admin
- [ ] Verificar se solicita IP e token
- [ ] Verificar se solicita senha
- [ ] Verificar se instala dependências
- [ ] Verificar se cria tarefa agendada
- [ ] Verificar se inicia probe

### Teste 2: Verificação
- [ ] Executar `verificar_instalacao.bat`
- [ ] Verificar se mostra arquivos OK
- [ ] Verificar se mostra Python OK
- [ ] Verificar se mostra tarefa OK
- [ ] Verificar se mostra probe rodando

### Teste 3: Auto-Start
- [ ] Reiniciar Windows
- [ ] Verificar se probe iniciou automaticamente
- [ ] Verificar log após reboot
- [ ] Verificar se sensores aparecem no dashboard

### Teste 4: Gerenciamento
- [ ] Parar probe manualmente
- [ ] Iniciar probe manualmente
- [ ] Desabilitar auto-start
- [ ] Habilitar auto-start novamente

---

## 📝 Próximos Passos

### Melhorias Futuras
1. **Serviço Windows Real**
   - Usar `nssm` ou `pywin32` para criar serviço real
   - Mais robusto que tarefa agendada
   - Melhor gerenciamento via services.msc

2. **Interface Gráfica**
   - Criar GUI para instalação
   - Mais amigável para usuários não técnicos
   - Validação de campos em tempo real

3. **Atualização Automática**
   - Probe verifica atualizações
   - Download e instalação automática
   - Reinício automático após atualização

4. **Monitoramento de Saúde**
   - Probe envia heartbeat a cada minuto
   - API detecta probe offline
   - Notificação quando probe para

---

## 🐛 Troubleshooting

### Problema: Tarefa não foi criada

**Causa**: Erro ao executar schtasks  
**Solução**:
```batch
# Verificar se tem privilégios admin
net session

# Criar manualmente
schtasks /create /tn "CorujaProbe" /tr "python C:\Coruja Monitor\probe\probe_core.py" /sc onstart /ru SYSTEM /rl HIGHEST /f
```

### Problema: Probe não inicia

**Causa**: Python não encontrado ou dependências faltando  
**Solução**:
```batch
# Verificar Python
python --version

# Instalar dependências
pip install -r requirements.txt

# Testar manualmente
python probe_core.py
```

### Problema: Probe para após alguns minutos

**Causa**: Erro no código ou conexão com API  
**Solução**:
```batch
# Ver log
type probe.log

# Ver últimas linhas
powershell -Command "Get-Content probe.log -Tail 50"

# Verificar conectividade
ping 192.168.0.9
curl http://192.168.0.9:8000/health
```

---

## ✅ Status Final

### Implementado
- ✅ Instalador completo com serviço
- ✅ Criação de tarefa agendada Windows
- ✅ Início automático em segundo plano
- ✅ Script de verificação
- ✅ Documentação atualizada
- ✅ Comandos de gerenciamento

### Testado
- ⏳ Aguardando teste pelo usuário
- ⏳ Verificar se tarefa é criada corretamente
- ⏳ Verificar se probe inicia automaticamente
- ⏳ Verificar se sensores aparecem no dashboard

### Próximos Passos
1. Usuário testar instalador completo
2. Verificar se probe inicia automaticamente
3. Verificar se sensores aparecem no dashboard
4. Ajustar se necessário

---

## 📞 Arquivos Criados/Modificados

### Novos Arquivos
```
probe/install_completo_com_servico.bat    ← Instalador com auto-start
probe/verificar_instalacao.bat            ← Verificador de instalação
PROBE_AUTO_START_IMPLEMENTADO.md          ← Esta documentação
```

### Arquivos Modificados
```
COMO_INSTALAR_NOVA_PROBE.md               ← Atualizado com novo instalador
probe/install_completo_com_servico.bat    ← Melhorias no feedback
```

---

**Instalador com início automático implementado e pronto para uso!** 🚀
