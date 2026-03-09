# Guia Completo: Reset e Reinstalação

## 📋 O QUE FOI IMPLEMENTADO

### 1. Sistema de Reset Completo
- ✅ Endpoint API: `/api/v1/system/reset` (POST)
- ✅ Interface no Frontend: Menu Ferramentas > Reset do Sistema
- ✅ Script Python: `api/reset_sistema.py`
- ✅ Apaga: métricas, incidentes, sensores, servidores, probes, empresas
- ✅ Mantém: usuário admin

### 2. Correções na Probe
- ✅ Porta corrigida: 3000 (não 8000)
- ✅ Script automático: `CONFIGURAR_TUDO_AUTOMATICO.bat`
- ✅ Adiciona servidor automaticamente via API
- ✅ Corrige config.yaml automaticamente

### 3. Instalador BAT Funcional
- ✅ Detecta Python automaticamente
- ✅ Instala dependências
- ✅ Copia arquivos da probe
- ✅ Cria atalhos
- ✅ Funciona fora do domínio

---

## 🔄 PASSO 1: RESETAR O SISTEMA

### Opção A: Via Interface Web (Recomendado)

1. Acesse: http://192.168.31.161:3000
2. Login: admin@coruja.com / admin123
3. Menu: **Ferramentas Administrativas**
4. Clique: **Reset do Sistema**
5. Veja as estatísticas atuais
6. Clique: **Resetar Sistema**
7. Digite: **RESETAR** (em maiúsculas)
8. Confirme

### Opção B: Via Linha de Comando (Linux)

```bash
cd /caminho/do/projeto
git pull origin main
cd api
python reset_sistema.py
```

---

## 🖥️ PASSO 2: INSTALAR PROBE NO WINDOWS

### Método Automático (Recomendado)

1. **Baixe os arquivos do Git** na máquina Windows

2. **Execute como Administrador:**
   ```
   CONFIGURAR_TUDO_AUTOMATICO.bat
   ```

3. **O script faz tudo automaticamente:**
   - Detecta Python
   - Corrige config.yaml (porta 3000)
   - Adiciona servidor no dashboard
   - Inicia a probe

4. **Mantenha a janela aberta** para ver os logs

### Método Manual (Se preferir)

1. **Corrigir config.yaml:**
   ```
   CORRIGIR_CONFIG_PROBE.bat
   ```

2. **Adicionar servidor:**
   ```
   ADICIONAR_SERVIDOR_AGORA.bat
   ```

3. **Iniciar probe:**
   ```
   EXECUTAR_PROBE_DIRETO.bat
   ```

---

## 📊 PASSO 3: VERIFICAR SE FUNCIONOU

### Na Janela da Probe

Você deve ver:
```
[INFO] Collecting metrics...
[INFO] Sent 15 metrics successfully
[INFO] Heartbeat sent successfully
```

### No Dashboard

1. Aguarde 60-90 segundos
2. Acesse: http://192.168.31.161:3000
3. Menu: **Servidores**
4. Clique em: **WIN-15GM8UTRS4K**
5. Verifique:
   - CPU %
   - Memória %
   - Disco %
   - Gráficos com dados

---

## 🔧 FERRAMENTAS ADMINISTRATIVAS

### Reset do Sistema

**Localização:** Menu > Ferramentas Administrativas > Reset do Sistema

**Funcionalidades:**
- Ver estatísticas atuais do sistema
- Resetar tudo com confirmação
- Apagar empresas, probes, sensores, servidores
- Manter usuário admin

**Segurança:**
- Requer login como admin
- Confirmação digitando "RESETAR"
- Não pode ser desfeito

---

## 📁 ARQUIVOS CRIADOS

### Backend (API)
- `api/reset_sistema.py` - Script Python para reset
- `api/routers/system_reset.py` - Endpoint da API
- `api/main.py` - Atualizado com novo router

### Frontend
- `frontend/src/components/SystemReset.js` - Interface React
- `frontend/src/components/SystemReset.css` - Estilos

### Scripts Windows
- `CONFIGURAR_TUDO_AUTOMATICO.bat` - Faz tudo automaticamente
- `CORRIGIR_CONFIG_PROBE.bat` - Corrige config.yaml
- `ADICIONAR_SERVIDOR_AGORA.bat` - Adiciona servidor via API
- `adicionar_servidor_automatico.py` - Script Python usado

### Documentação
- `GUIA_RESET_E_REINSTALACAO.md` - Este arquivo
- `EXECUTAR_ISTO_AGORA.txt` - Guia rápido
- `PROBLEMA_CONFIG_VAZIO.txt` - Explicação do problema

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### Probe não envia métricas

**Causa:** config.yaml com campos vazios ou porta errada

**Solução:**
```
CORRIGIR_CONFIG_PROBE.bat
```

### Servidor não aparece no dashboard

**Causa:** Servidor não cadastrado

**Solução:**
```
ADICIONAR_SERVIDOR_AGORA.bat
```

### Não consigo excluir empresa/probe

**Causa:** Bug no frontend (cache)

**Solução:**
1. Use o Reset do Sistema
2. Ou execute: `python api/reset_sistema.py`

### Porta errada (8000 em vez de 3000)

**Causa:** Scripts antigos

**Solução:** Todos os scripts foram corrigidos para porta 3000

---

## 📝 NOTAS IMPORTANTES

1. **Porta do Dashboard:** 3000 (não 8000)
2. **Porta da API:** 3000 (mesma porta)
3. **Manter janela aberta:** A probe precisa rodar continuamente
4. **Aguardar 60-90s:** Tempo para primeira coleta de métricas
5. **Fora do domínio:** MSI funciona, mas dados não aparecem (use BAT)

---

## 🚀 PRÓXIMOS PASSOS

Após resetar e reinstalar:

1. ✅ Sistema limpo
2. ✅ Probe instalada e rodando
3. ✅ Servidor cadastrado
4. ✅ Métricas sendo coletadas

Agora você pode:
- Adicionar mais servidores
- Criar sensores personalizados
- Configurar alertas
- Visualizar dashboards

---

## 📞 COMANDOS RÁPIDOS

### No Windows (Git Bash)
```bash
# Baixar atualizações
git pull origin main

# Executar configuração automática
./CONFIGURAR_TUDO_AUTOMATICO.bat
```

### No Linux (Servidor)
```bash
# Baixar atualizações
cd /caminho/do/projeto
git pull origin main

# Resetar sistema
cd api
python reset_sistema.py

# Reiniciar serviços
docker-compose restart
```

---

## ✅ CHECKLIST

- [ ] Código enviado para Git
- [ ] Git pull no servidor Linux
- [ ] Reset do sistema executado
- [ ] Probe instalada no Windows
- [ ] Config.yaml corrigido
- [ ] Servidor adicionado
- [ ] Probe rodando
- [ ] Métricas aparecendo no dashboard

---

**Última atualização:** 09/03/2026
**Versão:** 1.0
