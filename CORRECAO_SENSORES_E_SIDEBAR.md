# Correção de Sensores Duplicados e Melhorias na Sidebar

## Data: 19/02/2026

## Problema Identificado

### 1. Sensores Duplicados
- Sistema mostrava 49 sensores quando deveria ter apenas 28
- 21 sensores Docker estavam duplicados com `sensor_type='unknown'`
- Sensores duplicados: IDs 93-113 (todos com tipo 'unknown')

### 2. Alinhamento da Sidebar
- Ícones desalinhados verticalmente
- Espaçamento inconsistente
- Falta de hierarquia visual clara

## Solução Implementada

### 1. Remoção de Sensores Duplicados

#### Script Criado: `api/remove_unknown_sensors.py`
```python
# Remove sensores com tipo 'unknown' e suas métricas
- 21 sensores removidos
- 1260 métricas associadas removidas
```

#### Sensores Removidos:
- Docker Containers Total (ID 93)
- Docker Containers Running (ID 94)
- Docker Containers Stopped (ID 95)
- Docker coruja-frontend + CPU + Memory (IDs 96-98)
- Docker coruja-api + CPU + Memory (IDs 99-101)
- Docker coruja-worker + CPU + Memory (IDs 102-104)
- Docker coruja-ai-agent + CPU + Memory (IDs 105-107)
- Docker coruja-postgres + CPU + Memory (IDs 108-110)
- Docker coruja-redis + CPU + Memory (IDs 111-113)

#### Resultado:
✅ **28 sensores totais** (correto!)
- 7 sensores de sistema
- 21 sensores Docker

### 2. Melhorias na Sidebar (Servidores)

#### Alinhamento Perfeito:
```css
/* Status Icon */
- align-self: center
- Tamanho fixo: 10px x 10px
- Gap reduzido: 8px

/* Server Info */
- justify-content: center
- Gap: 2px
- Line-height: 1.3

/* Tree Icon */
- Container fixo: 14px x 14px
- display: flex + align-items: center

/* Action Buttons */
- align-self: center
- display: flex + align-items: center
```

### 3. Melhorias nos Summary Cards (Dashboard)

#### Antes:
- Cards grandes (180px mínimo)
- Ícone 32px sem fundo
- Padding 20px
- Border-left simples

#### Depois:
- Cards compactos (140px mínimo)
- Ícone 28px com fundo #f9fafb e border-radius
- Padding 16px
- Border-left 4px colorido por status
- Active state com background colorido
- Hover com elevação

#### Cores por Status:
- **OK**: #10b981 (verde) → background #ecfdf5
- **Warning**: #f59e0b (laranja) → background #fffbeb
- **Critical**: #ef4444 (vermelho) → background #fef2f2
- **Unknown**: #9ca3af (cinza) → background #f3f4f6
- **Default**: #3b82f6 (azul) → background #eff6ff

### 4. Scripts Utilitários Criados

#### `api/check_duplicate_sensors.py`
- Verifica sensores duplicados
- Agrupa por servidor, tipo e nome
- Mostra contagem por servidor

#### `api/list_sensors.py`
- Lista todos os sensores organizados
- Agrupa por servidor e tipo
- Mostra resumo por tipo

#### `api/remove_unknown_sensors.py`
- Remove sensores com tipo 'unknown'
- Remove métricas associadas primeiro
- Evita erros de constraint

## Estrutura Final dos Sensores

### Servidor: DESKTOP-P9VGN04 (28 sensores)

#### Sistema (7 sensores):
1. PING (ID: 63)
2. CPU (ID: 64)
3. Memória (ID: 65)
4. Disco C (ID: 66)
5. Uptime (ID: 67)
6. Network IN (ID: 68)
7. Network OUT (ID: 69)

#### Docker (21 sensores):
1. Docker Containers Total (ID: 72)
2. Docker Containers Running (ID: 73)
3. Docker Containers Stopped (ID: 74)
4. Docker coruja-frontend + CPU + Memory (IDs: 75-77)
5. Docker coruja-api + CPU + Memory (IDs: 78-80)
6. Docker coruja-worker + CPU + Memory (IDs: 81-83)
7. Docker coruja-ai-agent + CPU + Memory (IDs: 84-86)
8. Docker coruja-postgres + CPU + Memory (IDs: 87-89)
9. Docker coruja-redis + CPU + Memory (IDs: 90-92)

## Arquivos Modificados

### CSS:
1. `frontend/src/components/Management.css`
   - `.server-card` (alinhamento)
   - `.tree-view` e `.tree-server` (alinhamento)
   - `.sensors-summary` (cards melhorados)
   - `.summary-card` (estados e cores)

### Scripts Python:
1. `api/check_duplicate_sensors.py` (novo)
2. `api/list_sensors.py` (novo)
3. `api/remove_unknown_sensors.py` (novo)

## Como Usar os Scripts

### Verificar Duplicados:
```bash
docker exec coruja-api python check_duplicate_sensors.py
```

### Listar Todos os Sensores:
```bash
docker exec coruja-api python list_sensors.py
```

### Remover Sensores Unknown:
```bash
docker cp api/remove_unknown_sensors.py coruja-api:/app/
docker exec coruja-api python remove_unknown_sensors.py
```

## Resultado Visual

### Dashboard (Todos os Sensores):
```
📊 28 Total  ✅ 28 OK  ⚠️ 0 Aviso  🔥 0 Crítico  ✓ 0 Verificado  ❓ 0 Desconhecido
```

### Sidebar (Servidores):
- Ícones perfeitamente alinhados verticalmente
- Status indicator (bolinha) centralizado
- Textos com line-height consistente
- Action buttons aparecem no hover, alinhados

### Summary Cards:
- Compactos e informativos
- Ícones com fundo arredondado
- Border colorido por status
- Hover com elevação suave
- Active state destacado

## Próximos Passos

1. ✅ Sensores duplicados removidos
2. ✅ Sidebar alinhada perfeitamente
3. ✅ Summary cards melhorados
4. 🔄 Monitorar se novos sensores 'unknown' aparecem
5. 🔄 Investigar por que sensores Docker foram criados como 'unknown'

## Prevenção de Duplicados

### Causa Provável:
- Probe criou sensores Docker sem definir `sensor_type` corretamente
- Valor padrão 'unknown' foi usado

### Solução:
- Verificar `probe/collectors/docker_collector.py`
- Garantir que `sensor_type='docker'` está sendo passado
- Adicionar validação no backend

## Comandos Rápidos

### Reiniciar Frontend:
```bash
docker restart coruja-frontend
```

### Ver Logs da API:
```bash
docker logs coruja-api --tail 50
```

### Acessar Container:
```bash
docker exec -it coruja-api bash
```

---

**Desenvolvido por:** Kiro AI Assistant  
**Data:** 19 de Fevereiro de 2026  
**Status:** ✅ Concluído
