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
        'schedule': 60.0,
    },
    'evaluate-thresholds-every-minute': {
        'task': 'tasks.evaluate_all_thresholds',
        'schedule': 60.0,
    },
    'run-aiops-pipeline-every-5-minutes': {
        'task': 'tasks.run_aiops_pipeline_v3',
        'schedule': 300.0,  # A cada 5 minutos
    },
    'calculate-monthly-sla': {
        'task': 'tasks.generate_monthly_reports',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
    },
    'auto-backup-3-times-daily': {
        'task': 'tasks.create_automatic_backup',
        'schedule': crontab(hour='7,12,18', minute=0),
    },
    'collect-http-sensors-every-minute': {
        'task': 'tasks.collect_http_sensors',
        'schedule': 60.0,
    },
}

@app.task
def evaluate_all_thresholds():
    """Evaluate thresholds for all active sensors — v3.5 Enterprise Hardening"""
    import redis as redis_lib
    db = SessionLocal()

    # Redis para cooldown — fail-open se indisponível
    try:
        redis_client = redis_lib.Redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=2)
        redis_client.ping()
    except Exception as e:
        logger.warning("Redis indisponível para cooldown: %s — prosseguindo sem cooldown Redis", e)
        redis_client = None

    try:
        now = datetime.now(timezone.utc)
        sensors = db.query(Sensor).filter(Sensor.is_active == True).all()

        for sensor in sensors:
            # 1. Skip disabled sensors
            if not getattr(sensor, 'enabled', True):
                continue

            # 2. Skip sensors paused until future timestamp
            paused_until = getattr(sensor, 'paused_until', None)
            if paused_until is not None:
                pu = paused_until
                if pu.tzinfo is None:
                    pu = pu.replace(tzinfo=timezone.utc)
                if pu > now:
                    continue

            # 3. Check metric_only — coleta mas não cria Incident nem envia ao predictor
            alert_mode = getattr(sensor, 'alert_mode', 'normal') or 'normal'
            # Hardcoded: network_in/network_out são SEMPRE metric_only (nunca criam incidentes)
            if sensor.sensor_type in ('network_in', 'network_out'):
                alert_mode = 'metric_only'
            is_metric_only = alert_mode == 'metric_only'

            # 4. Skip silent sensors (no alerts, no incidents)
            if alert_mode == 'silent':
                continue

            # Get latest metric
            latest_metric = db.query(Metric).filter(
                Metric.sensor_id == sensor.id
            ).order_by(Metric.timestamp.desc()).first()

            if not latest_metric:
                continue

            # metric_only: coleta registrada, mas não cria Incident e não envia ao predictor
            if is_metric_only:
                continue

            # Evaluate threshold
            threshold_breached, severity = evaluate_thresholds(
                sensor, latest_metric.value
            )

            # HTTP sensors: tratar status='critical' como breach mesmo se latência é 0
            if not threshold_breached and sensor.sensor_type == 'http' and latest_metric.status == 'critical':
                threshold_breached = True
                severity = 'critical'

            if threshold_breached:
                # ── WARNING: não cria incidente, mas auto-resolve incidentes antigos se sensor melhorou ──
                if severity == 'warning' and sensor.sensor_type != 'system':
                    # Auto-resolve incidentes CRITICAL que agora são apenas WARNING (sensor melhorou)
                    open_incidents = db.query(Incident).filter(
                        Incident.sensor_id == sensor.id,
                        Incident.status.in_(['open', 'acknowledged']),
                        Incident.severity == 'critical'
                    ).all()
                    for inc in open_incidents:
                        inc.status = "resolved"
                        inc.resolved_at = datetime.now(timezone.utc)
                        inc.resolution_notes = "Auto-resolvido: sensor melhorou de critical para warning"
                        db.commit()
                        logger.info(f"✅ Incidente {inc.id} auto-resolvido (sensor {sensor.name} melhorou para warning)")

                        # Parar escalação ativa para o sensor (se houver)
                        try:
                            from escalation import stop_escalation
                            stop_escalation(sensor.id, reason="resolved")
                        except Exception:
                            pass  # fail-open
                    continue

                # ── SYSTEM/UPTIME: tratamento especial — incidente informativo de reboot ──
                # Cria UM incidente já resolvido (apenas registro) e cooldown de 1h.
                # Não fica "open" — é só notificação de que houve reboot.
                if sensor.sensor_type == 'system':
                    # Cooldown forte: 1 incidente por hora no máximo
                    cooldown_key = f"cooldown:{sensor.id}"
                    if redis_client is not None:
                        try:
                            if redis_client.exists(cooldown_key):
                                logger.debug("Cooldown reboot ativo para sensor %s — skip", sensor.id)
                                continue
                        except Exception:
                            pass

                    # Dedup: já existe incidente de reboot nos últimos 60 min?
                    recent_cutoff = now - timedelta(minutes=60)
                    recent_reboot = db.query(Incident).filter(
                        Incident.sensor_id == sensor.id,
                        Incident.created_at >= recent_cutoff
                    ).first()
                    if recent_reboot:
                        logger.debug("Dedup reboot: sensor %s já tem incidente na última hora — skip", sensor.id)
                        continue

                    uptime_minutes = round(latest_metric.value * 24 * 60, 1)
                    server_name = ""
                    if sensor.server_id:
                        srv = db.query(Server).filter(Server.id == sensor.server_id).first()
                        if srv:
                            server_name = srv.hostname

                    incident = Incident(
                        sensor_id=sensor.id,
                        severity="warning",
                        status="resolved",  # Já nasce resolvido — é informativo
                        title=f"{server_name or sensor.name} - Servidor reiniciado",
                        description=f"Reboot detectado: uptime atual é {uptime_minutes} minutos. "
                                    f"Incidente informativo — servidor já está online.",
                        resolved_at=now,
                        resolution_notes="Auto-resolvido: incidente informativo de reboot"
                    )
                    db.add(incident)
                    db.commit()
                    db.refresh(incident)

                    # Cooldown de 1h
                    if redis_client is not None:
                        try:
                            redis_client.setex(cooldown_key, 3600, "1")
                        except Exception:
                            pass

                    logger.info(f"🔄 Reboot detectado: {incident.title} (ID: {incident.id}) — incidente informativo criado já resolvido")
                    print(f"🔄 Reboot: {incident.title} (ID: {incident.id}) — informativo")

                    # Enviar e-mail informativo de reboot
                    try:
                        _send_reboot_email(db, sensor, server_name, uptime_minutes)
                    except Exception as mail_err:
                        logger.warning(f"Erro ao enviar e-mail de reboot: {mail_err}")

                    # Resolver qualquer incidente PING aberto do mesmo servidor (o server voltou)
                    if sensor.server_id:
                        ping_sensor = db.query(Sensor).filter(
                            Sensor.server_id == sensor.server_id,
                            Sensor.sensor_type == 'ping',
                            Sensor.is_active == True
                        ).first()
                        if ping_sensor:
                            ping_incidents = db.query(Incident).filter(
                                Incident.sensor_id == ping_sensor.id,
                                Incident.status.in_(['open', 'acknowledged'])
                            ).all()
                            for pi in ping_incidents:
                                pi.status = 'resolved'
                                pi.resolved_at = now
                                pi.resolution_notes = f"Auto-resolvido: servidor reiniciou (uptime: {uptime_minutes}min)"
                                db.commit()
                                logger.info(f"✅ Incidente PING {pi.id} resolvido após reboot detectado")

                    continue  # Não precisa do fluxo normal de incidentes

                # 5. Deduplicação: Incident aberto OU acknowledged já existe?
                existing_incident = db.query(Incident).filter(
                    Incident.sensor_id == sensor.id,
                    Incident.status.in_(["open", "acknowledged"])
                ).first()

                # 5b. Para PING: também verificar se já existe incidente
                # criado nos últimos 30 min (mesmo que resolvido) — evita flood
                if not existing_incident and sensor.sensor_type == 'ping':
                    recent_cutoff = now - timedelta(minutes=30)
                    recent_incident = db.query(Incident).filter(
                        Incident.sensor_id == sensor.id,
                        Incident.created_at >= recent_cutoff
                    ).first()
                    if recent_incident:
                        logger.debug(
                            "Dedup temporal: sensor %s (%s) já tem incidente nos últimos 30min (ID %s) — skip",
                            sensor.id, sensor.sensor_type, recent_incident.id
                        )
                        continue

                if not existing_incident:
                    # 6. Supressão por dependência: PING é sensor MASTER do servidor
                    # Se PING DOWN aberto → suprimir TODOS os outros sensores do mesmo server
                    # (uptime, cpu, memory, disk, network, service — tudo depende do ping)
                    if sensor.server_id and sensor.sensor_type != 'ping':
                        ping_sensor = db.query(Sensor).filter(
                            Sensor.server_id == sensor.server_id,
                            Sensor.sensor_type == 'ping',
                            Sensor.is_active == True
                        ).first()
                        if ping_sensor:
                            ping_incident = db.query(Incident).filter(
                                Incident.sensor_id == ping_sensor.id,
                                Incident.status.in_(["open", "acknowledged"])
                            ).first()
                            if ping_incident:
                                logger.info(
                                    "Supressão: PING master (sensor %s) com incidente aberto → skip %s (%s)",
                                    ping_sensor.id, sensor.id, sensor.sensor_type
                                )
                                continue

                    # 7. Cooldown via Redis
                    cooldown_key = f"cooldown:{sensor.id}"
                    # PING: cooldown maior (30 min) para evitar flood de incidentes
                    if sensor.sensor_type == 'ping':
                        cooldown_secs = getattr(sensor, 'cooldown_seconds', None) or 1800  # 30 min
                    else:
                        cooldown_secs = getattr(sensor, 'cooldown_seconds', None) or 300  # 5 min
                    if redis_client is not None:
                        try:
                            if redis_client.exists(cooldown_key):
                                logger.debug("Cooldown ativo para sensor %s — skip", sensor.id)
                                continue
                        except Exception:
                            pass  # fail-open

                    # 7b. PING: exigir múltiplas falhas consecutivas antes de criar incidente
                    # Evita flood de chamados por latência momentânea
                    if sensor.sensor_type == 'ping':
                        consecutive_key = f"consecutive_fail:{sensor.id}"
                        required_fails = 3  # 3 ciclos consecutivos (~3 min)
                        if redis_client is not None:
                            try:
                                count = redis_client.incr(consecutive_key)
                                redis_client.expire(consecutive_key, 300)  # reset após 5 min sem falha
                                if count < required_fails:
                                    logger.debug(
                                        "PING sensor %s: falha %d/%d — aguardando confirmação",
                                        sensor.id, count, required_fails
                                    )
                                    continue
                            except Exception:
                                pass  # fail-open

                    # Get sensor type specific description
                    description = get_incident_description(sensor, latest_metric)

                    # Título específico por tipo de sensor
                    if sensor.sensor_type == 'ping':
                        inc_title = f"{sensor.name} - HOST DOWN (sem resposta)"
                    elif sensor.sensor_type == 'service':
                        inc_title = f"{sensor.name} - Serviço parado"
                    else:
                        inc_title = f"{sensor.name} - {severity.upper()}"

                    # Create new incident
                    incident = Incident(
                        sensor_id=sensor.id,
                        severity=severity,
                        status="open",
                        title=inc_title,
                        description=description
                    )
                    db.add(incident)
                    db.commit()
                    db.refresh(incident)

                    # Setar cooldown Redis após criar Incident
                    if redis_client is not None:
                        try:
                            redis_client.setex(cooldown_key, cooldown_secs, "1")
                        except Exception:
                            pass

                    print(f"✅ Incidente criado: {incident.title} (ID: {incident.id})")

                    # Execute AIOps analysis automatically
                    execute_aiops_analysis.delay(incident.id)

                    # Attempt self-healing
                    attempt_self_healing.delay(incident.id)

                    # ── PRIORIDADE: só envia notificação externa se priority == 5 ──
                    sensor_priority = getattr(sensor, 'priority', 3) or 3
                    if sensor_priority >= 5:
                        logger.info(
                            "Sensor %s priority=%d → disparando notificação externa (Telegram/Teams)",
                            sensor.name, sensor_priority
                        )
                        send_external_notification.delay(incident.id)
                    else:
                        logger.debug(
                            "Sensor %s priority=%d < 5 → notificação externa suprimida",
                            sensor.name, sensor_priority
                        )
                    # ─────────────────────────────────────────────────────────────
                else:
                    # Update existing incident severity if it changed
                    if existing_incident.severity != severity:
                        existing_incident.severity = severity
                        db.commit()
                        print(f"⚠️ Incidente {existing_incident.id} atualizado para {severity}")
            else:
                # Sensor OK — resetar contador de falhas consecutivas
                if redis_client is not None and sensor.sensor_type == 'ping':
                    try:
                        redis_client.delete(f"consecutive_fail:{sensor.id}")
                    except Exception:
                        pass

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

                    # Parar escalação ativa para o sensor (se houver)
                    try:
                        from escalation import stop_escalation
                        stop_escalation(sensor.id, reason="resolved")
                    except Exception:
                        pass  # fail-open

    except Exception as e:
        print(f"❌ Erro ao avaliar thresholds: {e}")
    finally:
        db.close()


