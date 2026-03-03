# 👋 LEIA ISTO PRIMEIRO

## 🎯 O Que Você Precisa Fazer

Você tentou instalar a Biblioteca de Sensores mas deu erro porque:
- ❌ Não tem ambiente virtual Python (venv)
- ❌ Dependências não estão instaladas
- ❌ Migração do banco não foi executada

## ⚡ Solução em 1 Comando

Abra o PowerShell e execute:

```powershell
.\instalar_biblioteca_sensores.ps1
```

**Pronto!** Isso vai:
1. ✅ Instalar todas as dependências Python no sistema global
2. ✅ Executar a migração do banco de dados
3. ✅ Mostrar os próximos passos

## 🔄 Depois da Instalação

### 1. Reinicie a API
```powershell
# Pare com Ctrl+C e execute:
cd api
uvicorn main:app --reload
```

### 2. Reinicie o Frontend
```powershell
# Pare com Ctrl+C e execute:
cd frontend
npm start
```

### 3. Teste
1. Acesse: http://localhost:3000
2. Login: `admin@coruja.com` / `admin123`
3. Clique em **📚 Biblioteca de Sensores**
4. Adicione seu primeiro sensor!

## 📚 O Que É a Biblioteca de Sensores?

Uma nova funcionalidade que permite adicionar sensores **independentes de servidores**:

- 📡 **Access Points WiFi** - Monitore APs em toda empresa
- ❄️ **Ar-Condicionado** - Temperatura do datacenter
- 🔋 **Nobreaks** - Status de bateria e carga
- 🖨️ **Impressoras** - Níveis de toner
- ☁️ **Azure Services** - VMs, Web Apps, SQL, Storage, etc.
- 🌐 **URLs HTTP/HTTPS** - Monitoramento de sites
- 💾 **Storage** - SANs e NAS (Dell, NetApp, Synology, etc.)

## 🔌 Teste de Conexão

**NOVO!** Antes de adicionar um sensor, você pode testar a conexão:
- ✅ Valida credenciais Azure
- ✅ Testa SNMP (IP, community, OID)
- ✅ Testa HTTP/HTTPS
- ✅ Feedback visual imediato

## 📖 Mais Informações

- **Instalação rápida**: `EXECUTAR_AGORA.md`
- **Guia detalhado**: `INSTALAR_BIBLIOTECA_AGORA.md`
- **Documentação completa**: `BIBLIOTECA_SENSORES_IMPLEMENTADA.md`
- **Índice de arquivos**: `INDICE_BIBLIOTECA_SENSORES.md`

## ❌ Se Der Erro

### Python não encontrado
```powershell
# Instale Python 3.8+ e adicione ao PATH
```

### Banco de dados não está rodando
```powershell
docker ps
# Se não aparecer, inicie:
docker-compose up -d db
```

### Dependências não instalaram
```powershell
cd api
python -m pip install sqlalchemy psycopg2-binary
python -m pip install azure-identity azure-mgmt-resource pysnmp requests
```

## 🎉 Resultado Final

Após executar o script, você terá:
- ✅ Nova aba "📚 Biblioteca de Sensores" no menu
- ✅ Interface para adicionar sensores independentes
- ✅ Teste de conexão integrado
- ✅ Templates rápidos para configuração
- ✅ Suporte para Azure, SNMP, HTTP
- ✅ Filtros e busca de sensores

## 🚀 Comece Agora

```powershell
.\instalar_biblioteca_sensores.ps1
```

**É só isso!** O script faz todo o trabalho pesado. 😊

---

**Dúvidas?** Consulte `EXECUTAR_AGORA.md` ou `INSTALAR_BIBLIOTECA_AGORA.md`

**Tudo pronto!** 🎯
