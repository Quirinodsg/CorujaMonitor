# Comparação Visual: Sonda Local vs WMI Remoto

## 🏗️ Arquitetura Atual - SONDA LOCAL (Recomendado)

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR WINDOWS 1                       │
│                    (192.168.0.38)                           │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │         SONDA CORUJA (Instalada Localmente)        │    │
│  │                                                     │    │
│  │  • Roda como Serviço Windows                       │    │
│  │  • Coleta métricas localmente (psutil)             │    │
│  │  • CPU, Memória, Disco, Rede, Serviços             │    │
│  │  • NÃO precisa credenciais                         │    │
│  │  • NÃO precisa abrir firewall                      │    │
│  │                                                     │    │
│  │  Token: abc123xyz...                                │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│                    HTTPS (8000)                             │
└──────────────────────────┼──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR WINDOWS 2                       │
│                    (192.168.0.39)                           │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │         SONDA CORUJA (Instalada Localmente)        │    │
│  │                                                     │    │
│  │  Token: def456uvw...                                │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                  │
│                    HTTPS (8000)                             │
└──────────────────────────┼──────────────────────────────────┘
                           ↓
                           ↓
              ┌────────────────────────┐
              │   API CORUJA MONITOR   │
              │   (Docker Container)   │
              │                        │
              │  • Recebe métricas     │
              │  • Armazena no banco   │
              │  • Avalia thresholds   │
              │  • Cria incidentes     │
              └────────────────────────┘
```

### ✅ Vantagens
- **Segurança**: Não expõe credenciais
- **Simplicidade**: Não precisa configurar firewall
- **Confiabilidade**: Coleta local é mais estável
- **Performance**: Acesso direto ao SO

### ❌ Desvantagens
- Precisa instalar sonda em cada servidor
- Precisa manter sondas atualizadas

---

## 🆕 Arquitetura Nova - WMI REMOTO (Agentless)

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR WINDOWS 1                       │
│                    (192.168.0.38)                           │
│                                                             │
│  ⚙️ WMI Habilitado                                          │
│  🔓 Firewall: Portas 135, 445 abertas                      │
│  👤 Usuário: Administrator                                  │
│  🔑 Senha: ********                                         │
│                                                             │
│  ❌ SEM SONDA INSTALADA                                     │
└──────────────────────────┬──────────────────────────────────┘
                           ↑
                      WMI/DCOM
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                    SERVIDOR WINDOWS 2                       │
│                    (192.168.0.39)                           │
│                                                             │
│  ⚙️ WMI Habilitado                                          │
│  🔓 Firewall: Portas 135, 445 abertas                      │
│  👤 Usuário: Administrator                                  │
│  🔑 Senha: ********                                         │
│                                                             │
│  ❌ SEM SONDA INSTALADA                                     │
└──────────────────────────┬──────────────────────────────────┘
                           ↑
                      WMI/DCOM
                           │
              ┌────────────┴───────────┐
              │   SONDA CENTRAL        │
              │   (1 única instalação) │
              │                        │
              │  • Conecta via WMI     │
              │  • Usa credenciais     │
              │  • Coleta de múltiplos │
              │    servidores          │
              └────────────────────────┘
                           ↓
                      HTTPS (8000)
                           ↓
              ┌────────────────────────┐
              │   API CORUJA MONITOR   │
              │   (Docker Container)   │
              │                        │
              │  • Recebe métricas     │
              │  • Armazena credenciais│
              │    criptografadas      │
              └────────────────────────┘
```

### ✅ Vantagens
- Não precisa instalar nada nos servidores remotos
- 1 sonda monitora múltiplos servidores
- Útil para monitoramento temporário

### ❌ Desvantagens
- **Segurança**: Expõe credenciais de administrador
- **Complexidade**: Precisa configurar WMI, DCOM, firewall
- **Confiabilidade**: Dependente da rede
- **Performance**: Overhead de rede

---

## 🔐 Fluxo de Credenciais WMI