def _send_reboot_email(db, sensor, server_name, uptime_minutes):
    """Envia e-mail informativo quando um servidor reinicia."""
    from models import Tenant
    tenant = db.query(Tenant).filter(Tenant.id == 1).first()
    if not tenant or not tenant.notification_config:
        return
    email_cfg = tenant.notification_config.get('email', {})
    if not email_cfg.get('enabled'):
        return

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    smtp_server = email_cfg.get('smtp_server')
    smtp_port = email_cfg.get('smtp_port', 587)
    smtp_user = email_cfg.get('smtp_user')
    smtp_password = email_cfg.get('smtp_password')
    from_email = email_cfg.get('from_email')
    to_emails = email_cfg.get('to_emails', [])

    if not all([smtp_server, smtp_user, smtp_password, from_email, to_emails]):
        return

    now_str = datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')
    subject = f"🔄 Reboot Detectado: {server_name}"
    body = f"""
    <html><body style="font-family:Arial;background:#0f172a;color:#e2e8f0;padding:20px;">
    <div style="max-width:600px;margin:0 auto;background:#1e293b;border-radius:12px;padding:24px;border:1px solid #334155;">
        <h2 style="color:#f59e0b;margin-top:0;">🔄 Servidor Reiniciado</h2>
        <table style="width:100%;font-size:14px;">
            <tr><td style="padding:8px 0;color:#94a3b8;">Servidor:</td><td style="font-weight:bold;">{server_name}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Uptime atual:</td><td>{uptime_minutes} minutos</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Data/Hora:</td><td>{now_str}</td></tr>
            <tr><td style="padding:8px 0;color:#94a3b8;">Status:</td><td style="color:#22c55e;">✅ Online (já resolvido)</td></tr>
        </table>
        <p style="color:#64748b;font-size:12px;margin-top:16px;">Este é um e-mail informativo. O servidor foi reiniciado e já está online. Nenhuma ação necessária.</p>
        <hr style="border-color:#334155;margin:16px 0;">
        <p style="color:#475569;font-size:11px;">🦉 Coruja Monitor — Sistema de Monitoramento Inteligente</p>
    </div>
    </body></html>
    """

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_emails, msg.as_string())
        server.quit()
        logger.info(f"📧 E-mail de reboot enviado: {server_name}")
    except Exception as e:
        logger.warning(f"Erro ao enviar e-mail de reboot: {e}")


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
        return f"Host DOWN — Ping sem resposta (timeout). Servidor: {sensor.name}"
    elif sensor.sensor_type == 'system':
        minutes = round(value * 24 * 60, 1)
        return f"Reboot detectado: uptime atual é {minutes} minutos. O servidor foi reiniciado recentemente. Servidor: {sensor.name}"
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
def run_aiops_pipeline_v3():
    """
    Executa o pipeline de agentes v3 com incidentes abertos dos últimos 30 minutos.
    Agendado a cada 5 minutos pelo Celery Beat.
    """
    logger.info("🤖 AIOps Pipeline v3: iniciando execução agendada")
    db = SessionLocal()
    try:
        import sys, os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from ai_agents.pipeline_orchestrator import PipelineOrchestrator
        from core.spec.models import Event
        from core.spec.enums import EventSeverity
        from uuid import uuid4, UUID

        since = datetime.now(timezone.utc) - timedelta(minutes=30)
        incidents = db.query(Incident).filter(
            Incident.status == "open",
            Incident.created_at >= since,
        ).order_by(Incident.created_at.desc()).limit(50).all()

        if not incidents:
            logger.info("AIOps Pipeline v3: nenhum incidente aberto nos últimos 30 min")
            return

        events = []
        for inc in incidents:
            sensor = db.query(Sensor).filter(Sensor.id == inc.sensor_id).first()
            sensor_type = sensor.sensor_type if sensor else "unknown"
            server_id = sensor.server_id if sensor else 0
            try:
                host_uuid = UUID(int=server_id)
            except Exception:
                host_uuid = uuid4()

            sev = EventSeverity.CRITICAL if inc.severity == "critical" else EventSeverity.WARNING
            ts = inc.created_at
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            event = Event(
                host_id=host_uuid,
                type=f"high_{sensor_type}",
                severity=sev,
                timestamp=ts,
                description=inc.title or f"Incidente #{inc.id}",
            )
            events.append(event)

        logger.info("AIOps Pipeline v3: processando %d eventos", len(events))

        orch = PipelineOrchestrator(db_conn=db)
        result = orch.run_from_events(events)

        logger.info(
            "AIOps Pipeline v3: run_id=%s agents=%d/%d alert=%s",
            result.get("run_id"),
            result.get("agents_success", 0),
            result.get("agents_run", 0),
            result.get("should_alert"),
        )

    except Exception as e:
        logger.error("AIOps Pipeline v3: erro — %s", e, exc_info=True)
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
                json={"email": "admin@example.com", "password": "REPLACE_WITH_SYSTEM_TOKEN"}  # Use env var in production
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
    """Cria backup automático do banco de dados 3x ao dia (07h, 12h, 18h)"""
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
        
        # Limpar backups antigos (manter últimos 9 = 3 dias de histórico)
        cleanup_old_backups(BACKUP_DIR, keep_last=9)
        
        return {
            "success": True,
            "filename": backup_filename,
            "size_mb": size_mb
        }
    except Exception as e:
        logger.error(f"❌ Erro ao criar backup automático: {str(e)}")
        return {"success": False, "error": str(e)}


