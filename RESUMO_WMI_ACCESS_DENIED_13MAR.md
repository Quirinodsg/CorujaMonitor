# Resumo: WMI "Access Denied" - 13/03/2026

## Situação Atual

### ✅ O que está funcionando:
- WMI nativo implementado e integrado
- Bibliotecas `pywin32` e `WMI` instaladas na SRVSONDA001
- Arquivos copiados para produção
- Hostname FQDN configurado: `SRVHVSPRD010.ad.techbiz.com.br`
- Credencial Domain Admin configurada no banco (ID 2)
- Usuário `Techbiz\coruja.monitor` é Domain Admin
- Usuário adicionado ao grupo Administrators local do SRVHVSPRD010

### ❌ O que NÃO está funcionando:
- WMI nativo dá erro "Access denied" ao conectar
- Erro: `<x_wmi: Unexpected COM Error (-2147352567, 'Exception occurred.', (0, 'SWbemLocator', 'Access is denied. ', None, 0, -2147024891), None)>`

## Mudança de Estratégia

### Por que mudamos de PowerShell Remoting para WMI nativo?

**PowerShell Remoting (WinRM):**
- ❌ Requer configuração complexa (GPO controla)
- ❌ Kerberos não funciona com IP
- ❌ Listener configurado via GPO (não podemos alterar)
- ❌ Pode estar bloqueado por política

**WMI Nativo (DCOM/RPC):**
- ✅ Mesma tecnologia do PRTG
- ✅ Funciona automaticamente no domínio
- ✅ Não precisa habilitar WinRM
- ✅ Usa Kerberos automaticamente
- ❌ **MAS** ainda dá "Access denied"

## Possíveis Causas do "Access Denied"

### 1. Permissões DCOM/WMI não configuradas
Mesmo Domain Admin precisa de permissões explícitas no namespace WMI do servidor de destino.

**Solução:** Configurar permissões WMI no SRVHVSPRD010 via `wmimgmt.msc` ou script PowerShell.

### 2. Biblioteca WMI Python ignora credenciais
A biblioteca `wmi` pode ter bug ou limitação que faz ela usar o contexto de segurança atual em vez das credenciais passadas.

**Soluções:**
- Usar `win32com.client` diretamente
- Executar probe como usuário do domínio

### 3. Firewall bloqueando portas dinâmicas
WMI usa porta 135 + portas dinâmicas (RPC).

**Solução:** Verificar conectividade e liberar firewall.

### 4. GPO bloqueando WMI remoto
Política de domínio pode estar bloqueando acesso WMI remoto.

**Solução:** Verificar GPO e criar exceção.

## Próximos Passos

### 1. Diagnóstico (AGORA)
Executar `testar_wmi_nativo_diagnostico.py` na SRVSONDA001 para identificar a causa exata.

### 2. Aplicar Solução
Baseado no diagnóstico, aplicar uma das soluções documentadas em `SOLUCOES_WMI_ACCESS_DENIED.md`.

### 3. Alternativa
Se WMI continuar problemático, considerar usar SNMP (mais simples, funciona em Windows e Linux).

## Arquivos Criados

1. `testar_wmi_nativo_diagnostico.py` - Script de diagnóstico completo
2. `DIAGNOSTICAR_WMI_ACCESS_DENIED_AGORA.txt` - Instruções para executar diagnóstico
3. `SOLUCOES_WMI_ACCESS_DENIED.md` - Documentação de todas as soluções possíveis
4. `RESUMO_WMI_ACCESS_DENIED_13MAR.md` - Este arquivo

## Contexto Técnico

### Erro Detalhado
```
ERROR:collectors.wmi_native_collector:❌ Erro ao conectar WMI nativo em SRVHVSPRD010.ad.techbiz.com.br: 
<x_wmi: Unexpected COM Error (-2147352567, 'Exception occurred.', 
(0, 'SWbemLocator', 'Access is denied. ', None, 0, -2147024891), None)>
```

**Código de erro:** `-2147024891` = `0x80070005` = "Access Denied" (Win32)

### Credenciais Usadas
- Usuário: `Techbiz\coruja.monitor`
- Senha: `Dj8SXoXie!o6Tkc@`
- Domínio: `ad.techbiz.com.br`
- Nível: Domain Admin + Administrators local

### Ambiente
- Probe: SRVSONDA001 (192.168.31.162) - Windows Server no domínio
- Destino: SRVHVSPRD010 (192.168.31.110) - Windows Server no domínio
- Domínio: `ad.techbiz.com.br`

## Teste Manual que Funcionou

```powershell
# PowerShell Remoting funcionou:
Invoke-Command -ComputerName SRVHVSPRD010.ad.techbiz.com.br -ScriptBlock { hostname; whoami }
# Retornou: SRVHVSPRD010 / techbiz\steve.jobs
```

Isso prova que:
- ✅ Kerberos funciona
- ✅ Rede está OK
- ✅ Hostname FQDN resolve
- ✅ Autenticação funciona

**MAS** PowerShell Remoting não é viável porque:
- GPO controla WinRM (Listener [Source="GPO"])
- Não podemos alterar configuração via GPO
- Biblioteca Python para PowerShell Remoting é complexa

## Decisão

Continuar com WMI nativo, mas primeiro **diagnosticar** para identificar a causa exata do "Access denied".

---

**Status:** Aguardando execução do diagnóstico  
**Data:** 13/03/2026 16:30  
**Próxima ação:** Executar `DIAGNOSTICAR_WMI_ACCESS_DENIED_AGORA.txt`
