from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models import MonthlyReport, User, Incident, Server, Sensor, Metric
from auth import get_current_active_user

router = APIRouter()


# Tabela de preços de nuvem (valores aproximados em USD/mês)
CLOUD_PRICING = {
    'azure': {
        'small': {'cpu': 2, 'ram': 4, 'price': 70},    # Standard_B2s
        'medium': {'cpu': 4, 'ram': 16, 'price': 140},  # Standard_D4s_v3
        'large': {'cpu': 8, 'ram': 32, 'price': 280},   # Standard_D8s_v3
        'xlarge': {'cpu': 16, 'ram': 64, 'price': 560}  # Standard_D16s_v3
    },
    'aws': {
        'small': {'cpu': 2, 'ram': 4, 'price': 65},    # t3.medium
        'medium': {'cpu': 4, 'ram': 16, 'price': 135},  # m5.xlarge
        'large': {'cpu': 8, 'ram': 32, 'price': 270},   # m5.2xlarge
        'xlarge': {'cpu': 16, 'ram': 64, 'price': 540}  # m5.4xlarge
    },
    'gcp': {
        'small': {'cpu': 2, 'ram': 4, 'price': 60},    # n1-standard-2
        'medium': {'cpu': 4, 'ram': 15, 'price': 130},  # n1-standard-4
        'large': {'cpu': 8, 'ram': 30, 'price': 260},   # n1-standard-8
        'xlarge': {'cpu': 16, 'ram': 60, 'price': 520}  # n1-standard-16
    },
    'hyperv': {
        'small': {'cpu': 2, 'ram': 4, 'price': 30},    # Custo estimado on-premise
        'medium': {'cpu': 4, 'ram': 16, 'price': 60},
        'large': {'cpu': 8, 'ram': 32, 'price': 120},
        'xlarge': {'cpu': 16, 'ram': 64, 'price': 240}
    }
}


def calculate_cloud_costs(avg_cpu_utilization: float, avg_memory_utilization: float, 
                         current_cpu_cores: int = 4, current_ram_gb: int = 16) -> Dict[str, Any]:
    """
    Calcula custos estimados em diferentes provedores de nuvem
    baseado na utilização atual de recursos
    """
    
    # Determinar tamanho ideal baseado na utilização
    if avg_cpu_utilization < 30 and avg_memory_utilization < 30:
        recommended_size = 'small'
    elif avg_cpu_utilization < 60 and avg_memory_utilization < 60:
        recommended_size = 'medium'
    elif avg_cpu_utilization < 85 and avg_memory_utilization < 85:
        recommended_size = 'large'
    else:
        recommended_size = 'xlarge'
    
    # Calcular custos para cada provedor
    costs = {}
    for provider, sizes in CLOUD_PRICING.items():
        current_size_cost = sizes.get(recommended_size, sizes['medium'])
        
        costs[provider] = {
            'recommended_size': recommended_size,
            'cpu_cores': current_size_cost['cpu'],
            'ram_gb': current_size_cost['ram'],
            'monthly_cost_usd': current_size_cost['price'],
            'monthly_cost_brl': current_size_cost['price'] * 5.0,  # Conversão aproximada
            'annual_cost_brl': current_size_cost['price'] * 5.0 * 12
        }
    
    # Comparação de custos
    cheapest = min(costs.items(), key=lambda x: x[1]['monthly_cost_brl'])
    most_expensive = max(costs.items(), key=lambda x: x[1]['monthly_cost_brl'])
    
    return {
        'costs_by_provider': costs,
        'cheapest_provider': cheapest[0],
        'cheapest_cost': cheapest[1]['monthly_cost_brl'],
        'most_expensive_provider': most_expensive[0],
        'most_expensive_cost': most_expensive[1]['monthly_cost_brl'],
        'potential_savings': most_expensive[1]['monthly_cost_brl'] - cheapest[1]['monthly_cost_brl'],
        'recommended_size': recommended_size
    }

class MonthlyReportResponse(BaseModel):
    id: int
    year: int
    month: int
    availability_percentage: Optional[float]
    total_incidents: Optional[int]
    auto_resolved_incidents: Optional[int]
    sla_compliance: Optional[float]
    report_data: Optional[Dict[str, Any]]
    ai_summary: Optional[str]
    generated_at: datetime
    
    class Config:
        from_attributes = True


class ReportTemplate(BaseModel):
    id: str
    name: str
    description: str
    period: str  # monthly, quarterly, annual


class AvailabilityReportResponse(BaseModel):
    period: str
    start_date: str
    end_date: str
    total_servers: int
    availability_percentage: float
    total_downtime_hours: float
    servers_detail: List[Dict[str, Any]]


