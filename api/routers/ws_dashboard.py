"""
WebSocket endpoint para o Dashboard — push de atualizações em tempo real.
Envia overview, health summary e novos incidentes a cada 10s.
"""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from database import SessionLocal

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_overview(db: Session) -> dict:
    try:
        from models import Server, Sensor, Incident
        total_servers = db.query(Server).filter(Server.is_active == True).count()
        total_sensors = db.query(Sensor).filter(
            Sensor.is_active == True,
        ).count()
        open_incidents = db.query(Incident).filter(Incident.status == "open").count()
        critical = db.query(Incident).filter(
            Incident.status == "open", Incident.severity == "critical"
        ).count()
        return {
            "total_servers": total_servers,
            "total_sensors": total_sensors,
            "open_incidents": open_incidents,
            "critical_incidents": critical,
        }
    except Exception as e:
        logger.debug(f"ws_dashboard overview erro: {e}")
        return {}


def _get_health(db: Session) -> dict:
    try:
        from models import Sensor, Metric, Server
        from sqlalchemy import func

        result = {"healthy": 0, "warning": 0, "critical": 0, "unknown": 0, "acknowledged": 0}

        # Get all active sensors
        sensors = db.query(Sensor).join(Server, Sensor.server_id == Server.id).filter(
            Sensor.is_active == True
        ).all()

        if not sensors:
            return result

        sensor_ids = [s.id for s in sensors]

        # Acknowledged sensors counted separately
        ack_ids = {s.id for s in sensors if s.is_acknowledged}
        result["acknowledged"] = len(ack_ids)
        non_ack_ids = [sid for sid in sensor_ids if sid not in ack_ids]

        if not non_ack_ids:
            return result

        # Get latest metric per sensor in a single batch query
        subq = (
            db.query(Metric.sensor_id, func.max(Metric.id).label('max_id'))
            .filter(Metric.sensor_id.in_(non_ack_ids))
            .group_by(Metric.sensor_id)
            .subquery()
        )
        latest_metrics = (
            db.query(Metric.sensor_id, Metric.status)
            .join(subq, Metric.id == subq.c.max_id)
            .all()
        )

        sensors_with_metric = set()
        for sensor_id, status in latest_metrics:
            sensors_with_metric.add(sensor_id)
            if status == "critical":
                result["critical"] += 1
            elif status == "warning":
                result["warning"] += 1
            else:
                result["healthy"] += 1

        # Sensors with no metrics at all
        result["unknown"] += len(set(non_ack_ids) - sensors_with_metric)

        return result
    except Exception as e:
        logger.debug(f"ws_dashboard health erro: {e}")
        return {}


@router.websocket("/ws/dashboard")
async def ws_dashboard(websocket: WebSocket, token: str = Query(default="")):
    await websocket.accept()
    logger.info("WebSocket dashboard conectado")
    try:
        while True:
            db = SessionLocal()
            try:
                overview = _get_overview(db)
                health = _get_health(db)
            finally:
                db.close()

            await websocket.send_text(json.dumps({"type": "overview", "data": overview}))
            await websocket.send_text(json.dumps({"type": "health", "data": health}))
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logger.info("WebSocket dashboard desconectado")
    except Exception as e:
        logger.debug(f"WebSocket dashboard erro: {e}")


def _get_services_status(db: Session, server_id: int = None) -> list:
    """Retorna status atual dos sensores de serviço (tipo 'service')"""
    try:
        from models import Sensor, Metric, Server
        from sqlalchemy import func

        query = db.query(Sensor).join(Server, Sensor.server_id == Server.id).filter(
            Sensor.sensor_type == 'service',
            Sensor.is_active == True
        )
        if server_id:
            query = query.filter(Sensor.server_id == server_id)

        sensors = query.all()
        if not sensors:
            return []

        sensor_ids = [s.id for s in sensors]

        # Latest metric per sensor
        subq = (
            db.query(Metric.sensor_id, func.max(Metric.id).label('max_id'))
            .filter(Metric.sensor_id.in_(sensor_ids))
            .group_by(Metric.sensor_id)
            .subquery()
        )
        latest = db.query(Metric).join(subq, Metric.id == subq.c.max_id).all()
        latest_map = {m.sensor_id: m for m in latest}

        result = []
        for sensor in sensors:
            m = latest_map.get(sensor.id)
            meta = (m.extra_metadata or {}) if m else {}
            result.append({
                "sensor_id": sensor.id,
                "server_id": sensor.server_id,
                "service_name": meta.get("service_name", sensor.name),
                "display_name": meta.get("display_name", sensor.name),
                "state": meta.get("state", "Unknown"),
                "is_running": bool(m and m.value == 1) if m else None,
                "status": m.status if m else "unknown",
                "last_seen": m.timestamp.isoformat() if m else None,
            })
        return result
    except Exception as e:
        logger.debug(f"ws services status erro: {e}")
        return []


