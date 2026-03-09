#!/usr/bin/env python3
"""
Script para adicionar servidor automaticamente via API
"""
import httpx
import sys

# Configurações
SERVER_IP = "192.168.31.161"
API_URL = f"http://{SERVER_IP}:3000"
EMAIL = "admin@coruja.com"
PASSWORD = "admin123"
PROBE_TOKEN = "qozrs7hP8ZcrzXc5odjHw60NVejB0RHIeTaFurorDE8"

# Dados do servidor a adicionar
SERVER_NAME = "WIN-15GM8UTRS4K"
SERVER_IP_LOCAL = "127.0.0.1"
TENANT_NAME = "Techbiz"
PROBE_NAME = "WIN-15GM8UTRS4K"

def main():
    print("=" * 60)
    print("  ADICIONAR SERVIDOR AUTOMATICAMENTE")
    print("=" * 60)
    print()
    
    try:
        with httpx.Client(timeout=30.0, verify=False) as client:
            # 1. Fazer login
            print("[1/5] Fazendo login...")
            response = client.post(
                f"{API_URL}/api/v1/auth/login",
                json={"email": EMAIL, "password": PASSWORD}
            )
            
            if response.status_code != 200:
                print(f"[ERRO] Login falhou: {response.status_code}")
                print(response.text)
                return 1
            
            token = response.json().get("access_token")
            print(f"[OK] Login realizado")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. Buscar tenant Techbiz
            print("\n[2/5] Buscando tenant Techbiz...")
            response = client.get(f"{API_URL}/api/v1/tenants", headers=headers)
            
            if response.status_code != 200:
                print(f"[ERRO] Falha ao buscar tenants: {response.status_code}")
                return 1
            
            tenants = response.json()
            tenant_id = None
            for tenant in tenants:
                if tenant.get("name") == TENANT_NAME:
                    tenant_id = tenant.get("id")
                    break
            
            if not tenant_id:
                print(f"[ERRO] Tenant '{TENANT_NAME}' nao encontrado")
                return 1
            
            print(f"[OK] Tenant encontrado: ID={tenant_id}")
            
            # 3. Buscar probe
            print("\n[3/5] Buscando probe...")
            response = client.get(f"{API_URL}/api/v1/probes", headers=headers)
            
            if response.status_code != 200:
                print(f"[ERRO] Falha ao buscar probes: {response.status_code}")
                return 1
            
            probes = response.json()
            probe_id = None
            for probe in probes:
                if probe.get("name") == PROBE_NAME:
                    probe_id = probe.get("id")
                    break
            
            if not probe_id:
                print(f"[AVISO] Probe '{PROBE_NAME}' nao encontrada")
                print("A probe sera associada automaticamente quando enviar metricas")
                probe_id = None
            else:
                print(f"[OK] Probe encontrada: ID={probe_id}")
            
            # 4. Verificar se servidor já existe
            print("\n[4/5] Verificando se servidor ja existe...")
            response = client.get(f"{API_URL}/api/v1/servers", headers=headers)
            
            if response.status_code == 200:
                servers = response.json()
                for server in servers:
                    if server.get("name") == SERVER_NAME:
                        print(f"[OK] Servidor '{SERVER_NAME}' ja existe!")
                        print(f"    ID: {server.get('id')}")
                        print(f"    IP: {server.get('ip_address')}")
                        print(f"    Status: {server.get('status')}")
                        print(f"    Probe: {server.get('probe_name')}")
                        print()
                        print("=" * 60)
                        print("  SERVIDOR JA CADASTRADO")
                        print("=" * 60)
                        return 0
            
            # 5. Adicionar servidor
            print("\n[5/5] Adicionando servidor...")
            
            server_data = {
                "name": SERVER_NAME,
                "ip_address": SERVER_IP_LOCAL,
                "tenant_id": tenant_id,
                "description": "Servidor Windows monitorado pela probe local",
                "status": "active"
            }
            
            if probe_id:
                server_data["probe_id"] = probe_id
            
            response = client.post(
                f"{API_URL}/api/v1/servers",
                headers=headers,
                json=server_data
            )
            
            if response.status_code in [200, 201]:
                server = response.json()
                print(f"[OK] Servidor adicionado com sucesso!")
                print(f"    ID: {server.get('id')}")
                print(f"    Nome: {server.get('name')}")
                print(f"    IP: {server.get('ip_address')}")
                print()
                print("=" * 60)
                print("  SUCESSO!")
                print("=" * 60)
                print()
                print("Aguarde 60-90 segundos para as metricas aparecerem")
                print("Acesse: http://192.168.31.161:3000")
                print("Menu: Servidores > WIN-15GM8UTRS4K")
                return 0
            else:
                print(f"[ERRO] Falha ao adicionar servidor: {response.status_code}")
                print(response.text)
                return 1
                
    except httpx.ConnectError:
        print("[ERRO] Nao foi possivel conectar ao servidor")
        print(f"Verifique se o servidor esta rodando em {API_URL}")
        return 1
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
