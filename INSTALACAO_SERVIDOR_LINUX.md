# 🐧 INSTALAÇÃO - Servidor Linux (Ubuntu Server)

## 🎯 Arquitetura Recomendada

```
Servidor Central: Ubuntu Server 22.04 LTS
Probes: Windows 10/11 ou Windows Server
```

---

## 📋 Pré-requisitos

### Hardware Mínimo

```
CPU: 4 cores
RAM: 8 GB
Disco: 100 GB SSD
Rede: 1 Gbps
```

### Software

```
Ubuntu Server 22.04 LTS (ou superior)
Acesso SSH
Usuário com sudo
```

---

## 🚀 INSTALAÇÃO RÁPIDA (10 minutos)

### PASSO 1: Conectar ao Servidor

```bash
# De uma máquina Windows, use PuTTY ou PowerShell
ssh usuario@IP_DO_SERVIDOR

# Exemplo:
ssh admin@192.168.1.100
```

---

### PASSO 2: Atualizar Sistema

```bash
# Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# Instalar utilitários básicos
sudo apt install -y curl git nano htop net-tools
```

---

### PASSO 3: Instalar Docker

```bash
# Baixar script de instalação
curl -fsSL https://get.docker.com -o get-docker.sh

# Executar instalação
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Aplicar mudanças (ou fazer logout/login)
newgrp docker

# Verificar instalação
docker --version
```

**Saída esperada:**
```
Docker version 24.0.7, build afdd53b
```

---

### PASSO 4: Instalar Docker Compose

```bash
# Instalar plugin do Docker Compose
sudo apt install -y docker-compose-plugin

# Verificar instalação
docker compose version
```

**Saída esperada:**
```
Docker Compose version v2.23.0
```

---

### PASSO 5: Clonar Repositório

```bash
# Ir para diretório home
cd ~

# Clonar repositório
git clone https://github.com/seu-usuario/coruja-monitor.git

# Entrar no diretório
cd coruja-monitor

# Verificar arquivos
ls -la
```

**Arquivos esperados:**
```
docker-compose.yml
.env.example
api/
frontend/
probe/
...
```

---

### PASSO 6: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

**Configurações importantes:**

```bash
# Banco de Dados
POSTGRES_USER=coruja
POSTGRES_PASSWORD=SuaSenhaSegura123!  # MUDE ISSO!
POSTGRES_DB=coruja_monitor

# API
API_SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria  # MUDE ISSO!
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=http://IP_DO_SERVIDOR:8000  # MUDE PARA SEU IP!

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Ollama (IA)
OLLAMA_HOST=http://ollama:11434
```

**Gerar chave secreta:**
```bash
# Gerar chave aleatória
openssl rand -hex 32
```

**Salvar e sair:**
- Pressione `Ctrl + X`
- Pressione `Y`
- Pressione `Enter`

---

### PASSO 7: Configurar Firewall

```bash
# Instalar UFW (se não estiver instalado)
sudo apt install -y ufw

# Permitir SSH (IMPORTANTE!)
sudo ufw allow 22/tcp

# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir HTTPS
sudo ufw allow 443/tcp

# Permitir API
sudo ufw allow 8000/tcp

# Permitir Frontend
sudo ufw allow 3000/tcp

# Habilitar firewall
sudo ufw enable

# Verificar status
sudo ufw status
```

**Saída esperada:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
8000/tcp                   ALLOW       Anywhere
3000/tcp                   ALLOW       Anywhere
```

---

### PASSO 8: Iniciar Sistema

```bash
# Iniciar containers
docker compose up -d

# Aguardar inicialização (30-60 segundos)
sleep 60

# Verificar containers
docker ps
```

**Saída esperada:**
```
CONTAINER ID   IMAGE                    STATUS         PORTS
abc123def456   coruja-frontend          Up 1 minute    0.0.0.0:3000->3000/tcp
def456ghi789   coruja-api               Up 1 minute    0.0.0.0:8000->8000/tcp
ghi789jkl012   postgres:15              Up 1 minute    5432/tcp
jkl012mno345   redis:7-alpine           Up 1 minute    6379/tcp
mno345pqr678   coruja-worker            Up 1 minute
pqr678stu901   coruja-ai-agent          Up 1 minute    5000/tcp
stu901vwx234   ollama/ollama:latest     Up 1 minute    11434/tcp
```

**Todos os 7 containers devem estar "Up"!**

---

### PASSO 9: Verificar Logs

```bash
# Ver logs da API
docker logs coruja-api --tail 50

# Ver logs do Frontend
docker logs coruja-frontend --tail 50

# Ver logs de todos os containers
docker compose logs --tail 20
```

**Procure por erros!**

---

### PASSO 10: Testar Acesso

```bash
# Testar API
curl http://localhost:8000/health

# Testar Frontend
curl http://localhost:3000
```

**API deve retornar:**
```json
{"status":"healthy"}
```

---

### PASSO 11: Criar Usuário Admin

```bash
# Executar script de inicialização
docker compose exec api python init_admin.py
```

**Credenciais padrão:**
```
Email: admin@coruja.com
Senha: admin123
```

**⚠️ MUDE A SENHA APÓS PRIMEIRO LOGIN!**

---

### PASSO 12: Acessar Sistema

**De uma máquina Windows na mesma rede:**

1. Abra o navegador
2. Acesse: `http://IP_DO_SERVIDOR:3000`
3. Login:
   - Email: `admin@coruja.com`
   - Senha: `admin123`
