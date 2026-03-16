# RESUMO: Resolver CredSSP para WMI Remoto
**Data:** 13 de Março de 2026  
**Problema:** Group Policy bloqueando delegação de credenciais CredSSP

---

## 🎯 OBJETIVO

Permitir que a SRVSONDA001 (Workgroup) colete métricas WMI do SRVHVSPRD010 (Domain) usando PowerShell Remoting com CredSSP.

---

## 📊 SITUAÇÃO ATUAL

### ✅ O QUE JÁ ESTÁ FUNCIONANDO

1. **WinRM habilitado** no servidor 192.168.31.110
2. **CredSSP habilitado** no servidor (.110) e cliente (.162)
3. **TrustedHosts configurado** na SRVSONDA001
4. **Credencial WMI** criada no banco (ID: 2, Techbiz\coruja.monitor)
5. **Probe reconhecendo credencial** do banco via API
6. **Collector PowerShell** implementado (substitui wmic.exe deprecado)

### ❌ PROBLEMA ATUAL

```
[192.168.31.110] Connecting to remote server 192.168.31.110 failed with the following error message:
The WinRM client cannot process the request. A computer policy does not allow the delegation of the user 
credentials to the target computer because the computer is not trusted.
```

**Causa:** Group Policy na SRVSONDA001 bloqueando delegação CredSSP

---

## 🔧 SOLUÇÃO

### PASSO 1: Configurar Group Policy na SRVSONDA001

**Arquivo:** `CONFIGURAR_CREDSSP_SRVSONDA001.ps1`

**O que faz:**
- Cria chaves de registro em `HKLM:\SOFTWARE\Policies\Microsoft\Windows\CredentialsDelegation`
- Habilita `AllowFreshCredentials` e `AllowFreshCredentialsWhenNTLMOnly`
- Adiciona `WSMAN/192.168.31.110` e `WSMAN/*` às políticas
- Aplica com `gpupdate /force`
- Testa conexão automaticamente

**Como executar:**
1. Copiar script para SRVSONDA001 via RDP
2. Executar PowerShell como Administrador
3. Executar: `.\CONFIGURAR_CREDSSP_SRVSONDA001.ps1`
4. Se falhar, reiniciar máquina: `Restart-Computer -Force`

### PASSO 2: Atualizar Collector WMI

**Arquivo:** `probe/collectors/wmi_remote_collector.py`

**Mudança:** Adicionar `-Authentication CredSSP` ao `Invoke-Command`

```powershell
Invoke-Command -ComputerName {hostname} -Credential $credential -Authentication CredSSP -ScriptBlock { ... }
```

**Como aplicar:**
1. Copiar arquivo atualizado via RDP para:
   `C:\Program Files\CorujaMonitor\Probe\collectors\wmi_remote_collector.py`
2. Reiniciar probe

### PASSO 3: Verificar Funcionamento

**Logs esperados:**
```
INFO:__main__:🔐 Usando credencial: Techbiz (Nível: tenant)
INFO:__main__:Collected 7 WMI metrics from 192.168.31.110
```

**Dashboard:** Sensores do SRVHVSPRD010 devem mostrar valores (não "Unknown")

---

## 📁 ARQUIVOS CRIADOS/MODIFICADOS

| Arquivo | Status | Descrição |
|---------|--------|-----------|
| `CONFIGURAR_CREDSSP_SRVSONDA001.ps1` | ✅ Novo | Script para configurar políticas CredSSP |
| `probe/collectors/wmi_remote_collector.py` | ✅ Atualizado | Adicionado `-Authentication CredSSP` |
| `RESOLVER_CREDSSP_COMPLETO_AGORA.txt` | ✅ Novo | Instruções passo a passo |
| `COPIAR_WMI_COLLECTOR_POWERSHELL_AGORA.txt` | ✅ Atualizado | Instruções de cópia |

---

## 🔍 TROUBLESHOOTING

### Se ainda der "Access Denied" após configurar:

1. **Reiniciar SRVSONDA001:**
   ```powershell
   Restart-Computer -Force
   ```

2. **Verificar CredSSP no servidor .110:**
   ```powershell
   Get-WSManCredSSP
   # Deve mostrar: "This computer is configured to receive credentials"
   ```

3. **Verificar TrustedHosts:**
   ```powershell
   Get-Item WSMan:\localhost\Client\TrustedHosts
   # Deve conter: 192.168.31.110
   ```

4. **Testar manualmente:**
   ```powershell
   $password = ConvertTo-SecureString 'Coruja@2025' -AsPlainText -Force
   $credential = New-Object System.Management.Automation.PSCredential('Techbiz\coruja.monitor', $password)
   Invoke-Command -ComputerName 192.168.31.110 -Credential $credential -Authentication CredSSP -ScriptBlock { hostname }
   ```

### Alternativa: Usuário Local

Se CredSSP não funcionar, criar usuário local no .110:

```powershell
# No servidor .110
$password = ConvertTo-SecureString 'Coruja@2025' -AsPlainText -Force
New-LocalUser -Name "corujamonitor" -Password $password -FullName "Coruja Monitor"
Add-LocalGroupMember -Group "Administrators" -Member "corujamonitor"
```

Atualizar credencial no banco para usar `192.168.31.110\corujamonitor`

---

## 📋 CHECKLIST DE EXECUÇÃO

- [ ] Copiar `CONFIGURAR_CREDSSP_SRVSONDA001.ps1` para SRVSONDA001
- [ ] Executar script como Administrador
- [ ] Verificar teste automático (deve retornar Caption do Windows)
- [ ] Se falhar, reiniciar SRVSONDA001
- [ ] Copiar `wmi_remote_collector.py` atualizado para SRVSONDA001
- [ ] Reiniciar probe
- [ ] Aguardar 1 minuto
- [ ] Verificar logs (deve mostrar "Collected 7 WMI metrics")
- [ ] Verificar dashboard (sensores devem ter valores)

---

## 🎓 CONTEXTO TÉCNICO

### Por que CredSSP?

**Cenário:**
- SRVSONDA001 (192.168.31.162) = WORKGROUP
- SRVHVSPRD010 (192.168.31.110) = DOMAIN (Techbiz)

**Problema:** Autenticação Workgroup → Domain requer delegação de credenciais

**Solução:** CredSSP (Credential Security Support Provider)
- Permite delegação segura de credenciais
- Necessário para "double-hop" authentication
- Requer configuração de Group Policy

### Por que PowerShell Remoting?

- `wmic.exe` foi deprecado pela Microsoft
- PowerShell Remoting (WinRM) é a solução moderna
- Suporta CredSSP, Kerberos, NTLM
- Porta 5985 (HTTP) ou 5986 (HTTPS)

---

## 📞 PRÓXIMOS PASSOS

1. Executar `CONFIGURAR_CREDSSP_SRVSONDA001.ps1`
2. Copiar collector atualizado
3. Reiniciar probe
4. Verificar coleta de métricas WMI

**Tempo estimado:** 10-15 minutos (incluindo possível reinicialização)

---

**Última atualização:** 13/03/2026 - Kiro AI
