# 🚀 Instalar Biblioteca de Sensores - AGORA

## ⚡ Instalação Rápida (1 comando)

Abra o PowerShell na pasta do projeto e execute:

```powershell
.\instalar_biblioteca_sensores.ps1
```

**Pronto!** O script vai:
1. ✅ Instalar todas as dependências Python
2. ✅ Executar a migração do banco de dados
3. ✅ Mostrar próximos passos

---

## 📋 O Que Será Instalado

### Dependências Python
- `sqlalchemy` - ORM para banco de dados
- `psycopg2-binary` - Driver PostgreSQL
- `azure-identity` - Autenticação Azure
- `azure-mgmt-resource` - Gerenciamento Azure
- `azure-mgmt-compute` - Azure VMs
- `azure-mgmt-monitor` - Azure Monitor
- `pysnmp` - Protocolo SNMP
- `requests` - Requisições HTTP

### Alterações no Banco de Dados
- `server_id` agora é opcional (nullable)
- Nova coluna `probe_id` para sensores independentes
- Índice para melhor performance

---

## 🔧 Após a Instalação

### 1. Reiniciar API
```powershell
# Pare o processo atual (Ctrl+C)
cd api
uvicorn main:app --reload
```

### 2. Reiniciar Frontend
```powershell
# Pare o processo atual (Ctrl+C)
cd frontend
npm start
```

### 3. Acessar o Sistema
1. Faça login: `admin@coruja.com` / `admin123`
2. Clique em **📚 Biblioteca de Sensores** no menu lateral
3. Clique em **+ Adicionar Sensor**
4. Escolha uma categoria e adicione seu primeiro sensor!

---

## 🎯 Exemplos de Uso

### Adicionar Access Point WiFi
1. Categoria: **SNMP**
2. Template: **Access Point**
3. Preencha:
   - Nome: `AP-Sala-01`
   - IP: `192.168.1.100`
   - Community: `public`
4. Clique em **🔌 Testar Conexão**
5. Se sucesso, clique em **Adicionar Sensor**

### Adicionar Serviço Azure
1. Categoria: **Microsoft Azure**
2. Template: **Azure Web App**
3. Preencha as credenciais Azure
4. Clique em **🔌 Testar Conexão**
5. Se sucesso, clique em **Adicionar Sensor**

### Adicionar Ar-Condicionado
1. Categoria: **SNMP**
2. Template: **Ar-Condicionado**
3. Preencha:
   - Nome: `AC-Datacenter`
   - IP: `192.168.1.50`
   - Community: `public`
   - Threshold Warning: `28°C`
   - Threshold Critical: `32°C`
4. Clique em **🔌 Testar Conexão**
5. Se sucesso, clique em **Adicionar Sensor**

---

## ❌ Problemas Comuns

### Erro: "python não é reconhecido"
**Solução**: Instale Python 3.8+ e adicione ao PATH

### Erro: "Falha na migração"
**Causa**: Banco de dados não está rodando
**Solução**: 
```powershell
# Verifique se PostgreSQL está rodando
docker ps
# Ou inicie o banco
docker-compose up -d db
```

### Erro: "Module not found"
**Causa**: Dependências não instaladas
**Solução**:
```powershell
cd api
python -m pip install -r requirements.txt
```

### Erro: "Teste de conexão falhou"
**Azure**: Verifique credenciais no Azure Portal
**SNMP**: Verifique IP, community string e firewall
**HTTP**: Verifique URL e porta

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- `BIBLIOTECA_SENSORES_IMPLEMENTADA.md` - Documentação completa
- `TESTE_CONEXAO_IMPLEMENTADO.md` - Detalhes do teste de conexão
- `aplicar_biblioteca_sensores_manual.md` - Instalação manual passo a passo

---

## ✅ Checklist

- [ ] Executar `.\instalar_biblioteca_sensores.ps1`
- [ ] Reiniciar API
- [ ] Reiniciar Frontend
- [ ] Acessar "📚 Biblioteca de Sensores"
- [ ] Adicionar primeiro sensor
- [ ] Testar conexão
- [ ] Verificar coleta de dados

---

## 🎉 Pronto!

Após seguir estes passos, você terá a Biblioteca de Sensores funcionando e poderá monitorar:
- 📡 Access Points
- ❄️ Ar-Condicionado
- 🔋 Nobreaks
- 🖨️ Impressoras
- ☁️ Serviços Azure
- 🌐 URLs HTTP/HTTPS
- 💾 Storage (SAN/NAS)
- E muito mais!

**Dúvidas?** Consulte a documentação ou execute o script novamente.
