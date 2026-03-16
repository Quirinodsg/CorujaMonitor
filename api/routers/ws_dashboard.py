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
        from models import Sensor
        from sqlalchemy import func
        rows = db.query(Sensor.status, func.count(Sensor.id)).group_by(Sensor.status).all()
        result = {"healthy": 0, "warning": 0, "critical": 0, "unknown": 0, "acknowledged": 0}
        for status, count in rows:
            key = status if status in result else "unknown"
            result[key] = count
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
