"""
Módulo de despacho de notificações — Matriz de Notificação Inteligente.

Contém a função pura `resolve_channels` que mapeia sensor_type → conjunto de canais,
e as constantes da matriz de notificação padrão.
"""

import os as _os
import sys as _sys
_app_dir = _os.path.dirname(_os.path.abspath(__file__))
if _app_dir not in _sys.path:
    _sys.path.insert(0, _app_dir)

# Import antecipado do módulo escalation para garantir disponibilidade nos forks Celery
try:
    import importlib as _importlib
    import importlib.util as _importlib_util
    _esc_path = _os.path.join(_app_dir, 'escalation.py')
    _esc_spec = _importlib_util.spec_from_file_location('escalation', _esc_path)
    _esc_mod = _importlib_util.module_from_spec(_esc_spec)
    _esc_spec.loader.exec_module(_esc_mod)
    _sys.modules['escalation'] = _esc_mod
except Exception as _e:
    pass  # fail-open — erro será capturado no uso

VALID_CHANNELS: set[str] = {
    "email", "teams", "ticket", "sms", "whatsapp", "phone_call"
}

VALID_SENSOR_TYPES: set[str] = {
    "ping", "cpu", "memory", "disk", "service", "http", "printer",
    "equallogic", "conflex", "engetron", "snmp", "docker", "kubernetes",
    "hyperv", "system", "network_in", "network_out",
}

DEFAULT_MATRIX: dict[str, list[str]] = {
    "ping":        ["email", "teams"],
    "cpu":         ["email", "teams"],
    "memory":      ["email", "teams"],
    "disk":        ["email", "teams"],
    "service":     ["email", "teams"],
    "http":        ["email", "teams"],
    "printer":     ["email", "teams"],
    "equallogic":  ["email", "teams"],
    "conflex":     ["phone_call", "email", "teams", "sms", "whatsapp"],
    "engetron":    ["phone_call", "email", "teams", "sms", "whatsapp"],
    "snmp":        ["email", "teams"],
    "docker":      ["email", "teams"],
    "kubernetes":  ["email", "teams"],
    "hyperv":      ["email", "teams"],
    "network_in":  [],
    "network_out": [],
    "system":      ["email"],
}


def _effective_sensor_type(sensor_type: str, sensor_name: str = '') -> str:
    """
    Resolve o sensor_type efetivo para lookup na matriz.
    Sensores SNMP com nomes específicos são mapeados para seus tipos reais
    para que a matriz de notificação seja aplicada corretamente.
    """
    if sensor_type not in ('snmp', 'snmp_ap', 'snmp_ups', 'snmp_switch'):
        return sensor_type

    name_lower = (sensor_name or '').lower()

    # Nobreak/UPS Engetron
    if any(kw in name_lower for kw in ('engetron', 'nobreak', 'ups', 'nobreak engetron')):
        return 'engetron'

    # Ar-condicionado Conflex
    if any(kw in name_lower for kw in ('conflex', 'ar-condicionado', 'ar condicionado', 'hvac', 'climatizacao', 'climatização')):
        return 'conflex'

    # Storage EqualLogic
    if any(kw in name_lower for kw in ('equallogic', 'storage', 'dell storage')):
        return 'equallogic'

    # Impressora
    if any(kw in name_lower for kw in ('impressora', 'printer', 'hp laserjet')):
        return 'printer'

    return sensor_type


