# Índice de Documentação - 20/02/2026

## 📚 Documentação Criada Hoje

### 🚀 Guias de Instalação

1. **GUIA_RAPIDO_INSTALACAO.md** ⭐ PRINCIPAL
   - Guia rápido com IPs corretos (192.168.0.9)
   - Passo a passo para instalar em outras máquinas
   - Checklist completo

2. **GUIA_MONITORAMENTO_SEM_DOMINIO.md**
   - Como funciona sem Active Directory
   - Arquitetura de rede
   - Autenticação local (workgroup)
   - Cenários de uso

3. **GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md**
   - Conceito agentless (PRTG/CheckMK style)
   - Configuração WMI
   - Configuração SNMP
   - Arquitetura completa

4. **GUIA_REINSTALACAO_LIMPA.md**
   - Como limpar e reinstalar servidor
   - Passo a passo detalhado
   - Troubleshooting

---

### 🔧 Scripts de Instalação

1. **probe/install_workgroup.bat** ⭐ NOVO
   - Instalador para máquinas SEM domínio
   - Cria usuário local MonitorUser
   - Configura WMI, DCOM, Firewall
   - Gera credenciais automaticamente

2. **probe/install_automated.bat**
   - Instalador para máquinas COM domínio
   - Usa usuário de domínio
   - Requer Active Directory

3. **reinstalar_servidor_completo.bat**
   - Limpa servidor atual
   - Remove sensores antigos
   - Recria com configuração limpa

4. **iniciar_probe.bat**
   - Inicia probe local
   - Verifica configuração
   - Mostra logs em tempo real

5. **sincronizar_pastas.bat** ⭐ NOVO
   - Sincroniza entre as duas pastas
   - Copia documentação, scripts, código
   - Mantém tudo atualizado

---

### 🐛 Correções Aplicadas

1. **CORRECOES_DASHBOARD_NOC_TESTES_20FEV.md**
   - Dashboard mostrando 0 servidores (CORRIGIDO)
   - NOC mostrando empresa errada (CORRIGIDO)
   - Falhas simuladas não aparecendo (CORRIGIDO)
   - Auto-resolução não funcionando (CORRIGIDO)

2. **CORRECOES_FINAIS_SENSORES_PROBES_20FEV.md**
   - Sensores não aparecendo (CORRIGIDO)
   - Empresas mostrando 0 probes (CORRIGIDO)
   - Admin não vendo todos os recursos (CORRIGIDO)

3. **SOLUCAO_SENSORES_DESCONHECIDOS.md**
   - Sensores mostrando "Desconhecido"
   - Causa: Probe não está rodando
   - Solução: Iniciar probe

---

### 📊 Arquivos Modificados (Backend)

1. **api/routers/dashboard.py**
   - Admin vê TODOS os servidores/sensores
   - Filtro por tenant apenas para usuários normais

2. **api/routers/sensors.py**
   - Admin vê TODOS os sensores
   - Corrigido filtro de tenant

3. **api/routers/probes.py**
   - Admin vê TODAS as probes
   - Aceita parâmetro tenant_id
   - Usado pela página de Empresas

4. **api/routers/incidents.py**
   - Adicionado endpoint POST /{incident_id}/resolve
   - Admin pode resolver qualquer incidente

5. **api/routers/test_tools.py**
   - Ferramentas de teste para admin
   - Simular falhas
   - Listar falhas ativas
   - Limpar falhas

6. **api/routers/noc.py**
   - Admin vê todos os servidores no NOC
   - Filtro por tenant para usuários normais

---

### 🎨 Arquivos Modificados (Frontend)

1. **frontend/src/components/TestTools.js**
   - Adicionado botão "Resolver" para cada falha
   - Auto-refresh a cada 5 segundos
   - Melhor visualização de falhas ativas

---

### 📝 Documentação de Referência

1. **ARQUITETURA_PRTG_AGENTLESS.md**
   - Como funciona monitoramento agentless
   - Comparação com PRTG, Zabbix, CheckMK

2. **WMI_REMOTO_RESUMO.md**
   - Configuração WMI remoto
   - Credenciais e segurança

3. **docs/snmp-sensors-oids.md**
   - OIDs SNMP padrão
   - Configuração de dispositivos SNMP

---

## 🗂️ Estrutura de Pastas

