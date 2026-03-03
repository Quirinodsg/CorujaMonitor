from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Sensor, Metric, Server, Incident
from auth import get_current_active_user, User

router = APIRouter()


class AIAnalysisResponse(BaseModel):
    sensor_id: int
    sensor_name: str
    sensor_type: str
    current_status: str
    current_value: Optional[float] = None
    ai_analysis: Dict[str, Any]
    
    class Config:
        from_attributes = True


@router.get("/sensor/{sensor_id}", response_model=AIAnalysisResponse)
async def get_sensor_ai_analysis(
    sensor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get AI analysis for a specific sensor"""
    
    # Get sensor with server info
    sensor = db.query(Sensor).join(Server).filter(
        Sensor.id == sensor_id,
        Server.tenant_id == current_user.tenant_id
    ).first()
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    # Get latest metric
    latest_metric = db.query(Metric).filter(
        Metric.sensor_id == sensor_id
    ).order_by(desc(Metric.timestamp)).first()
    
    # Get metrics from last 24 hours
    since = datetime.now() - timedelta(hours=24)
    recent_metrics = db.query(Metric).filter(
        Metric.sensor_id == sensor_id,
        Metric.timestamp >= since
    ).order_by(desc(Metric.timestamp)).limit(100).all()
    
    # Generate AI analysis based on sensor type and status
    ai_analysis = generate_analysis(
        sensor=sensor,
        latest_metric=latest_metric,
        recent_metrics=recent_metrics
    )
    
    return AIAnalysisResponse(
        sensor_id=sensor.id,
        sensor_name=sensor.name,
        sensor_type=sensor.sensor_type,
        current_status=latest_metric.status if latest_metric else "unknown",
        current_value=latest_metric.value if latest_metric else None,
        ai_analysis=ai_analysis
    )


def generate_analysis(sensor: Sensor, latest_metric: Metric, recent_metrics: List[Metric]) -> Dict[str, Any]:
    """Generate AI analysis for sensor"""
    
    if not latest_metric:
        return {
            "root_cause": "Aguardando dados do sensor",
            "confidence": 0.0,
            "evidence": ["Nenhuma métrica coletada ainda"],
            "suggested_actions": [
                {
                    "priority": "medium",
                    "action": "Verificar se a probe está ativa e coletando dados",
                    "command": None
                }
            ],
            "auto_remediation_available": False,
            "estimated_resolution_time": "N/A"
        }
    
    status = latest_metric.status
    value = latest_metric.value
    sensor_type = sensor.sensor_type
    
    # Calculate trend
    trend = "stable"
    if len(recent_metrics) >= 5:
        recent_values = [m.value for m in recent_metrics[:5]]
        if all(recent_values[i] < recent_values[i+1] for i in range(len(recent_values)-1)):
            trend = "increasing"
        elif all(recent_values[i] > recent_values[i+1] for i in range(len(recent_values)-1)):
            trend = "decreasing"
    
    # Generate analysis based on sensor type and status
    if status == "critical":
        return generate_critical_analysis(sensor_type, value, trend, sensor, latest_metric)
    elif status == "warning":
        return generate_warning_analysis(sensor_type, value, trend, sensor, latest_metric)
    else:
        return generate_ok_analysis(sensor_type, value, trend)


def generate_critical_analysis(sensor_type: str, value: float, trend: str, sensor: Sensor, metric: Metric) -> Dict[str, Any]:
    """Generate analysis for critical sensors"""
    
    analyses = {
        "cpu": {
            "root_cause": f"CPU em {value:.1f}% - Possível processo consumindo recursos excessivos",
            "confidence": 0.85,
            "evidence": [
                f"CPU atual: {value:.1f}% (limite crítico: {sensor.threshold_critical}%)",
                f"Tendência: {trend}",
                "Possíveis causas: processo travado, malware, aplicação mal otimizada"
            ],
            "suggested_actions": [
                {
                    "priority": "high",
                    "action": "Identificar processos com maior consumo de CPU",
                    "command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"
                },
                {
                    "priority": "high",
                    "action": "Verificar se há processos suspeitos ou travados",
                    "command": "Get-Process | Where-Object {$_.Responding -eq $false}"
                },
                {
                    "priority": "medium",
                    "action": "Considerar reiniciar processos problemáticos",
                    "command": "Stop-Process -Name [processo] -Force"
                }
            ],
            "auto_remediation_available": False,
            "estimated_resolution_time": "5-10 minutos"
        },
        "memory": {
            "root_cause": f"Memória em {value:.1f}% - Possível memory leak ou falta de RAM",
            "confidence": 0.80,
            "evidence": [
                f"Memória atual: {value:.1f}% (limite crítico: {sensor.threshold_critical}%)",
                f"Tendência: {trend}",
                "Possíveis causas: memory leak, muitos processos, cache excessivo"
            ],
            "suggested_actions": [
                {
                    "priority": "high",
                    "action": "Identificar processos com maior consumo de memória",
                    "command": "Get-Process | Sort-Object WS -Descending | Select-Object -First 10"
                },
                {
                    "priority": "medium",
                    "action": "Limpar cache do sistema",
                    "command": "Clear-RecycleBin -Force; Remove-Item $env:TEMP\\* -Recurse -Force"
                },
                {
                    "priority": "low",
                    "action": "Considerar aumentar RAM do servidor",
                    "command": None
                }
            ],
            "auto_remediation_available": True,
            "estimated_resolution_time": "2-5 minutos"
        },
        "disk": {
            "root_cause": f"Disco em {value:.1f}% - Espaço insuficiente",
            "confidence": 0.95,
            "evidence": [
                f"Uso de disco: {value:.1f}% (limite crítico: {sensor.threshold_critical}%)",
                f"Tendência: {trend}",
                "Possíveis causas: logs não rotacionados, arquivos temporários, backups antigos"
            ],
            "suggested_actions": [
                {
                    "priority": "high",
                    "action": "Identificar pastas com maior uso de espaço",
                    "command": "Get-ChildItem C:\\ -Directory | ForEach-Object {Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum} | Sort-Object Sum -Descending"
                },
                {
                    "priority": "high",
                    "action": "Limpar arquivos temporários",
                    "command": "Remove-Item $env:TEMP\\* -Recurse -Force; Remove-Item C:\\Windows\\Temp\\* -Recurse -Force"
                },
                {
                    "priority": "medium",
                    "action": "Verificar logs antigos",
                    "command": "Get-ChildItem C:\\*.log -Recurse | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)}"
                }
            ],
            "auto_remediation_available": True,
            "estimated_resolution_time": "5-15 minutos"
        },
        "service": {
            "root_cause": f"Serviço '{sensor.name}' está offline",
            "confidence": 0.90,
            "evidence": [
                f"Status: Offline",
                "Possíveis causas: falha na aplicação, dependências não disponíveis, erro de configuração"
            ],
            "suggested_actions": [
                {
                    "priority": "high",
                    "action": "Verificar logs do serviço",
                    "command": f"Get-EventLog -LogName Application -Source {sensor.name} -Newest 20"
                },
                {
                    "priority": "high",
                    "action": "Tentar reiniciar o serviço",
                    "command": f"Restart-Service -Name {sensor.name.replace('service_', '')}"
                },
                {
                    "priority": "medium",
                    "action": "Verificar dependências do serviço",
                    "command": f"Get-Service -Name {sensor.name.replace('service_', '')} -DependentServices"
                }
            ],
            "auto_remediation_available": True,
            "estimated_resolution_time": "2-5 minutos"
        },
        "ping": {
            "root_cause": f"Latência alta: {value:.0f}ms - Problemas de rede ou servidor sobrecarregado",
            "confidence": 0.75,
            "evidence": [
                f"Latência: {value:.0f}ms (limite crítico: {sensor.threshold_critical}ms)",
                f"Tendência: {trend}",
                "Possíveis causas: problemas de rede, firewall, servidor sobrecarregado"
            ],
            "suggested_actions": [
                {
                    "priority": "high",
                    "action": "Verificar conectividade de rede",
                    "command": f"Test-NetConnection -ComputerName {sensor.config.get('target', '8.8.8.8') if sensor.config else '8.8.8.8'} -TraceRoute"
                },
                {
                    "priority": "medium",
                    "action": "Verificar uso de banda",
                    "command": "Get-NetAdapterStatistics"
                },
                {
                    "priority": "low",
                    "action": "Verificar regras de firewall",
                    "command": "Get-NetFirewallRule | Where-Object {$_.Enabled -eq 'True'}"
                }
            ],
            "auto_remediation_available": False,
            "estimated_resolution_time": "10-30 minutos"
        },
        "network": {
            "root_cause": f"Tráfego de rede alto: {value:.2f} MB/s",
            "confidence": 0.70,
            "evidence": [
                f"Tráfego: {value:.2f} MB/s (limite crítico: {sensor.threshold_critical} MB/s)",
                f"Tendência: {trend}",
                "Possíveis causas: transferência de arquivos, backup, ataque DDoS"
            ],
            "suggested_actions": [
                {
                    "priority": "high",
                    "action": "Identificar processos usando rede",
                    "command": "Get-NetTCPConnection | Group-Object -Property OwningProcess | Sort-Object Count -Descending"
                },
                {
                    "priority": "medium",
                    "action": "Verificar conexões ativas",
                    "command": "Get-NetTCPConnection -State Established"
                }
            ],
            "auto_remediation_available": False,
            "estimated_resolution_time": "5-15 minutos"
        }
    }
    
    return analyses.get(sensor_type, {
        "root_cause": f"Sensor {sensor.name} em estado crítico",
        "confidence": 0.50,
        "evidence": [f"Valor atual: {value}", f"Tendência: {trend}"],
        "suggested_actions": [
            {
                "priority": "high",
                "action": "Investigar causa do problema",
                "command": None
            }
        ],
        "auto_remediation_available": False,
        "estimated_resolution_time": "Indeterminado"
    })


def generate_warning_analysis(sensor_type: str, value: float, trend: str, sensor: Sensor, metric: Metric) -> Dict[str, Any]:
    """Generate analysis for warning sensors"""
    
    return {
        "root_cause": f"Sensor em estado de aviso - Valor: {value:.1f}",
        "confidence": 0.70,
        "evidence": [
            f"Valor atual: {value:.1f} (limite aviso: {sensor.threshold_warning})",
            f"Tendência: {trend}",
            "Situação sob controle, mas requer atenção"
        ],
        "suggested_actions": [
            {
                "priority": "medium",
                "action": "Monitorar evolução nas próximas horas",
                "command": None
            },
            {
                "priority": "low",
                "action": "Considerar ajustar thresholds se alertas forem frequentes",
                "command": None
            }
        ],
        "auto_remediation_available": False,
        "estimated_resolution_time": "Monitoramento contínuo"
    }


def generate_ok_analysis(sensor_type: str, value: float, trend: str) -> Dict[str, Any]:
    """Generate analysis for OK sensors"""
    
    return {
        "root_cause": "Sensor operando normalmente",
        "confidence": 1.0,
        "evidence": [
            f"Valor atual: {value:.1f}",
            f"Tendência: {trend}",
            "Todos os parâmetros dentro dos limites esperados"
        ],
        "suggested_actions": [
            {
                "priority": "low",
                "action": "Continuar monitoramento regular",
                "command": None
            }
        ],
        "auto_remediation_available": False,
        "estimated_resolution_time": "N/A"
    }
