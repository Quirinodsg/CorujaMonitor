from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta

from database import get_db
from models import Tenant, User
from auth import get_current_active_user, require_role

# Brazil timezone (UTC-3)
BRAZIL_TZ = timezone(timedelta(hours=-3))

router = APIRouter()


class NotificationConfig(BaseModel):
    email: Optional[Dict[str, Any]] = None
    twilio: Optional[Dict[str, Any]] = None
    teams: Optional[Dict[str, Any]] = None
    whatsapp: Optional[Dict[str, Any]] = None
    telegram: Optional[Dict[str, Any]] = None
    topdesk: Optional[Dict[str, Any]] = None
    glpi: Optional[Dict[str, Any]] = None
    dynamics365: Optional[Dict[str, Any]] = None


class NotificationConfigResponse(BaseModel):
    tenant_id: int
    tenant_name: str
    notification_config: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


@router.get("/config", response_model=NotificationConfigResponse)
async def get_notification_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification configuration for current tenant"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return NotificationConfigResponse(
        tenant_id=tenant.id,
        tenant_name=tenant.name,
        notification_config=tenant.notification_config or {}
    )


@router.put("/config", response_model=NotificationConfigResponse)
async def update_notification_config(
    config: NotificationConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update notification configuration (admin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Build configuration dict
    notification_config = {}
    
    if config.email:
        notification_config['email'] = {
            'enabled': config.email.get('enabled', False),
            'smtp_server': config.email.get('smtp_server'),
            'smtp_port': config.email.get('smtp_port', 587),
            'smtp_user': config.email.get('smtp_user'),
            'smtp_password': config.email.get('smtp_password'),
            'from_email': config.email.get('from_email'),
            'to_emails': config.email.get('to_emails', []),
            'use_tls': config.email.get('use_tls', True)
        }
    
    if config.twilio:
        notification_config['twilio'] = {
            'enabled': config.twilio.get('enabled', False),
            'account_sid': config.twilio.get('account_sid'),
            'auth_token': config.twilio.get('auth_token'),
            'from_number': config.twilio.get('from_number'),
            'to_numbers': config.twilio.get('to_numbers', [])
        }
    
    if config.teams:
        notification_config['teams'] = {
            'enabled': config.teams.get('enabled', False),
            'webhook_url': config.teams.get('webhook_url')
        }
    
    if config.whatsapp:
        notification_config['whatsapp'] = {
            'enabled': config.whatsapp.get('enabled', False),
            'api_key': config.whatsapp.get('api_key'),
            'phone_numbers': config.whatsapp.get('phone_numbers', [])
        }
    
    if config.telegram:
        notification_config['telegram'] = {
            'enabled': config.telegram.get('enabled', False),
            'bot_token': config.telegram.get('bot_token'),
            'chat_ids': config.telegram.get('chat_ids', [])
        }
    
    if config.topdesk:
        notification_config['topdesk'] = {
            'enabled': config.topdesk.get('enabled', False),
            'url': config.topdesk.get('url'),
            'username': config.topdesk.get('username'),
            'password': config.topdesk.get('password'),
            'operator_group': config.topdesk.get('operator_group'),
            'category': config.topdesk.get('category'),
            'subcategory': config.topdesk.get('subcategory')
        }
    
    if config.glpi:
        notification_config['glpi'] = {
            'enabled': config.glpi.get('enabled', False),
            'url': config.glpi.get('url'),
            'app_token': config.glpi.get('app_token'),
            'user_token': config.glpi.get('user_token'),
            'entity_id': config.glpi.get('entity_id'),
            'category_id': config.glpi.get('category_id'),
            'urgency': config.glpi.get('urgency', 4),
            'impact': config.glpi.get('impact', 3)
        }
    
    if config.dynamics365:
        notification_config['dynamics365'] = {
            'enabled': config.dynamics365.get('enabled', False),
            'url': config.dynamics365.get('url'),
            'tenant_id': config.dynamics365.get('tenant_id'),
            'client_id': config.dynamics365.get('client_id'),
            'client_secret': config.dynamics365.get('client_secret'),
            'resource': config.dynamics365.get('resource'),
            'api_version': config.dynamics365.get('api_version', '9.2'),
            'incident_type': config.dynamics365.get('incident_type', 'incident'),
            'priority': config.dynamics365.get('priority', 2),
            'owner_id': config.dynamics365.get('owner_id')
        }
    
    tenant.notification_config = notification_config
    db.commit()
    db.refresh(tenant)
    
    return NotificationConfigResponse(
        tenant_id=tenant.id,
        tenant_name=tenant.name,
        notification_config=tenant.notification_config
    )


@router.post("/test/{channel}")
async def test_notification(
    channel: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Test notification channel"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant or not tenant.notification_config:
        raise HTTPException(status_code=404, detail="Notification config not found")
    
    config = tenant.notification_config.get(channel)
    if not config or not config.get('enabled'):
        raise HTTPException(status_code=400, detail=f"{channel} not configured or disabled")
    
    # Route to appropriate test function
    if channel == 'email':
        return await test_email(db, current_user)
    elif channel == 'teams':
        return await test_teams_internal(config, tenant, current_user)
    elif channel == 'twilio':
        return await test_twilio_internal(config, tenant, current_user)
    elif channel == 'whatsapp':
        return await test_whatsapp_internal(config, tenant, current_user)
    elif channel == 'telegram':
        return await test_telegram_internal(config, tenant, current_user)
    elif channel == 'topdesk':
        return await test_topdesk(db, current_user)
    elif channel == 'glpi':
        return await test_glpi(db, current_user)
    elif channel == 'dynamics365':
        return await test_dynamics365(db, current_user)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown channel: {channel}")



# Email Integration
async def send_email_notification(config: Dict[str, Any], email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send email notification via SMTP
    
    Args:
        config: Email configuration (smtp_server, smtp_port, smtp_user, etc)
        email_data: Email details (subject, body, etc)
    
    Returns:
        Dict with success status and message
    """
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
        raise ValueError("Email configuration incomplete")
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email_data.get('subject', 'Alerta do Coruja Monitor')
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        
        # Plain text version
        text_body = email_data.get('body', '')
        
        # HTML version
        html_body = f"""
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
              .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
              .content {{ padding: 20px; background-color: #f4f4f4; }}
              .alert-box {{ background-color: white; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0; }}
              .alert-box.warning {{ border-left-color: #f39c12; }}
              .alert-box.critical {{ border-left-color: #e74c3c; }}
              .details {{ background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
              .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }}
              .btn {{ display: inline-block; padding: 10px 20px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
          </head>
          <body>
            <div class="header">
              <h1>🦉 Coruja Monitor</h1>
              <p>Sistema de Monitoramento de Infraestrutura</p>
            </div>
            <div class="content">
              <div class="alert-box {email_data.get('severity', 'warning')}">
                <h2>{email_data.get('subject', 'Alerta do Sistema')}</h2>
                <p>{text_body}</p>
              </div>
              {f'<div class="details">{email_data.get("details_html", "")}</div>' if email_data.get("details_html") else ''}
              {f'<a href="{email_data.get("dashboard_url", "#")}" class="btn">Ver no Dashboard</a>' if email_data.get("dashboard_url") else ''}
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
            # Use STARTTLS (port 587)
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            # Use SSL (port 465)
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_emails, msg.as_string())
        server.quit()
        
        return {
            'success': True,
            'message': f'E-mail enviado para {len(to_emails)} destinatário(s)'
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            'success': False,
            'error': 'Falha na autenticação SMTP. Verifique usuário e senha.'
        }
    except smtplib.SMTPException as e:
        return {
            'success': False,
            'error': f'Erro SMTP: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro ao enviar e-mail: {str(e)}'
        }


@router.post("/test/email")
async def test_email(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Test email integration"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant or not tenant.notification_config:
        raise HTTPException(status_code=404, detail="Notification config not found")
    
    config = tenant.notification_config.get('email')
    if not config or not config.get('enabled'):
        raise HTTPException(status_code=400, detail="Email not configured or disabled")
    
    # Test email data
    test_data = {
        'subject': '✅ Teste de Integração - Coruja Monitor',
        'body': '''Este é um e-mail de teste enviado pelo Coruja Monitor.

Se você recebeu este e-mail, a integração está funcionando corretamente!

Informações do teste:
- Data/Hora: ''' + datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S') + '''
- Tenant: ''' + tenant.name + '''
- Usuário: ''' + current_user.email + '''

Próximos passos:
1. Verifique se o e-mail chegou na caixa de entrada
2. Confirme que não está na pasta de spam
3. Adicione o remetente aos contatos confiáveis

Coruja Monitor está pronto para enviar alertas!''',
        'severity': 'warning',
        'details_html': '''
            <strong>Configuração Testada:</strong><br>
            Servidor SMTP: ''' + config.get('smtp_server', 'N/A') + '''<br>
            Porta: ''' + str(config.get('smtp_port', 'N/A')) + '''<br>
            Remetente: ''' + config.get('from_email', 'N/A') + '''<br>
            Destinatários: ''' + str(len(config.get('to_emails', []))) + '''
        '''
    }
    
    result = await send_email_notification(config, test_data)
    
    if result.get('success'):
        return {
            'message': result.get('message'),
            'recipients': config.get('to_emails')
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))


# TOPdesk Integration
async def create_topdesk_incident(config: Dict[str, Any], incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create incident in TOPdesk
    
    Args:
        config: TOPdesk configuration (url, username, password, etc)
        incident_data: Incident details (title, description, severity, etc)
    
    Returns:
        Dict with incident ID and status
    """
    import httpx
    import base64
    import logging
    
    logger = logging.getLogger(__name__)
    
    url = config.get('url', '').rstrip('/')
    username = config.get('username')
    password = config.get('password')
    
    logger.info(f"TOPdesk: Tentando criar incidente em {url} com usuário {username}")
    
    if not all([url, username, password]):
        logger.error("TOPdesk: Configuração incompleta")
        raise ValueError("TOPdesk configuration incomplete")
    
    # Basic authentication
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/json'
    }
    
    # Build incident payload
    # Note: username is the caller (person who opens the ticket), not the operator
    # operatorGroup is where the ticket will be assigned (infrastructure team)
    # Keep it minimal - only required fields
    payload = {
        'callerLookup': {'loginName': username},  # Use configured user as caller (requisitante)
        'briefDescription': incident_data.get('title', 'Alerta do Coruja Monitor'),
        'request': incident_data.get('description', '')
    }
    
    # Add optional fields only if configured
    # These fields must match EXACTLY as they appear in TOPdesk
    if config.get('category'):
        payload['category'] = {'name': config.get('category')}
        logger.info(f"TOPdesk: Categoria configurada: {config.get('category')}")
    if config.get('subcategory'):
        payload['subcategory'] = {'name': config.get('subcategory')}
        logger.info(f"TOPdesk: Subcategoria configurada: {config.get('subcategory')}")
    if config.get('operator_group'):
        payload['operatorGroup'] = {'name': config.get('operator_group')}
        logger.info(f"TOPdesk: Grupo de operadores configurado: {config.get('operator_group')}")
    
    logger.info(f"TOPdesk: Payload: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            logger.info(f"TOPdesk: Enviando POST para {url}/tas/api/incidents")
            response = await client.post(
                f"{url}/tas/api/incidents",
                headers=headers,
                json=payload
            )
            
            logger.info(f"TOPdesk: Status code: {response.status_code}")
            logger.info(f"TOPdesk: Response: {response.text[:500]}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"TOPdesk: Incidente criado com sucesso: {result.get('number')}")
                return {
                    'success': True,
                    'incident_id': result.get('number'),
                    'incident_url': f"{url}/tas/secure/incident?unid={result.get('id')}"
                }
            elif response.status_code == 401:
                logger.error(f"TOPdesk: Erro 401 - Credenciais inválidas ou usuário sem permissão de API")
                return {
                    'success': False,
                    'error': f"Erro de Autenticação (401): Usuário '{username}' ou senha incorretos, ou usuário não tem permissão para usar a API REST do TOPdesk. Verifique: 1) Credenciais corretas, 2) Usuário ativo no TOPdesk, 3) Permissões de API habilitadas"
                }
            elif response.status_code == 400:
                error_detail = response.text
                logger.error(f"TOPdesk: Erro 400 - Dados inválidos: {error_detail}")
                
                # Parse error message
                if 'category' in error_detail.lower():
                    return {
                        'success': False,
                        'error': f"Erro 400: Categoria '{config.get('category')}' não encontrada no TOPdesk. Verifique se o nome está EXATAMENTE como aparece no TOPdesk (maiúsculas/minúsculas importam). Ou deixe o campo vazio para criar sem categoria."
                    }
                elif 'subcategory' in error_detail.lower():
                    return {
                        'success': False,
                        'error': f"Erro 400: Subcategoria '{config.get('subcategory')}' não encontrada no TOPdesk. Verifique se o nome está EXATAMENTE como aparece no TOPdesk. Ou deixe o campo vazio."
                    }
                elif 'operatorgroup' in error_detail.lower() or 'operator' in error_detail.lower():
                    return {
                        'success': False,
                        'error': f"Erro 400: Grupo de Operadores '{config.get('operator_group')}' não encontrado no TOPdesk. Verifique se o nome está EXATAMENTE como aparece no TOPdesk. Ou deixe o campo vazio."
                    }
                else:
                    return {
                        'success': False,
                        'error': f"Erro 400: Dados inválidos - {error_detail[:300]}"
                    }
            else:
                logger.error(f"TOPdesk: Erro na API: {response.status_code} - {response.text[:500]}")
                return {
                    'success': False,
                    'error': f"TOPdesk API error: {response.status_code} - {response.text[:500]}"
                }
    except Exception as e:
        logger.error(f"TOPdesk: Exceção: {type(e).__name__}: {str(e)}")
        return {
            'success': False,
            'error': f"TOPdesk connection error: {str(e)}"
        }


# GLPI Integration
async def create_glpi_ticket(config: Dict[str, Any], ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create ticket in GLPI
    
    Args:
        config: GLPI configuration (url, app_token, user_token, etc)
        ticket_data: Ticket details (title, description, urgency, etc)
    
    Returns:
        Dict with ticket ID and status
    """
    import httpx
    
    url = config.get('url', '').rstrip('/')
    app_token = config.get('app_token')
    user_token = config.get('user_token')
    
    if not all([url, app_token, user_token]):
        raise ValueError("GLPI configuration incomplete")
    
    headers = {
        'Content-Type': 'application/json',
        'App-Token': app_token,
        'Session-Token': ''  # Will be set after init session
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            # Step 1: Initialize session
            init_response = await client.get(
                f"{url}/apirest.php/initSession",
                headers={
                    'Content-Type': 'application/json',
                    'App-Token': app_token,
                    'Authorization': f'user_token {user_token}'
                }
            )
            
            if init_response.status_code != 200:
                return {
                    'success': False,
                    'error': f"GLPI authentication failed: {init_response.status_code}"
                }
            
            session_token = init_response.json().get('session_token')
            headers['Session-Token'] = session_token
            
            # Step 2: Create ticket
            # Map severity to urgency/impact
            urgency = config.get('urgency', 4)
            impact = config.get('impact', 3)
            
            if ticket_data.get('severity') == 'critical':
                urgency = 5  # Very high
                impact = 5   # Very high
            elif ticket_data.get('severity') == 'warning':
                urgency = 3  # Medium
                impact = 3   # Medium
            
            payload = {
                'input': {
                    'name': ticket_data.get('title', 'Alerta do Coruja Monitor'),
                    'content': ticket_data.get('description', ''),
                    'entities_id': config.get('entity_id', 0),
                    'itilcategories_id': config.get('category_id', 0),
                    'urgency': urgency,
                    'impact': impact,
                    'priority': 5 if ticket_data.get('severity') == 'critical' else 3,
                    'type': 1,  # 1 = Incident
                    'status': 2  # 2 = Processing (Assigned)
                }
            }
            
            ticket_response = await client.post(
                f"{url}/apirest.php/Ticket",
                headers=headers,
                json=payload
            )
            
            # Step 3: Kill session
            await client.get(
                f"{url}/apirest.php/killSession",
                headers=headers
            )
            
            if ticket_response.status_code in [200, 201]:
                result = ticket_response.json()
                ticket_id = result.get('id')
                return {
                    'success': True,
                    'ticket_id': ticket_id,
                    'ticket_url': f"{url}/front/ticket.form.php?id={ticket_id}"
                }
            else:
                return {
                    'success': False,
                    'error': f"GLPI API error: {ticket_response.status_code} - {ticket_response.text}"
                }
                
    except Exception as e:
        return {
            'success': False,
            'error': f"GLPI connection error: {str(e)}"
        }


@router.post("/test/topdesk")
async def test_topdesk(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Test TOPdesk integration"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant or not tenant.notification_config:
        raise HTTPException(status_code=404, detail="Notification config not found")
    
    config = tenant.notification_config.get('topdesk')
    if not config or not config.get('enabled'):
        raise HTTPException(status_code=400, detail="TOPdesk not configured or disabled")
    
    # Test incident data
    test_data = {
        'title': 'Teste de Integração - Coruja Monitor',
        'description': 'Este é um chamado de teste criado automaticamente pelo Coruja Monitor para validar a integração com TOPdesk.',
        'severity': 'warning'
    }
    
    result = await create_topdesk_incident(config, test_data)
    
    if result.get('success'):
        return {
            'message': 'Chamado de teste criado com sucesso no TOPdesk!',
            'incident_id': result.get('incident_id'),
            'incident_url': result.get('incident_url')
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))


@router.post("/test/glpi")
async def test_glpi(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Test GLPI integration"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant or not tenant.notification_config:
        raise HTTPException(status_code=404, detail="Notification config not found")
    
    config = tenant.notification_config.get('glpi')
    if not config or not config.get('enabled'):
        raise HTTPException(status_code=400, detail="GLPI not configured or disabled")
    
    # Test ticket data
    test_data = {
        'title': 'Teste de Integração - Coruja Monitor',
        'description': 'Este é um ticket de teste criado automaticamente pelo Coruja Monitor para validar a integração com GLPI.',
        'severity': 'warning'
    }
    
    result = await create_glpi_ticket(config, test_data)
    
    if result.get('success'):
        return {
            'message': 'Ticket de teste criado com sucesso no GLPI!',
            'ticket_id': result.get('ticket_id'),
            'ticket_url': result.get('ticket_url')
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))


# Microsoft Teams Integration
async def send_teams_notification(config: Dict[str, Any], message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send notification to Microsoft Teams via webhook
    
    Args:
        config: Teams configuration (webhook_url)
        message_data: Message details (title, text, severity, etc)
    
    Returns:
        Dict with success status
    """
    import httpx
    
    webhook_url = config.get('webhook_url')
    
    if not webhook_url:
        raise ValueError("Teams webhook URL not configured")
    
    # Determine color based on severity
    severity = message_data.get('severity', 'info')
    color_map = {
        'critical': 'FF0000',  # Red
        'warning': 'FFA500',   # Orange
        'info': '0078D4',      # Blue
        'success': '00FF00'    # Green
    }
    theme_color = color_map.get(severity, '0078D4')
    
    # Build Teams message card
    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": message_data.get('title', 'Alerta do Coruja Monitor'),
        "themeColor": theme_color,
        "title": f"🦉 {message_data.get('title', 'Alerta do Coruja Monitor')}",
        "sections": [
            {
                "activityTitle": message_data.get('subtitle', 'Sistema de Monitoramento'),
                "activitySubtitle": datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S'),
                "activityImage": "https://i.imgur.com/desrDrc.png",
                "facts": message_data.get('facts', []),
                "text": message_data.get('text', '')
            }
        ],
        "potentialAction": message_data.get('actions', [])
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(webhook_url, json=card)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Mensagem enviada para o Teams com sucesso'
                }
            else:
                return {
                    'success': False,
                    'error': f"Teams API error: {response.status_code} - {response.text}"
                }
    except Exception as e:
        return {
            'success': False,
            'error': f"Teams connection error: {str(e)}"
        }


async def test_teams_internal(config: Dict[str, Any], tenant: Tenant, current_user: User) -> Dict[str, Any]:
    """Internal function to test Teams integration"""
    test_data = {
        'title': 'Teste de Integração - Coruja Monitor',
        'subtitle': 'Teste de Notificação',
        'text': 'Este é um teste de integração com Microsoft Teams. Se você está vendo esta mensagem, a integração está funcionando corretamente!',
        'severity': 'info',
        'facts': [
            {'name': 'Tenant:', 'value': tenant.name},
            {'name': 'Usuário:', 'value': current_user.email},
            {'name': 'Data/Hora:', 'value': datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')},
            {'name': 'Status:', 'value': '✅ Integração Ativa'}
        ],
        'actions': [
            {
                "@type": "OpenUri",
                "name": "Abrir Dashboard",
                "targets": [
                    {"os": "default", "uri": "http://localhost:3000"}
                ]
            }
        ]
    }
    
    result = await send_teams_notification(config, test_data)
    
    if result.get('success'):
        return {
            'message': result.get('message'),
            'channel': 'teams'
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))


# Twilio Integration (SMS/Voice)
async def send_twilio_notification(config: Dict[str, Any], message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send SMS notification via Twilio
    
    Args:
        config: Twilio configuration (account_sid, auth_token, from_number, to_numbers)
        message_data: Message details (body, etc)
    
    Returns:
        Dict with success status
    """
    try:
        from twilio.rest import Client
        
        account_sid = config.get('account_sid')
        auth_token = config.get('auth_token')
        from_number = config.get('from_number')
        to_numbers = config.get('to_numbers', [])
        
        if not all([account_sid, auth_token, from_number, to_numbers]):
            raise ValueError("Twilio configuration incomplete")
        
        client = Client(account_sid, auth_token)
        
        message_body = message_data.get('body', 'Alerta do Coruja Monitor')
        
        sent_count = 0
        errors = []
        
        for to_number in to_numbers:
            try:
                # SMS
                message = client.messages.create(
                    body=message_body,
                    from_=from_number,
                    to=to_number
                )
                sent_count += 1

                # Ligação telefônica (TTS - Text to Speech)
                try:
                    call_body = message_data.get('call_body', message_body[:160])
                    call = client.calls.create(
                        twiml=f'<Response><Say language="pt-BR" voice="alice">{call_body}</Say><Pause length="1"/><Say language="pt-BR" voice="alice">{call_body}</Say></Response>',
                        from_=from_number,
                        to=to_number
                    )
                except Exception as call_err:
                    errors.append(f"Ligação {to_number}: {str(call_err)}")
            except Exception as e:
                errors.append(f"{to_number}: {str(e)}")
        
        if sent_count > 0:
            return {
                'success': True,
                'message': f'SMS enviado para {sent_count} número(s)',
                'errors': errors if errors else None
            }
        else:
            return {
                'success': False,
                'error': f'Falha ao enviar SMS: {", ".join(errors)}'
            }
            
    except ImportError:
        return {
            'success': False,
            'error': 'Biblioteca Twilio não instalada. Execute: pip install twilio'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro Twilio: {str(e)}'
        }


async def test_twilio_internal(config: Dict[str, Any], tenant: Tenant, current_user: User) -> Dict[str, Any]:
    """Internal function to test Twilio integration"""
    test_data = {
        'body': f'''🦉 Coruja Monitor - Teste de Integração

Tenant: {tenant.name}
Usuário: {current_user.email}
Data/Hora: {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')}

✅ Se você recebeu este SMS, a integração está funcionando!''',
        'call_body': f'Atenção. Teste do Coruja Monitor. Sistema de monitoramento ativo. Tenant {tenant.name}.'
    }
    
    result = await send_twilio_notification(config, test_data)
    
    if result.get('success'):
        return {
            'message': result.get('message'),
            'channel': 'twilio',
            'errors': result.get('errors')
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))


# WhatsApp Integration
async def send_whatsapp_notification(config: Dict[str, Any], message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send WhatsApp notification via API
    
    Args:
        config: WhatsApp configuration (api_key, phone_numbers)
        message_data: Message details (text, etc)
    
    Returns:
        Dict with success status
    """
    import httpx
    
    api_key = config.get('api_key')
    phone_numbers = config.get('phone_numbers', [])
    
    if not all([api_key, phone_numbers]):
        raise ValueError("WhatsApp configuration incomplete")
    
    # Note: This is a generic implementation. Adjust based on your WhatsApp API provider
    # Common providers: Twilio, MessageBird, WhatsApp Business API, etc.
    
    return {
        'success': False,
        'error': 'WhatsApp integration requires specific API provider configuration. Please contact support.'
    }


async def test_whatsapp_internal(config: Dict[str, Any], tenant: Tenant, current_user: User) -> Dict[str, Any]:
    """Internal function to test WhatsApp integration"""
    test_data = {
        'text': f'''🦉 *Coruja Monitor* - Teste de Integração

*Tenant:* {tenant.name}
*Usuário:* {current_user.email}
*Data/Hora:* {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')}

✅ Se você recebeu esta mensagem, a integração está funcionando!'''
    }
    
    result = await send_whatsapp_notification(config, test_data)
    
    if result.get('success'):
        return {
            'message': result.get('message'),
            'channel': 'whatsapp'
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))


# Telegram Integration
async def send_telegram_notification(config: Dict[str, Any], message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send Telegram notification via Bot API
    
    Args:
        config: Telegram configuration (bot_token, chat_ids)
        message_data: Message details (text, etc)
    
    Returns:
        Dict with success status
    """
    import httpx
    
    bot_token = config.get('bot_token')
    chat_ids = config.get('chat_ids', [])
    
    if not all([bot_token, chat_ids]):
        raise ValueError("Telegram configuration incomplete")
    
    # Determine emoji based on severity
    severity = message_data.get('severity', 'info')
    emoji_map = {
        'critical': '🔴',
        'warning': '🟡',
        'info': '🔵',
        'success': '🟢'
    }
    emoji = emoji_map.get(severity, '🔵')
    
    # Build message text
    text = f"{emoji} *{message_data.get('title', 'Alerta do Coruja Monitor')}*\n\n"
    text += message_data.get('text', '')
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            sent_count = 0
            errors = []
            
            for chat_id in chat_ids:
                try:
                    response = await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={
                            'chat_id': chat_id,
                            'text': text,
                            'parse_mode': 'Markdown'
                        }
                    )
                    
                    if response.status_code == 200:
                        sent_count += 1
                    else:
                        errors.append(f"Chat {chat_id}: {response.text}")
                except Exception as e:
                    errors.append(f"Chat {chat_id}: {str(e)}")
            
            if sent_count > 0:
                return {
                    'success': True,
                    'message': f'Mensagem enviada para {sent_count} chat(s) no Telegram',
                    'errors': errors if errors else None
                }
            else:
                return {
                    'success': False,
                    'error': f'Falha ao enviar mensagem: {", ".join(errors)}'
                }
                
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro Telegram: {str(e)}'
        }


async def test_telegram_internal(config: Dict[str, Any], tenant: Tenant, current_user: User) -> Dict[str, Any]:
    """Internal function to test Telegram integration"""
    test_data = {
        'title': 'Teste de Integração - Coruja Monitor',
        'text': f'''Este é um teste de integração com Telegram.

*Tenant:* {tenant.name}
*Usuário:* {current_user.email}
*Data/Hora:* {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')}

✅ Se você recebeu esta mensagem, a integração está funcionando!''',
        'severity': 'info'
    }
    
    result = await send_telegram_notification(config, test_data)
    
    if result.get('success'):
        return {
            'message': result.get('message'),
            'channel': 'telegram',
            'errors': result.get('errors')
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))



# Microsoft Dynamics 365 Integration
async def create_dynamics365_incident(config: Dict[str, Any], incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create incident in Microsoft Dynamics 365
    
    Args:
        config: Dynamics 365 configuration (url, tenant_id, client_id, client_secret, etc)
        incident_data: Incident details (title, description, severity, etc)
    
    Returns:
        Dict with incident ID and status
    """
    import httpx
    import logging
    
    logger = logging.getLogger(__name__)
    
    url = config.get('url', '').rstrip('/')
    tenant_id = config.get('tenant_id')
    client_id = config.get('client_id')
    client_secret = config.get('client_secret')
    resource = config.get('resource', url)
    api_version = config.get('api_version', '9.2')
    incident_type = config.get('incident_type', 'incident')
    
    logger.info(f"Dynamics 365: Tentando criar incidente em {url}")
    
    if not all([url, tenant_id, client_id, client_secret]):
        logger.error("Dynamics 365: Configuração incompleta")
        raise ValueError("Dynamics 365 configuration incomplete")
    
    try:
        async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
            # Step 1: Get OAuth2 token
            logger.info(f"Dynamics 365: Obtendo token OAuth2 para tenant {tenant_id}")
            
            token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'resource': resource
            }
            
            token_response = await client.post(token_url, data=token_data)
            
            if token_response.status_code != 200:
                logger.error(f"Dynamics 365: Erro ao obter token: {token_response.status_code} - {token_response.text}")
                return {
                    'success': False,
                    'error': f"Erro de autenticação OAuth2: {token_response.status_code} - Verifique tenant_id, client_id e client_secret"
                }
            
            access_token = token_response.json().get('access_token')
            logger.info("Dynamics 365: Token OAuth2 obtido com sucesso")
            
            # Step 2: Create incident
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0',
                'Accept': 'application/json',
                'Prefer': 'return=representation'
            }
            
            # Map severity to Dynamics 365 priority
            # Priority: 1 = High, 2 = Normal, 3 = Low
            priority_map = {
                'critical': 1,  # High
                'warning': 2,   # Normal
                'info': 3       # Low
            }
            priority = priority_map.get(incident_data.get('severity', 'warning'), 2)
            
            # Build incident payload
            # Entity name depends on your Dynamics 365 configuration
            # Common entities: incident (case), msdyn_workorder, etc.
            payload = {
                'title': incident_data.get('title', 'Alerta do Coruja Monitor')[:200],  # Max 200 chars
                'description': incident_data.get('description', '')[:2000],  # Max 2000 chars
                'prioritycode': priority,
                'caseorigincode': 3,  # 3 = Web (you can customize this)
                'casetypecode': 1,    # 1 = Problem
                'statecode': 0,       # 0 = Active
                'statuscode': 1       # 1 = In Progress
            }
            
            # Add owner if configured
            if config.get('owner_id'):
                payload['ownerid@odata.bind'] = f"/systemusers({config.get('owner_id')})"
            
            logger.info(f"Dynamics 365: Payload: {payload}")
            
            # Determine API endpoint based on incident type
            api_endpoint = f"{url}/api/data/v{api_version}/{incident_type}s"
            logger.info(f"Dynamics 365: Enviando POST para {api_endpoint}")
            
            incident_response = await client.post(
                api_endpoint,
                headers=headers,
                json=payload
            )
            
            logger.info(f"Dynamics 365: Status code: {incident_response.status_code}")
            logger.info(f"Dynamics 365: Response: {incident_response.text[:500]}")
            
            if incident_response.status_code in [200, 201, 204]:
                # Get incident ID from response
                if incident_response.status_code == 204:
                    # No content, get ID from OData-EntityId header
                    entity_id_header = incident_response.headers.get('OData-EntityId', '')
                    incident_id = entity_id_header.split('(')[-1].split(')')[0] if '(' in entity_id_header else 'unknown'
                else:
                    result = incident_response.json()
                    incident_id = result.get('incidentid') or result.get('msdyn_workorderid') or result.get('id', 'unknown')
                
                logger.info(f"Dynamics 365: Incidente criado com sucesso: {incident_id}")
                
                return {
                    'success': True,
                    'incident_id': incident_id,
                    'incident_url': f"{url}/main.aspx?pagetype=entityrecord&etn={incident_type}&id={incident_id}"
                }
            elif incident_response.status_code == 401:
                logger.error("Dynamics 365: Erro 401 - Token inválido ou expirado")
                return {
                    'success': False,
                    'error': "Erro de Autenticação (401): Token OAuth2 inválido ou expirado. Verifique as credenciais e permissões do aplicativo no Azure AD."
                }
            elif incident_response.status_code == 403:
                logger.error("Dynamics 365: Erro 403 - Sem permissão")
                return {
                    'success': False,
                    'error': "Erro de Permissão (403): O aplicativo não tem permissão para criar incidentes. Verifique as permissões no Azure AD e Dynamics 365."
                }
            elif incident_response.status_code == 400:
                error_detail = incident_response.text
                logger.error(f"Dynamics 365: Erro 400 - Dados inválidos: {error_detail}")
                return {
                    'success': False,
                    'error': f"Erro 400: Dados inválidos - {error_detail[:300]}"
                }
            else:
                logger.error(f"Dynamics 365: Erro na API: {incident_response.status_code} - {incident_response.text[:500]}")
                return {
                    'success': False,
                    'error': f"Dynamics 365 API error: {incident_response.status_code} - {incident_response.text[:500]}"
                }
                
    except Exception as e:
        logger.error(f"Dynamics 365: Exceção: {type(e).__name__}: {str(e)}")
        return {
            'success': False,
            'error': f"Dynamics 365 connection error: {str(e)}"
        }


@router.post("/test/dynamics365")
async def test_dynamics365(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Test Microsoft Dynamics 365 integration"""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    if not tenant or not tenant.notification_config:
        raise HTTPException(status_code=404, detail="Notification config not found")
    
    config = tenant.notification_config.get('dynamics365')
    if not config or not config.get('enabled'):
        raise HTTPException(status_code=400, detail="Dynamics 365 not configured or disabled")
    
    # Test incident data
    test_data = {
        'title': 'Teste de Integração - Coruja Monitor',
        'description': f'''Este é um incidente de teste criado automaticamente pelo Coruja Monitor para validar a integração com Microsoft Dynamics 365.

Tenant: {tenant.name}
Usuário: {current_user.email}
Data/Hora: {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')}

Se você está vendo este incidente no Dynamics 365, a integração está funcionando corretamente!''',
        'severity': 'warning'
    }
    
    result = await create_dynamics365_incident(config, test_data)
    
    if result.get('success'):
        return {
            'message': 'Incidente de teste criado com sucesso no Dynamics 365!',
            'incident_id': result.get('incident_id'),
            'incident_url': result.get('incident_url')
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))


# Enhanced Twilio Integration with WhatsApp support
async def send_twilio_whatsapp(config: Dict[str, Any], message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send WhatsApp message via Twilio API
    
    Args:
        config: Twilio configuration (account_sid, auth_token, from_number, to_numbers)
        message_data: Message details (body, etc)
    
    Returns:
        Dict with success status
    """
    try:
        from twilio.rest import Client
        
        account_sid = config.get('account_sid')
        auth_token = config.get('auth_token')
        from_number = config.get('from_number')  # Format: whatsapp:+14155238886
        to_numbers = config.get('to_numbers', [])  # Format: whatsapp:+5511999999999
        
        if not all([account_sid, auth_token, from_number, to_numbers]):
            raise ValueError("Twilio WhatsApp configuration incomplete")
        
        # Ensure numbers have whatsapp: prefix
        if not from_number.startswith('whatsapp:'):
            from_number = f'whatsapp:{from_number}'
        
        client = Client(account_sid, auth_token)
        
        message_body = message_data.get('body', 'Alerta do Coruja Monitor')
        
        sent_count = 0
        errors = []
        
        for to_number in to_numbers:
            try:
                # Ensure number has whatsapp: prefix
                if not to_number.startswith('whatsapp:'):
                    to_number = f'whatsapp:{to_number}'
                
                message = client.messages.create(
                    body=message_body,
                    from_=from_number,
                    to=to_number
                )
                sent_count += 1
            except Exception as e:
                errors.append(f"{to_number}: {str(e)}")
        
        if sent_count > 0:
            return {
                'success': True,
                'message': f'WhatsApp enviado para {sent_count} número(s) via Twilio',
                'errors': errors if errors else None
            }
        else:
            return {
                'success': False,
                'error': f'Falha ao enviar WhatsApp: {", ".join(errors)}'
            }
            
    except ImportError:
        return {
            'success': False,
            'error': 'Biblioteca Twilio não instalada. Execute: pip install twilio'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro Twilio WhatsApp: {str(e)}'
        }


# Update WhatsApp integration to use Twilio
async def send_whatsapp_notification_enhanced(config: Dict[str, Any], message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send WhatsApp notification via Twilio API (recommended) or custom API
    
    Args:
        config: WhatsApp configuration
        message_data: Message details
    
    Returns:
        Dict with success status
    """
    # Check if using Twilio for WhatsApp
    if config.get('provider') == 'twilio' or config.get('account_sid'):
        return await send_twilio_whatsapp(config, message_data)
    
    # Otherwise use custom API (if configured)
    api_url = config.get('api_url')
    api_key = config.get('api_key')
    phone_numbers = config.get('phone_numbers', [])
    
    if not all([api_url, api_key, phone_numbers]):
        return {
            'success': False,
            'error': 'WhatsApp configuration incomplete. Configure Twilio (recommended) or custom API provider.'
        }
    
    import httpx
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            sent_count = 0
            errors = []
            
            for phone in phone_numbers:
                try:
                    # Generic API call - adjust based on your provider
                    response = await client.post(
                        api_url,
                        headers={'Authorization': f'Bearer {api_key}'},
                        json={
                            'phone': phone,
                            'message': message_data.get('body', 'Alerta do Coruja Monitor')
                        }
                    )
                    
                    if response.status_code in [200, 201]:
                        sent_count += 1
                    else:
                        errors.append(f"{phone}: HTTP {response.status_code}")
                except Exception as e:
                    errors.append(f"{phone}: {str(e)}")
            
            if sent_count > 0:
                return {
                    'success': True,
                    'message': f'WhatsApp enviado para {sent_count} número(s)',
                    'errors': errors if errors else None
                }
            else:
                return {
                    'success': False,
                    'error': f'Falha ao enviar WhatsApp: {", ".join(errors)}'
                }
    except Exception as e:
        return {
            'success': False,
            'error': f'Erro WhatsApp: {str(e)}'
        }


# Update test function for WhatsApp
async def test_whatsapp_enhanced(config: Dict[str, Any], tenant: Tenant, current_user: User) -> Dict[str, Any]:
    """Enhanced test function for WhatsApp integration"""
    test_data = {
        'body': f'''🦉 *Coruja Monitor* - Teste de Integração

*Tenant:* {tenant.name}
*Usuário:* {current_user.email}
*Data/Hora:* {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M:%S')}

✅ Se você recebeu esta mensagem no WhatsApp, a integração está funcionando corretamente!

_Mensagem enviada via {config.get('provider', 'API customizada')}_'''
    }
    
    result = await send_whatsapp_notification_enhanced(config, test_data)
    
    if result.get('success'):
        return {
            'message': result.get('message'),
            'channel': 'whatsapp',
            'provider': config.get('provider', 'custom'),
            'errors': result.get('errors')
        }
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))