@app.task
def collect_http_sensors():
    """
    Coleta sensores HTTP standalone diretamente do servidor Linux.
    Independente da probe Windows — garante monitoramento de sites externos.
    """
    import httpx as _httpx
    import time as _time

    db = SessionLocal()
    try:
        sensors = db.query(Sensor).filter(
            Sensor.sensor_type == 'http',
            Sensor.is_active == True,
        ).all()

        if not sensors:
            return

        logger.info(f"🌐 Coletando {len(sensors)} sensores HTTP...")
        now = datetime.now(timezone.utc)

        for sensor in sensors:
            cfg = sensor.config or {}
            http_cfg = cfg.get('http') or {}
            url = http_cfg.get('url') or cfg.get('http_url')
            if not url:
                logger.warning(f"Sensor HTTP {sensor.id} sem URL configurada — pulando")
                continue

            method = http_cfg.get('method', 'GET')
            elapsed_ms = 0.0
            status = 'critical'

            try:
                t0 = _time.monotonic()
                with _httpx.Client(timeout=15.0, verify=False, follow_redirects=True) as client:
                    resp = client.request(method, url, headers={'User-Agent': 'CorujaMonitor/3.5'})
                elapsed_ms = (_time.monotonic() - t0) * 1000

                if resp.status_code < 400:
                    w = sensor.threshold_warning or 2000
                    c = sensor.threshold_critical or 5000
                    if elapsed_ms >= c:
                        status = 'critical'
                    elif elapsed_ms >= w:
                        status = 'warning'
                    else:
                        status = 'ok'
                else:
                    status = 'critical' if resp.status_code >= 500 else 'warning'

                logger.info(f"🌐 HTTP {url}: {resp.status_code} em {elapsed_ms:.0f}ms → {status}")

            except Exception as e:
                logger.warning(f"🌐 HTTP {url} falhou: {e}")
                status = 'critical'
                elapsed_ms = 0.0

            metric = Metric(
                sensor_id=sensor.id,
                value=round(elapsed_ms, 2),
                unit='ms',
                status=status,
                timestamp=now,
            )
            db.add(metric)

        db.commit()
        logger.info("🌐 Coleta HTTP concluída")

    except Exception as e:
        logger.error(f"❌ Erro ao coletar sensores HTTP: {e}", exc_info=True)
    finally:
        db.close()


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
                # Skip servers without IP address
                if not server.ip_address:
                    logger.warning(f"⚠️ Servidor {server.hostname} sem IP configurado - pulando PING")
                    continue

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
                    # PRTG/Zabbix style: thresholds de ping NÃO são por latência.
                    # warning/critical só disparam em perda de pacotes ou timeout (value=0).
                    logger.info(f"✨ Criando sensor PING automático para {server.hostname}")
                    ping_sensor = Sensor(
                        server_id=server.id,
                        sensor_type='ping',
                        name='PING',  # Maiúsculo para consistência com API
                        threshold_warning=None,   # Ping não usa threshold de latência
                        threshold_critical=None,   # Ping não usa threshold de latência
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
                
                # Determine status — PRTG/Zabbix style:
                # Ping ONLY marks critical on DOWN (no response / timeout).
                # High latency is just a metric value, NEVER changes status to warning/critical.
                if latency_ms == 0:
                    status = 'critical'  # Offline / timeout
                else:
                    status = 'ok'  # Any response = host is UP
                
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

                # NÃO criar incidentes aqui — evaluate_all_thresholds() já cuida disso.
                # Duplicar a lógica aqui causava incidentes espúrios por latência.

                logger.debug(f"✅ Métrica PING salva: {server.hostname} = {latency_ms}ms ({status})")
                
            except Exception as e:
                logger.error(f"❌ Erro ao fazer PING em {server.hostname}: {e}")
                continue
        
        logger.info(f"✅ PING concluído para {len(servers)} servidores")
        
    except Exception as e:
        logger.error(f"❌ Erro ao fazer PING de servidores: {e}")
    finally:
        db.close()


def _check_reboot_via_uptime(db, server, ping_sensor):
    """
    Detecta reboot verificando se o uptime do servidor é muito baixo (< 10 minutos).
    Cria incidente de reboot mesmo que o ping já tenha voltado ao normal.
    Evita duplicar incidente se já existe um aberto para o mesmo servidor.
    """
    try:
        from models import Sensor as SensorModel
        uptime_sensor = db.query(SensorModel).filter(
            SensorModel.server_id == server.id,
            SensorModel.sensor_type == 'system',
            SensorModel.is_active == True
        ).first()

        if not uptime_sensor:
            return

        latest_uptime = db.query(Metric).filter(
            Metric.sensor_id == uptime_sensor.id
        ).order_by(Metric.timestamp.desc()).first()

        if not latest_uptime:
            return

        # Uptime em dias — 10 minutos = 0.00694 dias
        REBOOT_THRESHOLD_DAYS = 10 / (60 * 24)  # 10 minutos

        if latest_uptime.value <= REBOOT_THRESHOLD_DAYS:
            # Verificar se já existe incidente de reboot aberto recente (última hora)
            recent_reboot = db.query(Incident).filter(
                Incident.sensor_id == ping_sensor.id,
                Incident.status.in_(['open', 'acknowledged']),
                Incident.title.like('%reiniciado%')
            ).first()

            if not recent_reboot:
                minutes = round(latest_uptime.value * 24 * 60, 1)
                incident = Incident(
                    sensor_id=ping_sensor.id,
                    severity='warning',
                    status='open',
                    title=f"{server.hostname} - Servidor reiniciado",
                    description=f"Reboot detectado: uptime atual é {minutes} minutos. "
                                f"O servidor foi reiniciado recentemente."
                )
                db.add(incident)
                db.commit()
                db.refresh(incident)
                logger.warning(f"🔄 Reboot detectado em {server.hostname} (uptime: {minutes}min) — incidente {incident.id} criado")
                execute_aiops_analysis.delay(incident.id)
    except Exception as e:
        logger.debug(f"_check_reboot_via_uptime erro para {server.hostname}: {e}")


def execute_ping(ip_address: str) -> float:
    """
    Executa PING e retorna latência em ms (0 se offline).
    Usa TCP connect como fallback quando ping não está disponível.
    """
    import socket
    import time

    # Tenta ping nativo primeiro
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '2', ip_address],
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0:
            output = result.stdout
            if 'time=' in output:
                time_str = output.split('time=')[1].split()[0]
                return float(time_str)
        return 0
    except FileNotFoundError:
        # ping não instalado — usa TCP connect nas portas comuns
        pass
    except subprocess.TimeoutExpired:
        return 0
    except Exception as e:
        logger.debug(f"ping nativo falhou para {ip_address}: {e}")

    # Fallback: TCP connect (porta 135 WMI, 445 SMB, 22 SSH, 80 HTTP)
    ports = [135, 445, 22, 80, 443, 3389]
    for port in ports:
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip_address, port))
            elapsed = (time.time() - start) * 1000
            sock.close()
            if result == 0:
                return round(elapsed, 2)
        except Exception:
            continue

    return 0  # Offline


