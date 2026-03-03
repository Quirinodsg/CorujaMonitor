# Diagnóstico - Coleta Remota Não Funcionando

## Problema
A sonda local está coletando dados corretamente, mas os dados do servidor remoto não estão chegando.

## Possíveis Causas

### 1. Servidor Remoto Não Configurado na API
- Verificar se o servidor remoto foi adicionado na interface
- Verificar se o servidor está associado à mesma probe
- Verificar se o servidor está ativo (is_active=True)

### 2. Credenciais WMI Não Configuradas
- Servidor remoto precisa ter:
  - `wmi_enabled = True`
  - `wmi_username` preenchido
  - `wmi_password_encrypted` preenchido
  - `wmi_domain` (opcional, se for domínio)

### 3. Firewall no Servidor Remoto
O WMI remoto requer as seguintes portas abertas:
- TCP 135 (RPC Endpoint Mapper)
- TCP 445 (SMB)
- TCP 49152-65535 (Dynamic RPC ports)

### 4. Permissões WMI
O usuário configurado precisa:
- Ser administrador local OU
- Ter permissões WMI específicas
- Ter permissões DCOM

### 5. Configuração Windows no Servidor Remoto
Verificar se está habilitado:
- Serviço "Windows Management Instrumentation" (Winmgmt)
- Compartilhamento administrativo (Admin$, C$)
- Remote Registry (opcional, mas recomendado)

## Como Diagnosticar

### Passo 1: Verificar Logs da Probe
```bash
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
type probe.log | findstr "remote"
```

### Passo 2: Testar Endpoint da API
Execute o script de debug:
```bash
debug_remote.bat
```

Ou manualmente:
```bash
curl -k "https://localhost:8000/api/v1/probes/servers?probe_token=SEU_TOKEN"
```

### Passo 3: Testar WMI Manualmente
No servidor onde a probe está instalada, teste WMI remoto:
```cmd
wmic /node:IP_SERVIDOR_REMOTO /user:USUARIO /password:SENHA computersystem get name
```

Exemplo:
```cmd
wmic /node:192.168.0.100 /user:Administrator /password:SuaSenha computersystem get name
```

### Passo 4: Verificar Configuração no Banco
```sql
SELECT 
    id, hostname, ip_address, monitoring_protocol,
    wmi_enabled, wmi_username, wmi_domain,
    is_active, probe_id
FROM servers
WHERE is_active = 1;
```

## Soluções

### Solução 1: Habilitar WMI Remoto no Servidor
No servidor remoto (Windows), execute como Administrador:
```cmd
REM Habilitar WMI
sc config winmgmt start= auto
net start winmgmt

REM Habilitar Remote Registry
sc config RemoteRegistry start= auto
net start RemoteRegistry

REM Configurar firewall
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=yes
```

### Solução 2: Configurar Credenciais na Interface
1. Acesse Gestão > Servidores
2. Clique em editar (✏️) no servidor remoto
3. Preencha:
   - Usuário WMI: `Administrator` ou `DOMINIO\usuario`
   - Senha WMI: senha do usuário
   - Domínio WMI: nome do domínio (se aplicável)
4. Marque "WMI Habilitado"
5. Salve

### Solução 3: Usar Usuário Local se Não Estiver no Domínio
Se as máquinas não estão no domínio:
1. Crie um usuário administrador local no servidor remoto
2. Use o formato: `NOME_MAQUINA\usuario` ou apenas `usuario`
3. Certifique-se que a senha é a mesma

### Solução 4: Desabilitar UAC para Contas Remotas (Não Recomendado para Produção)
Se estiver usando conta local (não domínio):
```cmd
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
```

## Verificação de Sucesso

Após aplicar as soluções, você deve ver nos logs da probe:
```
INFO - Collected WMI metrics from 192.168.0.100
```

E no dashboard, os sensores do servidor remoto devem aparecer com dados atualizados.

## Alternativa: Usar PING Apenas
Se o WMI não funcionar, a probe ainda coletará PING do servidor remoto automaticamente.
Para ver apenas PING funcionando, deixe `wmi_enabled = False` no servidor.

## Próximos Passos
1. Execute `debug_remote.bat` e compartilhe o resultado
2. Verifique se o servidor remoto aparece na lista retornada pela API
3. Teste WMI manualmente com wmic
4. Verifique os logs da probe para erros específicos