4. ✅ Sistema funcionando!

---

## 🔧 Configurações Adicionais

### Configurar IP Estático

```bash
# Editar configuração de rede
sudo nano /etc/netplan/00-installer-config.yaml
```

**Exemplo:**
```yaml
network:
  version: 2
  ethernets:
    ens33:  # Nome da interface (use: ip a)
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

**Aplicar:**
```bash
sudo netplan apply
```

---

### Configurar Auto-Start

```bash
# Docker já inicia automaticamente no boot

# Verificar
sudo systemctl status docker

# Habilitar (se não estiver)
sudo systemctl enable docker
```

---

### Configurar Backup Automático

```bash
# Criar script de backup
nano ~/backup-coruja.sh
```

**Conteúdo:**
```bash
#!/bin/bash

# Diretório de backup
BACKUP_DIR="/home/$USER/backups"
mkdir -p $BACKUP_DIR

# Data atual
DATE=$(date +%Y%m%d_%H%M%S)

# Backup do banco de dados
docker compose exec -T postgres pg_dump -U coruja coruja_monitor > "$BACKUP_DIR/coruja_backup_$DATE.sql"

# Manter apenas últimos 7 backups
cd $BACKUP_DIR
ls -t coruja_backup_*.sql | tail -n +8 | xargs -r rm

echo "Backup concluído: coruja_backup_$DATE.sql"
```

**Tornar executável:**
```bash
chmod +x ~/backup-coruja.sh
```

**Agendar backup diário (2h da manhã):**
```bash
# Editar crontab
crontab -e

# Adicionar linha:
0 2 * * * /home/$USER/backup-coruja.sh >> /home/$USER/backup.log 2>&1
```

---

## 📊 Monitoramento do Servidor

### Ver Uso de Recursos

```bash
# CPU e RAM
htop

# Disco
df -h

# Rede
ifconfig

# Containers
docker stats
```

---

### Ver Logs em Tempo Real

```bash
# Todos os containers
docker compose logs -f

# Apenas API
docker logs -f coruja-api

# Apenas Frontend
docker logs -f coruja-frontend
```

---

## 🔄 Comandos Úteis

### Gerenciar Sistema

```bash
# Parar sistema
docker compose down

# Iniciar sistema
docker compose up -d

# Reiniciar sistema
docker compose restart

# Reiniciar apenas API
docker compose restart api

# Ver status
docker compose ps
```

---

### Atualizar Sistema

```bash
# Ir para diretório
cd ~/coruja-monitor

# Baixar atualizações
git pull

# Atualizar containers
docker compose pull
docker compose up -d

# Verificar
docker ps
```

---

### Limpar Sistema

```bash
# Remover containers parados
docker container prune -f

# Remover imagens não usadas
docker image prune -a -f

# Remover volumes não usados
docker volume prune -f

# Limpar tudo
docker system prune -a -f
```

---

## 🚨 Troubleshooting

### Container não inicia

```bash
# Ver logs
docker logs coruja-api

# Ver eventos
docker events

# Reiniciar container
docker compose restart api
```

---

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Ver logs do PostgreSQL
docker logs coruja-postgres

# Reiniciar banco
docker compose restart postgres
```

---

### Porta já em uso

```bash
# Ver o que está usando a porta 8000
sudo lsof -i :8000

# Matar processo
sudo kill -9 PID
```

---

### Sem espaço em disco

```bash
# Ver uso de disco
df -h

# Limpar Docker
docker system prune -a -f

# Limpar logs antigos
sudo journalctl --vacuum-time=7d
```

---

## 🔒 Segurança

### Atualizar Sistema Regularmente

```bash
# Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# Atualizar Docker
sudo apt install docker-ce docker-ce-cli containerd.io
```

---

### Configurar Fail2Ban (Proteção SSH)

```bash
# Instalar
sudo apt install -y fail2ban

# Configurar
sudo nano /etc/fail2ban/jail.local
```

**Conteúdo:**
```ini
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
```

**Iniciar:**
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

### Mudar Porta SSH (Opcional)

```bash
# Editar configuração
sudo nano /etc/ssh/sshd_config

# Mudar linha:
Port 2222  # Ao invés de 22

# Reiniciar SSH
sudo systemctl restart sshd

# Atualizar firewall
sudo ufw allow 2222/tcp
sudo ufw delete allow 22/tcp
```

---

## 📞 Próximos Passos

1. ✅ Servidor Linux instalado e funcionando
2. ➡️ Instalar probes Windows nas máquinas remotas
3. ➡️ Configurar sensores e monitoramento
4. ➡️ Configurar alertas e notificações
5. ➡️ Configurar backup automático
6. ➡️ Configurar HTTPS (Let's Encrypt)

---

## 📚 Documentação Relacionada

- `RECOMENDACAO_ARQUITETURA_SERVIDOR.md` - Comparação de arquiteturas
- `probe/INSTALACAO.md` - Instalação de probes Windows
- `installer/README_INSTALADOR_MSI.md` - Instalador MSI
- `GUIA_HTTPS_LETSENCRYPT.md` - Configurar HTTPS

---

**Data**: 04/03/2026  
**Status**: ✅ GUIA COMPLETO  
**Plataforma**: Ubuntu Server 22.04 LTS  
**Autor**: Kiro AI Assistant
