"""
Kubernetes Engine - Coleta pods/nodes/deployments via kubernetes client
Retorna status=unknown com error="engine_unavailable" se kubernetes não instalado.
"""
import logging
from typing import Optional

from .base_engine import BaseProtocolEngine, EngineResult

logger = logging.getLogger(__name__)

try:
    from kubernetes import client as k8s_client, config as k8s_config
    from kubernetes.client.rest import ApiException
    _K8S_AVAILABLE = True
except ImportError:
    _K8S_AVAILABLE = False


class KubernetesEngine(BaseProtocolEngine):
    """
    Engine para coleta de métricas de clusters Kubernetes.

    kwargs esperados em execute():
        namespace (str): namespace a monitorar (None = todos)
        kubeconfig (str): caminho para kubeconfig (None = in-cluster ou ~/.kube/config)
        resource (str): "pods" | "nodes" | "deployments" | "all" (padrão: "all")
    """

    def is_available(self) -> bool:
        return _K8S_AVAILABLE

    def execute(self, host: str, **kwargs) -> EngineResult:
        if not _K8S_AVAILABLE:
            return self._unavailable_result()

        namespace: Optional[str] = kwargs.get("namespace")
        kubeconfig: Optional[str] = kwargs.get("kubeconfig")
        resource: str = kwargs.get("resource", "all")

        try:
            self._load_config(kubeconfig)

            v1 = k8s_client.CoreV1Api()
            apps_v1 = k8s_client.AppsV1Api()

            metadata: dict = {"host": host, "namespace": namespace or "all"}

            if resource in ("pods", "all"):
                metadata["pods"] = self._collect_pods(v1, namespace)

            if resource in ("nodes", "all"):
                metadata["nodes"] = self._collect_nodes(v1)

            if resource in ("deployments", "all"):
                metadata["deployments"] = self._collect_deployments(apps_v1, namespace)

            # Status geral: ok se há nodes prontos
            nodes = metadata.get("nodes", [])
            ready_nodes = sum(1 for n in nodes if n.get("ready"))
            total_nodes = len(nodes)

            if total_nodes == 0:
                status = "unknown"
            elif ready_nodes == total_nodes:
                status = "ok"
            elif ready_nodes > 0:
                status = "warning"
            else:
                status = "critical"

            return EngineResult(
                status=status,
                value=float(ready_nodes),
                unit="nodes_ready",
                metadata=metadata,
            )

        except ApiException as e:
            logger.warning(f"KubernetesEngine API error for {host}: {e}")
            return EngineResult(
                status="unknown",
                error=f"k8s_api_error:{e.status}",
                metadata={"host": host},
            )
        except Exception as e:
            logger.error(f"KubernetesEngine error for {host}: {e}")
            return EngineResult(
                status="unknown",
                error=str(e),
                metadata={"host": host},
            )

    def _load_config(self, kubeconfig: Optional[str]):
        """Carrega configuração do cluster"""
        try:
            if kubeconfig:
                k8s_config.load_kube_config(config_file=kubeconfig)
            else:
                try:
                    k8s_config.load_incluster_config()
                except k8s_config.ConfigException:
                    k8s_config.load_kube_config()
        except Exception as e:
            raise RuntimeError(f"Failed to load k8s config: {e}")

    def _collect_pods(self, v1, namespace: Optional[str]) -> list:
        if namespace:
            pods = v1.list_namespaced_pod(namespace)
        else:
            pods = v1.list_pod_for_all_namespaces()

        result = []
        for pod in pods.items:
            phase = pod.status.phase or "Unknown"
            result.append({
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "phase": phase,
                "ready": phase == "Running",
                "node": pod.spec.node_name,
            })
        return result

    def _collect_nodes(self, v1) -> list:
        nodes = v1.list_node()
        result = []
        for node in nodes.items:
            ready = False
            for condition in (node.status.conditions or []):
                if condition.type == "Ready":
                    ready = condition.status == "True"
                    break
            result.append({
                "name": node.metadata.name,
                "ready": ready,
                "roles": self._get_node_roles(node),
                "version": node.status.node_info.kubelet_version if node.status.node_info else "",
            })
        return result

    def _collect_deployments(self, apps_v1, namespace: Optional[str]) -> list:
        if namespace:
            deployments = apps_v1.list_namespaced_deployment(namespace)
        else:
            deployments = apps_v1.list_deployment_for_all_namespaces()

        result = []
        for dep in deployments.items:
            desired = dep.spec.replicas or 0
            ready = dep.status.ready_replicas or 0
            result.append({
                "name": dep.metadata.name,
                "namespace": dep.metadata.namespace,
                "desired": desired,
                "ready": ready,
                "available": dep.status.available_replicas or 0,
                "healthy": ready == desired and desired > 0,
            })
        return result

    def _get_node_roles(self, node) -> list:
        labels = node.metadata.labels or {}
        roles = []
        for label in labels:
            if label.startswith("node-role.kubernetes.io/"):
                roles.append(label.split("/", 1)[1])
        return roles or ["worker"]
