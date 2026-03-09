# Coruja Monitor Probe

Agente de monitoramento para Windows que coleta métricas e envia para o servidor Coruja Monitor.

## 🎯 NOVO: Instalador com Auto-Start

**Agora temos um instalador que inicia a probe automaticamente!**

### Instalador Completo (RECOMENDADO)

```batch
# Execute como Administrador (botão direito → Executar como administrador)
install_completo_com_servico.bat
```

**Vantagens**:
- ✅ Detecta usuário atual automaticamente
- ✅ Configura tudo (Firewall, DCOM, WMI)
- ✅ Instala dependências Python
- ✅ Inicia probe imediatamente
- ✅ Configura auto-start com Windows
- ✅ Não precisa deixar janela aberta!

**Verificar instalação**:
```batch
verificar_instalacao.bat
```

---

## 🚀 Instalação Rápida

### 1. Obter o Token do Probe

No dashboard do Coruja Monitor:
1. Vá em **Probes** → **Novo Probe**
2. Digite um nome
3. **Copie o token** gerado

### 2. Baixar e Instalar

1. Copie a pasta `probe` para a máquina Windows
2. Abra PowerShell **como Administrador**
3. Execute:

```powershell
cd C:\caminho\para\probe
.\setup_wizard.bat
```

4. Siga as instruções:
   - Digite a URL do servidor (ex: `http://192.168.1.100:8000`)
   - Cole o token do probe
   - Aguarde a instalação

### 3. Verificar

```cmd
sc query CorujaProbe
```

Deve mostrar: `STATE: 4 RUNNING`

## 📊 O que é Monitorado

- ✅ CPU (uso por core e total)
- ✅ Memória (total, usado, disponível)
- ✅ Disco (todas as partições)
- ✅ Rede (throughput, pacotes, erros)
- ✅ Serviços Windows (status, auto-restart)
- ✅ Hyper-V (VMs, status)
- ✅ Links WAN/Internet (ping, latência)

## 🔧 Configuração

Edite `probe_config.json`:

```json
{
  "api_url": "http://seu-servidor:8000",
  "probe_token": "seu-token-aqui",
  "collection_interval": 60,
  "monitored_services": [
    "W3SVC",
    "MSSQLSERVER",
    "Spooler"
  ],
  "udm_targets": [
    "8.8.8.8"
  ]
}
```

Após alterar, reinicie o serviço:
```cmd
net stop CorujaProbe && net start CorujaProbe
```

## 📝 Comandos Úteis

```cmd
# Iniciar
net start CorujaProbe

# Parar
net stop CorujaProbe

# Reiniciar
net stop CorujaProbe && net start CorujaProbe

# Ver status
sc query CorujaProbe

# Ver logs
type probe.log

# Desinstalar (mantém código)
desinstalar_probe.bat

# Desinstalar tudo (remove código)
desinstalar_tudo.bat
```

---

## 🗑️ Desinstalação

### Desinstalação Padrão (Recomendado)
```batch
# Remove configurações mas mantém código
desinstalar_probe.bat
```

Remove:
- Tarefa agendada
- Processo rodando
- Configurações
- Logs

Mantém:
- Código fonte
- Coletores
- Instaladores

**Use para**: Reconfigurar ou reinstalar

### Desinstalação Completa
```batch
# Remove TUDO incluindo código
desinstalar_tudo.bat
```

Remove:
- Tudo da desinstalação padrão
- Código fonte
- Coletores
- Dependências

**Use para**: Remover completamente

Veja `GUIA_DESINSTALACAO.md` para detalhes.

## 🔍 Troubleshooting

### Probe não conecta

1. Verifique a URL no `probe_config.json`
2. Teste conectividade:
```powershell
Test-NetConnection -ComputerName SEU-SERVIDOR -Port 8000
```

3. Verifique o firewall
4. Verifique os logs: `type probe.log`

### Serviço não inicia

1. Verifique se Python está instalado: `python --version`
2. Reinstale dependências: `pip install -r requirements.txt`
3. Execute manualmente para ver erros: `python probe_core.py`

### Métricas não aparecem

1. Aguarde 2-3 minutos
2. Verifique se o probe está "Online" no dashboard
3. Verifique os logs do probe

## 📖 Documentação Completa

Veja [INSTALACAO.md](INSTALACAO.md) para instruções detalhadas.

## 🔐 Segurança

- Token é criptografado
- Apenas conexões de saída (não expõe portas)
- Comunicação HTTPS em produção
- Logs auditáveis

## 💡 Dicas

- Use um probe por cliente/localização
- Configure serviços específicos para monitorar
- Ajuste `collection_interval` conforme necessário (padrão: 60s)
- Monitore links críticos com `udm_targets`

---

**Suporte**: Veja os logs em `probe.log` ou contate o administrador do sistema.
