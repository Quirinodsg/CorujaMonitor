from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from ai_engine import AIEngine
from config import settings
from ml_routes import router as ml_router

app = FastAPI(
    title="Coruja AI Agent",
    description="AI-powered analysis and recommendations for Coruja Monitor",
    version="1.0.0"
)

ai_engine = AIEngine()

# Include ML routes
app.include_router(ml_router, prefix="/ml", tags=["Machine Learning"])

class RootCauseRequest(BaseModel):
    incident_id: int
    sensor_type: str
    sensor_name: str
    server_hostname: str
    current_value: Optional[float]
    threshold_critical: Optional[float]
    threshold_warning: Optional[float]
    recent_metrics: List[Dict[str, Any]]
    remediation_attempted: bool
    remediation_successful: Optional[bool]

class RootCauseResponse(BaseModel):
    root_cause: str
    analysis: Dict[str, Any]
    recommendations: List[str]

class MonthlySummaryRequest(BaseModel):
    tenant_id: int
    year: int
    month: int
    availability_percentage: float
    total_incidents: int
    auto_resolved_incidents: int
    report_data: Dict[str, Any]

class MonthlySummaryResponse(BaseModel):
    summary: str
    insights: List[str]
    recommendations: List[str]

@app.get("/")
async def root():
    return {"message": "Coruja AI Agent", "status": "operational", "provider": settings.AI_PROVIDER}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/analyze/root-cause", response_model=RootCauseResponse)
async def analyze_root_cause(request: RootCauseRequest):
    """Perform root cause analysis for an incident"""
    result = await ai_engine.analyze_root_cause(request.dict())
    return result

@app.post("/api/v1/analyze/monthly-summary", response_model=MonthlySummaryResponse)
async def generate_monthly_summary(request: MonthlySummaryRequest):
    """Generate AI-powered monthly summary"""
    result = await ai_engine.generate_monthly_summary(request.dict())
    return result

@app.post("/api/v1/analyze/anomaly")
async def detect_anomaly(metrics: List[Dict[str, Any]]):
    """Detect anomalies in metric patterns"""
    result = await ai_engine.detect_anomaly(metrics)
    return result

@app.post("/api/v1/analyze/recommendation")
async def get_recommendations(context: Dict[str, Any]):
    """Get preventive recommendations"""
    result = await ai_engine.get_recommendations(context)
    return result
