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
            # Set default thresholds based on sensor type
            threshold_warning = 80.0
            threshold_critical = 95.0
            
            # Customize thresholds for specific sensor types
            if metric_data.sensor_type == 'ping':
                threshold_warning = 100.0  # 100ms
                threshold_critical = 200.0  # 200ms
            elif metric_data.sensor_type == 'system':  # uptime
                threshold_warning = None
                threshold_critical = None
            
            sensor = Sensor(
                server_id=server.id,
                sensor_type=metric_data.sensor_type,
                name=sensor_name,  # Use normalized name
                threshold_warning=threshold_warning,
                threshold_critical=threshold_critical,
                is_active=True
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
    # Verify sensor belongs to user's tenant
    sensor = db.query(Sensor).join(Server).filter(
        Sensor.id == sensor_id,
        Server.tenant_id == current_user.tenant_id
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
