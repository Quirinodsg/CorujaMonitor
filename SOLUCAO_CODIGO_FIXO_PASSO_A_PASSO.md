# 🔧 SOLUÇÃO: Google Authenticator com Código Fixo - Passo a Passo

## 🎯 Problema Identificado

O Google Authenticator está mostrando sempre o mesmo número e não está rotacionando a cada 30 segundos.

## ✅ Diagnóstico Completo

Executei testes no servidor e confirmei:

```
✅ TOTP funcionando corretamente no servidor
✅ Códigos mudando a cada 30 segundos
✅ URI do QR Code no formato correto
✅ Secret válido: VUEBGGLYTDZ4SV5RGZOBFATY5P5EDZYU

Código atual do servidor: 478819
Próximo código: 471549
```

**Conclusão**: O problema NÃO é o servidor. O problema é o QR Code escaneado no Google Authenticator.

---

## 🚀 SOLUÇÃO COMPLETA - Siga Estes Passos

### PASSO 1: Limpar Google Authenticator ⚠️

**IMPORTANTE**: Você precisa remover TODAS as contas antigas antes de adicionar uma nova.

1. Abra o **Google Authenticator** no seu smartphone
2. Procure por contas com nome:
   - "CorujaMonitor"
   - "admin@coruja.com"
   - Qualquer conta relacionada ao sistema
3. Para cada conta encontrada:
   - Toque e segure na conta
   - Selecione **"Remover"** ou **"Excluir"**
   - Confirme a remoção
4. **Verifique se TODAS foram removidas**

---

### PASSO 2: Acessar o Sistema

1. Abra o navegador
2. Acesse: **http://localhost:3000**
3. Faça login:
   - Email: `admin@coruja.com`
   - Senha: sua senha
4. Se pedir código MFA:
   - Use um código de backup (formato: XXXX-XXXX)
   - OU execute o script: `.\desabilitar_mfa_todos.ps1`

---

### PASSO 3: Desabilitar MFA Atual

1. No sistema, clique no menu superior direito
2. Selecione **"Configurações"** ou **"Settings"**
3. Vá na aba **"Segurança"**
4. Role até encontrar **"🔐 Autenticação de Dois Fatores (MFA)"**
5. Se o MFA estiver habilitado:
   - Clique em **"Desabilitar MFA"**
   - Digite sua **senha**
   - Digite um **código de backup** (se tiver)
   - Clique em **"Confirmar"**

**Se não conseguir desabilitar**, execute no PowerShell:

```powershell
.\desabilitar_mfa_todos.ps1
```

---

### PASSO 4: Habilitar MFA Novamente (NOVO QR Code)

1. Na mesma página de Configurações > Segurança
2. Clique em **"Habilitar MFA"**
3. Um NOVO QR Code será gerado
4. **NÃO ESCANEIE AINDA!**

---

### PASSO 5: Sincronizar Relógio do Smartphone ⏰

**Antes de escanear o QR Code, sincronize o relógio:**

#### Android:
1. Abra **Configurações**
2. Vá em **Sistema** → **Data e hora**
3. Ative **"Usar hora da rede"**
4. Ative **"Usar fuso horário da rede"**

#### iOS:
1. Abra **Ajustes**
2. Vá em **Geral** → **Data e Hora**
3. Ative **"Definir Automaticamente"**

#### Google Authenticator:
1. Abra o **Google Authenticator**
2. Toque nos **três pontos** (⋮) no canto superior direito
3. Vá em **"Configurações"**
4. Toque em **"Correção de hora para códigos"**
5. Toque em **"Sincronizar agora"**
6. Aguarde a mensagem de confirmação

---

### PASSO 6: Escanear NOVO QR Code

1. No Google Authenticator, toque em **"+"** ou **"Adicionar conta"**
2. Escolha **"Escanear QR Code"**
3. Aponte a câmera para o QR Code na tela do computador
4. A conta **"CorujaMonitor"** será adicionada
5. **AGUARDE 5 SEGUNDOS**
6. **Observe o código no app**

---

### PASSO 7: Verificar se o Código Está MUDANDO ✅

**CRÍTICO**: Antes de ativar o MFA, verifique:

1. Olhe para o código no Google Authenticator
2. Anote o código: ____________
3. Aguarde 30 segundos
4. O código DEVE mudar para um número diferente
5. Aguarde mais 30 segundos
6. O código DEVE mudar novamente

**Se o código NÃO mudar:**
- ❌ Você escaneou o QR Code errado
- ❌ Volte ao PASSO 1 e refaça todo o processo
- ❌ Certifique-se de remover TODAS as contas antigas

**Se o código MUDAR a cada 30s:**
- ✅ Perfeito! Continue para o próximo passo

---

### PASSO 8: Comparar com o Servidor

Execute este comando no PowerShell:

