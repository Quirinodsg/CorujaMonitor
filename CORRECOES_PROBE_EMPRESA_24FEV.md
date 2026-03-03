# Correções: Probe e Empresa - 24/Fev/2026

## 🔍 Problemas Reportados

1. **Probe vai para Default** em vez da empresa nova
2. **Sensores não aparecem** no dashboard
3. **Criar usuário trava** o instalador
4. **Usar usuário admin local** em vez de criar novo

---

## ✅ CORREÇÃO 1: Probe Indo para Default

### Problema
Quando admin cria probe em empresa nova, a probe vai para Default (tenant_id=1) em vez da empresa selecionada.

### Causa
Backend estava usando `current_user.tenant_id` (que é 1 para admin) em vez do `tenant_id` enviado pelo frontend.

### Solução Aplicada

**Arquivo**: `api/routers/probes.py`

```python
class ProbeCreate(BaseModel):
    name: str
    tenant_id: Optional[int] = None  # Admin pode especificar tenant_id

@router.post("/", response_model=ProbeResponse)
async def create_probe(
    probe: ProbeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Se admin especificou tenant_id, usar ele. Senão, usar do usuário atual
    if probe.tenant_id is not None and current_user.role == 'admin':
        tenant_id = probe.tenant_id
    else:
        tenant_id = current_user.tenant_id
    
    token = secrets.token_urlsafe(32)
    new_probe = Probe(
        tenant_id=tenant_id,  # Usa o tenant_id correto
        name=probe.name,
        token=token
    )
    db.add(new_probe)
    db.commit()
    db.refresh(new_probe)
    return new_probe
```

### Como Testar

1. Acesse http://192.168.0.9:3000
2. Vá em "Empresas"
3. Crie nova empresa (ex: "Teste")
4. Clique na empresa para expandir
5. Clique em "+ Nova Probe"
6. Crie probe (ex: "Probe Teste")
7. **Verifique**: Probe deve aparecer dentro da empresa "Teste", NÃO em Default

---

## ✅ CORREÇÃO 2: Instalador com Usuário Atual

### Problema
Instalador trava na criação de usuário. Usuário quer usar seu próprio usuário admin local.

### Solução Criada

**Arquivo**: `probe/install_usuario_atual.bat`

**O que faz:**
- ✅ Detecta automaticamente o usuário atual (`%USERNAME%`)
- ✅ Detecta automaticamente o computador (`%HOSTNAME%`)
- ✅ Solicita apenas a senha do usuário
- ✅ NÃO cria novo usuário
- ✅ Configura tudo usando o usuário atual

**Como usar:**
```batch
# Como Admin
cd "C:\Coruja Monitor\probe"
install_usuario_atual.bat

# Vai perguntar:
# - Senha do seu usuário
# - IP do servidor (192.168.0.9)
# - Token da probe
```

---

## ✅ CORREÇÃO 3: Sensores Não Aparecem

### Possíveis Causas

#### Causa 1: Probe Não Está Rodando
**Sintoma**: Sensores mostram "Desconhecido"

**Solução**:
```batch
cd "C:\Coruja Monitor\probe"
python probe_core.py
# Deixar janela aberta!
```

#### Causa 2: Probe Está na Empresa Errada
**Sintoma**: Servidor aparece mas em empresa errada

**Solução**:
1. Verificar qual empresa a probe está
2. Se estiver em Default, excluir e criar novamente
3. Usar a correção 1 (já aplicada)

#### Causa 3: Servidor Não Foi Criado
**Sintoma**: Nenhum servidor aparece

**Solução**:
- Probe cria servidor automaticamente ao enviar primeira métrica
- Aguarde 2-3 minutos após iniciar probe
- Verifique se probe está rodando

#### Causa 4: Filtro de Tenant
**Sintoma**: Admin não vê sensores de outras empresas

**Solução**: Já corrigido anteriormente - admin vê tudo

---

## 📋 Instaladores Disponíveis

### 1. install_usuario_atual.bat ⭐ RECOMENDADO
```
probe/install_usuario_atual.bat
```
- ✅ Usa seu usuário atual
- ✅ Detecta automaticamente
- ✅ Não cria novo usuário
- ✅ Não trava

### 2. install_sem_usuario.bat
```
probe/install_sem_usuario.bat
```
- ✅ Configura tudo menos usuário
- ✅ Cria template de credenciais
- ✅ Você edita depois

### 3. criar_usuario.bat
```
probe/criar_usuario.bat
```
- ✅ Cria usuário MonitorUser
- ✅ Atualiza credenciais automaticamente
- ✅ Usa com install_sem_usuario.bat

### 4. install_simples.bat
```
probe/install_simples.bat
```
- ✅ Instalação completa
- ⚠️ Cria novo usuário (pode travar)

---

## 🚀 Fluxo Recomendado Agora

### Passo 1: Criar Empresa e Probe (Interface Web)

