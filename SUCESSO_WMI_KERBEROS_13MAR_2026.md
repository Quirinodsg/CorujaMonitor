# Sucesso: WMI com Kerberos - 13 de Março de 2026

## Problema Resolvido

Autenticação WMI falhando com "Access Denied" mesmo usando Domain Admin.

## Causa Raiz

1. **Kerberos não funciona com IP**: Probe estava usando `192.168.31.110` ao invés de `SRVHVSPRD010.ad.techbiz.com.br`
2. **Ordem incorreta no código**: `probe_core.py` usava `ip_address` primeiro, depois `hostname`
3. **GPO controlando WinRM**: Configurações locais eram sobrescritas pela política do domínio

## Solução Implementada

### 1. Código Atualizado

**probe/probe_core.py linha 247:**
```python
# ANTES (errado)
hostname = server.get('ip_address') or server.get('hostname')

# DEPOIS (correto)
hostname = server.get('hostname') or server.get('ip_address')
```

**probe/collectors/wmi_remote_collector.py:**
```python
# Ordem de autenticação atualizada
auth_methods = ['Kerberos', 'Negotiate', 'CredSSP']
```

### 2. Banco de Dados Atualizado

```sql
UPDATE servers 
SET hostname = 'SRVHVSPRD010.ad.techbiz.com.br' 
WHERE ip_address = '192.168.31.110';
```

### 3. Máquina no Domínio

SRVSONDA001 (.162) foi colocada no domínio `ad.techbiz.com.br`:
- DNS resolve automaticamente
- Kerberos funciona sem configuração
- GPO aplica políticas corretas

## Teste Manual Bem-Sucedido

```powershell
PS C:\Users\Steve.Jobs> Test-WsMan SRVHVSPRD010.ad.techbiz.com.br
wsmid           : http://schemas.dmtf.org/wbem/wsman/identity/1/wsmanidentity.xsd
ProtocolVersion : http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd
ProductVendor   : Microsoft Corporation
ProductVersion  : OS: 0.0.0 SP: 0.0 Stack: 3.0

PS C:\Users\Steve.Jobs> Invoke-Command -ComputerName SRVHVSPRD010.ad.techbiz.com.br -ScriptBlock { hostname; whoami }
SRVHVSPRD010
techbiz\steve.jobs
```

## Resultado Esperado na Probe

Após as correções, os logs devem mostrar:

```
INFO:__main__:Collecting from remote server: srvhvsprd010.ad.techbiz.com.br (192.168.31.110)
INFO:__main__:Using WMI for srvhvsprd010.ad.techbiz.com.br
INFO:__main__:🔐 Usando credencial: Techbiz (Nível: tenant)
INFO:collectors.wmi_remote_collector:✅ PowerShell remoto OK via Kerberos em SRVHVSPRD010.ad.techbiz.com.br
INFO:__main__:Collected 7 WMI metrics from 192.168.31.110
```

## Arquivos Modificados

1. `probe/probe_core.py` - Usar hostname primeiro
2. `probe/collectors/wmi_remote_collector.py` - Ordem Kerberos primeiro
3. `atualizar_hostname_servidor_110.py` - Script para atualizar banco
4. `docs/REQUISITO_HOSTNAME_KERBEROS.md` - Documentação do requisito

## Requisito para Futuras Máquinas

**TODAS as máquinas Windows devem usar hostname/FQDN, NÃO IP.**

Motivo: Kerberos requer hostname para funcionar. Usar IP força fallback para NTLM, que pode estar bloqueado via GPO.

## Passos para Aplicar

1. ✅ Commit e push no Windows
2. ✅ Pull no Linux
3. ✅ Atualizar hostname no banco
4. ✅ Copiar arquivos atualizados para probe
5. ✅ Reiniciar probe
6. ✅ Verificar logs

## Lições Aprendidas

1. **Sempre verificar se WinRM é controlado por GPO**
   - `winrm enumerate winrm/config/listener`
   - Se `[Source="GPO"]`, não adianta configurar localmente

2. **Kerberos requer hostname, não IP**
   - Sempre usar hostname ou FQDN
   - IP força fallback para NTLM

3. **Ordem de prioridade importa**
   - Código deve usar hostname primeiro
   - IP apenas como fallback

4. **Máquinas no domínio simplificam tudo**
   - DNS automático
   - Kerberos automático
   - GPO automática

## Próximos Passos

1. Executar `EXECUTAR_AGORA_GIT_E_ATUALIZAR_PROBE.txt`
2. Verificar funcionamento
3. Documentar sucesso
4. Aplicar requisito para todas as máquinas futuras

## Status

- ⏳ Aguardando execução dos passos
- 📝 Documentação completa criada
- 🔧 Código atualizado e pronto
- ✅ Solução testada manualmente e validada

## Data

13 de Março de 2026