@app.task
def send_external_notification(incident_id: int):
    """
    Envia notificação externa (Telegram/Teams) para incidentes de sensores priority=5.
    Sensores com priority < 5 NÃO chegam aqui — filtro feito antes de chamar esta task.
    """
    logger.info("📣 send_external_notification: incidente %d", incident_id)
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            logger.warning("send_external_notification: incidente %d não encontrado", incident_id)
            return

        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        if not sensor:
            return

        server = db.query(Server).filter(Server.id == sensor.server_id).first() if sensor.server_id else None

        # Buscar configuração de notificação do tenant
        from models import Tenant
        tenant = db.query(Tenant).filter(Tenant.id == (server.tenant_id if server else None)).first()
        if not tenant or not tenant.notification_config:
            logger.debug("send_external_notification: tenant sem notification_config")
            return

        notif_cfg = tenant.notification_config
        priority = getattr(sensor, 'priority', 3) or 3
        stars = "⭐" * priority

        message_data = {
            "title": f"🚨 [{incident.severity.upper()}] {incident.title}",
            "text": (
                f"Sensor: {sensor.name} {stars}\n"
                f"Servidor: {server.hostname if server else 'N/A'}\n"
                f"Severidade: {incident.severity}\n"
                f"Prioridade: {priority}/5\n"
                f"Horário: {incident.created_at.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Descrição: {incident.description or 'N/A'}"
            ),
            "severity": incident.severity,
        }

        # Telegram
        tg_cfg = notif_cfg.get("telegram", {})
        if tg_cfg.get("enabled") and tg_cfg.get("bot_token"):
            try:
                import httpx as _httpx
                bot_token = tg_cfg["bot_token"]
                chat_ids = tg_cfg.get("chat_ids", [])
                text_msg = f"{message_data['title']}\n\n{message_data['text']}"
                for chat_id in chat_ids:
                    _httpx.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={"chat_id": chat_id, "text": text_msg, "parse_mode": "HTML"},
                        timeout=10,
                    )
                logger.info("send_external_notification: Telegram enviado para %d chats", len(chat_ids))
            except Exception as tg_err:
                logger.error("send_external_notification: Telegram error: %s", tg_err)

        # Teams
        teams_cfg = notif_cfg.get("teams", {})
        if teams_cfg.get("enabled") and teams_cfg.get("webhook_url"):
            try:
                import httpx as _httpx
                card = {
                    "@type": "MessageCard",
                    "@context": "http://schema.org/extensions",
                    "themeColor": "FF0000" if incident.severity == "critical" else "FFA500",
                    "summary": message_data["title"],
                    "sections": [{"activityTitle": message_data["title"], "activityText": message_data["text"]}],
                }
                _httpx.post(teams_cfg["webhook_url"], json=card, timeout=10)
                logger.info("send_external_notification: Teams enviado")
            except Exception as teams_err:
                logger.error("send_external_notification: Teams error: %s", teams_err)

    except Exception as e:
        logger.error("send_external_notification: erro geral: %s", e, exc_info=True)
    finally:
        db.close()


