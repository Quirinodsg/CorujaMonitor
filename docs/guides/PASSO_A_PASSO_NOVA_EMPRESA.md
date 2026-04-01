# Passo a Passo: Criar Empresa e Adicionar Máquina

## 🎯 Objetivo
Criar nova empresa no Coruja Monitor e adicionar uma máquina para monitoramento.

---

## 📋 Pré-requisitos

- ✅ Servidor Coruja rodando em 192.168.0.9
- ✅ Acesso: http://192.168.0.9:3000
- ✅ Login: admin@coruja.com / admin123
- ✅ Máquina cliente na mesma rede (192.168.0.X)

---

## 🚀 PARTE 1: Criar Empresa e Probe (Interface Web)

### Passo 1: Acessar Interface Web

1. Abra navegador
2. Acesse: http://192.168.0.9:3000
3. Login: admin@coruja.com
4. Senha: admin123

---

### Passo 2: Criar Nova Empresa

1. No menu lateral, clique em **"Empresas"**
2. Clique no botão **"+ Nova Empresa"**
3. Preencha:
   - **Nome da Empresa**: Ex: "Empresa ABC"
   - **Slug**: Ex: "empresa-abc" (automático)
4. Clique em **"Criar Empresa"**

✅ Empresa criada!

---

### Passo 3: Criar Probe para a Empresa

1. Na lista de empresas, encontre a empresa que você criou
2. Clique na empresa para expandir
3. Clique no botão **"+ Nova Probe"**
4. Preencha:
   - **Nome da Probe**: Ex: "Probe Filial SP"
5. Clique em **"Criar Probe"**

✅ Probe criada!

---

### Passo 4: Copiar Token da Probe

1. A probe aparecerá na lista com um token
2. Clique no botão **📋** (copiar) ao lado do token
3. **GUARDE ESTE TOKEN!** Você vai precisar dele

Exemplo de token:
```
abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

---

## 💻 PARTE 2: Instalar Probe na Máquina Cliente

### Passo 5: Copiar Pasta Probe

**Na sua máquina (192.168.0.9)**:

1. Abra o Windows Explorer
2. Vá para: `C:\Users\user\Coruja Monitor\probe\`
3. Copie a pasta inteira `probe`

**Opções para copiar:**

**Opção A - Compartilhamento de Rede**:
```
1. Compartilhe a pasta probe
2. Na máquina cliente, acesse: \\192.168.0.9\probe
3. Copie para: C:\Coruja Monitor\probe\
```

**Opção B - Pendrive**:
```
1. Copie pasta probe para pendrive
2. Leve até máquina cliente
3. Copie para: C:\Coruja Monitor\probe\
```

**Opção C - OneDrive/Rede**:
```
1. Use OneDrive ou pasta compartilhada
2. Copie para: C:\Coruja Monitor\probe\
```

---

### Passo 6: Executar Instalador (NA MÁQUINA CLIENTE)

**⚠️ IMPORTANTE: Execute como Administrador!**

1. Na máquina cliente, abra **CMD como Administrador**:
   - Pressione `Win + X`
   - Escolha "Prompt de Comando (Admin)" ou "Windows PowerShell (Admin)"

2. Execute:
```bash
cd C:\Coruja Monitor\probe
install_workgroup.bat
```

---

### Passo 7: Configurar Instalador

O instalador vai perguntar:

```
Digite o IP do servidor Coruja Monitor:
IP (ex: 192.168.0.100): 
```
**Digite**: `192.168.0.9` ← SEU IP!

```
Digite o token da probe (copie da interface web):
Token: 
```
**Cole o token** que você copiou no Passo 4

---

### Passo 8: Aguardar Instalação

O instalador vai:
1. ✓ Criar usuário local `MonitorUser`
2. ✓ Configurar grupos e permissões
3. ✓ Configurar Firewall para WMI
4. ✓ Configurar DCOM
5. ✓ Criar arquivo `probe_config.json`
6. ✓ Criar arquivo `wmi_credentials.json`
7. ✓ Testar WMI local

**Aguarde até aparecer "INSTALAÇÃO CONCLUÍDA!"**

---

### Passo 9: Instalar Python (se necessário)

Se a máquina não tiver Python:

1. Baixe: https://www.python.org/downloads/
2. Execute o instalador
3. **IMPORTANTE**: Marque "Add Python to PATH"
4. Clique em "Install Now"
5. Aguarde instalação
6. Teste no CMD: `python --version`

---

### Passo 10: Instalar Dependências

No CMD (ainda como Admin):

```bash
cd C:\Coruja Monitor\probe
pip install -r requirements.txt
```

Aguarde instalação de todas as bibliotecas.

---

### Passo 11: Iniciar Probe

```bash
python probe_core.py
```

**Você deve ver**:
```
✓ Conectado à API: http://192.168.0.9:8000
✓ Probe autenticada: Probe Filial SP
✓ Coletando métricas a cada 60 segundos...

