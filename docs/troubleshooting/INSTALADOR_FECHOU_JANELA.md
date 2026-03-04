# Solução: Instalador Fechou a Janela

## 🔍 Problema

Você executou `install.bat` e a janela fechou imediatamente.

---

## ✅ Solução Rápida

### Opção 1: Use o Novo Instalador (RECOMENDADO)

Criamos um instalador que força execução como admin:

```bash
# Duplo clique neste arquivo:
probe/INSTALAR_AQUI.bat
```

Este arquivo vai:
1. Verificar se você é admin
2. Se não for, pedir elevação (UAC)
3. Executar o instalador corretamente

---

### Opção 2: Executar Manualmente como Admin

1. **Abra CMD como Administrador**:
   - Pressione `Win + X`
   - Escolha "Prompt de Comando (Admin)" ou "Windows PowerShell (Admin)"

2. **Execute o instalador**:
```bash
cd C:\Coruja Monitor\probe
install.bat
```

---

### Opção 3: Clique com Botão Direito

1. Vá até a pasta: `C:\Coruja Monitor\probe\`
2. Encontre o arquivo: `install.bat`
3. **Clique com botão direito** no arquivo
4. Escolha: **"Executar como administrador"**

---

## 🎯 Por Que a Janela Fechou?

O instalador verifica se você tem privilégios de administrador logo no início:

```batch
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute como Administrador!
    pause
    exit /b 1
)
```

Se você **não** executou como admin:
- ❌ O instalador detecta
- ❌ Mostra erro
- ❌ Tenta fazer `pause`
- ❌ Mas a janela fecha antes de você ver

---

## 🚀 Solução Definitiva

Use o novo arquivo que criamos:

```
probe/INSTALAR_AQUI.bat
```

**Como usar:**
1. Duplo clique em `INSTALAR_AQUI.bat`
2. Janela UAC vai aparecer
3. Clique em **SIM**
4. Instalador vai abrir corretamente

---

## 📋 Checklist

Antes de executar o instalador:

- [ ] Você está na pasta correta? (`C:\Coruja Monitor\probe\`)
- [ ] Você executou como Administrador?
- [ ] Você tem o token da probe? (copie da interface web)
- [ ] Você sabe o IP do servidor? (192.168.0.9)

---

## 🔧 Teste Rápido

Para testar se você é admin, execute no CMD:

```bash
net session
```

**Se aparecer**:
```
Nome do computador    \\DESKTOP-...
Nome de usuário       ...
```
✅ Você é admin!

**Se aparecer**:
```
Acesso negado
```
❌ Você NÃO é admin - execute como admin!

---

## 📞 Arquivos Disponíveis

### Para Instalar Nova Probe

```
probe/INSTALAR_AQUI.bat          ← USE ESTE! (força admin)
probe/install.bat                ← Instalador universal
probe/install_entraid.bat        ← Específico Entra ID
probe/install_workgroup.bat      ← Específico Workgroup
```

### Documentação

```
GUIA_INSTALADOR_UNIVERSAL.md     ← Guia completo
PASSO_A_PASSO_NOVA_EMPRESA.md    ← Passo a passo
GUIA_RAPIDO_INSTALACAO.md        ← Guia rápido
```

---

## 🎉 Resumo

**Problema**: Janela fechou
**Causa**: Não executou como admin
**Solução**: Use `INSTALAR_AQUI.bat` (duplo clique)

---

**Agora tente novamente com `INSTALAR_AQUI.bat`!** 🚀
