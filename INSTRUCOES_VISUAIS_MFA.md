# 📱 INSTRUÇÕES VISUAIS - Resolver Código Fixo no Google Authenticator

## 🎯 Problema

```
Google Authenticator
┌─────────────────────┐
│  CorujaMonitor      │
│                     │
│      123456  ⏱️     │  ← Código NÃO muda
│                     │
└─────────────────────┘
```

## ✅ Solução

### PASSO 1: Remover Contas Antigas

```
Google Authenticator
┌─────────────────────┐
│  CorujaMonitor      │  ← Toque e segure
│      123456  ⏱️     │
└─────────────────────┘
         ↓
┌─────────────────────┐
│  [ Remover ]        │  ← Clique aqui
│  [ Cancelar ]       │
└─────────────────────┘
```

**Remova TODAS as contas "CorujaMonitor"!**

---

### PASSO 2: Desabilitar MFA

```powershell
# Execute no PowerShell:
.\desabilitar_mfa_todos.ps1
```

```
✅ MFA desabilitado para todos os usuários
```

---

### PASSO 3: Acessar Sistema

```
Navegador
┌─────────────────────────────────┐
│  http://localhost:3000          │
└─────────────────────────────────┘

Login
┌─────────────────────────────────┐
│  Email: admin@coruja.com        │
│  Senha: ••••••••                │
│                                 │
│  [ ACESSAR SISTEMA ]            │
└─────────────────────────────────┘
```

---

### PASSO 4: Habilitar MFA

```
Configurações > Segurança
┌─────────────────────────────────┐
│  🔐 Autenticação de Dois        │
│     Fatores (MFA)               │
│                                 │
│  Status: ❌ Desabilitado        │
│                                 │
│  [ Habilitar MFA ]              │  ← Clique aqui
└─────────────────────────────────┘
```

---

### PASSO 5: Escanear NOVO QR Code

```
Tela do Sistema                    Google Authenticator
┌─────────────────────┐           ┌─────────────────────┐
│  Escaneie o QR Code │           │  [ + ]              │  ← Toque aqui
│                     │           │                     │
│  ███████████████    │           │  Escanear QR Code   │  ← Escolha
│  ███████████████    │  ────────>│  Inserir código     │
│  ███████████████    │           │                     │
│  ███████████████    │           └─────────────────────┘
│                     │
│  Secret:            │
│  VUEB...DZYU        │
└─────────────────────┘
```

---

### PASSO 6: Verificar se Código Está MUDANDO

```
Google Authenticator
┌─────────────────────┐
│  CorujaMonitor      │
│                     │
│      478819  ⏱️ 25s │  ← Aguarde 30 segundos
└─────────────────────┘
         ↓
         ↓ (30 segundos depois)
         ↓
┌─────────────────────┐
│  CorujaMonitor      │
│                     │
│      471549  ⏱️ 25s │  ← Código MUDOU! ✅
└─────────────────────┘
```

**Se o código NÃO mudar**: Volte ao PASSO 1!

---

### PASSO 7: Comparar com Servidor

```powershell
# Execute no PowerShell:
.\verificar_codigo_mfa.ps1
```

```
Servidor                          Google Authenticator
┌─────────────────────┐           ┌─────────────────────┐
│  Código atual:      │           │  CorujaMonitor      │
│                     │           │                     │
│      478819         │  ═══════> │      478819  ⏱️ 15s │
│                     │   IGUAL   │                     │
└─────────────────────┘           └─────────────────────┘
```

**Devem ser IGUAIS!** ✅

---

### PASSO 8: Salvar Códigos de Backup

```
Códigos de Backup
┌─────────────────────────────────┐
│  Salve estes códigos:           │
│                                 │
│  1234-5678                      │  ← Copie TODOS
│  9012-3456                      │
│  7890-1234                      │
│  ...                            │
│                                 │
│  [ Copiar Todos ]               │
└─────────────────────────────────┘
```

**Guarde em local seguro!**

---

### PASSO 9: Ativar MFA

