"""
Script para testar o fluxo completo de incidentes:
1. Simular falha
2. Verificar incidente criado
3. Resolver incidente
4. Verificar métrica simulada deletada
5. Verificar sensor voltou ao normal
"""

import requests
import time
import json

BASE_URL = "http://192.168.30.189:8000"
EMAIL = "admin@coruja.com"
PASSWORD = "admin123"

def login():
    """Fazer login e obter token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={"username": EMAIL, "password": PASSWORD}
    )
    response.raise_for_status()
    return response.json()["access_token"]

def simulate_failure(token, sensor_id, failure_type="critical", value=98.0):
    """Simular falha em um sensor"""
    print(f"\n1. Simulando falha {failure_type} no sensor {sensor_id}...")
    response = requests.post(
        f"{BASE_URL}/api/v1/test-tools/simulate-failure",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "sensor_id": sensor_id,
            "failure_type": failure_type,
            "value": value,
            "duration_minutes": 5
        }
    )
    response.raise_for_status()
    result = response.json()
    print(f"   ✓ Falha simulada: {result['sensor_name']} = {result['value']}%")
    return result

def get_open_incidents(token):
    """Buscar incidentes abertos"""
    print("\n2. Verificando incidentes abertos...")
    response = requests.get(
        f"{BASE_URL}/api/v1/incidents/?status=open",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    incidents = response.json()
    print(f"   ✓ {len(incidents)} incidente(s) aberto(s)")
    for inc in incidents:
        print(f"     - ID {inc['id']}: {inc['title']} (Sensor {inc['sensor_id']})")
    return incidents

def get_sensor_metrics(token, sensor_id):
    """Buscar última métrica do sensor"""
    response = requests.get(
        f"{BASE_URL}/api/v1/metrics/?sensor_id={sensor_id}&limit=1",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    metrics = response.json()
    if metrics:
        metric = metrics[0]
        print(f"   Sensor {sensor_id}: {metric['value']}{metric['unit']} - {metric['status'].upper()}")
        return metric
    return None

def resolve_incident(token, incident_id, notes="Teste de resolução automática"):
    """Resolver incidente"""
    print(f"\n3. Resolvendo incidente {incident_id}...")
    response = requests.post(
        f"{BASE_URL}/api/v1/incidents/{incident_id}/resolve",
        headers={"Authorization": f"Bearer {token}"},
        json={"resolution_notes": notes}
    )
    response.raise_for_status()
    result = response.json()
    print(f"   ✓ Incidente resolvido")
    print(f"   ✓ Métricas simuladas deletadas: {result.get('simulated_metrics_deleted', 0)}")
    return result

def main():
    print("=" * 60)
    print("TESTE DE FLUXO COMPLETO DE INCIDENTES")
    print("=" * 60)
    
    # Login
    print("\n0. Fazendo login...")
    token = login()
    print("   ✓ Login realizado com sucesso")
    
    # Escolher sensor para teste (CPU = 199)
    sensor_id = 199
    
    # Verificar estado inicial
    print(f"\n📊 Estado inicial do sensor {sensor_id}:")
    get_sensor_metrics(token, sensor_id)
    
    # Simular falha
    simulate_failure(token, sensor_id, "critical", 96.0)
    
    # Aguardar 2 segundos
    time.sleep(2)
    
    # Verificar incidentes
    incidents = get_open_incidents(token)
    
    if not incidents:
        print("\n❌ ERRO: Nenhum incidente foi criado!")
        return
    
    # Verificar métrica simulada
    print(f"\n📊 Estado após simulação:")
    metric = get_sensor_metrics(token, sensor_id)
    
    if not metric:
        print("   ❌ ERRO: Nenhuma métrica encontrada!")
        return
    
    if metric['status'] != 'critical':
        print(f"   ⚠️ AVISO: Status esperado 'critical', encontrado '{metric['status']}'")
    
    # Resolver incidente
    incident_id = incidents[0]['id']
    result = resolve_incident(token, incident_id, "Teste automatizado - incidente resolvido")
    
    # Aguardar 2 segundos
    time.sleep(2)
    
    # Verificar se incidente foi resolvido
    print("\n4. Verificando se incidente foi resolvido...")
    open_incidents = get_open_incidents(token)
    
    if open_incidents:
        print(f"   ⚠️ AVISO: Ainda há {len(open_incidents)} incidente(s) aberto(s)")
    else:
        print("   ✓ Nenhum incidente aberto")
    
    # Aguardar probe coletar nova métrica (60 segundos)
    print("\n5. Aguardando probe coletar nova métrica (60 segundos)...")
    for i in range(60, 0, -10):
        print(f"   Aguardando {i} segundos...")
        time.sleep(10)
    
    # Verificar estado final
    print(f"\n📊 Estado final do sensor {sensor_id}:")
    final_metric = get_sensor_metrics(token, sensor_id)
    
    if not final_metric:
        print("   ❌ ERRO: Nenhuma métrica encontrada!")
        return
    
    # Verificar se voltou ao normal
    print("\n" + "=" * 60)
    print("RESULTADO DO TESTE")
    print("=" * 60)
    
    if final_metric['status'] == 'ok':
        print("✅ SUCESSO! Sensor voltou ao normal")
        print(f"   Valor atual: {final_metric['value']}{final_metric['unit']}")
    else:
        print(f"❌ FALHA! Sensor ainda está em {final_metric['status'].upper()}")
        print(f"   Valor atual: {final_metric['value']}{final_metric['unit']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