# ─── Escalação Contínua de Alarmes ──────────────────────────────────────────

@app.task(bind=True, max_retries=3, default_retry_delay=30)
def escalation_cycle(self, sensor_id: int):
    """Executa um ciclo de escalação para o sensor.

    Adquire lock distribuído, lê estado do Redis, verifica se foi
    reconhecido/expirado, executa chamadas (simultâneo ou sequencial),
    registra call_history, incrementa attempt_count e agenda próximo ciclo
    ou marca como expirado.

    Requisitos: 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.3, 3.5, 7.1, 7.2, 7.4, 7.5
    """
    import redis as redis_lib
    from escalation import (
        deserialize_state,
        serialize_state,
        _redis_key,
        _lock_key,
        _log_to_incident_history,
        stop_escalation,
    )

    logger.info("🔔 escalation_cycle: iniciando ciclo para sensor %d", sensor_id)

    # ── 1. Conectar ao Redis ────────────────────────────────────────────────
    try:
        r = redis_lib.Redis.from_url(
            settings.CELERY_BROKER_URL, decode_responses=True, socket_connect_timeout=2
        )
        r.ping()
    except Exception as e:
        logger.error(
            "escalation_cycle: Redis indisponível para sensor %d — %s. "
            "Tentando fallback de ligação única.",
            sensor_id, e,
        )
        _escalation_fallback_single_call(sensor_id)
        return

    # ── 2. Adquirir lock distribuído ────────────────────────────────────────
    lock_key = _lock_key(sensor_id)
    lock_acquired = False
    try:
        # Lock com TTL para auto-liberação em caso de crash
        lock_acquired = r.set(lock_key, "locked", nx=True, ex=300)
        if not lock_acquired:
            logger.warning(
                "escalation_cycle: lock não adquirido para sensor %d — outro worker processando",
                sensor_id,
            )
            return
    except Exception as e:
        logger.error("escalation_cycle: erro ao adquirir lock: %s", e)
        return

    try:
        # ── 3. Ler estado de escalação do Redis ─────────────────────────────
        key = _redis_key(sensor_id)
        raw = r.get(key)
        if not raw:
            logger.warning(
                "escalation_cycle: nenhum estado encontrado para sensor %d — abortando",
                sensor_id,
            )
            return

        try:
            state = deserialize_state(raw)
        except ValueError as e:
            logger.error(
                "escalation_cycle: estado corrompido para sensor %d — %s", sensor_id, e
            )
            r.delete(key)
            return

        # ── 4. Verificar se foi reconhecido ou expirado ────────────────────
        if state.get("status") != "active":
            logger.info(
                "escalation_cycle: sensor %d status='%s' — parando ciclo",
                sensor_id, state.get("status"),
            )
            return

        # ── 5. Verificar max_attempts atingido ─────────────────────────────
        if state["attempt_count"] >= state["max_attempts"]:
            logger.info(
                "escalation_cycle: sensor %d atingiu max_attempts (%d) — expirando",
                sensor_id, state["max_attempts"],
            )
            state["status"] = "expired"
            serialized = serialize_state(state)
            r.setex(key, 3600, serialized)  # Manter 1h para consulta

            # Registrar expiração no histórico do incidente
            try:
                from database import SessionLocal
                db = SessionLocal()
                try:
                    _log_to_incident_history(db, state["incident_id"], "escalation_expired", {
                        "sensor_id": sensor_id,
                        "attempt_count": state["attempt_count"],
                        "max_attempts": state["max_attempts"],
                    })
                finally:
                    db.close()
            except Exception as log_err:
                logger.warning("escalation_cycle: erro ao registrar expiração: %s", log_err)

            return

        # ── 6. Executar chamadas conforme modo ─────────────────────────────
        now = datetime.now(timezone.utc)
        mode = state.get("mode", "sequential")
        phone_numbers = state.get("phone_numbers", [])
        call_duration = state.get("call_duration_seconds", 30)
        new_calls = []

        if not phone_numbers:
            logger.error(
                "escalation_cycle: cadeia de escalação vazia para sensor %d — parando",
                sensor_id,
            )
            stop_escalation(sensor_id, reason="expired")
            return

        if mode == "simultaneous":
            # Ligar para todos os números ao mesmo tempo
            for entry in phone_numbers:
                number = entry.get("number", "") if isinstance(entry, dict) else str(entry)
                result = _make_escalation_call(state, number, call_duration)
                new_calls.append({
                    "number": number,
                    "timestamp": now.isoformat(),
                    "result": result,
                })
        else:
            # Modo sequencial: ligar para o número no current_number_index
            idx = state.get("current_number_index", 0) % len(phone_numbers)
            entry = phone_numbers[idx]
            number = entry.get("number", "") if isinstance(entry, dict) else str(entry)
            result = _make_escalation_call(state, number, call_duration)
            new_calls.append({
                "number": number,
                "timestamp": now.isoformat(),
                "result": result,
            })
            # Avançar índice com wrap-around
            state["current_number_index"] = (idx + 1) % len(phone_numbers)

        # ── 7. Registrar chamadas no call_history ──────────────────────────
        state["call_history"].extend(new_calls)
        state["attempt_count"] += 1
        state["last_attempt_at"] = now.isoformat()

        # ── 8. Verificar se atingiu max_attempts após incremento ───────────
        if state["attempt_count"] >= state["max_attempts"]:
            logger.info(
                "escalation_cycle: sensor %d atingiu max_attempts (%d) após ciclo — expirando",
                sensor_id, state["max_attempts"],
            )
            state["status"] = "expired"
            serialized = serialize_state(state)
            r.setex(key, 3600, serialized)

            try:
                from database import SessionLocal
                db = SessionLocal()
                try:
                    _log_to_incident_history(db, state["incident_id"], "escalation_expired", {
                        "sensor_id": sensor_id,
                        "attempt_count": state["attempt_count"],
                        "max_attempts": state["max_attempts"],
                    })
                finally:
                    db.close()
            except Exception as log_err:
                logger.warning("escalation_cycle: erro ao registrar expiração: %s", log_err)

            return

        # ── 9. Agendar próximo ciclo ───────────────────────────────────────
        interval = state.get("interval_minutes", 5)
        next_attempt = now + timedelta(minutes=interval)
        state["next_attempt_at"] = next_attempt.isoformat()

        # Persistir estado atualizado no Redis
        ttl = state["max_attempts"] * state["interval_minutes"] * 60 + 3600
        serialized = serialize_state(state)
        r.setex(key, ttl, serialized)

        # Agendar próximo ciclo
        try:
            self.apply_async(args=[sensor_id], eta=next_attempt)
            logger.info(
                "escalation_cycle: sensor %d — ciclo %d/%d concluído, próximo em %s",
                sensor_id, state["attempt_count"], state["max_attempts"],
                next_attempt.isoformat(),
            )
        except Exception as sched_err:
            logger.error(
                "escalation_cycle: erro ao agendar próximo ciclo para sensor %d: %s",
                sensor_id, sched_err,
            )

    except Exception as e:
        logger.error(
            "escalation_cycle: erro inesperado para sensor %d: %s",
            sensor_id, e, exc_info=True,
        )
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(
                "escalation_cycle: max retries excedido para sensor %d", sensor_id
            )
    finally:
        # Liberar lock
        try:
            r.delete(lock_key)
        except Exception:
            pass


