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
        total_servers = db.query(Server).count()
        total_sensors = db.query(Sensor).count()
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
