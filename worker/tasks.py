from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta, timezone
from pathlib import Path
import httpx
import sys
import subprocess
import os

from config import settings
from database import SessionLocal
from models import Metric, Sensor, Incident, RemediationLog, Server
from threshold_evaluator import evaluate_thresholds
from self_healing import attempt_remediation
from sla_calculator import calculate_monthly_sla

# Logger do Celery
logger = get_task_logger(__name__)

app = Celery('coruja_worker')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.result_backend = settings.CELERY_RESULT_BACKEND

app.conf.beat_schedule = {
    'ping-all-servers-every-minute': {
        'task': 'tasks.ping_all_servers',
        'schedule': 60.0,  # A cada 60 segundos
    },
    'evaluate-thresholds-every-minute': {
        'task': 'tasks.evaluate_all_thresholds',
        'schedule': 60.0,
    },
    'calculate-monthly-sla': {
        'task': 'tasks.generate_monthly_reports',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
    },
    'auto-backup-5-times-daily': {
        'task': 'tasks.create_automatic_backup',
        'schedule': crontab(hour='*/5'),  # A cada 5 horas = 5x ao dia (0h, 5h, 10h, 15h, 20h)
    },
}

@app.task
def evaluate_all_thresholds():
    """Evaluate thresholds for all active sensors"""
    db = SessionLocal()
    try:
        sensors = db.query(Sensor).filter(Sensor.is_active == True).all()
        
        for sensor in sensors:
            # Get latest metric
            latest_metric = db.query(Metric).filter(
                Metric.sensor_id == sensor.id
            ).order_by(Metric.timestamp.desc()).first()
            
            if not latest_metric:
                continue
            
            # Evaluate threshold
            threshold_breached, severity = evaluate_thresholds(
                sensor, latest_metric.value
            )
            
            if threshold_breached:
                # Check if there's already an open incident
                existing_incident = db.query(Incident).filter(
                    Incident.sensor_id == sensor.id,
                    Incident.status == "open"
                ).first()
                
                if not existing_incident:
                    # Get sensor type specific description
                    description = get_incident_description(sensor, latest_metric)
                    
                    # Create new incident
                    incident = Incident(
                        sensor_id=sensor.id,
                        severity=severity,
                        status="open",
                        title=f"{sensor.name} - Limite {severity} ultrapassado",
                        description=description
                    )
                    db.add(incident)
                    db.commit()
                    db.refresh(incident)
                    
                    print(f"✅ Incidente criado: {incident.title} (ID: {incident.id})")
                    
                    # Execute AIOps analysis automatically
                    execute_aiops_analysis.delay(incident.id)
                    
                    # Attempt self-healing
                    attempt_self_healing.delay(incident.id)
                else:
                    # Update existing incident severity if it changed
                    if existing_incident.severity != severity:
                        existing_incident.severity = severity
                        db.commit()
                        print(f"⚠️ Incidente {existing_incident.id} atualizado para {severity}")
            else:
                # Check if we should auto-resolve incidents
                # Auto-resolve both 'open' and 'acknowledged' incidents when sensor is back to normal
                open_incidents = db.query(Incident).filter(
                    Incident.sensor_id == sensor.id,
                    Incident.status.in_(['open', 'acknowledged'])
                ).all()
                
                for incident in open_incidents:
                    incident.status = "resolved"
                    incident.resolved_at = datetime.now(timezone.utc)
                    incident.resolution_notes = "Auto-resolvido: sensor voltou ao normal"
                    db.commit()
                    logger.info(f"✅ Incidente {incident.id} auto-resolvido (sensor {sensor.name} voltou ao normal)")
                    print(f"✅ Incidente {incident.id} auto-resolvido")
        
    except Exception as e:
        print(f"❌ Erro ao avaliar thresholds: {e}")
    finally:
        db.close()


def get_incident_description(sensor, metric):
    """Generate incident description based on sensor type"""
    value = metric.value
    unit = metric.unit
    
    if sensor.sensor_type == 'cpu':
        return f"CPU em {value:.1f}% (Crítico: {sensor.threshold_critical}%, Aviso: {sensor.threshold_warning}%)"
    elif sensor.sensor_type == 'memory':
        return f"Memória em {value:.1f}% (Crítico: {sensor.threshold_critical}%, Aviso: {sensor.threshold_warning}%)"
    elif sensor.sensor_type == 'disk':
        return f"Disco em {value:.1f}% (Crítico: {sensor.threshold_critical}%, Aviso: {sensor.threshold_warning}%)"
    elif sensor.sensor_type == 'ping':
        if value == 0:
            return f"Servidor OFFLINE - Ping sem resposta"
        else:
            return f"Latência alta: {value:.0f}ms (Crítico: {sensor.threshold_critical}ms, Aviso: {sensor.threshold_warning}ms)"
    elif sensor.sensor_type == 'network':
        mbps = value / 1024 / 1024
        return f"Tráfego de rede: {mbps:.2f} MB/s (Crítico: {sensor.threshold_critical} MB/s, Aviso: {sensor.threshold_warning} MB/s)"
    elif sensor.sensor_type == 'service':
        return f"Serviço parado ou não respondendo"
    else:
        return f"Valor: {value}, Limite crítico: {sensor.threshold_critical}, Limite aviso: {sensor.threshold_warning}"

