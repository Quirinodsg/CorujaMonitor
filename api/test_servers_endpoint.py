"""
Teste do endpoint de servidores
"""
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    data={
        "username": "admin@coruja.com",
        "password": "admin123"
    }
)
token = response.json()["access_token"]

print(f"\n{'='*60}")
print(f"TESTE: Endpoint /api/v1/servers/")
print(f"{'='*60}\n")

# Buscar servidores
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/v1/servers/", headers=headers)

print(f"Status: {response.status_code}")
print(f"Servidores retornados: {len(response.json())}\n")

if response.json():
    for server in response.json():
        print(f"  - {server['hostname']}")
        print(f"    ID: {server['id']}")
        print(f"    Probe ID: {server['probe_id']}")
        print()
else:
    print("  ❌ Nenhum servidor retornado!")
    print(f"  Resposta: {response.json()}")
