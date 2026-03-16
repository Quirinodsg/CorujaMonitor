# 🎯 SOLUÇÃO COMPLETA: PING Direto do Servidor Linux

**Implementado em**: 11 Março 2026  
**Status**: ✅ Funcionando (pendente limpeza de duplicados)  
**Commit Git**: 98a8c92

---

## 📋 RESUMO EXECUTIVO

Sistema de PING implementado direto no servidor Linux (SRVCMONITOR001), funcionando de forma automática e independente da probe Windows, igual ao PRTG.

### O Que Foi Feito

1. ✅ Task Celery no worker executando PING a cada 60s
2. ✅ Função `execute_ping()` usando comando nativo do Linux
3. ✅ Criação automática de sensores PING
4. ✅ Coluna `updated_at` adicionada na tabela sensors
5. ✅ Pacote `iputils-ping` instalado no container worker
6. ✅ API corrigida (não cria mais PING automaticamente)
7. ✅ Código commitado e enviado para Git
8. ✅ Servidor Linux atualizado

### O Que Falta

- ⏳ Deletar sensores PING duplicados (IDs 35 e 37)
- ⏳ Reiniciar frontend
- ⏳ Limpar cache do navegador
- ⏳ Testar adicionando servidor novo

---

## 🏗️ ARQUITETURA

### Antes (Problema)

```
┌─────────────────────────────────────┐
│  PROBE WINDOWS (SRVSONDA001)        │
│  - Coleta métricas WMI/SNMP         │
│  - Coleta PING ❌                    │
│  - Envia tudo para API              │
└─────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  SERVIDOR LINUX (SRVCMONITOR001)    │
│  - API recebe métricas              │
│  - Cria sensor PING na API ❌        │
│  - Duplicação de sensores ❌         │
└─────────────────────────────────────┘
```

### Depois (Solução)

```
┌─────────────────────────────────────┐
│  SERVIDOR LINUX (SRVCMONITOR001)    │
│  ┌───────────────────────────────┐  │
│  │  WORKER (Celery)              │  │
│  │  - ping_all_servers() 60s ✅  │  │
│  │  - execute_ping() Linux ✅    │  │
│  │  - Cria sensor auto ✅        │  │
│  │  - Atualiza métricas ✅       │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  API                          │  │
│  │  - NÃO cria PING ✅           │  │
│  │  - Recebe métricas WMI/SNMP   │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
           ▲
           │ WMI/SNMP (sem PING)
           │
┌─────────────────────────────────────┐
│  PROBE WINDOWS (SRVSONDA001)        │
│  - Coleta métricas WMI/SNMP ✅      │
│  - NÃO coleta PING ✅               │
└─────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### 1. Worker Task (worker/tasks.py)

**Localização**: Linha ~1050

```python
@celery_app.task(name='worker.tasks.ping_all_servers')
def ping_all_servers():
    """
    Task que faz PING de todos os servidores ativos.
    Executa a cada 60 segundos via Celery Beat.
    """
    logger.info("🏓 Iniciando PING de todos os servidores...")
    
    db = SessionLocal()
    try:
        # Buscar todos os servidores ativos
        servers = db.query(Server).filter(Server.is_active == True).all()
        logger.info(f"📊 Encontrados {len(servers)} servidores ativos")
        
        for server in servers:
            # Executar PING
            latency = execute_ping(server.ip_address)
            
            if latency is not None:
                # Buscar ou criar sensor PING
                sensor = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.sensor_type == 'ping'
                ).first()
                
                if not sensor:
                    # Criar sensor PING automaticamente
                    sensor = Sensor(
                        server_id=server.id,
                        name='PING',
                        sensor_type='ping',
                        threshold_warning=100,
                        threshold_critical=200,
                        is_active=True
                    )
                    db.add(sensor)
                    db.commit()
                    db.refresh(sensor)
                    logger.info(f"✅ Sensor PING criado para {server.hostname}")
                
                # Atualizar timestamp do sensor
                sensor.updated_at = datetime.utcnow()
                
                # Determinar status baseado em thresholds
                if latency < sensor.threshold_warning:
                    status = 'ok'
                elif latency < sensor.threshold_critical:
                    status = 'warning'
                else:
                    status = 'critical'
                
                # Criar métrica
                metric = Metric(
                    sensor_id=sensor.id,
                    value=latency,
                    status=status,
                    timestamp=datetime.utcnow()
                )
                db.add(metric)
                db.commit()
                
                logger.info(f"📊 PING {server.hostname}: {latency}ms ({status})")
        
        logger.info(f"✅ PING concluído para {len(servers)} servidores")
        
    except Exception as e:
        logger.error(f"❌ Erro ao fazer PING: {str(e)}")
        db.rollback()
    finally:
        db.close()


