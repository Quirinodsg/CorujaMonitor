"""
NOC Real-Time Router com WebSocket
Sistema de monitoramento em tempo real para NOC
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import json
import asyncio

from database import get_db
from models import Server, Sensor, Metric, Incident, User, Tenant
from auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nova conexão WebSocket. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Conexão WebSocket fechada. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todos os clientes conectados"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem: {e}")
                disconnected.append(connection)
        
        # Remove conexões mortas
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket para atualizações em tempo real do NOC
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Mantém conexão viva
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        manager.disconnect(websocket)


@router.get("/realtime/dashboard")
async def get_realtime_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Dashboard completo em tempo real
    Retorna TODOS os dados necessários para o NOC em uma única chamada
    """
    try:
        # Filtro por tenant
        if current_user.role == 'admin':
            server_filter = Server.is_active == True
        else:
            server_filter = and_(
                Server.tenant_id == current_user.tenant_id,
                Server.is_active == True
            )
        
        # 1. SERVIDORES COM STATUS
        servers = db.query(Server).filter(server_filter).all()
        
        servers_data = []
        servers_ok = 0
        servers_warning = 0
        servers_critical = 0
        servers_offline = 0
        
        logger.info(f"Processando {len(servers)} servidores para dashboard NOC")
        
        for server in servers:
            # Buscar incidentes ativos
            critical_incidents = db.query(Incident).join(Sensor).filter(
                Sensor.server_id == server.id,
                Incident.status.in_(['open', 'acknowledged']),
                Incident.severity == 'critical'
            ).all()
            
            warning_incidents = db.query(Incident).join(Sensor).filter(
                Sensor.server_id == server.id,
                Incident.status.in_(['open', 'acknowledged']),
                Incident.severity == 'warning'
            ).all()
            
            # Buscar sensores do servidor
            sensors = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.is_active == True
            ).all()
            
            # Calcular status do servidor
            if len(critical_incidents) > 0:
                server_status = 'critical'
                servers_critical += 1
            elif len(warning_incidents) > 0:
                server_status = 'warning'
                servers_warning += 1
            else:
                # Servidor sem incidentes = OK
                server_status = 'ok'
                servers_ok += 1
                logger.debug(f"Servidor {server.hostname} marcado como OK")
            
            # Calcular disponibilidade (últimas 24h)
            total_metrics = db.query(Metric).join(Sensor).filter(
                Sensor.server_id == server.id,
                Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            ok_metrics = db.query(Metric).join(Sensor).filter(
                Sensor.server_id == server.id,
                Metric.status == 'ok',
                Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            availability = (ok_metrics / total_metrics * 100) if total_metrics > 0 else 100
            
            # Última atualização
            last_metric = db.query(Metric).join(Sensor).filter(
                Sensor.server_id == server.id
            ).order_by(Metric.timestamp.desc()).first()
            
            last_update = last_metric.timestamp if last_metric else None
            
            servers_data.append({
                'id': server.id,
                'hostname': server.hostname,
                'ip_address': server.ip_address,
                'public_ip': server.public_ip,
                'os_type': server.os_type,
                'status': server_status,
                'availability': round(availability, 2),
                'critical_incidents': len(critical_incidents),
                'warning_incidents': len(warning_incidents),
                'total_sensors': len(sensors),
                'last_update': last_update.isoformat() if last_update else None
            })
        
        logger.info(f"Contadores finais - OK: {servers_ok}, Warning: {servers_warning}, Critical: {servers_critical}, Offline: {servers_offline}")
        
        # 2. INCIDENTES ATIVOS
        if current_user.role == 'admin':
            incidents = db.query(Incident).join(Sensor).join(Server).filter(
                Incident.status.in_(['open', 'acknowledged'])
            ).order_by(desc(Incident.created_at)).limit(100).all()
        else:
            incidents = db.query(Incident).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Incident.status.in_(['open', 'acknowledged'])
            ).order_by(desc(Incident.created_at)).limit(100).all()
        
        incidents_data = []
        for incident in incidents:
            try:
                duration = datetime.utcnow() - incident.created_at
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                
                server = incident.sensor.server if incident.sensor else None
                incidents_data.append({
                    'id': incident.id,
                    'severity': incident.severity,
                    'status': incident.status,
                    'server_id': server.id if server else None,
                    'server_name': server.hostname if server else 'N/A',
                    'sensor_id': incident.sensor.id if incident.sensor else None,
                    'sensor_name': incident.sensor.name if incident.sensor else 'N/A',
                    'sensor_type': incident.sensor.sensor_type if incident.sensor else 'unknown',
                    'title': incident.title,
                    'description': incident.description,
                    'created_at': incident.created_at.isoformat(),
                    'acknowledged_at': incident.acknowledged_at.isoformat() if incident.acknowledged_at else None,
                    'duration_seconds': int(duration.total_seconds()),
                    'duration_text': f"{hours}h {minutes}m"
                })
            except Exception as inc_err:
                logger.warning(f"Erro ao processar incidente {incident.id}: {inc_err}")
                continue
        
        # 3. MÉTRICAS CRÍTICAS (sensores em estado crítico/warning)
        critical_sensors = []
        
        for server in servers:
            sensors = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.is_active == True
            ).all()
            
            for sensor in sensors:
                last_metric = db.query(Metric).filter(
                    Metric.sensor_id == sensor.id
                ).order_by(Metric.timestamp.desc()).first()
                
                if last_metric and last_metric.status in ['warning', 'critical']:
                    critical_sensors.append({
                        'server_id': server.id,
                        'server_name': server.hostname,
                        'sensor_id': sensor.id,
                        'sensor_name': sensor.name,
                        'sensor_type': sensor.sensor_type,
                        'value': last_metric.value,
                        'unit': last_metric.unit,
                        'status': last_metric.status,
                        'threshold_warning': sensor.threshold_warning,
                        'threshold_critical': sensor.threshold_critical,
                        'timestamp': last_metric.timestamp.isoformat()
                    })
        
        # 4. KPIs
        # MTTR - Mean Time To Repair
        if current_user.role == 'admin':
            resolved_incidents = db.query(Incident).join(Sensor).join(Server).filter(
                Incident.resolved_at.isnot(None),
                Incident.created_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
        else:
            resolved_incidents = db.query(Incident).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Incident.resolved_at.isnot(None),
                Incident.created_at >= datetime.utcnow() - timedelta(days=30)
            ).all()
        
        if resolved_incidents:
            total_resolution_time = sum([
                (inc.resolved_at - inc.created_at).total_seconds() / 60
                for inc in resolved_incidents
            ])
            mttr = int(total_resolution_time / len(resolved_incidents))
        else:
            mttr = 0
        
        # SLA
        if current_user.role == 'admin':
            total_metrics_30d = db.query(Metric).join(Sensor).join(Server).filter(
                Metric.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            ok_metrics_30d = db.query(Metric).join(Sensor).join(Server).filter(
                Metric.status == 'ok',
                Metric.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).count()
        else:
            total_metrics_30d = db.query(Metric).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Metric.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            ok_metrics_30d = db.query(Metric).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Metric.status == 'ok',
                Metric.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).count()
        
        sla = (ok_metrics_30d / total_metrics_30d * 100) if total_metrics_30d > 0 else 100
        
        # Incidentes por período
        if current_user.role == 'admin':
            incidents_24h = db.query(Incident).join(Sensor).join(Server).filter(
                Incident.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            incidents_7d = db.query(Incident).join(Sensor).join(Server).filter(
                Incident.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        else:
            incidents_24h = db.query(Incident).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Incident.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            incidents_7d = db.query(Incident).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Incident.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        
        # 5. EMPRESAS (se admin)
        companies = []
        if current_user.role == 'admin':
            tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
            for tenant in tenants:
                tenant_servers = db.query(Server).filter(
                    Server.tenant_id == tenant.id,
                    Server.is_active == True
                ).count()
                
                if tenant_servers == 0:
                    continue
                
                # Contar incidentes ativos
                tenant_critical = db.query(Incident).join(Sensor).join(Server).filter(
                    Server.tenant_id == tenant.id,
                    Incident.status.in_(['open', 'acknowledged']),
                    Incident.severity == 'critical'
                ).count()
                
                tenant_warning = db.query(Incident).join(Sensor).join(Server).filter(
                    Server.tenant_id == tenant.id,
                    Incident.status.in_(['open', 'acknowledged']),
                    Incident.severity == 'warning'
                ).count()
                
                # Status geral
                if tenant_critical > 0:
                    tenant_status = 'critical'
                elif tenant_warning > 0:
                    tenant_status = 'warning'
                else:
                    tenant_status = 'ok'
                
                companies.append({
                    'id': tenant.id,
                    'name': tenant.name,
                    'servers': tenant_servers,
                    'critical_incidents': tenant_critical,
                    'warning_incidents': tenant_warning,
                    'status': tenant_status
                })
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'servers_ok': servers_ok,
                'servers_warning': servers_warning,
                'servers_critical': servers_critical,
                'servers_offline': servers_offline,
                'total_servers': len(servers),
                'total_incidents': len(incidents_data),
                'critical_incidents': len([i for i in incidents_data if i['severity'] == 'critical']),
                'warning_incidents': len([i for i in incidents_data if i['severity'] == 'warning'])
            },
            'servers': servers_data,
            'incidents': incidents_data,
            'critical_sensors': critical_sensors,
            'kpis': {
                'mttr': mttr,
                'sla': round(sla, 2),
                'incidents_24h': incidents_24h,
                'incidents_7d': incidents_7d,
                'resolved_30d': len(resolved_incidents)
            },
            'companies': companies
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar dashboard em tempo real: {e}", exc_info=True)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "degraded",
            "message": f"NOC data temporarily unavailable: {str(e)}",
            "summary": {
                "servers_ok": 0, "servers_warning": 0, "servers_critical": 0,
                "servers_offline": 0, "total_servers": 0,
                "total_incidents": 0, "critical_incidents": 0, "warning_incidents": 0
            },
            "servers": [],
            "incidents": [],
            "critical_sensors": [],
            "kpis": {"mttr": 0, "sla": 100.0, "incidents_24h": 0, "incidents_7d": 0, "resolved_30d": 0},
            "companies": []
        }


