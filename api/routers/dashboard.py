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
        
        # Open incidents — outerjoin para incluir sensores standalone (server_id NULL)
        open_incidents = db.query(func.count(Incident.id)).join(Sensor).outerjoin(Server).filter(
            Incident.status == "open"
        ).scalar()
        
        # Critical incidents — outerjoin para incluir sensores standalone
        critical_incidents = db.query(func.count(Incident.id)).join(Sensor).outerjoin(Server).filter(
            Incident.severity == "critical",
            Incident.status == "open"
        ).scalar()
        
        # Recent incidents (last 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_incidents = db.query(func.count(Incident.id)).join(Sensor).outerjoin(Server).filter(
            Incident.created_at >= yesterday
        ).scalar()
        
        # Auto-resolved incidents (last 30 days)
        last_month = datetime.utcnow() - timedelta(days=30)
        auto_resolved = db.query(func.count(Incident.id)).join(Sensor).outerjoin(Server).filter(
            Incident.status == "auto_resolved",
            Incident.created_at >= last_month
        ).scalar()
    else:
        from sqlalchemy import or_
        from models import Probe

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

        def _incident_base_query():
            return (
                db.query(func.count(Incident.id))
                .join(Sensor, Incident.sensor_id == Sensor.id)
                .outerjoin(Server, Sensor.server_id == Server.id)
                .outerjoin(Probe, Sensor.probe_id == Probe.id)
                .filter(
                    or_(
                        Server.tenant_id == current_user.tenant_id,
                        Probe.tenant_id == current_user.tenant_id,
                        (Sensor.server_id == None) & (Sensor.probe_id == None),
                    )
                )
            )

        # Open incidents
        open_incidents = _incident_base_query().filter(
            Incident.status == "open"
        ).scalar()
        
        # Critical incidents
        critical_incidents = _incident_base_query().filter(
            Incident.severity == "critical",
            Incident.status == "open"
        ).scalar()
        
        # Recent incidents (last 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_incidents = _incident_base_query().filter(
            Incident.created_at >= yesterday
        ).scalar()
        
        # Auto-resolved incidents (last 30 days)
        last_month = datetime.utcnow() - timedelta(days=30)
        auto_resolved = _incident_base_query().filter(
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


@router.get("/network-assets-status")
async def get_network_assets_status(
    ids: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retorna status dos ativos de rede (switch, AP, router, etc.) baseado nos sensores."""
    from sqlalchemy import text

    if not ids:
        return {}

    server_ids = [int(x) for x in ids.split(",") if x.strip().isdigit()]
    if not server_ids:
        return {}

    ids_str = ",".join(str(sid) for sid in server_ids)

    try:
        rows = db.execute(text(f"""
            SELECT
                sen.server_id,
                COUNT(*) FILTER (WHERE m.status = 'critical') AS crit,
                COUNT(*) FILTER (WHERE m.status = 'warning')  AS warn,
                COUNT(*) FILTER (WHERE m.status = 'ok')       AS ok_count,
                COUNT(sen.id) AS total
            FROM sensors sen
            LEFT JOIN LATERAL (
                SELECT status FROM metrics
                WHERE sensor_id = sen.id
                ORDER BY timestamp DESC
                LIMIT 1
            ) m ON TRUE
            WHERE sen.server_id IN ({ids_str}) AND sen.is_active = true
            GROUP BY sen.server_id
        """)).fetchall()

        result = {}
        for r in rows:
            if r.total == 0:
                result[r.server_id] = "unknown"
            elif r.crit > 0:
                result[r.server_id] = "critical"
            elif r.warn > 0:
                result[r.server_id] = "warning"
            elif r.ok_count > 0:
                result[r.server_id] = "ok"
            else:
                result[r.server_id] = "unknown"

        # Servidores sem sensores ficam como unknown
        for sid in server_ids:
            if sid not in result:
                result[sid] = "unknown"

        return result
    except Exception:
        return {sid: "unknown" for sid in server_ids}
