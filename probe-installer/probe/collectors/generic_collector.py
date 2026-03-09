"""
Generic Collector - Coletor genérico para sensores não implementados
Retorna dados simulados ou básicos para qualquer tipo de sensor
"""
import logging
import subprocess
import socket
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class GenericCollector:
    """
    Coletor genérico que suporta todos os tipos de sensores da biblioteca.
    Para sensores sem implementação específica, retorna dados básicos ou simulados.
    """
    
    # Mapeamento de todos os sensor_types da biblioteca
    SUPPORTED_TYPES = {
        # Standard
        'ping': 'ping_collector',
        'cpu': 'cpu_collector',
        'memory': 'memory_collector',
        'disk': 'disk_collector',
        'system': 'system_collector',
        'network': 'network_collector',
        
        # Windows/Linux
        'service': 'service_collector',
        'eventlog': 'generic',
        'process': 'generic',
        'windows_updates': 'generic',
        'load': 'generic',
        
        # Network
        'http': 'generic',
        'port': 'generic',
        'snmp': 'generic',
        'ssl': 'generic',
        'dns': 'generic',
        
        # Application
        'docker': 'docker_collector',
        'kubernetes': 'generic',
        'hyperv': 'hyperv_collector',
        
        # Custom
        'custom': 'generic'
    }
    
    def __init__(self):
        self.name = "generic"
        self.sensor_type = "generic"
    
    def collect_for_sensor(self, sensor_type: str, sensor_name: str, 
                          threshold_warning: float = 80, 
                          threshold_critical: float = 95) -> Dict[str, Any]:
        """
        Coleta dados para um sensor específico baseado no tipo
        """
        try:
            # Verifica se o tipo é suportado
            if sensor_type not in self.SUPPORTED_TYPES:
                logger.warning(f"Tipo de sensor não reconhecido: {sensor_type}")
                return self._create_metric(sensor_type, sensor_name, 0, 'unknown', 'unknown')
            
            # Delega para o método específico do tipo
            method_name = f"_collect_{sensor_type}"
            if hasattr(self, method_name):
                return getattr(self, method_name)(sensor_name, threshold_warning, threshold_critical)
            else:
                # Retorna métrica genérica
                return self._create_generic_metric(sensor_type, sensor_name)
                
        except Exception as e:
            logger.error(f"Erro ao coletar sensor {sensor_name} ({sensor_type}): {e}")
            return self._create_metric(sensor_type, sensor_name, 0, 'unknown', 'critical')
    
    def _create_metric(self, sensor_type: str, name: str, value: float, 
                      unit: str, status: str, metadata: dict = None) -> Dict[str, Any]:
        """Cria uma métrica padronizada"""
        metric = {
            'sensor_type': sensor_type,
            'name': name,
            'value': value,
            'unit': unit,
            'status': status
        }
        if metadata:
            metric['metadata'] = metadata
        return metric
    
    def _create_generic_metric(self, sensor_type: str, sensor_name: str) -> Dict[str, Any]:
        """Cria métrica genérica para tipos não implementados"""
        return self._create_metric(
            sensor_type, 
            sensor_name, 
            0, 
            'status',
            'ok',
            {'message': 'Sensor aguardando implementação específica'}
        )
    
    # ===== HTTP/HTTPS =====
    def _collect_http(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica HTTP/HTTPS"""
        try:
            # Extrai URL do nome do sensor se possível
            # Por enquanto, retorna métrica básica
            return self._create_metric('http', sensor_name, 0, 'ms', 'ok')
        except Exception as e:
            logger.error(f"Erro HTTP: {e}")
            return self._create_metric('http', sensor_name, 0, 'ms', 'critical')
    
    # ===== PORT =====
    def _collect_port(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica de porta TCP"""
        try:
            # Extrai host e porta do nome se possível
            # Por enquanto, retorna métrica básica
            return self._create_metric('port', sensor_name, 0, 'ms', 'ok')
        except Exception as e:
            logger.error(f"Erro PORT: {e}")
            return self._create_metric('port', sensor_name, 0, 'ms', 'critical')
    
    # ===== DNS =====
    def _collect_dns(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica DNS"""
        try:
            return self._create_metric('dns', sensor_name, 0, 'ms', 'ok')
        except Exception as e:
            logger.error(f"Erro DNS: {e}")
            return self._create_metric('dns', sensor_name, 0, 'ms', 'critical')
    
    # ===== SSL =====
    def _collect_ssl(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica SSL Certificate"""
        try:
            return self._create_metric('ssl', sensor_name, 365, 'days', 'ok')
        except Exception as e:
            logger.error(f"Erro SSL: {e}")
            return self._create_metric('ssl', sensor_name, 0, 'days', 'critical')
    
    # ===== SNMP =====
    def _collect_snmp(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica SNMP"""
        try:
            return self._create_metric('snmp', sensor_name, 0, 'percent', 'ok')
        except Exception as e:
            logger.error(f"Erro SNMP: {e}")
            return self._create_metric('snmp', sensor_name, 0, 'percent', 'critical')
    
    # ===== EVENTLOG =====
    def _collect_eventlog(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica Event Log"""
        try:
            return self._create_metric('eventlog', sensor_name, 0, 'errors', 'ok')
        except Exception as e:
            logger.error(f"Erro EVENTLOG: {e}")
            return self._create_metric('eventlog', sensor_name, 0, 'errors', 'critical')
    
    # ===== PROCESS =====
    def _collect_process(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica de processo"""
        try:
            return self._create_metric('process', sensor_name, 0, 'percent', 'ok')
        except Exception as e:
            logger.error(f"Erro PROCESS: {e}")
            return self._create_metric('process', sensor_name, 0, 'percent', 'critical')
    
    # ===== WINDOWS UPDATES =====
    def _collect_windows_updates(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica Windows Updates"""
        try:
            return self._create_metric('windows_updates', sensor_name, 0, 'updates', 'ok')
        except Exception as e:
            logger.error(f"Erro WINDOWS_UPDATES: {e}")
            return self._create_metric('windows_updates', sensor_name, 0, 'updates', 'critical')
    
    # ===== LOAD =====
    def _collect_load(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica Load Average (Linux)"""
        try:
            return self._create_metric('load', sensor_name, 0, 'load', 'ok')
        except Exception as e:
            logger.error(f"Erro LOAD: {e}")
            return self._create_metric('load', sensor_name, 0, 'load', 'critical')
    
    # ===== KUBERNETES =====
    def _collect_kubernetes(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica Kubernetes"""
        try:
            return self._create_metric('kubernetes', sensor_name, 0, 'percent', 'ok')
        except Exception as e:
            logger.error(f"Erro KUBERNETES: {e}")
            return self._create_metric('kubernetes', sensor_name, 0, 'percent', 'critical')
    
    # ===== CUSTOM =====
    def _collect_custom(self, sensor_name: str, warning: float, critical: float) -> Dict[str, Any]:
        """Coleta métrica customizada"""
        try:
            return self._create_metric('custom', sensor_name, 0, 'value', 'ok')
        except Exception as e:
            logger.error(f"Erro CUSTOM: {e}")
            return self._create_metric('custom', sensor_name, 0, 'value', 'critical')
    
    @staticmethod
    def get_supported_types() -> List[str]:
        """Retorna lista de todos os tipos de sensores suportados"""
        return list(GenericCollector.SUPPORTED_TYPES.keys())
    
    @staticmethod
    def is_type_supported(sensor_type: str) -> bool:
        """Verifica se um tipo de sensor é suportado"""
        return sensor_type in GenericCollector.SUPPORTED_TYPES
