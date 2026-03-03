"""
SNMP Access Point Collector
Coleta métricas de Access Points WiFi via SNMP

OIDs Comuns para Access Points:
- Ubiquiti UniFi: .1.3.6.1.4.1.41112
- Cisco Aironet: .1.3.6.1.4.1.9.9.273
- TP-Link: .1.3.6.1.4.1.11863
- Aruba: .1.3.6.1.4.1.14823
"""

from pysnmp.hlapi import *
import logging

logger = logging.getLogger(__name__)

# OIDs padrão para Access Points
AP_OIDS = {
    # System Info (RFC 1213)
    'sysDescr': '1.3.6.1.2.1.1.1.0',
    'sysUpTime': '1.3.6.1.2.1.1.3.0',
    'sysName': '1.3.6.1.2.1.1.5.0',
    
    # Interface Stats (RFC 1213)
    'ifNumber': '1.3.6.1.2.1.2.1.0',
    'ifInOctets': '1.3.6.1.2.1.2.2.1.10',
    'ifOutOctets': '1.3.6.1.2.1.2.2.1.16',
    'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',
    
    # Wireless Stats (IEEE 802.11 MIB)
    'dot11StationID': '1.2.840.10036.1.1.1.1.0',
    
    # Ubiquiti UniFi específico
    'unifiApSystemModel': '1.3.6.1.4.1.41112.1.6.3.3.0',
    'unifiApSystemVersion': '1.3.6.1.4.1.41112.1.6.3.6.0',
    'unifiApSystemUptime': '1.3.6.1.4.1.41112.1.6.3.5.0',
    
    # Cisco Aironet específico
    'cDot11ActiveDevices': '1.3.6.1.4.1.9.9.273.1.1.2.1.1',
    
    # TP-Link específico
    'tplinkApModel': '1.3.6.1.4.1.11863.1.1.1.0',
}


def collect_snmp_ap(target_ip, community='public', port=161, version='v2c'):
    """
    Coleta métricas de Access Point via SNMP
    
    Args:
        target_ip: IP do Access Point
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
            ObjectType(ObjectIdentity(AP_OIDS['sysDescr'])),
            ObjectType(ObjectIdentity(AP_OIDS['sysUpTime'])),
            ObjectType(ObjectIdentity(AP_OIDS['sysName']))
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
            
            if AP_OIDS['sysDescr'] in oid:
                metrics['description'] = value
            elif AP_OIDS['sysUpTime'] in oid:
                # Converter timeticks para dias
                timeticks = int(value)
                uptime_seconds = timeticks / 100
                uptime_days = uptime_seconds / 86400
                metrics['uptime'] = uptime_days
            elif AP_OIDS['sysName'] in oid:
                metrics['name'] = value
        
        # Tentar coletar estatísticas de interface
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=snmp_version),
                UdpTransportTarget((target_ip, port), timeout=5, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(AP_OIDS['ifOperStatus'] + '.1'))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if not errorIndication and not errorStatus:
                for varBind in varBinds:
                    value = int(varBind[1])
                    # 1 = up, 2 = down
                    metrics['status'] = 'online' if value == 1 else 'offline'
        except Exception as e:
            logger.warning(f"Não foi possível coletar status da interface: {e}")
            metrics['status'] = 'online'  # Assume online se conseguiu conectar
        
        # Adicionar timestamp
        from datetime import datetime
        metrics['timestamp'] = datetime.utcnow().isoformat()
        metrics['target_ip'] = target_ip
        
        logger.info(f"Métricas coletadas do AP {target_ip}: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao coletar métricas SNMP do AP {target_ip}: {e}")
        return None


def format_ap_metrics(metrics, sensor_config):
    """
    Formata métricas do AP para o formato esperado pela API
    
    Args:
        metrics: Métricas brutas coletadas
        sensor_config: Configuração do sensor
    
    Returns:
        dict: Métricas formatadas
    """
    if not metrics:
        return None
    
    # Determinar status baseado na disponibilidade
    status = 'ok' if metrics.get('status') == 'online' else 'critical'
    
    # Valor principal: uptime em dias
    value = metrics.get('uptime', 0)
    
    return {
        'sensor_id': sensor_config.get('sensor_id'),
        'value': value,
        'unit': 'days',
        'status': status,
        'metadata': {
            'description': metrics.get('description', 'Unknown AP'),
            'name': metrics.get('name', 'Unknown'),
            'target_ip': metrics.get('target_ip'),
            'interface_status': metrics.get('status', 'unknown'),
            'collector': 'snmp_ap'
        }
    }


if __name__ == '__main__':
    # Teste do coletor
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python snmp_ap_collector.py <IP_DO_AP> [community] [porta]")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    community = sys.argv[2] if len(sys.argv) > 2 else 'public'
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 161
    
    logging.basicConfig(level=logging.INFO)
    
    print(f"\n🔍 Testando coleta SNMP do Access Point {target_ip}...")
    print(f"   Community: {community}")
    print(f"   Porta: {port}\n")
    
    metrics = collect_snmp_ap(target_ip, community, port)
    
    if metrics:
        print("✅ Métricas coletadas com sucesso!")
        print(f"\n📊 Resultados:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        # Testar formatação
        sensor_config = {'sensor_id': 999}
        formatted = format_ap_metrics(metrics, sensor_config)
        print(f"\n📦 Métricas formatadas:")
        print(f"   Status: {formatted['status']}")
        print(f"   Valor: {formatted['value']} {formatted['unit']}")
        print(f"   Metadata: {formatted['metadata']}")
    else:
        print("❌ Falha ao coletar métricas!")
        print("\n💡 Dicas:")
        print("   - Verifique se o IP está correto")
        print("   - Verifique se o SNMP está habilitado no AP")
        print("   - Verifique se a community string está correta")
        print("   - Verifique se não há firewall bloqueando a porta 161")
