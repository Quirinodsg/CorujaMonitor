# Solução: Interface Resetada Após docker-compose down

## Problema
Após executar `docker-compose down`, a interface voltou ao estado original, perdendo todas as melhorias visuais.

## Causa
O comando `docker-compose down` remove os containers. Quando você faz `docker-compose up -d` novamente, o Docker pode usar cache antigo da imagem.

## Verificação: Arquivos Locais Estão Corretos ✅

Confirmado que os arquivos locais têm todas as alterações:
- ✅ `Management.css` - Cards 320px, altura reduzida, text overflow
- ✅ `SensorGroups.css` - Cores de alto contraste (WCAG AA)
- ✅ `Servers.js` - Card "Sistema" mostra "Sistema"

## Solução Passo a Passo

### Opção 1: Restart Simples (Tente Primeiro)

```bash
# Na pasta raiz do projeto
cd "C:\Users\andre.quirino\Coruja Monitor"

# Reiniciar frontend
docker-compose restart frontend

# Aguardar 30 segundos
# Abrir http://localhost:3000
# Fazer Ctrl+Shift+R (hard refresh)
```

### Opção 2: Rebuild Sem Cache (Se Opção 1 Não Funcionar)

```bash
# Na pasta raiz
cd "C:\Users\andre.quirino\Coruja Monitor"

# Parar frontend
docker-compose stop frontend

# Remover container
docker rm coruja-frontend

# Rebuild sem cache
docker-compose build --no-cache frontend

# Iniciar
docker-compose up -d frontend

# Aguardar 1-2 minutos (compilação)
# Fazer Ctrl+Shift+R no navegador
```

### Opção 3: Usar o Script Automático

```bash
# Executar o script criado
restart_frontend.bat
```

## Comandos Corretos

### ❌ ERRADO
```bash
docker-compose restart coruja-frontend  # Nome do container
```

### ✅ CORRETO
```bash
docker-compose restart frontend  # Nome do serviço
```

## Nomes no Docker Compose

| Serviço | Container | Porta |
|---------|-----------|-------|
| `frontend` | coruja-frontend | 3000 |
| `api` | coruja-api | 8000 |
| `ai-agent` | coruja-ai-agent | 8001 |
| `worker` | coruja-worker | - |
| `postgres` | coruja-postgres | 5432 |
| `redis` | coruja-redis | 6379 |

## Verificar se Funcionou

1. Abrir http://localhost:3000
2. Login: admin@coruja.com / admin123
3. Ir em "Servidores" → Selecionar um servidor
4. Verificar:

### Cards de Sensores
- ✅ Largura: 320px (mais largos)
- ✅ Altura: ~180px (menos altos)
- ✅ Proporção: 16:9 (retangular horizontal)
- ✅ Texto não cortado
- ✅ Padding reduzido

### Cards Agregadores
- ✅ Cores com alto contraste
- ✅ OK: Verde escuro (#065f46) em fundo verde claro (#d1fae5)
- ✅ Warning: Marrom (#92400e) em fundo laranja (#fed7aa)
- ✅ Critical: Vermelho escuro (#991b1b) em fundo vermelho claro (#fecaca)

### Card Sistema
- ✅ Mostra "Sistema" ao invés do nome da máquina

## Se Ainda Não Funcionar

### 1. Verificar Logs do Frontend

```bash
docker-compose logs -f frontend
```

Procurar por erros de compilação.

### 2. Verificar se Arquivos Estão Montados

```bash
docker exec coruja-frontend ls -la /app/src/components/
```

Deve mostrar os arquivos CSS e JS.

### 3. Limpar Cache do Docker

```bash
# Remover imagens antigas
docker image prune -a

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 4. Verificar Arquivo Local

```bash
# Windows PowerShell
Get-Content "frontend\src\components\Management.css" | Select-String "320px"

# Deve retornar a linha com minmax(320px, 1fr)
```

## Prevenção Futura

### ✅ Use Estes Comandos
```bash
docker-compose restart frontend  # Reiniciar
docker-compose stop frontend     # Parar
docker-compose start frontend    # Iniciar
```

### ❌ Evite Este Comando
```bash
docker-compose down  # Remove containers e pode causar problemas
```

### Se Precisar Fazer Down
```bash
# Fazer backup antes
docker-compose down

# Depois, rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Status Atual

Frontend foi reiniciado com o comando:
```bash
docker-compose restart frontend
```

**Próximos Passos:**
1. Aguardar 30 segundos
2. Abrir http://localhost:3000
3. Fazer Ctrl+Shift+R (hard refresh)
4. Verificar se as alterações voltaram

Se não funcionar, execute:
```bash
restart_frontend.bat
```

## Alterações Preservadas nos Arquivos

Todas as alterações estão salvas nos arquivos locais:

1. **Management.css** (linha 641-644)
   ```css
   .sensors-grid {
     display: grid;
     grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
     gap: 14px;
   }
   ```

2. **SensorGroups.css** (linhas 261-274)
   ```css
   .aggregator-card-stats .stat-item.ok {
     background: #d1fae5;
     color: #065f46;
   }
   ```

3. **Servers.js** (linha 658)
   ```javascript
   const cardName = group.name;
   ```

Essas alterações estão nos arquivos e serão aplicadas quando o frontend recompilar.
