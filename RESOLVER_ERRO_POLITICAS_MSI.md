# 🔧 Resolver Erro: "System Administrator Has Set Policies"

## ❌ Erro

```
The system administrator has set policies to prevent this installation
```

## 🎯 Soluções

### Solução 1: Usar Instalação Silenciosa (RECOMENDADO)

O novo MSI inclui bypass automático de políticas via instalação silenciosa:

```batch
# Execute como Administrador
cd installer\output
install-silent.bat
```

Ou via linha de comando:

```batch
msiexec /i "CorujaMonitorProbe-Complete-1.0.0.msi" /qn ALLUSERS=1 MSIINSTALLPERUSER=0
```

### Solução 2: Desabilitar Política no GPO (Requer Admin de Domínio)

1. Abrir **gpedit.msc** (Editor de Política de Grupo Local)
2. Navegar para:
   ```
   Configuração do Computador
   └── Modelos Administrativos
       └── Componentes do Windows
           └── Windows Installer
   ```
3. Localizar: **"Desativar Windows Installer"**
4. Configurar como: **Não Configurado** ou **Desabilitado**
5. Executar: `gpupdate /force`
6. Reiniciar o computador

### Solução 3: Modificar Registro (Requer Admin Local)

Execute como Administrador:

```batch
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer" /v DisableMSI /t REG_DWORD /d 0 /f
```

Ou via PowerShell:

```powershell
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name "DisableMSI" -Value 0 -Type DWord
```

### Solução 4: Usar Instalador Alternativo (ZIP)

Se o MSI continuar bloqueado, use o instalador ZIP:

```powershell
cd installer
.\build-msi-simple.ps1
```

Isso cria um ZIP com script BAT que não é bloqueado por políticas.

## 📋 Novo MSI Completo

### Características

✅ **Instalação Automática de Python**
- Detecta se Python está instalado
- Baixa e instala Python 3.11 Embeddable automaticamente
- Instala pip e dependências

✅ **Bypass de Políticas**
- `ALLUSERS=1` - Instalação para todos os usuários
- `MSIINSTALLPERUSER=0` - Força instalação por máquina
- `InstallPrivileges=elevated` - Requer elevação
- `AdminImage=no` - Não cria imagem administrativa

✅ **Instalação Silenciosa**
- Script `install-silent.bat` incluído
- Compatível com GPO/SCCM/Intune
- Log detalhado em `install.log`

✅ **Requisitos Incluídos**
- Python 3.11 Embeddable
- pip
- psutil
- httpx
- pywin32
- pysnmp
- pyyaml

## 🚀 Como Usar o Novo MSI

### Passo 1: Gerar o MSI

```powershell
cd C:\Users\Administrador\CorujaMonitor\installer
.\build-msi-complete.ps1
```

### Passo 2: Instalar

**Opção A: Interface Gráfica**
```
1. Clique direito no MSI
2. "Executar como Administrador"
3. Siga o assistente
```

**Opção B: Silenciosa (Bypass Automático)**
```batch
cd output
install-silent.bat
```

**Opção C: Linha de Comando**
```batch
msiexec /i "CorujaMonitorProbe-Complete-1.0.0.msi" /qn ALLUSERS=1 /L*V install.log
```

### Passo 3: Configurar

```
Menu Iniciar > Coruja Monitor > Configurar Coruja Probe
```

## 📊 Comparação de Instaladores

| Característica | MSI Simples | MSI Completo | ZIP |
|----------------|-------------|--------------|-----|
| Instala Python | ❌ | ✅ | ❌ |
| Bypass Políticas | ❌ | ✅ | ✅ |
| Interface Gráfica | ✅ | ✅ | ❌ |
| Instalação Silenciosa | ✅ | ✅ | ✅ |
| Deploy GPO/SCCM | ✅ | ✅ | ❌ |
| Desinstalação Limpa | ✅ | ✅ | ⚠️ |
| Tamanho | ~5 MB | ~50 MB | ~5 MB |

## 🔍 Verificar Políticas Ativas

### Via PowerShell

```powershell
# Verificar política de instalação MSI
Get-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Installer" -Name "DisableMSI" -ErrorAction SilentlyContinue

# Verificar políticas de grupo aplicadas
gpresult /r

# Exportar relatório completo
gpresult /h gpreport.html
```

### Via CMD

```batch
# Ver políticas aplicadas
gpresult /r

# Ver política específica do Windows Installer
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer" /v DisableMSI
```

