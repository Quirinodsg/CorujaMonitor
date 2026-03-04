# Requisitos para Monitoramento Kubernetes
## Baseado em CheckMK, Prometheus e Grafana

## 📋 Visão Geral

O monitoramento Kubernetes permite coletar métricas de clusters, nodes, pods, deployments e outros recursos de forma automática, com auto-discovery e atualização em tempo real.

---

## 🔐 Métodos de Autenticação

### 1. Kubeconfig File (Recomendado)

**Descrição:** Arquivo de configuração padrão do kubectl contendo certificados e credenciais.

**Localização:** `~/.kube/config`

**Como obter:**
```bash
# Visualizar kubeconfig atual
kubectl config view

# Exportar kubeconfig completo (com certificados)
kubectl config view --raw > kubeconfig.yaml

# Para clusters gerenciados:
# Azure AKS
az aks get-credentials --resource-group RG_NAME --name CLUSTER_NAME

# AWS EKS
aws eks update-kubeconfig --name CLUSTER_NAME --region REGION

# Google GKE
gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE
```

**Vantagens:**
- Método mais completo e seguro
- Suporta múltiplos clusters e contextos
- Inclui certificados CA automaticamente
- Funciona com todos os tipos de cluster

---

### 2. Service Account Token

**Descrição:** Token de um Service Account com permissões RBAC de leitura.

**Como criar:**
```bash
# 1. Criar Service Account
kubectl create serviceaccount coruja-monitor -n default

# 2. Criar ClusterRoleBinding (permissões de leitura)
kubectl create clusterrolebinding coruja-monitor \
  --clusterrole=view \
  --serviceaccount=default:coruja-monitor

# 3. Gerar token (Kubernetes 1.24+)
kubectl create token coruja-monitor -n default --duration=8760h

# Para Kubernetes < 1.24, obter do secret:
kubectl get secret $(kubectl get serviceaccount coruja-monitor -n default -o jsonpath='{.secrets[0].name}') -n default -o jsonpath='{.data.token}' | base64 --decode
```

