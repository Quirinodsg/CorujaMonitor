# 🧪 Testar Knowledge Base - Guia Rápido

## Data: 25/02/2026

---

## ✅ SERVIÇOS RODANDO

```
✅ coruja-api        - Up 4 minutes  - http://192.168.30.189:8000
✅ coruja-frontend   - Up 4 minutes  - http://192.168.30.189:3000
✅ coruja-postgres   - Up 5 days (healthy)
✅ coruja-redis      - Up 5 days (healthy)
✅ coruja-ai-agent   - Up 5 days
✅ coruja-worker     - Up 5 days
```

---

## 🎯 TESTE 1: Acessar Interface

### Passo 1: Login
```
URL: http://192.168.30.189:3000
Email: admin@coruja.com
Senha: admin123
```

### Passo 2: Verificar Novos Menus
No menu lateral, você deve ver:

```
📊 Dashboard
🏢 Empresas
🖥️ Servidores
📡 Sensores
⚠️ Incidentes
🧠 Base de Conhecimento    ← NOVO!
🤖 Atividades da IA        ← NOVO!
🔧 Manutenção
🔮 AIOps
📈 Relatórios
🧪 Testes
⚙️ Configurações
```

---

## 🎯 TESTE 2: Base de Conhecimento

### Passo 1: Acessar
Clique em **🧠 Base de Conhecimento** no menu lateral

### Passo 2: Verificar Interface
Você deve ver:

1. **Estatísticas no topo** (4 cards):
   - 📚 Problemas Conhecidos
   - 🤖 Com Auto-Resolução
   - ✅ Taxa de Sucesso Média
   - 🚀 Resoluções Este Mês

2. **Barra de busca e filtro**:
   - Campo de busca
   - Dropdown para filtrar por tipo de sensor

3. **Lista de problemas**:
   - Se vazio: "Nenhum problema encontrado"
   - Mensagem: "A IA aprenderá com as resoluções dos técnicos"

### Resultado Esperado
- ✅ Página carrega sem erros
- ✅ Estatísticas mostram zeros (ainda não há dados)
- ✅ Interface está bonita e funcional

---

## 🎯 TESTE 3: Atividades da IA

### Passo 1: Acessar
Clique em **🤖 Atividades da IA** no menu lateral

### Passo 2: Verificar Status do Ollama
No topo da página, você deve ver um card:

**Se Ollama estiver rodando**:
```
✅ Ollama: Online
URL: http://localhost:11434
Modelo: llama2
[Testar Conexão]
```

**Se Ollama NÃO estiver rodando**:
```
❌ Ollama: Offline
Connection refused - Ollama not running
```

### Passo 3: Verificar Estatísticas
Você deve ver 5 cards:

1. 🔍 Análises Hoje
2. 🚀 Auto-Resoluções Hoje
3. ⏳ Aguardando Aprovação
4. ✅ Taxa de Sucesso Hoje
5. ⏱️ Minutos Economizados (card destacado em roxo)

### Passo 4: Verificar Abas
Duas abas disponíveis:

1. **🔄 Atividades Recentes**
   - Lista de atividades da IA
   - Se vazio: "Nenhuma atividade recente"

2. **⏳ Aguardando Aprovação (0)**
   - Resoluções pendentes
   - Se vazio: "✅ Nenhuma resolução aguardando aprovação"

### Resultado Esperado
- ✅ Página carrega sem erros
- ✅ Status do Ollama é exibido (online ou offline)
- ✅ Estatísticas mostram zeros (ainda não há dados)
- ✅ Abas funcionam corretamente

---

## 🎯 TESTE 4: Testar Conexão com Ollama

### Se Ollama estiver Online

1. Na página **Atividades da IA**
2. Clique no botão **[Testar Conexão]**
3. Aguarde alguns segundos
4. Deve aparecer um alert com a resposta do Ollama

**Resposta esperada**:
```
Ollama está funcionando!

Resposta: Hello, I am working!
```

### Se Ollama estiver Offline

Você verá o erro:
```
Erro ao testar Ollama:
Connection refused - Ollama not running
```

**Para instalar Ollama**:

**Windows**:
```
1. Baixar de: https://ollama.ai/download
2. Instalar o executável
3. Abrir terminal e executar: ollama pull llama2
```

**Linux**:
```bash
curl https://ollama.ai/install.sh | sh
ollama pull llama2
```

---

## 🎯 TESTE 5: API Endpoints (Swagger)

### Passo 1: Acessar Swagger
```
URL: http://192.168.30.189:8000/docs
```

### Passo 2: Autenticar
1. Clique no botão **Authorize** (cadeado verde)
2. Use as credenciais:
   ```
   username: admin@coruja.com
   password: admin123
   ```
3. Clique em **Authorize**

### Passo 3: Testar Endpoints

#### Knowledge Base
```
GET /api/v1/knowledge-base/
GET /api/v1/knowledge-base/stats
```