def _make_escalation_call(state: dict, number: str, call_duration: int) -> str:
    """Executa uma ligação de escalação via Twilio.

    Returns:
        Resultado da chamada: 'completed', 'no-answer', 'failed', 'rate-limited'.
    """
    try:
        from database import SessionLocal
        from models import Tenant
        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(Tenant.id == state.get("tenant_id")).first()
            if not tenant or not tenant.notification_config:
                logger.warning("_make_escalation_call: tenant %d sem config", state.get("tenant_id"))
                return "failed"

            twilio_config = tenant.notification_config.get("twilio", {})
            account_sid = twilio_config.get("account_sid")
            auth_token = twilio_config.get("auth_token")
            from_number = twilio_config.get("from_number")

            if not all([account_sid, auth_token, from_number]):
                logger.warning("_make_escalation_call: Twilio não configurado")
                return "failed"

            from twilio.rest import Client
            client = Client(account_sid, auth_token)

            device = state.get("device_type", "equipamento")
            problem = state.get("problem_description", "problema detectado")

            speech = (
                f'Atenção. Alerta crítico. '
                f'{problem}. '
                f'Verifique imediatamente. '
                f'Repito. {problem}.'
            )

            call = client.calls.create(
                twiml=(
                    f'<Response>'
                    f'<Say language="pt-BR" voice="alice">{speech}</Say>'
                    f'<Pause length="2"/>'
                    f'<Say language="pt-BR" voice="alice">{speech}</Say>'
                    f'</Response>'
                ),
                from_=from_number,
                to=number,
                timeout=call_duration,
            )
            logger.info("_make_escalation_call: chamada para %s — SID %s", number, call.sid)
            return "completed"

        finally:
            db.close()

    except ImportError:
        logger.warning("_make_escalation_call: Twilio não instalado")
        return "failed"
    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "rate" in error_str:
            logger.warning(
                "_make_escalation_call: rate-limit do Twilio para %s — aguardando 60s", number
            )
            import time
            time.sleep(60)
            return "rate-limited"
        logger.error("_make_escalation_call: erro para %s — %s", number, e)
        return "failed"


