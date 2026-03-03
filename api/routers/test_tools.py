"""
Test Tools Router - Ferramentas para testar alertas e notificações
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from database import get_db
from models import Sensor, Metric, Incident, User, Server
from auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)

class SimulateFailureRequest(BaseModel):
    sensor_id: int
    failure_type: str  # 'critical', 'warning'
    value: Optional[float] = None
    duration_minutes: Optional[int] = 5

@router.post("/simulate-failure")
async def simulate_sensor_failure(
    request: SimulateFailureRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Simula uma falha em um sensor para testar alertas e notificações
    Apenas para usuários admin
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem usar esta ferramenta")
    
    try:
        # Buscar sensor
        sensor = db.query(Sensor).filter(Sensor.id == request.sensor_id).first()
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor não encontrado")
        
        # Determinar valor baseado no tipo de falha
        if request.value is not None:
            value = request.value
        else:
            # Valores padrão que acionam alertas
            if request.failure_type == 'critical':
                value = 98.0  # 98% para CPU/Memory/Disk
            elif request.failure_type == 'warning':
                value = 85.0  # 85% para warning
            else:
                raise HTTPException(status_code=400, detail="Tipo de falha inválido. Use 'critical' ou 'warning'")
        
        # Criar métrica com falha
        # Usar getattr para evitar erro se sensor não tiver atributo unit
        sensor_unit = getattr(sensor, 'unit', None) or '%'
        
        metric = Metric(
            sensor_id=sensor.id,
            value=value,
            unit=sensor_unit,
            status=request.failure_type,
            timestamp=datetime.utcnow(),
            extra_metadata={
                'simulated': True,
                'test_mode': True,
                'admin_user': current_user.email
            }
        )
        db.add(metric)
        
        # Criar incidente se não existir
        existing_incident = db.query(Incident).filter(
            Incident.sensor_id == sensor.id,
            Incident.resolved_at.is_(None)
        ).first()
        
        if not existing_incident:
            incident = Incident(
                sensor_id=sensor.id,
                severity=request.failure_type,
                title=f"[TESTE] Falha simulada - {sensor.name}",
                description=f"Falha simulada para teste de alertas. Valor: {value}{sensor_unit}",
                created_at=datetime.utcnow(),
                ai_analysis={
                    'simulated': True,
                    'test_mode': True,
                    'admin_user': current_user.email,
                    'duration_minutes': request.duration_minutes
                }
            )
            db.add(incident)
        
        db.commit()
        
        logger.info(f"Falha simulada criada pelo admin {current_user.email} no sensor {sensor.id}")
        
        return {
            'success': True,
            'message': f'Falha {request.failure_type} simulada com sucesso',
            'sensor_id': sensor.id,
            'sensor_name': sensor.name,
            'value': value,
            'status': request.failure_type,
            'incident_created': not existing_incident,
            'duration_minutes': request.duration_minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao simular falha: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-simulated-failures")
async def clear_simulated_failures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove todas as falhas simuladas e incidentes de teste
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem usar esta ferramenta")
    
    try:
        # Buscar e remover métricas simuladas (filtrar em Python)
        all_metrics = db.query(Metric).all()
        metrics_deleted = 0
        for metric in all_metrics:
            if metric.extra_metadata and isinstance(metric.extra_metadata, dict) and metric.extra_metadata.get('simulated'):
                db.delete(metric)
                metrics_deleted += 1
        
        # Resolver incidentes simulados (filtrar em Python)
        all_incidents = db.query(Incident).filter(
            Incident.resolved_at.is_(None)
        ).all()
        
        incidents_resolved = []
        for incident in all_incidents:
            if incident.ai_analysis and isinstance(incident.ai_analysis, dict) and incident.ai_analysis.get('simulated'):
                incident.resolved_at = datetime.utcnow()
                incident.resolution_notes = "Teste finalizado - incidente simulado resolvido automaticamente"
                incidents_resolved.append(incident)
        
        db.commit()
        
        logger.info(f"Falhas simuladas limpas pelo admin {current_user.email}")
        
        return {
            'success': True,
            'message': 'Falhas simuladas removidas com sucesso',
            'metrics_deleted': metrics_deleted,
            'incidents_resolved': len(incidents_resolved)
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar falhas simuladas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulated-failures")
async def list_simulated_failures(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todas as falhas simuladas ativas
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Apenas administradores podem usar esta ferramenta")
    
    try:
        # Buscar todos os incidentes ativos e filtrar em Python
        incidents = db.query(Incident).join(Sensor).join(Server).filter(
            Incident.resolved_at.is_(None)
        ).all()
        
        logger.info(f"Total de incidentes ativos encontrados: {len(incidents)}")
        
        result = []
        for incident in incidents:
            logger.info(f"Incidente {incident.id}: ai_analysis={incident.ai_analysis}, type={type(incident.ai_analysis)}")
            
            # Verificar se é simulado através do ai_analysis
            if incident.ai_analysis and isinstance(incident.ai_analysis, dict) and incident.ai_analysis.get('simulated'):
                logger.info(f"Incidente {incident.id} é simulado, adicionando à lista")
                result.append({
                    'id': incident.id,
                    'sensor_id': incident.sensor_id,
                    'sensor_name': incident.sensor.name,
                    'server_name': incident.sensor.server.hostname,
                    'severity': incident.severity,
                    'title': incident.title,
                    'created_at': incident.created_at.isoformat(),
                    'duration_minutes': incident.ai_analysis.get('duration_minutes', 5)
                })
        
        logger.info(f"Total de falhas simuladas retornadas: {len(result)}")
        
        return {
            'success': True,
            'count': len(result),
            'failures': result
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar falhas simuladas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
