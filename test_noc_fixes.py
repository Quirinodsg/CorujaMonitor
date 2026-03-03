#!/usr/bin/env python3
"""
Script para testar correções do NOC e Testes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """Faz login e retorna token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={
            "username": "admin@coruja.com",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]

def test_simulated_failures(token):
    """Testa endpoint de falhas simuladas"""
    print("\n" + "="*60)
    print("TESTE 1: Falhas Simuladas Ativas")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/test-tools/simulated-failures",
        headers=headers
    )
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Total de falhas: {data.get('count', 0)}")
    
    if data.get('failures'):
        print("\nFalhas encontradas:")
        for failure in data['failures']:
            print(f"  - {failure['server_name']} / {failure['sensor_name']}")
            print(f"    Severity: {failure['severity']}")
            print(f"    Criado: {failure['created_at']}")
    else:
        print("  Nenhuma falha ativa")
    
    return data

def test_noc_global_status(token):
    """Testa endpoint de status global do NOC"""
    print("\n" + "="*60)
    print("TESTE 2: NOC - Status Global")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/noc/global-status",
        headers=headers
    )
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Total de servidores: {data.get('total_servers', 0)}")
    print(f"Servidores OK: {data.get('servers_ok', 0)}")
    print(f"Servidores Warning: {data.get('servers_warning', 0)}")
    print(f"Servidores Critical: {data.get('servers_critical', 0)}")
    print(f"Disponibilidade: {data.get('availability', 0)}%")
    
    return data

def test_noc_active_incidents(token):
    """Testa endpoint de incidentes ativos do NOC"""
    print("\n" + "="*60)
    print("TESTE 3: NOC - Incidentes Ativos")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/noc/active-incidents",
        headers=headers
    )
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Total de incidentes: {len(data)}")
    
    if data:
        print("\nIncidentes encontrados:")
        for incident in data[:5]:  # Mostrar apenas 5
            print(f"  - {incident['server_name']} / {incident['sensor_name']}")
            print(f"    Severity: {incident['severity']}")
            print(f"    Duração: {incident['duration']}")
    else:
        print("  Nenhum incidente ativo")
    
    return data

def test_noc_kpis(token):
    """Testa endpoint de KPIs do NOC"""
    print("\n" + "="*60)
    print("TESTE 4: NOC - KPIs")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/noc/kpis",
        headers=headers
    )
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"MTTR: {data.get('mttr', 0)} minutos")
    print(f"MTBF: {data.get('mtbf', 0)} horas")
    print(f"SLA: {data.get('sla', 0)}%")
    print(f"Incidentes 24h: {data.get('incidents_24h', 0)}")
    
    return data

def main():
    print("="*60)
    print("TESTE DE CORREÇÕES - NOC E TESTES")
    print("="*60)
    
    try:
        # Login
        print("\nFazendo login...")
        token = login()
        print("✅ Login bem-sucedido")
        
        # Executar testes
        test_simulated_failures(token)
        test_noc_global_status(token)
        test_noc_active_incidents(token)
        test_noc_kpis(token)
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES CONCLUÍDOS")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
