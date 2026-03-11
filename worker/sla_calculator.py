from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx

from models import MonthlyReport, Incident, Sensor, Server, Metric
from config import settings

def calculate_monthly_sla(db: Session, tenant_id: int, year: int, month: int):
    """Calculate and generate monthly SLA report for a tenant"""
    
    # Date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Total incidents
    total_incidents = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
        Server.tenant_id == tenant_id,
        Incident.created_at >= start_date,
        Incident.created_at < end_date
    ).scalar()
    
    # Auto-resolved incidents
    auto_resolved = db.query(func.count(Incident.id)).join(Sensor).join(Server).filter(
        Server.tenant_id == tenant_id,
        Incident.status == "auto_resolved",
        Incident.created_at >= start_date,
        Incident.created_at < end_date
    ).scalar()
    
    # Calculate availability (simplified)
    total_sensors = db.query(func.count(Sensor.id)).join(Server).filter(
        Server.tenant_id == tenant_id,
        Sensor.is_active == True
    ).scalar()
    
    if total_sensors > 0:
        # Count metrics with "ok" status
        ok_metrics = db.query(func.count(Metric.id)).join(Sensor).join(Server).filter(
            Server.tenant_id == tenant_id,
            Metric.status == "ok",
            Metric.timestamp >= start_date,
            Metric.timestamp < end_date
        ).scalar()
        
        total_metrics = db.query(func.count(Metric.id)).join(Sensor).join(Server).filter(
            Server.tenant_id == tenant_id,
            Metric.timestamp >= start_date,
            Metric.timestamp < end_date
        ).scalar()
        
        availability_percentage = (ok_metrics / total_metrics * 100) if total_metrics > 0 else 100.0
    else:
        availability_percentage = 100.0
    
    # SLA compliance (>= 99.5% is compliant)
    sla_compliance = availability_percentage >= 99.5
    
    # Get top incidents
    top_incidents = db.query(Incident).join(Sensor).join(Server).filter(
        Server.tenant_id == tenant_id,
        Incident.created_at >= start_date,
        Incident.created_at < end_date
    ).order_by(Incident.created_at.desc()).limit(10).all()
    
    report_data = {
        "top_incidents": [
            {
                "id": inc.id,
                "title": inc.title,
                "severity": inc.severity,
                "status": inc.status,
                "created_at": inc.created_at.isoformat()
            }
            for inc in top_incidents
        ],
        "total_sensors": total_sensors
    }
    
    # Request AI summary
    ai_summary = None
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{settings.AI_AGENT_URL}/api/v1/analyze/monthly-summary",
                json={
                    "tenant_id": tenant_id,
                    "year": year,
                    "month": month,
                    "availability_percentage": availability_percentage,
                    "total_incidents": total_incidents,
                    "auto_resolved_incidents": auto_resolved,
                    "report_data": report_data
                }
            )
            if response.status_code == 200:
                ai_summary = response.json().get("summary")
    except Exception as e:
        print(f"AI summary generation failed: {e}")
    
    # Create or update report
    existing_report = db.query(MonthlyReport).filter(
        MonthlyReport.tenant_id == tenant_id,
        MonthlyReport.year == year,
        MonthlyReport.month == month
    ).first()
    
    if existing_report:
        existing_report.availability_percentage = availability_percentage
        existing_report.total_incidents = total_incidents
        existing_report.auto_resolved_incidents = auto_resolved
        existing_report.sla_compliance = sla_compliance
        existing_report.report_data = report_data
        existing_report.ai_summary = ai_summary
        existing_report.generated_at = datetime.now(timezone.utc)
    else:
        report = MonthlyReport(
            tenant_id=tenant_id,
            year=year,
            month=month,
            availability_percentage=availability_percentage,
            total_incidents=total_incidents,
            auto_resolved_incidents=auto_resolved,
            sla_compliance=sla_compliance,
            report_data=report_data,
            ai_summary=ai_summary
        )
        db.add(report)
    
    db.commit()
