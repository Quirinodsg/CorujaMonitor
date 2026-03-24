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
            Sensor.is_active == True,
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
            Sensor.is_active == True,
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
    from sqlalchemy import text

    if current_user.role == 'admin':
        tenant_filter = ""
        params = {}
    else:
        tenant_filter = "AND srv.tenant_id = :tenant_id"
        params = {"tenant_id": current_user.tenant_id}

    rows = db.execute(text(f"""
        SELECT
            SUM(CASE WHEN s.is_acknowledged = TRUE THEN 1 ELSE 0 END) AS acknowledged,
            SUM(CASE WHEN s.is_acknowledged = FALSE AND m.status = 'critical' THEN 1 ELSE 0 END) AS critical,
            SUM(CASE WHEN s.is_acknowledged = FALSE AND m.status = 'warning' THEN 1 ELSE 0 END) AS warning,
            SUM(CASE WHEN s.is_acknowledged = FALSE AND m.status = 'ok' THEN 1 ELSE 0 END) AS healthy,
            SUM(CASE WHEN s.is_acknowledged = FALSE AND m.status IS NULL THEN 1 ELSE 0 END) AS unknown
        FROM sensors s
        JOIN servers srv ON srv.id = s.server_id
        LEFT JOIN LATERAL (
            SELECT status FROM metrics
            WHERE sensor_id = s.id
            ORDER BY timestamp DESC
            LIMIT 1
        ) m ON TRUE
        WHERE s.is_active = TRUE {tenant_filter}
    """), params).fetchone()

    return {
        "healthy": int(rows.healthy or 0),
        "warning": int(rows.warning or 0),
        "critical": int(rows.critical or 0),
        "unknown": int(rows.unknown or 0),
        "acknowledged": int(rows.acknowledged or 0),
    }
