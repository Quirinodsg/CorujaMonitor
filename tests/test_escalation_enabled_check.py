"""
Testes para verificar que o campo 'enabled' da configuração de escalação
é respeitado no dispatch_notifications.

Corrige o bug onde phone_call ignorava escalation.enabled=false.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import logging

# Adicionar o diretório worker ao path para importar notification_dispatcher
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'worker'))


def _patch_db_modules(mock_db):
    """
    Mocka database e models no sys.modules para evitar importação real
    (que falha por pydantic config no ambiente de teste).
    As classes em mock_models têm __name__ correto para o side_effect funcionar.
    """
    mock_database = MagicMock()
    mock_database.SessionLocal = MagicMock(return_value=mock_db)

    mock_models = MagicMock()
    for cls_name in ('Incident', 'Sensor', 'Server', 'Tenant', 'Probe'):
        cls_mock = MagicMock()
        cls_mock.__name__ = cls_name
        setattr(mock_models, cls_name, cls_mock)

    return patch.dict('sys.modules', {
        'database': mock_database,
        'models': mock_models,
    })


class TestEscalationEnabledCheck:
    """Testa que phone_call respeita escalation.enabled=false."""

    def test_phone_call_disabled_escalation_not_called(self):
        """
        Quando escalation.enabled=false, start_escalation não deve ser chamado
        e o canal deve retornar erro 'Escalação não habilitada'.
        """
        # Mock do banco de dados
        mock_db = MagicMock()
        
        # Mock do incidente
        mock_incident = MagicMock()
        mock_incident.id = 123
        mock_incident.sensor_id = 456
        mock_incident.title = "Teste"
        mock_incident.description = "Descrição do teste"
        mock_incident.severity = "critical"
        
        # Mock do sensor
        mock_sensor = MagicMock()
        mock_sensor.id = 456
        mock_sensor.server_id = 789
        mock_sensor.probe_id = None
        mock_sensor.sensor_type = "conflex"
        mock_sensor.name = "Ar Condicionado"
        mock_sensor.priority = 3
        
        # Mock do servidor
        mock_server = MagicMock()
        mock_server.id = 789
        mock_server.tenant_id = 1
        mock_server.hostname = "Servidor Teste"
        
        # Mock do tenant com escalation.enabled=false
        mock_tenant = MagicMock()
        mock_tenant.id = 1
        mock_tenant.notification_config = {
            'escalation': {
                'enabled': False,  # ← Campo que estava sendo ignorado
                'phone_chain': [
                    {'name': 'Contato 1', 'number': '+5511999999999'}
                ],
                'mode': 'sequential',
                'interval_minutes': 5,
                'max_attempts': 3,
            }
        }
        mock_tenant.notification_matrix = {
            'conflex': ['phone_call']
        }
        
        # Configurar retornos do mock_db
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_incident,  # Primeira query: Incident
            mock_sensor,    # Segunda query: Sensor
            mock_server,    # Terceira query: Server
            mock_tenant,    # Quarta query: Tenant
        ]
        
        # Patch dos módulos e executar
        with _patch_db_modules(mock_db):
            from notification_dispatcher import dispatch_notifications
            result = dispatch_notifications(incident_id=123)
        
        # Verificações
        assert result['sent'] == []
        assert len(result['failed']) == 1
        assert result['failed'][0]['channel'] == 'phone_call'
        assert result['failed'][0]['error'] == 'Escalação não habilitada'

    def test_phone_call_enabled_escalation_called(self):
        """
        Quando escalation.enabled=true, start_escalation deve ser chamado.
        """
        # Mock do banco de dados
        mock_db = MagicMock()
        
        # Mock do incidente
        mock_incident = MagicMock()
        mock_incident.id = 123
        mock_incident.sensor_id = 456
        mock_incident.title = "Teste"
        mock_incident.description = "Descrição do teste"
        mock_incident.severity = "critical"
        
        # Mock do sensor
        mock_sensor = MagicMock()
        mock_sensor.id = 456
        mock_sensor.server_id = 789
        mock_sensor.probe_id = None
        mock_sensor.sensor_type = "conflex"
        mock_sensor.name = "Ar Condicionado"
        mock_sensor.priority = 3
        
        # Mock do servidor
        mock_server = MagicMock()
        mock_server.id = 789
        mock_server.tenant_id = 1
        mock_server.hostname = "Servidor Teste"
        
        # Mock do tenant com escalation.enabled=true
        mock_tenant = MagicMock()
        mock_tenant.id = 1
        mock_tenant.notification_config = {
            'escalation': {
                'enabled': True,  # ← Escalação habilitada
                'phone_chain': [
                    {'name': 'Contato 1', 'number': '+5511999999999'}
                ],
                'mode': 'sequential',
                'interval_minutes': 5,
                'max_attempts': 3,
            }
        }
        mock_tenant.notification_matrix = {
            'conflex': ['phone_call']
        }
        
        # Configurar retornos do mock_db
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_incident,  # Primeira query: Incident
            mock_sensor,    # Segunda query: Sensor
            mock_server,    # Terceira query: Server
            mock_tenant,    # Quarta query: Tenant
        ]
        
        # Mock do start_escalation para retornar sucesso
        mock_escalation_result = {'sensor_id': 456, 'status': 'active'}
        
        # Patch dos módulos e start_escalation
        with _patch_db_modules(mock_db), \
             patch('escalation.start_escalation', return_value=mock_escalation_result) as mock_start_esc:
            
            from notification_dispatcher import dispatch_notifications
            result = dispatch_notifications(incident_id=123)
        
        # Verificações
        assert result['sent'] == ['phone_call']
        assert result['failed'] == []
        
        # Verificar que start_escalation foi chamado com os parâmetros corretos
        mock_start_esc.assert_called_once_with(
            sensor_id=456,
            incident_id=123,
            tenant_id=1,
            alert_data={
                'device_type': 'conflex',
                'problem_description': 'Descrição do teste',
                'phone_chain': [{'name': 'Contato 1', 'number': '+5511999999999'}],
                'mode': 'sequential',
                'interval_minutes': 5,
                'max_attempts': 3,
                'call_duration_seconds': 30,
            }
        )

    def test_phone_call_no_escalation_config_disabled_by_default(self):
        """
        Quando não há configuração de escalação, enabled=false por padrão.
        """
        # Mock do banco de dados
        mock_db = MagicMock()
        
        # Mock do incidente
        mock_incident = MagicMock()
        mock_incident.id = 123
        mock_incident.sensor_id = 456
        mock_incident.title = "Teste"
        mock_incident.description = "Descrição do teste"
        mock_incident.severity = "critical"
        
        # Mock do sensor
        mock_sensor = MagicMock()
        mock_sensor.id = 456
        mock_sensor.server_id = 789
        mock_sensor.probe_id = None
        mock_sensor.sensor_type = "engetron"
        mock_sensor.name = "Nobreak"
        mock_sensor.priority = 5
        
        # Mock do servidor
        mock_server = MagicMock()
        mock_server.id = 789
        mock_server.tenant_id = 1
        mock_server.hostname = "Servidor Teste"
        
        # Mock do tenant SEM configuração de escalação
        mock_tenant = MagicMock()
        mock_tenant.id = 1
        mock_tenant.notification_config = {}  # ← Sem config de escalação
        mock_tenant.notification_matrix = {
            'engetron': ['phone_call']
        }
        
        # Configurar retornos do mock_db
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_incident,  # Primeira query: Incident
            mock_sensor,    # Segunda query: Sensor
            mock_server,    # Terceira query: Server
            mock_tenant,    # Quarta query: Tenant
        ]
        
        # Patch dos módulos e executar
        with _patch_db_modules(mock_db):
            from notification_dispatcher import dispatch_notifications
            result = dispatch_notifications(incident_id=123)
        
        # Verificações - deve falhar porque enabled=false por padrão
        assert result['sent'] == []
        assert len(result['failed']) == 1
        assert result['failed'][0]['channel'] == 'phone_call'
        assert result['failed'][0]['error'] == 'Escalação não habilitada'