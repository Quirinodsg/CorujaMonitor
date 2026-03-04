# 🐳 Sensor Docker Implementado

## 🎯 Problema Identificado

Você adicionou o sensor Docker com sucesso, mas ele ficou "Aguardando dados" porque:

1. ✅ O sensor foi criado no banco de dados
2. ❌ A probe não tinha um coletor implementado para o tipo `docker`
3. ❌ A probe não estava coletando métricas Docker

## ✅ Solução Implementada

### 1. Coletor Docker Criado

Criei o arquivo `probe/collectors/docker_collector.py` que:

- ✅ Verifica se Docker está disponível
- ✅ Lista todos os containers (rodando e parados)
- ✅ Coleta métricas gerais:
  - Total de containers
  - Containers rodando
  - Containers parados
- ✅ Coleta métricas individuais por container (top 10):
  - Status (running/stopped)
  - CPU usage (%)
  - Memory usage (%)
  - Informações do container (ID, imagem, estado)

### 2. Probe Atualizada

Atualizei `probe/probe_core.py` para incluir o `DockerCollector` na lista de coletores.

### 3. Script de Inicialização

Criei `probe/start_probe.bat` para facilitar o início da probe com verificação de Docker.

## 🚀 Como Ativar

### Opção 1: Reiniciar a Probe (Recomendado)

Se você tem uma probe rodando, precisa reiniciá-la:

1. **Pare a probe atual** (se estiver rodando):
   - Procure por processo Python rodando
   - Ou feche a janela do terminal da probe

2. **Inicie a probe atualizada**:
   ```bash
   cd probe
   python probe_core.py
   ```
   
   Ou use o script:
   ```bash
   cd probe
   start_probe.bat
   ```

### Opção 2: Verificar se Probe Está Rodando

```powershell
# Ver processos Python
Get-Process python

# Ver se há probe rodando
Get-Process | Where-Object {$_.Path -like "*probe*"}
```

## 📊 Métricas Docker Coletadas

### Métricas Gerais
1. **Docker Containers Total** - Total de containers
2. **Docker Containers Running** - Containers em execução
3. **Docker Containers Stopped** - Containers parados

### Métricas por Container (Top 10 rodando)
Para cada container:
1. **Docker [nome] Status** - Status do container (running/stopped)
2. **Docker [nome] CPU** - Uso de CPU (%)
3. **Docker [nome] Memory** - Uso de memória (%)

### Exemplo de Containers Monitorados
Se você tem containers como:
- `coruja-frontend`
- `coruja-api`
- `coruja-postgres`
- `coruja-redis`

Você verá sensores como:
- Docker coruja-frontend Status
- Docker coruja-frontend CPU
- Docker coruja-frontend Memory
- Docker coruja-api Status
- Docker coruja-api CPU
- Docker coruja-api Memory
- etc.

## 🔍 Verificação

### 1. Verificar se Docker está acessível

```bash
docker version
docker ps
```

### 2. Verificar logs da probe

Após iniciar a probe, verifique o arquivo `probe/probe.log`:

```bash
# Ver últimas linhas do log
Get-Content probe/probe.log -Tail 20
```

Deve mostrar:
```
INFO - Initialized 10 collectors
INFO - Docker não está disponível ou não está rodando
```
ou
```
INFO - Coletadas X métricas Docker
```

### 3. Verificar no Frontend

Após 1-2 minutos de coleta:
1. Acesse http://localhost:3000
2. Vá em Servidores → Selecione o servidor
3. O sensor Docker deve mostrar dados em vez de "Aguardando dados"

## ⚠️ Requisitos

### Docker Desktop
- ✅ Docker Desktop instalado
- ✅ Docker Desktop rodando
- ✅ Docker CLI acessível via terminal

### Permissões
A probe precisa ter permissão para executar comandos Docker:
```bash
docker ps
docker stats
```

Se houver erro de permissão, execute o terminal como Administrador.

## 🐛 Troubleshooting

### Problema: "Docker não está disponível"

**Causa**: Docker Desktop não está rodando ou não está no PATH

**Solução**:
1. Abra Docker Desktop
2. Aguarde inicializar completamente
3. Teste no terminal: `docker version`
4. Reinicie a probe

### Problema: Sensor ainda mostra "Aguardando dados"

**Causa**: Probe não foi reiniciada ou não está rodando

**Solução**:
1. Verifique se a probe está rodando
2. Reinicie a probe com o novo coletor
3. Aguarde 1-2 minutos para primeira coleta
4. Recarregue a página do frontend (F5)

### Problema: "Access Denied" ao executar docker

**Causa**: Falta de permissões

**Solução**:
1. Execute o terminal como Administrador
2. Ou adicione seu usuário ao grupo docker-users
3. Reinicie o terminal e a probe

## 📁 Arquivos Criados/Modificados

### Novos Arquivos
1. ✅ `probe/collectors/docker_collector.py` - Coletor Docker
2. ✅ `probe/start_probe.bat` - Script de inicialização
3. ✅ `SENSOR_DOCKER_IMPLEMENTADO.md` - Esta documentação

### Arquivos Modificados
1. ✅ `probe/probe_core.py` - Adicionado DockerCollector

## 🎯 Próximos Passos

### 1. Reiniciar a Probe
```bash
cd probe
python probe_core.py
```

### 2. Aguardar Coleta
Aguarde 1-2 minutos para a primeira coleta de métricas

### 3. Verificar no Frontend
Recarregue a página e veja os dados do sensor Docker

### 4. Adicionar Mais Sensores Docker (Opcional)
Você pode adicionar sensores específicos para containers individuais:
- Docker Container Status
- Docker Container CPU
- Docker Container Memory

## 📊 Exemplo de Resultado

Após a probe coletar dados, você verá:

```
Sensor: Docker Containers Total
Valor: 6 containers
Status: OK

Sensor: Docker Containers Running  
Valor: 6 containers
Status: OK

Sensor: Docker coruja-frontend Status
Valor: Online
Status: OK

Sensor: Docker coruja-frontend CPU
Valor: 2.5%
Status: OK

Sensor: Docker coruja-frontend Memory
Valor: 15.3%
Status: OK
```

## 🎉 Benefícios

Com o monitoramento Docker ativo, você pode:

1. ✅ Ver quantos containers estão rodando
2. ✅ Detectar containers parados inesperadamente
3. ✅ Monitorar uso de CPU por container
4. ✅ Monitorar uso de memória por container
5. ✅ Receber alertas se containers pararem
6. ✅ Receber alertas se CPU/memória ultrapassarem limites

## 📞 Suporte

Se ainda houver problemas:

1. Compartilhe o conteúdo de `probe/probe.log`
2. Compartilhe a saída de `docker ps`
3. Compartilhe a saída de `docker version`
4. Informe se a probe está rodando

---

**Data**: 19/02/2026 - 15:00
**Status**: ✅ Coletor Docker implementado
**Ação Necessária**: Reiniciar a probe para ativar o coletor
