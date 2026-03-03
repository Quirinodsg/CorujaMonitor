# WMI Remoto - Resumo Executivo

## ❓ Sua Pergunta

> "Como está funcionando hoje, se eu adicionar um servidor WMI preciso colocar algum usuário com permissão para enviar os dados para sonda?"

## ✅ Resposta Direta

### Como Funciona HOJE (Modo Sonda Local)

**NÃO precisa de usuário/senha!**

A sonda é instalada **dentro do próprio servidor** que será monitorado. Ela coleta as métricas localmente usando a biblioteca Python `psutil`, que tem acesso direto ao sistema operacional.

```
┌─────────────────────────────────┐
│  Servidor Windows               │
│                                 │
│  ┌──────────────────────────┐  │
│  │  Sonda Instalada         │  │
│  │  - Roda como serviço     │  │
│  │  - Acesso local ao SO    │  │
│  │  - SEM credenciais       │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
         ↓ HTTPS
    ┌─────────────┐
    │ API Coruja  │
    └─────────────┘
```

**Vantagens:**
- ✅ Não precisa configurar usuário/senha
- ✅ Não precisa abrir portas no firewall
- ✅ Mais seguro
- ✅ Mais confiável

**Desvantagens:**
- ❌ Precisa instalar a sonda em cada servidor

---

## 🆕 Modo WMI Remoto (Agentless) - NOVO

Se você quiser monitorar servidores **SEM instalar a sonda** neles, aí sim precisa de credenciais!

### Configuração Necessária

#### 1. No Servidor Remoto (que será monitorado)

**Opção A: Usar Administrador Existente (Mais Simples)**
```
Usuário: Administrator
Senha: [senha do administrador]
```

**Opção B: Criar Usuário Dedicado (Mais Seguro)**
```powershell
# Criar usuário específico para monitoramento
$Password = ConvertTo-SecureString "SenhaForte123!" -AsPlainText -Force
New-LocalUser -Name "CorujaMonitor" -Password $Password
Add-LocalGroupMember -Group "Administrators" -Member "CorujaMonitor"
```

#### 2. Habilitar WMI e Firewall

```powershell
# Habilitar WMI
Set-Service -Name Winmgmt -StartupType Automatic
Start-Service -Name Winmgmt

# Liberar firewall (portas 135 e 445)
Enable-NetFirewallRule -DisplayGroup "Windows Management Instrumentation (WMI)"
```

#### 3. Configurar no Coruja Monitor

Na interface web, ao adicionar o servidor:
- **Protocolo**: WMI Remoto
- **Hostname**: 192.168.0.38
- **Usuário WMI**: Administrator (ou CorujaMonitor)
- **Senha WMI**: [senha do usuário]
- **Domínio**: [vazio para local, ou DOMAIN para domínio]

---

## 📊 Comparação Rápida

| Aspecto | Sonda Local (Atual) | WMI Remoto (Novo) |
|---------|---------------------|-------------------|
| **Precisa credenciais?** | ❌ NÃO | ✅ SIM (Administrador) |
| **Precisa instalar?** | ✅ Sim (em cada servidor) | ❌ Não |
| **Configuração firewall?** | ❌ Não | ✅ Sim (portas 135, 445) |
| **Segurança** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Facilidade** | ⭐⭐⭐⭐ | ⭐⭐ |
| **Recomendado para** | Produção | Testes/Lab |

---

## 🎯 Recomendação

### Para Produção: Use Sonda Local (Modo Atual)

**Por quê?**
- Não precisa expor credenciais de administrador
- Não precisa abrir portas no firewall
- Mais seguro e confiável
- Configuração mais simples

**Como instalar:**
```bash
# No servidor que será monitorado
cd probe
configurar_probe.bat
```

### Para Testes/Lab: Pode usar WMI Remoto

**Quando usar:**
- Monitoramento temporário
- Ambiente de testes
- Servidores que não podem ter software instalado
- Monitoramento de múltiplos servidores de uma vez

---

## 🔐 Segurança das Credenciais WMI

Se você optar por usar WMI remoto, as credenciais são:

1. **Criptografadas** antes de salvar no banco (usando Fernet)
2. **Descriptografadas** apenas no momento de usar
3. **Nunca expostas** na interface web
4. **Chave de criptografia** armazenada em variável de ambiente

```python
# Exemplo de como funciona
from cryptography.fernet import Fernet

# Ao salvar
senha_original = "SenhaForte123!"
senha_criptografada = cipher.encrypt(senha_original.encode())
# Salva no banco: gAAAAABh... (texto criptografado)

# Ao usar
senha_descriptografada = cipher.decrypt(senha_criptografada)
# Usa para conectar WMI
```

---

## 📝 Resumo Final

### Modo Atual (Sonda Local)
```
✅ Não precisa usuário/senha
✅ Instalar sonda em cada servidor
✅ Mais seguro
✅ Recomendado para produção
```

### Modo Novo (WMI Remoto)
```
⚠️ Precisa usuário Administrador
⚠️ Precisa configurar firewall (135, 445)
⚠️ Precisa habilitar WMI
✅ Não precisa instalar nada no servidor remoto
✅ Útil para testes e monitoramento temporário
```

---

## 🚀 Próximos Passos

Se você quiser implementar WMI remoto:

1. ✅ Arquivos criados:
   - `probe/collectors/wmi_remote_collector.py` - Coletor WMI
   - `api/migrate_wmi_credentials.py` - Migração do banco
   - `docs/wmi-remote-monitoring.md` - Documentação completa

2. ⏭️ Próximas etapas:
   - Executar migração do banco
   - Adicionar campos na interface web (formulário de servidor)
   - Implementar criptografia de senhas
   - Atualizar probe_core.py para suportar WMI remoto
   - Testar conexão WMI

**Quer que eu implemente a funcionalidade completa de WMI remoto?**

---

**Data**: 13/02/2026
**Status**: Documentação e código base criados
**Decisão**: Aguardando confirmação do usuário para implementação completa
