# Requisito: Hostname para Autenticação Kerberos

## Regra Obrigatória

**TODAS as máquinas Windows adicionadas ao portal DEVEM usar hostname/FQDN, NÃO IP.**

## Por Quê?

### Kerberos não funciona com IP
- Kerberos usa SPN (Service Principal Name) baseado em hostname
- Formato do SPN: `HOST/SRVHVSPRD010.ad.techbiz.com.br`
- Não existe SPN para endereços IP
- Quando usa IP, Windows tenta NTLM como fallback
- Se NTLM está bloqueado via GPO → "Access Denied"

### Benefícios do Hostname
- ✅ Autenticação Kerberos automática
- ✅ Funciona com GPO do domínio
- ✅ Não precisa configurar WinRM manualmente
- ✅ Não precisa CredSSP
- ✅ Não precisa TrustedHosts
- ✅ Segurança melhorada

## Como Adicionar Máquinas Corretamente

### 1. No Portal Web

Ao adicionar servidor Windows:

```
Hostname: SRVHVSPRD010.ad.techbiz.com.br  ✅ CORRETO
IP: 192.168.31.110                         ✅ Pode preencher também

OU

Hostname: SRVHVSPRD010                     ✅ CORRETO (se DNS resolver)
IP: 192.168.31.110                         ✅ Pode preencher também
```

**NUNCA:**
```
Hostname: 192.168.31.110                   ❌ ERRADO
IP: 192.168.31.110
```

### 2. Verificar DNS

Antes de adicionar, verificar se hostname resolve:

```powershell
# Windows
nslookup SRVHVSPRD010.ad.techbiz.com.br
ping SRVHVSPRD010.ad.techbiz.com.br

# Linux
nslookup SRVHVSPRD010.ad.techbiz.com.br
ping -c 4 SRVHVSPRD010.ad.techbiz.com.br
```

### 3. Formato do Hostname

Aceitos:
- `SRVHVSPRD010.ad.techbiz.com.br` (FQDN completo - RECOMENDADO)
- `SRVHVSPRD010` (nome curto - se DNS resolver)

Não aceitos:
- `192.168.31.110` (IP)
- `srv-hvs-prd-010` (formato incorreto)

## Implementação Técnica

### probe_core.py

```python
# IMPORTANTE: Usar hostname primeiro para permitir autenticação Kerberos
# Kerberos NÃO funciona com IP, apenas com hostname/FQDN
hostname = server.get('hostname') or server.get('ip_address')
```

**Ordem de prioridade:**
1. Hostname (permite Kerberos)
2. IP (fallback se hostname não existir)

### wmi_remote_collector.py

```python
# Ordem de autenticação
auth_methods = ['Kerberos', 'Negotiate', 'CredSSP']
```

**Tentativas:**
1. Kerberos (funciona com hostname + Domain Admin)
2. Negotiate (fallback)
3. CredSSP (fallback final)

## Troubleshooting

### Erro: "Access Denied" com Domain Admin

**Causa:** Provavelmente usando IP ao invés de hostname

**Solução:**
1. Verificar campo hostname no banco de dados
2. Atualizar para FQDN se necessário
3. Reiniciar probe

```bash
# Verificar no banco
psql -U postgres -d coruja -c "SELECT id, hostname, ip_address FROM servers WHERE ip_address = '192.168.31.110';"

# Atualizar se necessário
psql -U postgres -d coruja -c "UPDATE servers SET hostname = 'SRVHVSPRD010.ad.techbiz.com.br' WHERE ip_address = '192.168.31.110';"
```

### Erro: "Hostname não resolve"

**Causa:** DNS não configurado ou hostname incorreto

**Solução:**
1. Verificar DNS do domínio
2. Adicionar entrada no DNS se necessário
3. Ou adicionar no arquivo hosts como temporário

```powershell
# Windows (temporário)
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n192.168.31.110    SRVHVSPRD010.ad.techbiz.com.br"
```

```bash
# Linux (temporário)
echo "192.168.31.110    SRVHVSPRD010.ad.techbiz.com.br" >> /etc/hosts
```

## Checklist para Novas Máquinas

- [ ] Hostname está no formato FQDN ou nome curto (não IP)
- [ ] Hostname resolve via DNS
- [ ] Máquina está no domínio (para Kerberos)
- [ ] Credencial Domain Admin configurada
- [ ] WinRM habilitado (geralmente via GPO)
- [ ] Probe atualizada com código que usa hostname primeiro

## Histórico

- **13/03/2026**: Requisito documentado após resolver problema de autenticação Kerberos
- **Problema identificado**: Probe usava IP primeiro, causando falha de Kerberos
- **Solução implementada**: Probe agora usa hostname primeiro, permitindo Kerberos

## Referências

- [Microsoft: Kerberos Authentication](https://docs.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)
- [PowerShell Remoting with Kerberos](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/winrmsecurity)
- Arquivo: `probe/probe_core.py` linha 247
- Arquivo: `probe/collectors/wmi_remote_collector.py` linha 200
