"""
Kubernetes Collector - Coleta métricas de clusters Kubernetes
Data: 27 FEV 2026
Baseado em: CheckMK, Prometheus, Grafana
"""

import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
import tempfile
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verificar se biblioteca kubernetes está disponível
try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    logger.warning("Biblioteca 'kubernetes' não instalada. Collector Kubernetes desabilitado.")
    logger.warning("Para habilitar: pip install kubernetes pyyaml")


class KubernetesCollector:
    """Coletor de métricas Kubernetes"""
    
    def __init__(self, api_url: str, probe_token: str):
        if not KUBERNETES_AVAILABLE:
            raise ImportError("Biblioteca 'kubernetes' não está instalada")
        
        self.api_url = api_url
        self.probe_token = probe_token
        self.headers = {"Authorization": f"Bearer {self.probe_token}"}
        self.resource_buffer = []
    
    def collect_all_clusters(self):
        """Coletar métricas de todos os clusters ativos"""
        try:
            # Buscar clusters ativos (com credenciais descriptografadas)
            response = requests.get(
                f"{self.api_url}/api/v1/kubernetes/clusters/for-collector",
                params={"probe_token": self.probe_token},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Erro ao buscar clusters: {response.status_code}")
                return
            
            clusters = response.json()
            logger.info(f"📊 Encontrados {len(clusters)} cluster(s) Kubernetes")
            
            for cluster in clusters:
                self.collect_cluster_metrics(cluster)
        
        except Exception as e:
            logger.error(f"❌ Erro ao coletar clusters: {e}")
    
    def collect_cluster_metrics(self, cluster: Dict):
        """Coletar métricas de um cluster específico"""
        cluster_id = cluster["id"]
        cluster_name = cluster["cluster_name"]
        
        logger.info(f"🔍 Coletando métricas do cluster: {cluster_name}")
        
        try:
            # Configurar autenticação
            self._configure_auth(cluster)
            
            # Criar clientes API
            v1 = client.CoreV1Api()
            apps_v1 = client.AppsV1Api()
            metrics_api = client.CustomObjectsApi()
            
            # Coletar métricas baseado nos recursos selecionados
            selected_resources = cluster.get("selected_resources", [])
            
            if "nodes" in selected_resources:
                self._collect_nodes(cluster_id, v1, metrics_api)
            
            if "pods" in selected_resources:
                self._collect_pods(cluster_id, v1, metrics_api, cluster)
            
            if "deployments" in selected_resources:
                self._collect_deployments(cluster_id, apps_v1, cluster)
            
            if "daemonsets" in selected_resources:
                self._collect_daemonsets(cluster_id, apps_v1, cluster)
            
            if "statefulsets" in selected_resources:
                self._collect_statefulsets(cluster_id, apps_v1, cluster)
            
            if "services" in selected_resources:
                self._collect_services(cluster_id, v1, cluster)
            
            # Enviar buffer restante
            self._flush_resource_buffer()
            
            # Atualizar timestamp de última coleta
            self._update_last_collected(cluster_id)
            
            logger.info(f"✅ Métricas coletadas com sucesso: {cluster_name}")
        
        except ApiException as e:
            logger.error(f"❌ Erro API Kubernetes ({cluster_name}): {e.status} - {e.reason}")
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas ({cluster_name}): {e}")
    
    def _configure_auth(self, cluster: Dict):
        """Configurar autenticação com o cluster"""
        auth_method = cluster["auth_method"]
        
        if auth_method == "kubeconfig":
            # Salvar kubeconfig em arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
                f.write(cluster["kubeconfig_content"])
                kubeconfig_path = f.name
            
            try:
                config.load_kube_config(config_file=kubeconfig_path)
            finally:
                os.unlink(kubeconfig_path)
        
        elif auth_method in ["service_account", "token"]:
            # Configurar com token
            configuration = client.Configuration()
            configuration.host = cluster["api_endpoint"]
            configuration.api_key = {"authorization": f"Bearer {cluster['service_account_token']}"}
            
            if cluster.get("ca_cert"):
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.crt') as f:
                    f.write(cluster["ca_cert"])
                    configuration.ssl_ca_cert = f.name
            else:
                configuration.verify_ssl = False
            
            client.Configuration.set_default(configuration)
    
    def _collect_nodes(self, cluster_id: int, v1, metrics_api):
        """Coletar métricas de nodes"""
        try:
            # Listar nodes
            nodes = v1.list_node()
            
            # Obter métricas de nodes
            try:
                node_metrics = metrics_api.list_cluster_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    plural="nodes"
                )
                metrics_by_node = {m["metadata"]["name"]: m for m in node_metrics["items"]}
            except:
                metrics_by_node = {}
            
            for node in nodes.items:
                node_name = node.metadata.name
                
                # Capacidade
                capacity = node.status.capacity
                cpu_capacity = self._parse_cpu(capacity.get("cpu", "0"))
                memory_capacity = self._parse_memory(capacity.get("memory", "0"))
                pod_capacity = int(capacity.get("pods", "0"))
                
                # Allocatable
                allocatable = node.status.allocatable
                cpu_allocatable = self._parse_cpu(allocatable.get("cpu", "0"))
                memory_allocatable = self._parse_memory(allocatable.get("memory", "0"))
                
                # Uso atual (do Metrics Server)
                cpu_usage = 0.0
                memory_usage = 0.0
                if node_name in metrics_by_node:
                    usage = metrics_by_node[node_name]["usage"]
                    cpu_usage = self._parse_cpu(usage.get("cpu", "0"))
                    memory_usage = self._parse_memory(usage.get("memory", "0"))
                
                # Calcular percentuais
                cpu_percent = (cpu_usage / cpu_allocatable * 100) if cpu_allocatable > 0 else 0
                memory_percent = (memory_usage / memory_allocatable * 100) if memory_allocatable > 0 else 0
                
                # Status
                ready = False
                for condition in node.status.conditions:
                    if condition.type == "Ready":
                        ready = condition.status == "True"
                        break
                
                # Contar pods no node
                pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}")
                pod_count = len(pods.items)
                
                # Enviar dados para API
                resource_data = {
                    "cluster_id": cluster_id,
                    "resource_type": "node",
                    "resource_name": node_name,
                    "namespace": None,
                    "uid": node.metadata.uid,
                    "status": "Ready" if ready else "NotReady",
                    "ready": ready,
                    "node_cpu_capacity": cpu_capacity,
                    "node_memory_capacity": memory_capacity,
                    "node_cpu_usage": cpu_percent,
                    "node_memory_usage": memory_percent,
                    "node_pod_count": pod_count,
                    "node_pod_capacity": pod_capacity,
                    "labels": node.metadata.labels,
                    "metrics": {
                        "cpu_cores": cpu_capacity,
                        "memory_bytes": memory_capacity,
                        "cpu_usage_cores": cpu_usage,
                        "memory_usage_bytes": memory_usage,
                        "os_image": node.status.node_info.os_image,
                        "kernel_version": node.status.node_info.kernel_version,
                        "kubelet_version": node.status.node_info.kubelet_version
                    }
                }
                
                self._send_resource_data(resource_data)
            
            logger.info(f"  ✓ Coletados {len(nodes.items)} node(s)")
        
        except Exception as e:
            logger.error(f"  ✗ Erro ao coletar nodes: {e}")
    
    def _collect_pods(self, cluster_id: int, v1, metrics_api, cluster: Dict):
        """Coletar métricas de pods"""
        try:
            # Determinar namespaces
            if cluster.get("monitor_all_namespaces"):
                pods = v1.list_pod_for_all_namespaces()
            else:
                namespaces = cluster.get("namespaces", [])
                all_pods = []
                for ns in namespaces:
                    ns_pods = v1.list_namespaced_pod(ns)
                    all_pods.extend(ns_pods.items)
                
                class PodList:
                    def __init__(self, items):
                        self.items = items
                pods = PodList(all_pods)
            
            # Obter métricas de pods
            try:
                pod_metrics = metrics_api.list_cluster_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    plural="pods"
                )
                metrics_by_pod = {}
                for m in pod_metrics["items"]:
                    key = f"{m['metadata']['namespace']}/{m['metadata']['name']}"
                    metrics_by_pod[key] = m
            except:
                metrics_by_pod = {}
            
            for pod in pods.items:
                pod_name = pod.metadata.name
                namespace = pod.metadata.namespace
                
                # Status
                phase = pod.status.phase
                ready = False
                if pod.status.conditions:
                    for condition in pod.status.conditions:
                        if condition.type == "Ready":
                            ready = condition.status == "True"
                            break
                
                # Restarts
                restart_count = 0
                if pod.status.container_statuses:
                    restart_count = sum(c.restart_count for c in pod.status.container_statuses)
                
                # Uso de CPU e memória
                cpu_usage = 0.0
                memory_usage = 0.0
                pod_key = f"{namespace}/{pod_name}"
                if pod_key in metrics_by_pod:
                    for container in metrics_by_pod[pod_key].get("containers", []):
                        usage = container.get("usage", {})
                        cpu_usage += self._parse_cpu(usage.get("cpu", "0"))
                        memory_usage += self._parse_memory(usage.get("memory", "0"))
                
                # Enviar dados
                resource_data = {
                    "cluster_id": cluster_id,
                    "resource_type": "pod",
                    "resource_name": pod_name,
                    "namespace": namespace,
                    "uid": pod.metadata.uid,
                    "status": phase,
                    "phase": phase,
                    "ready": ready,
                    "pod_cpu_usage": cpu_usage,
                    "pod_memory_usage": memory_usage,
                    "pod_restart_count": restart_count,
                    "pod_node_name": pod.spec.node_name,
                    "labels": pod.metadata.labels,
                    "metrics": {
                        "cpu_millicores": cpu_usage * 1000,
                        "memory_bytes": memory_usage,
                        "restart_count": restart_count,
                        "start_time": pod.status.start_time.isoformat() if pod.status.start_time else None
                    }
                }
                
                self._send_resource_data(resource_data)
            
            logger.info(f"  ✓ Coletados {len(pods.items)} pod(s)")
        
        except Exception as e:
            logger.error(f"  ✗ Erro ao coletar pods: {e}")
    
    def _collect_deployments(self, cluster_id: int, apps_v1, cluster: Dict):
        """Coletar métricas de deployments"""
        try:
            if cluster.get("monitor_all_namespaces"):
                deployments = apps_v1.list_deployment_for_all_namespaces()
            else:
                namespaces = cluster.get("namespaces", [])
                all_deployments = []
                for ns in namespaces:
                    ns_deployments = apps_v1.list_namespaced_deployment(ns)
                    all_deployments.extend(ns_deployments.items)
                
                class DeploymentList:
                    def __init__(self, items):
                        self.items = items
                deployments = DeploymentList(all_deployments)
            
            for deployment in deployments.items:
                name = deployment.metadata.name
                namespace = deployment.metadata.namespace
                
                # Réplicas
                desired = deployment.spec.replicas or 0
                ready = deployment.status.ready_replicas or 0
                available = deployment.status.available_replicas or 0
                updated = deployment.status.updated_replicas or 0
                
                # Status
                status = "Healthy" if ready == desired else "Degraded"
                
                resource_data = {
                    "cluster_id": cluster_id,
                    "resource_type": "deployment",
                    "resource_name": name,
                    "namespace": namespace,
                    "uid": deployment.metadata.uid,
                    "status": status,
                    "ready": ready == desired,
                    "desired_replicas": desired,
                    "ready_replicas": ready,
                    "available_replicas": available,
                    "updated_replicas": updated,
                    "labels": deployment.metadata.labels,
                    "metrics": {
                        "health_percent": (ready / desired * 100) if desired > 0 else 0
                    }
                }
                
                self._send_resource_data(resource_data)
            
            logger.info(f"  ✓ Coletados {len(deployments.items)} deployment(s)")
        
        except Exception as e:
            logger.error(f"  ✗ Erro ao coletar deployments: {e}")
    
    def _collect_daemonsets(self, cluster_id: int, apps_v1, cluster: Dict):
        """Coletar métricas de daemonsets"""
        try:
            if cluster.get("monitor_all_namespaces"):
                daemonsets = apps_v1.list_daemon_set_for_all_namespaces()
            else:
                namespaces = cluster.get("namespaces", [])
                all_daemonsets = []
                for ns in namespaces:
                    ns_daemonsets = apps_v1.list_namespaced_daemon_set(ns)
                    all_daemonsets.extend(ns_daemonsets.items)
                
                class DaemonSetList:
                    def __init__(self, items):
                        self.items = items
                daemonsets = DaemonSetList(all_daemonsets)
            
            for daemonset in daemonsets.items:
                name = daemonset.metadata.name
                namespace = daemonset.metadata.namespace
                
                desired = daemonset.status.desired_number_scheduled or 0
                ready = daemonset.status.number_ready or 0
                
                status = "Healthy" if ready == desired else "Degraded"
                
                resource_data = {
                    "cluster_id": cluster_id,
                    "resource_type": "daemonset",
                    "resource_name": name,
                    "namespace": namespace,
                    "uid": daemonset.metadata.uid,
                    "status": status,
                    "ready": ready == desired,
                    "desired_replicas": desired,
                    "ready_replicas": ready,
                    "labels": daemonset.metadata.labels,
                    "metrics": {
                        "coverage_percent": (ready / desired * 100) if desired > 0 else 0
                    }
                }
                
                self._send_resource_data(resource_data)
            
            logger.info(f"  ✓ Coletados {len(daemonsets.items)} daemonset(s)")
        
        except Exception as e:
            logger.error(f"  ✗ Erro ao coletar daemonsets: {e}")
    
    def _collect_statefulsets(self, cluster_id: int, apps_v1, cluster: Dict):
        """Coletar métricas de statefulsets"""
        try:
            if cluster.get("monitor_all_namespaces"):
                statefulsets = apps_v1.list_stateful_set_for_all_namespaces()
            else:
                namespaces = cluster.get("namespaces", [])
                all_statefulsets = []
                for ns in namespaces:
                    ns_statefulsets = apps_v1.list_namespaced_stateful_set(ns)
                    all_statefulsets.extend(ns_statefulsets.items)
                
                class StatefulSetList:
                    def __init__(self, items):
                        self.items = items
                statefulsets = StatefulSetList(all_statefulsets)
            
            for statefulset in statefulsets.items:
                name = statefulset.metadata.name
                namespace = statefulset.metadata.namespace
                
                desired = statefulset.spec.replicas or 0
                ready = statefulset.status.ready_replicas or 0
                
                status = "Healthy" if ready == desired else "Degraded"
                
                resource_data = {
                    "cluster_id": cluster_id,
                    "resource_type": "statefulset",
                    "resource_name": name,
                    "namespace": namespace,
                    "uid": statefulset.metadata.uid,
                    "status": status,
                    "ready": ready == desired,
                    "desired_replicas": desired,
                    "ready_replicas": ready,
                    "labels": statefulset.metadata.labels,
                    "metrics": {
                        "health_percent": (ready / desired * 100) if desired > 0 else 0
                    }
                }
                
                self._send_resource_data(resource_data)
            
            logger.info(f"  ✓ Coletados {len(statefulsets.items)} statefulset(s)")
        
        except Exception as e:
            logger.error(f"  ✗ Erro ao coletar statefulsets: {e}")
    
    def _collect_services(self, cluster_id: int, v1, cluster: Dict):
        """Coletar métricas de services"""
        try:
            if cluster.get("monitor_all_namespaces"):
                services = v1.list_service_for_all_namespaces()
            else:
                namespaces = cluster.get("namespaces", [])
                all_services = []
                for ns in namespaces:
                    ns_services = v1.list_namespaced_service(ns)
                    all_services.extend(ns_services.items)
                
                class ServiceList:
                    def __init__(self, items):
                        self.items = items
                services = ServiceList(all_services)
            
            for service in services.items:
                name = service.metadata.name
                namespace = service.metadata.namespace
                
                # Obter endpoints
                try:
                    endpoints = v1.read_namespaced_endpoints(name, namespace)
                    endpoint_count = 0
                    if endpoints.subsets:
                        for subset in endpoints.subsets:
                            if subset.addresses:
                                endpoint_count += len(subset.addresses)
                except:
                    endpoint_count = 0
                
                status = "Healthy" if endpoint_count > 0 else "NoEndpoints"
                
                resource_data = {
                    "cluster_id": cluster_id,
                    "resource_type": "service",
                    "resource_name": name,
                    "namespace": namespace,
                    "uid": service.metadata.uid,
                    "status": status,
                    "ready": endpoint_count > 0,
                    "labels": service.metadata.labels,
                    "metrics": {
                        "endpoint_count": endpoint_count,
                        "service_type": service.spec.type,
                        "cluster_ip": service.spec.cluster_ip
                    }
                }
                
                self._send_resource_data(resource_data)
            
            logger.info(f"  ✓ Coletados {len(services.items)} service(s)")
        
        except Exception as e:
            logger.error(f"  ✗ Erro ao coletar services: {e}")
    
    def _send_resource_data(self, resource_data: Dict):
        """Enviar dados de recurso para API"""
        try:
            # Adicionar ao buffer local para envio em lote
            if not hasattr(self, 'resource_buffer'):
                self.resource_buffer = []
            
            self.resource_buffer.append(resource_data)
            
            # Enviar em lote quando atingir 50 recursos
            if len(self.resource_buffer) >= 50:
                self._flush_resource_buffer()
                
        except Exception as e:
            logger.error(f"Erro ao enviar dados de recurso: {e}")
    
    def _flush_resource_buffer(self):
        """Enviar buffer de recursos para API"""
        if not hasattr(self, 'resource_buffer') or not self.resource_buffer:
            return
        
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/kubernetes/resources/bulk",
                params={"probe_token": self.probe_token},
                json=self.resource_buffer,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"  ✓ Enviados {result.get('total', 0)} recursos ({result.get('created', 0)} novos, {result.get('updated', 0)} atualizados)")
                self.resource_buffer = []
            else:
                logger.error(f"  ✗ Erro ao enviar recursos: {response.status_code} - {response.text}")
        
        except Exception as e:
            logger.error(f"  ✗ Erro ao enviar buffer de recursos: {e}")
    
    def _update_last_collected(self, cluster_id: int):
        """Atualizar timestamp de última coleta"""
        try:
            requests.patch(
                f"{self.api_url}/api/v1/kubernetes/clusters/{cluster_id}",
                headers=self.headers,
                json={"last_collected_at": datetime.utcnow().isoformat()},
                timeout=5
            )
        except Exception as e:
            logger.error(f"Erro ao atualizar timestamp: {e}")
    
    @staticmethod
    def _parse_cpu(cpu_str: str) -> float:
        """Converter string de CPU para float (cores)"""
        if not cpu_str:
            return 0.0
        
        cpu_str = str(cpu_str)
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000
        elif cpu_str.endswith('n'):
            return float(cpu_str[:-1]) / 1000000000
        else:
            return float(cpu_str)
    
    @staticmethod
    def _parse_memory(memory_str: str) -> float:
        """Converter string de memória para float (bytes)"""
        if not memory_str:
            return 0.0
        
        memory_str = str(memory_str)
        units = {
            'Ki': 1024,
            'Mi': 1024 ** 2,
            'Gi': 1024 ** 3,
            'Ti': 1024 ** 4,
            'K': 1000,
            'M': 1000 ** 2,
            'G': 1000 ** 3,
            'T': 1000 ** 4
        }
        
        for unit, multiplier in units.items():
            if memory_str.endswith(unit):
                return float(memory_str[:-len(unit)]) * multiplier
        
        return float(memory_str)


if __name__ == "__main__":
    # Teste local
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python kubernetes_collector.py <API_URL> <PROBE_TOKEN>")
        sys.exit(1)
    
    api_url = sys.argv[1]
    probe_token = sys.argv[2]
    
    collector = KubernetesCollector(api_url, probe_token)
    collector.collect_all_clusters()
