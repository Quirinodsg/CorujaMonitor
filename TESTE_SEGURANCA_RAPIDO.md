# 🧪 Teste Rápido - Aba Segurança

## ✅ STATUS DA IMPLEMENTAÇÃO

- ✅ Migração do banco de dados: CONCLUÍDA
- ✅ API reiniciada: RODANDO
- ✅ Frontend rebuilded: COMPILADO COM SUCESSO
- ✅ Containers ativos: TODOS RODANDO

## 🚀 COMO TESTAR AGORA

### 1. Abrir o Sistema

```
URL: http://localhost:3000
Login: admin@coruja.com
Senha: admin123
```

### 2. Navegar até Segurança

1. Após login, clique em **"⚙️ Configurações"** no menu lateral esquerdo
2. Você verá várias abas no topo
3. Clique na aba **"🔐 Segurança"** (nova aba adicionada)

### 3. O Que Você Verá

A aba Segurança contém 8 seções configuráveis:

#### 🏢 LDAP / Active Directory
- Servidor, porta, SSL/TLS
- Base DN, Bind DN, senha
- Filtros de usuário e grupo
- Mapeamento de roles (Admin, User, Viewer)
- Botão "Testar Conexão LDAP"

#### ☁️ Azure AD (Microsoft Entra ID)
- Tenant ID, Client ID, Client Secret
- Redirect URI
- IDs dos grupos para roles
- Botão "Testar Azure AD"

#### 🔑 SAML 2.0 SSO
- Entity ID, SSO URL, SLO URL
- Certificado X.509
- Mapeamento de atributos
- Botão "Testar Configuração SAML"

#### 🔐 OAuth2 / OpenID Connect
- Suporte para múltiplos providers (Keycloak, Auth0, GitLab, GitHub)
- Client ID, Client Secret
- URLs de autorização, token e userinfo
- Botão "Testar OAuth2"

#### 🔒 MFA / 2FA
- Métodos: TOTP, SMS, E-mail
- Issuer para TOTP
- Obrigatoriedade para admins ou todos
- Toggle para ativar/desativar

#### 🔑 Política de Senha
- Comprimento mínimo (6-32)
- Requisitos: maiúsculas, minúsculas, números, especiais
- Expiração (0-365 dias)
- Prevenção de reutilização (0-24 senhas)

#### ⏱️ Gerenciamento de Sessões
- Timeout de sessão (5-1440 minutos)
- Sessões simultâneas máximas (1-10)
- Duração "Lembrar-me" (1-90 dias)

### 4. Testar Funcionalidades

#### Teste 1: Ativar LDAP
1. Na seção LDAP, clique no toggle para ativar
2. Preencha os campos:
   - Servidor: `ldap.exemplo.com`
   - Porta: `389`
   - Base DN: `dc=exemplo,dc=com`
   - Bind DN: `cn=admin,dc=exemplo,dc=com`
   - Senha: `senha123`
3. Role até o final da página
4. Clique em **"💾 Salvar Configurações de Segurança"**
5. Aguarde mensagem de sucesso

#### Teste 2: Configurar Política de Senha
1. Na seção "Política de Senha"
2. Altere comprimento mínimo para `12`
3. Marque todas as opções (maiúsculas, minúsculas, números, especiais)
4. Defina expiração para `90` dias
5. Defina prevenção de reutilização para `5`
6. Clique em **"💾 Salvar Configurações de Segurança"**

#### Teste 3: Ativar MFA
1. Na seção MFA, ative o toggle
2. Selecione método: `TOTP (Google Authenticator, Authy)`
3. Defina Issuer: `CorujaMonitor`
4. Marque "Obrigatório para Administradores"
5. Salve as configurações

#### Teste 4: Configurar Sessões
1. Na seção "Gerenciamento de Sessões"
2. Defina timeout para `480` minutos (8 horas)
3. Defina sessões simultâneas para `3`
4. Defina "Lembrar-me" para `30` dias
5. Salve as configurações

### 5. Verificar Salvamento

Após salvar, você pode:

1. **Recarregar a página** (F5)
2. Voltar para a aba **"🔐 Segurança"**
3. Verificar se as configurações foram mantidas

### 6. Testar API Diretamente (Opcional)

Se quiser testar a API diretamente:

```bash
# 1. Fazer login e obter token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@coruja.com","password":"admin123"}'

# 2. Usar o token retornado para acessar configurações
curl http://localhost:8000/api/v1/auth-config \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 🎯 CHECKLIST DE VALIDAÇÃO

- [ ] Consegui acessar http://localhost:3000
- [ ] Fiz login com admin@coruja.com / admin123
- [ ] Cliquei em "Configurações" no menu lateral
- [ ] Vi a nova aba "🔐 Segurança"
- [ ] Consegui ativar/desativar toggles
- [ ] Consegui preencher campos de texto
- [ ] Consegui salvar configurações
- [ ] Após recarregar, as configurações foram mantidas
- [ ] Não vi erros no console do navegador (F12)

## 🐛 TROUBLESHOOTING

### Aba Segurança não aparece
**Solução:**
```bash
# Limpar cache do navegador
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)

# Ou abrir em aba anônima
Ctrl + Shift + N (Chrome)
Ctrl + Shift + P (Firefox)
```

### Erro ao salvar configurações
**Verificar:**
1. Console do navegador (F12 > Console)
2. Logs da API: `docker-compose logs api --tail 50`
3. Token de autenticação válido

### Campos não aparecem ao ativar toggle
**Solução:**
- Aguarde 1-2 segundos após ativar o toggle
- Se não aparecer, desative e ative novamente
- Verifique console do navegador para erros

### Configurações não são salvas
**Verificar:**
1. Você está logado como admin?
2. Clicou no botão "Salvar" no final da página?
3. Aguardou a mensagem de sucesso?
4. Logs da API: `docker-compose logs api --tail 50`

## 📊 PRÓXIMOS PASSOS

### Fase Atual: Interface Funcional ✅
- Interface web completa
- Salvamento no banco de dados
- Validação de campos

### Próxima Fase: Implementação Real ⏳
- Conexão real com LDAP
- Autenticação via SAML
- Integração com Azure AD
- MFA funcional (TOTP, SMS, E-mail)
- Aplicação de políticas de senha

## 📞 SUPORTE

Se encontrar problemas:

1. **Verificar logs:**
   ```bash
   docker-compose logs api --tail 100
   docker-compose logs frontend --tail 100
   ```

2. **Reiniciar containers:**
   ```bash
   docker-compose restart api frontend
   ```

3. **Verificar banco de dados:**
   ```bash
   docker-compose exec api python migrate_auth_config.py
   ```

4. **Consultar documentação:**
   - `IMPLEMENTACAO_SEGURANCA_AUTH_04MAR.md`
   - `docs/LGPD_COMPLIANCE.md`
   - `docs/ISO27001_COMPLIANCE.md`

---

**Data:** 04 de Março de 2026  
**Status:** ✅ PRONTO PARA TESTE  
**Tempo estimado de teste:** 10-15 minutos
