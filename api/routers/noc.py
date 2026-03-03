"""
NOC (Network Operations Center) Router
Endpoints para modo NOC com dados em tempo real
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from database import get_db
from models import Server, Sensor, Metric, Incident, User, Tenant
from auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/global-status")
async def get_global_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Status global do sistema para NOC
    """
    try:
        # Se admin, mostra todos os servidores; senão, filtra por tenant
        if current_user.role == 'admin':
            servers = db.query(Server).all()
            total_servers = len(servers)
        else:
            servers = db.query(Server).filter(
                Server.tenant_id == current_user.tenant_id
            ).all()
            total_servers = len(servers)
        
        # Servidores por status (baseado em sensores)
        servers_ok = 0
        servers_warning = 0
        servers_critical = 0
        
        for server in servers:
            # Verificar se há incidentes ativos (críticos ou avisos) para este servidor
            # Incluir tanto 'open' quanto 'acknowledged'
            critical_incident = db.query(Incident).join(Sensor).filter(
                Sensor.server_id == server.id,
                Incident.status.in_(['open', 'acknowledged']),
                Incident.severity == 'critical'
            ).first()
            
            warning_incident = db.query(Incident).join(Sensor).filter(
                Sensor.server_id == server.id,
                Incident.status.in_(['open', 'acknowledged']),
                Incident.severity == 'warning'
            ).first()
            
            # Se há incidente crítico, servidor é crítico
            if critical_incident:
                servers_critical += 1
            # Se há incidente de aviso, servidor está em aviso
            elif warning_incident:
                servers_warning += 1
            else:
                servers_ok += 1
        
        # Disponibilidade geral
        if current_user.role == 'admin':
            total_metrics = db.query(Metric).join(Sensor).join(Server).filter(
                Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            ok_metrics = db.query(Metric).join(Sensor).join(Server).filter(
                Metric.status == 'ok',
                Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).count()
        else:
            total_metrics = db.query(Metric).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            ok_metrics = db.query(Metric).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Metric.status == 'ok',
                Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
            ).count()
        
        availability = (ok_metrics / total_metrics * 100) if total_metrics > 0 else 100
        
        # Status por empresa (se admin)
        companies = []
        if current_user.role == 'admin':
            tenants = db.query(Tenant).all()
            for tenant in tenants:
                tenant_servers = db.query(Server).filter(
                    Server.tenant_id == tenant.id
                ).count()
                
                # Pular empresas sem servidores
                if tenant_servers == 0:
                    continue
                
                # Calcular status da empresa
                tenant_ok = 0
                tenant_warning = 0
                tenant_critical = 0
                
                for server in db.query(Server).filter(Server.tenant_id == tenant.id).all():
                    # Verificar incidentes ativos primeiro (open OU acknowledged)
                    critical_incident = db.query(Incident).join(Sensor).filter(
                        Sensor.server_id == server.id,
                        Incident.status.in_(['open', 'acknowledged']),
                        Incident.severity == 'critical'
                    ).first()
                    
                    warning_incident = db.query(Incident).join(Sensor).filter(
                        Sensor.server_id == server.id,
                        Incident.status.in_(['open', 'acknowledged']),
                        Incident.severity == 'warning'
                    ).first()
                    
                    if critical_incident:
                        tenant_critical += 1
                    elif warning_incident:
                        tenant_warning += 1
                    else:
                        tenant_ok += 1
                
                # Status geral da empresa
                company_status = 'ok'
                if tenant_critical > 0:
                    company_status = 'critical'
                elif tenant_warning > 0:
                    company_status = 'warning'
                
                # Disponibilidade da empresa
                company_availability = 99.9  # Simplificado
                
                companies.append({
                    'id': tenant.id,
                    'name': tenant.name,
                    'ok': tenant_ok,
                    'warning': tenant_warning,
                    'critical': tenant_critical,
                    'status': company_status,
                    'availability': round(company_availability, 2)
                })
        
        return {
            'servers_ok': servers_ok,
            'servers_warning': servers_warning,
            'servers_critical': servers_critical,
            'total_servers': total_servers,
            'availability': round(availability, 2),
            'companies': companies,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting global status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap")
async def get_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mapa de calor de disponibilidade dos servidores
    Mostra TODOS os servidores, independente de terem incidentes
    """
    try:
        # Se admin, mostra todos; senão, filtra por tenant
        if current_user.role == 'admin':
            servers = db.query(Server).filter(Server.is_active == True).all()
        else:
            servers = db.query(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Server.is_active == True
            ).all()
        
        heatmap = []
        
        for server in servers:
            # Verificar se há incidentes ativos (críticos ou avisos)
            critical_incident = db.query(Incident).join(Sensor).filter(
                Sensor.server_id == server.id,
                Incident.status.in_(['open', 'acknowledged']),
                Incident.severity == 'critical'
            ).first()
            
            warning_incident = db.query(Incident).join(Sensor).filter(
                Sensor.server_id == server.id,
                Incident.status.in_(['open', 'acknowledged']),
                Incident.severity == 'warning'
            ).first()
            
            # Determinar status baseado em incidentes ativos
            if critical_incident:
                status = 'critical'
                availability = 50.0  # Servidor crítico
            elif warning_incident:
                status = 'warning'
                availability = 85.0  # Servidor em aviso
            else:
                # Calcular disponibilidade real (últimas 24h)
                total = db.query(Metric).join(Sensor).filter(
                    Sensor.server_id == server.id,
                    Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                ok_count = db.query(Metric).join(Sensor).filter(
                    Sensor.server_id == server.id,
                    Metric.status == 'ok',
                    Metric.timestamp >= datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                availability = (ok_count / total * 100) if total > 0 else 100
                
                # Determinar status baseado em disponibilidade
                if availability >= 95:
                    status = 'ok'
                elif availability >= 90:
                    status = 'warning'
                else:
                    status = 'critical'
            
            heatmap.append({
                'id': server.id,
                'hostname': server.hostname,
                'ip_address': server.ip_address,
                'availability': round(availability, 1),
                'status': status
            })
        
        return heatmap
        
    except Exception as e:
        logger.error(f"Error getting heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-incidents")
async def get_active_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Incidentes ativos para ticker do NOC
    Busca incidentes com status 'open' ou 'acknowledged' (não resolvidos)
    """
    try:
        # Se admin, mostra todos; senão, filtra por tenant
        if current_user.role == 'admin':
            incidents = db.query(Incident).join(Sensor).join(Server).filter(
                Incident.status.in_(['open', 'acknowledged'])
            ).order_by(desc(Incident.created_at)).limit(50).all()
        else:
            incidents = db.query(Incident).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Incident.status.in_(['open', 'acknowledged'])
            ).order_by(desc(Incident.created_at)).limit(50).all()
        
        result = []
        for incident in incidents:
            # Fix timezone: ensure both datetimes are naive (no timezone)
            now = datetime.utcnow()
            created_at = incident.created_at
            
            # If created_at is timezone-aware, make it naive
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
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting active incidents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis")
async def get_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    KPIs consolidados para NOC
    """
    try:
        # MTTR - Mean Time To Repair (tempo médio de resolução)
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
        
        # MTBF - Mean Time Between Failures (tempo médio entre falhas)
        mtbf = 720  # Simplificado - 30 dias em horas
        
        # SLA - Service Level Agreement
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
        
        # Incidentes 24h
        if current_user.role == 'admin':
            incidents_24h = db.query(Incident).join(Sensor).join(Server).filter(
                Incident.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
        else:
            incidents_24h = db.query(Incident).join(Sensor).join(Server).filter(
                Server.tenant_id == current_user.tenant_id,
                Incident.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
        
        return {
            'mttr': mttr,
            'mtbf': mtbf,
            'sla': round(sla, 2),
            'incidents_24h': incidents_24h
        }
        
    except Exception as e:
        logger.error(f"Error getting KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