@router.get("/realtime/events")
async def get_recent_events(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Eventos recentes do sistema (incidentes criados, resolvidos, reconhecidos)
    """
    try:
        if current_user.role == 'admin':
            incidents = db.query(Incident).join(Sensor).join(Server).order_by(
                desc(Incident.created_at)
            ).limit(limit).all()
        else:
            incidents = db.query(Incident).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id
            ).order_by(desc(Incident.created_at)).limit(limit).all()
        
        events = []
        for incident in incidents:
            # Evento de criação
            events.append({
                'id': f"incident_{incident.id}_created",
                'type': 'incident_created',
                'severity': incident.severity,
                'server_name': incident.sensor.server.hostname,
                'sensor_name': incident.sensor.name,
                'description': incident.title,
                'timestamp': incident.created_at.isoformat()
            })
            
            # Evento de reconhecimento
            if incident.acknowledged_at:
                events.append({
                    'id': f"incident_{incident.id}_acknowledged",
                    'type': 'incident_acknowledged',
                    'severity': incident.severity,
                    'server_name': incident.sensor.server.hostname,
                    'sensor_name': incident.sensor.name,
                    'description': f"Incidente reconhecido",
                    'timestamp': incident.acknowledged_at.isoformat()
                })
            
            # Evento de resolução
            if incident.resolved_at:
                events.append({
                    'id': f"incident_{incident.id}_resolved",
                    'type': 'incident_resolved',
                    'severity': incident.severity,
                    'server_name': incident.sensor.server.hostname,
                    'sensor_name': incident.sensor.name,
                    'description': f"Incidente resolvido",
                    'timestamp': incident.resolved_at.isoformat()
                })
        
        # Ordenar por timestamp
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return events[:limit]
        
    except Exception as e:
        logger.error(f"Erro ao buscar eventos: {e}")
        return []


async def broadcast_noc_update(event_type: str, data: dict):
    """
    Função auxiliar para enviar atualizações via WebSocket
    Deve ser chamada quando houver mudanças no sistema
    """
    message = {
        'type': event_type,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    await manager.broadcast(message)
