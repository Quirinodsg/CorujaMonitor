# CORREÇÕES IMPLEMENTADAS - 09/03/2026

## ✅ PROBLEMA 1: CD-ROM Aparecendo como Sensor

### Problema
- Unidade D: (CD-ROM) aparecia como sensor de disco
- Não deveria monitorar unidades de CD/DVD

### Solução Implementada
Atualizado `probe/collectors/disk_collector.py`:

```python
# Filtros adicionados:
1. Skip CD-ROM drives (cdrom in opts)
2. Skip drives with empty fstype
3. Skip drives with 0 total space
4. Melhor tratamento de OSError (CD sem disco)
```

### Como Testar
1. Reinicie a probe no Windows
2. Aguarde 60 segundos
3. Verifique dashboard: Disco D não deve aparecer mais

---

## ✅ PROBLEMA 2: Erro ao Excluir Sensor

### Problema
- Ao tentar excluir sensor: "Erro ao remover sensor: Network Error"
- Não pode ocorrer erro ao excluir

### Possíveis Causas
1. **CORS** - Backend não permite DELETE
2. **URL errada** - Frontend conectando na porta errada
3. **Timeout** - Requisição demora muito

### Solução Implementada
Melhorado tratamento de erro em `frontend/src/components/Servers.js`:

```javascript
// Agora mostra erro detalhado:
- Se servidor respondeu: mostra status code
- Se sem resposta: avisa que API não está rodando
- Logs detalhados no console do navegador
```

### Como Diagnosticar

#### 1. Abrir Console do Navegador
```
F12 → Console
```

#### 2. Tentar Excluir Sensor
- Clique no botão de excluir
- Veja os logs no console

#### 3. Verificar Erro
```
Se aparecer:
  "Tentando deletar sensor X..."
  "Error details: ..."
  
Copie e cole aqui para análise
```

---

## 🔧 PRÓXIMOS PASSOS

### 1. Commit e Push
```bash
git add probe/collectors/disk_collector.py
git add frontend/src/components/Servers.js
git commit -m "Filtrar CD-ROM e melhorar erro ao excluir sensor"
git push origin master
```

### 2. Atualizar Linux
```bash
ssh root@192.168.31.161
cd /home/administrador/CorujaMonitor
git pull origin master
docker-compose restart
```

### 3. Copiar Arquivo Atualizado para Produção (Windows)
```
Copie: probe/collectors/disk_collector.py
Para: C:\Program Files\CorujaMonitor\Probe\collectors\
```

### 4. Reiniciar Probe
```
C:\Program Files\CorujaMonitor\Probe\INICIAR_PROBE.bat
```

### 5. Testar Exclusão de Sensor
- Abra dashboard: http://192.168.31.161:3000
- Abra console (F12)
- Tente excluir um sensor
- Veja os logs no console

---

## 📊 VERIFICAÇÕES

### CD-ROM Filtrado?
```
✅ Disco C aparece
✅ Disco E aparece (se existir)
❌ Disco D (CD-ROM) NÃO aparece
```

### Exclusão Funciona?
```
Teste 1: Excluir sensor de disco
Teste 2: Excluir sensor de CPU
Teste 3: Excluir sensor de memória
```

---

## 🐛 SE ERRO PERSISTIR

### Erro: "Network Error"

**Causa Provável**: CORS não permite DELETE

**Solução**: Verificar `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # ← Deve incluir DELETE
    allow_headers=["*"],
)
```

### Erro: "404 Not Found"

**Causa**: Endpoint não existe

**Solução**: Verificar se endpoint está registrado:
```bash
docker-compose exec api python -c "from main import app; print([r.path for r in app.routes])"
```

### Erro: "401 Unauthorized"

**Causa**: Token inválido

**Solução**: Fazer logout e login novamente

---

## 📁 ARQUIVOS MODIFICADOS

1. `probe/collectors/disk_collector.py` - Filtrar CD-ROM
2. `frontend/src/components/Servers.js` - Melhor erro ao excluir

---

## 🎯 RESULTADO ESPERADO

### Antes
```
❌ Disco D (CD-ROM) aparece
❌ Erro genérico ao excluir: "Network Error"
```

### Depois
```
✅ Disco D (CD-ROM) NÃO aparece
✅ Erro detalhado ao excluir: "Sem resposta do servidor..."
✅ Logs no console para diagnóstico
```

---

**Última atualização**: 09/03/2026 - 16:30  
**Status**: Correções implementadas, aguardando commit/push