def resolve_channels(
    sensor_type: str,
    custom_matrix: dict | None = None,
    sensor_name: str = '',
) -> set[str]:
    """Resolve os canais de notificação para um dado sensor_type.

    Regras:
    - Mapeia sensor_type efetivo baseado no nome do sensor (ex: snmp "Nobreak Engetron" → engetron)
    - Se custom_matrix contém o sensor_type, usa esses canais.
    - Caso contrário, usa DEFAULT_MATRIX.
    - Se sensor_type não existe em nenhum dos dois, retorna {"email"} (fallback seguro).
    - Filtra canais inválidos (interseção com VALID_CHANNELS).
    - Garante resultado não-vazio (adiciona "email" se vazio após filtragem).
    """
    effective_type = _effective_sensor_type(sensor_type, sensor_name)

    if custom_matrix is not None and effective_type in custom_matrix:
        raw_channels = custom_matrix[effective_type]
    elif custom_matrix is not None and sensor_type in custom_matrix:
        raw_channels = custom_matrix[sensor_type]
    elif effective_type in DEFAULT_MATRIX:
        raw_channels = DEFAULT_MATRIX[effective_type]
    elif sensor_type in DEFAULT_MATRIX:
        raw_channels = DEFAULT_MATRIX[sensor_type]
    else:
        return {"email"}

    channels = set(raw_channels) & VALID_CHANNELS

    if not channels:
        channels.add("email")

    # Garantia: conflex e engetron sempre incluem phone_call
    # (são sensores críticos de datacenter que devem sempre ligar)
    if effective_type in ('conflex', 'engetron') and 'phone_call' not in channels:
        channels.add('phone_call')

    return channels

import logging

logger = logging.getLogger(__name__)

# Sensor types que são metric_only (não geram notificação)
METRIC_ONLY_TYPES: set[str] = {"network_in", "network_out"}


