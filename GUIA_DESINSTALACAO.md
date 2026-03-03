# Guia de Desinstalação - Coruja Probe

## 📅 Data: 24 de Fevereiro de 2026

## 🎯 Opções de Desinstalação

Criamos 2 desinstaladores com níveis diferentes de remoção:

---

## 🔧 Opção 1: Desinstalação Padrão (RECOMENDADO)

### Arquivo: `probe/desinstalar_probe.bat`

**Remove**:
- ✅ Tarefa agendada "CorujaProbe"
- ✅ Processo Python rodando
- ✅ Arquivos de configuração (probe_config.json, wmi_credentials.json)
- ✅ Logs (probe.log, pasta logs/)

**Mantém**:
- ✅ Código fonte (probe_core.py)
- ✅ Coletores (collectors/)
- ✅ Dependências (requirements.txt)
- ✅ Instaladores (.bat)
- ✅ Documentação (.md)

**Quando usar**:
- Quer reconfigurar a probe
- Quer reinstalar com novas credenciais
- Quer limpar configurações antigas
- Quer manter o código para reinstalar depois

**Como usar**:
```batch
# Botão direito → Executar como administrador
probe/desinstalar_probe.bat
```

---

## 🗑️ Opção 2: Desinstalação Completa (CUIDADO!)

### Arquivo: `probe/desinstalar_tudo.bat`

**Remove TUDO**:
- ✅ Tarefa agendada "CorujaProbe"
- ✅ Processo Python rodando
- ✅ Arquivos de configuração
- ✅ Logs
- ✅ Código fonte (probe_core.py, config.py, etc)
- ✅ Coletores (collectors/)
- ✅ Dependências (requirements.txt)
- ✅ Cache Python (__pycache__/)

**Mantém apenas**:
- ✅ Instaladores (.bat)
- ✅ Documentação (.md)

**Quando usar**:
- Quer remover completamente a probe
- Não vai usar mais
- Quer limpar tudo
- Vai copiar pasta probe novamente do zero

**Como usar**:
```batch
# Botão direito → Executar como administrador
probe/desinstalar_tudo.bat
```

**⚠️ ATENÇÃO**: Pede confirmação dupla!
1. Confirmar com "S"
2. Digitar "REMOVER TUDO"

---

## 📋 Comparação

| Item | Desinstalação Padrão | Desinstalação Completa |
|------|---------------------|------------------------|
| Tarefa agendada | ✅ Remove | ✅ Remove |
| Processo | ✅ Para | ✅ Para |
| Configurações | ✅ Remove | ✅ Remove |
| Logs | ✅ Remove | ✅ Remove |
| Código fonte | ❌ Mantém | ✅ Remove |
| Coletores | ❌ Mantém | ✅ Remove |
| Dependências | ❌ Mantém | ✅ Remove |
| Instaladores | ❌ Mantém | ❌ Mantém |
| Documentação | ❌ Mantém | ❌ Mantém |
| Reinstalar | ✅ Fácil | ⚠️ Precisa copiar pasta |

---

## 🎮 Como Usar

### Desinstalação Padrão

```batch
# 1. Ir para pasta probe
cd C:\Coruja Monitor\probe

# 2. Executar como admin (botão direito)
desinstalar_probe.bat

# 3. Confirmar com "S"

# 4. Aguardar conclusão
```

**Resultado**:
```
========================================
  DESINSTALACAO CONCLUIDA COM SUCESSO!
========================================

A probe foi completamente removida:
  - Tarefa agendada removida
  - Processo parado
  - Arquivos de configuracao removidos
  - Logs removidos

Para reinstalar, execute:
  install_completo_com_servico.bat
```

### Desinstalação Completa

```batch
# 1. Ir para pasta probe
cd C:\Coruja Monitor\probe

# 2. Executar como admin (botão direito)
desinstalar_tudo.bat

# 3. Confirmar com "S"

# 4. Digitar "REMOVER TUDO"

# 5. Escolher se quer backup (S/N)

# 6. Aguardar conclusão
```

**Resultado**:
```
========================================
  REMOCAO COMPLETA COM SUCESSO!
========================================

Tudo foi removido:
  - Tarefa agendada
  - Processo
  - Configuracoes
  - Codigo fonte
  - Coletores
  - Logs

Para reinstalar do zero:
  1. Copie a pasta probe novamente
  2. Execute: install_completo_com_servico.bat
```

---

## 🔍 O Que Cada Desinstalador Faz

### Desinstalação Padrão (desinstalar_probe.bat)

**Passo 1**: Verificar privilégios admin
**Passo 2**: Parar processo Python
**Passo 3**: Remover tarefa agendada "CorujaProbe"
**Passo 4**: Remover arquivos de configuração
**Passo 5**: Remover logs
**Passo 6**: Verificar remoção

### Desinstalação Completa (desinstalar_tudo.bat)

**Passo 1**: Verificar privilégios admin
**Passo 2**: Parar processo Python
**Passo 3**: Remover tarefa agendada "CorujaProbe"
**Passo 4**: Oferecer backup (opcional)
**Passo 5**: Listar arquivos a remover
**Passo 6**: Remover TODOS os arquivos
**Passo 7**: Verificar remoção

---

## 📝 Arquivos Removidos

### Desinstalação Padrão

**Configurações**:
- `probe_config.json`
- `wmi_credentials.json`

**Logs**:
- `probe.log`
- `logs/` (pasta inteira)