def _escalation_fallback_single_call(sensor_id: int):
    """Fallback quando Redis está indisponível: tenta uma única ligação.

    Busca dados do incidente/tenant e dispara ligação direta via Twilio.
    """
    logger.warning(
        "escalation_fallback: Redis indisponível, tentando ligação única para sensor %d",
        sensor_id,
    )
    try:
        from database import SessionLocal
        from models import Incident, Sensor, Tenant

        db = SessionLocal()
        try:
            sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
            if not sensor:
                return

            incident = db.query(Incident).filter(
                Incident.sensor_id == sensor_id,
                Incident.status.in_(["open", "acknowledged"]),
            ).order_by(Incident.created_at.desc()).first()

            server = None
            tenant = None
            if sensor.server_id:
                from models import Server
                server = db.query(Server).filter(Server.id == sensor.server_id).first()
                if server:
                    tenant = db.query(Tenant).filter(Tenant.id == server.tenant_id).first()

            if not tenant or not tenant.notification_config:
                logger.warning("escalation_fallback: sem configuração de notificação")
                return

            twilio_config = tenant.notification_config.get("twilio", {})
            if not twilio_config.get("account_sid"):
                return

            from twilio.rest import Client
            client = Client(
                twilio_config["account_sid"], twilio_config["auth_token"]
            )
            from_number = twilio_config.get("from_number")
            to_numbers = twilio_config.get("to_numbers", [])

            speech = (
                f'Atenção. Alerta crítico. Sensor {sensor.name}. '
                f'Verifique imediatamente.'
            )

            for to_number in to_numbers:
                try:
                    client.calls.create(
                        twiml=f'<Response><Say language="pt-BR" voice="alice">{speech}</Say></Response>',
                        from_=from_number,
                        to=to_number,
                    )
                except Exception as call_err:
                    logger.error("escalation_fallback: erro chamada %s: %s", to_number, call_err)

        finally:
            db.close()
    except Exception as e:
        logger.error("escalation_fallback: erro geral: %s", e)


