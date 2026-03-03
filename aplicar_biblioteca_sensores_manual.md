# 📚 Aplicar Biblioteca de Sensores - Manual

## Passo a Passo

### 1. Ativar Ambiente Virtual

Primeiro, ative o ambiente virtual Python onde o projeto está instalado:

```powershell
# Se usar venv
.\venv\Scripts\Activate.ps1

# OU se usar .venv
.\.venv\Scripts\Activate.ps1

# OU se usar env
.\env\Scripts\Activate.ps1
```

**Importante:** Você deve ver `(venv)` ou `(.venv)` no início da linha do terminal.

### 2. Instalar Dependências

```powershell
cd api
pip install -r requirements.txt
```

Ou instale individualmente:

```powershell
pip install azure-identity==1.15.0
pip install azure-mgmt-resource==23.0.1
pip install azure-mgmt-compute==30.5.0
pip install azure-mgmt-monitor==6.0.2
pip install pysnmp==4.4.12
pip install requests==2.31.0
```

### 3. Executar Migração

```powershell
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

### 4. Voltar ao Diretório Raiz

```powershell
cd ..
```

### 5. Reiniciar Serviços

**API Backend:**
- Pare o processo atual (Ctrl+C)
- Reinicie: `uvicorn api.main:app --reload`

**Frontend:**
- Pare o processo atual (Ctrl+C)
- Reinicie: `npm start` (na pasta frontend)

### 6. Testar

1. Acesse o sistema
2. Faça login
3. Clique em **📚 Biblioteca de Sensores** no menu lateral
4. Clique em **+ Adicionar Sensor**
5. Teste a funcionalidade!

## Troubleshooting

### Erro: "No module named 'sqlalchemy'"

**Causa:** Ambiente virtual não está ativado ou dependências não instaladas.

**Solução:**
```powershell
# 1. Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# 2. Instalar dependências
cd api
pip install -r requirements.txt
cd ..
```

### Erro: "cannot import name 'Probe'"

**Causa:** Modelo Probe não existe ou não foi importado.

**Solução:** Verifique se o arquivo `api/models.py` tem a classe `Probe` definida.

### Erro: "relation 'probes' does not exist"

**Causa:** Tabela probes não existe no banco de dados.

**Solução:** Execute as migrações anteriores primeiro:
```powershell
cd api
python migrate_db.py
cd ..
```

### Erro: "column 'probe_id' already exists"

**Causa:** Migração já foi executada anteriormente.

**Solução:** Tudo certo! A migração já está aplicada. Pode prosseguir.

## Verificar se Funcionou

Execute este comando SQL no banco de dados:

```sql
-- Verificar se coluna probe_id existe
SELECT column_name, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'sensors' 
AND column_name IN ('server_id', 'probe_id');
```

Resultado esperado:
```
column_name | is_nullable
------------+-------------
server_id   | YES
probe_id    | YES
```

## Comandos Rápidos

```powershell
# Tudo em um comando (copie e cole)
.\venv\Scripts\Activate.ps1; cd api; pip install -r requirements.txt; python migrate_standalone_sensors.py; cd ..
```

## Próximos Passos

Após aplicar com sucesso:

1. ✅ Reinicie API e Frontend
2. ✅ Acesse **📚 Biblioteca de Sensores**
3. ✅ Adicione seu primeiro sensor
4. ✅ Teste a conexão antes de salvar
5. ✅ Monitore dispositivos independentes!

## Suporte

Se encontrar problemas:

1. Verifique se o ambiente virtual está ativado
2. Confirme que todas as dependências foram instaladas
3. Verifique os logs de erro
4. Consulte a documentação: `BIBLIOTECA_SENSORES_IMPLEMENTADA.md`
