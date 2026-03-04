# Aplicar Melhorias - Biblioteca de Sensores

## O Que Foi Implementado

### 1. Biblioteca de Sensores Estilo PRTG ✅
- 40+ templates de sensores pré-configurados
- 7 categorias organizadas
- Interface em 3 passos intuitiva
- Descoberta automática em tempo real

### 2. Correção de Bugs ✅
- Probes filtradas por tenant (backend já estava correto)
- Descoberta de serviços usando server_id correto
- Descoberta de discos usando server_id correto

## Como Aplicar

### Passo 1: Rebuild do Frontend

Execute um destes comandos:

**Opção A - Docker (RECOMENDADO):**
```bash
rebuild_docker_frontend.bat
```

**Opção B - Manual:**
```bash
cd frontend
npm install
npm run build
docker-compose restart frontend
```

### Passo 2: Verificar

Após o rebuild (aguarde 30-60 segundos):

1. Acesse: http://localhost:3000
2. Faça login
3. Vá em "Servidores"
4. Clique em "Adicionar Sensor"
5. Você verá a nova interface com:
   - ⭐ Sensores Recomendados
   - 📂 Categorias organizadas
   - 🔍 Busca de sensores
   - 📊 Progress indicator

### Passo 3: Testar Descoberta

1. Selecione um servidor
2. Clique "Adicionar Sensor"
3. Escolha "Windows" → "Serviço Windows"
4. Deve carregar lista REAL de serviços do servidor
5. Selecione um serviço e adicione

## Problemas Conhecidos

### Probe Não Mostra Empresa Correta

**Causa:** Cache do navegador

**Solução:**
1. Limpe o cache do navegador (Ctrl+Shift+Del)
2. Ou force refresh (Ctrl+F5)
3. Ou use aba anônima

O backend JÁ filtra corretamente por tenant.

### Sensores Padrão Não Aparecem

**Causa:** Probe na máquina não foi atualizada

**Solução:**
```bash
# Execute na raiz do projeto
atualizar_probe_instalada.bat
```

Ou copie manualmente:
```
probe/probe_core.py → [pasta_instalacao]/probe_core.py
probe/collectors/ping_collector.py → [pasta_instalacao]/collectors/ping_collector.py
```

E reinicie:
```bash
net stop CorujaProbe
net start CorujaProbe
```

## Novos Arquivos

```
frontend/src/data/sensorTemplates.js       (Biblioteca de templates)
frontend/src/components/AddSensorModal.js  (Modal novo)
frontend/src/components/AddSensorModal.css (Estilos)
```

## Arquivos Modificados

```
frontend/src/components/Servers.js         (Usa novo modal)
```

## Checklist de Validação

Após aplicar, verifique:

- [ ] Frontend rebuilda sem erros
- [ ] Login funciona normalmente
- [ ] Ao clicar "Adicionar Sensor" abre modal novo
- [ ] Modal mostra sensores recomendados
- [ ] Modal mostra categorias com ícones
- [ ] Ao selecionar "Windows" → "Serviço" carrega lista real
- [ ] Ao selecionar "Disco" carrega lista real de discos
- [ ] Consegue adicionar sensor com sucesso
- [ ] Probe mostra apenas empresas do tenant atual

## Rollback (Se Necessário)

Se algo der errado, você pode voltar:

```bash
cd frontend
git checkout frontend/src/components/Servers.js
docker-compose restart frontend
```

Isso volta para o modal antigo (funcional mas menos intuitivo).

## Suporte

Se encontrar problemas:

1. Verifique logs do frontend:
   ```bash
   docker-compose logs -f frontend
   ```

2. Verifique logs do navegador (F12 → Console)

3. Verifique se o rebuild completou:
   ```bash
   docker-compose ps
   ```

4. Force rebuild sem cache:
   ```bash
   docker-compose build --no-cache frontend
   docker-compose up -d
   ```

---

**IMPORTANTE:** O rebuild do frontend é OBRIGATÓRIO para ver as mudanças!

Execute: `rebuild_docker_frontend.bat`
