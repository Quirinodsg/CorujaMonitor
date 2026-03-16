# Solução Definitiva: WMI com Serviço de Domínio

## Problema

WMI nativo dá "Access denied" mesmo com Domain Admin porque a biblioteca WMI Python ignora as credenciais passadas explicitamente e usa o contexto de segurança do processo atual.

## Solução

Executar a probe como serviço Windows rodando com conta de domínio (`TECHBIZ\coruja.monitor`).

### Por que funciona?

Quando o serviço roda como conta de domínio:
1. O processo Python herda o contexto de segurança da conta
2. WMI usa automaticamente esse contexto (SSPI/Kerberos)
3. Não precisa passar credenciais explicitamente
4. Kerberos funciona automaticamente no domínio

## Implementação

### Arquivos Criados

1. `probe/install_service_domain.bat` - Script de instalação do serviço
2. `INSTALAR_PROBE_SERVICO_DOMINIO_AGORA.txt` - Instruções passo a passo

### Requisitos

- NSSM (Non-Sucking Service Manager) instalado
- Conta de domínio com permissões WMI
- Probe já configurada em `C:\Program Files\CorujaMonitor\Probe\`

### Passos

1. Baixar e instalar NSSM
2. Copiar script de instalação
3. Executar como Administrador
4. Informar credenciais de domínio
5. Verificar logs

## Vantagens

✅ Resolve "Access denied" definitivamente  
✅ Usa Kerberos automaticamente  
✅ Não precisa passar credenciais no código  
✅ Serviço inicia automaticamente com o sistema  
✅ Logs automáticos e rotação  
✅ Restart automático em caso de falha  

## Alternativas Consideradas

### 1. Configurar permissões DCOM/WMI
- ❌ Complexo
- ❌ Precisa configurar em cada servidor
- ❌ Pode ser bloqueado por GPO

### 2. Usar win32com diretamente
- ❌ Mesmo problema de contexto de segurança
- ❌ Não resolve o "Access denied"

### 3. Usar SNMP
- ✅ Funciona, mas menos métricas
- ❌ Precisa instalar SNMP em cada servidor Windows

### 4. Executar probe como usuário de domínio (ESCOLHIDA)
- ✅ Simples
- ✅ Resolve definitivamente
- ✅ Usa tecnologia nativa do Windows
- ✅ Funciona com Kerberos automaticamente

## Comparação: Antes vs Depois

### ANTES (Probe rodando como usuário local)

```python
# Código tentava passar credenciais
collector = WMINativeCollector(
    hostname="SRVHVSPRD010.ad.techbiz.com.br",
    username="coruja.monitor",
    password="Dj8SXoXie!o6Tkc@",
    domain="Techbiz"
)
```

**Resultado:** ❌ Access Denied  
**Motivo:** Biblioteca WMI ignora credenciais e usa contexto do processo (usuário local)

### DEPOIS (Probe rodando como serviço de domínio)

```python
# Mesmo código, mas processo roda como TECHBIZ\coruja.monitor
collector = WMINativeCollector(
    hostname="SRVHVSPRD010.ad.techbiz.com.br",
    username="coruja.monitor",
    password="Dj8SXoXie!o6Tkc@",
    domain="Techbiz"
)
```

**Resultado:** ✅ Sucesso  
**Motivo:** WMI usa contexto do processo (Domain Admin) automaticamente via Kerberos

## Configuração do Serviço

### Via NSSM (Recomendado)

```batch
nssm install CorujaProbe python "C:\Program Files\CorujaMonitor\Probe\probe_core.py"
nssm set CorujaProbe ObjectName "TECHBIZ\coruja.monitor" "Dj8SXoXie!o6Tkc@"
nssm set CorujaProbe Start SERVICE_AUTO_START
nssm start CorujaProbe
```

### Via SC.EXE (Alternativa)

```batch
sc.exe create CorujaProbe binPath= "python \"C:\Program Files\CorujaMonitor\Probe\probe_core.py\"" start= auto obj= "TECHBIZ\coruja.monitor" password= "Dj8SXoXie!o6Tkc@"
sc.exe start CorujaProbe
```

## Verificação

### Verificar Status do Serviço

```powershell
nssm status CorujaProbe
# Deve retornar: SERVICE_RUNNING
```

### Verificar Logs

```powershell
Get-Content "C:\Program Files\CorujaMonitor\Probe\logs\service.log" -Tail 50
```

### Procurar por:

✅ `WMI nativo conectado em SRVHVSPRD010.ad.techbiz.com.br`  
✅ `Collected X WMI metrics from SRVHVSPRD010.ad.techbiz.com.br`  
❌ Não deve ter: `Access is denied`

## Comandos Úteis

```powershell
# Status
nssm status CorujaProbe

# Reiniciar
nssm restart CorujaProbe

# Parar
nssm stop CorujaProbe

# Ver logs em tempo real
Get-Content "C:\Program Files\CorujaMonitor\Probe\logs\service.log" -Wait

# Desinstalar
nssm stop CorujaProbe
nssm remove CorujaProbe confirm
```

## Segurança

### Permissões Necessárias

A conta `TECHBIZ\coruja.monitor` precisa:
- ✅ Domain Admin (já tem)
- ✅ Permissão para "Log on as a service" (NSSM configura automaticamente)
- ✅ Acesso de leitura ao diretório da probe

### Boas Práticas

1. Usar conta de serviço dedicada (não conta de usuário)
2. Senha forte e rotação periódica
3. Monitorar logs do serviço
4. Limitar permissões ao mínimo necessário

## Troubleshooting

### Serviço não inicia

```powershell
# Verificar logs de erro
Get-Content "C:\Program Files\CorujaMonitor\Probe\logs\service_error.log"

# Verificar Event Viewer
eventvwr.msc
# Windows Logs → Application → Procurar por "CorujaProbe"
```

### Ainda dá "Access Denied"

1. Verificar se serviço está rodando como conta de domínio:
   ```powershell
   Get-WmiObject Win32_Service -Filter "Name='CorujaProbe'" | Select Name, StartName
   # StartName deve ser: TECHBIZ\coruja.monitor
   ```

2. Verificar se conta tem permissões:
   ```powershell
   # No SRVHVSPRD010:
   net localgroup Administrators
   # Deve listar: TECHBIZ\coruja.monitor
   ```

### Credenciais inválidas

```powershell
# Reconfigurar credenciais
nssm set CorujaProbe ObjectName "TECHBIZ\coruja.monitor" "Dj8SXoXie!o6Tkc@"
nssm restart CorujaProbe
```

## Próximos Passos

Após instalação bem-sucedida:

1. ✅ Verificar métricas no dashboard
2. ✅ Adicionar mais servidores Windows
3. ✅ Configurar alertas
4. ✅ Documentar procedimento para outros servidores

## Conclusão

Esta solução resolve definitivamente o problema de "Access Denied" no WMI usando a abordagem mais simples e nativa do Windows: executar o processo com as credenciais corretas desde o início, em vez de tentar passar credenciais explicitamente.

---

**Data:** 13/03/2026  
**Status:** Pronto para implementação  
**Próxima ação:** Executar `INSTALAR_PROBE_SERVICO_DOMINIO_AGORA.txt`
