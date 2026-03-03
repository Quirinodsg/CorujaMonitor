# Atualizar Probe - Sensores Padrão

## Problema

Os sensores padrão não estão na ordem correta e o PING não está aparecendo.

## Ordem Esperada

1. ✅ Ping (8.8.8.8)
2. ✅ CPU
3. ✅ Memória
4. ✅ Disco C
5. ✅ Uptime
6. ✅ Network IN
7. ✅ Network OUT

## Solução

A probe precisa ser atualizada com o novo código que já está corrigido.

### Opção 1: Copiar Arquivos Manualmente (RECOMENDADO)

1. **Localize a pasta da probe instalada:**
   - Provavelmente em: `C:\Users\andre.quirino\OneDrive - Techbiz Forense Digital Ltda\Desktop\probe`
   - Ou onde você instalou a probe

2. **Copie os arquivos atualizados:**
   ```
   probe/probe_core.py → [pasta_instalacao]/probe_core.py
   probe/collectors/ping_collector.py → [pasta_instalacao]/collectors/ping_collector.py
   ```

3. **Reinicie a probe:**
   - Se estiver como serviço:
     ```cmd
     net stop CorujaProbe
     net start CorujaProbe
     ```
   
   - Se estiver rodando manualmente:
     - Feche a janela do Python
     - Execute novamente: `python main.py`

### Opção 2: Usar Script Automático

Na pasta da probe instalada, execute:

```cmd
atualizar_sensores.bat
```

### Opção 3: Reinstalar a Probe

Se as opções acima não funcionarem:

1. **Pare a probe:**
   ```cmd
   net stop CorujaProbe
   ```

2. **Delete o servidor no Coruja Monitor** (interface web)

3. **Execute o setup novamente:**
   ```cmd
   cd probe
   setup_wizard.bat
   ```

4. **Configure com os mesmos dados:**
   - URL da API: `http://localhost:8000`
   - Token da probe: (mesmo token anterior)

## Verificação

Após atualizar, aguarde 30 segundos e verifique na interface web:

✅ Deve aparecer 7 sensores na ordem:
1. Ping
2. CPU
3. Memória
4. Disco C
5. Uptime
6. Network IN
7. Network OUT

## Logs

Para verificar se está funcionando:

```cmd
cd [pasta_probe]
type probe.log
```

Deve aparecer:
```
Initialized 8 collectors
Collecting from PingCollector
Collecting from CPUCollector
...
```

## Troubleshooting

### Ping não aparece

- Verifique se o arquivo `collectors/ping_collector.py` existe
- Verifique se o `probe_core.py` tem a linha: `from collectors.ping_collector import PingCollector`
- Verifique se a probe foi reiniciada

### Ordem errada

- A ordem é definida no `probe_core.py` na função `_init_collectors()`
- Certifique-se de que copiou o arquivo atualizado
- Reinicie a probe

### Sensores duplicados

- Delete o servidor na interface web
- Reinstale a probe com o setup_wizard.bat

---

**IMPORTANTE:** A probe precisa ser atualizada na máquina onde está instalada, não no Docker!

O Docker roda apenas a API, Frontend e banco de dados. A probe roda separadamente na máquina que você quer monitorar.
