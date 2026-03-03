# 🚨 REINICIAR PROBE AGORA

## Problema Atual

Os sensores ainda mostram timestamp antigo (25/02/2026, 14:41:25) porque a probe não está enviando métricas.

## Causa

A probe estava lendo o arquivo de configuração errado. Corrigi o código em `probe/config.py` mas você precisa reiniciar a probe para aplicar a correção.

## ✅ SOLUÇÃO IMEDIATA

### Passo 1: Pare a Probe Atual

No terminal onde a probe está rodando, pressione `Ctrl+C`

Ou execute:
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Passo 2: Inicie a Probe Corrigida

```powershell
python probe\probe_core.py
```

### Passo 3: Verifique os Logs

Você DEVE ver estas mensagens no início:

```
🔍 Procurando configuração em: probe\probe_config.json
✅ Configuração encontrada: probe\probe_config.json
📡 API URL: http://192.168.0.41:8000
🔑 Token: TvQ8v6wdYA...
⏱️  Intervalo: 60s
```

Se você NÃO ver essas mensagens, a correção não foi aplicada.

### Passo 4: Aguarde 60 Segundos

Após 60 segundos, você deve ver:
```
✅ Sent 372 metrics successfully
✅ Heartbeat sent successfully
```

### Passo 5: Verifique a Interface

Recarregue a página (Ctrl+F5) e verifique:
- Sensores devem mostrar timestamp ATUAL
- Incidentes devem fechar automaticamente
- Contador deve mostrar "0 Incidentes Abertos"

---

## 🔍 O Que Foi Corrigido

Modifiquei `probe/config.py` para procurar o arquivo de configuração em múltiplos locais:

1. Diretório atual (`probe_config.json`)
2. Subdiretório probe (`probe/probe_config.json`)
3. Mesmo diretório do arquivo config.py

Agora a probe encontra automaticamente o arquivo correto independente de onde você a executa.

---

## ⚠️ Se Ainda Não Funcionar

### Verificar se a correção foi aplicada

```powershell
Get-Content probe\config.py | Select-String -Pattern "possible_paths"
```

Deve mostrar:
```python
possible_paths = [
    Path(config_file),  # Current directory
    Path("probe") / config_file,  # probe subdirectory
    Path(__file__).parent / config_file,  # Same directory as this file
]
```

### Verificar arquivo de configuração

```powershell
Get-Content probe\probe_config.json
```

Deve mostrar:
```json
{
  "api_url": "http://192.168.0.41:8000",
  "probe_token": "TvQ8v6wdYAIhbtSdciuwbb8CP74LilEOMFSYL-4qWXk",
  ...
}
```

---

## 📊 Validação Final

Após reiniciar a probe e aguardar 60 segundos:

### 1. Sensores Atualizando
- ✅ Timestamp deve ser ATUAL (26/02/2026, hora atual)
- ✅ Status deve ser válido (OK/Warning/Critical)
- ✅ Valores devem ser atuais

### 2. Incidentes Fechados
- ✅ Contador: "0 Incidentes Abertos"
- ✅ Incidente de PING: "Resolvido"

### 3. NOC Funcionando
- ✅ Servidor visível
- ✅ Status verde (OK)
- ✅ IP correto (192.168.0.41)

---

**EXECUTE AGORA:**

```powershell
# 1. Parar probe
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Aguardar
Start-Sleep -Seconds 2

# 3. Iniciar probe corrigida
python probe\probe_core.py
```

Aguarde 60 segundos e recarregue a página!
