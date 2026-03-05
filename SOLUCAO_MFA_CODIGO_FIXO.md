# 🔧 SOLUÇÃO: Google Authenticator Mostrando Código Fixo

## 🎯 Problema

Você cadastrou o MFA e o Google Authenticator está mostrando sempre o mesmo número, e o código não funciona no login.

## ✅ Diagnóstico

Executei um teste no servidor e o TOTP está funcionando corretamente:

```
✅ TOTP está funcionando corretamente!
Código atual do servidor: 812966
Sistema: Linux
Hora: 2026-03-04 16:22:50
Intervalo: 30 segundos
```

## 🔍 Causa do Problema

O Google Authenticator mostra sempre o mesmo número quando:

1. **QR Code escaneado múltiplas vezes**: Você pode ter escaneado o mesmo QR Code várias vezes, criando entradas duplicadas
2. **QR Code antigo**: Você pode ter escaneado um QR Code de uma configuração anterior
3. **Relógio dessincronizado**: O relógio do smartphone está muito diferente do servidor
4. **Conta errada**: Você está olhando para a conta errada no Google Authenticator

## ✅ SOLUÇÃO COMPLETA

### Passo 1: Limpar Google Authenticator

1. Abra o **Google Authenticator**
2. Encontre a conta **"CorujaMonitor"** ou **"admin@coruja.com"**
3. Toque e segure na conta
4. Selecione **"Remover"** ou **"Excluir"**
5. Confirme a remoção

**Se houver múltiplas contas "CorujaMonitor", remova TODAS!**

### Passo 2: Desabilitar MFA no Sistema

1. Acesse: http://localhost:3000
2. Faça login (use um código de backup se necessário)
3. Vá em: **Configurações** → **Segurança**
4. Role até **"🔐 Autenticação de Dois Fatores (MFA)"**
5. Clique em **"Desabilitar MFA"**
6. Digite sua senha
7. Digite um código de backup (exemplo: 1234-5678)
8. Confirme

**Códigos de backup que você recebeu**:
- Use qualquer um dos 10 códigos que foram gerados
- Formato: XXXX-XXXX (exemplo: 1234-5678)

### Passo 3: Habilitar MFA Novamente (LIMPO)

1. Na mesma página, clique em **"Habilitar MFA"**
2. Um NOVO QR Code será gerado
3. Um NOVO secret será criado
4. NOVOS códigos de backup serão gerados

### Passo 4: Escanear NOVO QR Code

1. Abra o Google Authenticator
2. Toque em **"+"** ou **"Adicionar conta"**
3. Escolha **"Escanear QR Code"**
4. Aponte para o NOVO QR Code na tela
5. A conta "CorujaMonitor" será adicionada
6. **Verifique se o código está MUDANDO a cada 30 segundos**

### Passo 5: Ativar MFA

1. Digite sua **senha**
2. Digite o **código de 6 dígitos** do Google Authenticator
3. Clique em **"Ativar MFA"**
4. ✅ MFA ativado!

### Passo 6: Testar Login

1. Faça logout
2. Faça login com email e senha
3. Sistema solicitará código MFA
4. Digite o código do Google Authenticator
5. ✅ Login bem-sucedido!

---

## 🚨 Se Não Conseguir Fazer Login

### Opção 1: Usar Código de Backup

Se você salvou os códigos de backup:

1. No campo "Código MFA", digite um código de backup
2. Formato: XXXX-XXXX (exemplo: 1234-5678)
3. Cada código funciona UMA VEZ apenas

### Opção 2: Desabilitar MFA via Banco de Dados

Se você não tem códigos de backup:

```powershell
# Execute este comando
.\desabilitar_mfa_todos.ps1
```

Ou manualmente:

```powershell
docker-compose exec -T postgres psql -U coruja -d coruja_monitor -c "UPDATE users SET mfa_enabled = FALSE, mfa_secret = NULL, mfa_backup_codes = NULL WHERE email = 'admin@coruja.com';"
```

---

## 🔍 Verificar Código Atual do Servidor

Para ver qual código o servidor está gerando:

```powershell
.\verificar_codigo_mfa.ps1
```

Isso mostrará:
- Código atual do servidor
- Códigos dos próximos 30 segundos
- Informações de diagnóstico

Compare com o código no Google Authenticator:
- **Se forem IGUAIS**: Problema de sincronização de relógio
- **Se forem DIFERENTES**: QR Code errado, refaça o processo

---

## ⏰ Sincronizar Relógio

### Android

1. Abra **Configurações**
2. Vá em **Sistema** → **Data e hora**
3. Ative **"Usar hora da rede"**
4. Ative **"Usar fuso horário da rede"**

### iOS

1. Abra **Ajustes**
2. Vá em **Geral** → **Data e Hora**
3. Ative **"Definir Automaticamente"**

### Google Authenticator

1. Abra o Google Authenticator
2. Toque nos **três pontos** (⋮)
3. Vá em **Configurações**
4. Toque em **Correção de hora para códigos**
5. Toque em **Sincronizar agora**

---

## 📊 Checklist de Solução

- [ ] Remover conta antiga do Google Authenticator
- [ ] Desabilitar MFA no sistema
- [ ] Habilitar MFA novamente (novo QR Code)
- [ ] Escanear NOVO QR Code
- [ ] Verificar se código está MUDANDO
- [ ] Salvar NOVOS códigos de backup
- [ ] Ativar MFA com senha + código
- [ ] Testar login
- [ ] Sincronizar relógio do smartphone
- [ ] Verificar código do servidor vs Google Authenticator

---

## 🎯 Resumo Rápido

**Problema**: Código fixo no Google Authenticator

**Solução**:
1. Remover conta do Google Authenticator
2. Desabilitar MFA no sistema
3. Habilitar MFA novamente
4. Escanear NOVO QR Code
5. Verificar se código muda a cada 30s
6. Ativar e testar

**Scripts úteis**:
- `verificar_codigo_mfa.ps1` - Ver código atual do servidor
- `desabilitar_mfa_todos.ps1` - Desabilitar MFA (emergência)

---

## 📞 Comandos Úteis

```powershell
# Ver código atual do servidor
.\verificar_codigo_mfa.ps1

# Desabilitar MFA de todos os usuários
.\desabilitar_mfa_todos.ps1

# Desabilitar MFA de um usuário específico
docker-compose exec -T postgres psql -U coruja -d coruja_monitor -c "UPDATE users SET mfa_enabled = FALSE WHERE email = 'admin@coruja.com';"

# Ver status MFA dos usuários
docker-compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT email, mfa_enabled FROM users;"

# Ver secret do usuário (para debug)
docker-compose exec -T postgres psql -U coruja -d coruja_monitor -c "SELECT email, mfa_secret FROM users WHERE mfa_enabled = TRUE;"
```

---

## ✅ Resultado Esperado

Após seguir os passos:

1. ✅ Google Authenticator mostra código MUDANDO a cada 30s
2. ✅ Código do Google Authenticator = Código do servidor
3. ✅ Login funciona com código MFA
4. ✅ Códigos de backup salvos
5. ✅ MFA funcionando perfeitamente

---

**Data**: 04/03/2026  
**Status**: ✅ SOLUÇÃO DOCUMENTADA  
**Autor**: Kiro AI Assistant