```
Ativar MFA
┌─────────────────────────────────┐
│  Senha: ••••••••                │
│                                 │
│  Código MFA: 478819             │  ← Do Google Authenticator
│                                 │
│  [ Ativar MFA ]                 │  ← Clique aqui
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  ✅ MFA ativado com sucesso!    │
└─────────────────────────────────┘
```

---

### PASSO 10: Testar Login

```
Login
┌─────────────────────────────────┐
│  Email: admin@coruja.com        │
│  Senha: ••••••••                │
│                                 │
│  [ ACESSAR SISTEMA ]            │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  Digite o código MFA:           │
│                                 │
│  Código: 471549                 │  ← Do Google Authenticator
│                                 │
│  [ ACESSAR SISTEMA ]            │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│  ✅ Login bem-sucedido!         │
│                                 │
│  Bem-vindo ao Coruja Monitor    │
└─────────────────────────────────┘
```

---

## 🎉 Resultado Final

```
Google Authenticator
┌─────────────────────┐
│  CorujaMonitor      │
│                     │
│      471549  ⏱️ 15s │  ← Código MUDANDO ✅
└─────────────────────┘
         ↓
         ↓ (30 segundos)
         ↓
┌─────────────────────┐
│  CorujaMonitor      │
│                     │
│      892341  ⏱️ 25s │  ← Novo código ✅
└─────────────────────┘
```

**Tudo funcionando!** 🎉

---

## 🚨 Troubleshooting Visual

### Problema: Código não muda

```
❌ ERRADO                         ✅ CORRETO
┌─────────────────────┐           ┌─────────────────────┐
│  CorujaMonitor      │           │  CorujaMonitor      │
│      123456  ⏱️     │           │      478819  ⏱️ 15s │
│                     │           │                     │
│  (sempre o mesmo)   │           │  (muda a cada 30s)  │
└─────────────────────┘           └─────────────────────┘

Solução:
1. Remover conta
2. Escanear NOVO QR Code
```

---

### Problema: Múltiplas contas

```
❌ ERRADO                         ✅ CORRETO
┌─────────────────────┐           ┌─────────────────────┐
│  CorujaMonitor      │           │  CorujaMonitor      │
│      123456  ⏱️     │           │      478819  ⏱️ 15s │
├─────────────────────┤           └─────────────────────┘
│  CorujaMonitor      │
│      789012  ⏱️     │           (apenas UMA conta)
├─────────────────────┤
│  CorujaMonitor      │
│      345678  ⏱️     │
└─────────────────────┘

(múltiplas contas)

Solução:
1. Remover TODAS as contas
2. Adicionar apenas UMA
```

---

### Problema: Códigos diferentes

```
Servidor                          Google Authenticator
┌─────────────────────┐           ┌─────────────────────┐
│  Código atual:      │           │  CorujaMonitor      │
│                     │           │                     │
│      478819         │  ≠≠≠≠≠≠>  │      123456  ⏱️     │
│                     │ DIFERENTE │                     │
└─────────────────────┘           └─────────────────────┘

Solução:
1. Sincronizar relógio do smartphone
2. Sincronizar Google Authenticator
3. Remover e adicionar conta novamente
```

---

## 📞 Scripts Úteis

```powershell
# Script interativo (RECOMENDADO)
.\resolver_mfa_codigo_fixo.ps1

# Desabilitar MFA
.\desabilitar_mfa_todos.ps1

# Verificar código atual
.\verificar_codigo_mfa.ps1
```

---

## 📚 Documentação Completa

- `COMO_RESOLVER_CODIGO_FIXO.txt` - Resumo rápido
- `SOLUCAO_CODIGO_FIXO_PASSO_A_PASSO.md` - Guia detalhado
- `DIAGNOSTICO_MFA_COMPLETO_04MAR.md` - Diagnóstico técnico
- `RESUMO_FINAL_MFA_04MAR.md` - Resumo da implementação

---

**Data**: 04/03/2026  
**Status**: ✅ GUIA VISUAL COMPLETO  
**Autor**: Kiro AI Assistant
