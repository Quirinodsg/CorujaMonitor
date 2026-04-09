"""
NOC Real-Time Router
OTIMIZADO: queries agregadas, sem N+1 loops por servidor/sensor
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, case
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import asyncio

from database import get_db
from models import Server, Sensor, Metric, Incident, User, Tenant
from auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nova conexão WebSocket NOC. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Conexão WebSocket NOC fechada. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Erro no WebSocket NOC: {e}")
        manager.disconnect(websocket)


@router.get("/realtime/dashboard")
async def get_realtime_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Dashboard completo em tempo real.
    Usa queries agregadas — O(1) queries independente do número de servidores.
    """
    try:
        now = datetime.utcnow()
        since_24h = now - timedelta(hours=24)
        since_30d = now - timedelta(days=30)
        since_7d  = now - timedelta(days=7)

        # ── Filtro de servidores ──────────────────────────────────────────
        srv_q = db.query(Server).filter(Server.is_active == True)
        if current_user.role != 'admin':
            srv_q = srv_q.filter(Server.tenant_id == current_user.tenant_id)
        servers = srv_q.all()
        server_ids = [s.id for s in servers]
        srv_map = {s.id: s for s in servers}

        if not server_ids:
            return _empty_dashboard(now)

        # ── 1. Incidentes ativos agrupados por server_id ──────────────────
        # Uma query retorna severidade máxima por servidor
        inc_sev_rows = (
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
                ).label('sev'),
                func.count(
                    case((and_(Incident.status.in_(['open', 'acknowledged']),
                               Incident.severity == 'critical'), 1))
                ).label('crit_count'),
                func.count(
                    case((and_(Incident.status.in_(['open', 'acknowledged']),
                               Incident.severity == 'warning'), 1))
                ).label('warn_count'),
            )
            .join(Incident, Incident.sensor_id == Sensor.id)
            .filter(Sensor.server_id.in_(server_ids))
            .group_by(Sensor.server_id)
            .all()
        )
        sev_map = {r.server_id: r for r in inc_sev_rows}

        # ── 2. Contagem de sensores por servidor ──────────────────────────
        sensor_count_rows = (
            db.query(Sensor.server_id, func.count(Sensor.id).label('cnt'))
            .filter(Sensor.server_id.in_(server_ids), Sensor.is_active == True)
            .group_by(Sensor.server_id)
            .all()
        )
        sensor_count_map = {r.server_id: r.cnt for r in sensor_count_rows}

        # ── 3. Disponibilidade 24h por servidor ───────────────────────────
        avail_rows = (
            db.query(
                Sensor.server_id,
                func.count(Metric.id).label('total'),
                func.sum(case((Metric.status == 'ok', 1), else_=0)).label('ok_count')
            )
            .join(Sensor, Metric.sensor_id == Sensor.id)
            .filter(Sensor.server_id.in_(server_ids), Metric.timestamp >= since_24h)
            .group_by(Sensor.server_id)
            .all()
        )
        avail_map = {
            r.server_id: (r.ok_count / r.total * 100) if r.total > 0 else 100.0
            for r in avail_rows
        }

        # ── 4. Última métrica por servidor ────────────────────────────────
        # Subquery: max timestamp por sensor, depois max por servidor
        last_metric_rows = (
            db.query(
                Sensor.server_id,
                func.max(Metric.timestamp).label('last_ts')
            )
            .join(Sensor, Metric.sensor_id == Sensor.id)
            .filter(Sensor.server_id.in_(server_ids))
            .group_by(Sensor.server_id)
            .all()
        )
        last_ts_map = {r.server_id: r.last_ts for r in last_metric_rows}

        # ── 5. Montar lista de servidores ─────────────────────────────────
        servers_data = []
        servers_ok = servers_warning = servers_critical = 0

        for server in servers:
            row = sev_map.get(server.id)
            sev = row.sev if row else 0
            crit_count = row.crit_count if row else 0
            warn_count = row.warn_count if row else 0

            if sev == 2:
                server_status = 'critical'; servers_critical += 1
            elif sev == 1:
                server_status = 'warning'; servers_warning += 1
            else:
                server_status = 'ok'; servers_ok += 1

            availability = avail_map.get(server.id, 100.0)
            last_ts = last_ts_map.get(server.id)

            servers_data.append({
                'id': server.id,
                'hostname': server.hostname,
                'ip_address': server.ip_address,
                'public_ip': getattr(server, 'public_ip', None),
                'os_type': getattr(server, 'os_type', None),
                'status': server_status,
                'availability': round(availability, 2),
                'critical_incidents': crit_count,
                'warning_incidents': warn_count,
                'total_sensors': sensor_count_map.get(server.id, 0),
                'last_update': last_ts.isoformat() if last_ts else None
            })

        # ── 6. Incidentes ativos (lista completa) ─────────────────────────
        inc_q = (
            db.query(Incident)
            .join(Sensor, Incident.sensor_id == Sensor.id)
            .join(Server, Sensor.server_id == Server.id)
            .filter(
                Incident.status.in_(['open', 'acknowledged']),
                Server.id.in_(server_ids)
            )
            .order_by(desc(Incident.created_at))
            .limit(100)
        )
        incidents_data = []
        for incident in inc_q.all():
            try:
                duration = now - incident.created_at.replace(tzinfo=None)
                h = int(duration.total_seconds() // 3600)
                m = int((duration.total_seconds() % 3600) // 60)
                srv = incident.sensor.server if incident.sensor else None
                incidents_data.append({
                    'id': incident.id,
                    'severity': incident.severity,
                    'status': incident.status,
                    'server_id': srv.id if srv else None,
                    'server_name': srv.hostname if srv else 'N/A',
                    'sensor_id': incident.sensor.id if incident.sensor else None,
                    'sensor_name': incident.sensor.name if incident.sensor else 'N/A',
                    'sensor_type': incident.sensor.sensor_type if incident.sensor else 'unknown',
                    'title': incident.title,
                    'description': incident.description,
                    'created_at': incident.created_at.isoformat(),
                    'acknowledged_at': incident.acknowledged_at.isoformat() if incident.acknowledged_at else None,
                    'duration_seconds': int(duration.total_seconds()),
                    'duration_text': f"{h}h {m}m"
                })
            except Exception:
                continue

        # ── 7. Sensores críticos — uma query com subquery de última métrica ─
        # Subquery: última métrica por sensor
        latest_metric_sub = (
            db.query(
                Metric.sensor_id,
                func.max(Metric.timestamp).label('max_ts')
            )
            .join(Sensor, Metric.sensor_id == Sensor.id)
            .filter(Sensor.server_id.in_(server_ids))
            .group_by(Metric.sensor_id)
            .subquery()
        )

        critical_sensor_rows = (
            db.query(Metric, Sensor, Server)
            .join(Sensor, Metric.sensor_id == Sensor.id)
            .join(Server, Sensor.server_id == Server.id)
            .join(
                latest_metric_sub,
                and_(
                    Metric.sensor_id == latest_metric_sub.c.sensor_id,
                    Metric.timestamp == latest_metric_sub.c.max_ts
                )
            )
            .filter(
                Sensor.server_id.in_(server_ids),
                Sensor.is_active == True,
                Metric.status.in_(['warning', 'critical'])
            )
            .all()
        )

        critical_sensors = []
        for metric, sensor, server in critical_sensor_rows:
            critical_sensors.append({
                'server_id': server.id,
                'server_name': server.hostname,
                'sensor_id': sensor.id,
                'sensor_name': sensor.name,
                'sensor_type': sensor.sensor_type,
                'value': metric.value,
                'unit': metric.unit,
                'status': metric.status,
                'threshold_warning': sensor.threshold_warning,
                'threshold_critical': sensor.threshold_critical,
                'timestamp': metric.timestamp.isoformat()
            })

        # ── 8. KPIs ───────────────────────────────────────────────────────
        inc_base = (
            db.query(Incident)
            .join(Sensor, Incident.sensor_id == Sensor.id)
            .join(Server, Sensor.server_id == Server.id)
            .filter(Server.id.in_(server_ids))
        )

        mttr_val = (
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
        mttr = int((mttr_val or 0) / 60)

        metric_base = (
            db.query(Metric)
            .join(Sensor, Metric.sensor_id == Sensor.id)
            .join(Server, Sensor.server_id == Server.id)
            .filter(Server.id.in_(server_ids), Metric.timestamp >= since_30d)
        )
        total_30d = metric_base.count()
        ok_30d    = metric_base.filter(Metric.status == 'ok').count()
        sla = (ok_30d / total_30d * 100) if total_30d > 0 else 100.0

        incidents_24h = inc_base.filter(Incident.created_at >= since_24h).count()
        incidents_7d  = inc_base.filter(Incident.created_at >= since_7d).count()
        resolved_30d  = inc_base.filter(
            Incident.resolved_at.isnot(None), Incident.created_at >= since_30d
        ).count()

        # ── 9. Empresas (admin only) ──────────────────────────────────────
        companies = []
        if current_user.role == 'admin':
            tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
            # Mapa server_id → tenant_id
            srv_tenant = {s.id: s.tenant_id for s in servers}
            from collections import defaultdict
            tenant_sev: Dict[int, Dict] = defaultdict(lambda: {'critical': 0, 'warning': 0, 'ok': 0, 'total': 0})
            for server in servers:
                tid = srv_tenant[server.id]
                row = sev_map.get(server.id)
                sev = row.sev if row else 0
                tenant_sev[tid]['total'] += 1
                if sev == 2:
                    tenant_sev[tid]['critical'] += 1
                elif sev == 1:
                    tenant_sev[tid]['warning'] += 1
                else:
                    tenant_sev[tid]['ok'] += 1

            for tenant in tenants:
                ts = tenant_sev.get(tenant.id)
                if not ts or ts['total'] == 0:
                    continue
                t_status = 'critical' if ts['critical'] > 0 else ('warning' if ts['warning'] > 0 else 'ok')
                companies.append({
                    'id': tenant.id,
                    'name': tenant.name,
                    'servers': ts['total'],
                    'critical_incidents': ts['critical'],
                    'warning_incidents': ts['warning'],
                    'status': t_status
                })

        return {
            'timestamp': now.isoformat(),
            'summary': {
                'servers_ok': servers_ok,
                'servers_warning': servers_warning,
                'servers_critical': servers_critical,
                'servers_offline': 0,
                'total_servers': len(servers),
                'total_incidents': len(incidents_data),
                'critical_incidents': sum(1 for i in incidents_data if i['severity'] == 'critical'),
                'warning_incidents': sum(1 for i in incidents_data if i['severity'] == 'warning'),
            },
            'servers': servers_data,
            'incidents': incidents_data,
            'critical_sensors': critical_sensors,
            'kpis': {
                'mttr': mttr,
                'sla': round(sla, 2),
                'incidents_24h': incidents_24h,
                'incidents_7d': incidents_7d,
                'resolved_30d': resolved_30d
            },
            'companies': companies
        }

    except Exception as e:
        logger.error(f"Erro ao buscar dashboard NOC: {e}", exc_info=True)
        return _empty_dashboard(datetime.utcnow(), error=str(e))


def _empty_dashboard(now: datetime, error: str = None) -> dict:
    base = {
        'timestamp': now.isoformat(),
        'summary': {
            'servers_ok': 0, 'servers_warning': 0, 'servers_critical': 0,
            'servers_offline': 0, 'total_servers': 0,
            'total_incidents': 0, 'critical_incidents': 0, 'warning_incidents': 0
        },
        'servers': [], 'incidents': [], 'critical_sensors': [],
        'kpis': {'mttr': 0, 'sla': 100.0, 'incidents_24h': 0, 'incidents_7d': 0, 'resolved_30d': 0},
        'companies': []
    }
    if error:
        base['status'] = 'degraded'
        base['message'] = f"NOC data temporarily unavailable: {error}"
    return base


@router.get("/realtime/events")
async def get_recent_events(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Eventos recentes do sistema."""
    try:
        q = (
            db.query(Incident)
            .join(Sensor, Incident.sensor_id == Sensor.id)
            .join(Server, Sensor.server_id == Server.id)
        )
        if current_user.role != 'admin':
            q = q.filter(Server.tenant_id == current_user.tenant_id)
        incidents = q.order_by(desc(Incident.created_at)).limit(limit).all()

        events = []
        for incident in incidents:
            try:
                sensor = incident.sensor
                server = sensor.server if sensor else None
                server_name = server.hostname if server else 'N/A'
                sensor_name = sensor.name if sensor else 'N/A'

                events.append({
                    'id': f"incident_{incident.id}_created",
                    'type': 'incident_created',
                    'severity': incident.severity,
                    'server_name': server_name,
                    'sensor_name': sensor_name,
                    'description': incident.title,
                    'timestamp': incident.created_at.isoformat()
                })
                if incident.acknowledged_at:
                    events.append({
                        'id': f"incident_{incident.id}_acknowledged",
                        'type': 'incident_acknowledged',
                        'severity': incident.severity,
                        'server_name': server_name,
                        'sensor_name': sensor_name,
                        'description': "Incidente reconhecido",
                        'timestamp': incident.acknowledged_at.isoformat()
                    })
                if incident.resolved_at:
                    events.append({
                        'id': f"incident_{incident.id}_resolved",
                        'type': 'incident_resolved',
                        'severity': incident.severity,
                        'server_name': server_name,
                        'sensor_name': sensor_name,
                        'description': "Incidente resolvido",
                        'timestamp': incident.resolved_at.isoformat()
                    })
            except Exception:
                continue

        events.sort(key=lambda x: x['timestamp'], reverse=True)
        return events[:limit]

    except Exception as e:
        logger.error(f"Erro ao buscar eventos: {e}")
        return []


async def broadcast_noc_update(event_type: str, data: dict):
    message = {
        'type': event_type,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    await manager.broadcast(message)
