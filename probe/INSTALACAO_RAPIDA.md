# 🚀 Instalação Rápida do Coruja Probe

## Passo 1: Instalar Python

1. **Baixe Python 3.11:**
   - Acesse: https://www.python.org/downloads/
   - Clique em "Download Python 3.11.x"

2. **Durante a instalação:**
   - ✅ **IMPORTANTE:** Marque a opção **"Add Python to PATH"**
   - Clique em "Install Now"
   - Aguarde a instalação

3. **Verificar instalação:**
   - Abra um **novo** PowerShell
   - Digite: `python --version`
   - Deve mostrar: `Python 3.11.x`

## Passo 2: Obter Token do Probe

1. Acesse o dashboard: http://seu-servidor:3000
2. Faça login
3. Menu lateral → **Probes**
4. Clique em **+ Novo Probe**
5. Digite um nome (ex: "Servidor Principal")
6. Clique em **Criar Probe**
7. **COPIE O TOKEN** que aparece

## Passo 3: Instalar o Probe

1. **Copie a pasta `probe`** para: `C:\Coruja\probe`

2. **Abra PowerShell como Administrador:**
   - Pressione Win+X
   - Selecione "Windows PowerShell (Admin)"

3. **Execute:**
```powershell
cd C:\Coruja\probe
.\setup_wizard.bat
```

4. **Quando solicitado:**
   - URL do servidor: `http://IP-DO-SERVIDOR:8000`
   - Token: Cole o token copiado

5. **Pronto!** O serviço será instalado automaticamente

## Passo 4: Verificar

```powershell
sc query CorujaProbe
```

Deve mostrar: `STATE: 4 RUNNING`

## Problemas Comuns

### "Python não encontrado"

**Solução:**
1. Reinstale o Python
2. **Marque "Add Python to PATH"**
3. Reinicie o PowerShell
4. Teste: `python --version`

### "Não é possível conectar ao servidor"

**Solução:**
1. Verifique se o servidor está acessível:
```powershell
Test-NetConnection -ComputerName IP-DO-SERVIDOR -Port 8000
```

2. Verifique o firewall
3. Verifique se a URL está correta

### "Serviço não inicia"

**Solução:**
1. Veja os logs:
```cmd
type C:\Coruja\probe\probe.log
```

2. Execute manualmente para ver erros:
```cmd
python C:\Coruja\probe\probe_core.py
```

## Comandos Úteis

```cmd
# Ver status
sc query CorujaProbe

# Iniciar
net start CorujaProbe

# Parar
net stop CorujaProbe

# Reiniciar
net stop CorujaProbe && net start CorujaProbe

# Ver logs
type C:\Coruja\probe\probe.log

# Desinstalar
C:\Coruja\probe\uninstall_service.bat
```

## Suporte

- Logs: `C:\Coruja\probe\probe.log`
- Configuração: `C:\Coruja\probe\probe_config.json`

---

**Dúvidas?** Consulte o administrador do sistema.
