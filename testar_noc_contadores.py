#!/usr/bin/env python3
"""
Script para testar contadores do NOC Real-Time
"""

import requests
import json
from datetime import datetime

# Configuração
API_URL = "http://localhost:8000"
# Você precisa pegar o token de um usuário logado

def test_noc_dashboard():
    """Testa o endpoint do dashboard NOC"""
    
    print("=" * 60)
    print("TESTE DE CONTADORES NOC REAL-TIME")
    print("=" * 60)
    print()
    
    # Fazer login primeiro
    print("1. Fazendo login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/auth/login",
            data=login_data
        )
        
        if response.status_code != 200:
            print(f"❌ Erro no login: {response.status_code}")
            print(response.text)
            return
        
        token = response.json()["access_token"]
        print("✅ Login realizado com sucesso")
        print()
        
        # Buscar dashboard
        print("2. Buscando dashboard NOC...")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{API_URL}/api/v1/noc-realtime/realtime/dashboard",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao buscar dashboard: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        print("✅ Dashboard carregado com sucesso")
        print()
        
        # Exibir contadores
        print("=" * 60)
        print("CONTADORES DO SISTEMA")
        print("=" * 60)
        
        summary = data.get("summary", {})
        
        print(f"✅ Servidores OK:       {summary.get('servers_ok', 0)}")
        print(f"⚠️  Servidores Warning:  {summary.get('servers_warning', 0)}")
        print(f"🔥 Servidores Critical: {summary.get('servers_critical', 0)}")
        print(f"⚫ Servidores Offline:  {summary.get('servers_offline', 0)}")
        print(f"📊 Total de Servidores: {summary.get('total_servers', 0)}")
        print()
        print(f"🚨 Total de Incidentes: {summary.get('total_incidents', 0)}")
        print(f"🔥 Incidentes Críticos: {summary.get('critical_incidents', 0)}")
        print(f"⚠️  Incidentes Warning:  {summary.get('warning_incidents', 0)}")
        print()
        
        # Exibir servidores
        print("=" * 60)
        print("DETALHES DOS SERVIDORES")
        print("=" * 60)
        
        servers = data.get("servers", [])
        if not servers:
            print("⚠️  Nenhum servidor encontrado")
        else:
            for server in servers:
                status_icon = {
                    'ok': '✅',
                    'warning': '⚠️',
                    'critical': '🔥',
                    'offline': '⚫'
                }.get(server['status'], '❓')
                
                print(f"{status_icon} {server['hostname']} ({server['ip_address']})")
                print(f"   Status: {server['status']}")
                print(f"   Disponibilidade: {server['availability']}%")
                print(f"   Incidentes Críticos: {server['critical_incidents']}")
                print(f"   Incidentes Warning: {server['warning_incidents']}")
                print(f"   Total de Sensores: {server['total_sensors']}")
                print()
        
        # Exibir incidentes
        print("=" * 60)
        print("INCIDENTES ATIVOS")
        print("=" * 60)
        
        incidents = data.get("incidents", [])
        if not incidents:
            print("✅ Nenhum incidente ativo")
        else:
            for incident in incidents:
                severity_icon = '🔥' if incident['severity'] == 'critical' else '⚠️'
                print(f"{severity_icon} {incident['server_name']} - {incident['sensor_name']}")
                print(f"   Descrição: {incident['description']}")
                print(f"   Duração: {incident['duration_text']}")
                print()
        
        print("=" * 60)
        print("TESTE CONCLUÍDO")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_noc_dashboard()
