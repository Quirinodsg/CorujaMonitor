"""
API Router para Alertas Kubernetes
Data: 27 FEV 2026
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from database import get_db
from models import KubernetesAlert, KubernetesAlertRule, KubernetesCluster, KubernetesResource
from auth import get_current_user

router = APIRouter(prefix="/api/v1/kubernetes/alerts", tags=["kubernetes-alerts"])
logger = logging.getLogger(__name__)


# Schemas
class AlertRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    alert_type: str
    severity: str  # critical, warning, info
    resource_type: Optional[str] = None
    metric_name: str
    operator: str  # gt, lt, eq, gte, lte
    threshold: float
    duration: int = 60
    namespace_filter: Optional[str] = None
    cluster_id: Optional[int] = None
    notify_email: bool = True
    notify_webhook: bool = False
    webhook_url: Optional[str] = None


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    threshold: Optional[float] = None
    duration: Optional[int] = None
    is_active: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_webhook: Optional[bool] = None
    webhook_url: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    cluster_id: int
    alert_type: str
    severity: str
    title: str
    message: str
    resource_type: Optional[str]
    resource_name: Optional[str]
    namespace: Optional[str]
    current_value: Optional[float]
    threshold_value: Optional[float]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Endpoints

@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    cluster_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: str = "active",
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar alertas"""
    
    query = db.query(KubernetesAlert).join(KubernetesCluster).filter(
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    )
    
    if cluster_id:
        query = query.filter(KubernetesAlert.cluster_id == cluster_id)
    
    if severity:
        query = query.filter(KubernetesAlert.severity == severity)
    
    if status:
        query = query.filter(KubernetesAlert.status == status)
    
    alerts = query.order_by(KubernetesAlert.created_at.desc()).limit(limit).all()
    
    return alerts


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reconhecer um alerta"""
    
    alert = db.query(KubernetesAlert).join(KubernetesCluster).filter(
        KubernetesAlert.id == alert_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta não encontrado"
        )
    
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = current_user["user_id"]
    
    db.commit()
    
    return {"message": "Alerta reconhecido"}


@router.post("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Resolver um alerta"""
    
    alert = db.query(KubernetesAlert).join(KubernetesCluster).filter(
        KubernetesAlert.id == alert_id,
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta não encontrado"
        )
    
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Alerta resolvido"}