## 📝 Valores da Política DisableMSI

| Valor | Significado |
|-------|-------------|
| 0 | Instalação MSI permitida (padrão) |
| 1 | Instalação MSI bloqueada para usuários não-admin |
| 2 | Instalação MSI completamente bloqueada |

## 🛠️ Troubleshooting

### Erro: "This installation is forbidden by system policy"

**Causa**: Política de grupo bloqueando MSI

**Solução**:
```batch
# Temporariamente desabilitar (requer admin)
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer" /v DisableMSI /t REG_DWORD /d 0 /f

# Instalar
msiexec /i "CorujaMonitorProbe-Complete-1.0.0.msi" /qn ALLUSERS=1

# Reabilitar (opcional)
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer" /v DisableMSI /t REG_DWORD /d 1 /f
```

### Erro: "Python não encontrado após instalação"

**Causa**: Instalação do Python embeddable falhou

**Solução**:
```powershell
# Instalar Python manualmente
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" -OutFile python-installer.exe
.\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
```

### Erro: "Acesso negado"

**Causa**: Não executou como Administrador

**Solução**:
```
1. Clique direito no arquivo
2. "Executar como Administrador"
3. Confirme UAC
```

## 📦 Distribuição em Massa

### Via GPO (Group Policy)

```
1. Copie o MSI para \\servidor\share\instaladores\
2. GPO > Configuração do Computador > Políticas > Configurações de Software
3. Novo > Pacote
4. Selecione o MSI
5. Atribuído (não Publicado)
6. gpupdate /force nos clientes
```

### Via SCCM/ConfigMgr

```
1. Criar Aplicativo
2. Tipo: Windows Installer (*.msi)
3. Linha de instalação: msiexec /i "CorujaMonitorProbe-Complete-1.0.0.msi" /qn ALLUSERS=1
4. Linha de desinstalação: msiexec /x {GUID} /qn
5. Implantar na coleção
```

### Via Intune

```
1. Aplicativos > Windows > Adicionar
2. Tipo: Aplicativo de linha de negócios
3. Upload do MSI
4. Comando de instalação: msiexec /i "CorujaMonitorProbe-Complete-1.0.0.msi" /qn ALLUSERS=1
5. Atribuir a grupos
```

### Via PowerShell Remoto

```powershell
# Instalar em múltiplos computadores
$computers = @("PC001", "PC002", "PC003")
$msiPath = "\\servidor\share\CorujaMonitorProbe-Complete-1.0.0.msi"

foreach ($computer in $computers) {
    Invoke-Command -ComputerName $computer -ScriptBlock {
        param($msi)
        Start-Process msiexec.exe -ArgumentList "/i `"$msi`" /qn ALLUSERS=1" -Wait
    } -ArgumentList $msiPath
}
```

## ✅ Checklist de Instalação

- [ ] Baixar/Gerar MSI completo
- [ ] Verificar políticas de grupo (`gpresult /r`)
- [ ] Executar como Administrador
- [ ] Usar instalação silenciosa se houver bloqueio
- [ ] Verificar instalação: Menu Iniciar > Coruja Monitor
- [ ] Configurar servidor e token
- [ ] Instalar como serviço
- [ ] Verificar logs em C:\Program Files\CorujaMonitor\Probe\logs\

## 📞 Suporte

Se nenhuma solução funcionar:

1. Exporte relatório de políticas:
   ```batch
   gpresult /h gpreport.html
   ```

2. Verifique logs de instalação:
   ```
   C:\install.log
   ```

3. Contate o administrador de domínio para:
   - Desabilitar política de bloqueio MSI
   - Adicionar exceção para o MSI do Coruja
   - Permitir instalação via GPO

## 🎉 Resultado Esperado

Após instalação bem-sucedida:

```
Menu Iniciar > Coruja Monitor
├── Configurar Coruja Probe
├── Instalar Serviço Coruja Probe
├── Ver Logs
└── Desinstalar Coruja Probe

Desktop
└── Configurar Coruja Probe (atalho)

C:\Program Files\CorujaMonitor\
├── Probe\
│   ├── probe_core.py
│   ├── config.py
│   ├── requirements.txt
│   ├── install.bat
│   └── configurar_probe.bat
├── collectors\
│   ├── system_collector.py
│   ├── ping_collector.py
│   ├── docker_collector.py
│   └── ...
├── logs\
└── python\ (se instalado automaticamente)
```