@app.task
def recover_active_escalations():
    """Task de recuperação: busca escalações ativas no Redis sem tasks agendadas e reagenda.

    Deve ser chamada no startup do worker para retomar escalações pendentes
    após crash ou reinício.

    Requisitos: 7.3
    """
    import redis as redis_lib

    logger.info("🔄 recover_active_escalations: buscando escalações ativas no Redis...")

    try:
        r = redis_lib.Redis.from_url(
            settings.CELERY_BROKER_URL, decode_responses=True, socket_connect_timeout=2
        )
        r.ping()
    except Exception as e:
        logger.error("recover_active_escalations: Redis indisponível — %s", e)
        return

    from escalation import deserialize_state, _redis_key

    recovered = 0
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor, match="escalation:*", count=100)
        for key in keys:
            key_str = key if isinstance(key, str) else key.decode("utf-8")
            # Filtrar apenas chaves numéricas (excluir locks)
            suffix = key_str.split(":")[-1]
            if not suffix.isdigit():
                continue

            sensor_id = int(suffix)
            raw = r.get(key_str)
            if not raw:
                continue

            try:
                state = deserialize_state(raw)
            except ValueError:
                logger.warning(
                    "recover_active_escalations: estado corrompido para %s — removendo",
                    key_str,
                )
                r.delete(key_str)
                continue

            if state.get("status") != "active":
                continue

            # Reagendar ciclo de escalação
            next_attempt_str = state.get("next_attempt_at")
            if next_attempt_str:
                try:
                    next_attempt = datetime.fromisoformat(next_attempt_str)
                except (ValueError, TypeError):
                    next_attempt = datetime.now(timezone.utc) + timedelta(seconds=30)
            else:
                next_attempt = datetime.now(timezone.utc) + timedelta(seconds=30)

            # Se next_attempt já passou, agendar para agora + 10s
            now = datetime.now(timezone.utc)
            if next_attempt <= now:
                next_attempt = now + timedelta(seconds=10)

            try:
                escalation_cycle.apply_async(args=[sensor_id], eta=next_attempt)
                recovered += 1
                logger.info(
                    "recover_active_escalations: reagendado sensor %d para %s",
                    sensor_id, next_attempt.isoformat(),
                )
            except Exception as sched_err:
                logger.error(
                    "recover_active_escalations: erro ao reagendar sensor %d: %s",
                    sensor_id, sched_err,
                )

        if cursor == 0:
            break

    logger.info(
        "🔄 recover_active_escalations: %d escalação(ões) recuperada(s)", recovered
    )
