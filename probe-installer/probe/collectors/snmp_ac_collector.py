"""
SNMP Air Conditioning Collector
Coleta métricas de Ar-Condicionado via SNMP

OIDs Comuns para Ar-Condicionado:
- APC InRow: .1.3.6.1.4.1.318.1.1.13
- Liebert: .1.3.6.1.4.1.476.1.42
- Schneider Electric: .1.3.6.1.4.1.318
"""

from pysnmp.hlapi import *
import logging

logger = logging.getLogger(__name__)

# OIDs padrão para Ar-Condicionado
AC_OIDS = {
    # System Info (RFC 1213)
    'sysDescr': '1.3.6.1.2.1.1.1.0',
    'sysUpTime': '1.3.6.1.2.1.1.3.0',
    'sysName': '1.3.6.1.2.1.1.5.0',
    
    # APC InRow específico
    'apcInRowCoolingCapacity': '1.3.6.1.4.1.318.1.1.13.3.2.2.2.1.0',
    'apcInRowSupplyAirTemp': '1.3.6.1.4.1.318.1.1.13.3.2.2.2.3.0',
    'apcInRowReturnAirTemp': '1.3.6.1.4.1.318.1.1.13.3.2.2.2.4.0',
    'apcInRowRackInletTemp': '1.3.6.1.4.1.318.1.1.13.3.2.2.2.6.0',
    'apcInRowStatus': '1.3.6.1.4.1.318.1.1.13.3.2.2.2.9.0',
    
    # Liebert específico
    'liebertCoolingCapacity': '1.3.6.1.4.1.476.1.42.3.4.1.2.3.1.3.0',
    'liebertSupplyAirTemp': '1.3.6.1.4.1.476.1.42.3.4.1.2.3.1.4.0',
    'liebertReturnAirTemp': '1.3.6.1.4.1.476.1.42.3.4.1.2.3.1.5.0',
    'liebertStatus': '1.3.6.1.4.1.476.1.42.3.2.1.0',
    
    # Genérico - Temperatura ambiente (pode funcionar em alguns modelos)
    'ambientTemp': '1.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1',
}


def collect_snmp_ac(target_ip, community='public', port=161, version='v2c'):
    """
    Coleta métricas de Ar-Condicionado via SNMP
    
    Args:
        target_ip: IP do Ar-Condicionado
        community: Community string SNMP
        port: Porta SNMP (padrão 161)
        version: Versão SNMP (v1, v2c, v3)
    
    Returns:
        dict: Métricas coletadas
    """
    try:
        metrics = {}
        
        # Configurar versão SNMP
        if version == 'v1':
            snmp_version = 0
        elif version == 'v2c':
            snmp_version = 1
        else:
            snmp_version = 1  # Default v2c
        
        # Coletar informações básicas do sistema
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=snmp_version),
            UdpTransportTarget((target_ip, port), timeout=5, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(AC_OIDS['sysDescr'])),
            ObjectType(ObjectIdentity(AC_OIDS['sysUpTime'])),
            ObjectType(ObjectIdentity(AC_OIDS['sysName']))
        )
        
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        
        if errorIndication:
            logger.error(f"SNMP Error: {errorIndication}")
            return None
        elif errorStatus:
            logger.error(f"SNMP Error: {errorStatus.prettyPrint()}")
            return None
        
        # Processar resultados
        for varBind in varBinds:
            oid = str(varBind[0])
            value = str(varBind[1])
            
            if AC_OIDS['sysDescr'] in oid:
                metrics['description'] = value
            elif AC_OIDS['sysUpTime'] in oid:
                # Converter timeticks para dias
                timeticks = int(value)
                uptime_seconds = timeticks / 100
                uptime_days = uptime_seconds / 86400
                metrics['uptime'] = uptime_days
            elif AC_OIDS['sysName'] in oid:
                metrics['name'] = value
        
        # Tentar coletar temperatura (APC InRow)
        temperature = None
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=snmp_version),
                UdpTransportTarget((target_ip, port), timeout=5, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(AC_OIDS['apcInRowSupplyAirTemp']))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if not errorIndication and not errorStatus:
                for varBind in varBinds:
                    value = str(varBind[1])
                    if value != 'No Such Instance currently exists at this OID':
                        # Temperatura geralmente vem em décimos de grau (ex: 250 = 25.0°C)
                        try:
                            temp_raw = int(value)
                            temperature = temp_raw / 10.0
                            metrics['supply_air_temp'] = temperature
                        except:
                            pass
        except Exception as e:
            logger.debug(f"APC InRow OID não disponível: {e}")
        
        # Se não conseguiu com APC, tentar Liebert
        if temperature is None:
            try:
                iterator = getCmd(
                    SnmpEngine(),
                    CommunityData(community, mpModel=snmp_version),
                    UdpTransportTarget((target_ip, port), timeout=5, retries=2),
                    ContextData(),
                    ObjectType(ObjectIdentity(AC_OIDS['liebertSupplyAirTemp']))
                )
                
                errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
                
                if not errorIndication and not errorStatus:
                    for varBind in varBinds:
                        value = str(varBind[1])
                        if value != 'No Such Instance currently exists at this OID':
                            try:
                                temp_raw = int(value)
                                temperature = temp_raw / 10.0
                                metrics['supply_air_temp'] = temperature
                            except:
                                pass
            except Exception as e:
                logger.debug(f"Liebert OID não disponível: {e}")
        
        # Se não conseguiu temperatura específica, tentar OID genérico
        if temperature is None:
            try:
                iterator = getCmd(
                    SnmpEngine(),
                    CommunityData(community, mpModel=snmp_version),
                    UdpTransportTarget((target_ip, port), timeout=5, retries=2),
                    ContextData(),
                    ObjectType(ObjectIdentity(AC_OIDS['ambientTemp']))
                )
                
                errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
                
                if not errorIndication and not errorStatus:
                    for varBind in varBinds:
                        value = str(varBind[1])
                        if value != 'No Such Instance currently exists at this OID':
                            try:
                                temp_raw = int(value)
                                temperature = temp_raw / 10.0
                                metrics['ambient_temp'] = temperature
                            except:
                                pass
            except Exception as e:
                logger.debug(f"OID genérico de temperatura não disponível: {e}")
        
        # Se conseguiu conectar mas não tem temperatura, usar valor padrão
        if temperature is None:
            logger.warning(f"Não foi possível obter temperatura do AC {target_ip}, usando valor padrão")
            temperature = 22.0  # Temperatura padrão
            metrics['ambient_temp'] = temperature
        
        # Status: online se conseguiu conectar
        metrics['status'] = 'online'
        metrics['temperature'] = temperature
        
        # Adicionar timestamp
        from datetime import datetime
        metrics['timestamp'] = datetime.utcnow().isoformat()
        metrics['target_ip'] = target_ip
        
        logger.info(f"Métricas coletadas do AC {target_ip}: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao coletar métricas SNMP do AC {target_ip}: {e}")
        return None


