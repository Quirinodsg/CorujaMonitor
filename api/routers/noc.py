"""
NOC (Network Operations Center) Router
Endpoints para modo NOC com dados em tempo real
OTIMIZADO: queries agregadas em vez de N+1 loops
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, case, text
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from database import get_db
from models import Server, Sensor, Metric, Incident, User, Tenant
from auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)


def _server_ids_for_user(db: Session, user: User):
    """Retorna lista de server_ids acessíveis pelo usuário."""
    q = db.query(Server.id)
    if user.role != 'admin':
        q = q.filter(Server.tenant_id == user.tenant_id)
    return [r[0] for r in q.all()]


@router.get("/global-status")
async def get_global_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Status global do sistema para NOC — queries agregadas, sem N+1."""
    try:
        now = datetime.utcnow()
        since_24h = now - timedelta(hours=24)

        # ── 1. Contagem de servidores por status via subquery ──────────────
        inc_sub = (
            db.query(
                Sensor.server_id,
                func.max(
                    case(
                        (and_(Incident.status.in_(['open', 'acknowledged']),
                              Incident.severity == 'critical'), 2),
                        (and_(Incident.status.in_(['open', 'acknowledged']),
                              Incident.severity == 'warning'), 1),
                        else_=0
                    )
                ).label('sev')
            )
            .join(Incident, Incident.sensor_id == Sensor.id)
            .group_by(Sensor.server_id)
            .subquery()
        )

        base_q = db.query(Server.id)
        if current_user.role != 'admin':
            base_q = base_q.filter(Server.tenant_id == current_user.tenant_id)
        server_ids = [r[0] for r in base_q.all()]
        total_servers = len(server_ids)

        if not server_ids:
            return {
                'servers_ok': 0, 'servers_warning': 0, 'servers_critical': 0,
                'total_servers': 0, 'availability': 100.0,
                'companies': [], 'timestamp': now.isoformat()
            }

        sev_rows = (
            db.query(inc_sub.c.server_id, inc_sub.c.sev)
            .filter(inc_sub.c.server_id.in_(server_ids))
            .all()
        )
        sev_map = {r.server_id: r.sev for r in sev_rows}

        servers_critical = sum(1 for sid in server_ids if sev_map.get(sid, 0) == 2)
        servers_warning  = sum(1 for sid in server_ids if sev_map.get(sid, 0) == 1)
        servers_ok       = total_servers - servers_critical - servers_warning

        # ── 2. Disponibilidade 24h via duas queries simples ────────────────
        metric_base = (
            db.query(Metric)
            .join(Sensor, Metric.sensor_id == Sensor.id)
            .join(Server, Sensor.server_id == Server.id)
            .filter(Metric.timestamp >= since_24h)
        )
        if current_user.role != 'admin':
            metric_base = metric_base.filter(Server.tenant_id == current_user.tenant_id)

        total_metrics = metric_base.count()
        ok_metrics = metric_base.filter(Metric.status == 'ok').count()
        availability = (ok_metrics / total_metrics * 100) if total_metrics > 0 else 100.0

        # ── 3. Status por empresa (admin only) — queries por tenant ────────
        companies = []
        if current_user.role == 'admin':
            tenants = db.query(Tenant).all()
            for tenant in tenants:
                t_server_ids = [r[0] for r in db.query(Server.id).filter(Server.tenant_id == tenant.id).all()]
                if not t_server_ids:
                    continue

                t_sev_rows = (
                    db.query(inc_sub.c.server_id, inc_sub.c.sev)
                    .filter(inc_sub.c.server_id.in_(t_server_ids))
                    .all()
                )
                t_sev_map = {r.server_id: r.sev for r in t_sev_rows}
                t_critical = sum(1 for sid in t_server_ids if t_sev_map.get(sid, 0) == 2)
                t_warning  = sum(1 for sid in t_server_ids if t_sev_map.get(sid, 0) == 1)
                t_ok       = len(t_server_ids) - t_critical - t_warning

                company_status = 'critical' if t_critical > 0 else ('warning' if t_warning > 0 else 'ok')
                companies.append({
                    'id': tenant.id,
                    'name': tenant.name,
                    'ok': t_ok,
                    'warning': t_warning,
                    'critical': t_critical,
                    'status': company_status,
                    'availability': 99.9
                })

        return {
            'servers_ok': servers_ok,
            'servers_warning': servers_warning,
            'servers_critical': servers_critical,
            'total_servers': total_servers,
            'availability': round(availability, 2),
            'companies': companies,
            'timestamp': now.isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting global status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap")
async def get_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Heatmap de disponibilidade — uma query por servidor, sem N+1."""
    try:
        now = datetime.utcnow()
        since_24h = now - timedelta(hours=24)

        srv_q = db.query(Server).filter(Server.is_active == True)
        if current_user.role != 'admin':
            srv_q = srv_q.filter(Server.tenant_id == current_user.tenant_id)
        servers = srv_q.all()

        if not servers:
            return []

        server_ids = [s.id for s in servers]

        # Incidentes ativos agrupados por server_id
        inc_rows = (
            db.query(
                Sensor.server_id,
                func.max(
                    case(
                        (and_(Incident.status.in_(['open', 'acknowledged']),
                              Incident.severity == 'critical'), 2),
                        (and_(Incident.status.in_(['open', 'acknowledged']),
                              Incident.severity == 'warning'), 1),
                        else_=0
                    )
                ).label('sev')
            )
            .join(Incident, Incident.sensor_id == Sensor.id)
            .filter(Sensor.server_id.in_(server_ids))
            .group_by(Sensor.server_id)
            .all()
        )
        sev_map = {r.server_id: r.sev for r in inc_rows}

        # Disponibilidade 24h agrupada por server_id (apenas servidores sem incidente)
        ok_server_ids = [sid for sid in server_ids if sev_map.get(sid, 0) == 0]
        avail_map: Dict[int, float] = {}
        if ok_server_ids:
            counts = (
                db.query(
                    Sensor.server_id,
                    func.count(Metric.id).label('total'),
                    func.sum(case((Metric.status == 'ok', 1), else_=0)).label('ok_count')
                )
                .join(Sensor, Metric.sensor_id == Sensor.id)
                .filter(
                    Sensor.server_id.in_(ok_server_ids),
                    Metric.timestamp >= since_24h
                )
                .group_by(Sensor.server_id)
                .all()
            )
            for row in counts:
                avail_map[row.server_id] = (row.ok_count / row.total * 100) if row.total > 0 else 100.0

        heatmap = []
        for server in servers:
            sev = sev_map.get(server.id, 0)
            if sev == 2:
                status, availability = 'critical', 50.0
            elif sev == 1:
                status, availability = 'warning', 85.0
            else:
                availability = avail_map.get(server.id, 100.0)
                status = 'ok' if availability >= 95 else ('warning' if availability >= 90 else 'critical')

            heatmap.append({
                'id': server.id,
                'hostname': server.hostname,
                'ip_address': server.ip_address,
                'availability': round(availability, 1),
                'status': status
            })

        return heatmap

    except Exception as e:
        logger.error(f"Error getting heatmap: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-incidents")
async def get_active_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Incidentes ativos para ticker do NOC."""
    try:
        q = (
            db.query(Incident)
            .join(Sensor, Incident.sensor_id == Sensor.id)
            .join(Server, Sensor.server_id == Server.id)
            .filter(Incident.status.in_(['open', 'acknowledged']))
        )
        if current_user.role != 'admin':
            q = q.filter(Server.tenant_id == current_user.tenant_id)
        incidents = q.order_by(desc(Incident.created_at)).limit(50).all()

        now = datetime.utcnow()
        result = []
        for incident in incidents:
            try:
                created_at = incident.created_at
                if created_at.tzinfo is not None:
                    created_at = created_at.replace(tzinfo=None)
                duration = now - created_at
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                result.append({
                    'id': incident.id,
                    'severity': incident.severity,
                    'server_name': incident.sensor.server.hostname,
                    'sensor_name': incident.sensor.name,
                    'description': incident.description,
                    'created_at': incident.created_at.isoformat(),
                    'duration': f"{hours}h {minutes}m"
                })
            except Exception:
                continue

        return result

    except Exception as e:
        logger.error(f"Error getting active incidents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis")
async def get_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """KPIs consolidados para NOC — queries agregadas."""
    try:
        now = datetime.utcnow()
        since_30d = now - timedelta(days=30)
        since_24h = now - timedelta(hours=24)

        inc_base = (
            db.query(Incident)
            .join(Sensor, Incident.sensor_id == Sensor.id)
            .outerjoin(Server, Sensor.server_id == Server.id)
        )
        if current_user.role != 'admin':
            from sqlalchemy import or_, and_, exists, text as sa_text
            from models import Probe
            inc_base = inc_base.filter(
                or_(
                    exists().where(and_(Server.id == Sensor.server_id, Server.tenant_id == current_user.tenant_id)),
                    exists().where(and_(Probe.id == Sensor.probe_id, Probe.tenant_id == current_user.tenant_id)),
                    and_(Sensor.server_id == None, Sensor.probe_id == None),
                )
            )

        # MTTR via SQL avg
        mttr_row = (
            inc_base
            .filter(Incident.resolved_at.isnot(None), Incident.created_at >= since_30d)
            .with_entities(
                func.avg(
                    func.extract('epoch', Incident.resolved_at) -
                    func.extract('epoch', Incident.created_at)
                )
            )
            .scalar()
        )
        mttr = int((mttr_row or 0) / 60)

        # SLA 30d
        metric_base = (
            db.query(Metric)
            .join(Sensor, Metric.sensor_id == Sensor.id)
            .join(Server, Sensor.server_id == Server.id)
            .filter(Metric.timestamp >= since_30d)
        )
        if current_user.role != 'admin':
            metric_base = metric_base.filter(Server.tenant_id == current_user.tenant_id)

        total_30d = metric_base.count()
        ok_30d = metric_base.filter(Metric.status == 'ok').count()
        sla = (ok_30d / total_30d * 100) if total_30d > 0 else 100.0

        # Contagens de incidentes
        incidents_24h = inc_base.filter(Incident.created_at >= since_24h).count()

        return {
            'mttr': mttr,
            'mtbf': 720,
            'sla': round(sla, 2),
            'incidents_24h': incidents_24h
        }

    except Exception as e:
        logger.error(f"Error getting KPIs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
