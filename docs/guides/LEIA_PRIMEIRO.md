# 🦉 LEIA PRIMEIRO - Coruja Monitor

## ⚡ AÇÃO RÁPIDA

### Instalador Fechou a Janela?

**Use este arquivo** (duplo clique):
```
probe/INSTALAR_AQUI.bat
```

✅ Força execução como administrador  
✅ Não fecha a janela  
✅ Funciona sempre  

---

## 🎯 O QUE VOCÊ QUER FAZER?

### 1️⃣ Instalar Probe em Nova Máquina

**Leia**: `COMO_INSTALAR_NOVA_PROBE.md`  
**Execute**: `probe/INSTALAR_AQUI.bat`  
**Configure**: IP `192.168.0.9` + Token da interface web  

---

### 2️⃣ Sensores Mostrando "Desconhecido"

**Problema**: Probe não está rodando  
**Solução**: Execute `iniciar_probe.bat`  
**Leia**: `SOLUCAO_SENSORES_DESCONHECIDOS.md`  

---

### 3️⃣ Ver Todos os Instaladores

**Leia**: `INDICE_INSTALADORES.md`  
**Opções**: Workgroup, Entra ID, Domínio, WMI Remoto, Auto  

---

### 4️⃣ Reinstalar Servidor do Zero

**Execute**: `reinstalar_servidor_completo.bat`  
**Leia**: `GUIA_REINSTALACAO_LIMPA.md`  

---

### 5️⃣ Sincronizar Entre Pastas

**Execute**: `sincronizar_pastas.bat`  
**Sincroniza**:
- `C:\Users\user\Coruja Monitor`
- `C:\Users\user\OneDrive - ...\Coruja Monitor`

---

## 📚 DOCUMENTAÇÃO COMPLETA

### Guias de Instalação
- `COMO_INSTALAR_NOVA_PROBE.md` ⭐ **COMECE AQUI**
- `GUIA_INSTALADOR_UNIVERSAL.md`
- `PASSO_A_PASSO_NOVA_EMPRESA.md`
- `GUIA_RAPIDO_INSTALACAO.md`

### Guias por Ambiente
- `GUIA_ENTRA_ID_AZURE_AD.md` ⭐ **SUA EMPRESA**
- `GUIA_MONITORAMENTO_SEM_DOMINIO.md`
- `GUIA_INSTALADOR_DOMINIO.md`

### Troubleshooting
- `INSTALADOR_FECHOU_JANELA.md`
- `SOLUCAO_SENSORES_DESCONHECIDOS.md`

### Índices
- `INDICE_INSTALADORES.md` - Todos os instaladores
- `INDICE_DOCUMENTACAO_20FEV.md` - Todas as correções

---

## 🔑 INFORMAÇÕES IMPORTANTES

### Acesso ao Sistema
```
URL: http://192.168.0.9:3000
Login: admin@coruja.com
Senha: admin123
```

### Sua Configuração
```
IP Servidor: 192.168.0.9
Ambiente: Entra ID (Azure AD)
Probe Token: W_YxHARNTlE3G8bxoXhWt0FknTPysGnKFX_visaP_G4
```

### Pastas do Projeto
```
Pasta 1: C:\Users\user\Coruja Monitor
Pasta 2: C:\Users\user\OneDrive - ...\Coruja Monitor
```

---

## 🚀 INSTALAÇÃO RÁPIDA (3 Passos)

### Passo 1: Copiar Token
1. Acesse http://192.168.0.9:3000
2. Empresas → + Nova Probe
3. Copie o token

### Passo 2: Instalar
1. Copie pasta `probe` para máquina nova
2. Duplo clique em `probe/INSTALAR_AQUI.bat`
3. Configure IP e token

### Passo 3: Iniciar
```bash
pip install -r requirements.txt
python probe_core.py
```

**Pronto!** Aguarde 2-3 minutos e veja no dashboard.

---

## 🆘 PROBLEMAS COMUNS

### ❌ Janela do Instalador Fechou
**Solução**: Use `probe/INSTALAR_AQUI.bat` (duplo clique)

### ❌ Sensores "Desconhecido"
**Solução**: Execute `iniciar_probe.bat`

### ❌ Probe Não Conecta
**Solução**: Verifique IP (192.168.0.9) e token

### ❌ Python Não Encontrado
**Solução**: Instale Python e marque "Add to PATH"

---

## 📊 ARQUITETURA

```
┌─────────────────────────────────────────────────────┐
│              Rede Local 192.168.0.0/24               │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────────┐      ┌───────────────────┐  │
│  │  Servidor          │      │  Máquina Cliente  │  │
│  │  192.168.0.9       │      │  192.168.0.X      │  │
│  │                    │      │                   │  │
│  │  ✓ Docker          │      │  ✓ Windows       │  │
│  │  ✓ Coruja API      │◄─────┤  ✓ Probe Python  │  │
│  │  ✓ Frontend        │      │  ✓ Coleta local  │  │
│  │  ✓ PostgreSQL      │      │  ✓ Envia HTTP    │  │
│  │                    │      │                   │  │
│  └────────────────────┘      └───────────────────┘  │
│         ▲                                            │
│         │                                            │
│         └─── http://192.168.0.9:3000                │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## ✅ CHECKLIST

### Sistema Funcionando?
- [ ] Acesso a http://192.168.0.9:3000
- [ ] Dashboard mostra servidores
- [ ] Sensores coletando (não "Desconhecido")
- [ ] Probe rodando (janela aberta)

### Pronto para Instalar Nova Probe?
- [ ] Token copiado da interface web
- [ ] Pasta probe copiada para máquina nova
- [ ] Python instalado na máquina nova
- [ ] Arquivo INSTALAR_AQUI.bat pronto

---

## 🎯 PRÓXIMOS PASSOS

1. **Se instalador fechou**: Use `probe/INSTALAR_AQUI.bat`
2. **Se sensores "Desconhecido"**: Execute `iniciar_probe.bat`
3. **Para nova probe**: Leia `COMO_INSTALAR_NOVA_PROBE.md`
4. **Para entender tudo**: Leia `INDICE_INSTALADORES.md`

---

**Dúvidas? Leia `COMO_INSTALAR_NOVA_PROBE.md` primeiro!** 🚀
