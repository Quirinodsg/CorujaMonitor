# 🎯 Testar Integração TOPdesk - GUIA RÁPIDO

## ✅ Correções Aplicadas!

1. ✅ Loop de erro corrigido
2. ✅ Validação de campos implementada
3. ✅ API corrigida: `callerLookup` agora usa `loginName` em vez de `email`
4. ✅ Campos opcionais só são enviados se preenchidos
5. ✅ Mensagens específicas para cada tipo de erro

## ⚠️ IMPORTANTE: Entenda os Papéis

**Requisitante (Caller):**
- Quem **abre** o chamado = `coruja.monitor`
- Usuário comum do TOPdesk (não precisa ser operador)

**Operador (Operator):**
- Quem **atende** o chamado = Equipe de Infraestrutura
- Configurado no campo "Grupo de Operadores" (opcional)

**Fluxo:**
```
coruja.monitor → Abre chamado → Infraestrutura → Resolve
(Requisitante)                    (Operadores)
```

## 🚀 Como Testar AGORA

### Passo 0: Reiniciar a API (IMPORTANTE!)

```bash
docker restart coruja-api
```

Aguarde 10 segundos para a API reiniciar completamente.

### Passo 1: Recarregar o Frontend
```bash
# No navegador, pressione:
Ctrl + Shift + R  (Windows/Linux)
Cmd + Shift + R   (Mac)

# Ou force rebuild:
cd frontend
npm start
```

### Passo 2: Acessar Configurações
1. Abra o Coruja Monitor
2. Vá em **Configurações** (⚙️)
3. Clique na aba **Integrações e Notificações**
4. Procure por **TOPdesk (Service Desk)**

### Passo 3: Configurar TOPdesk

#### 3.1 Ativar
- Clique no toggle para **ATIVAR** o TOPdesk

#### 3.2 Preencher Campos Obrigatórios (*)

**URL do TOPdesk:**
```
https://empresa.topdesk.net
```

**Usuário (Login):**
```
coruja.monitor
```
⚠️ Este é o REQUISITANTE (quem abre o chamado), não o operador!

**Senha:**
```
[Sua senha do TOPdesk]
```

#### 3.3 Campos Opcionais (pode deixar vazio ou preencher)

**Grupo de Operadores:** (exemplo: "Infraestrutura", "Suporte TI")
- Este é o grupo que vai ATENDER os chamados
- Recomendado preencher para direcionar automaticamente
- Se deixar vazio, o chamado fica sem atribuição inicial

**Categoria:** (exemplo: "Infraestrutura", "Servidores")
- Ajuda a organizar os chamados
- Opcional

**Subcategoria:** (exemplo: "Monitoramento", "Alertas")
- Detalha ainda mais a categoria
- Opcional

### Passo 4: SALVAR (IMPORTANTE!)

1. **Role a página até o FINAL**
2. Procure o botão **"💾 Salvar Configurações"**
3. **CLIQUE** no botão
4. Aguarde a mensagem: **"Configurações de notificação salvas com sucesso!"**

### Passo 5: Testar

1. **Volte** para a seção TOPdesk (role para cima)
2. Clique no botão **"Testar Criação de Chamado"**
3. Aguarde o resultado

## 📊 Resultados Possíveis

### ✅ SUCESSO
```
✅ Sucesso!

Chamado de teste criado no TOPdesk com sucesso!
```

**O que fazer:**
- Verifique no TOPdesk se o chamado foi criado
- Confirme que o Requisitante é `coruja.monitor`
- Confirme que o Grupo de Operadores está correto (se configurado)
- A integração está funcionando! 🎉

### ⚠️ Campos Não Preenchidos
```
⚠️ Campos obrigatórios não preenchidos!

Para TOPdesk você precisa preencher:
✓ URL do TOPdesk
✓ Usuário (Login)
✓ Senha
```

**O que fazer:**
- Preencha os 3 campos obrigatórios
- Clique em "Salvar Configurações"
- Teste novamente

### ⚠️ Não Salvou
```
⚠️ Configuração não encontrada no servidor!

Você JÁ PREENCHEU os campos, mas ainda não salvou.

Próximo passo:
1. Role a página até o FINAL
2. Clique no botão "💾 Salvar Configurações"
3. Aguarde a mensagem de sucesso
4. Depois volte aqui e clique em "Testar Integração"
```

