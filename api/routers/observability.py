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
async def get_health_score(
    db: Session = Depends(get_db),
    current_user=Depends(__import__('auth').get_current_active_user),
):
    """
    Calcula health score geral da infraestrutura (0-100).
    Baseado em: sensores ok/total, incidentes abertos, alertas críticos.
    """
    try:
        from models import User as _User
        # Filtro de tenant
        if current_user.role == 'admin':
            tenant_filter = ""
            params: dict = {}
        else:
            tenant_filter = """
                AND (
                    EXISTS (SELECT 1 FROM servers srv WHERE srv.id = s.server_id AND srv.tenant_id = :tid)
                    OR EXISTS (SELECT 1 FROM probes p WHERE p.id = s.probe_id AND p.tenant_id = :tid)
                    OR (s.server_id IS NULL AND s.probe_id IS NULL)
                )
            """
            params = {"tid": current_user.tenant_id}

        sensor_stats = db.execute(text(f"""
            SELECT
                COUNT(*) FILTER (WHERE m.status = 'ok') as ok_count,
                COUNT(*) FILTER (WHERE m.status = 'warning') as warning_count,
                COUNT(*) FILTER (WHERE m.status = 'critical') as critical_count,
                COUNT(*) FILTER (WHERE m.status IS NULL OR m.status NOT IN ('ok','warning','critical')) as unknown_count,
                COUNT(s.id) as total
            FROM sensors s
            LEFT JOIN LATERAL (
                SELECT status FROM metrics
                WHERE sensor_id = s.id
                ORDER BY timestamp DESC
                LIMIT 1
            ) m ON TRUE
            WHERE s.is_active = true {tenant_filter}
        """), params).fetchone()

        total = sensor_stats.total or 1
        ok = sensor_stats.ok_count or 0
        warning = sensor_stats.warning_count or 0
        critical = sensor_stats.critical_count or 0

        # Open incidents filtrados por tenant
        if current_user.role == 'admin':
            incident_count = db.execute(text(
                "SELECT COUNT(*) FROM incidents WHERE status = 'open'"
            )).scalar() or 0
        else:
            incident_count = db.execute(text("""
                SELECT COUNT(i.id) FROM incidents i
                JOIN sensors s ON s.id = i.sensor_id
                LEFT JOIN servers srv ON srv.id = s.server_id
                LEFT JOIN probes p ON p.id = s.probe_id
                WHERE i.status = 'open'
                  AND (srv.tenant_id = :tid OR p.tenant_id = :tid
                       OR (s.server_id IS NULL AND s.probe_id IS NULL))
            """), {"tid": current_user.tenant_id}).scalar() or 0

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
async def get_impact_map(
    db: Session = Depends(get_db),
    current_user=Depends(__import__('auth').get_current_active_user),
):
    """
    Retorna mapa de impacto: servidores e sensores standalone com alertas críticos/warning.
    """
    try:
        if current_user.role == 'admin':
            tenant_filter = ""
            params: dict = {}
        else:
            tenant_filter = "AND srv.tenant_id = :tid"
            params = {"tid": current_user.tenant_id}

        # Servidores com sensores críticos/warning
        rows = db.execute(text(f"""
            SELECT
                srv.id as server_id,
                srv.hostname as server_name,
                srv.ip_address,
                COUNT(sen.id) FILTER (WHERE m.status = 'critical') as critical_sensors,
                COUNT(sen.id) FILTER (WHERE m.status = 'warning') as warning_sensors,
                COUNT(sen.id) as total_sensors
            FROM servers srv
            LEFT JOIN sensors sen ON sen.server_id = srv.id AND sen.is_active = true
            LEFT JOIN LATERAL (
                SELECT status FROM metrics
                WHERE sensor_id = sen.id
                ORDER BY timestamp DESC
                LIMIT 1
            ) m ON TRUE
            WHERE 1=1 {tenant_filter}
            GROUP BY srv.id, srv.hostname, srv.ip_address
            HAVING COUNT(sen.id) FILTER (WHERE m.status IN ('critical','warning')) > 0
            ORDER BY critical_sensors DESC, warning_sensors DESC
            LIMIT 50
        """), params).fetchall()

        nodes = []
        for r in rows:
            severity = "critical" if r.critical_sensors > 0 else "warning"
            nodes.append({
                "id": f"srv-{r.server_id}",
                "name": r.server_name,
                "ip": r.ip_address,
                "severity": severity,
                "critical_sensors": r.critical_sensors,
                "warning_sensors": r.warning_sensors,
                "total_sensors": r.total_sensors,
                "type": "server",
            })

        # Sensores standalone (sem servidor) com alertas
        if current_user.role == 'admin':
            standalone_filter = "AND (s.server_id IS NULL)"
            standalone_params: dict = {}
        else:
            standalone_filter = """
                AND s.server_id IS NULL
                AND (
                    EXISTS (SELECT 1 FROM probes p WHERE p.id = s.probe_id AND p.tenant_id = :tid)
                    OR s.probe_id IS NULL
                )
            """
            standalone_params = {"tid": current_user.tenant_id}

        standalone_rows = db.execute(text(f"""
            SELECT
                s.id as sensor_id,
                s.name as sensor_name,
                m.status
            FROM sensors s
            LEFT JOIN LATERAL (
                SELECT status FROM metrics
                WHERE sensor_id = s.id
                ORDER BY timestamp DESC
                LIMIT 1
            ) m ON TRUE
            WHERE s.is_active = true
              {standalone_filter}
              AND m.status IN ('critical', 'warning')
            ORDER BY CASE m.status WHEN 'critical' THEN 0 ELSE 1 END
            LIMIT 20
        """), standalone_params).fetchall()

        for r in standalone_rows:
            nodes.append({
                "id": f"sensor-{r.sensor_id}",
                "name": r.sensor_name,
                "ip": "Standalone",
                "severity": r.status,
                "critical_sensors": 1 if r.status == 'critical' else 0,
                "warning_sensors": 1 if r.status == 'warning' else 0,
                "total_sensors": 1,
                "type": "standalone",
            })

        # Reordenar: críticos primeiro
        nodes.sort(key=lambda n: (0 if n['severity'] == 'critical' else 1))

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


