"""
Teste direto dos endpoints do NOC
"""
from database import SessionLocal
from models import Server, Sensor, Metric, Incident, User
from datetime import datetime, timedelta
from sqlalchemy import func

db = SessionLocal()

try:
    print(f"\n{'='*60}")
    print(f"TESTE: Endpoints do NOC")
    print(f"{'='*60}\n")
    
    # Buscar usuário admin
    admin = db.query(User).filter(User.email == 'admin@coruja.com').first()
    print(f"Admin encontrado: {admin.email}, role: {admin.role}, tenant_id: {admin.tenant_id}\n")
    
    # 1. Global Status
    print("1. GLOBAL STATUS")
    print("-" * 60)
    
    # Buscar servidores (admin vê todos)
    if admin.role == 'admin':
        servers = db.query(Server).all()
    else:
        servers = db.query(Server).filter(Server.tenant_id == admin.tenant_id).all()
    
    print(f"Total de servidores: {len(servers)}")
    
    servers_ok = 0
    servers_warning = 0
    servers_critical = 0
    
    for server in servers:
        # Pegar última métrica do servidor
        last_metric = db.query(Metric).join(Sensor).filter(
            Sensor.server_id == server.id
        ).order_by(Metric.timestamp.desc()).first()
        
        if last_metric:
            print(f"  - {server.hostname}: {last_metric.status}")
            if last_metric.status == 'critical':
                servers_critical += 1
            elif last_metric.status == 'warning':
                servers_warning += 1
            else:
                servers_ok += 1
        else:
            print(f"  - {server.hostname}: sem métricas")
            servers_ok += 1
    
    print(f"\nResumo:")
    print(f"  OK: {servers_ok}")
    print(f"  Warning: {servers_warning}")
    print(f"  Critical: {servers_critical}")
    
    # 2. Active Incidents
    print(f"\n2. ACTIVE INCIDENTS")
    print("-" * 60)
    
    if admin.role == 'admin':
        incidents = db.query(Incident).join(Sensor).join(Server).filter(
            Incident.resolved_at.is_(None)
        ).all()
    else:
        incidents = db.query(Incident).join(Sensor).join(Server).filter(
            Server.tenant_id == admin.tenant_id,
            Incident.resolved_at.is_(None)
        ).all()
    
    print(f"Total de incidentes ativos: {len(incidents)}")
    for incident in incidents:
        print(f"  - {incident.sensor.server.hostname} / {incident.sensor.name}")
        print(f"    Severity: {incident.severity}")
        print(f"    Created: {incident.created_at}")
    
    # 3. KPIs
    print(f"\n3. KPIs")
    print("-" * 60)
    
    # Incidentes 24h
    if admin.role == 'admin':
        incidents_24h = db.query(Incident).join(Sensor).join(Server).filter(
            Incident.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
    else:
        incidents_24h = db.query(Incident).join(Sensor).join(Server).filter(
            Server.tenant_id == admin.tenant_id,
            Incident.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
    
    print(f"Incidentes 24h: {incidents_24h}")
    
    # SLA
    if admin.role == 'admin':
        total_metrics = db.query(Metric).join(Sensor).join(Server).filter(
            Metric.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        ok_metrics = db.query(Metric).join(Sensor).join(Server).filter(
            Metric.status == 'ok',
            Metric.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).count()
    else:
        total_metrics = db.query(Metric).join(Sensor).join(Server).filter(
            Server.tenant_id == admin.tenant_id,
            Metric.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        ok_metrics = db.query(Metric).join(Sensor).join(Server).filter(
            Server.tenant_id == admin.tenant_id,
            Metric.status == 'ok',
            Metric.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).count()
    
    sla = (ok_metrics / total_metrics * 100) if total_metrics > 0 else 100
    
    print(f"Total métricas 30d: {total_metrics}")
    print(f"Métricas OK: {ok_metrics}")
    print(f"SLA: {sla:.2f}%")
    
    print(f"\n{'='*60}")
    print(f"✅ TESTE CONCLUÍDO")
    print(f"{'='*60}\n")
    
finally:
    db.close()
