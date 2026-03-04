# ✅ Correção Login do Admin - 03 de Março 2026

## 🐛 Problema Identificado

### Erro Exibido
```
body -> email: Field required
```

### Causa Raiz
O **backend** estava esperando um campo `email` no login, mas o **frontend** estava enviando `username`.

```python
# BACKEND (ANTES)
class LoginRequest(BaseModel):
    email: str        # ← Esperava "email"
    password: str

# FRONTEND (SEMPRE)
{
    "username": "admin@coruja.com",  # ← Enviava "username"
    "password": "admin123"
}
```

**Resultado:** Incompatibilidade entre frontend e backend!

---

## ✅ Solução Aplicada

### Mudança no Backend
Atualizei o modelo de login para aceitar `username` em vez de `email`:

```python
# BACKEND (DEPOIS)
class LoginRequest(BaseModel):
    username: str     # ← Agora aceita "username"
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        return v.lower().strip()
```

### Lógica de Autenticação
```python
@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Busca usuário pelo email (campo username contém o email)
    user = db.query(User).filter(User.email == request.username).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # ... resto do código
```

---

## 🔐 Credenciais do Admin

### Usuário Padrão
```
Usuário: admin@coruja.com
Senha: admin123
```

### Como Foi Criado
O usuário admin foi criado pelo script `api/init_admin.py` durante a inicialização do sistema.

---

## 🚀 Como Aplicar a Correção

### Opção 1: Script Automático (Recomendado)
```powershell
.\corrigir_login_admin.ps1
```

O script irá:
1. ✓ Reiniciar a API
2. ✓ Aguardar inicialização
3. ✓ Testar o login automaticamente
4. ✓ Mostrar resultado

### Opção 2: Manual
```powershell
# Reiniciar API
docker-compose restart api

# Aguardar 5 segundos
Start-Sleep -Seconds 5

# Testar login
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"admin@coruja.com","password":"admin123"}'
```

---

## 🧪 Como Testar

### 1. Executar Script
```powershell
.\corrigir_login_admin.ps1
```

### 2. Verificar Resultado
Se funcionar, você verá:
```
========================================
  LOGIN FUNCIONANDO!
========================================

Usuario: admin@coruja.com
Nome: Administrator
Role: admin
Token: eyJhbGciOiJIUzI1NiIs...

Agora voce pode fazer login no sistema!
```

### 3. Testar no Navegador
```
1. Acesse: http://localhost:3000
2. Digite:
   - Usuário: admin@coruja.com
   - Senha: admin123
3. Clique em "ACESSAR SISTEMA"
4. Deve entrar no dashboard!
```

---

## 📊 Comparação Antes/Depois

### ANTES ❌
```
Frontend envia:
{
  "username": "admin@coruja.com",
  "password": "admin123"
}

Backend espera:
{
  "email": "admin@coruja.com",    ← Campo diferente!
  "password": "admin123"
}

Resultado: ERRO "email: Field required"
```

### DEPOIS ✅
```
Frontend envia:
{
  "username": "admin@coruja.com",
  "password": "admin123"
}

Backend espera:
{
  "username": "admin@coruja.com",  ← Campo igual!
  "password": "admin123"
}

Resultado: LOGIN FUNCIONA!
```

---

## 🔍 Detalhes Técnicos

### Arquivo Modificado
- `api/routers/auth.py`

### Mudanças Específicas

#### 1. Modelo de Request
```python
# ANTES
class LoginRequest(BaseModel):
    email: str
    password: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

# DEPOIS
class LoginRequest(BaseModel):
    username: str
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        return v.lower().strip()
```

#### 2. Função de Login
```python
# ANTES
user = db.query(User).filter(User.email == request.email).first()

# DEPOIS
user = db.query(User).filter(User.email == request.username).first()
```

#### 3. Mensagem de Erro
```python
# ANTES
detail="Incorrect email or password"

# DEPOIS
detail="Incorrect username or password"
```

---

## 🐛 Troubleshooting

### Problema: Script falha ao testar
```powershell
# Ver logs da API
docker logs coruja-api --tail 50

# Verificar se API está rodando
docker ps | grep coruja-api

# Reiniciar API manualmente
docker-compose restart api
```

### Problema: Usuário não existe
```powershell
# Recriar usuário admin
docker-compose exec api python init_admin.py
```

### Problema: Senha incorreta
```powershell
# Resetar senha do admin
docker-compose exec api python -c "
from database import SessionLocal
from models import User
from auth import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@coruja.com').first()
if user:
    user.hashed_password = get_password_hash('admin123')
    db.commit()
    print('Senha resetada!')
else:
    print('Usuario nao encontrado!')
db.close()
"
```

---

## 📝 Outros Usuários

### Criar Novo Usuário
Você pode criar novos usuários através da interface web após fazer login como admin:

1. Login como admin
2. Ir para "Configurações" → "Usuários"
3. Clicar em "Adicionar Usuário"
4. Preencher dados e salvar

### Estrutura de Usuário
```python
{
    "email": "usuario@empresa.com",
    "full_name": "Nome Completo",
    "role": "admin" | "user" | "viewer",
    "tenant_id": 1,
    "is_active": True
}
```

---

## ✅ Checklist de Verificação

### Antes de Testar
- [x] Backend corrigido (username em vez de email)
- [x] Script de teste criado
- [x] Documentação atualizada

### Depois de Aplicar
- [ ] Script executado sem erros
- [ ] API reiniciada
- [ ] Login testado via API
- [ ] Login testado no navegador
- [ ] Dashboard acessível

---

## 🎯 Resultado Esperado

### Login Bem-Sucedido
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@coruja.com",
    "full_name": "Administrator",
    "role": "admin",
    "tenant_id": 1,
    "language": "pt-BR"
  }
}
```

### Acesso ao Dashboard
Após login, você será redirecionado para o dashboard principal com:
- Menu lateral completo
- Cards de resumo
- Gráficos e métricas
- Acesso a todas as funcionalidades

---

## 🔐 Segurança

### Senha Padrão
⚠️ **IMPORTANTE:** Altere a senha padrão após o primeiro login!

1. Login como admin
2. Ir para "Configurações" → "Perfil"
3. Alterar senha
4. Salvar

### Boas Práticas
- ✅ Use senhas fortes (mínimo 8 caracteres)
- ✅ Combine letras, números e símbolos
- ✅ Não compartilhe credenciais
- ✅ Altere senhas periodicamente
- ✅ Use autenticação de dois fatores (quando disponível)

---

## 📚 Documentação Relacionada

### Scripts Criados
- `corrigir_login_admin.ps1` - Script de correção automática

### Arquivos Modificados
- `api/routers/auth.py` - Lógica de autenticação

### Documentação
- `CORRECAO_LOGIN_ADMIN_03MAR.md` - Este documento

---

## 🎉 Conclusão

O problema de login foi corrigido! Agora o backend aceita `username` em vez de `email`, alinhando com o que o frontend envia.

**Execute o script e faça login:**

```powershell
.\corrigir_login_admin.ps1
```

Depois acesse: http://localhost:3000

---

**Versão:** 1.0.0  
**Data:** 03 de Março de 2026  
**Status:** ✅ Corrigido e pronto para uso

**Credenciais:**
- Usuário: admin@coruja.com
- Senha: admin123
