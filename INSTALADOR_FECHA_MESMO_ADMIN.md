# Solução: Instalador Fecha Mesmo Como Admin

## 🔍 Problema

Você está executando como administrador, mas a janela fecha imediatamente.

---

## ✅ SOLUÇÃO IMEDIATA

### Use o Instalador Simples (SEM MENU)

Criamos um instalador que NÃO tem menu e mostra cada passo:

```
probe/install_simples.bat
```

**Como usar:**
1. Clique com botão direito
2. "Executar como administrador"
3. Siga as instruções na tela

---

### Ou Use o Instalador com Debug

Se quiser ver exatamente o que está acontecendo:

```
probe/install_debug.bat
```

Este instalador:
- ✅ Mostra cada passo
- ✅ Aguarda você pressionar tecla entre passos
- ✅ NÃO fecha automaticamente
- ✅ Mostra erros detalhados

---

## 🔧 Por Que Está Fechando?

### Possíveis Causas

1. **Erro de sintaxe no script**
   - Algum comando está falhando
   - Script termina prematuramente

2. **Variável não definida**
   - `%OPCAO%` vazia
   - Script não consegue processar

3. **Comando inválido**
   - Algum comando não existe no seu Windows
   - Versão do Windows diferente

4. **Encoding do arquivo**
   - Arquivo pode ter encoding errado
   - Caracteres especiais causando problema

---

## 🎯 Teste Diagnóstico

Execute este comando no CMD (como Admin):

```batch
cd C:\Coruja Monitor\probe
echo Teste 1: Verificando pasta
dir install*.bat
echo.
echo Teste 2: Verificando privilegios
net session
echo.
echo Teste 3: Testando WMI
wmic computersystem get name
echo.
pause
```

**Se algum desses falhar**, anote qual e me avise.

---

## 📋 Instaladores Disponíveis

### 1. install_simples.bat ⭐ RECOMENDADO
```
probe/install_simples.bat
```
- ✅ SEM menu
- ✅ Direto ao ponto
- ✅ Mostra cada passo
- ✅ Aguarda entre passos
- ✅ NÃO fecha

### 2. install_debug.bat
```
probe/install_debug.bat
```
- ✅ COM menu
- ✅ Debug completo
- ✅ Mostra tudo
- ✅ Aguarda confirmação
- ✅ NÃO fecha

### 3. install.bat (Original)
```
probe/install.bat
```
- ❌ Está fechando
- Não use por enquanto

---

## 🚀 Passo a Passo com Instalador Simples

### 1. Abrir CMD como Admin

```
Win + X → "Prompt de Comando (Admin)"
```

### 2. Ir para pasta probe

```batch
cd "C:\Coruja Monitor\probe"
```

### 3. Executar instalador simples

```batch
install_simples.bat
```

### 4. Seguir instruções

O instalador vai perguntar:
- IP do servidor (digite: `192.168.0.9`)
- Token da probe (cole o token)

### 5. Aguardar conclusão

O instalador vai:
- Criar usuário MonitorUser
- Configurar grupos
- Configurar Firewall
- Configurar DCOM e WMI
- Criar arquivos de configuração
- Testar WMI

---

## 🔍 Debug Manual

Se mesmo assim não funcionar, vamos fazer manualmente:

### Passo 1: Verificar se está na pasta certa

```batch
cd "C:\Coruja Monitor\probe"
dir
```

Deve mostrar:
- install.bat
- install_simples.bat
- install_debug.bat
- probe_core.py
- requirements.txt

### Passo 2: Verificar privilégios

```batch
net session
```

Deve mostrar informações do computador.
Se mostrar "Acesso negado", você NÃO é admin.

### Passo 3: Testar comandos básicos

```batch
REM Testar criação de usuário
net user MonitorUser Test@123 /add

REM Testar WMI
wmic computersystem get name

REM Testar Firewall
netsh advfirewall firewall show rule name=all
```

Se algum desses falhar, anote o erro.

---

## 🆘 Instalação Manual (Última Opção)

Se nenhum instalador funcionar, faça manualmente:

### 1. Criar Usuário

```batch
net user MonitorUser Monitor@12345 /add /comment:"Usuario para monitoramento" /passwordchg:no /expires:never /active:yes
wmic useraccount where "name='MonitorUser'" set PasswordExpires=FALSE
```

### 2. Adicionar aos Grupos

```batch
net localgroup "Administradores" MonitorUser /add
net localgroup "Administrators" MonitorUser /add
```

### 3. Configurar Firewall

```batch
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
netsh advfirewall firewall add rule name="WMI-In-TCP" dir=in action=allow protocol=TCP localport=135
```

### 4. Configurar DCOM

```batch
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f
```

### 5. Criar wmi_credentials.json

Abra Notepad e crie arquivo `wmi_credentials.json`:

```json
{
  "SEU-COMPUTADOR": {
    "username": "MonitorUser",
    "password": "Monitor@12345",
    "domain": "SEU-COMPUTADOR"
  }
}
```

Substitua `SEU-COMPUTADOR` pelo nome do seu computador.

### 6. Criar probe_config.json

Abra Notepad e crie arquivo `probe_config.json`:

```json
{
  "api_url": "http://192.168.0.9:8000",
  "probe_token": "SEU_TOKEN_AQUI",
  "collection_interval": 60,
  "log_level": "INFO"
}
```

Substitua `SEU_TOKEN_AQUI` pelo token da interface web.

### 7. Testar

```batch
wmic computersystem get name,domain
```

---

## 📊 Checklist de Troubleshooting

- [ ] Está executando como Administrador?
- [ ] Está na pasta correta? (`C:\Coruja Monitor\probe`)
- [ ] Arquivos .bat existem na pasta?
- [ ] Comando `net session` funciona?
- [ ] Comando `wmic` funciona?
- [ ] Windows está atualizado?
- [ ] Antivírus está bloqueando?

---

## 💡 Dicas

### Se Antivírus Bloquear

1. Adicione exceção para pasta `C:\Coruja Monitor`
2. Desabilite temporariamente
3. Execute instalador
4. Reabilite antivírus

### Se Windows Defender Bloquear

1. Windows Security → Proteção contra vírus e ameaças
2. Gerenciar configurações
3. Adicionar exclusão → Pasta
4. Adicione: `C:\Coruja Monitor`

### Se UAC Bloquear

1. Painel de Controle → Contas de Usuário
2. Alterar Configurações de Controle de Conta de Usuário
3. Mova para "Nunca notificar" (temporariamente)
4. Execute instalador
5. Volte configuração original

---

## 🎯 Resumo das Opções

### Opção 1: Instalador Simples (RECOMENDADO)
```batch
cd "C:\Coruja Monitor\probe"
install_simples.bat
```

### Opção 2: Instalador Debug
```batch
cd "C:\Coruja Monitor\probe"
install_debug.bat
```

### Opção 3: Instalação Manual
Siga os passos da seção "Instalação Manual" acima

---

## 📞 Informações para Suporte

Se nada funcionar, anote:

1. **Versão do Windows**: `winver`
2. **Privilégios**: Resultado de `net session`
3. **WMI funciona**: Resultado de `wmic computersystem get name`
4. **Pasta atual**: Resultado de `cd`
5. **Arquivos na pasta**: Resultado de `dir`
6. **Erro exato**: Tire print da tela

---

**Tente primeiro `install_simples.bat` - é o mais confiável!** 🚀