@app.task
def attempt_self_healing(incident_id: int):
    """Attempt automatic remediation for an incident"""
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return
        
        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        
        # Attempt remediation based on sensor type
        success, action_description, before_state, after_state, error_message = attempt_remediation(
            sensor, incident
        )
        
        # Log remediation attempt
        remediation_log = RemediationLog(
            incident_id=incident.id,
            action_type=f"auto_remediation_{sensor.sensor_type}",
            action_description=action_description,
            before_state=before_state,
            after_state=after_state,
            success=success,
            error_message=error_message
        )
        db.add(remediation_log)
        
        incident.remediation_attempted = True
        incident.remediation_successful = success
        
        db.commit()
        
        # Request AI analysis
        request_ai_analysis.delay(incident_id)
        
    finally:
        db.close()

@app.task
def request_ai_analysis(incident_id: int):
    """Request AI analysis for an incident"""
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return
        
        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        server = db.query(Server).filter(Server.id == sensor.server_id).first()
        
        # Get recent metrics (última hora)
        recent_metrics = db.query(Metric).filter(
            Metric.sensor_id == sensor.id,
            Metric.timestamp >= datetime.now(timezone.utc) - timedelta(hours=1)
        ).order_by(Metric.timestamp.desc()).limit(60).all()
        
        # Call AI Agent
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{settings.AI_AGENT_URL}/api/v1/analyze/root-cause",
                    json={
                        "incident_id": incident.id,
                        "sensor_type": sensor.sensor_type,
                        "sensor_name": sensor.name,
                        "server_hostname": server.hostname,
                        "current_value": recent_metrics[0].value if recent_metrics else None,
                        "threshold_critical": sensor.threshold_critical,
                        "threshold_warning": sensor.threshold_warning,
                        "recent_metrics": [
                            {"value": m.value, "timestamp": m.timestamp.isoformat()}
                            for m in recent_metrics
                        ],
                        "remediation_attempted": incident.remediation_attempted,
                        "remediation_successful": incident.remediation_successful
                    }
                )
                
                if response.status_code == 200:
                    ai_result = response.json()
                    incident.root_cause = ai_result.get("root_cause")
                    incident.ai_analysis = ai_result.get("analysis")
                    db.commit()
        except Exception as e:
            print(f"AI analysis failed: {e}")
    
    finally:
        db.close()

@app.task
def generate_monthly_reports():
    """Generate monthly SLA reports for all tenants"""
    db = SessionLocal()
    try:
        from models import Tenant
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        
        # Previous month (calcular mês anterior)
        today = datetime.now(timezone.utc)
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1
        
        for tenant in tenants:
            calculate_monthly_sla(db, tenant.id, year, month)
    
    finally:
        db.close()