@router.get("/rules")
def list_alert_rules(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar regras de alerta"""
    
    rules = db.query(KubernetesAlertRule).filter(
        KubernetesAlertRule.tenant_id == current_user["tenant_id"]
    ).all()
    
    return rules


@router.post("/rules")
def create_alert_rule(
    rule: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Criar regra de alerta"""
    
    db_rule = KubernetesAlertRule(
        tenant_id=current_user["tenant_id"],
        cluster_id=rule.cluster_id,
        name=rule.name,
        description=rule.description,
        alert_type=rule.alert_type,
        severity=rule.severity,
        resource_type=rule.resource_type,
        metric_name=rule.metric_name,
        operator=rule.operator,
        threshold=rule.threshold,
        duration=rule.duration,
        namespace_filter=rule.namespace_filter,
        notify_email=rule.notify_email,
        notify_webhook=rule.notify_webhook,
        webhook_url=rule.webhook_url
    )
    
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    logger.info(f"Regra de alerta criada: {rule.name}")
    
    return db_rule


@router.put("/rules/{rule_id}")
def update_alert_rule(
    rule_id: int,
    rule_update: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Atualizar regra de alerta"""
    
    rule = db.query(KubernetesAlertRule).filter(
        KubernetesAlertRule.id == rule_id,
        KubernetesAlertRule.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )
    
    update_data = rule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    
    return rule


@router.delete("/rules/{rule_id}")
def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deletar regra de alerta"""
    
    rule = db.query(KubernetesAlertRule).filter(
        KubernetesAlertRule.id == rule_id,
        KubernetesAlertRule.tenant_id == current_user["tenant_id"]
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )
    
    db.delete(rule)
    db.commit()
    
    return {"message": "Regra deletada"}


@router.get("/stats")
def get_alert_stats(
    cluster_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obter estatísticas de alertas"""
    
    query = db.query(KubernetesAlert).join(KubernetesCluster).filter(
        KubernetesCluster.tenant_id == current_user["tenant_id"]
    )
    
    if cluster_id:
        query = query.filter(KubernetesAlert.cluster_id == cluster_id)
    
    # Contar por status
    active = query.filter(KubernetesAlert.status == "active").count()
    acknowledged = query.filter(KubernetesAlert.status == "acknowledged").count()
    resolved = query.filter(KubernetesAlert.status == "resolved").count()
    
    # Contar por severidade (apenas ativos)
    critical = query.filter(
        KubernetesAlert.status == "active",
        KubernetesAlert.severity == "critical"
    ).count()
    
    warning = query.filter(
        KubernetesAlert.status == "active",
        KubernetesAlert.severity == "warning"
    ).count()
    
    info = query.filter(
        KubernetesAlert.status == "active",
        KubernetesAlert.severity == "info"
    ).count()
    
    return {
        "by_status": {
            "active": active,
            "acknowledged": acknowledged,
            "resolved": resolved
        },
        "by_severity": {
            "critical": critical,
            "warning": warning,
            "info": info
        },
        "total_active": active
    }


# Função para avaliar alertas (chamada pelo collector)
def evaluate_alerts(db: Session):
    """Avaliar regras de alerta e criar alertas quando necessário"""
    
    try:
        # Buscar regras ativas
        rules = db.query(KubernetesAlertRule).filter(
            KubernetesAlertRule.is_active == True
        ).all()
        
        for rule in rules:
            # Buscar recursos que correspondem à regra
            query = db.query(KubernetesResource)
            
            if rule.cluster_id:
                query = query.filter(KubernetesResource.cluster_id == rule.cluster_id)
            
            if rule.resource_type:
                query = query.filter(KubernetesResource.resource_type == rule.resource_type)
            
            if rule.namespace_filter:
                query = query.filter(KubernetesResource.namespace == rule.namespace_filter)
            
            resources = query.all()
            
            for resource in resources:
                # Obter valor da métrica
                metric_value = getattr(resource, rule.metric_name, None)
                
                if metric_value is None:
                    continue
                
                # Avaliar condição
                condition_met = False
                
                if rule.operator == "gt":
                    condition_met = metric_value > rule.threshold
                elif rule.operator == "lt":
                    condition_met = metric_value < rule.threshold
                elif rule.operator == "eq":
                    condition_met = metric_value == rule.threshold
                elif rule.operator == "gte":
                    condition_met = metric_value >= rule.threshold
                elif rule.operator == "lte":
                    condition_met = metric_value <= rule.threshold
                
                if condition_met:
                    # Verificar se já existe alerta ativo para este recurso
                    existing_alert = db.query(KubernetesAlert).filter(
                        KubernetesAlert.cluster_id == resource.cluster_id,
                        KubernetesAlert.resource_id == resource.id,
                        KubernetesAlert.alert_type == rule.alert_type,
                        KubernetesAlert.status == "active"
                    ).first()
                    
                    if not existing_alert:
                        # Criar novo alerta
                        alert = KubernetesAlert(
                            cluster_id=resource.cluster_id,
                            resource_id=resource.id,
                            alert_type=rule.alert_type,
                            severity=rule.severity,
                            title=f"{rule.name}: {resource.resource_name}",
                            message=f"{rule.description or rule.name}. Valor atual: {metric_value}, Threshold: {rule.threshold}",
                            resource_type=resource.resource_type,
                            resource_name=resource.resource_name,
                            namespace=resource.namespace,
                            current_value=float(metric_value) if metric_value is not None else None,
                            threshold_value=rule.threshold,
                            status="active"
                        )
                        
                        db.add(alert)
                        logger.info(f"Alerta criado: {alert.title}")
                else:
                    # Condição não atendida, resolver alertas ativos
                    active_alerts = db.query(KubernetesAlert).filter(
                        KubernetesAlert.cluster_id == resource.cluster_id,
                        KubernetesAlert.resource_id == resource.id,
                        KubernetesAlert.alert_type == rule.alert_type,
                        KubernetesAlert.status == "active"
                    ).all()
                    
                    for alert in active_alerts:
                        alert.status = "resolved"
                        alert.resolved_at = datetime.utcnow()
                        logger.info(f"Alerta resolvido automaticamente: {alert.title}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Erro ao avaliar alertas: {e}")
        db.rollback()
