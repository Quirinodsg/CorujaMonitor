# ✅ Biblioteca de Sensores - Solução Final

## 🎯 Status Atual

✅ Dependências instaladas com sucesso!
✅ Script de migração corrigido!
❌ Banco de dados PostgreSQL não está rodando

## 🔧 Problema Atual

```
could not translate host name "postgres" to address
```

**Causa**: O container Docker do PostgreSQL não está rodando.

## ✅ Solução

### 1. Iniciar o Banco de Dados

```powershell
# Volte ao diretório raiz
cd "C:\Users\andre.quirino\Coruja Monitor"

# Inicie o Docker Compose
docker-compose up -d db
```

### 2. Executar a Migração

```powershell
cd api
python migrate_standalone_sensors.py
```

Você deve ver:
```
🔧 Iniciando migração para sensores independentes...
1. Adicionando coluna probe_id...
   ✓ Coluna probe_id adicionada
2. Tornando server_id opcional...
   ✓ server_id agora é opcional
3. Criando índice para probe_id...
   ✓ Índice criado

✅ Migração concluída com sucesso!
```

### 3. Reiniciar Serviços

```powershell
# Volte ao diretório raiz
cd ..

# Reinicie TUDO
docker-compose restart
```

**OU** reinicie manualmente:

```powershell
# API (em um terminal)
cd api
python -m uvicorn main:app --reload

# Frontend (em outro terminal)
cd frontend
npm start
```

### 4. Testar

1. Acesse: http://localhost:3000
2. Login: `admin@coruja.com` / `admin123`
3. Clique em **📚 Biblioteca de Sensores**
4. Clique em **+ Adicionar Sensor**
5. Escolha uma categoria
6. Preencha os dados
7. Clique em **🔌 Testar Conexão**
8. Se sucesso, clique em **Adicionar Sensor**

## 📋 Comandos Resumidos

```powershell
# 1. Iniciar banco
docker-compose up -d db

# 2. Executar migração
cd api
python migrate_standalone_sensors.py
cd ..

# 3. Reiniciar tudo
docker-compose restart
```

## 🎯 O Que Você Poderá Fazer

Após concluir, você poderá adicionar sensores independentes:

- 📡 Access Points WiFi
- ❄️ Ar-Condicionado do Datacenter
- 🔋 Nobreaks e UPS
- 🖨️ Impressoras de Rede
- ☁️ Serviços Azure (VMs, Web Apps, SQL, Storage, etc.)
- 🌐 URLs HTTP/HTTPS
- 💾 Storage (SAN/NAS)

## ✅ Checklist Final

- [x] Python instalado
- [x] Dependências instaladas (`pydantic-settings`, Azure SDK, SNMP)
- [x] Script de migração corrigido
- [ ] Banco de dados rodando
- [ ] Migração executada
- [ ] Serviços reiniciados
- [ ] Biblioteca de Sensores testada

## 🚀 Próximo Passo

Execute AGORA:

```powershell
docker-compose up -d db
```

Depois:

```powershell
cd api
python migrate_standalone_sensors.py
```

**Quase lá!** 🎉
