# ✅ Correção da Biblioteca de Sensores

## 🔍 Problema Identificado

Após o rebuild dos containers, a biblioteca de sensores não estava aparecendo porque:
- O diretório `/app/src/data/` não existia no container do frontend
- O arquivo `sensorTemplates.js` não foi copiado durante o build

## 🛠️ Solução Aplicada

### 1. Criação do Diretório
```bash
docker exec coruja-frontend mkdir -p /app/src/data
```

### 2. Cópia do Arquivo de Templates
```bash
docker cp frontend/src/data/sensorTemplates.js coruja-frontend:/app/src/data/
```

### 3. Reinício do Container
```bash
docker restart coruja-frontend
```

## ✅ Resultado

A biblioteca de sensores agora está funcionando com:

### 📚 Categorias Disponíveis
- ⭐ **Sensores Padrão** - Ping, CPU, Memória, Disco, Uptime, Network IN/OUT
- 🪟 **Windows** - 14 sensores (Serviços, IIS, AD, DNS, DHCP, etc.)
- 🐧 **Linux** - 9 sensores (Apache, Nginx, SSH, Docker, etc.)
- 🌐 **Rede** - 11 sensores (HTTP, SSL, DNS, SMTP, FTP, RDP, etc.)
- 🗄️ **Banco de Dados** - 8 sensores (SQL Server, MySQL, PostgreSQL, MongoDB, etc.)
- 📦 **Aplicações** - 10 sensores (Docker, Redis, Kafka, Kubernetes, etc.)
- ⚙️ **Personalizado** - Scripts customizados

### 🎯 Total: 60+ Templates de Sensores

## 🔄 Como Usar

1. Acesse **http://localhost:3000**
2. Vá em **Servidores** → Selecione um servidor
3. Clique em **Adicionar Sensor**
4. Navegue pela biblioteca de sensores organizada por categorias
5. Selecione o template desejado
6. Configure e adicione

## 📝 Observações

- Os sensores padrão (Ping, CPU, Memória, Disco, Uptime, Network IN/OUT) são criados automaticamente
- Sensores que requerem descoberta (Serviços, Discos) mostram opções em tempo real
- Cada template vem com thresholds pré-configurados baseados em melhores práticas

## 🎉 Status

✅ **Biblioteca de Sensores Totalmente Funcional**

Data: 19/02/2026
