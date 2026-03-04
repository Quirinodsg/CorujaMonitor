# APIs e Métricas Kubernetes
## Endpoints, Queries e Fórmulas de Cálculo

## 📡 Kubernetes API Endpoints

### Core API (v1)

#### Nodes
```
GET /api/v1/nodes
GET /api/v1/nodes/{name}
GET /api/v1/nodes/{name}/status
```

**Campos Importantes:**
```json
{
  "status": {
    "capacity": {
      "cpu": "4",
      "memory": "16Gi",
      "pods": "110"
    },
    "allocatable": {
      "cpu": "3800m",
      "memory": "15Gi",
      "pods": "110"
    },
    "conditions": [
      {
        "type": "Ready",
        "status": "True"
      },
      {
        "type": "MemoryPressure",
        "status": "False"
      },
      {
        "type": "DiskPressure",
        "status": "False"
      }
    ]
  }
}
```

#### Pods
```
GET /api/v1/pods
GET /api/v1/namespaces/{namespace}/pods
GET /api/v1/namespaces/{namespace}/pods/{name}
```

**Campos Importantes:**
```json
{
  "status": {
    "phase": "Running",
    "conditions": [
      {
        "type": "Ready",
        "status": "True"
      }
    ],
    "containerStatuses": [
      {
        "name": "app",
        "ready": true,
        "restartCount": 0,
        "state": {
          "running": {
            "startedAt": "2024-02-27T10:00:00Z"
          }
        }
      }
    ]
  }
}
```

#### Services
```
GET /api/v1/services
GET /api/v1/namespaces/{namespace}/services
GET /api/v1/namespaces/{namespace}/endpoints/{name}
```

#### Namespaces
```
GET /api/v1/namespaces
GET /api/v1/namespaces/{name}
```

#### Persistent Volumes
```
GET /api/v1/persistentvolumes
GET /api/v1/persistentvolumeclaims
GET /api/v1/namespaces/{namespace}/persistentvolumeclaims
```

---

### Apps API (apps/v1)

#### Deployments
```
GET /apis/apps/v1/deployments
GET /apis/apps/v1/namespaces/{namespace}/deployments
GET /apis/apps/v1/namespaces/{namespace}/deployments/{name}
```

**Campos Importantes:**
```json
{
  "spec": {
    "replicas": 3
  },
  "status": {
    "replicas": 3,
    "updatedReplicas": 3,
    "readyReplicas": 3,
    "availableReplicas": 3,
    "conditions": [
      {
        "type": "Available",
        "status": "True"
      },
      {
        "type": "Progressing",
        "status": "True"
      }
    ]
  }
}
```

#### DaemonSets
```
GET /apis/apps/v1/daemonsets
GET /apis/apps/v1/namespaces/{namespace}/daemonsets
```

**Campos Importantes:**
```json
{
  "status": {
    "desiredNumberScheduled": 5,
    "currentNumberScheduled": 5,
    "numberReady": 5,
    "numberAvailable": 5
  }
}
```

#### StatefulSets
```
GET /apis/apps/v1/statefulsets
GET /apis/apps/v1/namespaces/{namespace}/statefulsets
```

#### ReplicaSets
```
GET /apis/apps/v1/replicasets
GET /apis/apps/v1/namespaces/{namespace}/replicasets
```

---

### Batch API (batch/v1)

#### Jobs
```
GET /apis/batch/v1/jobs
GET /apis/batch/v1/namespaces/{namespace}/jobs
```

#### CronJobs
```
GET /apis/batch/v1/cronjobs
GET /apis/batch/v1/namespaces/{namespace}/cronjobs
```

---

### Networking API (networking.k8s.io/v1)

#### Ingress
```
GET /apis/networking.k8s.io/v1/ingresses
GET /apis/networking.k8s.io/v1/namespaces/{namespace}/ingresses
```

---

### Metrics API (metrics.k8s.io/v1beta1)

#### Node Metrics
```
GET /apis/metrics.k8s.io/v1beta1/nodes
GET /apis/metrics.k8s.io/v1beta1/nodes/{name}
```

**Resposta:**
```json
{
  "metadata": {
    "name": "node-1"
  },
  "timestamp": "2024-02-27T10:00:00Z",
  "window": "30s",
  "usage": {
    "cpu": "250m",
    "memory": "4Gi"
  }
}
```

#### Pod Metrics
```
GET /apis/metrics.k8s.io/v1beta1/pods
GET /apis/metrics.k8s.io/v1beta1/namespaces/{namespace}/pods
GET /apis/metrics.k8s.io/v1beta1/namespaces/{namespace}/pods/{name}
```

