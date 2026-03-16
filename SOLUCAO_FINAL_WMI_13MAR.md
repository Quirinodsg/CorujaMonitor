# SOLUÇÃO FINAL WMI - 13 de Março de 2026

## ✅ PROGRESSO ALCANÇADO

### Antes:
```
ERROR: A computer policy does not allow the delegation of the user credentials
```

### Agora:
```
ERROR: Access is denied
```

**Isso é PROGRESSO!** A mensagem de policy sumiu, significa que as políticas CredSSP foram aplicadas com sucesso.

---

## 🎯 PRÓXIMO PASSO: REINICIAR

O erro "Access is denied" sem mensagem de policy indica que as políticas de grupo foram configuradas, mas precisam de reinicialização para entrar em vigor completamente.

### Executar na SRVSONDA001:

```powershell
Restart-Computer -Force
```

### Após reiniciar (2-3 minutos):

1. Conectar via RDP
2. Abrir PowerShell como Admin
3. Testar:

```powershell
$password = ConvertTo-SecureString 'Coruja@2025' -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential('Techbiz\coruja.monitor', $password)
Invoke-Command -ComputerName 192.168.31.110 -Credential $credential -Authentication CredSSP -ScriptBlock { hostname }
```

**Deve retornar:** `SRVHVSPRD010`

4. Iniciar probe: `.\iniciar_probe.bat`
5. Aguardar 1 minuto
6. Verificar logs: `Collected 7 WMI metrics`

---

## 🔄 ALTERNATIVA: Usuário Local

Se após reiniciar ainda não funcionar, usar usuário local do Windows:

### No servidor 192.168.31.110:

```powershell
$password = ConvertTo-SecureString 'Coruja@2025' -AsPlainText -Force
New-LocalUser -Name "corujamonitor" -Password $password -FullName "Coruja Monitor"
Add-LocalGroupMember -Group "Administrators" -Member "corujamonitor"
```

### Atualizar credencial no banco:

Dashboard → Credenciais → Editar "Techbiz":
- Tipo: WMI
- Usuário: `192.168.31.110\corujamonitor`
- Senha: `Coruja@2025`
- Domínio: (vazio)

### Testar:

```powershell
$password = ConvertTo-SecureString 'Coruja@2025' -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential('192.168.31.110\corujamonitor', $password)
Invoke-Command -ComputerName 192.168.31.110 -Credential $credential -ScriptBlock { hostname }
```

Não precisa de `-Authentication CredSSP` com usuário local!

---

## 📊 RESUMO TÉCNICO

### O que foi feito:

1. ✅ Collector WMI atualizado com PowerShell Remoting
2. ✅ Parâmetro `-Authentication CredSSP` adicionado
3. ✅ Políticas de registro CredSSP configuradas:
   - `AllowFreshCredentials = 1`
   - `AllowFreshCredentialsWhenNTLMOnly = 1`
   - `WSMAN/192.168.31.110` adicionado
   - `WSMAN/*` adicionado
4. ✅ `gpupdate /force` executado

### Por que reiniciar?

Group Policy changes geralmente requerem reinicialização para:
- Recarregar LSA (Local Security Authority)
- Atualizar cache de políticas
- Aplicar mudanças no CredSSP provider

### Por que usuário local funciona?

- Não requer delegação de credenciais
- Autenticação direta (não cross-domain)
- Não precisa CredSSP
- Mais simples e seguro para monitoramento

---

## 🎓 LIÇÕES APRENDIDAS

1. **wmic.exe está deprecado** → Use PowerShell Remoting
2. **Workgroup → Domain** requer CredSSP ou usuário local
3. **Group Policy** precisa reinicialização
4. **Usuário local** é mais simples que CredSSP para monitoramento

---

## 📁 ARQUIVOS CRIADOS

| Arquivo | Status |
|---------|--------|
| `CONFIGURAR_CREDSSP_SRVSONDA001.ps1` | ✅ Executado |
| `probe/collectors/wmi_remote_collector.py` | ✅ Atualizado |
| `REINICIAR_SRVSONDA001_AGORA.txt` | ⭐ Próximo passo |

---

## ⏱️ TIMELINE

- **Agora:** Reiniciar SRVSONDA001
- **+3 min:** Testar conexão CredSSP
- **+5 min:** Iniciar probe
- **+6 min:** Verificar logs
- **+7 min:** Verificar dashboard

**OU**

- **Agora:** Criar usuário local no .110
- **+2 min:** Atualizar credencial no banco
- **+3 min:** Reiniciar probe
- **+4 min:** Verificar logs
- **+5 min:** Verificar dashboard

---

**Recomendação:** Tente reiniciar primeiro. Se não funcionar em 10 minutos, use usuário local (mais simples e confiável).

---

**Última atualização:** 13/03/2026 - Kiro AI
