# STATUS ATUAL - CredSSP WMI
**Data:** 13 de Março de 2026  
**Hora:** Agora

---

## ✅ O QUE JÁ ESTÁ PRONTO

1. **Collector WMI atualizado** com `-Authentication CredSSP`
   - Arquivo: `probe/collectors/wmi_remote_collector.py`
   - Linha 283: `Invoke-Command ... -Authentication CredSSP`

2. **WinRM habilitado** no servidor 192.168.31.110

3. **CredSSP habilitado** no servidor (.110) e cliente (.162)

4. **TrustedHosts configurado** na SRVSONDA001

5. **Credencial WMI** funcionando (Techbiz\coruja.monitor)

6. **Probe reconhecendo credencial** do banco via API

---

## ❌ PROBLEMA ATUAL

```
ERROR: The WinRM client cannot process the request. 
A computer policy does not allow the delegation of the user credentials
```

**Causa:** Group Policy na SRVSONDA001 bloqueando delegação CredSSP

**Solução:** Executar script de configuração de políticas

---

## 🎯 PRÓXIMO PASSO (ÚNICO)

### Executar na SRVSONDA001 (192.168.31.162)

**Arquivo:** `COMECE_AQUI_CREDSSP_URGENTE.txt`

**Ação:**
1. Abrir PowerShell como Administrador
2. Copiar e colar o código do arquivo
3. Aguardar teste automático
4. Se falhar, reiniciar máquina
5. Reiniciar probe

**Tempo estimado:** 5 minutos (ou 10 se precisar reiniciar)

---

## 📊 LOGS ATUAIS

```
INFO:__main__:Using WMI for srvhvsprd010
INFO:__main__:🔐 Usando credencial: Techbiz (Nível: tenant)
ERROR:collectors.wmi_remote_collector:Erro PowerShell: [192.168.31.110] 
  The WinRM client cannot process the request. 
  A computer policy does not allow the delegation...
```

**Análise:**
- ✅ Probe encontrando servidor
- ✅ Credencial sendo carregada do banco
- ✅ Tentando conectar via WMI
- ❌ Group Policy bloqueando

---

## 🔧 O QUE O SCRIPT FAZ

1. Cria chaves de registro em:
   ```
   HKLM:\SOFTWARE\Policies\Microsoft\Windows\CredentialsDelegation
   ```

2. Habilita políticas:
   - `AllowFreshCredentials = 1`
   - `AllowFreshCredentialsWhenNTLMOnly = 1`

3. Adiciona servidores permitidos:
   - `WSMAN/192.168.31.110`
   - `WSMAN/*` (wildcard)

4. Aplica com `gpupdate /force`

5. Testa conexão automaticamente

---

## ✅ RESULTADO ESPERADO

### Após executar o script:

**Teste manual deve funcionar:**
```powershell
$password = ConvertTo-SecureString 'Coruja@2025' -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential('Techbiz\coruja.monitor', $password)
Invoke-Command -ComputerName 192.168.31.110 -Credential $credential -Authentication CredSSP -ScriptBlock { hostname }

# Deve retornar: SRVHVSPRD010
```

**Logs da probe:**
```
INFO:__main__:🔐 Usando credencial: Techbiz (Nível: tenant)
INFO:__main__:Collected 7 WMI metrics from 192.168.31.110
INFO:__main__:Sent 11 metrics successfully
```

**Dashboard:**
- CPU Usage: ~X%
- Memory Usage: ~X%
- Disk C:: ~X%
- Uptime: X days
- Network In/Out: X Mbps

---

## 🚨 SE NÃO FUNCIONAR

### Opção 1: Reiniciar máquina
```powershell
Restart-Computer -Force
```

Após reiniciar, testar novamente.

### Opção 2: Usar usuário local (alternativa)

Criar usuário local no servidor .110:
```powershell
# No servidor 192.168.31.110
$password = ConvertTo-SecureString 'Coruja@2025' -AsPlainText -Force
New-LocalUser -Name "corujamonitor" -Password $password
Add-LocalGroupMember -Group "Administrators" -Member "corujamonitor"
```

Atualizar credencial no banco:
- Usuário: `192.168.31.110\corujamonitor`
- Domínio: (vazio)

---

## 📁 ARQUIVOS CRIADOS

| Arquivo | Descrição |
|---------|-----------|
| `COMECE_AQUI_CREDSSP_URGENTE.txt` | ⭐ Executar este agora |
| `CONFIGURAR_CREDSSP_SRVSONDA001.ps1` | Script completo |
| `EXECUTAR_AGORA_CREDSSP.txt` | Versão simplificada |
| `RESOLVER_CREDSSP_COMPLETO_AGORA.txt` | Instruções detalhadas |
| `RESUMO_CREDSSP_13MAR_2026.md` | Documentação completa |

---

## 🎓 CONTEXTO TÉCNICO

**Por que CredSSP?**
- SRVSONDA001 = Workgroup
- SRVHVSPRD010 = Domain (Techbiz)
- Autenticação cross-domain requer delegação de credenciais
- CredSSP permite "double-hop" authentication

**Por que Group Policy?**
- Windows bloqueia delegação por padrão (segurança)
- Precisa autorizar explicitamente via políticas
- Configuração via registro ou gpedit.msc

---

## ⏱️ TIMELINE

1. **Agora:** Executar script na SRVSONDA001
2. **+2 min:** Testar conexão manual
3. **+3 min:** Reiniciar probe
4. **+4 min:** Verificar logs
5. **+5 min:** Verificar dashboard

**Total:** 5 minutos até WMI funcionando

---

## 📞 SUPORTE

Se após executar o script e reiniciar a máquina ainda não funcionar:

1. Verificar Event Viewer na SRVSONDA001:
   - Applications and Services Logs
   - Microsoft → Windows → WinRM → Operational

2. Verificar firewall no servidor .110:
   - Porta 5985 (WinRM HTTP)

3. Considerar alternativa de usuário local

---

**Última atualização:** 13/03/2026 - Kiro AI  
**Próxima ação:** Executar `COMECE_AQUI_CREDSSP_URGENTE.txt`
