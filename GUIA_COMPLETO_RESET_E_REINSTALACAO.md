# Guia Completo: Reset e Reinstalação

## 📋 Visão Geral

Este guia mostra como:
1. Fazer commit das alterações no Windows
2. Atualizar o servidor Linux
3. Resetar o sistema completamente
4. Reinstalar a probe automaticamente

---

## 🔄 PASSO 1: Commit no Windows

### Abra o Git Bash e execute:

```bash
cd /c/Users/Administrador/CorujaMonitor

git add .

git commit -m "Sistema de Reset Completo implementado"

git push origin master
```

**IMPORTANTE**: O branch é `master`, não `main`!

---

## 🐧 PASSO 2: Atualizar no Linux

### Copie e cole este comando no terminal Linux:

```bash
cd /home/administrador/CorujaMonitor && \
git fetch origin && \
git checkout master && \
git pull origin master && \
docker-compose restart
```

### Aguarde 30 segundos para os containers reiniciarem

---

## 🗑️ PASSO 3: Resetar o Sistema

### 3.1. Acesse o Dashboard

- URL: http://192.168.31.161:3000
- Login: admin@coruja.com
- Senha: admin123

### 3.2. Navegue até o Reset

1. Menu lateral → **Configurações**
2. Aba superior → **Ferramentas Admin**
3. Encontre o card **"Reset do Sistema"**
4. Clique no botão **"🗑️ Reset Completo"**

### 3.3. Confirme o Reset

1. Veja as estatísticas atuais (quantos itens serão apagados)
2. Leia o aviso de que a ação é irreversível
3. Digite: **RESETAR** (em maiúsculas)
4. Clique em **"Confirmar Reset"**

### 3.4. Aguarde a Conclusão

O sistema mostrará quantos itens foram apagados:
- ✗ X métricas
- ✗ X incidentes
- ✗ X sensores
- ✗ X servidores
- ✗ X probes
- ✗ X empresas

**Mantém**: Usuário admin

---

## 🔧 PASSO 4: Reinstalar a Probe (Windows)

### 4.1. Execute o Instalador Automático

No Windows, execute:

```
CONFIGURAR_TUDO_AUTOMATICO.bat
```

### 4.2. O que o script faz automaticamente:

1. ✓ Detecta Python instalado
2. ✓ Corrige config.yaml com token correto
3. ✓ Adiciona servidor via API
4. ✓ Inicia a probe

### 4.3. Dados Configurados Automaticamente:

- **Token**: qozrs7hP8ZcrzXc5odjHw60NVejB0RHIeTaFurorDE8
- **Nome da Probe**: WIN-15GM8UTRS4K
- **IP do Servidor**: 192.168.31.161
- **Porta**: 3000

---

## ✅ PASSO 5: Verificar Instalação

### 5.1. Verificar Probe no Dashboard

1. Acesse: http://192.168.31.161:3000
2. Menu → **Probes**
3. Deve aparecer: **WIN-15GM8UTRS4K** (Status: Ativo)

### 5.2. Verificar Servidor Cadastrado

1. Menu → **Servidores**
2. Deve aparecer: **WIN-15GM8UTRS4K**
3. Status: **Online**

### 5.3. Verificar Métricas

Aguarde 1-2 minutos e verifique:
1. Menu → **Dashboard**
2. Deve mostrar métricas de CPU, Memória, Disco

---

## 🚨 Solução de Problemas

### Problema: Empresa não foi apagada

**Solução**: Use o script Python direto no Linux:

```bash
cd /home/administrador/CorujaMonitor/api
python reset_sistema.py
cd ..
docker-compose restart
```

### Problema: Probe não conecta

**Solução**: Verifique o config.yaml:

```bash
# No Windows
notepad probe\config.yaml
```

Deve conter:
```yaml
token: "qozrs7hP8ZcrzXc5odjHw60NVejB0RHIeTaFurorDE8"
name: "WIN-15GM8UTRS4K"
api_url: "http://192.168.31.161:3000"
```

### Problema: Servidor não aparece

**Solução**: Execute o script de adicionar servidor:

```bash
# No Windows
ADICIONAR_SERVIDOR_AGORA.bat
```

---

## 📝 Resumo dos Arquivos Importantes

### Windows (Cliente)
- `CONFIGURAR_TUDO_AUTOMATICO.bat` - Instala probe automaticamente
- `ADICIONAR_SERVIDOR_AGORA.bat` - Adiciona servidor via API
- `CORRIGIR_CONFIG_PROBE.bat` - Corrige config.yaml
- `probe/config.yaml` - Configuração da probe

### Linux (Servidor)
- `api/reset_sistema.py` - Script de reset via linha de comando
- `api/routers/system_reset.py` - Endpoint de reset via API
- `frontend/src/components/SystemReset.js` - Interface de reset

---

## 🎯 Checklist Final

Após seguir todos os passos, verifique:

- [ ] Código commitado no GitHub (branch master)
- [ ] Servidor Linux atualizado (git pull)
- [ ] Containers reiniciados (docker-compose restart)
- [ ] Sistema resetado (empresas, probes, servidores apagados)
- [ ] Probe reinstalada no Windows
- [ ] Probe aparece no dashboard (Status: Ativo)
- [ ] Servidor cadastrado (Status: Online)
- [ ] Métricas sendo coletadas (CPU, Memória, Disco)

---

## 📞 Informações do Sistema

- **Servidor Linux**: 192.168.31.161
- **Dashboard**: http://192.168.31.161:3000
- **API**: http://192.168.31.161:3000/api/v1
- **Login**: admin@coruja.com / admin123
- **Branch Git**: master (não main!)
- **Repositório**: https://github.com/Quirinodsg/CorujaMonitor

---

## 🔐 Token da Probe

```
qozrs7hP8ZcrzXc5odjHw60NVejB0RHIeTaFurorDE8
```

**Guarde este token!** Ele é necessário para autenticar a probe.

---

**Última atualização**: 09/03/2026
