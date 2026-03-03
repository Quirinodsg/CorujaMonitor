# 🚀 Instruções para Aplicar Correções - 03 de Março 2026

## ✅ Correções Implementadas

Todas as 6 correções solicitadas foram implementadas:

1. ✅ **Card de sensores** - Valor aumentado de 32px para 42px
2. ✅ **Notas ocultas** - Nota some quando sensor está OK
3. ✅ **Card de métricas** - Aumentado para 500px mínimo
4. ✅ **Teste de sensores** - Não sai mais da aba Config
5. ✅ **Excluir probe** - Endpoint DELETE criado
6. ✅ **NOC zerado** - Servidores OK não somem mais

## 📋 Arquivos Modificados

- `frontend/src/components/Management.css` (correções 1 e 2)
- `frontend/src/components/MetricsViewer.css` (correção 3)
- `frontend/src/components/Settings.js` (correção 4)
- `api/routers/probes.py` (correção 5)
- `api/routers/noc_realtime.py` (correção 6 - já estava aplicada)

## 🔧 Como Aplicar

### Opção 1: Script Automático (Recomendado)

Abra o PowerShell e execute:

```powershell
.\aplicar_correcoes_finais_03mar.ps1
```

### Opção 2: Manual

Se o script não funcionar, execute os comandos manualmente:

```powershell
# 1. Reiniciar API (para aplicar endpoint DELETE)
docker-compose restart api

# 2. Aguardar API inicializar
Start-Sleep -Seconds 10

# 3. Reiniciar Frontend (para aplicar correção do teste de sensores)
docker-compose restart frontend

# 4. Aguardar Frontend inicializar
Start-Sleep -Seconds 15

# 5. Abrir navegador
Start-Process "http://localhost:3000"
```

### Opção 3: Rebuild Completo (Se houver problemas)

```powershell
# Parar tudo
docker-compose down

# Rebuild sem cache
docker-compose build --no-cache frontend api

# Iniciar novamente
docker-compose up -d

# Aguardar 30 segundos
Start-Sleep -Seconds 30
```

## 🧪 Testes Obrigatórios

Após aplicar as correções, teste cada item:

### ✅ 1. Card de Sensores

1. Vá em **Servidores**
2. Selecione um servidor
3. Verifique se o **valor do sensor está maior** (42px)
4. Adicione uma **nota** em um sensor com problema
5. Resolva o problema
6. **Verifique se a nota sumiu**

**Resultado esperado:** Valor maior e nota oculta quando OK

---

### ✅ 2. Card de Métricas Grafana

1. Vá em **Métricas Grafana**
2. Verifique se os **cards estão maiores**
3. Verifique se o **texto está visível**
4. Verifique se o **texto está dentro do card** (não saindo)

**Resultado esperado:** Cards maiores (500px), texto visível e dentro

---

### ✅ 3. Teste de Sensores

1. Vá em **Configurações**
2. Clique na aba **🧪 Testes de Sensores**
3. **Verifique se permanece na página de Config**
4. Não deve navegar para outra página

**Resultado esperado:** Permanece na aba Config

---

### ✅ 4. Excluir Probe

1. Vá em **Empresas**
2. Selecione uma empresa
3. Tente **excluir uma probe**
4. **Não deve dar erro "Not Found"**

**Resultado esperado:** Probe excluída com sucesso

---

### ✅ 5. NOC Real-Time

1. Vá em **NOC Real-Time**
2. Observe o contador **"SERVIDORES OK"**
3. Crie um alerta em um servidor (simule falha)
4. **Verifique se os servidores OK continuam visíveis**
5. **Contador não deve zerar**

**Resultado esperado:** Servidores OK permanecem visíveis

---

## 🔍 Troubleshooting

### Problema: Mudanças não aparecem

**Solução:**
1. Pressione **Ctrl+Shift+R** no navegador (limpa cache)
2. Ou abra uma **aba anônima** (Ctrl+Shift+N)
3. Se ainda não funcionar, execute rebuild completo (Opção 3)

### Problema: Docker não inicia

**Solução:**
1. Abra o **Docker Desktop**
2. Aguarde inicializar completamente
3. Execute os comandos novamente

### Problema: API não responde

**Solução:**
```powershell
# Ver logs da API
docker-compose logs -f api

# Se houver erro, reiniciar
docker-compose restart api
```

### Problema: Frontend não carrega

**Solução:**
```powershell
# Ver logs do Frontend
docker-compose logs -f frontend

# Se houver erro, rebuild
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## 📊 Checklist Final

Marque cada item após testar:

- [ ] Card de sensores com valor maior (42px)
- [ ] Notas ocultas quando sensor OK
- [ ] Card de métricas aumentado (500px)
- [ ] Teste de sensores não sai da aba
- [ ] Excluir probe funciona sem erro
- [ ] NOC não zera servidores OK

## ✅ Confirmação

Quando todos os itens estiverem marcados, as correções foram aplicadas com sucesso!

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `docker-compose logs -f api frontend`
2. Tente rebuild completo (Opção 3)
3. Verifique se o Docker Desktop está atualizado
4. Reinicie o computador se necessário

---

**Data:** 03 de Março de 2026  
**Versão:** 1.0  
**Status:** ✅ Pronto para aplicar
