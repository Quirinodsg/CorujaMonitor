# Guia Completo - Monitoramento Kubernetes
## Sistema Coruja Monitor - 27 FEV 2026

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Instalação](#instalação)
4. [Configuração](#configuração)
5. [Uso](#uso)
6. [Troubleshooting](#troubleshooting)
7. [Referências](#referências)

---

## 🎯 VISÃO GERAL

O Sistema Coruja Monitor agora suporta monitoramento completo de clusters Kubernetes, incluindo:

- ✅ Coleta automática de métricas
- ✅ Suporte para múltiplos clusters
- ✅ 3 métodos de autenticação
- ✅ 8 tipos de recursos monitorados
- ✅ Dashboards em tempo real (futuro)
- ✅ Alertas automáticos (futuro)
- ✅ Multi-tenant

### Recursos Monitorados

1. **Nodes** - Servidores do cluster
2. **Pods** - Containers agrupados
3. **Deployments** - Aplicações
4. **DaemonSets** - Pods por node
5. **StatefulSets** - Aplicações com estado
6. **Services** - Endpoints de rede
7. **Ingress** - Rotas HTTP/HTTPS (futuro)
8. **Persistent Volumes** - Armazenamento (futuro)

### Métricas Coletadas

- CPU usage (cores e %)
- Memory usage (bytes e %)
- Disk usage
- Network traffic
- Pod count
- Replica status
- Health status
- Restart count

---

## 🏗️ ARQUITETURA

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  - Wizard de configuração                                    │
│  - Dashboards (futuro)                                       │
│  - Alertas (futuro)                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      API (FastAPI)                           │
│  - Endpoints REST                                            │
│  - Autenticação JWT                                          │
│  - Validação de dados                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  BANCO DE DADOS (PostgreSQL)                 │
│  - kubernetes_clusters (configuração)                        │
│  - kubernetes_resources (recursos descobertos)               │
│  - kubernetes_metrics (histórico)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    PROBE (Python)                            │
│  - Scheduler (coleta a cada 60s)                             │
│  - Kubernetes Collector                                      │
│  - Buffer e envio em lote                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              KUBERNETES API SERVER                           │
│  - Core API (nodes, pods, services)                          │
│  - Apps API (deployments, daemonsets)                        │
│  - Metrics Server (CPU, memory)                              │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Dados

1. **Configuração** (Frontend → API → Banco)
   - Usuário configura cluster via wizard
   - API valida e salva no banco
   - Credenciais armazenadas

2. **Coleta** (Probe → Kubernetes → API → Banco)
   - Probe busca clusters ativos
   - Conecta ao Kubernetes API Server
   - Coleta métricas de recursos
   - Envia em lote para API
   - API armazena no banco

3. **Visualização** (Frontend → API → Banco)
   - Frontend busca métricas via API
   - Exibe dashboards e gráficos
   - Alertas em tempo real

---

## 🔧 INSTALAÇÃO

### Pré-requisitos

1. **Sistema Coruja Monitor instalado**
   - Docker e Docker Compose
   - API rodando em http://localhost:8000
   - Frontend rodando em http://localhost:3000

2. **Probe instalado e configurado**
   - Python 3.8+
   - Probe token configurado

3. **Biblioteca Kubernetes**
   ```bash
   cd probe
   pip install kubernetes pyyaml
   ```

### Verificar Instalação

```powershell
# Executar script de teste
.\testar_integracao_kubernetes.ps1
```

---

## ⚙️ CONFIGURAÇÃO

### Passo 1: Obter Credenciais do Cluster

#### Opção A: Kubeconfig (Recomendado)

```bash
# Exportar kubeconfig completo
kubectl config view --raw > kubeconfig.yaml

# Para clusters gerenciados:
# Azure AKS
az aks get-credentials --resource-group RG_NAME --name CLUSTER_NAME

# AWS EKS
aws eks update-kubeconfig --name CLUSTER_NAME --region REGION

# Google GKE
gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE
```

#### Opção B: Service Account Token

```bash
# 1. Criar Service Account
kubectl create serviceaccount coruja-monitor -n default

# 2. Criar ClusterRoleBinding
kubectl create clusterrolebinding coruja-monitor \
  --clusterrole=view \
  --serviceaccount=default:coruja-monitor

# 3. Gerar token (Kubernetes 1.24+)
kubectl create token coruja-monitor -n default --duration=8760h
```

#### Opção C: Bearer Token (Clusters Gerenciados)

```bash
# Azure AKS
az account get-access-token --resource https://management.azure.com

# AWS EKS
aws eks get-token --cluster-name CLUSTER_NAME

# Google GKE
gcloud auth print-access-token
```

### Passo 2: Configurar no Frontend

1. Acessar http://localhost:3000
2. Login: `admin@coruja.com` / `admin123`
3. Ir em **"Servidores"** → **"Monitorar Serviços"**
4. Clicar em **"☸️ Kubernetes"**
5. Seguir wizard:

#### Passo 1 do Wizard: Requisitos
- Ler requisitos e instruções
- Escolher método de autenticação
- Clicar em "Próximo"

#### Passo 2 do Wizard: Configuração
- **Nome do Cluster:** Nome descritivo (ex: "production-cluster")
- **Tipo de Cluster:** vanilla, aks, eks, gke, openshift
- **API Endpoint:** URL do API Server (ex: https://cluster.example.com:6443)
- **Método de Autenticação:** kubeconfig, service_account, token
- **Credenciais:** Colar kubeconfig ou token
- **Namespaces:** Selecionar "Todos" ou específicos
- Clicar em "Próximo"

#### Passo 3 do Wizard: Teste de Conexão
- Revisar configuração
- Clicar em "Testar Conexão"
- Aguardar resultado
- Se sucesso, clicar em "Próximo"

#### Passo 4 do Wizard: Seleção de Recursos
- Selecionar recursos a monitorar:
  - ☑️ Nodes (recomendado)
  - ☑️ Pods (recomendado)
  - ☑️ Deployments (recomendado)
  - ☑️ DaemonSets
  - ☑️ StatefulSets
  - ☑️ Services
  - ☐ Ingress (futuro)
  - ☐ Persistent Volumes (futuro)
- Clicar em "Finalizar"

### Passo 3: Reiniciar Probe

```powershell
cd probe
.\parar_todas_probes.bat
.\iniciar_probe_limpo.bat
```

### Passo 4: Verificar Coleta

```powershell
# Monitorar logs
Get-Content probe\probe.log -Tail 50 -Wait
```

**Logs esperados:**
```
INFO - Kubernetes collector initialized
INFO - 🔍 Starting Kubernetes collection...
INFO - 📊 Encontrados 1 cluster(s) Kubernetes
INFO - 🔍 Coletando métricas do cluster: production-cluster
INFO -   ✓ Coletados 5 node(s)
INFO -   ✓ Coletados 120 pod(s)
INFO -   ✓ Coletados 25 deployment(s)
INFO -   ✓ Enviados 150 recursos (5 novos, 145 atualizados)
INFO - ✅ Métricas coletadas com sucesso: production-cluster
```

---

## 🚀 USO

### Visualizar Clusters

```powershell
# Via API
curl http://localhost:8000/api/v1/kubernetes/clusters \
  -H "Authorization: Bearer TOKEN"
```

### Visualizar Recursos

```powershell
# Todos os recursos
curl http://localhost:8000/api/v1/kubernetes/clusters/1/resources \
  -H "Authorization: Bearer TOKEN"

# Filtrar por tipo
curl http://localhost:8000/api/v1/kubernetes/clusters/1/resources?resource_type=node \
  -H "Authorization: Bearer TOKEN"

# Filtrar por namespace
curl http://localhost:8000/api/v1/kubernetes/clusters/1/resources?namespace=production \
  -H "Authorization: Bearer TOKEN"
```

### Visualizar Métricas

```powershell
# Métricas agregadas
curl http://localhost:8000/api/v1/kubernetes/clusters/1/metrics \
  -H "Authorization: Bearer TOKEN"
```

### Testar Conexão

```powershell
# Testar conexão com cluster
curl -X POST http://localhost:8000/api/v1/kubernetes/clusters/1/test \
  -H "Authorization: Bearer TOKEN"
```

---

## 🔍 TROUBLESHOOTING

### Problema: Biblioteca kubernetes não instalada

**Sintoma:**
```
WARNING - Biblioteca 'kubernetes' não instalada. Collector Kubernetes desabilitado.
```

**Solução:**
```bash
cd probe
pip install kubernetes pyyaml
# Reiniciar probe
.\parar_todas_probes.bat
.\iniciar_probe_limpo.bat
```

---

### Problema: Connection Refused

**Sintoma:**
```
ERROR - Erro API Kubernetes: Connection refused
```

**Causas possíveis:**
- API Server não está acessível
- Firewall bloqueando porta 6443
- Endpoint incorreto

**Solução:**
```bash
# Testar conectividade
curl -k https://CLUSTER_ENDPOINT:6443

# Verificar firewall (Windows)
Test-NetConnection -ComputerName CLUSTER_IP -Port 6443

# Verificar endpoint no banco
SELECT api_endpoint FROM kubernetes_clusters;
```

---

### Problema: 401 Unauthorized

**Sintoma:**
```
ERROR - Erro API Kubernetes: 401 - Unauthorized
```

**Causas possíveis:**
- Token expirado
- Kubeconfig inválido
- Credenciais incorretas

**Solução:**
```bash
# Regenerar token
kubectl create token coruja-monitor -n default --duration=8760h

# Ou exportar kubeconfig novamente
kubectl config view --raw > kubeconfig.yaml

# Atualizar no frontend:
# Servidores → Editar cluster → Atualizar credenciais
```

---

### Problema: 403 Forbidden

**Sintoma:**
```
ERROR - Erro API Kubernetes: 403 - Forbidden
```

**Causa:** Service Account sem permissões RBAC

**Solução:**
```bash
# Verificar ClusterRoleBinding
kubectl get clusterrolebinding coruja-monitor

# Se não existir, criar:
kubectl create clusterrolebinding coruja-monitor \
  --clusterrole=view \
  --serviceaccount=default:coruja-monitor

# Verificar permissões
kubectl auth can-i list nodes --as=system:serviceaccount:default:coruja-monitor
```

---

### Problema: Metrics Server Not Found

**Sintoma:**
```
WARNING - Metrics Server não disponível
```

**Causa:** Metrics Server não instalado no cluster

**Solução:**
```bash
# Instalar Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Para ambientes de desenvolvimento (sem TLS):
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

# Verificar instalação
kubectl get deployment metrics-server -n kube-system
```

---

### Problema: Nenhum recurso coletado

**Sintoma:**
- Cluster configurado
- Probe rodando
- Mas nenhum recurso aparece

**Verificar:**

1. **Cluster está ativo?**
   ```sql
   SELECT id, cluster_name, is_active FROM kubernetes_clusters;
   ```
   Se `is_active = false`, ativar no frontend.

2. **Recursos selecionados?**
   ```sql
   SELECT id, cluster_name, selected_resources FROM kubernetes_clusters;
   ```
   Se vazio, editar cluster e selecionar recursos.

3. **Probe está rodando?**
   ```powershell
   Get-Process -Name python | Where-Object { $_.CommandLine -like "*probe*" }
   ```

4. **Logs mostram erros?**
   ```powershell
   Get-Content probe\probe.log -Tail 100 | Select-String -Pattern "error|ERROR"
   ```

---

### Problema: Token de probe inválido

**Sintoma:**
```
ERROR - Token de probe inválido
```

**Solução:**
```powershell
# Verificar token no arquivo de configuração
Get-Content probe\probe_config.json

# Ou reconfigurar probe
cd probe
.\configurar_probe.bat
```

---

## 📚 REFERÊNCIAS

### Documentação do Sistema

- `RESUMO_COMPLETO_KUBERNETES_27FEV.md` - Visão geral completa
- `INTEGRACAO_KUBERNETES_PROBE_27FEV.md` - Integração técnica
- `REQUISITOS_KUBERNETES_27FEV.md` - Requisitos e configuração
- `KUBERNETES_APIS_METRICAS_27FEV.md` - APIs e fórmulas
- `BACKEND_KUBERNETES_IMPLEMENTADO_27FEV.md` - Backend API
- `GUIA_RAPIDO_KUBERNETES.md` - Guia rápido

### Scripts Úteis

- `testar_integracao_kubernetes.ps1` - Teste completo
- `testar_backend_kubernetes.ps1` - Teste do backend
- `testar_kubernetes_wizard.ps1` - Teste do wizard

### Documentação Externa

- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Metrics Server](https://github.com/kubernetes-sigs/metrics-server)
- [Python Kubernetes Client](https://github.com/kubernetes-client/python)
- [CheckMK Kubernetes Monitoring](https://docs.checkmk.com/latest/en/monitoring_kubernetes.html)
- [Prometheus Kubernetes SD](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#kubernetes_sd_config)

---

## 🎯 PRÓXIMOS PASSOS

### Curto Prazo
1. Criar dashboards no frontend
2. Implementar alertas
3. Adicionar mais clusters
4. Implementar criptografia de credenciais

### Médio Prazo
1. Auto-discovery assíncrono
2. Logs de pods em tempo real
3. Exec em containers
4. Port-forward
5. Visualização de relacionamentos

### Longo Prazo
1. Auto-scaling
2. Integração com Helm
3. GitOps
4. Backup e restore
5. Cost optimization
6. Multi-cluster management
7. Service mesh monitoring

---

## 📞 SUPORTE

Para dúvidas ou problemas:

1. **Consultar documentação**
   - Ler este guia completo
   - Verificar seção de Troubleshooting

2. **Executar script de teste**
   ```powershell
   .\testar_integracao_kubernetes.ps1
   ```

3. **Verificar logs**
   ```powershell
   Get-Content probe\probe.log -Tail 50 -Wait
   ```

4. **Verificar banco de dados**
   ```sql
   -- Clusters configurados
   SELECT * FROM kubernetes_clusters;
   
   -- Recursos coletados
   SELECT resource_type, COUNT(*) FROM kubernetes_resources GROUP BY resource_type;
   
   -- Métricas recentes
   SELECT * FROM kubernetes_metrics ORDER BY timestamp DESC LIMIT 20;
   ```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Sistema Coruja Monitor instalado
- [ ] Probe instalado e configurado
- [ ] Biblioteca kubernetes instalada (`pip install kubernetes pyyaml`)
- [ ] Credenciais do cluster obtidas (kubeconfig ou token)
- [ ] Cluster configurado via wizard
- [ ] Teste de conexão bem-sucedido
- [ ] Recursos selecionados (nodes, pods, deployments)
- [ ] Probe reiniciado
- [ ] Logs verificados (coleta funcionando)
- [ ] Recursos aparecendo no banco de dados
- [ ] Script de teste executado com sucesso

---

**Data:** 27 de Fevereiro de 2026  
**Versão:** 1.0  
**Status:** ✅ DOCUMENTAÇÃO COMPLETA

---

**Desenvolvido por:** Kiro AI Assistant  
**Baseado em:** CheckMK, Prometheus, Grafana, PRTG, SolarWinds, Zabbix  
**Padrões:** Kubernetes API, Metrics Server, RBAC, REST API