**Permissões RBAC Necessárias:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: coruja-monitor-role
rules:
- apiGroups: [""]
  resources: ["nodes", "pods", "services", "endpoints", "namespaces", "persistentvolumes", "persistentvolumeclaims"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "daemonsets", "statefulsets", "replicasets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["batch"]
  resources: ["jobs", "cronjobs"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["metrics.k8s.io"]
  resources: ["nodes", "pods"]
  verbs: ["get", "list"]
```

**Vantagens:**
- Controle granular de permissões
- Pode ser revogado facilmente
- Ideal para ambientes de produção

---

### 3. Bearer Token

**Descrição:** Token de autenticação direto, comum em clusters gerenciados.

**Como obter:**
- **AKS:** `az account get-access-token --resource https://management.azure.com`
- **EKS:** `aws eks get-token --cluster-name CLUSTER_NAME`
- **GKE:** `gcloud auth print-access-token`

**Desvantagens:**
- Tokens podem expirar periodicamente
- Requer renovação automática

---

## ☸️ Tipos de Cluster Suportados

### Vanilla Kubernetes
- Kubernetes instalado manualmente (kubeadm, kubespray, etc.)
- Requer acesso direto ao API Server
- Porta padrão: 6443

### Azure AKS (Azure Kubernetes Service)
- Cluster gerenciado pela Microsoft Azure
- Autenticação via Azure AD ou kubeconfig
- Integração com Azure Monitor

### AWS EKS (Elastic Kubernetes Service)
- Cluster gerenciado pela Amazon AWS
- Autenticação via IAM ou kubeconfig
- Integração com CloudWatch

### Google GKE (Google Kubernetes Engine)
- Cluster gerenciado pelo Google Cloud
- Autenticação via Google Cloud IAM
- Integração com Cloud Monitoring

### Red Hat OpenShift
- Distribuição enterprise do Kubernetes
- Recursos adicionais (Routes, BuildConfigs)
- Autenticação via OAuth

---

## 📊 Recursos Monitorados

### 1. Cluster (Nível Global)
**Métricas:**
- Status geral do cluster
- Número total de nodes (ready/not ready)
- Capacidade total de CPU e memória
- Número total de pods rodando
- Versão do Kubernetes

**APIs Utilizadas:**
- `/api/v1/nodes`
- `/api/v1/componentstatuses`

---

### 2. Nodes (Servidores do Cluster)
**Métricas:**
- **CPU:** Uso atual, capacidade total, % utilização
- **Memória:** Uso atual, capacidade total, % utilização
- **Disco:** Uso do filesystem, inodes
- **Rede:** Bytes TX/RX
- **Pods:** Número de pods por node, capacidade máxima
- **Status:** Ready, NotReady, Unknown
- **Condições:** DiskPressure, MemoryPressure, PIDPressure

**APIs Utilizadas:**
- `/api/v1/nodes`
- `/apis/metrics.k8s.io/v1beta1/nodes`

**Thresholds Recomendados:**
- CPU: Warning 70%, Critical 85%
- Memória: Warning 80%, Critical 90%
- Disco: Warning 80%, Critical 90%

---

### 3. Pods (Containers Agrupados)
**Métricas:**
- **Status:** Running, Pending, Failed, Succeeded, Unknown
- **Restarts:** Número de reinicializações
- **CPU:** Uso por container
- **Memória:** Uso por container
- **Rede:** Bytes TX/RX
- **Fase:** Pending, Running, Succeeded, Failed, Unknown
- **Condições:** PodScheduled, Ready, Initialized, ContainersReady

**APIs Utilizadas:**
- `/api/v1/pods`
- `/apis/metrics.k8s.io/v1beta1/pods`

**Alertas Importantes:**
- Pod com restarts frequentes (> 5 em 10 minutos)
- Pod em CrashLoopBackOff
- Pod Pending por muito tempo (> 5 minutos)
- Pod usando > 90% do limite de memória

---

### 4. Deployments (Aplicações)
**Métricas:**
- Réplicas desejadas vs disponíveis
- Réplicas atualizadas
- Réplicas prontas
- Status do rollout
- Condições: Available, Progressing, ReplicaFailure

**APIs Utilizadas:**
- `/apis/apps/v1/deployments`

**Alertas:**
- Réplicas disponíveis < réplicas desejadas
- Rollout travado (Progressing = False)

---

### 5. DaemonSets (Pods por Node)
**Métricas:**
- Número de nodes que devem rodar o pod
- Número de nodes rodando o pod
- Número de nodes prontos
- Número de nodes com erro

**APIs Utilizadas:**
- `/apis/apps/v1/daemonsets`

**Alertas:**
- Pods não rodando em todos os nodes esperados

---

### 6. StatefulSets (Aplicações com Estado)
**Métricas:**
- Réplicas desejadas vs prontas
- Réplicas atualizadas
- Revisão atual
- Status de cada réplica

**APIs Utilizadas:**
- `/apis/apps/v1/statefulsets`

---

### 7. Services (Endpoints de Rede)
**Métricas:**
- Tipo de service (ClusterIP, NodePort, LoadBalancer)
- Número de endpoints disponíveis
- Portas expostas
- Selector labels

**APIs Utilizadas:**
- `/api/v1/services`
- `/api/v1/endpoints`

**Alertas:**
- Service sem endpoints disponíveis

---

### 8. Ingress (Rotas HTTP/HTTPS)
**Métricas:**
- Hosts configurados
- Paths e backends
- TLS configurado
- Status do ingress controller

**APIs Utilizadas:**
- `/apis/networking.k8s.io/v1/ingresses`

---

### 9. Persistent Volumes (Armazenamento)
**Métricas:**
- Capacidade total
- Uso atual
- Status: Available, Bound, Released, Failed
- Storage class
- Access modes

**APIs Utilizadas:**
- `/api/v1/persistentvolumes`
- `/api/v1/persistentvolumeclaims`

**Alertas:**
- PV usando > 80% da capacidade
- PVC em estado Pending

---

## 🔧 Requisitos Técnicos

### Metrics Server
O Metrics Server é **obrigatório** para coletar métricas de CPU e memória.

**Verificar se está instalado:**
```bash
kubectl get deployment metrics-server -n kube-system
```

**Instalar Metrics Server:**
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Para ambientes de desenvolvimento (sem TLS):**
```bash
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

---

### Permissões de Rede
- Porta 6443 (API Server) deve estar acessível
- Firewall deve permitir conexões HTTPS
- Certificados TLS válidos (ou skip-tls-verify para dev)

---

### Intervalo de Coleta
- **Recomendado:** 60 segundos
- **Mínimo:** 30 segundos (pode sobrecarregar o API Server)
- **Máximo:** 300 segundos (5 minutos)

---

## 📈 Dashboards Recomendados

### Dashboard de Cluster
- Status geral (nodes ready/total)
- Uso total de CPU e memória
- Número de pods rodando
- Pods com problemas (CrashLoop, Pending)

### Dashboard de Nodes
- Lista de nodes com status
- CPU e memória por node
- Pods por node
- Condições (DiskPressure, MemoryPressure)

### Dashboard de Workloads
- Deployments com réplicas insuficientes
- StatefulSets com problemas
- DaemonSets não rodando em todos os nodes
- Jobs falhados

### Dashboard de Recursos
- Top 10 pods por CPU
- Top 10 pods por memória
- Persistent Volumes por uso
- Services sem endpoints

---

## 🚨 Alertas Críticos

### Cluster
- ❌ Mais de 50% dos nodes NotReady
- ❌ API Server inacessível
- ❌ Metrics Server não disponível

### Nodes
- ❌ Node NotReady por > 5 minutos
- ❌ CPU > 90% por > 10 minutos
- ❌ Memória > 95%
- ❌ Disco > 90%

### Pods
- ❌ Pod em CrashLoopBackOff
- ❌ Pod com > 10 restarts em 1 hora
- ❌ Pod Pending por > 10 minutos
- ❌ Pod usando > 95% do limite de memória

### Deployments
- ❌ Réplicas disponíveis = 0
- ❌ Rollout travado por > 15 minutos

---

## 🔍 Troubleshooting

### Erro: "Connection Refused"
- Verificar se API Server está rodando
- Verificar firewall e regras de rede
- Testar conectividade: `curl -k https://API_ENDPOINT:6443`

### Erro: "401 Unauthorized"
- Token expirado ou inválido
- Regenerar token do Service Account
- Verificar kubeconfig

### Erro: "403 Forbidden"
- Service Account sem permissões RBAC
- Verificar ClusterRoleBinding
- Adicionar permissões necessárias

### Erro: "Metrics Server Not Found"
- Metrics Server não instalado
- Instalar: `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`

### Erro: "Certificate Error"
- CA certificate inválido
- Usar `--insecure-skip-tls-verify` para dev
- Obter CA correto do cluster

---

## 📚 Referências

- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Metrics Server](https://github.com/kubernetes-sigs/metrics-server)
- [CheckMK Kubernetes Monitoring](https://docs.checkmk.com/latest/en/monitoring_kubernetes.html)
- [Prometheus Kubernetes SD](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#kubernetes_sd_config)
- [Grafana Kubernetes Dashboards](https://grafana.com/grafana/dashboards/?search=kubernetes)

---

## ✅ Checklist de Implementação

- [ ] Obter kubeconfig ou criar Service Account
- [ ] Verificar conectividade com API Server
- [ ] Confirmar Metrics Server instalado
- [ ] Testar permissões RBAC
- [ ] Configurar intervalo de coleta (60s recomendado)
- [ ] Selecionar namespaces para monitorar
- [ ] Escolher tipos de recursos (nodes, pods, deployments, etc.)
- [ ] Configurar thresholds de alerta
- [ ] Testar auto-discovery de novos recursos
- [ ] Validar dashboards e visualizações