**Resposta:**
```json
{
  "metadata": {
    "name": "my-pod",
    "namespace": "default"
  },
  "timestamp": "2024-02-27T10:00:00Z",
  "window": "30s",
  "containers": [
    {
      "name": "app",
      "usage": {
        "cpu": "100m",
        "memory": "256Mi"
      }
    }
  ]
}
```

---

## 📊 Fórmulas de Cálculo

### CPU

#### CPU Usage Percentage (Node)
```
CPU % = (current_usage_millicores / allocatable_millicores) * 100

Exemplo:
current_usage = 2500m (2.5 cores)
allocatable = 3800m (3.8 cores)
CPU % = (2500 / 3800) * 100 = 65.79%
```

#### CPU Usage Percentage (Pod)
```
CPU % = (pod_usage_millicores / pod_limit_millicores) * 100

Se não houver limite definido, usar allocatable do node
```

#### Conversão de Unidades
```
1 core = 1000 millicores (m)
250m = 0.25 cores = 25% de 1 core
```

---

### Memória

#### Memory Usage Percentage (Node)
```
Memory % = (current_usage_bytes / allocatable_bytes) * 100

Exemplo:
current_usage = 8Gi = 8589934592 bytes
allocatable = 15Gi = 16106127360 bytes
Memory % = (8589934592 / 16106127360) * 100 = 53.33%
```

#### Memory Usage Percentage (Pod)
```
Memory % = (pod_usage_bytes / pod_limit_bytes) * 100

Se não houver limite definido, usar allocatable do node
```

#### Conversão de Unidades
```
1 Ki = 1024 bytes
1 Mi = 1024 Ki = 1048576 bytes
1 Gi = 1024 Mi = 1073741824 bytes
1 Ti = 1024 Gi = 1099511627776 bytes
```

---

### Pods

#### Pod Capacity Usage (Node)
```
Pod Capacity % = (current_pods / max_pods) * 100

Exemplo:
current_pods = 45
max_pods = 110
Pod Capacity % = (45 / 110) * 100 = 40.91%
```

---

### Deployments

#### Deployment Health
```
Health % = (ready_replicas / desired_replicas) * 100

Status:
- 100% = Healthy
- 50-99% = Degraded
- 0-49% = Critical
- 0% = Down
```

#### Deployment Availability
```
Available = (available_replicas > 0)

Conditions:
- Available = True: Pelo menos 1 réplica disponível
- Progressing = True: Rollout em andamento
- ReplicaFailure = True: Falha ao criar réplicas
```

---

### DaemonSets

#### DaemonSet Coverage
```
Coverage % = (number_ready / desired_number_scheduled) * 100

Exemplo:
number_ready = 4
desired_number_scheduled = 5
Coverage % = (4 / 5) * 100 = 80%
```

---

### StatefulSets

#### StatefulSet Health
```
Health % = (ready_replicas / desired_replicas) * 100

StatefulSets devem ter TODAS as réplicas prontas
Alerta se ready_replicas < desired_replicas
```

---

### Persistent Volumes

#### PV Usage Percentage
```
PV Usage % = (used_bytes / capacity_bytes) * 100

Obter de:
- kubectl top pv (se disponível)
- Prometheus metrics
- Node filesystem metrics
```

---

## 🔍 Queries Úteis

### Listar todos os pods com problemas
```bash
kubectl get pods --all-namespaces --field-selector=status.phase!=Running,status.phase!=Succeeded
```

### Listar pods com muitos restarts
```bash
kubectl get pods --all-namespaces --sort-by='.status.containerStatuses[0].restartCount' | tail -10
```

### Top pods por CPU
```bash
kubectl top pods --all-namespaces --sort-by=cpu | head -10
```

### Top pods por memória
```bash
kubectl top pods --all-namespaces --sort-by=memory | head -10
```

### Nodes com problemas
```bash
kubectl get nodes -o json | jq '.items[] | select(.status.conditions[] | select(.type=="Ready" and .status!="True")) | .metadata.name'
```

### Deployments com réplicas insuficientes
```bash
kubectl get deployments --all-namespaces -o json | jq '.items[] | select(.status.readyReplicas < .spec.replicas) | {namespace: .metadata.namespace, name: .metadata.name, ready: .status.readyReplicas, desired: .spec.replicas}'
```

---

## 📈 Métricas Agregadas

### Cluster Level

#### Total CPU Capacity
```
Sum of all nodes allocatable CPU
```

