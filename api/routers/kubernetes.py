"""
API Router para Monitoramento Kubernetes
Data: 27 FEV 2026
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import logging

from database import get_db
from models import KubernetesCluster, KubernetesResource, KubernetesMetric, Tenant
from auth import get_current_user
from utils.encryption import encrypt_kubernetes_credentials, decrypt_kubernetes_credentials

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/kubernetes", tags=["kubernetes"])


# Schemas
class KubernetesClusterCreate(BaseModel):
    cluster_name: str
    cluster_type: str  # vanilla, aks, eks, gke, openshift
    api_endpoint: str
    auth_method: str  # kubeconfig, service_account, token
    kubeconfig_content: Optional[str] = None
    service_account_token: Optional[str] = None
    ca_cert: Optional[str] = None
    monitor_all_namespaces: bool = True
    namespaces: Optional[List[str]] = []
    selected_resources: List[str] = []
    probe_id: Optional[int] = None
    collection_interval: int = 60


class KubernetesClusterUpdate(BaseModel):
    cluster_name: Optional[str] = None
    is_active: Optional[bool] = None
    monitor_all_namespaces: Optional[bool] = None
    namespaces: Optional[List[str]] = None
    selected_resources: Optional[List[str]] = None
    collection_interval: Optional[int] = None


class KubernetesClusterResponse(BaseModel):
    id: int
    tenant_id: int
    probe_id: Optional[int]
    cluster_name: str
    cluster_type: str
    api_endpoint: str
    auth_method: str
    monitor_all_namespaces: bool
    namespaces: Optional[List[str]]
    selected_resources: List[str]
    collection_interval: int
    is_active: bool
    connection_status: Optional[str]
    connection_error: Optional[str]
    total_nodes: int
    total_pods: int
    total_deployments: int
    cluster_cpu_usage: float
    cluster_memory_usage: float
    created_at: datetime
    last_collected_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[dict] = None


# Endpoints

@router.post("/clusters", response_model=KubernetesClusterResponse)
def create_cluster(
    cluster: KubernetesClusterCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Criar configuração de cluster Kubernetes"""
    
    # Verificar se já existe cluster com mesmo nome
    existing = db.query(KubernetesCluster).filter(
        KubernetesCluster.tenant_id == current_user["tenant_id"],
        KubernetesCluster.cluster_name == cluster.cluster_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cluster '{cluster.cluster_name}' já existe"
        )
    
    # Criptografar credenciais
    cluster_dict = cluster.dict()
    encrypted_data = encrypt_kubernetes_credentials(cluster_dict)
    
    # Criar cluster
    db_cluster = KubernetesCluster(
        tenant_id=current_user["tenant_id"],
        probe_id=encrypted_data.get('probe_id'),
        cluster_name=encrypted_data['cluster_name'],
        cluster_type=encrypted_data['cluster_type'],
        api_endpoint=encrypted_data['api_endpoint'],
        auth_method=encrypted_data['auth_method'],
        kubeconfig_content=encrypted_data.get('kubeconfig_content'),
        service_account_token=encrypted_data.get('service_account_token'),
        ca_cert=encrypted_data.get('ca_cert'),
        monitor_all_namespaces=encrypted_data['monitor_all_namespaces'],
        namespaces=encrypted_data.get('namespaces', []),
        selected_resources=encrypted_data['selected_resources'],
        collection_interval=encrypted_data['collection_interval'],
        connection_status="untested"
    )
    
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    
    logger.info(f"Cluster Kubernetes criado: {cluster.cluster_name} (credenciais criptografadas)")
    
    return db_cluster