### Cadastro de Servidor com WMI

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE WEB                            │
│                                                             │
│  Adicionar Servidor:                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Hostname: 192.168.0.38                              │   │
│  │ Protocolo: [x] WMI Remoto                           │   │
│  │ Usuário WMI: Administrator                          │   │
│  │ Senha WMI: ********                                 │   │
│  │ Domínio: [vazio]                                    │   │
│  │                                                     │   │
│  │ [Testar Conexão] [Salvar]                          │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
              ┌────────────────────────┐
              │   API BACKEND          │
              │                        │
              │  1. Recebe senha       │
              │  2. Criptografa        │
              │     (Fernet)           │
              │  3. Salva no banco     │
              └────────────────────────┘
                           ↓
              ┌────────────────────────┐
              │   BANCO DE DADOS       │
              │                        │
              │  wmi_username:         │
              │    "Administrator"     │
              │                        │
              │  wmi_password_encrypted│
              │    "gAAAAABh..."       │
              │    (criptografado)     │
              └────────────────────────┘
```

### Coleta de Métricas via WMI

```
              ┌────────────────────────┐
              │   SONDA CENTRAL        │
              │                        │
              │  1. Busca servidores   │
              │     com wmi_enabled    │
              └────────────┬───────────┘
                           ↓
              ┌────────────────────────┐
              │   API BACKEND          │
              │                        │
              │  2. Retorna lista:     │
              │     - hostname         │
              │     - username         │
              │     - senha criptogr.  │
              └────────────┬───────────┘
                           ↓
              ┌────────────────────────┐
              │   SONDA CENTRAL        │
              │                        │
              │  3. Descriptografa     │
              │     senha              │
              │  4. Conecta WMI        │
              │  5. Coleta métricas    │
              └────────────┬───────────┘
                           ↓
                      WMI/DCOM
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR REMOTO                          │
│                    (192.168.0.38)                           │
│                                                             │
│  6. Autentica usuário                                       │
│  7. Retorna métricas via WMI                                │
│     - Win32_Processor (CPU)                                 │
│     - Win32_OperatingSystem (Memória)                       │
│     - Win32_LogicalDisk (Disco)                             │
│     - Win32_Service (Serviços)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Decisão: Qual Usar?

### Use SONDA LOCAL se:
- ✅ Ambiente de produção
- ✅ Segurança é prioridade
- ✅ Tem acesso para instalar software
- ✅ Quer monitoramento confiável 24/7

### Use WMI REMOTO se:
- ⚠️ Ambiente de testes/lab
- ⚠️ Monitoramento temporário
- ⚠️ Não pode instalar software no servidor
- ⚠️ Precisa monitorar rapidamente sem instalação

---

## 📊 Tabela de Requisitos

| Requisito | Sonda Local | WMI Remoto |
|-----------|-------------|------------|
| **Instalação no servidor** | ✅ Sim | ❌ Não |
| **Usuário administrador** | ❌ Não | ✅ Sim |
| **Senha administrador** | ❌ Não | ✅ Sim |
| **Abrir firewall** | ❌ Não | ✅ Sim (135, 445) |
| **Habilitar WMI** | ❌ Não | ✅ Sim |
| **Configurar DCOM** | ❌ Não | ✅ Sim |
| **Configurar permissões** | ❌ Não | ✅ Sim |
| **Manutenção** | Baixa | Média |
| **Segurança** | Alta | Média |
| **Confiabilidade** | Alta | Média |

---

## 💡 Exemplo Prático

### Cenário 1: Empresa com 10 servidores Windows

**Opção A: Sonda Local**
```
• Instalar sonda em 10 servidores
• Tempo: ~5 minutos por servidor = 50 minutos
• Configuração: Simples (apenas token)
• Segurança: Alta
• Manutenção: Baixa
```

**Opção B: WMI Remoto**
```
• Instalar 1 sonda central
• Configurar WMI em 10 servidores
• Tempo: ~15 minutos por servidor = 150 minutos
• Configuração: Complexa (WMI, firewall, DCOM, permissões)
• Segurança: Média (10 senhas de admin expostas)
• Manutenção: Média
```

**Recomendação**: Sonda Local (mais rápido e seguro)

### Cenário 2: Monitoramento temporário de 1 servidor

**Opção A: Sonda Local**
```
• Instalar sonda
• Tempo: 5 minutos
• Desinstalar depois
```

**Opção B: WMI Remoto**
```
• Configurar WMI
• Tempo: 15 minutos
• Não precisa desinstalar
```

**Recomendação**: WMI Remoto (se for temporário)

---

**Conclusão**: Para produção, use **Sonda Local**. É mais simples, seguro e confiável!
