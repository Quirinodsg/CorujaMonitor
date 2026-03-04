# Guia Rápido - Monitoramento Kubernetes

## 🚀 Como Usar o Wizard

### Passo 1: Acessar o Wizard
1. Acesse http://localhost:3000
2. Login: `admin@coruja.com` / `admin123`
3. Vá em "Servidores Monitorados"
4. Clique em "☁️ Monitorar Serviços"
5. Clique em "☸️ Kubernetes"

### Passo 2: Obter Credenciais

#### Opção A: Kubeconfig (Recomendado)
```bash
# Exportar kubeconfig completo
kubectl config view --raw > kubeconfig.yaml

# Copiar conteúdo
cat kubeconfig.yaml
```

#### Opção B: Service Account Token
```bash
# Criar Service Account
kubectl create serviceaccount coruja-monitor
kubectl create clusterrolebinding coruja-monitor \
  --clusterrole=view \
  --serviceaccount=default:coruja-monitor

# Gerar token
kubectl create token coruja-monitor --duration=8760h
```

#### Opção C: Clusters Gerenciados
```bash
# Azure AKS
az aks get-credentials --resource-group RG --name CLUSTER

# AWS EKS
aws eks update-kubeconfig --name CLUSTER --region REGION

# Google GKE
gcloud container clusters get-credentials CLUSTER --zone ZONE
```

### Passo 3: Configurar no Wizard
1. **Passo 1:** Leia os requisitos
2. **Passo 2:** Preencha:
   - Nome do cluster
   - Tipo (Vanilla/AKS/EKS/GKE/OpenShift)
   - API endpoint (ex: https://cluster.example.com:6443)
   - Método de autenticação
   - Cole as credenciais
3. **Passo 3:** Teste a conexão
4. **Passo 4:** Selecione recursos para monitorar

---

## 📊 Recursos Disponíveis

| Recurso | Métricas | Alertas |
|---------|----------|---------|
| **Nodes** | CPU %, Memória %, Disco %, Pods | > 85% CPU, > 90% Memória |
| **Pods** | Status, Restarts, CPU, Memória | CrashLoop, > 5 restarts |
| **Deployments** | Réplicas (desired/ready) | Ready < Desired |
| **DaemonSets** | Coverage % | < 100% coverage |
| **StatefulSets** | Réplicas (desired/ready) | Ready < Desired |
| **Services** | Endpoints disponíveis | 0 endpoints |
| **Ingress** | Hosts, Paths, TLS | - |
| **PV** | Capacidade, Uso | > 80% uso |

---

## 🔧 Requisitos Técnicos

### Obrigatório
- ✅ Kubernetes 1.19+
- ✅ Metrics Server instalado
- ✅ Acesso ao API Server (porta 6443)
- ✅ Credenciais válidas (kubeconfig ou token)

### Verificar Metrics Server
```bash
kubectl get deployment metrics-server -n kube-system
```

### Instalar Metrics Server (se necessário)
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

## 🚨 Troubleshooting

### Erro: Connection Refused
- Verificar se API Server está acessível
- Testar: `curl -k https://API_ENDPOINT:6443`
- Verificar firewall

### Erro: 401 Unauthorized
- Token expirado ou inválido
- Regenerar token
- Verificar kubeconfig

### Erro: 403 Forbidden
- Service Account sem permissões RBAC
- Adicionar ClusterRoleBinding com role "view"

### Erro: Metrics Server Not Found
- Metrics Server não instalado
- Instalar usando comando acima

---

## 📈 Dashboards Recomendados

### Cluster Overview
- Total de nodes (ready/not ready)
- Uso total de CPU e memória
- Pods rodando vs capacidade
- Pods com problemas

### Node Details
- CPU e memória por node
- Pods por node
- Condições (DiskPressure, MemoryPressure)

### Workload Health
- Deployments com réplicas insuficientes
- Pods em CrashLoop
- DaemonSets não rodando em todos os nodes

---

## 🎯 Melhores Práticas

### Segurança
- ✅ Use Service Account com permissões mínimas (view)
- ✅ Não use tokens de admin
- ✅ Configure expiração de tokens
- ✅ Use certificados TLS válidos

### Performance
- ✅ Intervalo de coleta: 60 segundos
- ✅ Filtre namespaces desnecessários
- ✅ Selecione apenas recursos necessários
- ✅ Use auto-discovery incremental

### Monitoramento
- ✅ Configure alertas para métricas críticas
- ✅ Monitore nodes e pods
- ✅ Acompanhe deployments
- ✅ Verifique Metrics Server regularmente

---

## 📚 Documentação Completa

- **Requisitos:** `REQUISITOS_KUBERNETES_27FEV.md`
- **APIs e Métricas:** `KUBERNETES_APIS_METRICAS_27FEV.md`
- **Implementação:** `KUBERNETES_WIZARD_IMPLEMENTADO_27FEV.md`

---

## 🆘 Suporte

### Comandos Úteis
```bash
# Listar pods com problemas
kubectl get pods --all-namespaces --field-selector=status.phase!=Running

# Top pods por CPU
kubectl top pods --all-namespaces --sort-by=cpu

# Top pods por memória
kubectl top pods --all-namespaces --sort-by=memory

# Verificar nodes
kubectl get nodes

# Verificar deployments
kubectl get deployments --all-namespaces
```

### Links Úteis
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Metrics Server](https://github.com/kubernetes-sigs/metrics-server)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

**Última atualização:** 27 FEV 2026