**Tarefa**:
- Tarefa agendada "CorujaProbe"

### Desinstalação Completa

**Tudo da desinstalação padrão +**:

**Código fonte**:
- `probe_core.py`
- `config.py`
- `discovery_server.py`
- `probe_service.py`

**Coletores**:
- `collectors/` (pasta inteira)

**Dependências**:
- `requirements.txt`

**Cache**:
- `__pycache__/` (pasta inteira)

---

## 🔄 Reinstalar Após Desinstalação

### Após Desinstalação Padrão

**Muito fácil**:
```batch
# Código ainda está lá, só reinstalar
install_completo_com_servico.bat
```

### Após Desinstalação Completa

**Precisa copiar pasta novamente**:
```batch
# 1. Copiar pasta probe do servidor ou backup
# 2. Executar instalador
install_completo_com_servico.bat
```

---

## 🐛 Troubleshooting

### Problema: Tarefa não foi removida

**Solução manual**:
```batch
schtasks /delete /tn "CorujaProbe" /f
```

### Problema: Processo ainda rodando

**Solução manual**:
```batch
taskkill /F /IM python.exe
```

### Problema: Arquivos não foram removidos

**Solução manual**:
```batch
# Remover configurações
del probe_config.json
del wmi_credentials.json
del probe.log

# Remover logs
rmdir /s /q logs

# Remover código (se quiser)
del probe_core.py
rmdir /s /q collectors
```

### Problema: Desinstalador não executa

**Causa**: Não está executando como administrador

**Solução**:
1. Clique com botão direito no arquivo .bat
2. Escolha "Executar como administrador"

---

## ⚠️ Avisos Importantes

### Desinstalação Padrão
- ✅ Seguro, pode reinstalar facilmente
- ✅ Mantém código fonte
- ✅ Recomendado para reconfiguração

### Desinstalação Completa
- ⚠️ Remove TUDO
- ⚠️ Não pode desfazer
- ⚠️ Precisa copiar pasta novamente
- ⚠️ Use apenas se não vai usar mais

---

## 📊 Fluxo de Decisão

```
Quer desinstalar a probe?
│
├─ Vai reinstalar depois?
│  │
│  ├─ SIM → Use desinstalar_probe.bat
│  │        (mantém código)
│  │
│  └─ NÃO → Use desinstalar_tudo.bat
│           (remove tudo)
│
└─ Só quer reconfigurar?
   └─ Use desinstalar_probe.bat
      depois install_completo_com_servico.bat
```

---

## 🎯 Casos de Uso

### Caso 1: Reconfigurar Credenciais
```batch
# 1. Desinstalar configurações
desinstalar_probe.bat

# 2. Reinstalar com novas credenciais
install_completo_com_servico.bat
```

### Caso 2: Mudar de Servidor
```batch
# 1. Desinstalar configurações
desinstalar_probe.bat

# 2. Reinstalar com novo IP
install_completo_com_servico.bat
# Digitar novo IP: 192.168.1.100
```

### Caso 3: Limpar Tudo
```batch
# 1. Desinstalar tudo
desinstalar_tudo.bat

# 2. Copiar pasta probe novamente (se precisar)

# 3. Reinstalar
install_completo_com_servico.bat
```

### Caso 4: Atualizar Código
```batch
# 1. Desinstalar configurações (mantém código)
desinstalar_probe.bat

# 2. Copiar novos arquivos .py

# 3. Reinstalar
install_completo_com_servico.bat
```

---

## ✅ Checklist de Desinstalação

### Antes de Desinstalar
- [ ] Fazer backup das configurações (se precisar)
- [ ] Anotar IP do servidor
- [ ] Anotar token da probe
- [ ] Decidir qual desinstalador usar

### Durante Desinstalação
- [ ] Executar como administrador
- [ ] Confirmar remoção
- [ ] Aguardar conclusão
- [ ] Verificar mensagem de sucesso

### Após Desinstalação
- [ ] Verificar tarefa removida: `schtasks /query /tn "CorujaProbe"`
- [ ] Verificar processo parado: `tasklist | findstr python`
- [ ] Verificar arquivos removidos
- [ ] Remover da interface web (se não vai reinstalar)

---

## 📞 Comandos Úteis

### Verificar se foi desinstalado

```batch
# Ver tarefa agendada
schtasks /query /tn "CorujaProbe"
# Deve dar erro "não encontrado"

# Ver processo
tasklist | findstr python
# Não deve mostrar nada

# Ver arquivos
dir probe_config.json
# Deve dar erro "não encontrado"
```

### Desinstalar manualmente

```batch
# Parar probe
taskkill /F /IM python.exe

# Remover tarefa
schtasks /delete /tn "CorujaProbe" /f

# Remover configurações
del probe_config.json
del wmi_credentials.json
del probe.log

# Remover logs
rmdir /s /q logs
```

---

## 🚀 Resumo

### Desinstalação Padrão (RECOMENDADO)
```batch
probe/desinstalar_probe.bat
```
- Remove configurações e logs
- Mantém código fonte
- Fácil de reinstalar

### Desinstalação Completa (CUIDADO)
```batch
probe/desinstalar_tudo.bat
```
- Remove TUDO
- Precisa copiar pasta novamente
- Use apenas se não vai usar mais

---

**Use `desinstalar_probe.bat` para reconfigurar!** 🔧

**Use `desinstalar_tudo.bat` apenas se não vai usar mais!** 🗑️
