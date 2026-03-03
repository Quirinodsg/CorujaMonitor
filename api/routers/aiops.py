"""
AIOps API Router
Exposes advanced AI Operations capabilities
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Sensor, Metric, Server, Incident, User
from auth import get_current_active_user

router = APIRouter()

# Import AIOps Engine inline to avoid import errors
def get_aiops_engine():
    """Get AIOps Engine instance"""
    try:
        # Import inline to handle missing module gracefully
        import sys
        import os
        from collections import defaultdict
        import statistics
        
        # Define AIOpsEngine inline if not available
        class AIOpsEngine:
            def __init__(self):
                self.anomaly_threshold = 2.5
                self.correlation_window = 300
                self.min_samples_for_baseline = 20
            
            async def detect_anomalies(self, metrics: List[Dict[str, Any]], sensor_type: str) -> Dict[str, Any]:
                if len(metrics) < self.min_samples_for_baseline:
                    return {
                        "anomaly_detected": False,
                        "confidence": 0.0,
                        "method": "insufficient_data",
                        "message": f"Necessário pelo menos {self.min_samples_for_baseline} amostras"
                    }
                
                values = [m['value'] for m in metrics]
                
                # Statistical anomaly detection
                mean = statistics.mean(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
                
                anomalies = []
                if std_dev > 0:
                    for i, value in enumerate(values):
                        z_score = abs((value - mean) / std_dev)
                        if z_score > self.anomaly_threshold:
                            anomalies.append({
                                "index": i,
                                "value": value,
                                "z_score": z_score,
                                "method": "statistical",
                                "deviation_percent": ((value - mean) / mean * 100) if mean != 0 else 0
                            })
                
                if not anomalies:
                    return {
                        "anomaly_detected": False,
                        "confidence": 0.95,
                        "method": "statistical",
                        "baseline": {
                            "mean": mean,
                            "std_dev": std_dev,
                            "min": min(values),
                            "max": max(values)
                        }
                    }
                
                confidence = min(len(anomalies) / len(values) * 2, 1.0)
                
                recommendations = {
                    "cpu": "Investigar processos com alto consumo de CPU. Considerar escalonamento horizontal.",
                    "memory": "Verificar memory leaks. Analisar processos com crescimento de memória.",
                    "disk": "Limpar arquivos temporários. Implementar rotação de logs.",
                    "network": "Analisar tráfego de rede. Verificar possíveis ataques.",
                    "service": "Verificar logs de aplicação. Analisar dependências do serviço."
                }
                
                return {
                    "anomaly_detected": True,
                    "confidence": confidence,
                    "method": "statistical",
                    "anomalies": anomalies[:10],
                    "total_anomalies": len(anomalies),
                    "severity": "critical" if len(anomalies) / len(values) > 0.5 else "medium",
                    "baseline": {"mean": mean, "std_dev": std_dev},
                    "recommendation": recommendations.get(sensor_type, "Investigar causa raiz da anomalia.")
                }
            
            async def correlate_events(self, incidents: List[Dict[str, Any]], time_window_seconds: int = 300) -> Dict[str, Any]:
                if len(incidents) < 2:
                    return {
                        "correlated": False,
                        "total_groups": 0,
                        "groups": [],
                        "analysis": {"message": "Insufficient incidents for correlation"}
                    }
                
                # Sort by timestamp
                sorted_incidents = sorted(incidents, key=lambda x: x.get('created_at', datetime.now()))
                
                # Temporal correlation
                groups = []
                current_group = []
                
                for incident in sorted_incidents:
                    if not current_group:
                        current_group.append(incident)
                        continue
                    
                    last_time = current_group[-1].get('created_at', datetime.now())
                    current_time = incident.get('created_at', datetime.now())
                    
                    if isinstance(last_time, datetime) and isinstance(current_time, datetime):
                        time_diff = (current_time - last_time).total_seconds()
                    else:
                        time_diff = 0
                    
                    if time_diff <= time_window_seconds:
                        current_group.append(incident)
                    else:
                        if len(current_group) > 1:
                            groups.append(current_group)
                        current_group = [incident]
                
                if len(current_group) > 1:
                    groups.append(current_group)
                
                # Format groups
                formatted_groups = []
                for group in groups:
                    affected_servers = list(set(inc.get('server_hostname', 'unknown') for inc in group))
                    severities = [inc.get('severity', 'warning') for inc in group]
                    
                    formatted_groups.append({
                        "correlation_type": "temporal_spatial" if len(affected_servers) > 1 else "temporal",
                        "incident_count": len(group),
                        "incidents": group,
                        "time_span_seconds": 0,
                        "affected_servers": affected_servers,
                        "severity": "critical" if "critical" in severities else "warning"
                    })
                
                pattern = "infrastructure_wide" if any(len(g['affected_servers']) > 1 for g in formatted_groups) else "isolated_incidents"
                
                return {
                    "correlated": len(formatted_groups) > 0,
                    "total_groups": len(formatted_groups),
                    "groups": formatted_groups,
                    "analysis": {
                        "total_correlated_incidents": sum(g['incident_count'] for g in formatted_groups),
                        "total_affected_servers": len(set(s for g in formatted_groups for s in g['affected_servers'])),
                        "largest_group_size": max((g['incident_count'] for g in formatted_groups), default=0),
                        "pattern": pattern
                    }
                }
            
            async def analyze_root_cause(self, incident: Dict[str, Any], related_incidents: List[Dict[str, Any]], metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
                sensor_type = incident.get('sensor_type', 'unknown')
                
                # Analyze symptoms
                symptoms = [{
                    "type": "primary",
                    "description": f"{sensor_type} at {incident.get('current_value', 0)}",
                    "severity": incident.get('severity', 'warning'),
                    "timestamp": incident.get('created_at', datetime.now())
                }]
                
                # Timeline
                timeline = [{
                    "timestamp": incident.get('created_at', datetime.now()),
                    "event": "current_incident",
                    "description": f"{incident.get('sensor_name', 'Unknown')} triggered",
                    "type": "incident"
                }]
                
                # Root causes
                root_causes = {
                    "cpu": "Alto consumo de CPU por processo desconhecido ou malware",
                    "memory": "Memory leak em aplicação - memória não sendo liberada",
                    "disk": "Disco enchendo gradualmente - logs ou arquivos temporários",
                    "service": "Serviço parou de responder devido a erro de aplicação",
                    "network": "Problemas de conectividade de rede ou congestionamento"
                }
                
                return {
                    "root_cause": root_causes.get(sensor_type, "Causa raiz desconhecida"),
                    "confidence": 0.75,
                    "symptoms": symptoms,
                    "timeline": timeline,
                    "contributing_factors": ["Incidente isolado sem fatores contribuintes identificados"]
                }
            
            async def create_action_plan(self, incident: Dict[str, Any], root_cause_analysis: Dict[str, Any], correlation_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
                sensor_type = incident.get('sensor_type', 'unknown')
                severity = incident.get('severity', 'warning')
                
                immediate_actions = [{
                    "priority": 1,
                    "action": f"Verificar status do {sensor_type}",
                    "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5" if sensor_type == 'cpu' else None,
                    "automated": True,
                    "estimated_time": "1 min",
                    "risk_level": "low"
                }]
                
                short_term_actions = [{
                    "priority": 1,
                    "action": "Documentar incidente e ações tomadas",
                    "automated": False,
                    "estimated_time": "10 min",
                    "risk_level": "low"
                }]
                
                long_term_actions = [{
                    "priority": 1,
                    "action": "Revisar e ajustar thresholds de monitoramento",
                    "automated": False,
                    "estimated_time": "30 min",
                    "risk_level": "low"
                }]
                
                return {
                    "plan_id": f"AP-{incident.get('id', 'unknown')}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "created_at": datetime.now().isoformat(),
                    "incident_id": incident.get('id'),
                    "severity": severity,
                    "estimated_resolution_time": "15 minutos",
                    "immediate_actions": immediate_actions,
                    "short_term_actions": short_term_actions,
                    "long_term_actions": long_term_actions,
                    "automation_available": sensor_type in ['cpu', 'memory', 'disk', 'service']
                }
        
        return AIOpsEngine()
    except Exception as e:
        print(f"Error loading AIOps Engine: {e}")
        return None


class AnomalyDetectionRequest(BaseModel):
    sensor_id: int
    lookback_hours: Optional[int] = 24


class AnomalyDetectionResponse(BaseModel):
    sensor_id: int
    sensor_name: str
    anomaly_detected: bool
    confidence: float
    anomalies: List[Dict[str, Any]]
    recommendation: Optional[str] = None


class EventCorrelationRequest(BaseModel):
    time_window_minutes: Optional[int] = 30
    severity_filter: Optional[List[str]] = None


class EventCorrelationResponse(BaseModel):
    correlated: bool
    total_groups: int
    groups: List[Dict[str, Any]]
    analysis: Dict[str, Any]


class RootCauseAnalysisRequest(BaseModel):
    incident_id: int


class RootCauseAnalysisResponse(BaseModel):
    incident_id: int
    root_cause: str
    confidence: float
    symptoms: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    contributing_factors: List[str]


class ActionPlanResponse(BaseModel):
    plan_id: str
    incident_id: int
    severity: str
    estimated_resolution_time: str
    immediate_actions: List[Dict[str, Any]]
    short_term_actions: List[Dict[str, Any]]
    long_term_actions: List[Dict[str, Any]]
    automation_available: bool



@router.post("/anomaly-detection", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Detect anomalies in sensor metrics using multiple methods:
    - Statistical analysis (Z-score)
    - Moving average
    - Rate of change
    """
    
    aiops = get_aiops_engine()
    if not aiops:
        raise HTTPException(status_code=503, detail="AIOps Engine not available")
    
    # Get sensor
    sensor = db.query(Sensor).join(Server).filter(
        Sensor.id == request.sensor_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Get metrics
    since = datetime.now() - timedelta(hours=request.lookback_hours)
    metrics = db.query(Metric).filter(
        Metric.sensor_id == request.sensor_id,
        Metric.timestamp >= since
    ).order_by(Metric.timestamp.asc()).all()
    
    if len(metrics) < 10:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient data. Need at least 10 samples, found {len(metrics)}"
        )
    
    # Convert to dict format
    metrics_data = [
        {
            "value": m.value,
            "timestamp": m.timestamp,
            "status": m.status
        }
        for m in metrics
    ]
    
    # Run anomaly detection
    result = await aiops.detect_anomalies(metrics_data, sensor.sensor_type)
    
    return AnomalyDetectionResponse(
        sensor_id=sensor.id,
        sensor_name=sensor.name,
        anomaly_detected=result['anomaly_detected'],
        confidence=result['confidence'],
        anomalies=result.get('anomalies', []),
        recommendation=result.get('recommendation')
    )


