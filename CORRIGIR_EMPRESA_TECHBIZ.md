# CORREÇÃO: Empresa Techbiz Fantasma

## PROBLEMA IDENTIFICADO

A empresa "Techbiz" aparece no frontend mas NÃO existe no banco de dados:

```sql
SELECT id, name, slug FROM tenants;
-- Resultado: Apenas "Default" (id=1)
```

## CAUSA

O frontend no servidor Linux está usando uma versão antiga/em cache. O código React está correto e carrega dados da API, mas a imagem Docker do frontend não foi reconstruída após as últimas atualizações.

## SOLUÇÃO

### No Servidor Linux (192.168.31.161)

Execute o script de rebuild:

```bash
cd ~/CorujaMonitor
chmod +x rebuild_frontend_linux.sh
./rebuild_frontend_linux.sh
```

### O que o script faz:

1. Para todos os containers
2. Remove a imagem antiga do frontend
3. Limpa cache do Docker
4. Reconstrói o frontend sem cache
5. Sobe todos os containers novamente

### Após o rebuild:

1. Limpe o cache do navegador:
   - Chrome/Edge: `Ctrl+Shift+Delete` → Limpar cache
   - Ou abra em aba anônima: `Ctrl+Shift+N`

2. Acesse: http://192.168.31.161:3000

3. Faça login e vá em "Empresas"

4. Agora deve aparecer apenas "Default"

## VERIFICAÇÃO

Após o rebuild, a empresa "Techbiz" não deve mais aparecer, pois:

- O código do componente `Companies.js` está correto
- Carrega dados diretamente da API: `api.get('/api/v1/tenants')`
- Não há dados mockados ou hardcoded
- Não há cache em localStorage/sessionStorage

## COMANDOS MANUAIS (se preferir)

```bash
# Parar containers
docker compose down

# Remover imagem antiga
docker rmi coruja-frontend

# Rebuild sem cache
docker compose build --no-cache frontend

# Subir containers
docker compose up -d

# Verificar status
docker compose ps
```

## IMPORTANTE

Sempre que fizer alterações no código do frontend:

1. Faça commit e push no Windows
2. Faça pull no Linux
3. Execute rebuild do frontend: `docker compose build --no-cache frontend`
4. Reinicie os containers: `docker compose up -d`
5. Limpe o cache do navegador

---

**Data:** 05/03/2026  
**Status:** Solução pronta para execução
