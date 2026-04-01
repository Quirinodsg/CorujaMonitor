# Guia Rápido de Instalação - Coruja Monitor

## 🎯 Sua Configuração

### Máquina com Coruja (Servidor)
- **IP**: 192.168.0.9
- **Acesso Web**: http://192.168.0.9:3000
- **API**: http://192.168.0.9:8000
- **Sistema**: Docker rodando Coruja Monitor

### Outras Máquinas (Clientes a Monitorar)
- **IP**: 192.168.0.X (qualquer outra máquina na rede)
- **Sistema**: Windows (sem domínio, apenas workgroup)
- **Instalação**: Probe Python

---

## 🚀 Instalação em Outras Máquinas

### Passo 1: Copiar Pasta Probe

Da sua máquina (192.168.0.9), copie a pasta:
```
C:\Users\user\Coruja Monitor\probe\
```

Para a outra máquina:
```
C:\Coruja Monitor\probe\
```

**Dica**: Use compartilhamento de rede ou pendrive.

---

### Passo 2: Executar Instalador

Na outra máquina, abra CMD como **Administrador**:

```bash
cd C:\Coruja Monitor\probe
install_workgroup.bat
```

---

### Passo 3: Configurar Conexão

Quando o instalador perguntar:

```
Digite o IP do servidor Coruja Monitor:
IP (ex: 192.168.0.100): 192.168.0.9    ← SEU IP!

Digite o token da probe:
Token: [copie da interface web]
```

**Como pegar o token:**
1. Acesse http://192.168.0.9:3000
2. Login: admin@coruja.com / admin123
3. Vá em "Empresas"
4. Clique na empresa (ex: TENSO)
5. Clique em "+ Nova Probe"
6. Copie o token gerado

---

### Passo 4: Instalar Python

Se a máquina não tiver Python:

1. Baixe: https://www.python.org/downloads/
2. Instale marcando "Add Python to PATH"
3. Abra CMD e teste: `python --version`

---

### Passo 5: Instalar Dependências

```bash
cd C:\Coruja Monitor\probe
pip install -r requirements.txt
```

---

### Passo 6: Iniciar Probe

```bash
python probe_core.py
```

**Deixe a janela aberta!** A probe precisa rodar continuamente.

---

## 📊 Verificar no Dashboard

1. Acesse http://192.168.0.9:3000
2. Vá em "Servidores"
3. Aguarde 2-3 minutos
4. A nova máquina deve aparecer automaticamente!

---

## 🔧 Configuração Atual (Sua Máquina)

### Reinstalar Servidor Atual

Se quiser limpar e reinstalar o servidor atual (192.168.0.9):

```bash
# 1. Limpar tudo
reinstalar_servidor_completo.bat

# 2. Iniciar probe local
iniciar_probe.bat
```

---

## 📋 Arquitetura da Rede

```
┌─────────────────────────────────────────────────────┐
│              Rede Local 192.168.0.0/24               │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────────┐      ┌───────────────────┐  │
│  │  Sua Máquina       │      │  Outra Máquina    │  │
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

## ✅ Checklist de Instalação

### Na Sua Máquina (192.168.0.9)
- [x] Docker rodando
- [x] Coruja Monitor instalado
- [x] Acesso: http://192.168.0.9:3000
- [ ] Probe local rodando (execute `iniciar_probe.bat`)

### Em Outras Máquinas
- [ ] Copiar pasta `probe`
- [ ] Executar `install_workgroup.bat` (como Admin)
- [ ] Configurar IP: 192.168.0.9
- [ ] Configurar token da probe
- [ ] Instalar Python
- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Iniciar probe: `python probe_core.py`

---

## 🔥 Firewall

### Sua Máquina (192.168.0.9)

Liberar portas de entrada:
```bash
# Frontend
netsh advfirewall firewall add rule name="Coruja-Frontend" dir=in action=allow protocol=TCP localport=3000

# API
netsh advfirewall firewall add rule name="Coruja-API" dir=in action=allow protocol=TCP localport=8000
```

### Outras Máquinas

Já configurado pelo `install_workgroup.bat` automaticamente!

---

## 🆘 Troubleshooting

### Não consigo acessar http://192.168.0.9:3000

```bash
# Verificar se Docker está rodando
docker ps

# Verificar se containers estão UP
docker ps | findstr coruja

# Reiniciar se necessário
docker-compose restart
```

### Probe não conecta

```bash
# Testar conectividade
ping 192.168.0.9

# Testar API
curl http://192.168.0.9:8000/health

# Verificar probe_config.json
type probe_config.json
```

### Máquina não aparece no dashboard

1. Aguarde 2-3 minutos
2. Verifique se probe está rodando
3. Faça Ctrl+Shift+R no navegador
4. Verifique logs da probe

---

## 📝 Resumo dos IPs Corretos

- **Servidor Coruja**: 192.168.0.9
- **Frontend**: http://192.168.0.9:3000
- **API**: http://192.168.0.9:8000
- **Outras máquinas**: 192.168.0.X (qualquer IP da sua rede)

---

## 🎉 Pronto!

Agora você pode monitorar todas as máquinas da sua rede a partir de http://192.168.0.9:3000!