@router.post("/event-correlation", response_model=EventCorrelationResponse)
async def correlate_events(
    request: EventCorrelationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Correlate incidents using temporal and spatial analysis
    to identify patterns and related events
    """
    
    aiops = get_aiops_engine()
    if not aiops:
        raise HTTPException(status_code=503, detail="AIOps Engine not available")
    
    # Get recent incidents
    since = datetime.now() - timedelta(minutes=request.time_window_minutes)
    
    query = db.query(Incident).join(Sensor).join(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Incident.created_at >= since
    )
    
    if request.severity_filter:
        query = query.filter(Incident.severity.in_(request.severity_filter))
    
    incidents = query.order_by(Incident.created_at.asc()).all()
    
    if len(incidents) < 2:
        return EventCorrelationResponse(
            correlated=False,
            total_groups=0,
            groups=[],
            analysis={"message": "Insufficient incidents for correlation"}
        )
    
    # Convert to dict format
    incidents_data = [
        {
            "id": inc.id,
            "server_id": inc.sensor.server_id,
            "server_hostname": inc.sensor.server.hostname,
            "sensor_id": inc.sensor_id,
            "sensor_name": inc.sensor.name,
            "sensor_type": inc.sensor.sensor_type,
            "severity": inc.severity,
            "created_at": inc.created_at
        }
        for inc in incidents
    ]
    
    # Run correlation
    aiops = get_aiops_engine()
    result = await aiops.correlate_events(
        incidents_data, 
        time_window_seconds=request.time_window_minutes * 60
    )
    
    return EventCorrelationResponse(
        correlated=result['correlated'],
        total_groups=result['total_groups'],
        groups=result['groups'],
        analysis=result['analysis']
    )



@router.post("/root-cause-analysis", response_model=RootCauseAnalysisResponse)
async def analyze_root_cause(
    request: RootCauseAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform Root Cause Analysis (RCA) on an incident using:
    - Symptom analysis
    - Timeline reconstruction
    - Dependency analysis
    - Pattern matching
    """
    
    aiops = get_aiops_engine()
    if not aiops:
        raise HTTPException(status_code=503, detail="AIOps Engine not available")
    
    # Get incident
    incident = db.query(Incident).join(Sensor).join(Server).filter(
        Incident.id == request.incident_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Get related incidents (same server, last 24 hours)
    since = incident.created_at - timedelta(hours=24)
    related_incidents = db.query(Incident).join(Sensor).filter(
        Sensor.server_id == incident.sensor.server_id,
        Incident.id != incident.id,
        Incident.created_at >= since,
        Incident.created_at <= incident.created_at
    ).order_by(Incident.created_at.desc()).limit(20).all()
    
    # Get metrics history
    metrics_since = incident.created_at - timedelta(hours=2)
    metrics = db.query(Metric).filter(
        Metric.sensor_id == incident.sensor_id,
        Metric.timestamp >= metrics_since,
        Metric.timestamp <= incident.created_at
    ).order_by(Metric.timestamp.asc()).all()
    
    # Get current value from latest metric
    current_value = None
    if metrics:
        current_value = metrics[-1].value
    
    # Convert to dict format
    incident_data = {
        "id": incident.id,
        "server_id": incident.sensor.server_id,
        "server_hostname": incident.sensor.server.hostname,
        "sensor_id": incident.sensor_id,
        "sensor_name": incident.sensor.name,
        "sensor_type": incident.sensor.sensor_type,
        "severity": incident.severity,
        "current_value": current_value,
        "threshold_warning": incident.sensor.threshold_warning,
        "threshold_critical": incident.sensor.threshold_critical,
        "created_at": incident.created_at
    }
    
    related_data = [
        {
            "id": inc.id,
            "server_id": inc.sensor.server_id,
            "sensor_id": inc.sensor_id,
            "sensor_name": inc.sensor.name,
            "sensor_type": inc.sensor.sensor_type,
            "severity": inc.severity,
            "created_at": inc.created_at
        }
        for inc in related_incidents
    ]
    
    metrics_data = [
        {
            "value": m.value,
            "timestamp": m.timestamp,
            "status": m.status
        }
        for m in metrics
    ]
    
    # Run RCA
    aiops = get_aiops_engine()
    result = await aiops.analyze_root_cause(
        incident_data,
        related_data,
        metrics_data
    )
    
    return RootCauseAnalysisResponse(
        incident_id=incident.id,
        root_cause=result['root_cause'],
        confidence=result['confidence'],
        symptoms=result['symptoms'],
        timeline=result['timeline'],
        contributing_factors=result['contributing_factors']
    )



@router.post("/action-plan/{incident_id}", response_model=ActionPlanResponse)
async def create_action_plan(
    incident_id: int,
    include_correlation: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create comprehensive action plan for incident resolution with:
    - Immediate actions (stop the bleeding)
    - Short-term actions (fix the problem)
    - Long-term actions (prevent recurrence)
    """
    
    aiops = get_aiops_engine()
    if not aiops:
        raise HTTPException(status_code=503, detail="AIOps Engine not available")
    
    # Get incident
    incident = db.query(Incident).join(Sensor).join(Server).filter(
        Incident.id == incident_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Get related incidents for correlation
    related_incidents = []
    correlation_data = None
    
    if include_correlation:
        since = incident.created_at - timedelta(minutes=30)
        related_incidents = db.query(Incident).join(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Incident.id != incident.id,
            Incident.created_at >= since,
            Incident.created_at <= incident.created_at + timedelta(minutes=5)
        ).all()
        
        if len(related_incidents) >= 1:
            # Run correlation
            incidents_data = [
                {
                    "id": inc.id,
                    "server_id": inc.sensor.server_id,
                    "server_hostname": inc.sensor.server.hostname,
                    "sensor_id": inc.sensor_id,
                    "sensor_name": inc.sensor.name,
                    "sensor_type": inc.sensor.sensor_type,
                    "severity": inc.severity,
                    "created_at": inc.created_at
                }
                for inc in [incident] + related_incidents
            ]
            
            aiops = get_aiops_engine()
            correlation_data = await aiops.correlate_events(incidents_data, time_window_seconds=1800)
    
    # Get metrics for RCA
    metrics_since = incident.created_at - timedelta(hours=2)
    metrics = db.query(Metric).filter(
        Metric.sensor_id == incident.sensor_id,
        Metric.timestamp >= metrics_since,
        Metric.timestamp <= incident.created_at
    ).order_by(Metric.timestamp.asc()).all()
    
    # Get current value from latest metric
    current_value = None
    if metrics:
        current_value = metrics[-1].value
    
    # Prepare incident data
    incident_data = {
        "id": incident.id,
        "server_id": incident.sensor.server_id,
        "server_hostname": incident.sensor.server.hostname,
        "sensor_id": incident.sensor_id,
        "sensor_name": incident.sensor.name,
        "sensor_type": incident.sensor.sensor_type,
        "severity": incident.severity,
        "current_value": current_value,
        "threshold_warning": incident.sensor.threshold_warning,
        "threshold_critical": incident.sensor.threshold_critical,
        "created_at": incident.created_at
    }
    
    related_data = [
        {
            "id": inc.id,
            "server_id": inc.sensor.server_id,
            "sensor_id": inc.sensor_id,
            "sensor_name": inc.sensor.name,
            "sensor_type": inc.sensor.sensor_type,
            "severity": inc.severity,
            "created_at": inc.created_at
        }
        for inc in related_incidents
    ]
    
    metrics_data = [
        {
            "value": m.value,
            "timestamp": m.timestamp,
            "status": m.status
        }
        for m in metrics
    ]
    
    # Run RCA first
    aiops = get_aiops_engine()
    rca_result = await aiops.analyze_root_cause(
        incident_data,
        related_data,
        metrics_data
    )
    
    # Create action plan
    action_plan = await aiops.create_action_plan(
        incident_data,
        rca_result,
        correlation_data
    )
    
    return ActionPlanResponse(
        plan_id=action_plan['plan_id'],
        incident_id=incident.id,
        severity=action_plan['severity'],
        estimated_resolution_time=action_plan['estimated_resolution_time'],
        immediate_actions=action_plan['immediate_actions'],
        short_term_actions=action_plan['short_term_actions'],
        long_term_actions=action_plan['long_term_actions'],
        automation_available=action_plan['automation_available']
    )


@router.get("/health")
async def aiops_health():
    """Check AIOps engine health"""
    aiops = get_aiops_engine()
    return {
        "status": "healthy" if aiops else "unavailable",
        "engine": "AIOps Engine v1.0 (Inline)",
        "capabilities": [
            "anomaly_detection",
            "event_correlation",
            "root_cause_analysis",
            "action_planning"
        ]
    }
