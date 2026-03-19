"""
Observability Router — Coruja Monitor v3.0
Endpoints: health-score, impact-map, intelligent alerts, WebSocket
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/v1", tags=["Observability v3"])

# ─── WebSocket connection manager ────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = ConnectionManager()

# ─── Health Score ─────────────────────────────────────────────────────────────

@router.get("/observability/health-score")
async def get_health_score(db: Session = Depends(get_db)):
    """
    Calcula health score geral da infraestrutura (0-100).
    Baseado em: sensores ok/total, incidentes abertos, alertas críticos.
    """
    try:
        # Total sensors and their statuses — status comes from latest metric per sensor
        sensor_stats = db.execute(text("""
            WITH latest AS (
                SELECT DISTINCT ON (sensor_id)
                    sensor_id,
                    status
                FROM metrics
                ORDER BY sensor_id, timestamp DESC
            )
            SELECT
                COUNT(*) FILTER (WHERE l.status = 'ok') as ok_count,
                COUNT(*) FILTER (WHERE l.status = 'warning') as warning_count,
                COUNT(*) FILTER (WHERE l.status = 'critical') as critical_count,
                COUNT(*) FILTER (WHERE l.status IS NULL OR l.status NOT IN ('ok','warning','critical')) as unknown_count,
                COUNT(s.id) as total
            FROM sensors s
            LEFT JOIN latest l ON l.sensor_id = s.id
            WHERE s.is_active = true
        """)).fetchone()

        total = sensor_stats.total or 1
        ok = sensor_stats.ok_count or 0
        warning = sensor_stats.warning_count or 0
        critical = sensor_stats.critical_count or 0

        # Open incidents
        incident_count = db.execute(text(
            "SELECT COUNT(*) FROM incidents WHERE status = 'open'"
        )).scalar() or 0

        # Score formula: ok*1.0 + warning*0.5 + critical*0 — normalized
        weighted = (ok * 1.0 + warning * 0.5) / total * 100
        # Penalize for open incidents (max -20 points)
        penalty = min(incident_count * 2, 20)
        score = max(0, min(100, weighted - penalty))

        # Trend: compare with 1h ago (simplified)
        trend = "stable"
        if score >= 90:
            health_status = "healthy"
        elif score >= 70:
            health_status = "degraded"
        else:
            health_status = "critical"

        return {
            "score": round(score, 1),
            "status": health_status,
            "trend": trend,
            "breakdown": {
                "sensors_ok": ok,
                "sensors_warning": warning,
                "sensors_critical": critical,
                "sensors_unknown": sensor_stats.unknown_count or 0,
                "sensors_total": total,
                "open_incidents": incident_count,
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "score": 0,
            "status": "unknown",
            "trend": "unknown",
            "breakdown": {},
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# ─── Impact Map ───────────────────────────────────────────────────────────────

@router.get("/observability/impact-map")
async def get_impact_map(db: Session = Depends(get_db)):
    """
    Retorna mapa de impacto: servidores com sensores críticos e seus afetados.
    """
    try:
        rows = db.execute(text("""
            WITH latest AS (
                SELECT DISTINCT ON (sensor_id)
                    sensor_id,
                    status
                FROM metrics
                ORDER BY sensor_id, timestamp DESC
            )
            SELECT
                s.id as server_id,
                s.name as server_name,
                s.ip_address,
                COUNT(sen.id) FILTER (WHERE l.status = 'critical') as critical_sensors,
                COUNT(sen.id) FILTER (WHERE l.status = 'warning') as warning_sensors,
                COUNT(sen.id) as total_sensors
            FROM servers s
            LEFT JOIN sensors sen ON sen.server_id = s.id AND sen.is_active = true
            LEFT JOIN latest l ON l.sensor_id = sen.id
            GROUP BY s.id, s.name, s.ip_address
            HAVING COUNT(sen.id) FILTER (WHERE l.status IN ('critical','warning')) > 0
            ORDER BY critical_sensors DESC, warning_sensors DESC
            LIMIT 50
        """)).fetchall()

        nodes = []
        for r in rows:
            severity = "critical" if r.critical_sensors > 0 else "warning"
            nodes.append({
                "id": str(r.server_id),
                "name": r.server_name,
                "ip": r.ip_address,
                "severity": severity,
                "critical_sensors": r.critical_sensors,
                "warning_sensors": r.warning_sensors,
                "total_sensors": r.total_sensors,
            })

        return {
            "nodes": nodes,
            "total_affected": len(nodes),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"nodes": [], "total_affected": 0, "error": str(e),
                "timestamp": datetime.utcnow().isoformat()}

# ─── Intelligent Alerts ───────────────────────────────────────────────────────

@router.get("/alerts/intelligent")
async def get_intelligent_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Lista alertas inteligentes da tabela intelligent_alerts (v3).
    Fallback para incidents se tabela não existir.
    """
    try:
        where_clauses = []
        params = {"limit": limit}
        if status:
            where_clauses.append("status = :status")
            params["status"] = status
        if severity:
            where_clauses.append("severity = :severity")
            params["severity"] = severity

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        rows = db.execute(text(f"""
            SELECT id, title, severity, status, root_cause,
                   affected_hosts, confidence, created_at, resolved_at
            FROM intelligent_alerts
            {where_sql}
            ORDER BY created_at DESC
            LIMIT :limit
        """), params).fetchall()

        alerts = []
        for r in rows:
            alerts.append({
                "id": str(r.id),
                "title": r.title,
                "severity": r.severity,
                "status": r.status,
                "root_cause": r.root_cause,
                "affected_hosts": r.affected_hosts or [],
                "confidence": r.confidence,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
            })
        return {"alerts": alerts, "total": len(alerts)}

    except Exception:
        # Fallback: use incidents table
        try:
            rows = db.execute(text("""
                SELECT id, title, severity, status, description, created_at, resolved_at
                FROM incidents
                ORDER BY created_at DESC
                LIMIT :limit
            """), {"limit": limit}).fetchall()

            alerts = []
            for r in rows:
                alerts.append({
                    "id": str(r.id),
                    "title": r.title,
                    "severity": r.severity,
                    "status": r.status,
                    "root_cause": r.description,
                    "affected_hosts": [],
                    "confidence": None,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
                })
            return {"alerts": alerts, "total": len(alerts), "source": "incidents_fallback"}
        except Exception as e2:
            return {"alerts": [], "total": 0, "error": str(e2)}


