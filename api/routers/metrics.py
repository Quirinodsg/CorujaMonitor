from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db
from models import Metric, Sensor, Server, Probe, User
from auth import get_current_active_user

router = APIRouter()

class MetricCreate(BaseModel):
    sensor_id: int
    value: float
    unit: Optional[str] = None
    status: str = "ok"
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class MetricBulkCreate(BaseModel):
    probe_token: str
    metrics: List[MetricCreate]

class MetricResponse(BaseModel):
    id: int
    sensor_id: int
    value: float
    unit: Optional[str]
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

@router.post("/bulk")
async def create_metrics_bulk(
    data: MetricBulkCreate,
    db: Session = Depends(get_db)
):
    # Verify probe token
    probe = db.query(Probe).filter(Probe.token == data.probe_token).first()
    if not probe:
        raise HTTPException(status_code=401, detail="Invalid probe token")
    
    # Verify all sensors belong to this probe's tenant
    sensor_ids = [m.sensor_id for m in data.metrics]
    sensors = db.query(Sensor).join(Server).filter(
        Sensor.id.in_(sensor_ids),
        Server.tenant_id == probe.tenant_id
    ).all()
    
    if len(sensors) != len(set(sensor_ids)):
        raise HTTPException(status_code=400, detail="Invalid sensor IDs")
    
    # Create metrics
    metrics = [Metric(**metric.dict()) for metric in data.metrics]
    db.bulk_save_objects(metrics)
    db.commit()
    
    return {"message": f"Created {len(metrics)} metrics", "count": len(metrics)}


class ProbeMetricData(BaseModel):
    hostname: str
    sensor_type: str
    sensor_name: str
    value: float
    unit: Optional[str] = None
    status: str = "ok"
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ProbeMetricsBulk(BaseModel):
    probe_token: str
    metrics: List[ProbeMetricData]


