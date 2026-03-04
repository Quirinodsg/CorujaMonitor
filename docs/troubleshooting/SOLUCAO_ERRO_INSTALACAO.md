# Solução: Erro "No such file or directory: requirements.txt"

## ❌ Erro

```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

## 🔍 Causa

O script está sendo executado em um diretório diferente de onde está o arquivo `requirements.txt`.

## ✅ Solução

### Opção 1: Executar no Diretório Correto

```cmd
# Abrir CMD como Administrador
# Navegar para a pasta da probe
cd C:\Coruja\probe

# OU se estiver em outro local
cd "C:\Users\seu_usuario\Coruja Monitor\probe"

# Executar instalador
install_service.bat
```

### Opção 2: Usar Script Corrigido

Os scripts foram corrigidos para mudar automaticamente para o diretório correto.

**Arquivos corrigidos**:
- `install_service.bat` - Adicionado `cd /d "%~dp0"`
- `atualizar_sonda.bat` - Adicionado `cd /d "%~dp0"`

**Como usar**:
1. Substituir os arquivos `.bat` pelos novos
2. Executar normalmente (clique duplo ou CMD)
3. O script mudará automaticamente para o diretório correto

### Opção 3: Instalação Manual

Se os scripts continuarem com problema:

```cmd
# 1. Abrir CMD como Administrador
# 2. Navegar para pasta da probe
cd C:\Coruja\probe

# 3. Instalar dependências manualmente
pip install psutil httpx

# 4. Instalar serviço
python probe_service.py install

# 5. Iniciar serviço
python probe_service.py start

# 6. Verificar
sc query "Coruja Probe"
```

## 📋 Verificar Estrutura de Pastas

A estrutura deve estar assim:

```
C:\Coruja\probe\
├── probe_core.py
├── probe_service.py
├── config.py
├── requirements.txt          ← Este arquivo deve existir
├── install_service.bat
├── uninstall_service.bat
├── atualizar_sonda.bat
├── verificar_status.bat
└── collectors\
    ├── cpu_collector.py
    ├── memory_collector.py
    ├── disk_collector.py
    ├── network_collector.py
    ├── service_collector.py
    ├── wmi_remote_collector.py
    └── __init__.py
```

**Verificar se requirements.txt existe**:
```cmd
cd C:\Coruja\probe
dir requirements.txt
```

Se não existir, criar:
```cmd
echo psutil==5.9.5 > requirements.txt
echo httpx==0.26.0 >> requirements.txt
```

## 🚀 Instalação Passo a Passo

### 1. Verificar Localização

```cmd
# Onde você está?
cd

# Deve mostrar algo como:
# C:\Coruja\probe
```

### 2. Verificar Arquivos

```cmd
dir
```

Deve listar:
- probe_core.py
- requirements.txt
- install_service.bat
- etc

### 3. Instalar

```cmd
# Se estiver no diretório correto
install_service.bat

# Se não estiver, navegar primeiro
cd C:\Coruja\probe
install_service.bat
```

## 🔧 Troubleshooting

### Problema: "Python não encontrado"

**Solução**:
```cmd
# Verificar se Python está instalado
python --version

# Se não estiver, instalar:
# https://www.python.org/downloads/
```

### Problema: "pip não encontrado"

**Solução**:
```cmd
# Atualizar pip
python -m pip install --upgrade pip

# Ou usar python -m pip
python -m pip install -r requirements.txt
```

### Problema: "Acesso negado"

**Solução**:
- Executar CMD como Administrador
- Clicar com botão direito no CMD
- Selecionar "Executar como administrador"

### Problema: "Serviço não inicia"

**Verificar logs**:
```cmd
cd C:\Coruja\probe
type probe.log
```

**Reinstalar**:
```cmd
uninstall_service.bat
install_service.bat
```

## 📝 Conteúdo do requirements.txt

Se o arquivo não existir, criar com este conteúdo:

```txt
psutil==5.9.5
httpx==0.26.0
```

**Criar arquivo**:
```cmd
cd C:\Coruja\probe
notepad requirements.txt
```

Colar o conteúdo acima e salvar.

## ✅ Verificar Instalação

Após instalar:

```cmd
# Verificar serviço
sc query "Coruja Probe"

# Deve mostrar:
# STATE: 4 RUNNING

# Verificar logs
type probe.log

# Deve mostrar:
# INFO - Coruja Probe started
# INFO - Heartbeat sent successfully
```

## 🎯 Resumo

1. ✅ **Navegar** para pasta correta: `cd C:\Coruja\probe`
2. ✅ **Verificar** arquivos: `dir requirements.txt`
3. ✅ **Executar** instalador: `install_service.bat`
4. ✅ **Verificar** status: `sc query "Coruja Probe"`

---

**Data**: 13/02/2026
**Status**: Scripts corrigidos
**Solução**: Adicionar `cd /d "%~dp0"` nos scripts