@router.get("/alerts/intelligent/{alert_id}/root-cause")
async def get_alert_root_cause(alert_id: str, db: Session = Depends(get_db)):
    """Retorna análise de causa raiz de um alerta inteligente."""
    try:
        row = db.execute(text("""
            SELECT id, title, severity, status, root_cause,
                   affected_hosts, confidence, created_at, event_ids
            FROM intelligent_alerts
            WHERE id = :alert_id
        """), {"alert_id": alert_id}).fetchone()

        if not row:
            return {"error": "Alert not found", "alert_id": alert_id}

        return {
            "alert_id": str(row.id),
            "title": row.title,
            "root_cause": row.root_cause,
            "confidence": row.confidence,
            "affected_hosts": row.affected_hosts or [],
            "event_ids": row.event_ids or [],
            "severity": row.severity,
            "status": row.status,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
    except Exception as e:
        return {"error": str(e), "alert_id": alert_id}

# ─── WebSocket — real-time observability ─────────────────────────────────────

@router.websocket("/ws/observability")
async def ws_observability(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket para atualizações em tempo real do dashboard de observabilidade.
    Envia health-score + alertas críticos a cada 5 segundos.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Build snapshot
            try:
                sensor_stats = db.execute(text("""
                    WITH latest AS (
                        SELECT DISTINCT ON (sensor_id)
                            sensor_id, status
                        FROM metrics
                        ORDER BY sensor_id, timestamp DESC
                    )
                    SELECT
                        COUNT(s.id) FILTER (WHERE l.status = 'ok') as ok_count,
                        COUNT(s.id) FILTER (WHERE l.status = 'critical') as critical_count,
                        COUNT(s.id) as total
                    FROM sensors s
                    LEFT JOIN latest l ON l.sensor_id = s.id
                    WHERE s.is_active = true
                """)).fetchone()

                total = sensor_stats.total or 1
                ok = sensor_stats.ok_count or 0
                critical = sensor_stats.critical_count or 0
                score = round((ok / total) * 100, 1)

                payload = {
                    "type": "observability_update",
                    "health_score": score,
                    "sensors_ok": ok,
                    "sensors_critical": critical,
                    "sensors_total": total,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send_json(payload)
            except Exception:
                pass

            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