@router.post("/probe/bulk")
async def create_probe_metrics_bulk(
    data: ProbeMetricsBulk,
    db: Session = Depends(get_db)
):
    """
    Endpoint for probes to send metrics.
    Automatically creates servers and sensors if they don't exist.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Verify probe token
    probe = db.query(Probe).filter(Probe.token == data.probe_token).first()
    if not probe:
        raise HTTPException(status_code=401, detail="Invalid probe token")
    
    logger.info(f"Received {len(data.metrics)} metrics from probe {probe.id}")
    
    metrics_created = 0
    
    for metric_data in data.metrics:
        # VALIDAÇÃO: Rejeitar sensores com tipo 'unknown'
        if metric_data.sensor_type == 'unknown':
            logger.debug(f"Skipping unknown sensor type")
            continue  # Pula este sensor
        
        logger.debug(f"Processing metric: {metric_data.hostname} - {metric_data.sensor_type} - {metric_data.sensor_name}")
        # VALIDAÇÃO: Rejeitar sensores com tipo 'unknown'
        if metric_data.sensor_type == 'unknown':
            continue  # Pula este sensor

        # STANDALONE SENSOR: se metadata contém sensor_id, gravar direto sem criar servidor
        if metric_data.metadata and metric_data.metadata.get('sensor_id'):
            direct_sensor_id = metric_data.metadata['sensor_id']
            # Aceitar sensor da mesma probe OU do mesmo tenant (caso probe_id divergente)
            sensor = db.query(Sensor).filter(
                Sensor.id == direct_sensor_id,
                Sensor.probe_id == probe.id
            ).first()
            if not sensor:
                # Fallback: aceitar se sensor pertence ao tenant da probe
                sensor = db.query(Sensor).filter(
                    Sensor.id == direct_sensor_id,
                    Sensor.server_id == None
                ).join(Probe, Probe.id == Sensor.probe_id).filter(
                    Probe.tenant_id == probe.tenant_id
                ).first()
            if sensor:
                from datetime import timezone as tz
                import pytz
                timestamp = metric_data.timestamp
                if timestamp.tzinfo is None:
                    brazil_tz = pytz.timezone('America/Sao_Paulo')
                    timestamp = brazil_tz.localize(timestamp).astimezone(pytz.UTC)
                metric = Metric(
                    sensor_id=sensor.id,
                    value=metric_data.value,
                    unit=metric_data.unit,
                    status=metric_data.status,
                    timestamp=timestamp,
                    extra_metadata=metric_data.metadata
                )
                db.add(metric)
                metrics_created += 1

                # ── DATACENTER EMERGENCY CALL ──
                # Ligar se sensor de datacenter (engetron/conflex) ficou critical
                if metric_data.status == 'critical' and sensor.sensor_type in ('engetron', 'conflex', 'snmp'):
                    sensor_name_lower = (sensor.name or '').lower()
                    is_datacenter = any(kw in sensor_name_lower for kw in ['nobreak', 'engetron', 'ups', 'ar-condicionado', 'conflex', 'hvac'])
                    if is_datacenter:
                        try:
                            _trigger_datacenter_emergency(db, probe.tenant_id, sensor, metric_data)
                        except Exception as call_err:
                            logger.warning(f"Emergency call error: {call_err}")
            else:
                logger.warning(f"Standalone sensor_id {direct_sensor_id} not found for probe {probe.id} (tenant {probe.tenant_id})")
            continue  # Não cria servidor para sensores standalone
        
        # Get or create server
        server = db.query(Server).filter(
            Server.tenant_id == probe.tenant_id,
            Server.hostname == metric_data.hostname
        ).first()
        
        # Extract IP from metadata if available
        ip_address = None
        public_ip = None
        if metric_data.metadata:
            if 'ip_address' in metric_data.metadata:
                ip_address = metric_data.metadata['ip_address']
            if 'public_ip' in metric_data.metadata:
                public_ip = metric_data.metadata['public_ip']
        
        if not server:
            server = Server(
                tenant_id=probe.tenant_id,
                probe_id=probe.id,
                hostname=metric_data.hostname,
                ip_address=ip_address,
                public_ip=public_ip,
                os_type="Windows",
                is_active=True
            )
            db.add(server)
            db.flush()
        else:
            # Update IPs if changed
            if ip_address and server.ip_address != ip_address:
                server.ip_address = ip_address
            if public_ip and server.public_ip != public_ip:
                server.public_ip = public_ip
            db.flush()
        
        # Get or create sensor
        # Normalize ping sensor names to "PING"
        sensor_name = metric_data.sensor_name
        if metric_data.sensor_type == 'ping':
            # Check if there's already a PING sensor for this server
            existing_ping = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.sensor_type == 'ping',
                Sensor.name == 'PING'
            ).first()
            
            if existing_ping:
                # Use the existing PING sensor
                sensor = existing_ping
            else:
                # Normalize any ping sensor name to "PING"
                sensor_name = "PING"
                sensor = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.sensor_type == 'ping',
                    Sensor.name == sensor_name
                ).first()
        else:
            sensor = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.sensor_type == metric_data.sensor_type,
                Sensor.name == sensor_name
            ).first()
        
        if not sensor:
            # Mapeamento de tipos equivalentes criados pelo portal vs sonda
            # Portal cria com tipos antigos; sonda envia com tipos novos
            EQUIVALENT_TYPES = {
                'uptime':      ['system', 'uptime'],
                'system':      ['uptime', 'system'],
                'network_in':  ['network', 'network_in'],
                'network_out': ['network', 'network_out'],
                'network':     ['network_in', 'network_out', 'network'],
            }

            # Tentar encontrar sensor equivalente pelo tipo (match por tipo alternativo)
            alt_types = EQUIVALENT_TYPES.get(metric_data.sensor_type, [])
            for alt_type in alt_types:
                sensor = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.sensor_type == alt_type
                ).first()
                if sensor:
                    # Atualizar tipo e nome para o padrão da sonda
                    sensor.sensor_type = metric_data.sensor_type
                    sensor.name = sensor_name
                    db.flush()
                    break

        if not sensor:
            # Tentar encontrar sensor pelo tipo exato (ignorando nome diferente)
            # EXCEÇÃO: 'service' — cada serviço é um sensor distinto, nunca reutilizar por tipo
            if metric_data.sensor_type != 'service':
                sensor = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.sensor_type == metric_data.sensor_type
                ).first()
                if sensor:
                    # Atualizar nome para o padrão da sonda
                    sensor.name = sensor_name
                    db.flush()

        if not sensor:
            # Set default thresholds based on sensor type
            threshold_warning = 80.0
            threshold_critical = 95.0
            
            # Customize thresholds for specific sensor types
            if metric_data.sensor_type == 'ping':
                # PRTG/Zabbix style: ping não usa threshold de latência.
                # Alerta apenas em DOWN (value=0). Latência alta é só métrica.
                threshold_warning = None
                threshold_critical = None
            elif metric_data.sensor_type in ('uptime', 'system'):
                threshold_warning = None
                threshold_critical = None
            elif metric_data.sensor_type == 'service':
                threshold_warning = 0.5   # valor binário: 0=stopped, 1=running
                threshold_critical = 0.5
            
            sensor = Sensor(
                server_id=server.id,
                sensor_type=metric_data.sensor_type,
                name=sensor_name,
                threshold_warning=threshold_warning,
                threshold_critical=threshold_critical,
                # Serviços descobertos ficam inativos por padrão — usuário seleciona na UI
                is_active=(metric_data.sensor_type != 'service'),
            )
            db.add(sensor)
            db.flush()
        
        # Create metric
        # Fix timezone: if timestamp is naive, assume it's in Brazil timezone (America/Sao_Paulo)
        from datetime import timezone as tz
        import pytz
        
        timestamp = metric_data.timestamp
        if timestamp.tzinfo is None:
            # Timestamp is naive, assume it's in Brazil timezone
            brazil_tz = pytz.timezone('America/Sao_Paulo')
            timestamp = brazil_tz.localize(timestamp)
            # Convert to UTC for storage
            timestamp = timestamp.astimezone(pytz.UTC)
        
        metric = Metric(
            sensor_id=sensor.id,
            value=metric_data.value,
            unit=metric_data.unit,
            status=metric_data.status,
            timestamp=timestamp,
            extra_metadata=metric_data.metadata  # CORRIGIDO: usar extra_metadata
        )
        db.add(metric)
        metrics_created += 1
    
    db.commit()
    
    logger.info(f"Successfully created {metrics_created} metrics")
    
    return {
        "message": f"Created {metrics_created} metrics",
        "count": metrics_created
    }

@router.get("/", response_model=List[MetricResponse])
async def list_metrics(
    sensor_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify sensor belongs to user's tenant (outerjoin to support standalone sensors)
    from sqlalchemy import or_
    sensor = db.query(Sensor).outerjoin(Server, Sensor.server_id == Server.id).outerjoin(
        Probe, Sensor.probe_id == Probe.id
    ).filter(
        Sensor.id == sensor_id,
        or_(
            Server.tenant_id == current_user.tenant_id,
            Probe.tenant_id == current_user.tenant_id
        )
    ).first()
    
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    query = db.query(Metric).filter(Metric.sensor_id == sensor_id)
    
    if start_time:
        query = query.filter(Metric.timestamp >= start_time)
    if end_time:
        query = query.filter(Metric.timestamp <= end_time)
    
    metrics = query.order_by(Metric.timestamp.desc()).limit(limit).all()
    
    # Fix metrics with None status (legacy data)
    for metric in metrics:
        if metric.status is None:
            metric.status = "ok"
    
    return metrics


@router.get("/latest/batch")
async def get_latest_metrics_batch(
    sensor_ids: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the latest metric for multiple sensors at once.
    sensor_ids: comma-separated list of sensor IDs
    Returns: dict { sensor_id: metric }
    """
    ids = [int(i) for i in sensor_ids.split(',') if i.strip().isdigit()]
    if not ids:
        return {}

    # Verify all sensors belong to user's tenant
    # Use outerjoin to include standalone sensors (server_id = NULL)
    from sqlalchemy import or_
    sensors = db.query(Sensor).outerjoin(Server, Sensor.server_id == Server.id).outerjoin(
        Probe, Sensor.probe_id == Probe.id
    ).filter(
        Sensor.id.in_(ids),
        or_(
            Server.tenant_id == current_user.tenant_id,
            Probe.tenant_id == current_user.tenant_id,
            # Sensores HTTP sem server_id e sem probe_id (coletados pelo worker central)
            (Sensor.server_id == None) & (Sensor.probe_id == None)
        )
    ).all()
    valid_ids = {s.id for s in sensors}

    # Get latest metric per sensor using a subquery
    from sqlalchemy import func
    subq = (
        db.query(Metric.sensor_id, func.max(Metric.id).label('max_id'))
        .filter(Metric.sensor_id.in_(valid_ids))
        .group_by(Metric.sensor_id)
        .subquery()
    )
    latest_metrics = (
        db.query(Metric)
        .join(subq, Metric.id == subq.c.max_id)
        .all()
    )

    result = {}
    for m in latest_metrics:
        entry = {
            "id": m.id,
            "sensor_id": m.sensor_id,
            "value": m.value,
            "unit": m.unit,
            "status": m.status or "ok",
            "timestamp": m.timestamp.isoformat()
        }
        if hasattr(m, 'extra_metadata') and m.extra_metadata:
            entry["metadata"] = m.extra_metadata
        result[str(m.sensor_id)] = entry
    return result


