# 🚨 AÇÕES URGENTES - Correção de Incidentes

## Problema Identificado

O incidente de PING está aberto mesmo com o sensor OK porque:
1. A probe ainda está conectando no IP antigo (192.168.30.189)
2. O incidente precisa ser fechado manualmente
3. Os serviços precisam ser reiniciados

## ✅ Correções Já Aplicadas

### 1. Worker (`worker/tasks.py`)
- Modificado para fechar incidentes com status 'open' OU 'acknowledged'
- Auto-resolução funciona quando sensor volta ao normal
- Linhas 85-93 implementadas

### 2. NOC (`api/routers/noc.py`)
- Endpoint `/heatmap` agora mostra TODOS os servidores ativos
- Não depende mais de ter incidentes para mostrar servidor
- Calcula disponibilidade real das últimas 24h

### 3. Probe Config (`probe/probe_config.json`)
- IP atualizado de 192.168.30.189 para 192.168.0.41
- Configuração correta

### 4. Script Manual (`api/fechar_incidentes_resolvidos.py`)
- Criado para fechar incidentes já resolvidos
- Verifica última métrica do sensor
- Fecha automaticamente se status = 'ok'

## 🔧 AÇÕES NECESSÁRIAS (Execute Agora)

### Opção 1: Script Automático (RECOMENDADO)

```bash
# Execute este comando:
atualizar_sistema_completo.bat
```

Este script vai:
1. Parar a probe atual
2. Fechar incidentes resolvidos
3. Reiniciar worker
4. Reiniciar API
5. Aguardar serviços ficarem prontos

Depois execute:
```bash
iniciar_probe.bat
```

### Opção 2: Manual (Passo a Passo)

#### Passo 1: Parar a Probe
```bash
# Encontre o processo Python da probe e mate-o
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Coruja*"
```

#### Passo 2: Fechar Incidentes Resolvidos
```bash
docker-compose exec api python fechar_incidentes_resolvidos.py
```

Saída esperada:
```
📋 Encontrados X incidentes ativos
✅ Fechando incidente Y:
   Sensor: PING
   Servidor: DESKTOP-P9VGN04
   Status atual: ok
   ✅ Incidente fechado!
```

#### Passo 3: Reiniciar Worker
```bash
docker-compose restart worker
```

#### Passo 4: Reiniciar API
```bash
docker-compose restart api
```

#### Passo 5: Reiniciar Probe
```bash
iniciar_probe.bat
```

## 📊 Validação

Após executar os passos acima, verifique:

### 1. Incidentes Fechados
- Acesse a interface web
- Verifique que "⚠️ 1 Incidentes Abertos" mudou para "✅ 0 Incidentes"
- Incidente de PING deve estar com status "Resolvido"

### 2. NOC Atualizado
- Servidor DESKTOP-P9VGN04 deve aparecer no NOC
- Status deve ser "OK" (verde)
- Disponibilidade deve estar acima de 95%

### 3. Probe Conectada
- Verifique logs da probe
- Deve conectar em http://192.168.0.41:8000
- Métricas devem ser enviadas com sucesso

### 4. Auto-Resolução Funcionando
Para testar:
1. Crie um incidente de teste (altere threshold temporariamente)
2. Reconheça o incidente
3. Volte o threshold ao normal
4. Aguarde até 60 segundos
5. Incidente deve fechar automaticamente

## 🔄 Funcionamento Automático (Após Correção)

### Auto-Resolução de Incidentes
- Worker verifica sensores a cada 60 segundos
- Se sensor está OK e há incidente aberto/reconhecido:
  - Fecha automaticamente
  - Define status = "resolved"
  - Adiciona nota: "Auto-resolvido: sensor voltou ao normal"

### Atualização de IP
- Probe detecta IP local e público a cada coleta
- Envia nos metadados das métricas
- API compara e atualiza automaticamente se mudou
- Frequência: A cada 60 segundos

### NOC em Tempo Real
- Mostra TODOS os servidores ativos
- Atualiza status baseado em incidentes e métricas
- Calcula disponibilidade real (últimas 24h)
- Não depende de ter incidentes para mostrar servidor

## 📝 Logs para Monitorar

### Worker
```bash
docker-compose logs -f worker
```

Procure por:
- `✅ Incidente X auto-resolvido`
- `⚠️ Incidente X atualizado para critical/warning`

### API
```bash
docker-compose logs -f api
```

Procure por:
- `Server IP updated from X to Y`
- Requisições de métricas sendo recebidas

### Probe
Verifique o terminal onde a probe está rodando:
- `✅ Sent 372 metrics successfully`
- `📡 Heartbeat sent successfully`
- Conectando em `http://192.168.0.41:8000`

## ⚠️ Problemas Conhecidos

### Probe ainda conecta no IP antigo
**Causa**: Processo antigo ainda rodando
**Solução**: Mate o processo e reinicie
```bash
taskkill /F /IM python.exe
iniciar_probe.bat
```

### Incidente não fecha automaticamente
**Causa**: Worker não está rodando ou sensor ainda com problema
**Solução**: 
1. Verifique worker: `docker-compose ps worker`
2. Verifique última métrica do sensor
3. Execute script manual se necessário

### Servidor sumiu do NOC
**Causa**: Servidor marcado como inativo
**Solução**: Verifique `is_active = True` no banco

## 📞 Próximos Passos

Após validar que tudo está funcionando:
1. Monitore por 5 minutos
2. Crie um incidente de teste
3. Reconheça e aguarde auto-resolução
4. Valide que NOC mostra todos os servidores
5. Confirme que IP atualiza automaticamente

---

**Data**: 26/02/2026
**Status**: Correções aplicadas, aguardando execução dos comandos
