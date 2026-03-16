"""
SNMP Collector - Suporte v1, v2c e v3
Coleta métricas de dispositivos via SNMP
CORRECAO 09MAR: Atualizado para pysnmp 7.x API
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Tentar importar pysnmp (versão 7.x tem estrutura diferente)
PYSNMP_AVAILABLE = False
PYSNMP_VERSION = 0

try:
    # pysnmp 7.x - API síncrona
    from pysnmp.hlapi.v1arch.asyncio.sync import (
        getCmd,
        bulkCmd,
        SnmpEngine,
        CommunityData,
        UdpTransportTarget,
        ContextData,
        ObjectType,
        ObjectIdentity
    )
    PYSNMP_AVAILABLE = True
    PYSNMP_VERSION = 7
    logger.info("pysnmp 7.x carregado (v1arch.asyncio.sync)")
except ImportError:
    try:
        # pysnmp 7.x - API alternativa
        from pysnmp.hlapi.v1arch.asyncio import (
            getCmd,
            bulkCmd,
            SnmpEngine,
            CommunityData,
            UdpTransportTarget,
            ContextData,
            ObjectType,
            ObjectIdentity
        )
        PYSNMP_AVAILABLE = True
        PYSNMP_VERSION = 7
        logger.info("pysnmp 7.x carregado (v1arch.asyncio)")
    except ImportError:
        try:
            # pysnmp 4.x - API antiga
            from pysnmp.hlapi import (
                getCmd,
                bulkCmd,
                SnmpEngine,
                CommunityData,
                UdpTransportTarget,
                ContextData,
                ObjectType,
                ObjectIdentity
            )
            PYSNMP_AVAILABLE = True
            PYSNMP_VERSION = 4
            logger.info("pysnmp 4.x carregado")
        except ImportError:
            PYSNMP_AVAILABLE = False
            PYSNMP_VERSION = 0
            logger.warning("pysnmp não está instalado")

class SNMPCollector:
    """Coletor SNMP avançado com suporte a múltiplas versões"""
    
    # OIDs padrão (RFC 1213 - MIB-II)
    STANDARD_OIDS = {
        'sysDescr': '1.3.6.1.2.1.1.1.0',
        'sysUpTime': '1.3.6.1.2.1.1.3.0',
        'sysName': '1.3.6.1.2.1.1.5.0',
        'ifNumber': '1.3.6.1.2.1.2.1.0',
        'ifDescr': '1.3.6.1.2.1.2.2.1.2',
        'ifSpeed': '1.3.6.1.2.1.2.2.1.5',
        'ifInOctets': '1.3.6.1.2.1.2.2.1.10',
        'ifOutOctets': '1.3.6.1.2.1.2.2.1.16',
    }
    
    # OIDs do NET-SNMP (UCD-SNMP-MIB) para servidores Linux
    LINUX_SERVER_OIDS = {
        'memTotalReal': '1.3.6.1.4.1.2021.4.5.0',      # Memória Total (KB)
        'memAvailReal': '1.3.6.1.4.1.2021.4.6.0',      # Memória Disponível (KB)
        'memBuffer': '1.3.6.1.4.1.2021.4.14.0',        # Buffer
        'memCached': '1.3.6.1.4.1.2021.4.15.0',        # Cached
        'ssCpuUser': '1.3.6.1.4.1.2021.11.9.0',        # CPU User %
        'ssCpuSystem': '1.3.6.1.4.1.2021.11.10.0',     # CPU System %
        'ssCpuIdle': '1.3.6.1.4.1.2021.11.11.0',       # CPU Idle %
        'ssCpuRawUser': '1.3.6.1.4.1.2021.11.50.0',    # CPU Raw User
        'ssCpuRawSystem': '1.3.6.1.4.1.2021.11.52.0',  # CPU Raw System
        'ssCpuRawIdle': '1.3.6.1.4.1.2021.11.53.0',    # CPU Raw Idle
        'laLoad1': '1.3.6.1.4.1.2021.10.1.3.1',        # Load Average 1min
        'laLoad5': '1.3.6.1.4.1.2021.10.1.3.2',        # Load Average 5min
        'laLoad15': '1.3.6.1.4.1.2021.10.1.3.3',       # Load Average 15min
        'dskPath': '1.3.6.1.4.1.2021.9.1.2.1',         # Disk Path
        'dskPercent': '1.3.6.1.4.1.2021.9.1.9.1',      # Disk Usage %
        'dskTotal': '1.3.6.1.4.1.2021.9.1.6.1',        # Disk Total (KB)
        'dskUsed': '1.3.6.1.4.1.2021.9.1.8.1',         # Disk Used (KB)
    }
    
    # OIDs de impressoras (Printer MIB - RFC 3805)
    PRINTER_OIDS = {
        'prtMarkerSuppliesLevel': '1.3.6.1.2.1.43.11.1.1.9.1',  # Nível de toner
        'prtMarkerSuppliesMaxCapacity': '1.3.6.1.2.1.43.11.1.1.8.1',  # Capacidade máxima
        'prtMarkerSuppliesType': '1.3.6.1.2.1.43.11.1.1.4.1',  # Tipo (toner/ink)
        'prtMarkerSuppliesDescription': '1.3.6.1.2.1.43.11.1.1.6.1',  # Descrição
        'prtMarkerSuppliesColorantValue': '1.3.6.1.2.1.43.12.1.1.4.1',  # Cor
        'prtConsoleDisplayBufferText': '1.3.6.1.2.1.43.16.5.1.2.1',  # Status display
        'prtGeneralPrinterName': '1.3.6.1.2.1.43.5.1.1.16.1',  # Nome
        'prtGeneralSerialNumber': '1.3.6.1.2.1.43.5.1.1.17.1',  # Serial
        'prtMarkerLifeCount': '1.3.6.1.2.1.43.10.2.1.4.1',  # Contador de páginas
    }
    
    # OIDs de switches/roteadores
    NETWORK_OIDS = {
        'dot1dTpFdbAddress': '1.3.6.1.2.1.17.4.3.1.1',  # MAC addresses
        'dot1dTpFdbPort': '1.3.6.1.2.1.17.4.3.1.2',  # Portas
        'ipRouteNextHop': '1.3.6.1.2.1.4.21.1.7',  # Rotas
        'ipRouteDest': '1.3.6.1.2.1.4.21.1.1',  # Destinos
    }
    
    def __init__(self):
        self.custom_oids = {}
        
    def collect_snmp_v2c(
        self,
        host: str,
        community: str = 'public',
        port: int = 161,
        oids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Coleta dados via SNMP v2c
        CORRECAO 09MAR: Compatível com pysnmp 7.x
        
        Args:
            host: IP ou hostname do dispositivo
            community: Community string (padrão: public)
            port: Porta SNMP (padrão: 161)
            oids: Lista de OIDs para coletar (None = OIDs padrão)
            
        Returns:
            Dicionário com métricas coletadas
        """
        if not PYSNMP_AVAILABLE:
            return {
                'status': 'error',
                'host': host,
                'error': 'pysnmp not installed'
            }
        
        try:
            if oids is None:
                # Coletar OIDs padrão + OIDs de servidor Linux
                oids = list(self.STANDARD_OIDS.values()) + list(self.LINUX_SERVER_OIDS.values())
            
            results = {}
            
            for oid in oids:
                try:
                    # Executar SNMP GET - funciona em pysnmp 4.x e 7.x
                    iterator = getCmd(
                        SnmpEngine(),
                        CommunityData(community, mpModel=1),  # v2c
                        UdpTransportTarget((host, port), timeout=5, retries=2),
                        ContextData(),
                        ObjectType(ObjectIdentity(oid))
                    )
                    
                    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
                    
                    if errorIndication:
                        logger.debug(f"SNMP error for OID {oid}: {errorIndication}")
                        continue
                    elif errorStatus:
                        logger.debug(f"SNMP error for OID {oid}: {errorStatus.prettyPrint()}")
                        continue
                    else:
                        for varBind in varBinds:
                            oid_str = str(varBind[0])
                            value = str(varBind[1])
                            results[oid_str] = value
                except Exception as e:
                    logger.debug(f"Error getting OID {oid}: {e}")
                    continue
            
            return {
                'status': 'success',
                'host': host,
                'version': 'v2c',
                'timestamp': datetime.utcnow().isoformat(),
                'data': results
            }
            
        except Exception as e:
            logger.error(f"Error collecting SNMP v2c from {host}: {e}")
            return {
                'status': 'error',
                'host': host,
                'error': str(e)
            }
    
    def collect_snmp_v3(
        self,
        host: str,
        username: str,
        auth_key: str,
        priv_key: str,
        auth_protocol: str = 'SHA',
        priv_protocol: str = 'AES',
        port: int = 161,
        oids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Coleta dados via SNMP v3 (com autenticação e criptografia)
        
        Args:
            host: IP ou hostname
            username: Nome de usuário SNMPv3
            auth_key: Chave de autenticação
            priv_key: Chave de privacidade (criptografia)
            auth_protocol: Protocolo de autenticação (SHA ou MD5)
            priv_protocol: Protocolo de criptografia (AES ou DES)
            port: Porta SNMP
            oids: Lista de OIDs
            
        Returns:
            Dicionário com métricas
        """
        try:
            if oids is None:
                oids = list(self.STANDARD_OIDS.values())
            
            # Configurar autenticação
            if auth_protocol.upper() == 'SHA':
                auth_proto = usmHMACSHAAuthProtocol
            else:
                auth_proto = usmHMACMD5AuthProtocol
            
            # Configurar criptografia
            if priv_protocol.upper() == 'AES':
                priv_proto = usmAesCfb128Protocol
            else:
                priv_proto = usmDESPrivProtocol
            
            results = {}
            
            for oid in oids:
                iterator = getCmd(
                    SnmpEngine(),
                    UsmUserData(
                        username,
                        authKey=auth_key,
                        privKey=priv_key,
                        authProtocol=auth_proto,
                        privProtocol=priv_proto
                    ),
                    UdpTransportTarget((host, port), timeout=5, retries=2),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )
                
                errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
                
                if errorIndication:
                    logger.error(f"SNMP v3 error: {errorIndication}")
                    continue
                elif errorStatus:
                    logger.error(f"SNMP v3 error: {errorStatus.prettyPrint()}")
                    continue
                else:
                    for varBind in varBinds:
                        oid_str = str(varBind[0])
                        value = str(varBind[1])
                        results[oid_str] = value
            
            return {
                'status': 'success',
                'host': host,
                'version': 'v3',
                'timestamp': datetime.utcnow().isoformat(),
                'data': results
            }
            
        except Exception as e:
            logger.error(f"Error collecting SNMP v3 from {host}: {e}")
            return {
                'status': 'error',
                'host': host,
                'error': str(e)
            }
    
    def collect_printer_metrics(
        self,
        host: str,
        community: str = 'public',
        port: int = 161
    ) -> Dict[str, Any]:
        """
        Coleta métricas específicas de impressoras
        
        Returns:
            Dicionário com níveis de toner, contador de páginas, etc.
        """
        try:
            # Coletar OIDs de impressora
            result = self.collect_snmp_v2c(
                host,
                community,
                port,
                list(self.PRINTER_OIDS.values())
            )
            
            if result['status'] != 'success':
                return result
            
            # Processar dados da impressora
            printer_data = {
                'toner_levels': {},
                'page_count': 0,
                'status': 'unknown',
                'model': 'Unknown'
            }
            
            # Extrair níveis de toner
            for oid, value in result['data'].items():
                if 'prtMarkerSuppliesLevel' in oid:
                    # Identificar cor do toner
                    color = 'black'  # Simplificado
                    try:
                        level = int(value)
                        printer_data['toner_levels'][color] = level
                    except:
                        pass
                
                elif 'prtMarkerLifeCount' in oid:
                    try:
                        printer_data['page_count'] = int(value)
                    except:
                        pass
            
            return {
                'status': 'success',
                'host': host,
                'type': 'printer',
                'timestamp': datetime.utcnow().isoformat(),
                'data': printer_data
            }
            
        except Exception as e:
            logger.error(f"Error collecting printer metrics from {host}: {e}")
            return {
                'status': 'error',
                'host': host,
                'error': str(e)
            }
    
    def bulk_walk(
        self,
        host: str,
        community: str,
        oid: str,
        port: int = 161
    ) -> List[Dict[str, Any]]:
        """
        Executa SNMP WALK (GetBulk) para coletar múltiplos valores
        
        Args:
            host: IP ou hostname
            community: Community string
            oid: OID base para walk
            port: Porta SNMP
            
        Returns:
            Lista de resultados
        """
        try:
            results = []
            
            for (errorIndication,
                 errorStatus,
                 errorIndex,
                 varBinds) in bulkCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=1),
                UdpTransportTarget((host, port), timeout=5, retries=2),
                ContextData(),
                0, 25,  # Non-repeaters, max-repetitions
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False
            ):
                
                if errorIndication:
                    logger.error(f"SNMP walk error: {errorIndication}")
                    break
                elif errorStatus:
                    logger.error(f"SNMP walk error: {errorStatus.prettyPrint()}")
                    break
                else:
                    for varBind in varBinds:
                        results.append({
                            'oid': str(varBind[0]),
                            'value': str(varBind[1])
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in SNMP walk: {e}")
            return []
    
    def discover_device(
        self,
        host: str,
        community: str = 'public',
        port: int = 161
    ) -> Dict[str, Any]:
        """
        Descobre informações básicas do dispositivo via SNMP
        
        Returns:
            Informações do dispositivo (tipo, modelo, uptime, etc.)
        """
        try:
            result = self.collect_snmp_v2c(host, community, port)
            
            if result['status'] != 'success':
                return result
            
            data = result['data']
            
            # Extrair informações
            device_info = {
                'host': host,
                'description': data.get(self.STANDARD_OIDS['sysDescr'], 'Unknown'),
                'name': data.get(self.STANDARD_OIDS['sysName'], 'Unknown'),
                'uptime': data.get(self.STANDARD_OIDS['sysUpTime'], '0'),
                'type': 'unknown',
                'vendor': 'unknown'
            }
            
            # Identificar tipo de dispositivo pela descrição
            desc_lower = device_info['description'].lower()
            if 'printer' in desc_lower or 'hp' in desc_lower:
                device_info['type'] = 'printer'
                device_info['vendor'] = 'HP' if 'hp' in desc_lower else 'Unknown'
            elif 'switch' in desc_lower or 'cisco' in desc_lower:
                device_info['type'] = 'switch'
                device_info['vendor'] = 'Cisco' if 'cisco' in desc_lower else 'Unknown'
            elif 'router' in desc_lower:
                device_info['type'] = 'router'
            
            return {
                'status': 'success',
                'device': device_info,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error discovering device {host}: {e}")
            return {
                'status': 'error',
                'host': host,
                'error': str(e)
            }
    
    def add_custom_oid(self, name: str, oid: str, description: str = ''):
        """Adiciona OID customizado"""
        self.custom_oids[name] = {
            'oid': oid,
            'description': description
        }
        logger.info(f"Added custom OID: {name} = {oid}")
    
    def load_custom_oids_from_file(self, filepath: str):
        """Carrega OIDs customizados de arquivo YAML"""
        try:
            import yaml
            with open(filepath, 'r') as f:
                custom_oids = yaml.safe_load(f)
                for name, config in custom_oids.items():
                    self.add_custom_oid(
                        name,
                        config['oid'],
                        config.get('description', '')
                    )
            logger.info(f"Loaded custom OIDs from {filepath}")
        except Exception as e:
            logger.error(f"Error loading custom OIDs: {e}")
