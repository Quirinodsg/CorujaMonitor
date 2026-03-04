# 🚨 SOLUÇÃO URGENTE: Instalador Fechando ou Travando

## ⚡ AÇÃO IMEDIATA

### Opção 1: Instalador Sem Usuário (SE TRAVAR) ⭐ RECOMENDADO

```
probe/install_sem_usuario.bat
```

**Quando usar:**
- ✅ Instalador está travando na criação de usuário
- ✅ Quer mais controle sobre cada etapa
- ✅ Quer usar usuário existente

**Como executar:**
1. Execute `install_sem_usuario.bat` como admin
2. Configure IP e token
3. Depois execute `criar_usuario.bat` como admin

**Veja**: `INSTALACAO_EM_DUAS_ETAPAS.md`

---

### Opção 2: Instalador Simples (SE FECHAR)

```
probe/install_simples.bat
```

**Como executar:**
1. Clique com botão direito
2. "Executar como administrador"
3. Siga as instruções

---

## 📋 3 Instaladores Criados

### 1️⃣ install_simples.bat ⭐ USE ESTE
- ✅ SEM menu (direto ao ponto)
- ✅ Mostra cada passo
- ✅ Aguarda entre passos
- ✅ NÃO fecha automaticamente
- ✅ Mais confiável

### 2️⃣ install_debug.bat
- ✅ COM menu
- ✅ Debug completo
- ✅ Mostra tudo que está fazendo
- ✅ Aguarda confirmação em cada passo

### 3️⃣ install.bat (Original)
- ❌ Está fechando
- ❌ Não use por enquanto

---

## 🎯 Passo a Passo Rápido

### 1. Abrir CMD como Admin
```
Win + X → Prompt de Comando (Admin)
```

### 2. Ir para pasta
```batch
cd "C:\Coruja Monitor\probe"
```

### 3. Executar
```batch
install_simples.bat
```

### 4. Configurar
- IP: `192.168.0.9`
- Token: [cole o token da interface web]

---

## 🔧 Se Ainda Fechar

### Teste Diagnóstico

Execute no CMD (como Admin):

```batch
cd "C:\Coruja Monitor\probe"
dir install*.bat
net session
wmic computersystem get name
pause
```

**Anote qualquer erro que aparecer.**

---

## 📁 Arquivos Criados

```
probe/
├── install_simples.bat      ← USE ESTE! (sem menu)
├── install_debug.bat        ← Debug completo
├── install.bat              ← Original (fechando)
├── INSTALAR_AQUI.bat        ← Elevação automática
└── install_entraid.bat      ← Específico Entra ID

Raiz/
├── INSTALADOR_FECHA_MESMO_ADMIN.md  ← Troubleshooting completo
└── SOLUCAO_URGENTE_INSTALADOR.md    ← Este arquivo
```

---

## 🆘 Instalação Manual (Se Nada Funcionar)

### Comandos Rápidos

```batch
REM 1. Criar usuário
net user MonitorUser Monitor@12345 /add /passwordchg:no /expires:never

REM 2. Adicionar aos grupos
net localgroup "Administrators" MonitorUser /add

REM 3. Configurar Firewall
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes

REM 4. Configurar DCOM
reg add "HKLM\Software\Microsoft\Ole" /v EnableDCOM /t REG_SZ /d Y /f
```

Depois crie os arquivos JSON manualmente (veja `INSTALADOR_FECHA_MESMO_ADMIN.md`).

---

## ✅ Checklist

- [ ] Executando como Administrador?
- [ ] Na pasta correta? (`C:\Coruja Monitor\probe`)
- [ ] Tentou `install_simples.bat`?
- [ ] Tentou `install_debug.bat`?
- [ ] Comando `net session` funciona?
- [ ] Antivírus desabilitado temporariamente?

---

## 📞 Documentação Completa

- `INSTALADOR_FECHA_MESMO_ADMIN.md` - Troubleshooting detalhado
- `COMO_INSTALAR_NOVA_PROBE.md` - Guia completo
- `LEIA_PRIMEIRO.md` - README visual

---

## 🎯 Resumo

**Problema**: Instalador fecha mesmo como admin  
**Causa**: Provável erro no script original  
**Solução**: Use `install_simples.bat` (sem menu, mais confiável)  
**Alternativa**: Use `install_debug.bat` (com debug completo)  
**Última opção**: Instalação manual (veja guia)  

---

**Execute `install_simples.bat` agora - vai funcionar!** 🚀