@router.post("/alerts/intelligent/{alert_id}/resolve")
async def resolve_intelligent_alert(alert_id: str, db: Session = Depends(get_db)):
    """Resolve um alerta inteligente."""
    try:
        db.execute(text("""
            UPDATE intelligent_alerts SET status = 'resolved', resolved_at = NOW()
            WHERE id = :id
        """), {"id": alert_id})
        db.commit()
        return {"status": "ok", "message": "Alerta resolvido"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}


@router.post("/alerts/intelligent/{alert_id}/acknowledge")
async def acknowledge_intelligent_alert(alert_id: str, db: Session = Depends(get_db)):
    """Reconhece um alerta inteligente."""
    try:
        db.execute(text("""
            UPDATE intelligent_alerts SET status = 'acknowledged'
            WHERE id = :id
        """), {"id": alert_id})
        db.commit()
        return {"status": "ok", "message": "Alerta reconhecido"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}


@router.delete("/alerts/intelligent/{alert_id}")
async def delete_intelligent_alert(alert_id: str, db: Session = Depends(get_db)):
    """Exclui um alerta inteligente."""
    try:
        db.execute(text("DELETE FROM intelligent_alerts WHERE id = :id"), {"id": alert_id})
        db.commit()
        return {"status": "ok", "message": "Alerta excluído"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

# ─── WebSocket — real-time observability ─────────────────────────────────────

@router.websocket("/ws/observability")
async def ws_observability(websocket: WebSocket):
    """
    WebSocket para atualizações em tempo real do dashboard de observabilidade.
    Envia health-score + alertas críticos a cada 5 segundos.
    Não usa Depends(get_db) — cria sessão própria para evitar expiração.
    """
    from database import SessionLocal
    await manager.connect(websocket)
    try:
        while True:
            db = SessionLocal()
            try:
                sensor_stats = db.execute(text("""
                    SELECT
                        COUNT(s.id) FILTER (WHERE m.status = 'ok') as ok_count,
                        COUNT(s.id) FILTER (WHERE m.status = 'critical') as critical_count,
                        COUNT(s.id) as total
                    FROM sensors s
                    LEFT JOIN LATERAL (
                        SELECT status FROM metrics
                        WHERE sensor_id = s.id
                        ORDER BY timestamp DESC
                        LIMIT 1
                    ) m ON TRUE
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
            except Exception as e:
                # Enviar erro para o cliente saber o que aconteceu
                try:
                    await websocket.send_json({"type": "error", "message": str(e)})
                except Exception:
                    pass
            finally:
                db.close()

            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