@app.task
def execute_aiops_analysis(incident_id: int):
    """Execute complete AIOps analysis automatically when incident is created"""
    logger.info(f"🤖 Iniciando análise AIOps automática para incidente {incident_id}")
    db = SessionLocal()
    
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            logger.error(f"Incidente {incident_id} não encontrado")
            return
        
        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        server = db.query(Server).filter(Server.id == sensor.server_id).first()
        
        logger.info(f"🔍 Executando análise para {sensor.name} em {server.hostname}")
        
        # Get metrics history (last 2 hours)
        metrics_since = incident.created_at - timedelta(hours=2)
        metrics = db.query(Metric).filter(
            Metric.sensor_id == sensor.id,
            Metric.timestamp >= metrics_since,
            Metric.timestamp <= incident.created_at
        ).order_by(Metric.timestamp.asc()).all()
        
        # Get current value from latest metric
        current_value = None
        if metrics:
            current_value = metrics[-1].value
        
        # Prepare incident data for AIOps
        incident_data = {
            "id": incident.id,
            "server_id": sensor.server_id,
            "server_hostname": server.hostname,
            "sensor_id": sensor.id,
            "sensor_name": sensor.name,
            "sensor_type": sensor.sensor_type,
            "severity": incident.severity,
            "current_value": current_value,
            "threshold_warning": sensor.threshold_warning,
            "threshold_critical": sensor.threshold_critical,
            "created_at": incident.created_at.isoformat()
        }
        
        metrics_data = [
            {
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "status": m.status
            }
            for m in metrics
        ]
        
        # Call AIOps API for Root Cause Analysis
        aiops_result = {}
        action_plan = {}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                # 1. Root Cause Analysis
                logger.info("📊 Executando análise de causa raiz...")
                rca_response = client.post(
                    "http://coruja-api:8000/api/v1/aiops/root-cause-analysis",
                    json={"incident_id": incident.id},
                    headers={"Authorization": f"Bearer {get_system_token()}"}
                )
                
                if rca_response.status_code == 200:
                    aiops_result = rca_response.json()
                    logger.info(f"✅ RCA concluído: {aiops_result.get('root_cause', 'N/A')}")
                    
                    # Store RCA result in incident
                    incident.root_cause = aiops_result.get('root_cause')
                    incident.ai_analysis = {
                        'rca': aiops_result,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    db.commit()
                else:
                    logger.warning(f"⚠️ RCA falhou: {rca_response.status_code}")
                
                # 2. Create Action Plan
                logger.info("📋 Criando plano de ação...")
                plan_response = client.post(
                    f"http://coruja-api:8000/api/v1/aiops/action-plan/{incident.id}?include_correlation=true",
                    headers={"Authorization": f"Bearer {get_system_token()}"}
                )
                
                if plan_response.status_code == 200:
                    action_plan = plan_response.json()
                    logger.info(f"✅ Plano de ação criado: {action_plan.get('plan_id')}")
                    
                    # Update incident with action plan
                    if incident.ai_analysis:
                        incident.ai_analysis['action_plan'] = action_plan
                    else:
                        incident.ai_analysis = {'action_plan': action_plan}
                    db.commit()
                else:
                    logger.warning(f"⚠️ Plano de ação falhou: {plan_response.status_code}")
                    
        except Exception as e:
            logger.error(f"❌ Erro na análise AIOps: {e}")
        
        # Now send notifications with AIOps analysis included
        logger.info("📧 Enviando notificações com análise AIOps...")
        send_incident_notifications_with_aiops.delay(incident.id, aiops_result, action_plan)
        
    except Exception as e:
        logger.error(f"❌ Erro ao executar análise AIOps: {e}", exc_info=True)
    finally:
        db.close()


def get_system_token():
    """Get system authentication token for internal API calls"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                "http://coruja-api:8000/api/v1/auth/login",
                json={"email": "admin@coruja.com", "password": "admin123"}
            )
            if response.status_code == 200:
                return response.json().get('access_token')
    except:
        pass
    return None


@app.task
def send_incident_notifications_with_aiops(incident_id: int, aiops_result: dict = None, action_plan: dict = None):
    """Send notifications with AIOps analysis included"""
    logger.info(f"🔔 Enviando notificações com AIOps para incidente {incident_id}")
    db = SessionLocal()
    
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            logger.error(f"Incidente {incident_id} não encontrado")
            return
        
        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        server = db.query(Server).filter(Server.id == sensor.server_id).first()
        
        # Get tenant notification config
        from models import Tenant
        tenant = db.query(Tenant).filter(Tenant.id == server.tenant_id).first()
        
        if not tenant or not tenant.notification_config:
            logger.warning(f"Tenant {server.tenant_id} sem configuração de notificações")
            return
        
        notification_config = tenant.notification_config
        
        # Prepare enhanced incident data with AIOps
        incident_description = incident.description
        
        # Add AIOps analysis to description
        if aiops_result:
            incident_description += f"\n\n🤖 ANÁLISE AIOPS:\n"
            incident_description += f"Causa Raiz: {aiops_result.get('root_cause', 'N/A')}\n"
            incident_description += f"Confiança: {int(aiops_result.get('confidence', 0) * 100)}%\n"
            
            if aiops_result.get('symptoms'):
                incident_description += f"\nSintomas Detectados: {len(aiops_result['symptoms'])}\n"
            
            if aiops_result.get('contributing_factors'):
                incident_description += f"\nFatores Contribuintes:\n"
                for factor in aiops_result['contributing_factors'][:3]:
                    incident_description += f"  • {factor}\n"
        
        # Add Action Plan to description
        if action_plan:
            incident_description += f"\n📋 PLANO DE AÇÃO:\n"
            incident_description += f"ID: {action_plan.get('plan_id')}\n"
            incident_description += f"Tempo Estimado: {action_plan.get('estimated_resolution_time')}\n"
            
            if action_plan.get('immediate_actions'):
                incident_description += f"\n🚨 AÇÕES IMEDIATAS:\n"
                for i, action in enumerate(action_plan['immediate_actions'][:3], 1):
                    incident_description += f"{i}. {action.get('action')}\n"
                    if action.get('command'):
                        incident_description += f"   Comando: {action['command']}\n"
                    incident_description += f"   Tempo: {action.get('estimated_time')}\n"
        
        incident_data = {
            'title': incident.title,
            'description': incident_description,
            'severity': incident.severity,
            'server_hostname': server.hostname,
            'sensor_name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'incident_id': incident.id,
            'created_at': incident.created_at.isoformat() if incident.created_at else None,
            'aiops_analysis': aiops_result,
            'action_plan': action_plan
        }
        
        # Send to all enabled channels
        notifications_sent = []
        notifications_failed = []
        
        # TOPdesk
        if notification_config.get('topdesk', {}).get('enabled'):
            try:
                result = send_topdesk_notification_sync(notification_config['topdesk'], incident_data)
                if result.get('success'):
                    notifications_sent.append(f"TOPdesk: {result.get('incident_id')}")
                    logger.info(f"✅ TOPdesk: Chamado {result.get('incident_id')} criado com AIOps")
                else:
                    notifications_failed.append(f"TOPdesk: {result.get('error')}")
            except Exception as e:
                notifications_failed.append(f"TOPdesk: {str(e)}")
        
        # Teams
        if notification_config.get('teams', {}).get('enabled'):
            try:
                result = send_teams_notification_sync(notification_config['teams'], incident_data)
                if result.get('success'):
                    notifications_sent.append("Teams")
                    logger.info(f"✅ Teams: Mensagem enviada com AIOps")
                else:
                    notifications_failed.append(f"Teams: {result.get('error')}")
            except Exception as e:
                notifications_failed.append(f"Teams: {str(e)}")
        
        # Dynamics 365
        if notification_config.get('dynamics365', {}).get('enabled'):
            try:
                result = send_dynamics365_notification_sync(notification_config['dynamics365'], incident_data)
                if result.get('success'):
                    notifications_sent.append(f"Dynamics 365: {result.get('incident_id')}")
                    logger.info(f"✅ Dynamics 365: Incidente {result.get('incident_id')} criado com AIOps")
                else:
                    notifications_failed.append(f"Dynamics 365: {result.get('error')}")
            except Exception as e:
                notifications_failed.append(f"Dynamics 365: {str(e)}")
        
        # Email
        if notification_config.get('email', {}).get('enabled'):
            try:
                result = send_email_notification_sync(notification_config['email'], incident_data)
                if result.get('success'):
                    notifications_sent.append("Email")
                    logger.info(f"✅ Email: Enviado com AIOps")
                else:
                    notifications_failed.append(f"Email: {result.get('error')}")
            except Exception as e:
                notifications_failed.append(f"Email: {str(e)}")
        
        logger.info(f"📊 Resumo: {len(notifications_sent)} enviadas, {len(notifications_failed)} falharam")
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificações: {e}", exc_info=True)
    finally:
        db.close()


@app.task
def send_incident_notifications(incident_id: int):
    """Send notifications for a new incident to all configured channels"""
    print(f"🔔 INICIANDO envio de notificações para incidente {incident_id}", flush=True)
    sys.stdout.flush()
    logger.info(f"🔔 INICIANDO envio de notificações para incidente {incident_id}")
    db = SessionLocal()
    try:
        print(f"DEBUG: Buscando incidente {incident_id}...", flush=True)
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            print(f"❌ Incidente {incident_id} não encontrado", flush=True)
            logger.error(f"❌ Incidente {incident_id} não encontrado")
            return
        
        print(f"DEBUG: Incidente encontrado: {incident.title}", flush=True)
        
        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        print(f"DEBUG: Sensor encontrado: {sensor.name}", flush=True)
        
        server = db.query(Server).filter(Server.id == sensor.server_id).first()
        print(f"DEBUG: Server encontrado: {server.hostname}", flush=True)
        
        print(f"📋 Sensor: {sensor.name}, Server: {server.hostname}", flush=True)
        
        # Get tenant notification config
        from models import Tenant
        tenant = db.query(Tenant).filter(Tenant.id == server.tenant_id).first()
        print(f"DEBUG: Tenant encontrado: {tenant.name if tenant else 'None'}", flush=True)
        
        if not tenant or not tenant.notification_config:
            print(f"⚠️ Tenant {server.tenant_id} sem configuração de notificações", flush=True)
            logger.warning(f"⚠️ Tenant {server.tenant_id} sem configuração de notificações")
            return
        
        notification_config = tenant.notification_config
        print(f"DEBUG: Configuração encontrada, TOPdesk enabled: {notification_config.get('topdesk', {}).get('enabled')}", flush=True)
        print(f"📋 Configuração encontrada para tenant {tenant.name}", flush=True)
        logger.info(f"📋 Configuração encontrada para tenant {tenant.name}")
        
        # Prepare incident data
        incident_data = {
            'title': incident.title,
            'description': incident.description,
            'severity': incident.severity,
            'server_hostname': server.hostname,
            'sensor_name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'incident_id': incident.id,
            'created_at': incident.created_at.isoformat() if incident.created_at else None
        }
        
        logger.info(f"📢 Enviando notificações para incidente {incident_id}: {incident.title}")
        
        # Send to all enabled channels
        notifications_sent = []
        notifications_failed = []
        
        # TOPdesk
        if notification_config.get('topdesk', {}).get('enabled'):
            logger.info("🔵 TOPdesk está habilitado, tentando enviar...")
            try:
                result = send_topdesk_notification_sync(notification_config['topdesk'], incident_data)
                if result.get('success'):
                    notifications_sent.append(f"TOPdesk: {result.get('incident_id')}")
                    logger.info(f"✅ TOPdesk: Chamado {result.get('incident_id')} criado")
                else:
                    notifications_failed.append(f"TOPdesk: {result.get('error')}")
                    logger.error(f"❌ TOPdesk: {result.get('error')}")
            except Exception as e:
                notifications_failed.append(f"TOPdesk: {str(e)}")
                logger.error(f"❌ TOPdesk exception: {e}")
        else:
            logger.info("⚪ TOPdesk desabilitado")
        
        # Teams
        if notification_config.get('teams', {}).get('enabled'):
            logger.info("🔵 Teams está habilitado, tentando enviar...")
            try:
                result = send_teams_notification_sync(notification_config['teams'], incident_data)
                if result.get('success'):
                    notifications_sent.append("Teams")
                    logger.info(f"✅ Teams: Mensagem enviada")
                else:
                    notifications_failed.append(f"Teams: {result.get('error')}")
                    logger.error(f"❌ Teams: {result.get('error')}")
            except Exception as e:
                notifications_failed.append(f"Teams: {str(e)}")
                logger.error(f"❌ Teams exception: {e}")
        else:
            logger.info("⚪ Teams desabilitado")
        
        # Dynamics 365
        if notification_config.get('dynamics365', {}).get('enabled'):
            logger.info("🔵 Dynamics 365 está habilitado, tentando enviar...")
            try:
                result = send_dynamics365_notification_sync(notification_config['dynamics365'], incident_data)
                if result.get('success'):
                    notifications_sent.append(f"Dynamics 365: {result.get('incident_id')}")
                    logger.info(f"✅ Dynamics 365: Incidente {result.get('incident_id')} criado")
                else:
                    notifications_failed.append(f"Dynamics 365: {result.get('error')}")
                    logger.error(f"❌ Dynamics 365: {result.get('error')}")
            except Exception as e:
                notifications_failed.append(f"Dynamics 365: {str(e)}")
                logger.error(f"❌ Dynamics 365 exception: {e}")
        else:
            logger.info("⚪ Dynamics 365 desabilitado")
        
        # Email
        if notification_config.get('email', {}).get('enabled'):
            logger.info("🔵 Email está habilitado, tentando enviar...")
            try:
                result = send_email_notification_sync(notification_config['email'], incident_data)
                if result.get('success'):
                    notifications_sent.append("Email")
                    logger.info(f"✅ Email: Enviado")
                else:
                    notifications_failed.append(f"Email: {result.get('error')}")
                    logger.error(f"❌ Email: {result.get('error')}")
            except Exception as e:
                notifications_failed.append(f"Email: {str(e)}")
                logger.error(f"❌ Email exception: {e}")
        else:
            logger.info("⚪ Email desabilitado")
        
        logger.info(f"📊 Resumo: {len(notifications_sent)} enviadas, {len(notifications_failed)} falharam")
        if notifications_sent:
            logger.info(f"   ✅ Enviadas: {', '.join(notifications_sent)}")
        if notifications_failed:
            logger.error(f"   ❌ Falharam: {', '.join(notifications_failed)}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificações: {e}", exc_info=True)
    finally:
        db.close()


def send_topdesk_notification_sync(config: dict, incident_data: dict) -> dict:
    """Send notification to TOPdesk (synchronous)"""
    import httpx
    import base64
    
    url = config.get('url', '').rstrip('/')
    username = config.get('username')
    password = config.get('password')
    
    if not all([url, username, password]):
        return {'success': False, 'error': 'TOPdesk configuration incomplete'}
    
    # Basic authentication
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/json'
    }
    
    # Build payload
    payload = {
        'callerLookup': {'loginName': username},
        'briefDescription': incident_data.get('title', 'Alerta do Coruja Monitor'),
        'request': f"{incident_data.get('description', '')}\n\nServidor: {incident_data.get('server_hostname')}\nSensor: {incident_data.get('sensor_name')}\nSeveridade: {incident_data.get('severity')}"
    }
    
    # Add optional fields
    if config.get('category'):
        payload['category'] = {'name': config.get('category')}
    if config.get('subcategory'):
        payload['subcategory'] = {'name': config.get('subcategory')}
    if config.get('operator_group'):
        payload['operatorGroup'] = {'name': config.get('operator_group')}
    
    try:
        with httpx.Client(timeout=30.0, verify=False) as client:
            response = client.post(
                f"{url}/tas/api/incidents",
                headers=headers,
                json=payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'incident_id': result.get('number'),
                    'incident_url': f"{url}/tas/secure/incident?unid={result.get('id')}"
                }
            else:
                return {
                    'success': False,
                    'error': f"TOPdesk API error: {response.status_code}"
                }
    except Exception as e:
        return {
            'success': False,
            'error': f"TOPdesk connection error: {str(e)}"
        }


def send_teams_notification_sync(config: dict, incident_data: dict) -> dict:
    """Send notification to Microsoft Teams (synchronous)"""
    import httpx
    
    webhook_url = config.get('webhook_url')
    if not webhook_url:
        return {'success': False, 'error': 'Teams webhook URL not configured'}
    
    # Determine color based on severity
    severity = incident_data.get('severity', 'warning')
    color_map = {
        'critical': 'FF0000',  # Red
        'warning': 'FFA500',   # Orange
        'info': '0078D4'       # Blue
    }
    theme_color = color_map.get(severity, 'FFA500')
    
    # Build Teams message card
    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": incident_data.get('title', 'Alerta do Coruja Monitor'),
        "themeColor": theme_color,
        "title": f"🚨 {incident_data.get('title', 'Alerta do Coruja Monitor')}",
        "sections": [
            {
                "activityTitle": "Novo Incidente Detectado",
                "activitySubtitle": incident_data.get('created_at', ''),
                "facts": [
                    {"name": "Servidor:", "value": incident_data.get('server_hostname', 'N/A')},
                    {"name": "Sensor:", "value": incident_data.get('sensor_name', 'N/A')},
                    {"name": "Tipo:", "value": incident_data.get('sensor_type', 'N/A')},
                    {"name": "Severidade:", "value": severity.upper()},
                    {"name": "Descrição:", "value": incident_data.get('description', 'N/A')}
                ]
            }
        ]
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(webhook_url, json=card)
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Mensagem enviada para o Teams'}
            else:
                return {'success': False, 'error': f"Teams API error: {response.status_code}"}
    except Exception as e:
        return {'success': False, 'error': f"Teams connection error: {str(e)}"}


def send_email_notification_sync(config: dict, incident_data: dict) -> dict:
    """Send email notification (synchronous)"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    smtp_server = config.get('smtp_server')
    smtp_port = config.get('smtp_port', 587)
    smtp_user = config.get('smtp_user')
    smtp_password = config.get('smtp_password')
    from_email = config.get('from_email')
    to_emails = config.get('to_emails', [])
    use_tls = config.get('use_tls', True)
    
    if not all([smtp_server, smtp_user, smtp_password, from_email, to_emails]):
        return {'success': False, 'error': 'Email configuration incomplete'}
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 {incident_data.get('title', 'Alerta do Coruja Monitor')}"
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        
        # Plain text version
        text_body = f"""
Novo Incidente Detectado

Servidor: {incident_data.get('server_hostname', 'N/A')}
Sensor: {incident_data.get('sensor_name', 'N/A')}
Tipo: {incident_data.get('sensor_type', 'N/A')}
Severidade: {incident_data.get('severity', 'N/A').upper()}

Descrição:
{incident_data.get('description', 'N/A')}

Data/Hora: {incident_data.get('created_at', 'N/A')}

---
Coruja Monitor - Sistema de Monitoramento
"""
        
        # HTML version
        severity_color = '#dc3545' if incident_data.get('severity') == 'critical' else '#ffc107'
        html_body = f"""
<html>
  <head>
    <style>
      body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
      .header {{ background-color: {severity_color}; color: white; padding: 20px; text-align: center; }}
      .content {{ padding: 20px; background-color: #f4f4f4; }}
      .alert-box {{ background-color: white; border-left: 4px solid {severity_color}; padding: 15px; margin: 20px 0; }}
      .details {{ background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
      .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }}
    </style>
  </head>
  <body>
    <div class="header">
      <h1>🚨 Novo Incidente Detectado</h1>
    </div>
    <div class="content">
      <div class="alert-box">
        <h2>{incident_data.get('title', 'Alerta do Coruja Monitor')}</h2>
        <p><strong>Severidade:</strong> {incident_data.get('severity', 'N/A').upper()}</p>
      </div>
      <div class="details">
        <p><strong>Servidor:</strong> {incident_data.get('server_hostname', 'N/A')}</p>
        <p><strong>Sensor:</strong> {incident_data.get('sensor_name', 'N/A')}</p>
        <p><strong>Tipo:</strong> {incident_data.get('sensor_type', 'N/A')}</p>
        <p><strong>Descrição:</strong> {incident_data.get('description', 'N/A')}</p>
        <p><strong>Data/Hora:</strong> {incident_data.get('created_at', 'N/A')}</p>
      </div>
    </div>
    <div class="footer">
      <p>Este é um e-mail automático do Coruja Monitor. Não responda a este e-mail.</p>
      <p>© 2026 Coruja Monitor - Sistema de Monitoramento</p>
    </div>
  </body>
</html>
"""
        
        # Attach both versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_emails, msg.as_string())
        server.quit()
        
        return {'success': True, 'message': f'E-mail enviado para {len(to_emails)} destinatário(s)'}
        
    except Exception as e:
        return {'success': False, 'error': f'Erro ao enviar e-mail: {str(e)}'}


@app.task
def create_automatic_backup():
    """Cria backup automático do banco de dados 5x ao dia"""
    try:
        logger.info("🔄 Iniciando backup automático do banco de dados...")
        
        BACKUP_DIR = Path("/app/backups")
        BACKUP_DIR.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"coruja_backup_{timestamp}.sql"
        backup_path = BACKUP_DIR / backup_filename
        
        # Executar pg_dump
        cmd = [
            "pg_dump",
            "-h", settings.POSTGRES_HOST,
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", str(backup_path)
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Backup falhou: {result.stderr}")
            return {"success": False, "error": result.stderr}
        
        # Verificar se arquivo foi criado
        if not backup_path.exists():
            logger.error("❌ Arquivo de backup não foi criado")
            return {"success": False, "error": "Arquivo não criado"}
        
        stat = backup_path.stat()
        size_mb = round(stat.st_size / (1024 * 1024), 2)
        
        logger.info(f"✅ Backup automático criado: {backup_filename} ({size_mb} MB)")
        
        # Limpar backups antigos (manter últimos 30)
        cleanup_old_backups(BACKUP_DIR, keep_last=30)
        
        return {
            "success": True,
            "filename": backup_filename,
            "size_mb": size_mb
        }
    except Exception as e:
        logger.error(f"❌ Erro ao criar backup automático: {str(e)}")
        return {"success": False, "error": str(e)}

def cleanup_old_backups(backup_dir: Path, keep_last: int = 30):
    """Remove backups antigos, mantendo apenas os últimos N"""
    try:
        backups = sorted(backup_dir.glob("*.sql"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if len(backups) > keep_last:
            for old_backup in backups[keep_last:]:
                logger.info(f"🗑️ Removendo backup antigo: {old_backup.name}")
                old_backup.unlink()
    except Exception as e:
        logger.error(f"❌ Erro ao limpar backups antigos: {str(e)}")



def send_dynamics365_notification_sync(config: dict, incident_data: dict) -> dict:
    """Send notification to Microsoft Dynamics 365 (synchronous)"""
    import httpx
    
    url = config.get('url', '').rstrip('/')
    tenant_id = config.get('tenant_id')
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    resource = config.get('resource', url)
    api_version = config.get('api_version', '9.2')
    incident_type = config.get('incident_type', 'incident')
    
    if not all([url, tenant_id, client_id, client_secret]):
        return {'success': False, 'error': 'Dynamics 365 configuration incomplete'}
    
    try:
        with httpx.Client(timeout=60.0, verify=False) as client:
            # Step 1: Get OAuth2 token
            token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'resource': resource
            }
            
            token_response = client.post(token_url, data=token_data)
            
            if token_response.status_code != 200:
                return {
                    'success': False,
                    'error': f"OAuth2 authentication failed: {token_response.status_code}"
                }
            
            access_token = token_response.json().get('access_token')
            
            # Step 2: Create incident
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0',
                'Accept': 'application/json',
                'Prefer': 'return=representation'
            }
            
            # Map severity to priority
            priority_map = {
                'critical': 1,  # High
                'warning': 2,   # Normal
                'info': 3       # Low
            }
            priority = priority_map.get(incident_data.get('severity', 'warning'), 2)
            
            # Build payload
            description = f"{incident_data.get('description', '')}\n\n"
            description += f"Servidor: {incident_data.get('server_hostname')}\n"
            description += f"Sensor: {incident_data.get('sensor_name')}\n"
            description += f"Tipo: {incident_data.get('sensor_type')}\n"
            description += f"Severidade: {incident_data.get('severity')}"
            
            payload = {
                'title': incident_data.get('title', 'Alerta do Coruja Monitor')[:200],
                'description': description[:2000],
                'prioritycode': priority,
                'caseorigincode': 3,  # Web
                'casetypecode': 1,    # Problem
                'statecode': 0,       # Active
                'statuscode': 1       # In Progress
            }
            
            # Add owner if configured
            if config.get('owner_id'):
                payload['ownerid@odata.bind'] = f"/systemusers({config.get('owner_id')})"
            
            # Create incident
            api_endpoint = f"{url}/api/data/v{api_version}/{incident_type}s"
            incident_response = client.post(
                api_endpoint,
                headers=headers,
                json=payload
            )
            
            if incident_response.status_code in [200, 201, 204]:
                # Get incident ID
                if incident_response.status_code == 204:
                    entity_id_header = incident_response.headers.get('OData-EntityId', '')
                    incident_id = entity_id_header.split('(')[-1].split(')')[0] if '(' in entity_id_header else 'unknown'
                else:
                    result = incident_response.json()
                    incident_id = result.get('incidentid') or result.get('id', 'unknown')
                
                return {
                    'success': True,
                    'incident_id': incident_id,
                    'incident_url': f"{url}/main.aspx?pagetype=entityrecord&etn={incident_type}&id={incident_id}"
                }
            else:
                return {
                    'success': False,
                    'error': f"Dynamics 365 API error: {incident_response.status_code}"
                }
                
    except Exception as e:
        return {
            'success': False,
            'error': f"Dynamics 365 connection error: {str(e)}"
        }


@app.task
def ping_all_servers():
    """
    Faz PING em todos os servidores ativos direto do servidor Linux.
    Cria sensor PING automaticamente se não existir.
    Igual ao PRTG - PING independente de probe/SNMP/WMI.
    """
    logger.info("🏓 Iniciando PING de todos os servidores...")
    db = SessionLocal()
    
    try:
        servers = db.query(Server).filter(Server.is_active == True).all()
        logger.info(f"📊 Encontrados {len(servers)} servidores ativos para fazer PING")
        
        for server in servers:
            try:
                # Execute ping
                latency_ms = execute_ping(server.ip_address)
                logger.debug(f"🏓 PING {server.hostname} ({server.ip_address}): {latency_ms}ms")
                
                # Get or create PING sensor
                # Buscar por qualquer nome (ping, PING, Ping) para evitar duplicação
                ping_sensor = db.query(Sensor).filter(
                    Sensor.server_id == server.id,
                    Sensor.sensor_type == 'ping'
                ).first()
                
                if not ping_sensor:
                    # Create PING sensor automatically (nome maiúsculo para consistência com API)
                    logger.info(f"✨ Criando sensor PING automático para {server.hostname}")
                    ping_sensor = Sensor(
                        server_id=server.id,
                        sensor_type='ping',
                        name='PING',  # Maiúsculo para consistência com API
                        threshold_warning=100,
                        threshold_critical=200,
                        is_active=True
                    )
                    db.add(ping_sensor)
                    db.commit()
                    db.refresh(ping_sensor)
                else:
                    # Normalizar nome para PING (maiúsculo) se estiver diferente
                    if ping_sensor.name != 'PING':
                        logger.info(f"🔄 Normalizando nome do sensor PING de '{ping_sensor.name}' para 'PING'")
                        ping_sensor.name = 'PING'
                        db.commit()
                
                # Determine status
                if latency_ms == 0:
                    status = 'critical'  # Offline
                elif latency_ms > ping_sensor.threshold_critical:
                    status = 'critical'
                elif latency_ms > ping_sensor.threshold_warning:
                    status = 'warning'
                else:
                    status = 'ok'
                
                # Create metric (usar UTC para consistência com PostgreSQL)
                metric = Metric(
                    sensor_id=ping_sensor.id,
                    value=latency_ms,
                    unit='ms',
                    status=status,
                    timestamp=datetime.now(timezone.utc)
                )
                db.add(metric)
                db.commit()
                
                logger.debug(f"✅ Métrica PING salva: {server.hostname} = {latency_ms}ms ({status})")
                
            except Exception as e:
                logger.error(f"❌ Erro ao fazer PING em {server.hostname}: {e}")
                continue
        
        logger.info(f"✅ PING concluído para {len(servers)} servidores")
        
    except Exception as e:
        logger.error(f"❌ Erro ao fazer PING de servidores: {e}")
    finally:
        db.close()


def execute_ping(ip_address: str) -> float:
    """
    Executa PING e retorna latência em ms (0 se offline).
    Usa comando ping nativo do Linux.
    """
    try:
        # Linux ping command: -c 1 (1 pacote), -W 2 (timeout 2s)
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ip_address],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if result.returncode == 0:
            # Parse output: "time=1.23 ms"
            output = result.stdout
            if 'time=' in output:
                time_str = output.split('time=')[1].split()[0]
                return float(time_str)
        
        return 0  # Offline
        
    except subprocess.TimeoutExpired:
        logger.debug(f"⏱️ Timeout ao fazer PING em {ip_address}")
        return 0
    except Exception as e:
        logger.error(f"❌ Erro ao executar PING para {ip_address}: {e}")
        return 0
