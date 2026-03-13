# Topologia e Fluxo de Trabalho - Coruja Monitor

## Máquinas do Ambiente

### 1. Máquina de Desenvolvimento (Kiro)
- **Onde:** Máquina local onde você está desenvolvendo
- **Sistema:** Windows com Kiro IDE
- **Função:** Desenvolvimento e edição de código
- **Git:** Repositório local clonado

### 2. SRVSONDA001 (192.168.31.162)
- **Sistema:** Windows Server
- **Domínio:** ad.techbiz.com.br
- **Função:** Probe de monitoramento
- **Git:** Repositório clonado em `C:\Users\Steve.Jobs\Desktop\coruja-monitor`
- **Probe instalada:** `C:\Program Files\CorujaMonitor\Probe\`
- **Acesso:** RDP da máquina de desenvolvimento

### 3. Servidor Linux (192.168.31.161)
- **Sistema:** Linux
- **Função:** API, Frontend, Worker, Banco de Dados
- **Git:** Repositório em `/root/coruja-monitor`
- **Acesso:** SSH

## Fluxo de Trabalho Padrão

### Quando Modificar Código

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DESENVOLVIMENTO (Máquina Kiro)                          │
│    - Editar código no Kiro IDE                             │
│    - Testar localmente se possível                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. COPIAR PARA SRVSONDA001 (.162) via RDP                  │
│    - Abrir RDP para 192.168.31.162                         │
│    - Copiar arquivos modificados                           │
│    - Colar em C:\Users\Steve.Jobs\Desktop\coruja-monitor   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. COMMIT E PUSH (SRVSONDA001)                             │
│    PowerShell:                                              │
│    cd C:\Users\Steve.Jobs\Desktop\coruja-monitor           │
│    git add .                                                │
│    git commit -m "descrição"                                │
│    git push                                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. PULL NO LINUX (.161)                                    │
│    SSH:                                                     │
│    cd /root/coruja-monitor                                  │
│    git pull                                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. APLICAR MUDANÇAS                                         │
│    - Se mudou API: reiniciar containers Docker             │
│    - Se mudou Frontend: rebuild e reiniciar                │
│    - Se mudou Probe: copiar para SRVSONDA001               │
│    - Se mudou Worker: reiniciar worker                     │
└─────────────────────────────────────────────────────────────┘
```

## Comandos Rápidos por Tipo de Mudança

### Mudanças na Probe

**Na SRVSONDA001 (.162):**
```powershell
# 1. Commit e push
cd C:\Users\Steve.Jobs\Desktop\coruja-monitor
git add probe/
git commit -m "fix: descrição"
git push

# 2. Copiar para probe instalada
copy probe\probe_core.py "C:\Program Files\CorujaMonitor\Probe\"
copy probe\collectors\*.py "C:\Program Files\CorujaMonitor\Probe\collectors\"

# 3. Reiniciar probe
# Ctrl+C na janela do iniciar_probe.bat
cd C:\Users\Steve.Jobs\Desktop
.\iniciar_probe.bat
```

**No Linux (.161):**
```bash
# Pull (para manter sincronizado)
cd /root/coruja-monitor
git pull
```

### Mudanças na API

**Na SRVSONDA001 (.162):**
```powershell
# Commit e push
cd C:\Users\Steve.Jobs\Desktop\coruja-monitor
git add api/
git commit -m "feat: descrição"
git push
```

**No Linux (.161):**
```bash
# Pull e reiniciar
cd /root/coruja-monitor
git pull

# Reiniciar API
docker-compose restart api

# Ou rebuild se mudou dependências
docker-compose up -d --build api
```

### Mudanças no Frontend

**Na SRVSONDA001 (.162):**
```powershell
# Commit e push
cd C:\Users\Steve.Jobs\Desktop\coruja-monitor
git add frontend/
git commit -m "feat: descrição"
git push
```

**No Linux (.161):**
```bash
# Pull e rebuild
cd /root/coruja-monitor
git pull

# Rebuild frontend
docker-compose up -d --build frontend
```

### Mudanças no Worker

**Na SRVSONDA001 (.162):**
```powershell
# Commit e push
cd C:\Users\Steve.Jobs\Desktop\coruja-monitor
git add worker/
git commit -m "fix: descrição"
git push
```

**No Linux (.161):**
```bash
# Pull e reiniciar
cd /root/coruja-monitor
git pull

# Reiniciar worker
docker-compose restart worker
```

## Atalhos e Dicas

### Commit Rápido (SRVSONDA001)
```powershell
# Adicionar tudo, commit e push em um comando
cd C:\Users\Steve.Jobs\Desktop\coruja-monitor
git add . ; git commit -m "descrição" ; git push
```

### Pull e Restart Rápido (Linux)
```bash
# Pull e reiniciar tudo
cd /root/coruja-monitor && git pull && docker-compose restart
```

### Verificar Status Git
```powershell
# Windows
cd C:\Users\Steve.Jobs\Desktop\coruja-monitor
git status
git log -1

# Linux
cd /root/coruja-monitor
git status
git log -1
```

## Checklist de Deploy

- [ ] Código editado no Kiro
- [ ] Arquivos copiados para SRVSONDA001 via RDP
- [ ] Commit e push feito na SRVSONDA001
- [ ] Pull feito no Linux
- [ ] Serviços reiniciados conforme necessário
- [ ] Logs verificados para confirmar funcionamento

## Observações Importantes

1. **SEMPRE** fazer commit e push na SRVSONDA001 primeiro
2. **SEMPRE** fazer pull no Linux depois
3. **NUNCA** editar diretamente no Linux (usar apenas para pull)
4. **NUNCA** editar diretamente na SRVSONDA001 (copiar do Kiro)
5. Probe precisa ser copiada manualmente após pull
6. API/Frontend/Worker são atualizados via Docker

## Estrutura de Diretórios

### SRVSONDA001
```
C:\Users\Steve.Jobs\Desktop\
└── coruja-monitor\          (repositório Git)
    ├── probe\
    ├── api\
    ├── frontend\
    └── worker\

C:\Program Files\CorujaMonitor\
└── Probe\                   (probe instalada - copiar manualmente)
    ├── probe_core.py
    ├── config.yaml
    └── collectors\
```

### Linux
```
/root/
└── coruja-monitor\          (repositório Git)
    ├── api\                 (roda no Docker)
    ├── frontend\            (roda no Docker)
    ├── worker\              (roda no Docker)
    └── probe\               (não usado no Linux)
```

## Troubleshooting

### Git está desatualizado
```powershell
# SRVSONDA001
cd C:\Users\Steve.Jobs\Desktop\coruja-monitor
git pull
git status
```

```bash
# Linux
cd /root/coruja-monitor
git pull
git status
```

### Mudanças não aplicadas
1. Verificar se fez pull no Linux
2. Verificar se reiniciou o serviço correto
3. Verificar logs do Docker: `docker-compose logs -f [serviço]`

### Probe não atualizada
1. Verificar se copiou arquivos para `C:\Program Files\CorujaMonitor\Probe\`
2. Verificar se reiniciou a probe
3. Verificar logs da probe

## Contatos e Acessos

- **SRVSONDA001**: RDP via 192.168.31.162
- **Linux**: SSH via 192.168.31.161
- **Git**: GitHub (repositório remoto)