#### Total Memory Capacity
```
Sum of all nodes allocatable memory
```

#### Total Pods Running
```
Count of all pods with status.phase = "Running"
```

#### Cluster CPU Usage %
```
(Sum of all nodes current CPU usage / Sum of all nodes allocatable CPU) * 100
```

#### Cluster Memory Usage %
```
(Sum of all nodes current memory usage / Sum of all nodes allocatable memory) * 100
```

---

### Namespace Level

#### Namespace CPU Usage
```
Sum of all pods CPU usage in namespace
```

#### Namespace Memory Usage
```
Sum of all pods memory usage in namespace
```

#### Namespace Pod Count
```
Count of pods in namespace
```

---

## 🚨 Thresholds Recomendados

### Nodes
| Métrica | Warning | Critical |
|---------|---------|----------|
| CPU % | 70% | 85% |
| Memory % | 80% | 90% |
| Disk % | 80% | 90% |
| Pod Capacity % | 80% | 95% |

### Pods
| Métrica | Warning | Critical |
|---------|---------|----------|
| Restarts (10 min) | 3 | 5 |
| CPU % (vs limit) | 80% | 95% |
| Memory % (vs limit) | 80% | 95% |
| Pending Time | 5 min | 10 min |

### Deployments
| Métrica | Warning | Critical |
|---------|---------|----------|
| Ready Replicas % | < 100% | < 50% |
| Available Replicas | < desired | 0 |

### DaemonSets
| Métrica | Warning | Critical |
|---------|---------|----------|
| Coverage % | < 100% | < 80% |

---

## 🔧 Exemplo de Implementação Python

```python
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Carregar kubeconfig
config.load_kube_config()

# Criar clientes API
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
metrics_api = client.CustomObjectsApi()

# Obter nodes
def get_nodes():
    try:
        nodes = v1.list_node()
        for node in nodes.items:
            name = node.metadata.name
            status = node.status.conditions[-1].type
            cpu_capacity = node.status.capacity['cpu']
            memory_capacity = node.status.capacity['memory']
            print(f"Node: {name}, Status: {status}, CPU: {cpu_capacity}, Memory: {memory_capacity}")
    except ApiException as e:
        print(f"Error: {e}")

# Obter métricas de nodes
def get_node_metrics():
    try:
        metrics = metrics_api.list_cluster_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            plural="nodes"
        )
        for item in metrics['items']:
            name = item['metadata']['name']
            cpu_usage = item['usage']['cpu']
            memory_usage = item['usage']['memory']
            print(f"Node: {name}, CPU Usage: {cpu_usage}, Memory Usage: {memory_usage}")
    except ApiException as e:
        print(f"Error: {e}")

# Obter pods
def get_pods(namespace='default'):
    try:
        pods = v1.list_namespaced_pod(namespace)
        for pod in pods.items:
            name = pod.metadata.name
            phase = pod.status.phase
            restarts = sum([c.restart_count for c in pod.status.container_statuses or []])
            print(f"Pod: {name}, Phase: {phase}, Restarts: {restarts}")
    except ApiException as e:
        print(f"Error: {e}")

# Obter deployments
def get_deployments(namespace='default'):
    try:
        deployments = apps_v1.list_namespaced_deployment(namespace)
        for deployment in deployments.items:
            name = deployment.metadata.name
            desired = deployment.spec.replicas
            ready = deployment.status.ready_replicas or 0
            health = (ready / desired * 100) if desired > 0 else 0
            print(f"Deployment: {name}, Desired: {desired}, Ready: {ready}, Health: {health:.1f}%")
    except ApiException as e:
        print(f"Error: {e}")

# Executar
if __name__ == "__main__":
    print("=== Nodes ===")
    get_nodes()
    print("\n=== Node Metrics ===")
    get_node_metrics()
    print("\n=== Pods ===")
    get_pods()
    print("\n=== Deployments ===")
    get_deployments()
```

---

## 📚 Bibliotecas Recomendadas

### Python
- **kubernetes:** Cliente oficial Python
- **prometheus-client:** Exportar métricas para Prometheus
- **pykube-ng:** Cliente alternativo mais simples

### Go
- **client-go:** Cliente oficial Go
- **controller-runtime:** Framework para controllers

### Node.js
- **@kubernetes/client-node:** Cliente oficial Node.js

---

## 🔗 Referências

- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Metrics Server](https://github.com/kubernetes-sigs/metrics-server)
- [Python Kubernetes Client](https://github.com/kubernetes-client/python)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
