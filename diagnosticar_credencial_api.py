#!/usr/bin/env python3
"""
Diagnosticar resposta da API de credenciais
"""
import requests
import json
import urllib3

# Desabilitar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_URL = "http://192.168.31.161:8000"
PROBE_TOKEN = "V-PTetiHvbNsZgrkY14PFGRfyv6jPBZxdTb76Z2M7YY"
SERVER_ID = 5  # SRVHVSPRD010

print("=" * 60)
print("DIAGNÓSTICO - API CREDENCIAIS")
print("=" * 60)

url = f"{API_URL}/api/v1/credentials/resolve/{SERVER_ID}"
params = {"probe_token": PROBE_TOKEN}

print(f"\nURL: {url}")
print(f"Params: {params}")
print("\nFazendo requisição...")

try:
    response = requests.get(url, params=params, verify=False, timeout=10)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nHeaders:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\nResponse Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "=" * 60)
        print("ANÁLISE DA CREDENCIAL")
        print("=" * 60)
        
        print(f"\nID: {data.get('id')}")
        print(f"Nome: {data.get('name')}")
        print(f"Tipo: {data.get('credential_type')}")
        print(f"Nível: {data.get('inheritance_level')}")
        
        if data.get('credential_type') == 'wmi':
            username = data.get('username')
            password = data.get('password')
            domain = data.get('domain')
            
            print(f"\nUsername: {username if username else '❌ VAZIO'}")
            print(f"Password: {'✓ Presente' if password else '❌ VAZIO'}")
            print(f"Domain: {domain if domain else '(sem domínio)'}")
            
            if not username or not password:
                print("\n⚠️ PROBLEMA: Credencial WMI incompleta!")
                print("   Username ou Password está vazio")
            else:
                print("\n✓ Credencial WMI completa")
        
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