@router.get("/clusters", response_model=List[KubernetesClusterResponse])
def list_clusters(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar todos os clusters Kubernetes"""
    
    clusters = db.query(KubernetesCluster).filter(
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).all()
    
    return clusters


@router.get("/clusters/for-collector")
def list_clusters_for_collector(
    probe_token: str,
    db: Session = Depends(get_db)
):
    """Listar clusters com credenciais descriptografadas (apenas para collector)"""
    
    # Verificar probe token
    from models import Probe
    probe = db.query(Probe).filter(Probe.probe_token == probe_token).first()
    
    if not probe:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de probe inválido"
        )
    
    # Buscar clusters ativos
    clusters = db.query(KubernetesCluster).filter(
        KubernetesCluster.is_active == True
    ).all()
    
    # Descriptografar credenciais
    result = []
    for cluster in clusters:
        cluster_dict = {
            "id": cluster.id,
            "cluster_name": cluster.cluster_name,
            "cluster_type": cluster.cluster_type,
            "api_endpoint": cluster.api_endpoint,
            "auth_method": cluster.auth_method,
            "kubeconfig_content": cluster.kubeconfig_content,
            "service_account_token": cluster.service_account_token,
            "ca_cert": cluster.ca_cert,
            "monitor_all_namespaces": cluster.monitor_all_namespaces,
            "namespaces": cluster.namespaces,
            "selected_resources": cluster.selected_resources,
            "collection_interval": cluster.collection_interval
        }
        
        # Descriptografar
        decrypted = decrypt_kubernetes_credentials(cluster_dict)
        result.append(decrypted)
    
    return result


@router.get("/clusters/{cluster_id}", response_model=KubernetesClusterResponse)
def get_cluster(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter detalhes de um cluster"""
    
    cluster = db.query(KubernetesCluster).filter(
        KubernetesCluster.id == cluster_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster não encontrado"
        )
    
    return cluster


@router.put("/clusters/{cluster_id}", response_model=KubernetesClusterResponse)
def update_cluster(
    cluster_id: int,
    cluster_update: KubernetesClusterUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualizar configuração de cluster"""
    
    cluster = db.query(KubernetesCluster).filter(
        KubernetesCluster.id == cluster_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster não encontrado"
        )
    
    # Atualizar campos
    update_data = cluster_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cluster, field, value)
    
    db.commit()
    db.refresh(cluster)
    
    return cluster


@router.delete("/clusters/{cluster_id}")
def delete_cluster(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deletar cluster e todos os seus recursos"""
    
    cluster = db.query(KubernetesCluster).filter(
        KubernetesCluster.id == cluster_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster não encontrado"
        )
    
    # Deletar recursos associados
    db.query(KubernetesResource).filter(
        KubernetesResource.cluster_id == cluster_id
    ).delete()
    
    # Deletar cluster
    db.delete(cluster)
    db.commit()
    
    return {"message": "Cluster deletado com sucesso"}


@router.post("/clusters/{cluster_id}/test", response_model=ConnectionTestResponse)
async def test_connection(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Testar conexão com cluster Kubernetes"""
    
    cluster = db.query(KubernetesCluster).filter(
        KubernetesCluster.id == cluster_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster não encontrado"
        )
    
    try:
        # Importar biblioteca Kubernetes
        from kubernetes import client, config
        from kubernetes.client.rest import ApiException
        import tempfile
        import os
        
        # Configurar autenticação baseado no método
        if cluster.auth_method == "kubeconfig":
            # Salvar kubeconfig em arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
                f.write(cluster.kubeconfig_content)
                kubeconfig_path = f.name
            
            try:
                config.load_kube_config(config_file=kubeconfig_path)
            finally:
                os.unlink(kubeconfig_path)
        
        elif cluster.auth_method in ["service_account", "token"]:
            # Configurar com token
            configuration = client.Configuration()
            configuration.host = cluster.api_endpoint
            configuration.api_key = {"authorization": f"Bearer {cluster.service_account_token}"}
            
            if cluster.ca_cert:
                # Salvar CA cert em arquivo temporário
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.crt') as f:
                    f.write(cluster.ca_cert)
                    configuration.ssl_ca_cert = f.name
            else:
                configuration.verify_ssl = False
            
            client.Configuration.set_default(configuration)
        
        # Testar conexão
        v1 = client.CoreV1Api()
        
        # Listar nodes
        nodes = v1.list_node()
        node_count = len(nodes.items)
        
        # Listar namespaces
        namespaces = v1.list_namespace()
        namespace_list = [ns.metadata.name for ns in namespaces.items]
        
        # Verificar Metrics Server
        try:
            metrics_api = client.CustomObjectsApi()
            metrics_api.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes",
                limit=1
            )
            metrics_server_available = True
        except:
            metrics_server_available = False
        
        # Atualizar status do cluster
        cluster.connection_status = "connected"
        cluster.connection_error = None
        cluster.last_connection_test = datetime.utcnow()
        cluster.total_nodes = node_count
        db.commit()
        
        return ConnectionTestResponse(
            success=True,
            message=f"Conexão estabelecida com sucesso! {node_count} node(s) encontrado(s).",
            details={
                "nodes": node_count,
                "namespaces": namespace_list,
                "metrics_server_available": metrics_server_available,
                "cluster_version": nodes.items[0].status.node_info.kube_proxy_version if nodes.items else "unknown"
            }
        )
    
    except ApiException as e:
        error_msg = f"Erro API Kubernetes: {e.status} - {e.reason}"
        cluster.connection_status = "error"
        cluster.connection_error = error_msg
        cluster.last_connection_test = datetime.utcnow()
        db.commit()
        
        return ConnectionTestResponse(
            success=False,
            message=error_msg,
            details={"status_code": e.status, "reason": e.reason}
        )
    
    except Exception as e:
        error_msg = f"Erro ao conectar: {str(e)}"
        cluster.connection_status = "error"
        cluster.connection_error = error_msg
        cluster.last_connection_test = datetime.utcnow()
        db.commit()
        
        return ConnectionTestResponse(
            success=False,
            message=error_msg
        )


@router.post("/clusters/{cluster_id}/discover")
async def discover_resources(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Iniciar auto-discovery de recursos do cluster"""
    
    cluster = db.query(KubernetesCluster).filter(
        KubernetesCluster.id == cluster_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster não encontrado"
        )
    
    # TODO: Implementar discovery assíncrono via Celery/Background task
    # Por enquanto, retornar mensagem de sucesso
    
    return {
        "message": "Auto-discovery iniciado",
        "cluster_id": cluster_id,
        "cluster_name": cluster.cluster_name,
        "status": "in_progress"
    }


@router.get("/clusters/{cluster_id}/resources")
def list_resources(
    cluster_id: int,
    resource_type: Optional[str] = None,
    namespace: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar recursos descobertos do cluster"""
    
    # Verificar se cluster pertence ao tenant
    cluster = db.query(KubernetesCluster).filter(
        KubernetesCluster.id == cluster_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster não encontrado"
        )
    
    # Query base
    query = db.query(KubernetesResource).filter(
        KubernetesResource.cluster_id == cluster_id
    )
    
    # Filtros opcionais
    if resource_type:
        query = query.filter(KubernetesResource.resource_type == resource_type)
    
    if namespace:
        query = query.filter(KubernetesResource.namespace == namespace)
    
    resources = query.all()
    
    return resources


@router.get("/clusters/{cluster_id}/metrics")
def get_cluster_metrics(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter métricas agregadas do cluster"""
    
    cluster = db.query(KubernetesCluster).filter(
        KubernetesCluster.id == cluster_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster não encontrado"
        )
    
    # Contar recursos por tipo
    resources_by_type = {}
    for resource_type in cluster.selected_resources:
        count = db.query(KubernetesResource).filter(
            KubernetesResource.cluster_id == cluster_id,
            KubernetesResource.resource_type == resource_type
        ).count()
        resources_by_type[resource_type] = count
    
    return {
        "cluster_id": cluster_id,
        "cluster_name": cluster.cluster_name,
        "total_nodes": cluster.total_nodes,
        "total_pods": cluster.total_pods,
        "total_deployments": cluster.total_deployments,
        "cluster_cpu_usage": cluster.cluster_cpu_usage,
        "cluster_memory_usage": cluster.cluster_memory_usage,
        "resources_by_type": resources_by_type,
        "last_collected_at": cluster.last_collected_at
    }


# Endpoint para receber dados do collector (autenticação via probe token)
@router.post("/resources/bulk")
async def receive_resources_bulk(
    resources: List[dict],
    probe_token: str,
    db: Session = Depends(get_db)
):
    """Receber dados de recursos do collector (autenticação via probe token)"""
    
    # Verificar probe token
    from models import Probe
    probe = db.query(Probe).filter(Probe.probe_token == probe_token).first()
    
    if not probe:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de probe inválido"
        )
    
    created_count = 0
    updated_count = 0
    
    try:
        for resource_data in resources:
            cluster_id = resource_data.get("cluster_id")
            resource_type = resource_data.get("resource_type")
            resource_name = resource_data.get("resource_name")
            namespace = resource_data.get("namespace")
            uid = resource_data.get("uid")
            
            # Buscar recurso existente por UID
            existing = db.query(KubernetesResource).filter(
                KubernetesResource.cluster_id == cluster_id,
                KubernetesResource.uid == uid
            ).first()
            
            if existing:
                # Atualizar recurso existente
                for key, value in resource_data.items():
                    if key not in ["cluster_id", "uid"] and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.last_seen = datetime.utcnow()
                updated_count += 1
            else:
                # Criar novo recurso
                new_resource = KubernetesResource(
                    cluster_id=cluster_id,
                    resource_type=resource_type,
                    resource_name=resource_name,
                    namespace=namespace,
                    uid=uid,
                    status=resource_data.get("status"),
                    phase=resource_data.get("phase"),
                    ready=resource_data.get("ready", False),
                    labels=resource_data.get("labels", {}),
                    annotations=resource_data.get("annotations", {}),
                    metrics=resource_data.get("metrics", {}),
                    # Node fields
                    node_cpu_capacity=resource_data.get("node_cpu_capacity"),
                    node_memory_capacity=resource_data.get("node_memory_capacity"),
                    node_cpu_usage=resource_data.get("node_cpu_usage"),
                    node_memory_usage=resource_data.get("node_memory_usage"),
                    node_pod_count=resource_data.get("node_pod_count"),
                    node_pod_capacity=resource_data.get("node_pod_capacity"),
                    # Pod fields
                    pod_cpu_usage=resource_data.get("pod_cpu_usage"),
                    pod_memory_usage=resource_data.get("pod_memory_usage"),
                    pod_restart_count=resource_data.get("pod_restart_count"),
                    pod_node_name=resource_data.get("pod_node_name"),
                    # Deployment/StatefulSet/DaemonSet fields
                    desired_replicas=resource_data.get("desired_replicas"),
                    ready_replicas=resource_data.get("ready_replicas"),
                    available_replicas=resource_data.get("available_replicas"),
                    updated_replicas=resource_data.get("updated_replicas"),
                    last_seen=datetime.utcnow()
                )
                db.add(new_resource)
                created_count += 1
                
                # Criar métrica histórica
                metric = KubernetesMetric(
                    resource_id=None,  # Será atualizado após commit
                    cpu_usage=resource_data.get("node_cpu_usage") or resource_data.get("pod_cpu_usage"),
                    memory_usage=resource_data.get("node_memory_usage") or resource_data.get("pod_memory_usage"),
                    status=resource_data.get("status"),
                    ready=resource_data.get("ready", False),
                    restart_count=resource_data.get("pod_restart_count"),
                    timestamp=datetime.utcnow()
                )
                # Associar métrica ao recurso após commit
                new_resource.metrics_history = [metric]
        
        # Commit em lote
        db.commit()
        
        logger.info(f"Kubernetes resources received: {created_count} created, {updated_count} updated")
        
        return {
            "success": True,
            "created": created_count,
            "updated": updated_count,
            "total": len(resources)
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error receiving Kubernetes resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar recursos: {str(e)}"
        )
