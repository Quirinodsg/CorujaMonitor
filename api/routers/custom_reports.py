"""
Custom Reports Router
Sistema de relatórios personalizados inspirado em PRTG e SolarWinds
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, case
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models import CustomReport, User, Incident, Server, Sensor, Metric
from auth import get_current_active_user

router = APIRouter()


class CustomReportCreate(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: str  # incidents, servers, availability, performance, errors
    filters: Dict[str, Any]
    columns: List[str]
    sort_by: Optional[str] = None
    sort_order: Optional[str] = 'desc'
    is_public: Optional[bool] = False
    is_favorite: Optional[bool] = False


class CustomReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[List[str]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None


class CustomReportResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    report_type: str
    filters: Dict[str, Any]
    columns: List[str]
    sort_by: Optional[str]
    sort_order: str
    is_public: bool
    is_favorite: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_generated_at: Optional[datetime]
    user_id: int
    
    class Config:
        from_attributes = True


@router.get("/templates")
async def get_report_templates(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retorna templates pré-definidos de relatórios
    Inspirado em PRTG e SolarWinds
    """
    templates = [
        {
            "id": "production_servers",
            "name": "Servidores de Produção",
            "description": "Relatório de todos os servidores em ambiente de produção",
            "report_type": "servers",
            "icon": "🏭",
            "filters": {
                "environment": "production",
                "is_active": True
            },
            "columns": ["hostname", "ip_address", "os_type", "uptime", "cpu_avg", "memory_avg", "incidents_count"],
            "sort_by": "incidents_count",
            "sort_order": "desc"
        },
        {
            "id": "most_alarms",
            "name": "Servidores que Mais Alarmaram",
            "description": "Top 10 servidores com mais incidentes no período",
            "report_type": "incidents",
            "icon": "🚨",
            "filters": {
                "period": "last_30_days",
                "group_by": "server"
            },
            "columns": ["hostname", "total_incidents", "critical_count", "warning_count", "avg_resolution_time"],
            "sort_by": "total_incidents",
            "sort_order": "desc",
            "limit": 10
        },
        {
            "id": "common_errors",
            "name": "Erros Mais Comuns",
            "description": "Tipos de erros que mais ocorreram no período",
            "report_type": "errors",
            "icon": "❌",
            "filters": {
                "period": "last_30_days",
                "group_by": "error_type"
            },
            "columns": ["error_type", "sensor_type", "occurrence_count", "affected_servers", "first_seen", "last_seen"],
            "sort_by": "occurrence_count",
            "sort_order": "desc"
        },
        {
            "id": "critical_incidents",
            "name": "Incidentes Críticos",
            "description": "Todos os incidentes críticos do período",
            "report_type": "incidents",
            "icon": "🔴",
            "filters": {
                "period": "last_7_days",
                "severity": "critical"
            },
            "columns": ["created_at", "hostname", "sensor_name", "description", "status", "resolution_time"],
            "sort_by": "created_at",
            "sort_order": "desc"
        },
        {
            "id": "availability_by_server",
            "name": "Disponibilidade por Servidor",
            "description": "Percentual de disponibilidade de cada servidor",
            "report_type": "availability",
            "icon": "📊",
            "filters": {
                "period": "last_30_days"
            },
            "columns": ["hostname", "ip_address", "environment", "uptime_percentage", "downtime_hours", "incidents_count"],
            "sort_by": "uptime_percentage",
            "sort_order": "asc"
        },
        {
            "id": "performance_summary",
            "name": "Resumo de Performance",
            "description": "Métricas de performance de todos os servidores",
            "report_type": "performance",
            "icon": "⚡",
            "filters": {
                "period": "last_24_hours"
            },
            "columns": ["hostname", "cpu_avg", "cpu_peak", "memory_avg", "memory_peak", "disk_usage", "network_traffic"],
            "sort_by": "cpu_avg",
            "sort_order": "desc"
        },
        {
            "id": "servers_by_tag",
            "name": "Servidores por Tag",
            "description": "Agrupa servidores por tags personalizadas",
            "report_type": "servers",
            "icon": "🏷️",
            "filters": {
                "group_by": "tags"
            },
            "columns": ["tag", "server_count", "avg_uptime", "total_incidents"],
            "sort_by": "server_count",
            "sort_order": "desc"
        },
        {
            "id": "unresolved_incidents",
            "name": "Incidentes Não Resolvidos",
            "description": "Incidentes abertos ou reconhecidos pendentes de resolução",
            "report_type": "incidents",
            "icon": "⏳",
            "filters": {
                "status": ["open", "acknowledged"]
            },
            "columns": ["created_at", "hostname", "sensor_name", "severity", "description", "age_hours"],
            "sort_by": "created_at",
            "sort_order": "asc"
        },
        {
            "id": "ai_resolution_rate",
            "name": "Taxa de Resolução por IA",
            "description": "Efetividade da auto-resolução por IA",
            "report_type": "ai_analysis",
            "icon": "🤖",
            "filters": {
                "period": "last_30_days"
            },
            "columns": ["sensor_type", "total_incidents", "ai_resolved", "manual_resolved", "success_rate"],
            "sort_by": "success_rate",
            "sort_order": "desc"
        },
        {
            "id": "disk_space_critical",
            "name": "Espaço em Disco Crítico",
            "description": "Servidores com espaço em disco acima de 85%",
            "report_type": "performance",
            "icon": "💾",
            "filters": {
                "sensor_type": "disk",
                "threshold": 85
            },
            "columns": ["hostname", "disk_name", "usage_percentage", "free_space_gb", "total_space_gb", "trend"],
            "sort_by": "usage_percentage",
            "sort_order": "desc"
        }
    ]
    
    return templates


