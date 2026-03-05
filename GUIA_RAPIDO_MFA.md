# 🚀 GUIA RÁPIDO: Como Usar o MFA

## ✅ Sistema Atualizado!

O MFA agora está totalmente integrado ao sistema. Veja como usar:

---

## 📱 Passo a Passo

### 1. Acessar Configurações de MFA

1. Faça login no sistema: http://localhost:3000
2. Clique em **"Configurações"** no menu lateral
3. Clique na aba **"Segurança"**
4. Role a página até encontrar **"🔐 Autenticação de Dois Fatores (MFA)"**

### 2. Habilitar MFA

1. Clique no botão **"Habilitar MFA"**
2. O sistema irá gerar:
   - Um QR Code
   - Um código secreto (caso não consiga escanear)
   - 10 códigos de backup

### 3. Configurar Aplicativo Autenticador

**Opção A: Escanear QR Code** (Recomendado)
1. Abra o aplicativo no seu smartphone:
   - Google Authenticator
   - Microsoft Authenticator
   - Authy
2. Toque em "+" ou "Adicionar conta"
3. Escolha "Escanear QR Code"
4. Aponte a câmera para o QR Code na tela
5. A conta "CorujaMonitor" será adicionada

**Opção B: Inserir Código Manualmente**
1. No aplicativo, escolha "Inserir código manualmente"
2. Nome da conta: CorujaMonitor
3. Código: (copie o código exibido na tela)
4. Tipo: Baseado em tempo

### 4. Salvar Códigos de Backup

⚠️ **IMPORTANTE**: Guarde os códigos de backup em local seguro!

1. Clique em **"📋 Copiar Todos os Códigos"**
2. Cole em um gerenciador de senhas ou arquivo seguro
3. Você pode usar estes códigos se perder acesso ao smartphone

Exemplo de códigos:
```
1234-5678
8765-4321
5555-6666
...
```

### 5. Ativar MFA

1. Digite sua **senha da conta**
2. Digite o **código de 6 dígitos** do aplicativo autenticador
3. Clique em **"Ativar MFA"**
4. Pronto! MFA está ativo ✅

---

## 🔐 Login com MFA

Após habilitar o MFA, o processo de login muda:

### Passo 1: Login Normal
1. Digite seu email
2. Digite sua senha
3. Clique em "ACESSAR SISTEMA"

### Passo 2: Código MFA
1. O sistema solicitará o **Código MFA**
2. Abra o aplicativo autenticador
3. Digite o código de 6 dígitos exibido
4. Ou use um código de backup
5. Clique em "ACESSAR SISTEMA" novamente

**Exemplo de tela**:
```
┌─────────────────────────────────┐
│ Usuário: admin@example.com      │
│ Senha: ********                 │
│ Código MFA: [______]            │ ← NOVO!
│                                 │
│ Digite o código do seu          │
│ aplicativo autenticador ou      │
│ um código de backup             │
│                                 │
│ [ACESSAR SISTEMA]               │
└─────────────────────────────────┘
```

---

## 🔧 Gerenciar MFA

### Ver Status

Na página de Configurações → Segurança → MFA:

```
┌─────────────────────────────────────┐
│ ✅  Status: Habilitado              │
│     Códigos de backup restantes: 8  │
└─────────────────────────────────────┘
```

### Desabilitar MFA

1. Clique em **"Desabilitar MFA"**
2. Digite sua senha
3. Digite o código do aplicativo
4. Confirme

⚠️ **Aviso**: Desabilitar MFA torna sua conta menos segura!

### Regenerar Códigos de Backup

Se você usou muitos códigos ou quer novos:

1. Clique em **"Regenerar Códigos de Backup"**
2. Digite sua senha
3. Novos códigos serão gerados
4. Os códigos antigos serão invalidados

---

## 📱 Aplicativos Recomendados

### Google Authenticator
- **iOS**: https://apps.apple.com/app/google-authenticator/id388497605
- **Android**: https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2
- ✅ Simples e confiável
- ✅ Funciona offline

### Microsoft Authenticator
- **iOS**: https://apps.apple.com/app/microsoft-authenticator/id983156458
- **Android**: https://play.google.com/store/apps/details?id=com.azure.authenticator
- ✅ Backup na nuvem
- ✅ Notificações push

### Authy
- **iOS**: https://apps.apple.com/app/authy/id494168017
- **Android**: https://play.google.com/store/apps/details?id=com.authy.authy
- **Desktop**: https://authy.com/download/
- ✅ Sincronização multi-dispositivo
- ✅ Backup criptografado

---

## ❓ Problemas Comuns

### "Código MFA inválido"

**Causas**:
- Código expirou (códigos mudam a cada 30 segundos)
- Relógio do smartphone desincronizado
- Digitou errado

**Soluções**:
1. Aguarde o código mudar e tente novamente
2. Verifique se o relógio do smartphone está correto
3. Use um código de backup

### "Perdi meu smartphone"

**Solução**:
1. Use um dos códigos de backup
2. Após fazer login, desabilite o MFA
3. Configure novamente com novo dispositivo

### "Códigos de backup acabaram"

**Solução**:
1. Faça login com o último código
2. Vá em Configurações → Segurança → MFA
3. Clique em "Regenerar Códigos de Backup"
4. Salve os novos códigos

### "Não consigo escanear o QR Code"

**Solução**:
1. Use a opção "Inserir código manualmente"
2. Copie o código secreto exibido
3. Cole no aplicativo autenticador

---

## 🔒 Dicas de Segurança

### ✅ Faça

- ✅ Guarde os códigos de backup em local seguro
- ✅ Use um gerenciador de senhas
- ✅ Mantenha o aplicativo autenticador atualizado
- ✅ Configure MFA em todas as contas importantes
- ✅ Verifique regularmente os códigos de backup restantes

### ❌ Não Faça

- ❌ Não compartilhe códigos de backup
- ❌ Não tire foto dos códigos e deixe no celular
- ❌ Não use o mesmo código em múltiplas contas
- ❌ Não desabilite MFA sem motivo
- ❌ Não ignore avisos de segurança

---

## 📊 Verificar Usuários com MFA (Admin)

Se você é administrador, pode verificar quais usuários têm MFA ativo:

```sql
-- Conectar ao banco
docker-compose exec postgres psql -U coruja -d coruja

-- Ver usuários com MFA
SELECT 
    email, 
    full_name, 
    role, 
    mfa_enabled,
    CASE 
        WHEN mfa_backup_codes IS NOT NULL 
        THEN json_array_length(mfa_backup_codes)
        ELSE 0 
    END as backup_codes_remaining
FROM users
ORDER BY role, email;
```

---

## 🎯 Resumo

**Para Habilitar**:
1. Configurações → Segurança → MFA
2. Habilitar MFA
3. Escanear QR Code
4. Salvar códigos de backup
5. Ativar com senha + código

**Para Fazer Login**:
1. Email + Senha
2. Código MFA (6 dígitos)
3. Pronto!

**Para Emergências**:
- Use códigos de backup
- Cada código funciona uma vez
- Regenere quando acabarem

---

## 📞 Suporte

Se tiver problemas:

1. Verifique este guia
2. Consulte `MFA_IMPLEMENTADO.md` para detalhes técnicos
3. Verifique os logs: `docker logs coruja-api --tail 50`

---

**Data**: 04/03/2026  
**Versão**: 1.1.0  
**Status**: ✅ FUNCIONANDO