def dispatch_notifications(incident_id: int) -> dict:
    """Despacha notificações para todos os canais da matriz.

    Fluxo:
    1. Carrega incident, sensor, server, tenant do banco.
    2. Força priority=5 para sensor_type='ping'.
    3. Ignora network_in/network_out (metric_only).
    4. Resolve canais via resolve_channels(sensor_type, tenant.notification_matrix).
    5. Para cada canal: try/except isolado chamando a função de envio correspondente.
    6. phone_call → start_escalation() com dados do tenant.
    7. Retorna {sent: [...], failed: [...]}.

    Args:
        incident_id: ID do incidente a notificar.

    Returns:
        dict com 'sent' (list[str]) e 'failed' (list[dict]).
    """
    from database import SessionLocal
    from models import Incident, Sensor, Server, Tenant

    db = SessionLocal()
    sent = []
    failed = []

    try:
        # 1. Carregar dados
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            logger.error(f"Incidente {incident_id} não encontrado")
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': f'Incidente {incident_id} não encontrado'}]}

        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        if not sensor:
            logger.error(f"Sensor não encontrado para incidente {incident_id}")
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': 'Sensor não encontrado'}]}

        server = db.query(Server).filter(Server.id == sensor.server_id).first()

        # Para sensores standalone (sem server_id), buscar tenant via probe
        if server:
            tenant_id = server.tenant_id
        elif sensor.probe_id:
            from models import Probe
            probe = db.query(Probe).filter(Probe.id == sensor.probe_id).first()
            tenant_id = probe.tenant_id if probe else None
        else:
            tenant_id = None

        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

        if not tenant:
            # Fallback para sensores standalone sem probe (ex: HTTP coletado pelo worker)
            tenant = db.query(Tenant).order_by(Tenant.id).first()

        if not tenant:
            logger.warning(f"Tenant não encontrado para incidente {incident_id} (sensor_id={sensor.id}, server_id={sensor.server_id}, probe_id={sensor.probe_id})")
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': 'Tenant não encontrado'}]}

        # 2. Forçar priority=5 para sensor_type='ping'
        sensor_type = sensor.sensor_type or ''
        if sensor_type == 'ping':
            sensor.priority = 5

        # 3. Ignorar network_in/network_out (metric_only)
        if sensor_type in METRIC_ONLY_TYPES:
            logger.info(f"Sensor {sensor.id} é metric_only ({sensor_type}) — ignorando notificações")
            return {'sent': sent, 'failed': failed}

        # 4. Resolver canais
        custom_matrix = getattr(tenant, 'notification_matrix', None)
        channels = resolve_channels(sensor_type, custom_matrix, sensor.name)
        notification_config = tenant.notification_config or {}

        # Preparar incident_data
        from datetime import timezone as _tz
        import zoneinfo as _zi
        try:
            _tz_local = _zi.ZoneInfo("America/Sao_Paulo")
        except Exception:
            _tz_local = None

        def _fmt_dt(dt):
            if not dt:
                return 'N/A'
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=_tz.utc)
            if _tz_local:
                dt = dt.astimezone(_tz_local)
            return dt.strftime('%d/%m/%Y %H:%M:%S')

        # Para sensores PING, usar o hostname do servidor como nome principal
        display_server = server.hostname if server else sensor.name
        display_sensor = sensor.name
        # Se o sensor se chama igual ao servidor (ex: sensor "PING" no servidor "UDM 4º ANDAR"),
        # mostrar o hostname do servidor como servidor e o tipo como sensor
        if server and server.hostname and sensor.name.upper() in ('PING', 'CPU', 'MEMÓRIA', 'DISCO', 'UPTIME'):
            display_server = server.hostname
            display_sensor = f"{sensor.name} ({sensor_type})"

        incident_data = {
            'title': incident.title,
            'description': incident.description or '',
            'severity': incident.severity,
            'server_hostname': display_server,
            'sensor_name': display_sensor,
            'sensor_type': sensor_type,
            'incident_id': incident.id,
            'created_at': _fmt_dt(incident.created_at),
        }

        # ── Enriquecer com histórico de métricas (últimas 2h) ──────────────────
        try:
            from models import Metric
            from datetime import timedelta
            now_utc = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
            recent_metrics = db.query(Metric).filter(
                Metric.sensor_id == sensor.id,
                Metric.timestamp >= now_utc - timedelta(hours=2)
            ).order_by(Metric.timestamp.asc()).all()

            if recent_metrics:
                values = [m.value for m in recent_metrics if m.value is not None]
                current_val = values[-1] if values else None
                max_val = max(values) if values else None
                avg_val = sum(values) / len(values) if values else None

                # Calcular há quanto tempo está acima do threshold
                threshold = sensor.threshold_critical or sensor.threshold_warning or 90
                above_since = None
                for m in reversed(recent_metrics):
                    if m.value is not None and m.value >= threshold:
                        above_since = m.timestamp
                    else:
                        break

                duration_str = 'N/A'
                if above_since:
                    delta = now_utc - (above_since.replace(tzinfo=__import__('datetime').timezone.utc) if above_since.tzinfo is None else above_since)
                    total_min = int(delta.total_seconds() / 60)
                    if total_min >= 60:
                        duration_str = f"{total_min // 60}h {total_min % 60}min"
                    else:
                        duration_str = f"{total_min} minutos"

                # Sparkline ASCII simples (últimos 12 pontos)
                spark_vals = values[-12:] if len(values) >= 12 else values
                spark_chars = '▁▂▃▄▅▆▇█'
                if spark_vals:
                    mn, mx2 = min(spark_vals), max(spark_vals)
                    rng = mx2 - mn or 1
                    sparkline = ''.join(spark_chars[min(7, int((v - mn) / rng * 7))] for v in spark_vals)
                else:
                    sparkline = ''

                incident_data.update({
                    'current_value': f"{current_val:.1f}%" if current_val is not None else 'N/A',
                    'max_value_2h': f"{max_val:.1f}%" if max_val is not None else 'N/A',
                    'avg_value_2h': f"{avg_val:.1f}%" if avg_val is not None else 'N/A',
                    'duration_above_threshold': duration_str,
                    'sparkline': sparkline,
                    'metrics_count': len(recent_metrics),
                    'threshold_critical': f"{sensor.threshold_critical}%" if sensor.threshold_critical else 'N/A',
                    'threshold_warning': f"{sensor.threshold_warning}%" if sensor.threshold_warning else 'N/A',
                })
        except Exception as _e:
            logger.warning(f"Erro ao enriquecer métricas no email: {_e}")

        # ── Enriquecer com análise Ollama (se disponível) ──────────────────────
        try:
            ai_analysis = incident.ai_analysis or {}
            ollama = ai_analysis.get('ollama_analysis', {})
            incident_data['ai_analysis'] = ollama.get('analysis', '')
            incident_data['ai_model'] = ollama.get('model', 'llama3.2')
            incident_data['root_cause'] = incident.root_cause or ''

            # Se não tem análise ainda, tentar gerar agora (síncrono, timeout curto)
            if not incident_data['ai_analysis'] and sensor_type in ('cpu', 'memory', 'disk'):
                try:
                    import httpx as _httpx, os as _os, json as _json
                    ollama_url = _os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
                    current_v = incident_data.get('current_value', 'N/A')
                    dur = incident_data.get('duration_above_threshold', 'N/A')
                    prompt = (
                        f"Servidor {display_server} com {sensor_type.upper()} em {current_v} "
                        f"há {dur}. Threshold crítico: {incident_data.get('threshold_critical','N/A')}. "
                        f"Em 3 tópicos curtos: 1) Diagnóstico 2) Causas prováveis 3) Ação imediata. "
                        f"Seja direto e técnico em português."
                    )
                    with _httpx.Client(timeout=20.0) as _client:
                        _resp = _client.post(
                            f"{ollama_url}/api/generate",
                            json={"model": _os.environ.get("AI_MODEL", "llama3.2"), "prompt": prompt, "stream": False}
                        )
                        if _resp.status_code == 200:
                            incident_data['ai_analysis'] = _resp.json().get("response", "").strip()
                except Exception as _ai_e:
                    logger.warning(f"Ollama inline falhou: {_ai_e}")
        except Exception as _e:
            logger.warning(f"Erro ao enriquecer AI no email: {_e}")

        # 5. Para cada canal: try/except isolado
        for channel in channels:
            try:
                if channel == 'email':
                    email_config = notification_config.get('email', {})
                    if email_config.get('enabled'):
                        from tasks import send_email_notification_sync
                        result = send_email_notification_sync(email_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Email não habilitado'}

                elif channel == 'teams':
                    teams_config = notification_config.get('teams', {})
                    if teams_config.get('enabled'):
                        from tasks import send_teams_notification_sync
                        result = send_teams_notification_sync(teams_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Teams não habilitado'}

                elif channel == 'ticket':
                    from tasks import send_ticket_sync
                    result = send_ticket_sync(notification_config, incident_data)

                elif channel == 'sms':
                    twilio_config = notification_config.get('twilio', {})
                    if twilio_config.get('account_sid'):
                        from tasks import send_sms_notification_sync
                        result = send_sms_notification_sync(twilio_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Twilio SMS não configurado'}

                elif channel == 'whatsapp':
                    whatsapp_config = notification_config.get('whatsapp') or notification_config.get('twilio', {})
                    if whatsapp_config.get('account_sid'):
                        from tasks import send_whatsapp_notification_sync
                        result = send_whatsapp_notification_sync(whatsapp_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Twilio WhatsApp não configurado'}

                elif channel == 'phone_call':
                    escalation_config = notification_config.get('escalation', {})
                    phone_chain = escalation_config.get('phone_chain', [])

                    # Fallback: usar to_numbers do Twilio se phone_chain vazia
                    if not phone_chain:
                        twilio_config = notification_config.get('twilio', {})
                        to_numbers = twilio_config.get('to_numbers', [])
                        if isinstance(to_numbers, str):
                            to_numbers = [n.strip() for n in to_numbers.split(',') if n.strip()]
                        phone_chain = [{"name": f"Contato {i+1}", "number": n} for i, n in enumerate(to_numbers)]

                    if phone_chain:
                        from escalation import start_escalation
                        # Sensores padrão de datacenter (conflex/engetron) sempre disparam
                        # escalação quando há cadeia de telefones, independente do toggle enabled.
                        effective_st = _effective_sensor_type(sensor_type, sensor.name)
                        is_datacenter = effective_st in ('conflex', 'engetron')
                        escalation_enabled = escalation_config.get('enabled', False) or is_datacenter

                        if escalation_enabled:
                            esc_result = start_escalation(
                                sensor_id=sensor.id,
                                incident_id=incident.id,
                                tenant_id=tenant.id,
                                alert_data={
                                    'device_type': effective_st,
                                    'problem_description': incident.description or incident.title,
                                    'phone_chain': phone_chain,
                                    'mode': escalation_config.get('mode', 'sequential'),
                                    'interval_minutes': escalation_config.get('interval_minutes', 5),
                                    'max_attempts': escalation_config.get('max_attempts', 10),
                                    'call_duration_seconds': escalation_config.get('call_duration_seconds', 30),
                                },
                            )
                            result = {'success': esc_result is not None}
                            if not result['success']:
                                result['error'] = 'Escalação não iniciada (duplicata ou sensor reconhecido)'
                        else:
                            result = {'success': False, 'error': 'Escalação não habilitada e sensor não é datacenter padrão'}
                    else:
                        result = {'success': False, 'error': 'Nenhum número de telefone configurado (phone_chain e to_numbers vazios)'}

                else:
                    result = {'success': False, 'error': f'Canal desconhecido: {channel}'}

                if result.get('success'):
                    sent.append(channel)
                    logger.info(f"✅ Canal '{channel}' enviado para incidente {incident_id}")
                else:
                    failed.append({'channel': channel, 'error': result.get('error', 'Erro desconhecido')})
                    logger.warning(f"⚠️ Canal '{channel}' falhou para incidente {incident_id}: {result.get('error')}")

            except Exception as e:
                failed.append({'channel': channel, 'error': str(e)})
                logger.error(f"❌ Exceção no canal '{channel}' para incidente {incident_id}: {e}", exc_info=True)

        # Log resumo
        if not sent and failed:
            logger.critical(
                f"🚨 FALHA TOTAL: Nenhum canal enviou notificação para incidente {incident_id}. "
                f"Falhas: {failed}"
            )
        else:
            logger.info(f"📊 Dispatch incidente {incident_id}: {len(sent)} enviados, {len(failed)} falharam")

        return {'sent': sent, 'failed': failed}

    except Exception as e:
        logger.error(f"❌ Erro fatal no dispatch de incidente {incident_id}: {e}", exc_info=True)
        return {'sent': sent, 'failed': [{'channel': 'all', 'error': str(e)}]}
    finally:
        db.close()




def dispatch_resolution(incident_id: int) -> dict:
    """
    Envia notificação de RESOLUÇÃO (problema resolvido) para email e teams.
    Chamado quando um incidente é auto-resolvido.
    """
    from database import SessionLocal
    from models import Incident, Sensor, Server, Tenant

    db = SessionLocal()
    sent = []
    failed = []

    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': f'Incidente {incident_id} não encontrado'}]}

        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        if not sensor:
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': 'Sensor não encontrado'}]}

        # Sensores metric_only não notificam resolução
        if (sensor.sensor_type in METRIC_ONLY_TYPES or
                (sensor.sensor_type == 'snmp' and any(
                    kw in (sensor.name or '').lower()
                    for kw in ('network in', 'network out', 'network_in', 'network_out')))):
            return {'sent': sent, 'failed': failed}

        server = db.query(Server).filter(Server.id == sensor.server_id).first()

        # Para sensores standalone (sem server_id), buscar tenant via probe
        if server:
            tenant_id = server.tenant_id
        elif sensor.probe_id:
            from models import Probe
            probe = db.query(Probe).filter(Probe.id == sensor.probe_id).first()
            tenant_id = probe.tenant_id if probe else None
        else:
            tenant_id = None

        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            # Fallback para sensores standalone sem probe: usar o único tenant ativo
            # (sensores HTTP coletados pelo worker Linux não têm server_id nem probe_id)
            from sqlalchemy import func as _func
            tenant = db.query(Tenant).order_by(Tenant.id).first()
        if not tenant:
            logger.warning(f"Tenant não encontrado para resolução do incidente {incident_id}")
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': 'Tenant não encontrado'}]}

        notification_config = tenant.notification_config or {}
        custom_matrix = getattr(tenant, 'notification_matrix', None)
        channels = resolve_channels(sensor.sensor_type, custom_matrix, sensor.name)
        # Resolução só vai para email e teams (não SMS/whatsapp/phone)
        channels = channels & {'email', 'teams'}

        resolved_at = incident.resolved_at.strftime('%d/%m/%Y %H:%M') if incident.resolved_at else 'N/A'
        created_at_fmt = incident.created_at.strftime('%d/%m/%Y %H:%M') if incident.created_at else 'N/A'

        # Calcular tempo de queda
        downtime_str = ''
        if incident.created_at and incident.resolved_at:
            diff = incident.resolved_at - incident.created_at
            total_sec = int(diff.total_seconds())
            if total_sec < 60:
                downtime_str = f"{total_sec}s"
            elif total_sec < 3600:
                downtime_str = f"{total_sec // 60}min {total_sec % 60}s"
            else:
                downtime_str = f"{total_sec // 3600}h {(total_sec % 3600) // 60}min"

        # Para HTTP, incluir URL na descrição
        sensor_url = ''
        if sensor.sensor_type == 'http':
            cfg = sensor.config or {}
            http_cfg = cfg.get('http') or {}
            sensor_url = http_cfg.get('url') or cfg.get('http_url') or ''

        display_server = server.hostname if server else (sensor_url or sensor.name)

        description_parts = [incident.resolution_notes or 'Sensor voltou ao normal']
        if downtime_str:
            description_parts.append(f"Tempo de indisponibilidade: {downtime_str}")
        if sensor_url:
            description_parts.append(f"URL: {sensor_url}")
        description_parts.append(f"Início: {created_at_fmt} | Fim: {resolved_at}")

        incident_data = {
            'title': f"✅ RESOLVIDO: {incident.title}",
            'description': ' | '.join(description_parts),
            'severity': incident.severity,
            'server_hostname': display_server,
            'sensor_name': sensor.name,
            'sensor_type': sensor.sensor_type,
            'incident_id': incident.id,
            'created_at': created_at_fmt,
            'resolved_at': resolved_at,
            'downtime': downtime_str,
            'sensor_url': sensor_url,
            'is_resolution': True,
        }

        for channel in channels:
            try:
                if channel == 'email':
                    email_config = notification_config.get('email', {})
                    if email_config.get('enabled'):
                        from tasks import send_email_resolution_sync
                        result = send_email_resolution_sync(email_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Email não habilitado'}

                elif channel == 'teams':
                    teams_config = notification_config.get('teams', {})
                    if teams_config.get('enabled'):
                        from tasks import send_teams_resolution_sync
                        result = send_teams_resolution_sync(teams_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Teams não habilitado'}
                else:
                    result = {'success': False, 'error': f'Canal não suportado para resolução: {channel}'}

                if result.get('success'):
                    sent.append(channel)
                    logger.info(f"✅ Resolução enviada via '{channel}' para incidente {incident_id}")
                else:
                    failed.append({'channel': channel, 'error': result.get('error', 'Erro desconhecido')})
                    logger.warning(f"⚠️ Resolução falhou via '{channel}' para incidente {incident_id}: {result.get('error')}")

            except Exception as e:
                failed.append({'channel': channel, 'error': str(e)})
                logger.error(f"❌ Exceção ao enviar resolução via '{channel}': {e}", exc_info=True)

        logger.info(f"📊 Resolução incidente {incident_id}: {len(sent)} enviados, {len(failed)} falharam")
        return {'sent': sent, 'failed': failed}

    except Exception as e:
        logger.error(f"❌ Erro fatal no dispatch de resolução {incident_id}: {e}", exc_info=True)
        return {'sent': sent, 'failed': [{'channel': 'all', 'error': str(e)}]}
    finally:
        db.close()




def dispatch_renotification(incident_id: int) -> dict:
    """
    Re-notifica um incidente já aberto via email e teams APENAS.
    Não abre ticket para evitar spam de chamados.
    Chamado quando um incidente existente ainda está aberto após restart do worker.
    """
    from database import SessionLocal
    from models import Incident, Sensor, Server, Tenant

    db = SessionLocal()
    sent = []
    failed = []

    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': f'Incidente {incident_id} não encontrado'}]}

        sensor = db.query(Sensor).filter(Sensor.id == incident.sensor_id).first()
        if not sensor:
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': 'Sensor não encontrado'}]}

        if sensor.sensor_type in METRIC_ONLY_TYPES:
            return {'sent': sent, 'failed': failed}

        server = db.query(Server).filter(Server.id == sensor.server_id).first()

        if server:
            tenant_id = server.tenant_id
        elif sensor.probe_id:
            from models import Probe
            probe = db.query(Probe).filter(Probe.id == sensor.probe_id).first()
            tenant_id = probe.tenant_id if probe else None
        else:
            tenant_id = None

        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            # Fallback para sensores standalone sem probe (ex: HTTP coletado pelo worker)
            tenant = db.query(Tenant).order_by(Tenant.id).first()
        if not tenant:
            logger.warning(f"Tenant não encontrado para re-notificação do incidente {incident_id}")
            return {'sent': sent, 'failed': [{'channel': 'all', 'error': 'Tenant não encontrado'}]}

        notification_config = tenant.notification_config or {}
        sensor_type = sensor.sensor_type or ''

        from datetime import timezone as _tz
        import zoneinfo as _zi
        try:
            _tz_local = _zi.ZoneInfo("America/Sao_Paulo")
        except Exception:
            _tz_local = None

        def _fmt_dt(dt):
            if not dt:
                return 'N/A'
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=_tz.utc)
            if _tz_local:
                dt = dt.astimezone(_tz_local)
            return dt.strftime('%d/%m/%Y %H:%M:%S')

        display_server = server.hostname if server else sensor.name
        if server and server.hostname and sensor.name.upper() in ('PING', 'CPU', 'MEMÓRIA', 'DISCO', 'UPTIME'):
            display_server = server.hostname

        incident_data = {
            'title': f"🔔 LEMBRETE: {incident.title}",
            'description': incident.description or '',
            'severity': incident.severity,
            'server_hostname': display_server,
            'sensor_name': sensor.name,
            'sensor_type': sensor_type,
            'incident_id': incident.id,
            'created_at': _fmt_dt(incident.created_at),
        }

        # Re-notificação: respeitar a matriz de notificação do tenant
        # Para sensores datacenter (conflex/engetron): usar matriz ou DEFAULT_MATRIX
        # Nunca ignorar a configuração do tenant
        effective_st = _effective_sensor_type(sensor_type, sensor.name)
        is_datacenter = effective_st in ('conflex', 'engetron')

        # Resolver canais via matriz (igual ao dispatch_notifications)
        custom_matrix = getattr(tenant, 'notification_matrix', None)
        all_channels = resolve_channels(sensor_type, custom_matrix, sensor.name)

        # Re-notificação: email e teams sempre; outros canais apenas se na matriz E não bloqueados
        channels_to_notify = list(all_channels & {'email', 'teams'})

        escalation_blocked = False
        if is_datacenter:
            try:
                import redis as _redis_lib
                import os as _os
                _redis_url = _os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
                _r = _redis_lib.Redis.from_url(_redis_url, socket_connect_timeout=2)
                escalation_blocked = bool(_r.exists(f"escalation_blocked:{sensor.id}"))
            except Exception:
                pass

        if is_datacenter and not escalation_blocked:
            # Adicionar canais extras da matriz (sms, whatsapp, phone_call) se configurados
            extra = all_channels & {'sms', 'whatsapp', 'phone_call'}
            channels_to_notify += list(extra)
        elif is_datacenter and escalation_blocked:
            logger.info(f"Re-notificação incidente {incident_id}: SMS/WhatsApp/ligação bloqueados para sensor {sensor.id}")

        for channel in channels_to_notify:
            try:
                if channel == 'email':
                    email_config = notification_config.get('email', {})
                    if email_config.get('enabled'):
                        from tasks import send_email_notification_sync
                        result = send_email_notification_sync(email_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Email não habilitado'}

                elif channel == 'teams':
                    teams_config = notification_config.get('teams', {})
                    if teams_config.get('enabled'):
                        from tasks import send_teams_notification_sync
                        result = send_teams_notification_sync(teams_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Teams não habilitado'}

                elif channel == 'sms':
                    twilio_config = notification_config.get('twilio', {})
                    if twilio_config.get('account_sid'):
                        from tasks import send_sms_notification_sync
                        result = send_sms_notification_sync(twilio_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Twilio SMS não configurado'}

                elif channel == 'whatsapp':
                    whatsapp_config = notification_config.get('whatsapp') or notification_config.get('twilio', {})
                    if whatsapp_config.get('account_sid'):
                        from tasks import send_whatsapp_notification_sync
                        result = send_whatsapp_notification_sync(whatsapp_config, incident_data)
                    else:
                        result = {'success': False, 'error': 'Twilio WhatsApp não configurado'}

                elif channel == 'phone_call':
                    escalation_config = notification_config.get('escalation', {})
                    phone_chain = escalation_config.get('phone_chain', [])
                    if not phone_chain:
                        twilio_config = notification_config.get('twilio', {})
                        to_numbers = twilio_config.get('to_numbers', [])
                        if isinstance(to_numbers, str):
                            to_numbers = [n.strip() for n in to_numbers.split(',') if n.strip()]
                        phone_chain = [{"name": f"Contato {i+1}", "number": n} for i, n in enumerate(to_numbers)]
                    if phone_chain:
                        from escalation import start_escalation
                        esc_result = start_escalation(
                            sensor_id=sensor.id,
                            incident_id=incident.id,
                            tenant_id=tenant.id,
                            alert_data={
                                'device_type': effective_st,
                                'problem_description': incident.description or incident.title,
                                'phone_chain': phone_chain,
                                'mode': escalation_config.get('mode', 'sequential'),
                                'interval_minutes': escalation_config.get('interval_minutes', 5),
                                'max_attempts': escalation_config.get('max_attempts', 10),
                                'call_duration_seconds': escalation_config.get('call_duration_seconds', 30),
                            },
                        )
                        result = {'success': esc_result is not None, 'error': None if esc_result else 'Escalação não iniciada (duplicata ou reconhecido)'}
                    else:
                        result = {'success': False, 'error': 'Nenhum número configurado'}

                else:
                    result = {'success': False, 'error': f'Canal desconhecido: {channel}'}

                if result.get('success'):
                    sent.append(channel)
                else:
                    failed.append({'channel': channel, 'error': result.get('error', 'Erro desconhecido')})

            except Exception as e:
                failed.append({'channel': channel, 'error': str(e)})
                logger.error(f"❌ Exceção na re-notificação via '{channel}' para incidente {incident_id}: {e}")

        logger.info(f"🔔 Re-notificação incidente {incident_id}: {len(sent)} enviados, {len(failed)} falharam")
        return {'sent': sent, 'failed': failed}

    except Exception as e:
        logger.error(f"❌ Erro fatal na re-notificação {incident_id}: {e}", exc_info=True)
        return {'sent': sent, 'failed': [{'channel': 'all', 'error': str(e)}]}
    finally:
        db.close()
