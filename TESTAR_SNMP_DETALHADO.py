#!/usr/bin/env python3
"""
Teste SNMP detalhado com diagnóstico
CORRECAO 09MAR: Mostra exatamente o que está acontecendo
"""

import sys
sys.path.insert(0, r'C:\Program Files\CorujaMonitor\Probe')

print("=" * 70)
print("TESTE SNMP DETALHADO - DIAGNÓSTICO COMPLETO")
print("=" * 70)

# 1. Verificar pysnmp
print("\n[1/5] Verificando pysnmp...")
try:
    import pysnmp
    print(f"✓ pysnmp versão {pysnmp.__version__} instalado")
    
    # Tentar importar funções
    try:
        from pysnmp.hlapi.v1arch.asyncio.sync import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
        print("✓ Usando pysnmp 7.x (v1arch.asyncio.sync)")
        IMPORT_OK = True
    except ImportError:
        try:
            from pysnmp.hlapi.v1arch.asyncio import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
            print("✓ Usando pysnmp 7.x (v1arch.asyncio)")
            IMPORT_OK = True
        except ImportError:
            try:
                from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
                print("✓ Usando pysnmp 4.x (hlapi)")
                IMPORT_OK = True
            except ImportError as e:
                print(f"✗ Não conseguiu importar funções SNMP: {e}")
                IMPORT_OK = False
                
except ImportError as e:
    print(f"✗ pysnmp NÃO instalado: {e}")
    sys.exit(1)

if not IMPORT_OK:
    print("\n✗ pysnmp instalado mas imports falharam")
    print("Tentando instalar versão compatível...")
    print("Execute: pip uninstall pysnmp -y && pip install pysnmp==4.4.12")
    sys.exit(1)

# 2. Testar conectividade básica
print("\n[2/5] Testando conectividade...")
import socket
host = "192.168.31.161"
port = 161

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.sendto(b'test', (host, port))
    print(f"✓ Porta UDP {port} acessível em {host}")
    sock.close()
except Exception as e:
    print(f"✗ Erro de conectividade: {e}")
    print("  POSSÍVEL CAUSA: Firewall bloqueando porta 161 UDP")

# 3. Testar SNMP GET simples
print("\n[3/5] Testando SNMP GET (sysDescr)...")
community = "public"
oid = "1.3.6.1.2.1.1.1.0"  # sysDescr

try:
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((host, port), timeout=5, retries=2),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )
    
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    
    if errorIndication:
        print(f"✗ SNMP Error: {errorIndication}")
        print("  POSSÍVEL CAUSA:")
        if "timeout" in str(errorIndication).lower():
            print("  - Firewall bloqueando")
            print("  - SNMP não está rodando")
            print("  - SNMP não escuta em 0.0.0.0:161")
    elif errorStatus:
        print(f"✗ SNMP Status Error: {errorStatus.prettyPrint()}")
        print("  POSSÍVEL CAUSA:")
        print("  - Community string incorreta")
        print("  - OID não existe")
    else:
        for varBind in varBinds:
            print(f"✓ SNMP funcionando!")
            print(f"  OID: {varBind[0]}")
            print(f"  Valor: {varBind[1]}")
except Exception as e:
    print(f"✗ Exceção: {e}")
    import traceback
    traceback.print_exc()

# 4. Testar múltiplos OIDs
print("\n[4/5] Testando múltiplos OIDs...")
test_oids = [
    ("1.3.6.1.2.1.1.1.0", "sysDescr"),
    ("1.3.6.1.2.1.1.3.0", "sysUpTime"),
    ("1.3.6.1.2.1.1.5.0", "sysName"),
    ("1.3.6.1.4.1.2021.11.11.0", "ssCpuIdle"),
    ("1.3.6.1.4.1.2021.4.5.0", "memTotalReal"),
]

success_count = 0
for oid, name in test_oids:
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),
            UdpTransportTarget((host, port), timeout=3, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        
        if not errorIndication and not errorStatus:
            value = str(varBinds[0][1])
            print(f"  ✓ {name}: {value[:50]}")
            success_count += 1
        else:
            print(f"  ✗ {name}: {errorIndication or errorStatus}")
    except Exception as e:
        print(f"  ✗ {name}: {e}")

print(f"\nResultado: {success_count}/{len(test_oids)} OIDs coletados")

# 5. Usar SNMPCollector
print("\n[5/5] Testando SNMPCollector...")
try:
    from collectors.snmp_collector import SNMPCollector
    collector = SNMPCollector()
    
    result = collector.collect_snmp_v2c(
        host=host,
        community=community,
        port=port
    )
    
    print(f"Status: {result.get('status')}")
    data = result.get('data', {})
    print(f"Total OIDs: {len(data)}")
    
    if len(data) > 0:
        print("\n✓✓✓ SNMP FUNCIONANDO PERFEITAMENTE! ✓✓✓")
        print("\nPrimeiros 5 OIDs:")
        for i, (oid, value) in enumerate(list(data.items())[:5]):
            print(f"  {oid} = {value[:50]}")
    else:
        print("\n✗✗✗ PROBLEMA: SNMP não retorna dados ✗✗✗")
        print("\nVERIFIQUE NO SERVIDOR LINUX:")
        print("1. sudo ufw allow from 192.168.31.0/24 to any port 161 proto udp")
        print("2. sudo ufw reload")
        print("3. sudo systemctl status snmpd")
        
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
