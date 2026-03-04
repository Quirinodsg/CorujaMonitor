# Índice de Instaladores - Atualizado 24/02/2026

## 🎯 NOVO: Instalador com Auto-Start

### ⭐ Recomendado: Instalador Completo
**Arquivo**: `probe/install_completo_com_servico.bat`

**Use quando**:
- Quer instalação profissional
- Não quer deixar janela aberta
- Quer auto-start com Windows
- Quer tudo configurado automaticamente

**Vantagens**:
- ✅ Detecta usuário automaticamente
- ✅ Configura tudo (Firewall, DCOM, WMI)
- ✅ Instala dependências
- ✅ Inicia probe automaticamente
- ✅ Configura auto-start
- ✅ Roda em segundo plano

**Como usar**:
```batch
# Botão direito → Executar como administrador
probe/install_completo_com_servico.bat
```

---

## 📋 Outros Instaladores

### 1. Instalador com Usuário Atual
**Arquivo**: `probe/install_usuario_atual.bat`

**Use quando**:
- Quer instalação rápida
- Não precisa de auto-start
- Vai iniciar manualmente

**Vantagens**:
- ✅ Detecta usuário atual
- ✅ Só pede senha
- ✅ Mais rápido

**Desvantagens**:
- ❌ Não inicia automaticamente
- ❌ Precisa deixar janela aberta

### 2. Instalador Sem Usuário
**Arquivo**: `probe/install_sem_usuario.bat`

**Use quando**:
- Quer configurar usuário depois
- Só quer criar template

**Vantagens**:
- ✅ Muito rápido
- ✅ Cria apenas template

**Desvantagens**:
- ❌ Precisa configurar usuário depois
- ❌ Não inicia automaticamente

### 3. Instalador Universal (Menu)
**Arquivo**: `probe/INSTALAR_AQUI.bat`

**Use quando**:
- Quer escolher tipo de ambiente
- Workgroup, Entra ID, Active Directory
- Quer mais opções

**Vantagens**:
- ✅ Menu com opções
- ✅ Detecta ambiente automaticamente
- ✅ Mais completo

**Desvantagens**:
- ❌ Mais demorado
- ❌ Não inicia automaticamente

### 4. Instalador Simples
**Arquivo**: `probe/install_simples.bat`

**Use quando**:
- Quer instalação básica
- Sem menu, direto ao ponto

### 5. Instalador Debug
**Arquivo**: `probe/install_debug.bat`

**Use quando**:
- Está tendo problemas
- Quer ver cada passo
- Precisa debugar

---

## 🔍 Utilitários

### Verificar Instalação
**Arquivo**: `probe/verificar_instalacao.bat`

**O que faz**:
- Verifica arquivos de configuração
- Verifica Python instalado
- Verifica dependências
- Verifica tarefa agendada
- Verifica probe rodando
- Mostra log

**Como usar**:
```batch
cd C:\Coruja Monitor\probe
verificar_instalacao.bat
```

### Verificar Tarefa Agendada
**Arquivo**: `probe/check_task.bat`

**O que faz**:
- Verifica se tarefa existe
- Verifica se Python está rodando
- Mostra log da probe
- Testa probe manualmente

### Iniciar Probe
**Arquivo**: `probe/start_probe.bat`

**O que faz**:
- Inicia probe manualmente
- Verifica Python e Docker
- Mostra output

### Diagnóstico
**Arquivo**: `probe/diagnostico_probe.bat`

**O que faz**:
- Diagnóstico completo
- Verifica tudo
- Mostra problemas

---

## 📊 Comparação de Instaladores

| Instalador | Auto-Start | Segundo Plano | Detecta User | Velocidade | Recomendado |
|------------|-----------|---------------|--------------|------------|-------------|
| `install_completo_com_servico.bat` | ✅ | ✅ | ✅ | Médio | ⭐⭐⭐⭐⭐ |
| `install_usuario_atual.bat` | ❌ | ❌ | ✅ | Rápido | ⭐⭐⭐ |
| `install_sem_usuario.bat` | ❌ | ❌ | ❌ | Muito Rápido | ⭐⭐ |
| `INSTALAR_AQUI.bat` (menu) | ❌ | ❌ | Depende | Lento | ⭐⭐⭐⭐ |
| `install_simples.bat` | ❌ | ❌ | ❌ | Rápido | ⭐⭐ |
| `install_debug.bat` | ❌ | ❌ | ❌ | Lento | ⭐ (debug) |

---

## 📖 Documentação

### Guias de Instalação
- `GUIA_RAPIDO_AUTO_START.md` - Guia rápido do novo instalador
- `COMO_INSTALAR_NOVA_PROBE.md` - Guia completo atualizado
- `GUIA_INSTALADOR_UNIVERSAL.md` - Guia do instalador universal
- `PASSO_A_PASSO_NOVA_EMPRESA.md` - Passo a passo completo

### Documentação Técnica
- `PROBE_AUTO_START_IMPLEMENTADO.md` - Detalhes técnicos do auto-start
- `ARQUITETURA_PRTG_AGENTLESS.md` - Arquitetura do sistema
- `ARQUITETURA_SENSORES_PROBE.md` - Arquitetura dos sensores

### Guias Específicos
- `GUIA_ENTRA_ID_AZURE_AD.md` - Para ambientes Entra ID
- `GUIA_MONITORAMENTO_SEM_DOMINIO.md` - Para workgroup
- `GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md` - Monitoramento agentless

### Resumos de Correções
- `RESUMO_CORRECOES_24FEV_PARTE2.md` - Implementação auto-start
- `RESUMO_CORRECOES_24FEV_FINAL.md` - Correções anteriores
- `CORRECOES_PROBE_EMPRESA_24FEV.md` - Correção probe/empresa

---

## 🎯 Fluxo de Decisão

```
Precisa instalar probe?
│
├─ Quer instalação profissional?
│  └─ SIM → install_completo_com_servico.bat ⭐
│
├─ Quer instalação rápida?
│  └─ SIM → install_usuario_atual.bat
│
├─ Quer escolher tipo de ambiente?
│  └─ SIM → INSTALAR_AQUI.bat (menu)
│
├─ Só quer template?
│  └─ SIM → install_sem_usuario.bat
│
└─ Está com problemas?
   └─ SIM → install_debug.bat
```

---

## 🚀 Recomendação Final

### Para Produção
Use: `install_completo_com_servico.bat`

**Por quê?**
- Instalação profissional
- Auto-start configurado
- Não precisa deixar janela aberta
- Reinicia automaticamente
- Mais confiável

### Para Teste Rápido
Use: `install_usuario_atual.bat`

**Por quê?**
- Instalação rápida
- Pode ver output
- Fácil de parar/reiniciar

### Para Debug
Use: `install_debug.bat`

**Por quê?**
- Mostra cada passo
- Pausa entre etapas
- Fácil de identificar problemas

---

## 📞 Suporte

### Problemas com Instalação?
1. Leia: `COMO_INSTALAR_NOVA_PROBE.md`
2. Execute: `verificar_instalacao.bat`
3. Execute: `diagnostico_probe.bat`
4. Veja log: `type probe.log`

### Probe não inicia?
1. Verifique Python: `python --version`
2. Instale dependências: `pip install -r requirements.txt`
3. Teste manualmente: `python probe_core.py`

### Sensores não aparecem?
1. Aguarde 2-3 minutos
2. Verifique log: `type probe.log`
3. Verifique conectividade: `ping 192.168.0.9`
4. Recarregue dashboard: Ctrl+Shift+R

---

**Use `install_completo_com_servico.bat` para instalação profissional!** 🚀