def execute_ping(ip_address: str, count: int = 1, timeout: int = 2) -> Optional[float]:
    """
    Executa comando ping do Linux e retorna latência em ms.
    
    Args:
        ip_address: IP do servidor
        count: Número de pacotes (padrão: 1)
        timeout: Timeout em segundos (padrão: 2)
    
    Returns:
        Latência em ms ou None se falhar
    """
    try:
        # Executar comando ping
        result = subprocess.run(
            ['ping', '-c', str(count), '-W', str(timeout), ip_address],
            capture_output=True,
            text=True,
            timeout=timeout + 1
        )
        
        if result.returncode == 0:
            # Extrair latência da saída usando regex
            # Exemplo: "time=0.123 ms"
            match = re.search(r'time=(\d+\.?\d*)', result.stdout)
            if match:
                latency = float(match.group(1))
                return latency
        
        logger.warning(f"PING falhou para {ip_address}")
        return None
        
    except subprocess.TimeoutExpired:
        logger.warning(f"PING timeout para {ip_address}")
        return None
    except Exception as e:
        logger.error(f"Erro ao executar PING para {ip_address}: {str(e)}")
        return None
```

### 2. Celery Beat Schedule (worker/tasks.py)

```python
celery_app.conf.beat_schedule = {
    'ping-all-servers': {
        'task': 'worker.tasks.ping_all_servers',
        'schedule': 60.0,  # A cada 60 segundos
    },
    # ... outras tasks
}
```

### 3. API Corrigida (api/routers/servers.py)

**Linha ~144 (Sensores WMI)**:
```python
# PING removido - agora é criado automaticamente pelo worker a cada 60s
default_sensors = [
    {
        "name": "cpu_usage",
        "sensor_type": "cpu",
        "threshold_warning": 80,
        "threshold_critical": 95
    },
    {
        "name": "memory_usage",
        "sensor_type": "memory",
        "threshold_warning": 80,
        "threshold_critical": 95
    },
    {
        "name": "disk_C_",
        "sensor_type": "disk",
        "threshold_warning": 80,
        "threshold_critical": 95
    },
    {
        "name": "uptime",
        "sensor_type": "system",
        "threshold_warning": 80,
        "threshold_critical": 95
    },
    {
        "name": "network_in",
        "sensor_type": "network",
        "threshold_warning": 80,
        "threshold_critical": 95
    },
    {
        "name": "network_out",
        "sensor_type": "network",
        "threshold_warning": 80,
        "threshold_critical": 95
    }
]
```

**Linha ~210 (Sensores SNMP)**:
```python
# PING removido - agora é criado automaticamente pelo worker a cada 60s
snmp_sensors = [
    {
        "name": "SNMP_Uptime",
        "sensor_type": "snmp_uptime",
        "threshold_warning": None,
        "threshold_critical": None,
        "snmp_oid": "1.3.6.1.2.1.1.3.0"
    },
    # ... outros sensores SNMP
]
```

### 4. Dockerfile Worker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema incluindo ping
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "--beat"]
```

### 5. Migração Banco de Dados

```python
# api/adicionar_coluna_updated_at.py
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="coruja_monitor",
    user="coruja",
    password="coruja_secure_password"
)

cur = conn.cursor()

# Adicionar coluna updated_at
cur.execute("""
    ALTER TABLE sensors 
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
""")

conn.commit()
cur.close()
conn.close()
```

---

## 🚀 COMO FUNCIONA

### Fluxo de Execução

1. **Celery Beat** agenda task `ping_all_servers()` a cada 60s
2. **Worker** executa a task
3. **Task** busca todos os servidores ativos no banco
4. Para cada servidor:
   - Executa comando `ping -c 1 -W 2 <IP>`
   - Extrai latência da saída (regex)
   - Busca sensor PING existente
   - Se não existir, cria automaticamente
   - Atualiza `updated_at` do sensor
   - Cria métrica com latência e status
5. **Logs** registram execução completa

### Exemplo de Logs