**O que fazer:**
- Role até o final da página
- Clique em "💾 Salvar Configurações"
- Aguarde a confirmação
- Volte e teste novamente

### ❌ Erro de Autenticação
```
❌ Erro de Autenticação!

Usuário ou senha incorretos.

Verifique:
✓ URL: https://empresa.topdesk.net
✓ Usuário: monitor.user
✓ Senha está correta?
```

**O que fazer:**
1. Abra `https://empresa.topdesk.net` no navegador
2. Tente fazer login com as mesmas credenciais
3. Se funcionar no navegador mas não na integração:
   - Verifique se o usuário tem permissão de API
   - Verifique se a senha não tem caracteres especiais problemáticos
4. Corrija as credenciais
5. Clique em "Salvar Configurações"
6. Teste novamente

### ❌ Erro de Conexão
```
❌ Erro de Conexão!

Não foi possível conectar ao TOPdesk.

Verifique:
✓ URL está correta? https://empresa.topdesk.net
✓ O servidor está acessível?
✓ Firewall bloqueando?
```

**O que fazer:**
1. Verifique se a URL está correta
2. Teste acessar a URL no navegador
3. Verifique se o servidor Coruja tem acesso à internet
4. Verifique firewall/proxy

## 🔍 Troubleshooting

### Problema: Mensagem de erro diferente

**Solução:**
1. Copie a mensagem de erro completa
2. Vá em "Ferramentas Admin" > "Ver Logs do Sistema"
3. Procure por "topdesk" nos logs
4. Envie os logs para análise

### Problema: Botão "Salvar" não aparece

**Solução:**
- Role a página até o FINAL
- O botão está no final de TODAS as integrações
- Se não aparecer, recarregue a página (Ctrl+Shift+R)

### Problema: Configuração não persiste

**Solução:**
1. Verifique se o backend está rodando:
   ```bash
   docker ps | grep coruja-api
   ```
2. Verifique logs da API:
   ```bash
   docker logs coruja-api --tail 50
   ```

## 📝 Checklist Completo

- [ ] API reiniciada (`docker restart coruja-api`)
- [ ] Aguardou 10 segundos
- [ ] Frontend recarregado (Ctrl+Shift+R)
- [ ] TOPdesk ativado (toggle ligado)
- [ ] URL preenchida: `https://empresa.topdesk.net`
- [ ] Usuário preenchido: `coruja.monitor` (requisitante)
- [ ] Senha preenchida
- [ ] Grupo de Operadores preenchido (opcional mas recomendado)
- [ ] Rolou até o FINAL da página
- [ ] Clicou em "💾 Salvar Configurações"
- [ ] Viu mensagem de sucesso
- [ ] Voltou para seção TOPdesk
- [ ] Clicou em "Testar Criação de Chamado"
- [ ] Verificou resultado
- [ ] Verificou no TOPdesk:
  - [ ] Chamado criado
  - [ ] Requisitante: monitor.user
  - [ ] Grupo: Infraestrutura (se configurado)
  - [ ] Status: Novo/Em Andamento

## 🎉 Sucesso!

Se tudo funcionou:
1. ✅ Chamado de teste criado no TOPdesk
2. ✅ Requisitante correto: `coruja.monitor`
3. ✅ Grupo de operadores atribuído (se configurado)
4. ✅ Integração configurada e funcionando
5. ✅ Alertas críticos criarão chamados automaticamente

### Verifique no TOPdesk

Acesse: `https://empresa.topdesk.net`

Procure por: "Teste de Integração - Coruja Monitor"

Deve mostrar:
- **Requisitante**: coruja.monitor
- **Grupo**: Infraestrutura (se configurado)
- **Status**: Novo ou Em Andamento
- **Prioridade**: P2 - Normal

## 📞 Suporte

Se o problema persistir:
1. Tire um print da tela com o erro
2. Copie os logs da API
3. Verifique se consegue fazer login manual no TOPdesk
4. Envie as informações para análise

---

**Boa sorte! 🚀**