[2026-02-20 14:30:00] Coletando métricas...
  ✓ CPU: 15.2%
  ✓ Memória: 45.8%
  ✓ Disco C: 67.3%
  ...
```

**⚠️ DEIXE A JANELA ABERTA!** A probe precisa rodar continuamente.

---

## 🎉 PARTE 3: Verificar no Dashboard

### Passo 12: Verificar Máquina no Dashboard

1. Volte para http://192.168.0.9:3000
2. Vá em **"Servidores"**
3. Aguarde 2-3 minutos
4. A nova máquina deve aparecer automaticamente!

**Você verá**:
- Nome da máquina
- IP da máquina
- Sensores padrão (CPU, Memória, Disco, etc)
- Status em tempo real

---

## 📊 Estrutura Final

```
┌─────────────────────────────────────────────────────┐
│         Coruja Monitor - 192.168.0.9                 │
├─────────────────────────────────────────────────────┤
│                                                       │
│  📁 Empresa ABC                                      │
│    └─ 🔌 Probe Filial SP                            │
│         └─ 🖥️ MAQUINA-CLIENTE (192.168.0.X)        │
│              ├─ CPU: 15%                             │
│              ├─ Memória: 45%                         │
│              ├─ Disco C: 67%                         │
│              └─ ...                                  │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Probe não conecta?

**Teste conectividade**:
```bash
ping 192.168.0.9
curl http://192.168.0.9:8000/health
```

**Verifique configuração**:
```bash
type C:\Coruja Monitor\probe\probe_config.json
```

Deve mostrar:
```json
{
  "api_url": "http://192.168.0.9:8000",
  "probe_token": "seu_token_aqui",
  "collection_interval": 60,
  "log_level": "INFO"
}
```

---

### Máquina não aparece no dashboard?

1. Aguarde 2-3 minutos
2. Verifique se probe está rodando (janela CMD aberta)
3. Faça Ctrl+Shift+R no navegador
4. Verifique logs da probe na janela CMD

---

### Erro de permissão?

Execute o instalador **como Administrador**:
1. Clique com botão direito em `install_workgroup.bat`
2. Escolha "Executar como administrador"

---

### Python não encontrado?

Instale Python e marque "Add Python to PATH":
1. https://www.python.org/downloads/
2. Execute instalador
3. Marque checkbox "Add Python to PATH"
4. Instale
5. Reinicie CMD

---

## 📝 Checklist Completo

### Interface Web (192.168.0.9:3000)
- [ ] Criar nova empresa
- [ ] Criar probe para empresa
- [ ] Copiar token da probe

### Máquina Cliente
- [ ] Copiar pasta probe
- [ ] Executar install_workgroup.bat (como Admin)
- [ ] Configurar IP: 192.168.0.9
- [ ] Configurar token da probe
- [ ] Instalar Python (se necessário)
- [ ] Instalar dependências: pip install -r requirements.txt
- [ ] Iniciar probe: python probe_core.py
- [ ] Deixar janela aberta

### Verificação
- [ ] Aguardar 2-3 minutos
- [ ] Verificar máquina no dashboard
- [ ] Verificar sensores coletando
- [ ] Verificar métricas em tempo real

---

## 🎯 Resumo Rápido

```bash
# 1. Interface Web (192.168.0.9:3000)
Empresas → + Nova Empresa → Criar
Expandir empresa → + Nova Probe → Copiar token

# 2. Máquina Cliente (como Admin)
cd C:\Coruja Monitor\probe
install_workgroup.bat
# Digite IP: 192.168.0.9
# Cole token da probe

pip install -r requirements.txt
python probe_core.py
# Deixar rodando!

# 3. Verificar
http://192.168.0.9:3000 → Servidores
```

---

## 📞 Arquivos Importantes

### Instalador
```
C:\Users\user\Coruja Monitor\probe\install_workgroup.bat
```

### Configuração (criada pelo instalador)
```
C:\Coruja Monitor\probe\probe_config.json
C:\Coruja Monitor\probe\wmi_credentials.json
```

### Logs
```
C:\Coruja Monitor\probe\logs\
```

---

**Pronto! Agora você pode criar quantas empresas e máquinas quiser!** 🚀
