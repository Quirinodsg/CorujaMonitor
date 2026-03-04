# ⚠️ AÇÃO URGENTE: Reiniciar Probe

## 🚨 PROBLEMA CRÍTICO

A probe **AINDA ESTÁ RODANDO COM CONFIGURAÇÃO ANTIGA**!

**Evidência:** Os logs mostram erro SSL acontecendo AGORA (12:45):
```
2026-02-19 12:45:09 - ERROR - Error sending heartbeat: [SSL: WRONG_VERSION_NUMBER]
```

## ❌ Por Que Sensor Está "Aguardando Dados"

```
PROBE (configuração antiga)
   ↓
Tenta usar HTTPS ❌
   ↓
Erro SSL ❌
   ↓
NÃO envia métricas ❌
   ↓
API não recebe dados ❌
   ↓
Sensor fica "Aguardando dados" ❌
```

## ✅ Solução (3 Passos Simples)

### Passo 1: ENCONTRAR A JANELA DA PROBE

Procure uma janela de terminal/PowerShell/CMD que mostra logs como:
```
ERROR - Error sending heartbeat: [SSL: WRONG_VERSION_NUMBER]
```

**Essa é a janela da probe!**

### Passo 2: PARAR A PROBE

**Na janela da probe, pressione:**
```
Ctrl + C
```

Aguarde até aparecer:
```
Coruja Probe stopped
```

### Passo 3: INICIAR PROBE ATUALIZADA

**Na mesma janela, digite:**
```bash
python probe_core.py
```

E pressione Enter.

## ✅ Como Saber Se Funcionou

### Logs CORRETOS (após reiniciar):
```
2026-02-19 15:50:00 - INFO - Coruja Probe started
2026-02-19 15:50:00 - INFO - Initialized 10 collectors
2026-02-19 15:50:00 - INFO - Sending heartbeat to API
2026-02-19 15:51:00 - INFO - Sent 112 metrics successfully
```

**SEM ERRO SSL!**

### Logs ERRADOS (ainda com problema):
```
ERROR - Error sending heartbeat: [SSL: WRONG_VERSION_NUMBER]
```

**Se ainda aparecer erro SSL, a probe não foi reiniciada!**

## 🎯 Resultado Esperado

### Após 2 Minutos

1. **Logs da probe:**
   ```
   INFO - Sent 112 metrics successfully
   INFO - Coletadas 15 métricas Docker
   ```

2. **Frontend (após F5):**
   ```
   Sensor: Docker Containers Total
   Valor: 6 containers
   Status: OK ●
   ```

## 🔍 Verificação Rápida

### Comando 1: Ver se probe está rodando
```powershell
Get-Process python
```

### Comando 2: Ver últimos logs
```powershell
Get-Content probe\probe.log -Tail 10
```

**Deve mostrar:**
- ✅ "Sent X metrics successfully"
- ❌ NÃO deve ter "SSL: WRONG_VERSION_NUMBER"

## ⚠️ IMPORTANTE

**A probe PRECISA ser reiniciada!**

Não adianta:
- ❌ Recarregar o frontend
- ❌ Reiniciar containers Docker
- ❌ Esperar mais tempo

**Você DEVE:**
- ✅ Parar a probe (Ctrl+C)
- ✅ Iniciar novamente (python probe_core.py)

## 📊 Checklist

- [ ] Encontrei a janela da probe
- [ ] Vi os logs com erro SSL
- [ ] Pressionei Ctrl+C
- [ ] Vi "Coruja Probe stopped"
- [ ] Executei "python probe_core.py"
- [ ] Vi "Coruja Probe started"
- [ ] Vi "Initialized 10 collectors"
- [ ] NÃO vi erro SSL
- [ ] Aguardei 2 minutos
- [ ] Recarreguei frontend (F5)
- [ ] Sensor mostra dados

## 🎬 Passo a Passo Visual

```
1. ENCONTRAR JANELA
   ↓
   Procure janela com logs de erro SSL
   
2. PARAR
   ↓
   Ctrl + C
   
3. AGUARDAR
   ↓
   "Coruja Probe stopped"
   
4. INICIAR
   ↓
   python probe_core.py
   
5. VERIFICAR
   ↓
   "Coruja Probe started"
   "Initialized 10 collectors"
   SEM erro SSL
   
6. AGUARDAR
   ↓
   2 minutos
   
7. RECARREGAR
   ↓
   F5 no frontend
   
8. SUCESSO
   ↓
   Sensor mostra dados ✅
```

## 💡 Dica

Se você não encontrar a janela da probe:

1. Abra um novo terminal
2. Vá para pasta probe: `cd probe`
3. Execute: `python probe_core.py`
4. Deixe essa janela aberta

## 🚨 Resumo

**PROBLEMA:** Probe rodando com configuração antiga (HTTPS)
**CAUSA:** Probe não foi reiniciada após correções
**SOLUÇÃO:** Parar (Ctrl+C) e iniciar (python probe_core.py)
**TEMPO:** 30 segundos
**RESULTADO:** Sensor Docker funcionando

---

**AÇÃO IMEDIATA:** Vá até a janela da probe e pressione Ctrl+C AGORA!
