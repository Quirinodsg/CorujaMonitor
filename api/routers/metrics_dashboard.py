from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import statistics

from database import get_db
from models import Sensor, Metric, Server, User
from auth import get_current_active_user

router = APIRouter()

def parse_time_range(range_str: str) -> datetime:
    """Parse time range string to datetime"""
    now = datetime.now()
    
    if range_str == '1h':
        return now - timedelta(hours=1)
    elif range_str == '6h':
        return now - timedelta(hours=6)
    elif range_str == '24h':
        return now - timedelta(hours=24)
    elif range_str == '7d':
        return now - timedelta(days=7)
    elif range_str == '30d':
        return now - timedelta(days=30)
    else:
        return now - timedelta(hours=24)  # default


@router.get("/dashboard/servers")
async def get_servers_dashboard(
    time_range: str = Query('24h', description="Time range: 1h, 6h, 24h, 7d, 30d", alias="range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get servers dashboard data with metrics"""
    try:
        start_time = parse_time_range(time_range)
        
        # Get all servers for user's tenant
        servers = db.query(Server).filter(
            Server.tenant_id == current_user.tenant_id
        ).all()
        
        if not servers:
            return {
                "summary": {
                    "cpu_avg": 0,
                    "memory_avg": 0,
                    "disk_avg": 0,
                    "servers_online": 0,
                    "servers_total": 0
                },
                "servers": [],
                "timeseries": {
                    "cpu": [],
                    "memory": [],
                    "disk": []
                }
            }
        
        # Get latest metrics for each server
        servers_data = []
        cpu_values = []
        memory_values = []
        disk_values = []
        servers_online = 0
        
        for server in servers:
            # Get latest CPU metric
            cpu_sensor = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.sensor_type == 'cpu'
            ).first()
            
            cpu_value = 0
            cpu_status = 'unknown'
            if cpu_sensor:
                latest_cpu = db.query(Metric).filter(
                    Metric.sensor_id == cpu_sensor.id
                ).order_by(Metric.timestamp.desc()).first()
                if latest_cpu:
                    cpu_value = latest_cpu.value
                    cpu_status = latest_cpu.status
                    cpu_values.append(cpu_value)
            
            # Get latest Memory metric
            memory_sensor = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.sensor_type == 'memory'
            ).first()
            
            memory_value = 0
            if memory_sensor:
                latest_memory = db.query(Metric).filter(
                    Metric.sensor_id == memory_sensor.id
                ).order_by(Metric.timestamp.desc()).first()
                if latest_memory:
                    memory_value = latest_memory.value
                    memory_values.append(memory_value)
            
            # Get latest Disk metric
            disk_sensor = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.sensor_type == 'disk'
            ).first()
            
            disk_value = 0
            if disk_sensor:
                latest_disk = db.query(Metric).filter(
                    Metric.sensor_id == disk_sensor.id
                ).order_by(Metric.timestamp.desc()).first()
                if latest_disk:
                    disk_value = latest_disk.value
                    disk_values.append(disk_value)
            
            # Get uptime
            uptime_sensor = db.query(Sensor).filter(
                Sensor.server_id == server.id,
                Sensor.sensor_type == 'system'
            ).first()
            
            uptime = "N/A"
            if uptime_sensor:
                latest_uptime = db.query(Metric).filter(
                    Metric.sensor_id == uptime_sensor.id
                ).order_by(Metric.timestamp.desc()).first()
                if latest_uptime:
                    # Convert seconds to human readable
                    days = int(latest_uptime.value // 86400)
                    hours = int((latest_uptime.value % 86400) // 3600)
                    uptime = f"{days}d {hours}h"
            
            # Determine overall status
            status = 'ok'
            if cpu_status == 'critical' or memory_value >= 95 or disk_value >= 95:
                status = 'critical'
            elif cpu_status == 'warning' or memory_value >= 80 or disk_value >= 80:
                status = 'warning'
            
            if status == 'ok':
                servers_online += 1
            
            servers_data.append({
                "id": server.id,
                "name": server.hostname,
                "cpu": round(cpu_value, 1),
                "memory": round(memory_value, 1),
                "disk": round(disk_value, 1),
                "uptime": uptime,
                "status": status
            })
        
        # Calculate summary
        summary = {
            "cpu_avg": round(statistics.mean(cpu_values), 1) if cpu_values else 0,
            "memory_avg": round(statistics.mean(memory_values), 1) if memory_values else 0,
            "disk_avg": round(statistics.mean(disk_values), 1) if disk_values else 0,
            "servers_online": servers_online,
            "servers_total": len(servers)
        }
        
        # Get time series data
        timeseries_cpu = []
        timeseries_memory = []
        timeseries_disk = []
        
        # Sample data points based on time range
        if time_range == '1h':
            interval = timedelta(minutes=5)
            points = 12
        elif time_range == '6h':
            interval = timedelta(minutes=30)
            points = 12
        elif time_range == '24h':
            interval = timedelta(hours=2)
            points = 12
        elif time_range == '7d':
            interval = timedelta(hours=12)
            points = 14
        else:  # 30d
            interval = timedelta(days=2)
            points = 15
        
        for i in range(points):
            point_time = start_time + (interval * i)
            time_str = point_time.strftime('%H:%M' if time_range in ['1h', '6h', '24h'] else '%d/%m')
            
            cpu_point = {"time": time_str}
            memory_point = {"time": time_str}
            disk_point = {"time": time_str}
            
            for server in servers:
                # Get CPU metric near this time
                cpu_sensor = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.sensor_type == 'cpu'
                ).first()
                
                if cpu_sensor:
                    metric = db.query(Metric).filter(
                        Metric.sensor_id == cpu_sensor.id,
                        Metric.timestamp >= point_time,
                        Metric.timestamp < point_time + interval
                    ).order_by(Metric.timestamp.desc()).first()
                    
                    cpu_point[server.hostname] = round(metric.value, 1) if metric else None
                
                # Get Memory metric
                memory_sensor = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.sensor_type == 'memory'
                ).first()
                
                if memory_sensor:
                    metric = db.query(Metric).filter(
                        Metric.sensor_id == memory_sensor.id,
                        Metric.timestamp >= point_time,
                        Metric.timestamp < point_time + interval
                    ).order_by(Metric.timestamp.desc()).first()
                    
                    memory_point[server.hostname] = round(metric.value, 1) if metric else None
                
                # Get Disk metric
                disk_sensor = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.sensor_type == 'disk'
                ).first()
                
                if disk_sensor:
                    metric = db.query(Metric).filter(
                        Metric.sensor_id == disk_sensor.id,
                        Metric.timestamp >= point_time,
                        Metric.timestamp < point_time + interval
                    ).order_by(Metric.timestamp.desc()).first()
                    
                    disk_point[server.hostname] = round(metric.value, 1) if metric else None
            
            timeseries_cpu.append(cpu_point)
            timeseries_memory.append(memory_point)
            timeseries_disk.append(disk_point)
        
        return {
            "summary": summary,
            "servers": servers_data,
            "timeseries": {
                "cpu": timeseries_cpu,
                "memory": timeseries_memory,
                "disk": timeseries_disk
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/network")
async def get_network_dashboard(
    time_range: str = Query('24h', alias="range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get network devices dashboard (APs, Switches)"""
    try:
        start_time = parse_time_range(time_range)
        
        # Get network sensors (SNMP devices)
        network_sensors = db.query(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Sensor.sensor_type.in_(['snmp', 'network', 'ping'])
        ).all()
        
        devices = []
        devices_online = 0
        total_traffic_in = 0
        total_traffic_out = 0
        total_clients = 0
        
        for sensor in network_sensors:
            latest_metric = db.query(Metric).filter(
                Metric.sensor_id == sensor.id
            ).order_by(Metric.timestamp.desc()).first()
            
            if latest_metric:
                status = latest_metric.status
                if status == 'ok':
                    devices_online += 1
                
                # Extract metadata if available
                metadata = latest_metric.extra_metadata or {}
                
                devices.append({
                    "id": sensor.id,
                    "name": sensor.name,
                    "type": sensor.sensor_type,
                    "status": status,
                    "value": latest_metric.value,
                    "clients": metadata.get('clients', 0),
                    "traffic_in": metadata.get('traffic_in', 0),
                    "traffic_out": metadata.get('traffic_out', 0),
                    "signal": metadata.get('signal', 0)
                })
                
                total_clients += metadata.get('clients', 0)
                total_traffic_in += metadata.get('traffic_in', 0)
                total_traffic_out += metadata.get('traffic_out', 0)
        
        return {
            "summary": {
                "devices_total": len(network_sensors),
                "devices_online": devices_online,
                "total_clients": total_clients,
                "traffic_in": round(total_traffic_in / 1024 / 1024, 2),  # MB
                "traffic_out": round(total_traffic_out / 1024 / 1024, 2)  # MB
            },
            "devices": devices,
            "timeseries": {
                "traffic": [],
                "clients": []
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/webapps")
async def get_webapps_dashboard(
    time_range: str = Query('24h', alias="range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get web applications dashboard"""
    try:
        # Get HTTP/HTTPS sensors
        webapp_sensors = db.query(Sensor).join(Server).filter(
            Server.tenant_id == current_user.tenant_id,
            Sensor.sensor_type.in_(['http', 'https', 'ssl'])
        ).all()
        
        apps = []
        apps_online = 0
        response_times = []
        
        for sensor in webapp_sensors:
            latest_metric = db.query(Metric).filter(
                Metric.sensor_id == sensor.id
            ).order_by(Metric.timestamp.desc()).first()
            
            if latest_metric:
                status = latest_metric.status
                if status == 'ok':
                    apps_online += 1
                
                response_time = latest_metric.value
                response_times.append(response_time)
                
                metadata = latest_metric.extra_metadata or {}
                
                apps.append({
                    "id": sensor.id,
                    "name": sensor.name,
                    "url": metadata.get('url', ''),
                    "status": status,
                    "response_time": round(response_time, 2),
                    "status_code": metadata.get('status_code', 0),
                    "ssl_valid": metadata.get('ssl_valid', True),
                    "ssl_expires": metadata.get('ssl_expires', '')
                })
        
        return {
            "summary": {
                "apps_total": len(webapp_sensors),
                "apps_online": apps_online,
                "avg_response_time": round(statistics.mean(response_times), 2) if response_times else 0,
                "error_rate": round((len(webapp_sensors) - apps_online) / len(webapp_sensors) * 100, 1) if webapp_sensors else 0
            },
            "apps": apps,
            "timeseries": {
                "response_time": [],
                "status_codes": []
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/kubernetes")
async def get_kubernetes_dashboard(
    time_range: str = Query('24h', alias="range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get Kubernetes dashboard"""
    try:
        # Get Kubernetes sensors
        k8s_sensors = db.query(Sensor).filter(
            Sensor.sensor_type == 'kubernetes'
        ).all()
        
        clusters = []
        total_pods = 0
        total_cpu = 0
        total_memory = 0
        
        for sensor in k8s_sensors:
            latest_metric = db.query(Metric).filter(
                Metric.sensor_id == sensor.id
            ).order_by(Metric.timestamp.desc()).first()
            
            if latest_metric:
                metadata = latest_metric.extra_metadata or {}
                
                pods = metadata.get('pods', 0)
                cpu = metadata.get('cpu', 0)
                memory = metadata.get('memory', 0)
                
                total_pods += pods
                total_cpu += cpu
                total_memory += memory
                
                clusters.append({
                    "id": sensor.id,
                    "name": sensor.name,
                    "status": latest_metric.status,
                    "pods": pods,
                    "cpu": round(cpu, 1),
                    "memory": round(memory, 1),
                    "nodes": metadata.get('nodes', 0),
                    "namespaces": metadata.get('namespaces', 0)
                })
        
        return {
            "summary": {
                "clusters_total": len(k8s_sensors),
                "pods_total": total_pods,
                "cpu_total": round(total_cpu, 1),
                "memory_total": round(total_memory, 1)
            },
            "clusters": clusters,
            "timeseries": {
                "pods": [],
                "cpu": [],
                "memory": []
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