@router.websocket("/ws/services")
async def ws_services(
    websocket: WebSocket,
    token: str = Query(default=""),
    server_id: int = Query(default=None)
):
    await websocket.accept()
    logger.info(f"WebSocket services conectado (server_id={server_id})")
    try:
        while True:
            db = SessionLocal()
            try:
                services = _get_services_status(db, server_id=server_id)
                # Debug: count total service sensors regardless of server filter
                from models import Sensor
                total_service_sensors = db.query(Sensor).filter(
                    Sensor.sensor_type == 'service'
                ).count()
            finally:
                db.close()

            await websocket.send_text(json.dumps({
                "type": "services",
                "server_id": server_id,
                "data": services,
                "count": len(services),
                "running": sum(1 for s in services if s["is_running"]),
                "stopped": sum(1 for s in services if s["is_running"] is False),
                "debug": {
                    "total_service_sensors_in_db": total_service_sensors,
                    "filter_server_id": server_id,
                }
            }))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.info("WebSocket services desconectado")
    except Exception as e:
        logger.debug(f"WebSocket services erro: {e}")


from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

@router.get("/services/debug")
def services_debug(server_id: int = None, db: Session = Depends(get_db)):
    """Lista sensores de serviço com status atual — inclui ativos e inativos (para UI de seleção)"""
    from models import Sensor, Server, Metric
    from sqlalchemy import func

    query = db.query(Sensor).filter(Sensor.sensor_type == 'service')
    if server_id:
        query = query.filter(Sensor.server_id == server_id)

    sensors = query.all()
    if not sensors:
        return {"total": 0, "sensors": []}

    sensor_ids = [s.id for s in sensors]

    # Latest metric per sensor (single batch query)
    subq = (
        db.query(Metric.sensor_id, func.max(Metric.id).label('max_id'))
        .filter(Metric.sensor_id.in_(sensor_ids))
        .group_by(Metric.sensor_id)
        .subquery()
    )
    latest = db.query(Metric).join(subq, Metric.id == subq.c.max_id).all()
    latest_map = {m.sensor_id: m for m in latest}

    # Server hostname cache
    server_ids = list({s.server_id for s in sensors})
    servers_map = {
        srv.id: srv.hostname
        for srv in db.query(Server).filter(Server.id.in_(server_ids)).all()
    }

    # Metric count per sensor (batch)
    counts = (
        db.query(Metric.sensor_id, func.count(Metric.id).label('cnt'))
        .filter(Metric.sensor_id.in_(sensor_ids))
        .group_by(Metric.sensor_id)
        .all()
    )
    count_map = {row.sensor_id: row.cnt for row in counts}

    result = []
    for s in sensors:
        m = latest_map.get(s.id)
        meta = (m.extra_metadata or {}) if m else {}
        cfg = s.config or {}
        # display_name: métrica > config > fallback do nome
        svc_name = cfg.get("service_name") or s.name.replace("Service ", "", 1)
        disp_name = cfg.get("display_name") or svc_name
        # state: métrica > config (estado no momento do discovery) > Unknown
        cfg_state = cfg.get("state", "Unknown")
        cfg_running = cfg_state == "Running"
        result.append({
            "sensor_id": s.id,
            "server_id": s.server_id,
            "server_hostname": servers_map.get(s.server_id),
            "name": s.name,
            "service_name": meta.get("service_name", svc_name),
            "display_name": meta.get("display_name", disp_name),
            "is_active": s.is_active,
            "is_running": bool(m and m.value == 1) if m else cfg_running,
            "state": meta.get("state") or cfg_state,
            "last_status": m.status if m else "unknown",
            "last_seen": m.timestamp.isoformat() if m else None,
            "metric_count": count_map.get(s.id, 0),
        })
    return {"total": len(result), "sensors": result}