1. Acesse http://192.168.0.9:3000
2. Login: admin@coruja.com / admin123
3. Menu: "Empresas"
4. Clique em "+ Nova Empresa"
5. Preencha nome e slug
6. Clique na empresa para expandir
7. Clique em "+ Nova Probe"
8. Digite nome da probe
9. **Copie o token** (Ctrl+C)

---

### Passo 2: Instalar Probe na Máquina

**Opção A - Usar Seu Usuário (RECOMENDADO)**:
```batch
cd "C:\Coruja Monitor\probe"
install_usuario_atual.bat

# Configure:
# - Senha do seu usuário
# - IP: 192.168.0.9
# - Token: [cole o token]
```

**Opção B - Criar Novo Usuário**:
```batch
cd "C:\Coruja Monitor\probe"
install_sem_usuario.bat
# Configure IP e token

# Depois:
criar_usuario.bat
# Cria MonitorUser
```

---

### Passo 3: Iniciar Probe

```batch
pip install -r requirements.txt
python probe_core.py
# Deixar janela aberta!
```

---

### Passo 4: Verificar no Dashboard

1. Acesse http://192.168.0.9:3000
2. Menu: "Servidores"
3. Aguarde 2-3 minutos
4. Servidor deve aparecer na empresa correta
5. Sensores devem aparecer com status real (não "Desconhecido")

---

## 🔧 Troubleshooting

### Probe Ainda Vai para Default?

**Verifique**:
1. API foi reiniciada? `docker restart coruja-api`
2. Frontend foi recarregado? Ctrl+Shift+R
3. Está criando probe pela interface de Empresas?

**Teste**:
```bash
# Verificar se correção foi aplicada
docker logs coruja-api --tail 50 | findstr "tenant_id"
```

---

### Sensores Não Aparecem?

**Checklist**:
- [ ] Probe está rodando? (janela aberta)
- [ ] Aguardou 2-3 minutos?
- [ ] Servidor aparece na lista?
- [ ] Servidor está na empresa correta?
- [ ] Recarregou navegador? (Ctrl+Shift+R)

**Verificar probe**:
```bash
# Na janela da probe, deve mostrar:
✓ Conectado à API: http://192.168.0.9:8000
✓ Probe autenticada: Nome-Da-Probe
✓ Coletando métricas...
  ✓ CPU: 15.2%
  ✓ Memória: 45.8%
  ...
```

---

### Instalador Trava na Senha?

**Solução**: Use `install_usuario_atual.bat` que só pede senha uma vez

**Ou**: Use `install_sem_usuario.bat` que pula criação de usuário

---

## 📊 Comparação de Instaladores

| Instalador | Cria Usuário | Detecta Atual | Trava? | Uso |
|------------|--------------|---------------|--------|-----|
| install_usuario_atual.bat | Não | Sim | Não | ⭐ Recomendado |
| install_sem_usuario.bat | Não | Não | Não | Configuração manual |
| criar_usuario.bat | Sim | Não | Não | Complemento |
| install_simples.bat | Sim | Não | Pode | Completo |

---

## ✅ Checklist de Verificação

### Backend
- [x] Correção aplicada em `api/routers/probes.py`
- [x] API reiniciada (`docker restart coruja-api`)
- [x] Probe aceita `tenant_id` do frontend

### Frontend
- [x] Já estava enviando `tenant_id` correto
- [x] Não precisa alteração

### Instaladores
- [x] `install_usuario_atual.bat` criado
- [x] Detecta usuário automaticamente
- [x] Não trava na criação de usuário

### Documentação
- [x] `CORRECOES_PROBE_EMPRESA_24FEV.md` criado
- [x] `INSTALACAO_EM_DUAS_ETAPAS.md` criado
- [x] Guias atualizados

---

## 🎯 Resumo das Correções

### Problema 1: Probe vai para Default
**Status**: ✅ Corrigido  
**Arquivo**: `api/routers/probes.py`  
**Ação**: Reiniciar API (`docker restart coruja-api`)  

### Problema 2: Instalador trava
**Status**: ✅ Resolvido  
**Arquivo**: `probe/install_usuario_atual.bat`  
**Ação**: Usar novo instalador  

### Problema 3: Sensores não aparecem
**Status**: ⚠️ Verificar  
**Causa**: Probe não está rodando  
**Ação**: Executar `python probe_core.py`  

---

## 📞 Arquivos Importantes

### Backend
```
api/routers/probes.py  ← Corrigido (aceita tenant_id)
```

### Instaladores
```
probe/install_usuario_atual.bat  ← Novo (usa usuário atual)
probe/install_sem_usuario.bat    ← Pula criação de usuário
probe/criar_usuario.bat          ← Cria usuário depois
```

### Documentação
```
CORRECOES_PROBE_EMPRESA_24FEV.md  ← Este arquivo
INSTALACAO_EM_DUAS_ETAPAS.md      ← Guia instalação
```

---

**Agora probe vai para empresa correta e instalador não trava!** 🚀