```
[2026-03-11 10:00:00] INFO: 🏓 Iniciando PING de todos os servidores...
[2026-03-11 10:00:00] INFO: 📊 Encontrados 2 servidores ativos para fazer PING
[2026-03-11 10:00:00] INFO: 📊 PING SRVCMONITOR001: 0.06ms (ok)
[2026-03-11 10:00:00] INFO: 📊 PING SRVSONDA001: 0.55ms (ok)
[2026-03-11 10:00:00] INFO: ✅ PING concluído para 2 servidores
```

---

## ✅ BENEFÍCIOS

1. **Centralizado**: PING executado direto do servidor Linux
2. **Independente**: Funciona mesmo se probe Windows cair
3. **Automático**: Igual PRTG, sem configuração manual
4. **Confiável**: Servidor Linux sempre online
5. **Eficiente**: Menos carga na probe Windows
6. **Escalável**: Adiciona PING automaticamente em servidores novos
7. **Monitorável**: Logs centralizados no worker

---

## ⚠️ CONSIDERAÇÕES

### Delay de 60 Segundos

- Sensor PING criado até 60s após adicionar servidor
- Aceitável para monitoramento (igual PRTG)
- Pode ser reduzido alterando schedule (não recomendado)

### Worker é Crítico

- Se worker parar, PING para de funcionar
- Monitorar com healthcheck
- Configurar restart automático no Docker

### Limpeza de Duplicados

- Sensores antigos precisam ser deletados manualmente
- Apenas uma vez (após implementação)
- Comandos prontos em `DELETAR_SENSORES_35_37_AGORA.txt`

---

## 📊 MÉTRICAS ATUAIS

### Latências Medidas

- **SRVCMONITOR001**: ~0.06ms (rede local)
- **SRVSONDA001**: ~0.55ms (rede local)

### Sensores no Banco

```
hostname        | id | name | metricas | status
----------------+----+------+----------+--------
SRVCMONITOR001  | 36 | PING |       34 | ✅ OK
SRVCMONITOR001  | 35 | ping |       34 | ❌ DUPLICADO
SRVSONDA001     | 34 | ping |       34 | ✅ OK
SRVSONDA001     | 37 | PING |       10 | ❌ DUPLICADO
```

**Ação**: Deletar IDs 35 e 37

---

## 🔧 PRÓXIMOS PASSOS

### 1. Deletar Sensores Duplicados

**Arquivo**: `DELETAR_SENSORES_35_37_AGORA.txt`

```bash
# Cascata completa
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM remediation_logs WHERE incident_id IN (SELECT id FROM incidents WHERE sensor_id IN (35, 37));"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM incidents WHERE sensor_id IN (35, 37);"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM metrics WHERE sensor_id IN (35, 37);"
docker exec -it coruja-postgres psql -U coruja -d coruja_monitor -c "DELETE FROM sensors WHERE id IN (35, 37);"
```

### 2. Reiniciar Frontend

```bash
docker-compose restart frontend
sleep 20
docker logs coruja-frontend --tail 20
```

### 3. Limpar Cache do Navegador

1. `Ctrl + Shift + Delete`
2. Selecionar "Cache" e "Cookies"
3. Limpar dados
4. Fechar navegador
5. Abrir em modo anônimo
6. Acessar http://192.168.31.161:3000

### 4. Testar Servidor Novo

1. Dashboard → Adicionar Servidor
2. Verificar: Criado SEM sensor PING
3. Aguardar 60s
4. Verificar: Worker criou PING automaticamente

---

## 📚 ARQUIVOS DE REFERÊNCIA

- `COMECE_AQUI_PING_11MAR.txt` - Guia rápido passo a passo
- `DELETAR_SENSORES_35_37_AGORA.txt` - Comandos para deletar duplicados
- `DIAGNOSTICAR_SENSORES_PING.txt` - Comandos de diagnóstico
- `RESUMO_PING_COMPLETO_11MAR.md` - Documentação completa
- `SUCESSO_PING_11MAR.txt` - Resumo do sucesso
- `EXECUTAR_TUDO_AGORA_11MAR.txt` - Guia completo

---

## 🎉 CONCLUSÃO

Sistema de PING direto do servidor implementado com sucesso! Funciona de forma automática e independente, igual ao PRTG. Apenas falta limpar os sensores duplicados do banco de dados.

**Status Final**: ✅ Implementado e Funcionando (pendente limpeza)