def _trigger_datacenter_emergency(db, tenant_id, sensor, metric_data):
    """Dispara ligação de emergência para alertas críticos do datacenter."""
    import redis as redis_lib
    from models import Tenant

    # Cooldown: 1 ligação por sensor a cada 30 min (evita flood)
    try:
        redis_client = redis_lib.Redis.from_url("redis://redis:6379", socket_connect_timeout=2)
        cooldown_key = f"emergency_call:{sensor.id}"
        if redis_client.exists(cooldown_key):
            logger.info(f"Emergency call cooldown active for sensor {sensor.id}")
            return
        redis_client.setex(cooldown_key, 1800, "1")  # 30 min
    except Exception:
        pass  # fail-open

    # Buscar config Twilio do tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant or not tenant.notification_config:
        return
    twilio_config = tenant.notification_config.get('twilio', {})
    if not twilio_config.get('enabled') or not twilio_config.get('account_sid'):
        return

    # Identificar o problema
    sensor_name = sensor.name or ''
    metadata = metric_data.metadata or {}
    name_lower = sensor_name.lower()

    if 'nobreak' in name_lower or 'engetron' in name_lower or 'ups' in name_lower:
        device = 'nobreak'
        # Verificar queda de fase
        problems = []
        for fase in ['A', 'B', 'C']:
            key = f'Engetron tensao_entrada_fase{fase}'
            if key in metadata:
                v = metadata[key].get('value', 999)
                if v < 100:
                    problems.append(f'Queda de Fase {fase}, tensão {v} volts')
        if not problems:
            problems.append('Alerta crítico detectado')
        problem = '. '.join(problems)
    elif 'condicionado' in name_lower or 'conflex' in name_lower or 'hvac' in name_lower:
        device = 'ar-condicionado'
        problems = []
        if metadata.get('Conflex alarme_temp_alta', {}).get('value') == 1:
            problems.append('Alarme de temperatura alta ativado')
        if metadata.get('Conflex alarme_defeito', {}).get('value') == 1:
            problems.append('Alarme de defeito de máquinas ativado')
        if metadata.get('Conflex maquina_1', {}).get('value') == 0:
            problems.append('Máquina 1 parada')
        if metadata.get('Conflex maquina_2', {}).get('value') == 0:
            problems.append('Máquina 2 parada')
        if metadata.get('Conflex status_plc', {}).get('value') == 0:
            problems.append('PLC offline')
        if not problems:
            problems.append('Alerta crítico detectado')
        problem = '. '.join(problems)
    else:
        device = 'equipamento'
        problem = 'Alerta crítico detectado'

    alert_data = {
        'device': device,
        'problem': problem,
        'sensor_name': sensor_name,
    }

    # SMS inteligente com detalhes do problema
    sms_body = (
        f'🚨 DATACENTER - ALERTA CRÍTICO\n\n'
        f'Dispositivo: {sensor_name}\n'
        f'Problema: {problem}\n\n'
        f'Verifique o Datacenter imediatamente.'
    )
    sms_data = {'body': sms_body}

    # Disparar SMS + Ligação em background
    import asyncio
    from routers.notifications import send_datacenter_emergency_call, send_twilio_notification
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(send_twilio_notification(twilio_config, sms_data))
            loop.create_task(send_datacenter_emergency_call(twilio_config, alert_data))
        else:
            asyncio.run(send_twilio_notification(twilio_config, sms_data))
            asyncio.run(send_datacenter_emergency_call(twilio_config, alert_data))
    except Exception as e:
        logger.warning(f"Emergency notification dispatch error: {e}")

    logger.warning(f"🚨 DATACENTER EMERGENCY: {device} - {problem} - SMS + ligação disparados")