**Resposta esperada** (stats):
```json
{
  "total_entries": 0,
  "auto_resolution_enabled": 0,
  "average_success_rate": 0.0,
  "total_resolutions_this_month": 0,
  "by_sensor_type": {},
  "by_risk_level": {}
}
```

#### AI Activities
```
GET /api/v1/ai-activities/
GET /api/v1/ai-activities/stats
```

**Resposta esperada** (stats):
```json
{
  "today_analyses": 0,
  "today_resolutions": 0,
  "today_learning_sessions": 0,
  "pending_approvals": 0,
  "success_rate_today": 0.0,
  "total_time_saved_minutes": 0
}
```

#### AI Configuration
```
GET /api/v1/ai/status
```

**Resposta esperada** (se Ollama offline):
```json
{
  "online": false,
  "url": "http://localhost:11434",
  "model": "llama2",
  "version": null,
  "error": "Connection refused - Ollama not running"
}
```

**Resposta esperada** (se Ollama online):
```json
{
  "online": true,
  "url": "http://localhost:11434",
  "model": "llama2",
  "version": "0.1.23",
  "error": null
}
```

---

## 🎯 TESTE 6: Verificar Console do Navegador

### Passo 1: Abrir DevTools
```
Pressione F12 no navegador
Vá para a aba "Console"
```

### Passo 2: Navegar pelas Páginas
1. Acesse **Base de Conhecimento**
2. Acesse **Atividades da IA**

### Resultado Esperado
- ✅ Nenhum erro no console
- ✅ Apenas logs informativos (se houver)
- ❌ Não deve ter erros 404 ou 500

---

## 🎯 TESTE 7: Verificar Responsividade

### Teste em Diferentes Tamanhos
1. Redimensione a janela do navegador
2. Verifique se os cards se reorganizam
3. Verifique se o menu lateral funciona

### Resultado Esperado
- ✅ Layout se adapta ao tamanho da tela
- ✅ Cards ficam em grid responsivo
- ✅ Texto não fica cortado

---

## 📊 CHECKLIST DE TESTES

### Interface
- [ ] Login funciona
- [ ] Novos menus aparecem no sidebar
- [ ] Base de Conhecimento carrega
- [ ] Atividades da IA carrega
- [ ] Estatísticas são exibidas
- [ ] Busca e filtros funcionam
- [ ] Abas funcionam
- [ ] Botões respondem ao clique

### API
- [ ] Endpoints de Knowledge Base respondem
- [ ] Endpoints de AI Activities respondem
- [ ] Endpoint de AI Status responde
- [ ] Autenticação funciona no Swagger
- [ ] Respostas estão no formato correto

### Ollama
- [ ] Status é detectado corretamente
- [ ] Teste de conexão funciona (se online)
- [ ] Erro é exibido corretamente (se offline)

### Console
- [ ] Sem erros 404
- [ ] Sem erros 500
- [ ] Sem erros de JavaScript

---

## 🐛 PROBLEMAS COMUNS

### Problema 1: Página em Branco
**Solução**:
```bash
# Limpar cache do navegador
Ctrl + Shift + Delete

# Ou forçar reload
Ctrl + F5
```

### Problema 2: Erro 401 (Unauthorized)
**Solução**:
```
1. Fazer logout
2. Fazer login novamente
3. Token será renovado
```

### Problema 3: Ollama Offline
**Solução**:
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não estiver, iniciar Ollama
# Windows: Abrir aplicativo Ollama
# Linux: ollama serve
```

### Problema 4: Estatísticas Zeradas
**Isso é normal!**
```
As estatísticas estarão zeradas porque:
- Ainda não há problemas na Knowledge Base
- IA ainda não executou resoluções
- Técnicos ainda não adicionaram notas

Isso mudará quando:
- Técnicos resolverem incidentes com notas
- IA aprender com as resoluções
- IA executar auto-resoluções
```

---

## ✅ RESULTADO ESPERADO

Após todos os testes, você deve ter:

✅ Interface funcionando perfeitamente
✅ Novos menus acessíveis
✅ Páginas carregando sem erros
✅ API respondendo corretamente
✅ Status do Ollama sendo detectado
✅ Estatísticas zeradas (normal no início)
✅ Sistema pronto para aprender

---

## 🚀 PRÓXIMO PASSO

Agora que a interface está funcionando, o próximo passo é:

1. **Instalar/Iniciar Ollama** (se ainda não estiver rodando)
2. **Criar incidentes de teste** para a IA aprender
3. **Adicionar notas de resolução** para a IA capturar
4. **Ver a IA aprender e sugerir soluções**

---

## 📞 SUPORTE

Se encontrar algum problema:

1. Verifique os logs:
   ```bash
   docker logs coruja-api --tail 50
   docker logs coruja-frontend --tail 50
   ```

2. Verifique o console do navegador (F12)

3. Teste os endpoints no Swagger

4. Reinicie os serviços se necessário:
   ```bash
   docker restart coruja-api coruja-frontend
   ```

---

**Tudo pronto para testar! 🎉**

