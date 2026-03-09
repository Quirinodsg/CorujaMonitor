# 🦉 Guia de Instalação do Coruja Probe

## Pré-requisitos

- Windows Server 2016+ ou Windows 10+
- Python 3.11 ou superior
- Privilégios de Administrador
- Conectividade de rede com o servidor Coruja Monitor

## Passo 1: Criar um Probe no Dashboard

1. Acesse o dashboard: http://seu-servidor:3000
2. Faça login
3. Vá em **Probes** → **Novo Probe**
4. Digite um nome (ex: "Probe - Servidor Principal")
5. Clique em **Criar**
6. **COPIE O TOKEN** que aparece (você vai precisar dele!)

## Passo 2: Baixar os Arquivos do Probe

Copie toda a pasta `probe` para a máquina que será monitorada:

```
C:\Coruja\probe\
```

## Passo 3: Instalar Python

1. Baixe Python 3.11: https://www.python.org/downloads/
2. Durante a instalação, marque **"Add Python to PATH"**
3. Verifique a instalação:

```cmd
python --version
```

## Passo 4: Instalar Dependências

Abra o PowerShell como Administrador e execute:

```powershell
cd C:\Coruja\probe
pip install -r requirements.txt
```

## Passo 5: Configurar o Probe

Edite o arquivo `probe_config.json`:

```json
{
  "api_url": "http://SEU-SERVIDOR:8000",
  "probe_token": "COLE-O-TOKEN-AQUI",
  "collection_interval": 60,
  "monitored_services": [
    "W3SVC",
    "MSSQLSERVER",
    "Spooler"
  ],
  "udm_targets": [
    "8.8.8.8",
    "1.1.1.1"
  ]
}
```

**Importante:**
- `api_url`: URL do seu servidor Coruja Monitor
- `probe_token`: Token copiado no Passo 1
- `monitored_services`: Lista de serviços Windows para monitorar
- `udm_targets`: IPs para monitorar conectividade (opcional)

## Passo 6: Testar o Probe

Antes de instalar como serviço, teste se está funcionando:

```powershell
cd C:\Coruja\probe
python probe_core.py
```

Você deve ver:
```
Coruja Probe started
Initialized 7 collectors
```

Pressione Ctrl+C para parar.

## Passo 7: Instalar como Serviço Windows

Execute o script de instalação como Administrador:

```powershell
cd C:\Coruja\probe
.\install_service.bat
```

Ou manualmente:

```powershell
python probe_service.py install
python probe_service.py start
```

## Passo 8: Verificar o Serviço

Verifique se o serviço está rodando:

```powershell
sc query CorujaProbe
```

Ou no Gerenciador de Serviços:
1. Win+R → `services.msc`
2. Procure por "Coruja Monitor Probe"
3. Status deve estar "Em execução"

## Passo 9: Verificar no Dashboard

1. Volte ao dashboard
2. Vá em **Probes**
3. Verifique se o probe aparece como "Online"
4. Aguarde alguns minutos para os primeiros dados aparecerem

## Comandos Úteis

### Iniciar o serviço
```cmd
net start CorujaProbe
```

### Parar o serviço
```cmd
net stop CorujaProbe
```

### Reiniciar o serviço
```cmd
net stop CorujaProbe && net start CorujaProbe
```

### Ver logs
```cmd
type C:\Coruja\probe\probe.log
```

### Desinstalar o serviço
```powershell
.\uninstall_service.bat
```

Ou:
```powershell
python probe_service.py stop
python probe_service.py remove
```

## Configurações Avançadas

### Alterar Intervalo de Coleta

Edite `probe_config.json`:
```json
{
  "collection_interval": 30
}
```
(valor em segundos)

### Adicionar Serviços para Monitorar

Edite `probe_config.json`:
```json
{
  "monitored_services": [
    "W3SVC",
    "MSSQLSERVER",
    "Spooler",
    "DNS",
    "DHCP"
  ]
}
```

Para descobrir o nome do serviço:
```powershell
Get-Service | Select-Object Name, DisplayName
```

### Monitorar Links WAN/Internet

Edite `probe_config.json`:
```json
{
  "udm_targets": [
    "8.8.8.8",
    "1.1.1.1",
    "192.168.1.1"
  ]
}
```

## Troubleshooting

### Probe não conecta ao servidor

1. Verifique o firewall:
```powershell
Test-NetConnection -ComputerName SEU-SERVIDOR -Port 8000
```

2. Verifique o token no `probe_config.json`

3. Verifique os logs:
```cmd
type probe.log
```

### Serviço não inicia

1. Verifique se o Python está no PATH:
```cmd
python --version
```

2. Verifique as dependências:
```cmd
pip list
```

3. Execute manualmente para ver erros:
```cmd
python probe_core.py
```

### Métricas não aparecem no dashboard

1. Verifique se o probe está online no dashboard
2. Aguarde 2-3 minutos (tempo de coleta)
3. Verifique os logs do probe
4. Verifique se os sensores foram criados automaticamente

## Múltiplos Servidores

Para monitorar múltiplos servidores:

1. Instale o probe em cada servidor
2. Use o **mesmo token** para todos os servidores do mesmo cliente
3. Ou crie um probe diferente para cada servidor

## Firewall

O probe precisa de:
- **Saída** para o servidor Coruja na porta 8000 (HTTPS)
- Não precisa de portas de entrada

Regra de firewall:
```powershell
New-NetFirewallRule -DisplayName "Coruja Probe" -Direction Outbound -Action Allow -Protocol TCP -RemotePort 8000
```

## Segurança

- O token do probe é sensível - mantenha seguro
- Use HTTPS em produção
- O probe não expõe portas - apenas faz conexões de saída
- Todas as comunicações são autenticadas

## Suporte

- Logs: `C:\Coruja\probe\probe.log`
- Configuração: `C:\Coruja\probe\probe_config.json`
- Documentação: https://github.com/seu-repo/coruja-monitor

---

**Pronto!** Seu servidor agora está sendo monitorado pelo Coruja Monitor! 🦉
