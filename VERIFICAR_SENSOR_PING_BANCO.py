#!/usr/bin/env python3
"""
Script de Diagnóstico: Sensor PING no Banco de Dados
Verifica se sensor PING existe e se tem métricas associadas
"""

import psycopg2
from datetime import datetime, timedelta

# Configuração do banco
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'coruja_monitor',
    'user': 'coruja',
    'password': 'coruja123'
}

def main():
    print("=" * 80)
    print("DIAGNÓSTICO: SENSOR PING NO BANCO DE DADOS")
    print("=" * 80)
    print()
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados PostgreSQL")
        print()
        
        # 1. VERIFICAR SERVIDORES
        print("=" * 80)
        print("1. SERVIDORES CADASTRADOS")
        print("=" * 80)
        cursor.execute("""
            SELECT id, hostname, ip_address, monitoring_protocol, is_active
            FROM servers
            ORDER BY id
        """)
        servers = cursor.fetchall()
        
        if not servers:
            print("❌ NENHUM SERVIDOR ENCONTRADO!")
            return
        
        for server in servers:
            server_id, hostname, ip, protocol, active = server
            print(f"ID: {server_id} | {hostname} | IP: {ip} | Protocolo: {protocol} | Ativo: {active}")
        print()
        
        # 2. VERIFICAR SENSORES PING
        print("=" * 80)
        print("2. SENSORES PING")
        print("=" * 80)
        cursor.execute("""
            SELECT s.id, s.server_id, s.name, s.sensor_type, s.is_active, srv.hostname
            FROM sensors s
            LEFT JOIN servers srv ON s.server_id = srv.id
            WHERE s.sensor_type = 'ping' OR s.name ILIKE '%ping%'
            ORDER BY s.id
        """)
        ping_sensors = cursor.fetchall()
        
        if not ping_sensors:
            print("❌ NENHUM SENSOR PING ENCONTRADO!")
            print()
            print("CAUSA RAIZ: Sensor PING não foi criado automaticamente")
            print()
            print("SOLUÇÃO:")
            print("  1. Probe deve criar sensor PING automaticamente ao enviar primeira métrica")
            print("  2. Verificar se probe está enviando métricas PING corretamente")
            print("  3. Verificar endpoint /api/v1/metrics/probe/bulk")
            return
        
        print(f"✅ Encontrados {len(ping_sensors)} sensores PING:")
        for sensor in ping_sensors:
            sensor_id, server_id, name, sensor_type, active, hostname = sensor
            print(f"  ID: {sensor_id} | Servidor: {hostname} (ID: {server_id}) | Nome: {name} | Tipo: {sensor_type} | Ativo: {active}")
        print()
        
        # 3. VERIFICAR MÉTRICAS PING
        print("=" * 80)
        print("3. MÉTRICAS PING (ÚLTIMAS 24 HORAS)")
        print("=" * 80)
        
        for sensor in ping_sensors:
            sensor_id = sensor[0]
            sensor_name = sensor[2]
            hostname = sensor[5]
            
            # Contar métricas totais
            cursor.execute("""
                SELECT COUNT(*) FROM metrics WHERE sensor_id = %s
            """, (sensor_id,))
            total_metrics = cursor.fetchone()[0]
            
            # Contar métricas últimas 24h
            cursor.execute("""
                SELECT COUNT(*) FROM metrics 
                WHERE sensor_id = %s 
                AND timestamp >= NOW() - INTERVAL '24 hours'
            """, (sensor_id,))
            recent_metrics = cursor.fetchone()[0]
            
            # Última métrica
            cursor.execute("""
                SELECT value, unit, status, timestamp
                FROM metrics
                WHERE sensor_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (sensor_id,))
            last_metric = cursor.fetchone()
            
            print(f"Sensor: {sensor_name} ({hostname})")
            print(f"  Total de métricas: {total_metrics}")
            print(f"  Métricas (24h): {recent_metrics}")
            
            if last_metric:
                value, unit, status, timestamp = last_metric
                print(f"  Última métrica: {value} {unit} | Status: {status} | {timestamp}")
            else:
                print(f"  ❌ NENHUMA MÉTRICA ENCONTRADA!")
            print()
        
        # 4. DIAGNÓSTICO FINAL
        print("=" * 80)
        print("4. DIAGNÓSTICO FINAL")
        print("=" * 80)
        
        # Verificar se algum sensor PING tem métricas
        has_metrics = False
        for sensor in ping_sensors:
            sensor_id = sensor[0]
            cursor.execute("SELECT COUNT(*) FROM metrics WHERE sensor_id = %s", (sensor_id,))
            if cursor.fetchone()[0] > 0:
                has_metrics = True
                break
        
        if not has_metrics:
            print("❌ PROBLEMA IDENTIFICADO:")
            print("   Sensores PING existem mas NÃO TÊM MÉTRICAS")
            print()
            print("POSSÍVEIS CAUSAS:")
            print("  1. Probe não está enviando métricas PING")
            print("  2. Endpoint /api/v1/metrics/probe/bulk não está salvando métricas PING")
            print("  3. Associação sensor_id está incorreta")
            print()
            print("PRÓXIMOS PASSOS:")
            print("  1. Verificar logs da probe: probe.log")
            print("  2. Verificar se probe coleta PING: método _collect_ping_only()")
            print("  3. Verificar endpoint API: /api/v1/metrics/probe/bulk")
            print("  4. Verificar se métricas PING estão no buffer da probe")
        else:
            print("✅ Sensores PING têm métricas!")
            print()
            print("PROBLEMA PODE SER NO FRONTEND:")
            print("  1. Verificar endpoint /dashboard/health-summary")
            print("  2. Verificar se frontend está buscando métricas corretamente")
            print("  3. Verificar se status 'unknown' está sendo calculado errado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
