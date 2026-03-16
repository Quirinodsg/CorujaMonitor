#!/usr/bin/env python3
"""
Teste manual do SNMP collector
Execute na máquina SRVSONDA001
CORRECAO 09MAR: Compatível com pysnmp 7.x
"""

import sys
sys.path.insert(0, r'C:\Program Files\CorujaMonitor\Probe')

print("=" * 60)
print("TESTE SNMP COLLECTOR - pysnmp 7.x")
print("=" * 60)

# Verificar pysnmp
try:
    import pysnmp
    print(f"\n✓ pysnmp instalado: versão {pysnmp.__version__}")
except ImportError:
    print("\n✗ pysnmp NÃO instalado!")
    sys.exit(1)

# Importar collector
try:
    from collectors.snmp_collector import SNMPCollector
    print("✓ SNMPCollector importado com sucesso")
except Exception as e:
    print(f"✗ Erro ao importar SNMPCollector: {e}")
    sys.exit(1)

# Testar coleta SNMP
collector = SNMPCollector()

host = "192.168.31.161"
community = "public"
port = 161

print(f"\nColetando de: {host}")
print(f"Community: {community}")
print(f"Porta: {port}\n")

result = collector.collect_snmp_v2c(
    host=host,
    community=community,
    port=port
)

print("RESULTADO:")
print("-" * 60)
print(f"Status: {result.get('status')}")
print(f"Host: {result.get('host')}")
print(f"Version: {result.get('version')}")

if result.get('status') == 'success':
    data = result.get('data', {})
    print(f"\n✓ Total de OIDs coletados: {len(data)}")
    
    if len(data) > 0:
        print("\nPrimeiros 10 OIDs:")
        for i, (oid, value) in enumerate(list(data.items())[:10]):
            print(f"  {oid} = {value}")
        print("\n✓ SNMP FUNCIONANDO!")
    else:
        print("\n✗ Nenhum OID coletado - verificar firewall ou SNMP no servidor")
else:
    print(f"\n✗ ERRO: {result.get('error')}")

print("=" * 60)