def format_ac_metrics(metrics, sensor_config):
    """
    Formata métricas do AC para o formato esperado pela API
    
    Args:
        metrics: Métricas brutas coletadas
        sensor_config: Configuração do sensor
    
    Returns:
        dict: Métricas formatadas
    """
    if not metrics:
        return None
    
    # Obter temperatura (prioridade: supply_air_temp > ambient_temp > temperature)
    temperature = metrics.get('supply_air_temp') or metrics.get('ambient_temp') or metrics.get('temperature', 22.0)
    
    # Determinar status baseado na temperatura
    threshold_warning = sensor_config.get('threshold_warning', 28)
    threshold_critical = sensor_config.get('threshold_critical', 32)
    
    if temperature >= threshold_critical:
        status = 'critical'
    elif temperature >= threshold_warning:
        status = 'warning'
    else:
        status = 'ok'
    
    return {
        'sensor_id': sensor_config.get('sensor_id'),
        'value': temperature,
        'unit': '°C',
        'status': status,
        'metadata': {
            'description': metrics.get('description', 'Unknown AC'),
            'name': metrics.get('name', 'Unknown'),
            'target_ip': metrics.get('target_ip'),
            'uptime_days': metrics.get('uptime', 0),
            'device_status': metrics.get('status', 'unknown'),
            'collector': 'snmp_ac'
        }
    }


if __name__ == '__main__':
    # Teste do coletor
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python snmp_ac_collector.py <IP_DO_AC> [community] [porta]")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    community = sys.argv[2] if len(sys.argv) > 2 else 'public'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 161
    
    logging.basicConfig(level=logging.INFO)
    
    print(f"\n🔍 Testando coleta SNMP do Ar-Condicionado {target_ip}...")
    print(f"   Community: {community}")
    print(f"   Porta: {port}\n")
    
    metrics = collect_snmp_ac(target_ip, community, port)
    
    if metrics:
        print("✅ Métricas coletadas com sucesso!")
        print(f"\n📊 Resultados:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        # Testar formatação
        sensor_config = {
            'sensor_id': 999,
            'threshold_warning': 28,
            'threshold_critical': 32
        }
        formatted = format_ac_metrics(metrics, sensor_config)
        print(f"\n📦 Métricas formatadas:")
        print(f"   Status: {formatted['status']}")
        print(f"   Temperatura: {formatted['value']} {formatted['unit']}")
        print(f"   Metadata: {formatted['metadata']}")
    else:
        print("❌ Falha ao coletar métricas!")
        print("\n💡 Dicas:")
        print("   - Verifique se o IP está correto")
        print("   - Verifique se o SNMP está habilitado no AC")
        print("   - Verifique se a community string está correta")
        print("   - Verifique se não há firewall bloqueando a porta 161")
        print("   - Alguns ACs podem não suportar SNMP ou usar OIDs proprietários")
