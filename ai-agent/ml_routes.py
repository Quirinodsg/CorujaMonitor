"""
ML Engine Routes
Endpoints para funcionalidades de Machine Learning
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from ml_engine import MLEngine

router = APIRouter()
logger = logging.getLogger(__name__)

# Instância global do ML Engine
ml_engine = MLEngine()

class MetricsRequest(BaseModel):
    metrics: List[Dict[str, Any]]

class CapacityRequest(BaseModel):
    metrics: List[Dict[str, Any]]
    days_ahead: int = 30

class ServerMetricsRequest(BaseModel):
    server_metrics: Dict[str, List[Dict[str, Any]]]

@router.post("/detect-anomalies")
async def detect_anomalies(request: MetricsRequest):
    """
    Detecta anomalias em métricas usando Isolation Forest
    """
    try:
        anomalies = ml_engine.detect_anomalies(request.metrics)
        return {
            'status': 'success',
            'anomalies': anomalies,
            'total_analyzed': len(request.metrics),
            'anomalies_found': len(anomalies)
        }
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-capacity")
async def predict_capacity(request: CapacityRequest):
    """
    Prevê capacidade futura usando regressão
    """
    try:
        prediction = ml_engine.predict_capacity(
            request.metrics,
            request.days_ahead
        )
        return prediction
    except Exception as e:
        logger.error(f"Error predicting capacity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-baseline")
async def calculate_baseline(request: MetricsRequest):
    """
    Calcula baseline dinâmico para métricas
    """
    try:
        baseline = ml_engine.calculate_baseline(request.metrics)
        if baseline:
            return {
                'status': 'success',
                'baseline': baseline
            }
        else:
            return {
                'status': 'insufficient_data',
                'message': 'Dados insuficientes para calcular baseline'
            }
    except Exception as e:
        logger.error(f"Error calculating baseline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preventive-recommendations")
async def preventive_recommendations(request: ServerMetricsRequest):
    """
    Gera recomendações preventivas baseadas em métricas
    """
    try:
        recommendations = ml_engine.generate_preventive_recommendations(
            request.server_metrics
        )
        return {
            'status': 'success',
            'recommendations': recommendations,
            'count': len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check do ML Engine
    """
    return {
        'status': 'healthy',
        'service': 'ml-engine',
        'version': '1.0.0'
    }
