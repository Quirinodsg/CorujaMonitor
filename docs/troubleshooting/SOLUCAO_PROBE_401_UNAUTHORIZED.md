# SOLUÇÃO: Probe com 401 Unauthorized

## PROBLEMA IDENTIFICADO

Haviam **múltiplos processos da probe rodando simultaneamente**:
- `pythonservice.exe` (tarefa agendada)
- `python.exe` (processo 12972)
- `python.exe` (processo 22460)

Um deles estava usando o **token antigo**, causando erros 401 Unauthorized.

Além disso, o arquivo `probe_config.json` estava com:
- ❌ Token antigo: `W_YxHARNTlE3G8bxoXhWt0FknTPysGnKFX_visaP_G4`
- ❌ API URL antiga: `http://localhost:8000`

## SOLUÇÃO APLICADA

### 1. Arquivo de Configuração Corrigido

Atualizei `probe/probe_config.json` com:
```json
{
  "api_url": "http://192.168.30.189:8000",
  "probe_token": "TvQ8v6wdYAIhbtSdciuwbb8CP74LilEOMFSYL-4qWXk",
  "collection_interval": 60,
  "monitored_services": [],
  "udm_targets": []
}
```

### 2. Scripts Criados

#### `parar_todas_probes.bat` (EXECUTAR COMO ADMINISTRADOR)
Para todas as probes rodando:
- Para a tarefa agendada CorujaProbe
- Mata todos os processos python.exe
- Mata o processo pythonservice.exe
- Verifica se ainda há processos rodando

#### `iniciar_probe_limpo.bat`
Inicia a probe de forma limpa:
- Verifica se probe_config.json existe
- Verifica se já há probe rodando
- Inicia apenas UMA instância da probe
- Mostra instruções de verificação

## PASSOS PARA RESOLVER

### Passo 1: Parar Todas as Probes
```cmd
cd C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\Coruja Monitor\probe
```

**Clique com botão direito em `parar_todas_probes.bat`** e selecione **"Executar como administrador"**

Você deve ver:
```
[OK] Tarefa agendada parada
[OK] Processos python.exe finalizados
[OK] Processo pythonservice.exe finalizado
[OK] Nenhum processo Python rodando
```

### Passo 2: Iniciar Probe Limpa
Execute (não precisa ser admin):
```cmd
iniciar_probe_limpo.bat
```

Você deve ver:
```
[OK] Nenhuma probe rodando
[OK] Probe iniciada!
```

### Passo 3: Verificar Logs
Aguarde 60 segundos e verifique:
```cmd
Get-Content probe.log -Tail 20
```

Deve mostrar:
```
INFO - Sent 28 metrics successfully
HTTP Request: POST http://192.168.30.189:8000/api/v1/metrics/probe/bulk "HTTP/1.1 200 OK"
```

### Passo 4: Verificar API
```cmd
docker logs coruja-api --tail 20
```

Deve mostrar APENAS:
```
INFO: "POST /api/v1/metrics/probe/bulk HTTP/1.1" 200 OK
```

**NÃO deve ter mais 401 Unauthorized!**

### Passo 5: Verificar Dashboard
1. Abra http://192.168.30.189:3000
2. Faça login (admin@coruja.com / admin123)
3. Vá em "Sensores"
4. Aguarde 60 segundos
5. Recarregue a página (F5)

Os sensores devem mudar de:
- ❌ ❓ 28 Desconhecido
- ✅ ✅ 28 OK (ou com valores reais)

## POR QUE ESTAVA DANDO ERRO?

1. **Múltiplas probes rodando**: Uma com token antigo (401) e outra com token novo (200)
2. **Configuração desatualizada**: O arquivo `probe_config.json` não foi atualizado
3. **API URL errada**: Estava apontando para localhost em vez de 192.168.30.189

## COMO EVITAR NO FUTURO

### Sempre que mudar token ou IP:

1. **Pare TODAS as probes primeiro**:
   ```cmd
   parar_todas_probes.bat (como Admin)
   ```

2. **Atualize a configuração**:
   ```cmd
   configurar_probe.bat
   ```

3. **Inicie limpo**:
   ```cmd
   iniciar_probe_limpo.bat
   ```

### Para verificar se está tudo OK:

```cmd
# Ver processos Python rodando
tasklist | findstr python

# Deve mostrar APENAS 1 processo:
# python.exe    XXXXX Console    2    XX,XXX K
```

## COMANDOS ÚTEIS

```cmd
# Ver log em tempo real
Get-Content probe.log -Wait -Tail 10

# Ver últimas 50 linhas do log da API
docker logs coruja-api --tail 50

# Verificar se probe está enviando dados
Get-Content probe.log -Tail 5 | Select-String "Sent.*metrics"

# Verificar se API está aceitando (deve ser 200, não 401)
docker logs coruja-api --tail 10 | Select-String "probe/bulk"
```

## STATUS ESPERADO

Após seguir os passos:
- ✅ Apenas 1 processo Python rodando
- ✅ Probe enviando métricas a cada 60 segundos
- ✅ API respondendo 200 OK (não 401)
- ✅ Dashboard mostrando sensores com dados
- ✅ Status mudando de "Desconhecido" para "OK/Warning/Critical"

---

**Data**: 24/02/2026
**Problema**: Múltiplas probes com tokens diferentes
**Solução**: Parar todas, atualizar config, iniciar limpo
