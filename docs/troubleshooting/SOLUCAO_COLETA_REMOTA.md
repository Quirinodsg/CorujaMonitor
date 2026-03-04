# Solução: Coleta Remota Não Funcionando

## Problema Identificado
A sonda local está coletando dados, mas o servidor remoto não está enviando dados.

## Correções Aplicadas

### 1. Melhorias no probe_core.py
- Adicionado logging detalhado para debug
- Melhorado tratamento de exceções com `exc_info=True`
- Corrigido lógica de skip da máquina local (agora verifica hostname E IP)
- Adicionado contador de servidores encontrados
- Melhorado envio de métricas para preservar hostname do servidor remoto

### 2. Script de Debug Criado
Criado `probe/debug_remote.bat` para diagnosticar problemas.

## Como Atualizar a Sonda

### Opção 1: Atualizar Arquivos Manualmente
1. Copie o arquivo `probe_core.py` atualizado para a pasta da sonda
2. Execute como Administrador:
```cmd
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
atualizar_sonda.bat
```

### Opção 2: Reinstalar Serviço
```cmd
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
uninstall_service.bat
install_service.bat
```

## Como Diagnosticar

### Passo 1: Verificar Logs da Sonda
```cmd
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
type probe.log | findstr /i "remote server"
```

Você deve ver linhas como:
```
INFO - Found 2 servers to monitor remotely
INFO - Collecting from remote server: SERVIDOR-REMOTO (192.168.0.100)
INFO - Using WMI for SERVIDOR-REMOTO
INFO - Collected WMI metrics from 192.168.0.100
```

### Passo 2: Executar Debug
```cmd
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe
debug_remote.bat
```

Isso vai mostrar:
- Últimas 50 linhas do log
- Lista de servidores retornados pela API
- Se há servidores configurados para coleta remota

### Passo 3: Verificar Configuração do Servidor Remoto

Na interface web (Gestão > Servidores), verifique:

1. **Servidor está ativo?**
   - is_active = True

2. **Servidor está associado à probe correta?**
   - Deve estar na mesma probe onde a sonda está instalada

3. **Credenciais WMI configuradas?** (para Windows)
   - Usuário WMI: `Administrator` ou `DOMINIO\usuario`
   - Senha WMI: preenchida
   - WMI Habilitado: marcado

4. **Protocolo correto?**
   - Windows: `wmi`
   - Rede/Switch: `snmp`

## Requisitos no Servidor Remoto (Windows)

### Para WMI Funcionar:
1. **Firewall liberado:**
```cmd
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=yes
```

2. **Serviços rodando:**
```cmd
sc config winmgmt start= auto
net start winmgmt
```

3. **Usuário com permissões:**
   - Administrador local OU
   - Membro do grupo "Distributed COM Users" e "Performance Monitor Users"

### Para Máquinas Fora do Domínio:
Se as máquinas não estão no domínio, adicione no servidor remoto:
```cmd
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
```

## Teste Manual de WMI

No servidor onde a sonda está instalada, teste:
```cmd
wmic /node:192.168.0.100 /user:Administrator /password:SuaSenha computersystem get name
```

Se funcionar, o WMI está OK. Se não funcionar, o problema é de rede/firewall/permissões.

## Fluxo de Coleta Remota

```
┌─────────────────┐
│  Sonda Local    │
│  (probe_core)   │
└────────┬────────┘
         │
         │ 1. Busca lista de servidores
         ▼
┌─────────────────┐
│   API           │
│ /probes/servers │
└────────┬────────┘
         │
         │ 2. Retorna servidores + credenciais
         ▼
┌─────────────────┐
│  Sonda Local    │
│  Para cada      │
│  servidor:      │
│  - WMI remoto   │
│  - SNMP remoto  │
│  - PING         │
└────────┬────────┘
         │
         │ 3. Envia métricas
         ▼
┌─────────────────┐
│   API           │
│ /metrics/bulk   │
└─────────────────┘
```

## Checklist de Verificação

- [ ] Sonda atualizada com novo probe_core.py
- [ ] Serviço reiniciado
- [ ] Servidor remoto adicionado na interface
- [ ] Servidor remoto associado à probe correta
- [ ] Credenciais WMI configuradas (se Windows)
- [ ] WMI habilitado no servidor remoto
- [ ] Firewall liberado no servidor remoto
- [ ] Teste manual de WMI funcionando
- [ ] Logs mostram "Found X servers to monitor remotely"
- [ ] Logs mostram "Collecting from remote server"
- [ ] Logs mostram "Collected WMI metrics from"

## Próximos Passos

1. **Atualize a sonda** executando `atualizar_sonda.bat`
2. **Execute o debug** com `debug_remote.bat`
3. **Compartilhe os logs** para análise
4. **Teste WMI manualmente** se necessário

## Alternativa: PING Apenas

Se o WMI não funcionar por enquanto, a sonda ainda vai coletar PING do servidor remoto.
Para isso:
1. Deixe `wmi_enabled = False` no servidor
2. A sonda vai coletar apenas PING (latência e disponibilidade)
3. Você pode habilitar WMI depois quando resolver as permissões

## Suporte

Se após seguir todos os passos ainda não funcionar, compartilhe:
1. Saída do `debug_remote.bat`
2. Últimas 100 linhas do `probe.log`
3. Configuração do servidor na interface (screenshot)
4. Resultado do teste manual de WMI
