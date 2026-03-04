# ⚡ Executar Migração AGORA

## ✅ Docker Compose Reiniciado

Os containers estão reiniciando:
- coruja-postgres ✓
- coruja-api ✓
- coruja-frontend ✓
- coruja-redis ✓
- coruja-worker ✓
- coruja-ollama ✓
- coruja-ai-agent ✓

## 🔄 Aguarde 10 Segundos

Aguarde os containers subirem completamente (cerca de 10 segundos).

## ✅ Execute a Migração

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

## 🎯 Depois

Acesse: http://localhost:3000

Login: `admin@coruja.com` / `admin123`

Clique em **📚 Biblioteca de Sensores**

## 🚀 Pronto!

A Biblioteca de Sensores estará funcionando!

Você poderá adicionar:
- 📡 Access Points WiFi
- ❄️ Ar-Condicionado
- 🔋 Nobreaks
- 🖨️ Impressoras
- ☁️ Serviços Azure
- 🌐 URLs HTTP/HTTPS
- 💾 Storage (SAN/NAS)

**Aguarde 10 segundos e execute a migração!** ⏳
