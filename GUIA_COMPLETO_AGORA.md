# 🚀 GUIA COMPLETO - AUTO-REGISTRO DE SERVIDOR

## 📋 SITUAÇÃO ATUAL

✅ Código implementado:
- `probe/probe_core.py` - Método `_auto_register_server()`
- `api/routers/servers.py` - Endpoints `/check` e `/auto-register`
- `frontend/src/components/Probes.js` - Correção do copyToken()
- `probe/config.yaml` - Configurado com porta 3000

❌ Código NÃO está no GitHub ainda
❌ Servidor Linux NÃO tem as alterações
❌ Probe configurada mas não iniciada

## 🎯 OBJETIVO

Fazer a probe criar o servidor automaticamente quando iniciar.

---

## 📝 PASSO A PASSO

### PASSO 1: Commit e Push para GitHub

**Opção A: Executar script automático**
```bash
# Clique duas vezes em:
EXECUTAR_TUDO_SEQUENCIA.bat
```

**Opção B: Manual no Git Bash**
```bash
cd "/c/Users/andre.quirino/Coruja Monitor"
git add .
git commit -m "Auto-registro de servidor e correcao de copia de token"
git push origin master
```

**O que vai ser enviado:**
- ✅ Auto-registro de servidor (probe_core.py)
- ✅ Endpoints da API (servers.py)
- ✅ Correção do copyToken (Probes.js)
- ✅ Config.yaml com porta 3000

---

### PASSO 2: Atualizar Servidor Linux

**Conectar via SSH:**

**Opção A: PowerShell/CMD**
```powershell
ssh root@192.168.31.161
```

**Opção B: PuTTY**
- Host: 192.168.31.161
- Port: 22
- Login: root

**Após conectar, executar:**
```bash
cd /home/administrador/CorujaMonitor
git pull origin master
docker-compose restart
```

**Aguardar 30 segundos** para containers reiniciarem.

**Verificar:**
```bash
docker-compose ps
```

Deve mostrar:
```
api       Up
frontend  Up
postgres  Up
redis     Up
```

**Sair do SSH:**
```bash
exit
```

---

### PASSO 3: Iniciar Probe no Windows

**Executar:**
```
INICIAR_PROBE_DIRETO.bat
```

**O que vai acontecer:**

1. Script detecta Python
2. Inicia probe_core.py
3. Probe envia heartbeat
4. **Probe verifica se servidor existe**
5. **Servidor não existe → cria automaticamente**
6. Probe começa a coletar métricas

**Logs esperados:**
```
🔍 Checking if server 'SRVSONDA001' is registered...
📝 Auto-registering server 'SRVSONDA001'...
✅ Server 'SRVSONDA001' registered successfully! (ID: 1)
   IP: 192.168.31.161
   OS: Windows 10
```

---

### PASSO 4: Verificar no Dashboard

**Acessar:**
```
http://192.168.31.161:3000
```

**Login:**
- Email: admin@coruja.com
- Senha: admin123

**Verificar:**

1. **Menu → Servidores**
   - Deve aparecer: **SRVSONDA001**
   - Status: Online (verde)
   - IP: 192.168.31.161

2. **Menu → Sensores**
   - Deve ter 7 sensores criados automaticamente:
     - PING
     - cpu_usage
     - memory_usage
     - disk_C_
     - uptime
     - network_in
     - network_out

3. **Menu → Dashboard**
   - Gráficos devem começar a aparecer em 1 minuto

---

## 🔧 TROUBLESHOOTING

### Problema: Git não encontrado

**Solução:**
```bash
# Abra Git Bash e execute:
cd "/c/Users/andre.quirino/Coruja Monitor"
./COMMIT_E_PUSH_AGORA.sh
```

---

### Problema: SSH não conecta

**Solução 1: Verificar se SSH está rodando**
```bash
# No servidor Linux:
sudo systemctl status ssh
```

**Solução 2: Usar PuTTY**
- Baixe: https://www.putty.org/
- Host: 192.168.31.161
- Port: 22

---

### Problema: Servidor não foi criado

**Verificar logs da probe:**
```
# Na janela do INICIAR_PROBE_DIRETO.bat
# Procure por:
"✅ Server 'SRVSONDA001' registered successfully!"
```

**Se não aparecer:**

1. Verificar se API está rodando:
   ```
   http://192.168.31.161:3000/api/v1/health
   ```

2. Verificar se token está correto:
   ```yaml
   # probe/config.yaml
   token: "V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY"
   ```

3. Verificar se probe existe no dashboard:
   - Menu → Probes
   - Deve ter: Datacenter (empresa Techbiz)

---

### Problema: Métricas não aparecem

**Aguardar 1 minuto** (intervalo de coleta)

**Verificar logs:**
```
Sent X metrics successfully
```

**Se não aparecer:**

1. Verificar se servidor foi criado:
   - Menu → Servidores
   - Deve ter: SRVSONDA001

2. Verificar se sensores foram criados:
   - Menu → Sensores
   - Filtrar por: SRVSONDA001

---

## 📊 FLUXO COMPLETO

```
1. Probe inicia
   ↓
2. Envia heartbeat
   ↓
3. Chama _auto_register_server()
   ↓
4. GET /api/v1/servers/check
   ↓
5. Servidor não existe?
   ↓
6. POST /api/v1/servers/auto-register
   ↓
7. Servidor criado!
   ↓
8. Sensores criados automaticamente
   ↓
9. Probe coleta métricas
   ↓
10. Métricas aparecem no dashboard
```

---

## ✅ CHECKLIST

- [ ] Commit e push feito
- [ ] Linux atualizado (git pull)
- [ ] Containers reiniciados
- [ ] Probe iniciada no Windows
- [ ] Servidor SRVSONDA001 aparece no dashboard
- [ ] 7 sensores criados automaticamente
- [ ] Métricas aparecem nos gráficos

---

## 🎉 SUCESSO!

Quando tudo estiver funcionando:

✅ Servidor criado automaticamente
✅ Sensores criados automaticamente
✅ Métricas coletadas automaticamente
✅ Dashboard mostrando dados

**Nenhuma intervenção manual necessária!**

---

## 📞 PRÓXIMOS PASSOS

Após confirmar que está funcionando:

1. Adicionar mais servidores
2. Configurar alertas
3. Personalizar thresholds
4. Criar dashboards customizados

---

## 📝 ARQUIVOS CRIADOS

- `COMMIT_E_PUSH_AGORA.sh` - Script para commit/push
- `ATUALIZAR_LINUX_AGORA.sh` - Script para atualizar Linux
- `EXECUTAR_TUDO_SEQUENCIA.bat` - Script completo
- `SOLUCAO_ERRO_SERVICO.txt` - Solução para erro de serviço
- `GUIA_COMPLETO_AGORA.md` - Este guia

---

## 🔗 LINKS ÚTEIS

- Dashboard: http://192.168.31.161:3000
- GitHub: https://github.com/Quirinodsg/CorujaMonitor
- Documentação: README.md

---

**Última atualização:** 09/03/2026