```powershell
.\verificar_codigo_mfa.ps1
```

Você verá algo como:

```
Código atual do servidor: 478819
```

**Compare**:
- Código no Google Authenticator: ____________
- Código no servidor: 478819

**Devem ser IGUAIS** (ou muito próximos, considerando a janela de 30s)

**Se forem diferentes:**
- ❌ Você tem múltiplas contas no Google Authenticator
- ❌ Volte ao PASSO 1 e remova TODAS as contas

---

### PASSO 9: Salvar Códigos de Backup

1. Na tela de configuração do MFA, você verá 10 códigos de backup
2. **COPIE TODOS OS CÓDIGOS**
3. Salve em um local seguro:
   - Gerenciador de senhas
   - Arquivo criptografado
   - Papel guardado em local seguro
4. Formato dos códigos: XXXX-XXXX

**Exemplo**:
```
1234-5678
9012-3456
7890-1234
...
```

---

### PASSO 10: Ativar MFA

1. Digite sua **senha**
2. Digite o **código de 6 dígitos** do Google Authenticator
3. Clique em **"Ativar MFA"**
4. Aguarde a confirmação: **"MFA ativado com sucesso!"**

---

### PASSO 11: Testar Login

1. Clique em **"Sair"** ou **"Logout"**
2. Faça login novamente:
   - Email: `admin@coruja.com`
   - Senha: sua senha
3. Clique em **"ACESSAR SISTEMA"**
4. Sistema solicitará: **"Digite o código MFA"**
5. Abra o Google Authenticator
6. Digite o código de 6 dígitos
7. Clique em **"ACESSAR SISTEMA"** novamente
8. ✅ **Login bem-sucedido!**

---

## 🔍 Troubleshooting

### Problema: Código ainda não muda no Google Authenticator

**Solução**:
1. Remova a conta do Google Authenticator
2. Feche completamente o app (force stop)
3. Abra o app novamente
4. Adicione a conta novamente
5. Verifique se o código muda

### Problema: Código muda mas não funciona no login

**Possíveis causas**:
1. Relógio do smartphone dessincronizado
   - Solução: Sincronize conforme PASSO 5
2. Você está digitando o código errado
   - Solução: Digite com calma, verifique cada dígito
3. Código expirou enquanto você digitava
   - Solução: Aguarde o próximo código e digite rapidamente

### Problema: Não tenho códigos de backup

**Solução**:
```powershell
.\desabilitar_mfa_todos.ps1
```

Depois refaça todo o processo desde o PASSO 1.

---

## 📊 Checklist de Verificação

Antes de ativar o MFA, confirme:

- [ ] Removi TODAS as contas antigas do Google Authenticator
- [ ] Sincronizei o relógio do smartphone
- [ ] Sincronizei o Google Authenticator
- [ ] Escaneei o NOVO QR Code
- [ ] O código está MUDANDO a cada 30 segundos
- [ ] O código do app coincide com o código do servidor
- [ ] Salvei os códigos de backup
- [ ] Testei o login com MFA

---

## 🎯 Resumo Rápido

1. **Limpar**: Remover TODAS as contas antigas do Google Authenticator
2. **Sincronizar**: Relógio do smartphone e Google Authenticator
3. **Desabilitar**: MFA atual no sistema
4. **Habilitar**: MFA novamente (novo QR Code)
5. **Escanear**: NOVO QR Code
6. **Verificar**: Código está MUDANDO a cada 30s
7. **Comparar**: Código do app = código do servidor
8. **Salvar**: Códigos de backup
9. **Ativar**: MFA com senha + código
10. **Testar**: Login com MFA

---

## 📞 Scripts Úteis

```powershell
# Desabilitar MFA de todos os usuários
.\desabilitar_mfa_todos.ps1

# Verificar código atual do servidor
.\verificar_codigo_mfa.ps1

# Testar secret do usuário
docker-compose exec api python testar_secret_usuario.py

# Ver status MFA
docker-compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT email, mfa_enabled FROM users;"
```

---

## ✅ Resultado Esperado

Após seguir todos os passos:

1. ✅ Google Authenticator mostra código MUDANDO a cada 30s
2. ✅ Código do app = código do servidor
3. ✅ Login funciona com código MFA
4. ✅ Códigos de backup salvos
5. ✅ MFA funcionando perfeitamente

---

## 🎉 Sucesso!

Se você chegou até aqui e tudo funcionou, parabéns! Seu MFA está configurado corretamente.

**Lembre-se**:
- Guarde os códigos de backup em local seguro
- Não compartilhe o QR Code ou secret com ninguém
- Se trocar de smartphone, desabilite e reconfigure o MFA

---

**Data**: 04/03/2026  
**Status**: ✅ GUIA COMPLETO  
**Autor**: Kiro AI Assistant