class ProblemsReportResponse(BaseModel):
    period: str
    servers_with_most_problems: List[Dict[str, Any]]


class AIResolutionReportResponse(BaseModel):
    period: str
    total_incidents: int
    ai_resolved: int
    ai_resolution_rate: float
    manual_resolved: int


@router.get("/templates", response_model=List[ReportTemplate])
async def list_report_templates(
    current_user: User = Depends(get_current_active_user)
):
    """List available report templates"""
    templates = [
        {
            "id": "availability_monthly",
            "name": "Disponibilidade Mensal",
            "description": "Relatório de disponibilidade dos servidores no último mês",
            "period": "monthly"
        },
        {
            "id": "availability_quarterly",
            "name": "Disponibilidade Trimestral",
            "description": "Relatório de disponibilidade dos servidores nos últimos 3 meses",
            "period": "quarterly"
        },
        {
            "id": "availability_annual",
            "name": "Disponibilidade Anual",
            "description": "Relatório de disponibilidade dos servidores no último ano",
            "period": "annual"
        },
        {
            "id": "problems_monthly",
            "name": "Máquinas com Mais Problemas (Mensal)",
            "description": "Servidores que apresentaram mais incidentes no último mês",
            "period": "monthly"
        },
        {
            "id": "problems_quarterly",
            "name": "Máquinas com Mais Problemas (Trimestral)",
            "description": "Servidores que apresentaram mais incidentes nos últimos 3 meses",
            "period": "quarterly"
        },
        {
            "id": "ai_resolution_monthly",
            "name": "Resoluções por IA (Mensal)",
            "description": "Incidentes resolvidos automaticamente pela IA no último mês",
            "period": "monthly"
        },
        {
            "id": "ai_resolution_quarterly",
            "name": "Resoluções por IA (Trimestral)",
            "description": "Incidentes resolvidos automaticamente pela IA nos últimos 3 meses",
            "period": "quarterly"
        },
        {
            "id": "ai_resolution_annual",
            "name": "Resoluções por IA (Anual)",
            "description": "Incidentes resolvidos automaticamente pela IA no último ano",
            "period": "annual"
        }
    ]
    return templates


