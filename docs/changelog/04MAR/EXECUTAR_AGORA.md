# ⚡ EXECUTAR AGORA - 3 Passos Simples

## 🎯 Passo 1: Instalar

Abra o PowerShell na pasta do projeto e execute:

```powershell
.\instalar_biblioteca_sensores.ps1
```

**Aguarde** até ver a mensagem:
```
========================================
  INSTALACAO CONCLUIDA COM SUCESSO!
========================================
```

---

## 🔄 Passo 2: Reiniciar Serviços

### Reiniciar API
```powershell
# Em um terminal, pare a API (Ctrl+C) e execute:
cd api
uvicorn main:app --reload
```

### Reiniciar Frontend
```powershell
# Em outro terminal, pare o frontend (Ctrl+C) e execute:
cd frontend
npm start
```

---

## ✅ Passo 3: Testar

1. Acesse: http://localhost:3000
2. Login: `admin@coruja.com` / `admin123`
3. Clique em **📚 Biblioteca de Sensores**
4. Clique em **+ Adicionar Sensor**
5. Escolha uma categoria
6. Preencha os dados
7. Clique em **🔌 Testar Conexão**
8. Se sucesso, clique em **Adicionar Sensor**

---

## 🎉 Pronto!

Agora você pode adicionar:
- 📡 Access Points WiFi
- ❄️ Ar-Condicionado do Datacenter
- 🔋 Nobreaks e UPS
- 🖨️ Impressoras de Rede
- ☁️ Serviços Azure (VMs, Web Apps, SQL, etc.)
- 🌐 Monitoramento HTTP/HTTPS
- 💾 Storage (SAN/NAS)
- E muito mais!

---

## ❌ Se Der Erro

### Erro ao instalar dependências
```powershell
cd api
python -m pip install sqlalchemy psycopg2-binary
python -m pip install azure-identity azure-mgmt-resource pysnmp requests
```

### Erro na migração
```powershell
# Verifique se o banco está rodando
docker ps

# Se não estiver, inicie
docker-compose up -d db
```

### Erro ao testar conexão
- **Azure**: Verifique credenciais no Azure Portal
- **SNMP**: Verifique IP, community string e firewall
- **HTTP**: Verifique URL e porta

---

## 📚 Mais Informações

- `INSTALAR_BIBLIOTECA_AGORA.md` - Guia detalhado
- `BIBLIOTECA_SENSORES_IMPLEMENTADA.md` - Documentação completa
- `TESTE_CONEXAO_IMPLEMENTADO.md` - Detalhes do teste
- `RESUMO_SITUACAO_ATUAL.md` - Status atual

---

**Dúvidas?** Consulte a documentação ou execute o script novamente.

**Tudo pronto!** 🚀