```
C:\Users\user\Coruja Monitor\
├── api/
│   ├── routers/
│   │   ├── dashboard.py ✓ MODIFICADO
│   │   ├── sensors.py ✓ MODIFICADO
│   │   ├── probes.py ✓ MODIFICADO
│   │   ├── incidents.py ✓ MODIFICADO
│   │   ├── test_tools.py ✓ MODIFICADO
│   │   └── noc.py ✓ MODIFICADO
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── probe/
│   ├── install_workgroup.bat ⭐ NOVO
│   ├── install_automated.bat
│   ├── probe_core.py
│   ├── collectors/
│   │   ├── system_collector.py
│   │   ├── docker_collector.py
│   │   ├── generic_collector.py
│   │   └── snmp_collector.py
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       └── components/
│           ├── TestTools.js ✓ MODIFICADO
│           ├── Dashboard.js
│           ├── NOCMode.js
│           └── ...
│
├── GUIA_RAPIDO_INSTALACAO.md ⭐ PRINCIPAL
├── GUIA_MONITORAMENTO_SEM_DOMINIO.md ⭐ NOVO
├── GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md
├── GUIA_REINSTALACAO_LIMPA.md
├── CORRECOES_DASHBOARD_NOC_TESTES_20FEV.md
├── CORRECOES_FINAIS_SENSORES_PROBES_20FEV.md
├── SOLUCAO_SENSORES_DESCONHECIDOS.md
├── reinstalar_servidor_completo.bat
├── iniciar_probe.bat
├── sincronizar_pastas.bat ⭐ NOVO
└── INDICE_DOCUMENTACAO_20FEV.md (este arquivo)
```

---

## 🎯 Próximos Passos

### 1. Sincronizar Pastas
```bash
sincronizar_pastas.bat
```

### 2. Reinstalar Servidor Atual (Opcional)
```bash
reinstalar_servidor_completo.bat
iniciar_probe.bat
```

### 3. Instalar em Outras Máquinas
```bash
# Copiar pasta probe para outra máquina
# Executar como Admin:
cd C:\Coruja Monitor\probe
install_workgroup.bat
```

---

## 📞 Referência Rápida

### IPs da Sua Rede
- **Servidor Coruja**: 192.168.0.9
- **Frontend**: http://192.168.0.9:3000
- **API**: http://192.168.0.9:8000

### Login
- **Usuário**: admin@coruja.com
- **Senha**: admin123

### Token da Probe
- **Token**: W_YxHARNTlE3G8bxoXhWt0FknTPysGnKFX_visaP_G4

### Pastas
- **Pasta 1**: C:\Users\user\Coruja Monitor
- **Pasta 2**: C:\Users\user\OneDrive - EmpresaXPTO Ltda\Desktop\Coruja Monitor

---

## ✅ Status Atual

### Funcionando
- ✅ Dashboard mostra contadores corretos
- ✅ NOC mostra empresa TENSO
- ✅ Admin vê todos os recursos
- ✅ Sensores aparecem na lista
- ✅ Empresas mostram probes
- ✅ Falhas simuladas podem ser resolvidas

### Pendente
- ⚠️ Iniciar probe para coletar métricas
- ⚠️ Sincronizar pastas (execute sincronizar_pastas.bat)

---

## 📚 Documentos por Categoria

### Instalação
- GUIA_RAPIDO_INSTALACAO.md
- GUIA_MONITORAMENTO_SEM_DOMINIO.md
- GUIA_REINSTALACAO_LIMPA.md
- probe/install_workgroup.bat

### Correções
- CORRECOES_DASHBOARD_NOC_TESTES_20FEV.md
- CORRECOES_FINAIS_SENSORES_PROBES_20FEV.md
- SOLUCAO_SENSORES_DESCONHECIDOS.md

### Arquitetura
- GUIA_MONITORAMENTO_AGENTLESS_COMPLETO.md
- ARQUITETURA_PRTG_AGENTLESS.md
- ARQUITETURA_SENSORES_PROBE.md

### Scripts
- sincronizar_pastas.bat
- reinstalar_servidor_completo.bat
- iniciar_probe.bat
- probe/install_workgroup.bat

---

**Execute `sincronizar_pastas.bat` agora para copiar tudo para o OneDrive!** 🚀
