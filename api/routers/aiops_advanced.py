"""
AIOps Advanced Router
Endpoints para funcionalidades avançadas de AIOps com ML
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
import logging

from database import get_db
from models import Server, Sensor, Metric, User
from auth import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)

ML_ENGINE_URL = "http://coruja-ai-agent:8001"

@router.get("/anomalies/{sensor_id}")
async def detect_anomalies(
    sensor_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Detecta anomalias em um sensor usando ML
    """
    try:
        # Verificar sensor
        sensor = db.query(Sensor).join(Server).filter(
            Sensor.id == sensor_id,
            Server.tenant_id == current_user.tenant_id
        ).first()
        
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        # Buscar métricas
        since = datetime.utcnow() - timedelta(hours=hours)
        metrics = db.query(Metric).filter(
            Metric.sensor_id == sensor_id,
            Metric.timestamp >= since
        ).order_by(Metric.timestamp).all()
        
        if len(metrics) < 10:
            return {
                'status': 'insufficient_data',
                'message': 'Dados insuficientes para detecção de anomalias',
                'anomalies': []
            }
        
        # Preparar dados para ML
        metrics_data = [
            {
                'timestamp': m.timestamp.isoformat(),
                'value': float(m.value)
            }
            for m in metrics
        ]
        
        # Chamar ML Engine
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ML_ENGINE_URL}/ml/detect-anomalies",
                json={'metrics': metrics_data}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'sensor_id': sensor_id,
                    'sensor_name': sensor.name,
                    'period_hours': hours,
                    'total_metrics': len(metrics),
                    'anomalies': result.get('anomalies', []),
                    'anomaly_count': len(result.get('anomalies', []))
                }
            else:
                logger.error(f"ML Engine error: {response.text}")
                raise HTTPException(status_code=500, detail="ML Engine error")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capacity-forecast/{sensor_id}")
async def forecast_capacity(
    sensor_id: int,
    days_ahead: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Prevê capacidade futura de um sensor
    """
    try:
        # Verificar sensor
        sensor = db.query(Sensor).join(Server).filter(
            Sensor.id == sensor_id,
            Server.tenant_id == current_user.tenant_id
        ).first()
        
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        # Buscar histórico (mínimo 30 dias)
        since = datetime.utcnow() - timedelta(days=60)
        metrics = db.query(Metric).filter(
            Metric.sensor_id == sensor_id,
            Metric.timestamp >= since
        ).order_by(Metric.timestamp).all()
        
        if len(metrics) < 30:
            return {
                'status': 'insufficient_data',
                'message': 'Necessário pelo menos 30 dias de histórico',
                'required_days': 30,
                'current_days': len(metrics) // 24
            }
        
        # Preparar dados
        metrics_data = [
            {
                'timestamp': m.timestamp.isoformat(),
                'value': float(m.value)
            }
            for m in metrics
        ]
        
        # Chamar ML Engine
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{ML_ENGINE_URL}/ml/predict-capacity",
                json={
                    'metrics': metrics_data,
                    'days_ahead': days_ahead
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'sensor_id': sensor_id,
                    'sensor_name': sensor.name,
                    'forecast': result
                }
            else:
                logger.error(f"ML Engine error: {response.text}")
                raise HTTPException(status_code=500, detail="ML Engine error")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error forecasting capacity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/baseline/{sensor_id}")
async def calculate_baseline(
    sensor_id: int,
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calcula baseline dinâmico para um sensor
    """
    try:
        # Verificar sensor
        sensor = db.query(Sensor).join(Server).filter(
            Sensor.id == sensor_id,
            Server.tenant_id == current_user.tenant_id
        ).first()
        
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        # Buscar métricas
        since = datetime.utcnow() - timedelta(days=days)
        metrics = db.query(Metric).filter(
            Metric.sensor_id == sensor_id,
            Metric.timestamp >= since
        ).order_by(Metric.timestamp).all()
        
        if len(metrics) < 7:
            return {
                'status': 'insufficient_data',
                'message': 'Necessário pelo menos 7 dias de dados'
            }
        
        # Preparar dados
        metrics_data = [
            {
                'timestamp': m.timestamp.isoformat(),
                'value': float(m.value)
            }
            for m in metrics
        ]
        
        # Chamar ML Engine
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ML_ENGINE_URL}/ml/calculate-baseline",
                json={'metrics': metrics_data}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'sensor_id': sensor_id,
                    'sensor_name': sensor.name,
                    'period_days': days,
                    'baseline': result
                }
            else:
                logger.error(f"ML Engine error: {response.text}")
                raise HTTPException(status_code=500, detail="ML Engine error")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating baseline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preventive-recommendations/{server_id}")
async def get_preventive_recommendations(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Gera recomendações preventivas para um servidor
    """
    try:
        # Verificar servidor
        server = db.query(Server).filter(
            Server.id == server_id,
            Server.tenant_id == current_user.tenant_id
        ).first()
        
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        
        # Buscar sensores do servidor
        sensors = db.query(Sensor).filter(
            Sensor.server_id == server_id
        ).all()
        
        # Coletar métricas por tipo
        server_metrics = {}
        since = datetime.utcnow() - timedelta(hours=24)
        
        for sensor in sensors:
            metrics = db.query(Metric).filter(
                Metric.sensor_id == sensor.id,
                Metric.timestamp >= since
            ).order_by(Metric.timestamp).all()
            
            if metrics:
                sensor_type = sensor.sensor_type
                if sensor_type not in server_metrics:
                    server_metrics[sensor_type] = []
                
                server_metrics[sensor_type].extend([
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'value': float(m.value)
                    }
                    for m in metrics
                ])
        
        # Chamar ML Engine
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ML_ENGINE_URL}/ml/preventive-recommendations",
                json={'server_metrics': server_metrics}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'server_id': server_id,
                    'server_name': server.hostname,
                    'recommendations': result.get('recommendations', [])
                }
            else:
                logger.error(f"ML Engine error: {response.text}")
                raise HTTPException(status_code=500, detail="ML Engine error")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cloud-cost-analysis")
async def analyze_cloud_costs(
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analisa custos de cloud e detecta desperdícios
    """
    try:
        # Buscar servidores cloud
        cloud_servers = db.query(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Server.tags.contains(['cloud'])
        ).all()
        
        if not cloud_servers:
            return {
                'status': 'no_cloud_servers',
                'message': 'Nenhum servidor cloud encontrado'
            }
        
        # Analisar utilização
        analysis = []
        since = datetime.utcnow() - timedelta(days=days)
        
        for server in cloud_servers:
            # Buscar métricas de CPU e memória
            cpu_sensor = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.sensor_type == 'cpu'
            ).first()
            
            if cpu_sensor:
                avg_cpu = db.query(func.avg(Metric.value)).filter(
                    Metric.sensor_id == cpu_sensor.id,
                    Metric.timestamp >= since
                ).scalar()
                
                if avg_cpu and avg_cpu < 20:
                    analysis.append({
                        'server_id': server.id,
                        'server_name': server.hostname,
                        'issue': 'underutilized',
                        'resource': 'CPU',
                        'avg_usage': float(avg_cpu),
                        'recommendation': 'Considere reduzir o tamanho da instância (downsize)',
                        'potential_savings': '30-50%'
                    })
        
        return {
            'status': 'success',
            'period_days': days,
            'servers_analyzed': len(cloud_servers),
            'issues_found': len(analysis),
            'analysis': analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing cloud costs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
