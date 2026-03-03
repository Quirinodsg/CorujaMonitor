from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database import get_db
from models import Server, Sensor, Incident, Metric, User
from auth import get_current_active_user

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Admin vê todos os servidores, usuário normal vê apenas do seu tenant
    if current_user.role == 'admin':
        # Total servers
        total_servers = db.query(func.count(Server.id)).filter(
            Server.is_active == True
        ).scalar()
        
        # Total sensors
        total_sensors = db.query(func.count(Sensor.id)).join(Server).filter(
            Sensor.is_active == True
        ).scalar()
        
        # Open incidents
        open_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
            Incident.status == "open"
        ).scalar()
        
        # Critical incidents
        critical_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
            Incident.severity == "critical",
            Incident.status == "open"
        ).scalar()
        
        # Recent incidents (last 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
            Incident.created_at >= yesterday
        ).scalar()
        
        # Auto-resolved incidents (last 30 days)
        last_month = datetime.utcnow() - timedelta(days=30)
        auto_resolved = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
            Incident.status == "auto_resolved",
            Incident.created_at >= last_month
        ).scalar()
    else:
        # Total servers
        total_servers = db.query(func.count(Server.id)).filter(
            Server.tenant_id == current_user.tenant_id,
            Server.is_active == True
        ).scalar()
        
        # Total sensors
        total_sensors = db.query(func.count(Sensor.id)).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Sensor.is_active == True
        ).scalar()
        
        # Open incidents
        open_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Incident.status == "open"
        ).scalar()
        
        # Critical incidents
        critical_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Incident.severity == "critical",
            Incident.status == "open"
        ).scalar()
        
        # Recent incidents (last 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Incident.created_at >= yesterday
        ).scalar()
        
        # Auto-resolved incidents (last 30 days)
        last_month = datetime.utcnow() - timedelta(days=30)
        auto_resolved = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Incident.status == "auto_resolved",
            Incident.created_at >= last_month
        ).scalar()
    
    return {
        "total_servers": total_servers,
        "total_sensors": total_sensors,
        "open_incidents": open_incidents,
        "critical_incidents": critical_incidents,
        "recent_incidents_24h": recent_incidents,
        "auto_resolved_30d": auto_resolved,
        "health_status": "critical" if critical_incidents > 0 else "warning" if open_incidents > 0 else "healthy"
    }

@router.get("/health-summary")
async def get_health_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get latest metric for each sensor
    from sqlalchemy import distinct
    
    # Admin vê todos os sensores, usuário normal vê apenas do seu tenant
    if current_user.role == 'admin':
        sensors = db.query(Sensor).join(Server).filter(
            Sensor.is_active == True
        ).all()
    else:
        sensors = db.query(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Sensor.is_active == True
        ).all()
    
    health_summary = {
        "healthy": 0,
        "warning": 0,
        "critical": 0,
        "unknown": 0,
        "acknowledged": 0  # Novo: Verificado pela TI
    }
    
    for sensor in sensors:
        # Se sensor foi reconhecido por técnico, conta separadamente
        if sensor.is_acknowledged:
            health_summary["acknowledged"] += 1
            continue
            
        latest_metric = db.query(Metric).filter(
            Metric.sensor_id == sensor.id
        ).order_by(Metric.timestamp.desc()).first()
        
        if not latest_metric:
            health_summary["unknown"] += 1
        elif latest_metric.status == "critical":
            health_summary["critical"] += 1
        elif latest_metric.status == "warning":
            health_summary["warning"] += 1
        else:
            health_summary["healthy"] += 1
    
    return health_summary