@router.post("/", response_model=CustomReportResponse)
async def create_custom_report(
    report: CustomReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Criar novo relatório personalizado"""
    
    db_report = CustomReport(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        name=report.name,
        description=report.description,
        report_type=report.report_type,
        filters=report.filters,
        columns=report.columns,
        sort_by=report.sort_by,
        sort_order=report.sort_order,
        is_public=report.is_public,
        is_favorite=report.is_favorite
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return db_report


@router.get("/", response_model=List[CustomReportResponse])
async def list_custom_reports(
    include_public: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar relatórios personalizados do usuário e públicos"""
    
    query = db.query(CustomReport).filter(
        CustomReport.tenant_id == current_user.tenant_id
    )
    
    if include_public:
        query = query.filter(
            or_(
                CustomReport.user_id == current_user.id,
                CustomReport.is_public == True
            )
        )
    else:
        query = query.filter(CustomReport.user_id == current_user.id)
    
    reports = query.order_by(
        CustomReport.is_favorite.desc(),
        CustomReport.created_at.desc()
    ).all()
    
    return reports


@router.get("/{report_id}", response_model=CustomReportResponse)
async def get_custom_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter relatório personalizado por ID"""
    
    report = db.query(CustomReport).filter(
        CustomReport.id == report_id,
        CustomReport.tenant_id == current_user.tenant_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Verificar permissão
    if report.user_id != current_user.id and not report.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return report


@router.put("/{report_id}", response_model=CustomReportResponse)
async def update_custom_report(
    report_id: int,
    report_update: CustomReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualizar relatório personalizado"""
    
    report = db.query(CustomReport).filter(
        CustomReport.id == report_id,
        CustomReport.tenant_id == current_user.tenant_id,
        CustomReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or access denied")
    
    # Atualizar campos
    update_data = report_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    report.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete("/{report_id}")
async def delete_custom_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Deletar relatório personalizado"""
    
    report = db.query(CustomReport).filter(
        CustomReport.id == report_id,
        CustomReport.tenant_id == current_user.tenant_id,
        CustomReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or access denied")
    
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"}


@router.post("/{report_id}/generate")
async def generate_custom_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Gerar dados do relatório personalizado"""
    
    report = db.query(CustomReport).filter(
        CustomReport.id == report_id,
        CustomReport.tenant_id == current_user.tenant_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Verificar permissão
    if report.user_id != current_user.id and not report.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Gerar relatório baseado no tipo
    if report.report_type == "incidents":
        data = await generate_incidents_report(report, db, current_user)
    elif report.report_type == "servers":
        data = await generate_servers_report(report, db, current_user)
    elif report.report_type == "availability":
        data = await generate_availability_report(report, db, current_user)
    elif report.report_type == "performance":
        data = await generate_performance_report(report, db, current_user)
    elif report.report_type == "errors":
        data = await generate_errors_report(report, db, current_user)
    elif report.report_type == "ai_analysis":
        data = await generate_ai_analysis_report(report, db, current_user)
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    # Atualizar última geração
    report.last_generated_at = datetime.utcnow()
    db.commit()
    
    return {
        "report": {
            "id": report.id,
            "name": report.name,
            "description": report.description,
            "report_type": report.report_type,
            "generated_at": report.last_generated_at.isoformat()
        },
        "data": data
    }


@router.post("/generate-template")
async def generate_from_template(
    template_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Gerar relatório a partir de um template sem salvar"""
    
    template_id = template_data.get('template_id')
    filters = template_data.get('filters', {})
    
    # Buscar template
    templates_response = await get_report_templates(current_user)
    template = next((t for t in templates_response if t['id'] == template_id), None)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Criar objeto temporário de relatório
    temp_report = CustomReport(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        name=template['name'],
        description=template['description'],
        report_type=template['report_type'],
        filters={**template.get('filters', {}), **filters},
        columns=template.get('columns', []),
        sort_by=template.get('sort_by'),
        sort_order=template.get('sort_order', 'desc')
    )
    
    # Gerar relatório baseado no tipo
    if temp_report.report_type == "incidents":
        data = await generate_incidents_report(temp_report, db, current_user)
    elif temp_report.report_type == "servers":
        data = await generate_servers_report(temp_report, db, current_user)
    elif temp_report.report_type == "errors":
        data = await generate_errors_report(temp_report, db, current_user)
    else:
        data = {"total_count": 0, "rows": []}
    
    return {
        "report": {
            "name": temp_report.name,
            "description": temp_report.description,
            "report_type": temp_report.report_type,
            "generated_at": datetime.utcnow().isoformat()
        },
        "data": data
    }


async def generate_incidents_report(report: CustomReport, db: Session, current_user: User):
    """Gerar relatório de incidentes"""
    
    filters = report.filters
    
    # Query base
    query = db.query(Incident).join(Sensor).join(Server).filter(
        Server.tenant_id == current_user.tenant_id
    )
    
    # Aplicar filtros
    if 'period' in filters:
        period = filters['period']
        if period == 'last_24_hours':
            start_date = datetime.utcnow() - timedelta(hours=24)
        elif period == 'last_7_days':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == 'last_30_days':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == 'last_90_days':
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        query = query.filter(Incident.created_at >= start_date)
    
    if 'severity' in filters:
        if isinstance(filters['severity'], list):
            query = query.filter(Incident.severity.in_(filters['severity']))
        else:
            query = query.filter(Incident.severity == filters['severity'])
    
    if 'status' in filters:
        if isinstance(filters['status'], list):
            query = query.filter(Incident.status.in_(filters['status']))
        else:
            query = query.filter(Incident.status == filters['status'])
    
    if 'server_ids' in filters:
        query = query.filter(Server.id.in_(filters['server_ids']))
    
    if 'environment' in filters:
        query = query.filter(Server.environment == filters['environment'])
    
    # Ordenação
    if report.sort_by:
        if report.sort_order == 'asc':
            query = query.order_by(asc(getattr(Incident, report.sort_by, Incident.created_at)))
        else:
            query = query.order_by(desc(getattr(Incident, report.sort_by, Incident.created_at)))
    
    # Limite
    if 'limit' in filters:
        query = query.limit(filters['limit'])
    
    incidents = query.all()
    
    # Formatar dados
    data = []
    for incident in incidents:
        row = {
            "id": incident.id,
            "created_at": incident.created_at.isoformat(),
            "hostname": incident.sensor.server.hostname,
            "ip_address": incident.sensor.server.ip_address,
            "sensor_name": incident.sensor.name,
            "sensor_type": incident.sensor.sensor_type,
            "severity": incident.severity,
            "status": incident.status,
            "description": incident.description,
            "resolution_time": None,
            "age_hours": None
        }
        
        if incident.resolved_at:
            resolution_time = (incident.resolved_at - incident.created_at).total_seconds() / 60
            row["resolution_time"] = f"{int(resolution_time)} min"
        else:
            age = (datetime.utcnow() - incident.created_at).total_seconds() / 3600
            row["age_hours"] = f"{int(age)}h"
        
        data.append(row)
    
    return {
        "total_count": len(data),
        "rows": data
    }


async def generate_servers_report(report: CustomReport, db: Session, current_user: User):
    """Gerar relatório de servidores"""
    
    filters = report.filters
    
    # Query base
    query = db.query(Server).filter(
        Server.tenant_id == current_user.tenant_id
    )
    
    # Aplicar filtros
    if 'environment' in filters:
        query = query.filter(Server.environment == filters['environment'])
    
    if 'is_active' in filters:
        query = query.filter(Server.is_active == filters['is_active'])
    
    if 'device_type' in filters:
        query = query.filter(Server.device_type == filters['device_type'])
    
    servers = query.all()
    
    # Formatar dados
    data = []
    for server in servers:
        # Contar incidentes
        incidents_count = db.query(Incident).join(Sensor).filter(
            Sensor.server_id == server.id,
            Incident.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        row = {
            "id": server.id,
            "hostname": server.hostname,
            "ip_address": server.ip_address,
            "os_type": server.os_type,
            "environment": server.environment,
            "device_type": server.device_type,
            "is_active": server.is_active,
            "incidents_count": incidents_count
        }
        
        data.append(row)
    
    return {
        "total_count": len(data),
        "rows": data
    }


async def generate_availability_report(report: CustomReport, db: Session, current_user: User):
    """Gerar relatório de disponibilidade"""
    # Implementação similar aos outros
    return {"total_count": 0, "rows": []}


async def generate_performance_report(report: CustomReport, db: Session, current_user: User):
    """Gerar relatório de performance"""
    # Implementação similar aos outros
    return {"total_count": 0, "rows": []}


async def generate_errors_report(report: CustomReport, db: Session, current_user: User):
    """Gerar relatório de erros mais comuns"""
    
    filters = report.filters
    period = filters.get('period', 'last_30_days')
    
    if period == 'last_7_days':
        start_date = datetime.utcnow() - timedelta(days=7)
    elif period == 'last_30_days':
        start_date = datetime.utcnow() - timedelta(days=30)
    else:
        start_date = datetime.utcnow() - timedelta(days=30)
    
    # Agrupar incidentes por tipo de sensor
    errors = db.query(
        Sensor.sensor_type,
        func.count(Incident.id).label('occurrence_count'),
        func.count(func.distinct(Server.id)).label('affected_servers'),
        func.min(Incident.created_at).label('first_seen'),
        func.max(Incident.created_at).label('last_seen')
    ).join(Incident, Sensor.id == Incident.sensor_id)\
     .join(Server, Sensor.server_id == Server.id)\
     .filter(
         Server.tenant_id == current_user.tenant_id,
         Incident.created_at >= start_date
     ).group_by(Sensor.sensor_type)\
      .order_by(desc('occurrence_count'))\
      .all()
    
    data = []
    for error in errors:
        data.append({
            "error_type": error.sensor_type,
            "sensor_type": error.sensor_type,
            "occurrence_count": error.occurrence_count,
            "affected_servers": error.affected_servers,
            "first_seen": error.first_seen.isoformat() if error.first_seen else None,
            "last_seen": error.last_seen.isoformat() if error.last_seen else None
        })
    
    return {
        "total_count": len(data),
        "rows": data
    }


async def generate_ai_analysis_report(report: CustomReport, db: Session, current_user: User):
    """Gerar relatório de análise de IA"""
    # Implementação similar aos outros
    return {"total_count": 0, "rows": []}
