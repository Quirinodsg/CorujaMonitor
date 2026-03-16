#!/usr/bin/env python3
"""
Script para diagnosticar parsing de métricas SNMP
Executa coleta SNMP e mostra exatamente quais OIDs estão chegando
"""

import sys
sys.path.insert(0, '.')

from collectors.snmp_collector import SNMPCollector
import json

def main():
    print("=" * 70)
    print("DIAGNÓSTICO DE PARSING SNMP")
    print("=" * 70)
    
    # Configuração
    host = "192.168.31.161"
    community = "public"
    port = 161
    
    print(f"\nColetando de: {host}")
    print(f"Community: {community}")
    print(f"Porta: {port}\n")
    
    # Coletar dados
    collector = SNMPCollector()
    result = collector.collect_snmp_v2c(
        host=host,
        community=community,
        port=port
    )
    
    print(f"Status: {result.get('status')}")
    print(f"Erro: {result.get('error', 'Nenhum')}\n")
    
    if result.get('status') != 'success':
        print("FALHA NA COLETA!")
        return
    
    data = result.get('data', {})
    print(f"Total de OIDs coletados: {len(data)}\n")
    
    # OIDs esperados
    expected_oids = {
        '1.3.6.1.4.1.2021.11.11.0': 'CPU Idle',
        '1.3.6.1.4.1.2021.4.5.0': 'Memória Total',
        '1.3.6.1.4.1.2021.4.6.0': 'Memória Disponível',
        '1.3.6.1.4.1.2021.9.1.9': 'Disco Percentual',
        '1.3.6.1.2.1.1.3.0': 'Uptime',
        '1.3.6.1.2.1.1.5.0': 'Hostname',
        '1.3.6.1.2.1.1.1.0': 'Descrição Sistema',
        '1.3.6.1.4.1.2021.10.1.3.1': 'Load Average 1min'
    }
    
    print("=" * 70)
    print("VERIFICANDO OIDs ESPERADOS")
    print("=" * 70)
    
    found_count = 0
    for oid, description in expected_oids.items():
        found = False
        value = None
        
        # Procurar OID exato ou com sufixo
        for data_oid, data_value in data.items():
            if oid in data_oid:
                found = True
                value = data_value
                break
        
        status = "✓ ENCONTRADO" if found else "✗ NÃO ENCONTRADO"
        print(f"{status:20} | {description:25} | {oid}")
        if found:
            print(f"                     | Valor: {value}")
            found_count += 1
    
    print(f"\nEncontrados: {found_count}/{len(expected_oids)}")
    
    print("\n" + "=" * 70)
    print("TODOS OS OIDs RECEBIDOS")
    print("=" * 70)
    
    for oid, value in sorted(data.items()):
        # Identificar o que é
        desc = "Desconhecido"
        for expected_oid, expected_desc in expected_oids.items():
            if expected_oid in oid:
                desc = expected_desc
                break
        
        print(f"{oid:40} | {desc:25} | {value}")
    
    print("\n" + "=" * 70)
    print("SIMULANDO PARSING")
    print("=" * 70)
    
    # Simular parsing
    metrics = []
    
    # CPU
    OID_CPU_IDLE = '1.3.6.1.4.1.2021.11.11.0'
    for oid, value in data.items():
        if OID_CPU_IDLE in oid:
            try:
                cpu_idle = float(value)
                cpu_usage = 100 - cpu_idle
                metrics.append({
                    'type': 'cpu',
                    'name': 'CPU',
                    'value': cpu_usage,
                    'unit': 'percent'
                })
                print(f"✓ CPU: {cpu_usage:.2f}% (idle: {cpu_idle}%)")
            except ValueError as e:
                print(f"✗ CPU: Erro ao converter valor '{value}': {e}")
    
    # Memória
    OID_MEM_TOTAL = '1.3.6.1.4.1.2021.4.5.0'
    OID_MEM_AVAIL = '1.3.6.1.4.1.2021.4.6.0'
    mem_total = None
    mem_avail = None
    
    for oid, value in data.items():
        if OID_MEM_TOTAL in oid:
            try:
                mem_total = float(value)
                print(f"✓ Memória Total: {mem_total} KB")
            except ValueError as e:
                print(f"✗ Memória Total: Erro ao converter '{value}': {e}")
        elif OID_MEM_AVAIL in oid:
            try:
                mem_avail = float(value)
                print(f"✓ Memória Disponível: {mem_avail} KB")
            except ValueError as e:
                print(f"✗ Memória Disponível: Erro ao converter '{value}': {e}")
    
    if mem_total and mem_avail:
        mem_used_percent = ((mem_total - mem_avail) / mem_total) * 100
        metrics.append({
            'type': 'memory',
            'name': 'Memória',
            'value': mem_used_percent,
            'unit': 'percent'
        })
        print(f"✓ Memória Uso: {mem_used_percent:.2f}%")
    else:
        print(f"✗ Memória: Dados incompletos (total={mem_total}, avail={mem_avail})")
    
    # Disco
    OID_DISK_PERCENT = '1.3.6.1.4.1.2021.9.1.9'
    for oid, value in data.items():
        if OID_DISK_PERCENT in oid:
            try:
                disk_percent = float(value)
                metrics.append({
                    'type': 'disk',
                    'name': 'Disco',
                    'value': disk_percent,
                    'unit': 'percent'
                })
                print(f"✓ Disco: {disk_percent:.2f}%")
                break
            except ValueError as e:
                print(f"✗ Disco: Erro ao converter '{value}': {e}")
    
    print(f"\n{'=' * 70}")
    print(f"RESULTADO FINAL: {len(metrics)} métricas parseadas")
    print(f"{'=' * 70}")
    
    if metrics:
        print("\nMétricas geradas:")
        for metric in metrics:
            print(f"  - {metric['name']}: {metric['value']:.2f} {metric['unit']}")
    else:
        print("\n⚠️ NENHUMA MÉTRICA FOI GERADA!")
        print("\nPossíveis causas:")
        print("1. OIDs retornados não batem com os esperados")
        print("2. Valores não podem ser convertidos para float")
        print("3. Dados estão em formato inesperado")

if __name__ == '__main__':
    main()