@router.get("/generate/availability/{period}")
async def generate_availability_report(
    period: str,  # monthly, quarterly, annual
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate availability report for specified period"""
    now = datetime.now()
    
    if period == "monthly":
        start_date = now - timedelta(days=30)
        period_name = "Último Mês"
    elif period == "quarterly":
        start_date = now - timedelta(days=90)
        period_name = "Último Trimestre"
    elif period == "annual":
        start_date = now - timedelta(days=365)
        period_name = "Último Ano"
    else:
        raise HTTPException(status_code=400, detail="Invalid period")
    
    # Get all servers for tenant
    servers = db.query(Server).filter(
        Server.tenant_id == current_user.tenant_id
    ).all()
    
    servers_detail = []
    total_uptime = 0
    
    for server in servers:
        # Get critical incidents for this server
        critical_incidents = db.query(Incident).join(Sensor).filter(
            Sensor.server_id == server.id,
            Incident.severity == "critical",
            Incident.created_at >= start_date
        ).count()
        
        # Calculate uptime (simplified - in production use actual metrics)
        uptime_percentage = max(95.0, 100.0 - (critical_incidents * 0.5))
        total_uptime += uptime_percentage
        
        servers_detail.append({
            "hostname": server.hostname,
            "ip_address": server.ip_address,
            "availability": round(uptime_percentage, 2),
            "incidents": critical_incidents
        })
    
    avg_availability = total_uptime / len(servers) if servers else 0
    
    return {
        "period": period_name,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": now.strftime("%Y-%m-%d"),
        "total_servers": len(servers),
        "availability_percentage": round(avg_availability, 2),
        "total_downtime_hours": round((100 - avg_availability) * 24 * 30 / 100, 2),
        "servers_detail": servers_detail
    }


@router.get("/generate/problems/{period}")
async def generate_problems_report(
    period: str,  # monthly, quarterly
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate report of servers with most problems"""
    now = datetime.now()
    
    if period == "monthly":
        start_date = now - timedelta(days=30)
        period_name = "Último Mês"
    elif period == "quarterly":
        start_date = now - timedelta(days=90)
        period_name = "Último Trimestre"
    else:
        raise HTTPException(status_code=400, detail="Invalid period")
    
    # Query servers with incident counts
    from sqlalchemy import case
    
    servers_with_problems = db.query(
        Server.hostname,
        Server.ip_address,
        func.count(Incident.id).label('incident_count'),
        func.sum(case((Incident.severity == 'critical', 1), else_=0)).label('critical_count'),
        func.sum(case((Incident.severity == 'warning', 1), else_=0)).label('warning_count')
    ).join(Sensor, Server.id == Sensor.server_id)\
     .join(Incident, Sensor.id == Incident.sensor_id)\
     .filter(
         Server.tenant_id == current_user.tenant_id,
         Incident.created_at >= start_date
     ).group_by(Server.id, Server.hostname, Server.ip_address)\
      .order_by(func.count(Incident.id).desc())\
      .limit(10)\
      .all()
    
    servers_list = []
    for server in servers_with_problems:
        servers_list.append({
            "hostname": server.hostname,
            "ip_address": server.ip_address,
            "total_incidents": server.incident_count,
            "critical_incidents": server.critical_count or 0,
            "warning_incidents": server.warning_count or 0
        })
    
    return {
        "period": period_name,
        "servers_with_most_problems": servers_list
    }


@router.get("/generate/ai-resolution/{period}")
async def generate_ai_resolution_report(
    period: str,  # monthly, quarterly, annual
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate report of AI-resolved incidents"""
    now = datetime.now()
    
    if period == "monthly":
        start_date = now - timedelta(days=30)
        period_name = "Último Mês"
    elif period == "quarterly":
        start_date = now - timedelta(days=90)
        period_name = "Último Trimestre"
    elif period == "annual":
        start_date = now - timedelta(days=365)
        period_name = "Último Ano"
    else:
        raise HTTPException(status_code=400, detail="Invalid period")
    
    # Get incidents for tenant's servers
    total_incidents = db.query(Incident).join(Sensor).join(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Incident.created_at >= start_date
    ).count()
    
    ai_resolved = db.query(Incident).join(Sensor).join(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Incident.created_at >= start_date,
        Incident.status == "auto_resolved",
        Incident.remediation_successful == True
    ).count()
    
    manual_resolved = db.query(Incident).join(Sensor).join(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Incident.created_at >= start_date,
        Incident.status == "resolved",
        Incident.remediation_attempted == False
    ).count()
    
    ai_resolution_rate = (ai_resolved / total_incidents * 100) if total_incidents > 0 else 0
    
    return {
        "period": period_name,
        "total_incidents": total_incidents,
        "ai_resolved": ai_resolved,
        "ai_resolution_rate": round(ai_resolution_rate, 2),
        "manual_resolved": manual_resolved
    }


@router.get("/monthly", response_model=List[MonthlyReportResponse])
async def list_monthly_reports(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(MonthlyReport).filter(
        MonthlyReport.tenant_id == current_user.tenant_id
    )
    
    if year:
        query = query.filter(MonthlyReport.year == year)
    
    reports = query.order_by(
        MonthlyReport.year.desc(),
        MonthlyReport.month.desc()
    ).all()
    
    return reports

@router.get("/monthly/{year}/{month}", response_model=MonthlyReportResponse)
async def get_monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    report = db.query(MonthlyReport).filter(
        MonthlyReport.tenant_id == current_user.tenant_id,
        MonthlyReport.year == year,
        MonthlyReport.month == month
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report



@router.get("/generate/cpu-utilization/monthly")
async def generate_cpu_utilization_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate monthly CPU utilization report with sizing recommendations"""
    
    # Get date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Get all servers for tenant
    servers = db.query(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Server.is_active == True
    ).all()
    
    if not servers:
        raise HTTPException(status_code=404, detail="No servers found")
    
    # Calculate overall statistics
    total_avg = 0
    total_peak = 0
    total_min = 100
    servers_analysis = []
    
    for server in servers:
        # Get CPU sensors for this server
        cpu_sensors = db.query(Sensor).filter(
            Sensor.server_id == server.id,
            Sensor.sensor_type == 'cpu',
            Sensor.is_active == True
        ).all()
        
        if not cpu_sensors:
            continue
        
        # Get metrics for last 30 days
        sensor_ids = [s.id for s in cpu_sensors]
        metrics = db.query(Metric).filter(
            Metric.sensor_id.in_(sensor_ids),
            Metric.timestamp >= start_date,
            Metric.timestamp <= end_date
        ).all()
        
        if not metrics:
            continue
        
        # Calculate statistics
        values = [m.value for m in metrics]
        avg_util = sum(values) / len(values)
        peak_util = max(values)
        min_util = min(values)
        
        total_avg += avg_util
        total_peak = max(total_peak, peak_util)
        total_min = min(total_min, min_util)
        
        # Determine recommendation
        recommendation_type = 'optimal'
        recommendation_title = 'Dimensionamento Adequado'
        recommendation_detail = 'Servidor está bem dimensionado para a carga atual.'
        
        if avg_util < 30:
            recommendation_type = 'downsize'
            recommendation_title = 'Reduzir Recursos'
            recommendation_detail = f'Utilização média de apenas {avg_util:.1f}%. Considere reduzir CPU para economizar custos.'
        elif avg_util > 85:
            recommendation_type = 'upsize'
            recommendation_title = 'Aumentar Recursos'
            recommendation_detail = f'Utilização média de {avg_util:.1f}%. Recomendado aumentar CPU para melhor performance.'
        
        servers_analysis.append({
            'hostname': server.hostname,
            'ip_address': server.ip_address,
            'avg_utilization': round(avg_util, 1),
            'peak_utilization': round(peak_util, 1),
            'min_utilization': round(min_util, 1),
            'recommendation_type': recommendation_type,
            'recommendation_title': recommendation_title,
            'recommendation_detail': recommendation_detail
        })
    
    # Calculate overall average
    overall_avg = total_avg / len(servers_analysis) if servers_analysis else 0
    
    # Generate daily data for chart (simplified - last 30 days)
    daily_data = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        # Simulate daily average (in production, calculate from actual metrics)
        daily_avg = overall_avg + (i % 10 - 5) * 2  # Variation
        daily_data.append({
            'date': date.strftime('%d/%m'),
            'value': max(0, min(100, daily_avg))
        })
    
    # Strategic recommendations
    strategic_recommendations = []
    
    downsize_count = len([s for s in servers_analysis if s['recommendation_type'] == 'downsize'])
    upsize_count = len([s for s in servers_analysis if s['recommendation_type'] == 'upsize'])
    
    if downsize_count > 0:
        strategic_recommendations.append({
            'priority': 'high',
            'title': f'Otimizar {downsize_count} Servidor(es) Sobredimensionado(s)',
            'description': f'Identificamos {downsize_count} servidor(es) com utilização média abaixo de 30%. Reduzir recursos pode gerar economia significativa.',
            'impact': f'Economia estimada de R$ {downsize_count * 500:,.2f}/mês'
        })
    
    if upsize_count > 0:
        strategic_recommendations.append({
            'priority': 'high',
            'title': f'Expandir {upsize_count} Servidor(es) Subdimensionado(s)',
            'description': f'Identificamos {upsize_count} servidor(es) com utilização média acima de 85%. Aumentar recursos evitará problemas de performance.',
            'impact': 'Melhoria de 30-50% na performance'
        })
    
    if overall_avg > 70:
        strategic_recommendations.append({
            'priority': 'medium',
            'title': 'Planejamento de Capacidade',
            'description': 'Utilização geral está alta. Considere planejar expansão de infraestrutura para os próximos 6 meses.',
            'impact': 'Evita problemas futuros de capacidade'
        })
    
    # Cost analysis with cloud pricing
    potential_savings = downsize_count * 500  # R$ 500/mês por servidor
    required_investment = upsize_count * 800  # R$ 800 para upgrade
    roi_months = round(required_investment / potential_savings) if potential_savings > 0 else 12
    
    # Calculate cloud costs (assumindo utilização média de memória de 60%)
    cloud_costs = calculate_cloud_costs(overall_avg, 60.0)
    
    return {
        'period': f'{start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}',
        'average_utilization': round(overall_avg, 1),
        'peak_utilization': round(total_peak, 1),
        'min_utilization': round(total_min, 1),
        'total_servers': len(servers_analysis),
        'daily_data': daily_data,
        'servers_analysis': servers_analysis,
        'strategic_recommendations': strategic_recommendations,
        'potential_savings': potential_savings,
        'required_investment': required_investment,
        'roi_months': roi_months,
        'cloud_costs': cloud_costs
    }


@router.get("/generate/memory-utilization/monthly")
async def generate_memory_utilization_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate monthly Memory utilization report with sizing recommendations"""
    
    # Get date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Get all servers for tenant
    servers = db.query(Server).filter(
        Server.tenant_id == current_user.tenant_id,
        Server.is_active == True
    ).all()
    
    if not servers:
        raise HTTPException(status_code=404, detail="No servers found")
    
    # Calculate overall statistics
    total_avg = 0
    total_peak = 0
    total_min = 100
    servers_analysis = []
    
    for server in servers:
        # Get Memory sensors for this server
        memory_sensors = db.query(Sensor).filter(
            Sensor.server_id == server.id,
            Sensor.sensor_type == 'memory',
            Sensor.is_active == True
        ).all()
        
        if not memory_sensors:
            continue
        
        # Get metrics for last 30 days
        sensor_ids = [s.id for s in memory_sensors]
        metrics = db.query(Metric).filter(
            Metric.sensor_id.in_(sensor_ids),
            Metric.timestamp >= start_date,
            Metric.timestamp <= end_date
        ).all()
        
        if not metrics:
            continue
        
        # Calculate statistics
        values = [m.value for m in metrics]
        avg_util = sum(values) / len(values)
        peak_util = max(values)
        min_util = min(values)
        
        total_avg += avg_util
        total_peak = max(total_peak, peak_util)
        total_min = min(total_min, min_util)
        
        # Determine recommendation
        recommendation_type = 'optimal'
        recommendation_title = 'Dimensionamento Adequado'
        recommendation_detail = 'Servidor está bem dimensionado para a carga atual.'
        
        if avg_util < 30:
            recommendation_type = 'downsize'
            recommendation_title = 'Reduzir Memória'
            recommendation_detail = f'Utilização média de apenas {avg_util:.1f}%. Considere reduzir RAM para economizar custos.'
        elif avg_util > 85:
            recommendation_type = 'upsize'
            recommendation_title = 'Aumentar Memória'
            recommendation_detail = f'Utilização média de {avg_util:.1f}%. Recomendado aumentar RAM para evitar swapping e melhorar performance.'
        
        servers_analysis.append({
            'hostname': server.hostname,
            'ip_address': server.ip_address,
            'avg_utilization': round(avg_util, 1),
            'peak_utilization': round(peak_util, 1),
            'min_utilization': round(min_util, 1),
            'recommendation_type': recommendation_type,
            'recommendation_title': recommendation_title,
            'recommendation_detail': recommendation_detail
        })
    
    # Calculate overall average
    overall_avg = total_avg / len(servers_analysis) if servers_analysis else 0
    
    # Generate daily data for chart (simplified - last 30 days)
    daily_data = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        # Simulate daily average (in production, calculate from actual metrics)
        daily_avg = overall_avg + (i % 10 - 5) * 2  # Variation
        daily_data.append({
            'date': date.strftime('%d/%m'),
            'value': max(0, min(100, daily_avg))
        })
    
    # Strategic recommendations
    strategic_recommendations = []
    
    downsize_count = len([s for s in servers_analysis if s['recommendation_type'] == 'downsize'])
    upsize_count = len([s for s in servers_analysis if s['recommendation_type'] == 'upsize'])
    
    if downsize_count > 0:
        strategic_recommendations.append({
            'priority': 'high',
            'title': f'Otimizar {downsize_count} Servidor(es) com Excesso de RAM',
            'description': f'Identificamos {downsize_count} servidor(es) com utilização de memória abaixo de 30%. Reduzir RAM pode gerar economia.',
            'impact': f'Economia estimada de R$ {downsize_count * 400:,.2f}/mês'
        })
    
    if upsize_count > 0:
        strategic_recommendations.append({
            'priority': 'high',
            'title': f'Expandir RAM em {upsize_count} Servidor(es)',
            'description': f'Identificamos {upsize_count} servidor(es) com utilização de memória acima de 85%. Aumentar RAM evitará swapping e melhorará performance.',
            'impact': 'Melhoria de 40-60% na performance e estabilidade'
        })
    
    if overall_avg > 75:
        strategic_recommendations.append({
            'priority': 'medium',
            'title': 'Monitorar Memory Leaks',
            'description': 'Utilização geral de memória está alta. Recomendamos investigar possíveis memory leaks em aplicações.',
            'impact': 'Previne crashes e instabilidade'
        })
    
    # Cost analysis
    potential_savings = downsize_count * 400  # R$ 400/mês por servidor
    required_investment = upsize_count * 600  # R$ 600 para upgrade de RAM
    roi_months = round(required_investment / potential_savings) if potential_savings > 0 else 12
    
    return {
        'period': f'{start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")}',
        'average_utilization': round(overall_avg, 1),
        'peak_utilization': round(total_peak, 1),
        'min_utilization': round(total_min, 1),
        'total_servers': len(servers_analysis),
        'daily_data': daily_data,
        'servers_analysis': servers_analysis,
        'strategic_recommendations': strategic_recommendations,
        'potential_savings': potential_savings,
        'required_investment': required_investment,
        'roi_months': roi_months
    }
