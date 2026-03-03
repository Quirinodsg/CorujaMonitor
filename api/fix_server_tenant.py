"""
Script para corrigir tenant do servidor e probe
"""
from database import SessionLocal
from models import Server, Probe, Tenant

db = SessionLocal()

try:
    print(f"\n{'='*60}")
    print(f"CORRIGIR TENANT DO SERVIDOR E PROBE")
    print(f"{'='*60}\n")
    
    # Buscar tenant TENSO
    tenso = db.query(Tenant).filter(Tenant.name == 'TENSO').first()
    if not tenso:
        print("❌ Tenant TENSO não encontrado!")
        print("Criando tenant TENSO...")
        tenso = Tenant(name='TENSO', slug='tenso', is_active=True)
        db.add(tenso)
        db.commit()
        print(f"✅ Tenant TENSO criado com ID: {tenso.id}")
    else:
        print(f"✅ Tenant TENSO encontrado: ID {tenso.id}")
    
    # Atualizar probe
    probe = db.query(Probe).filter(Probe.name == 'Quirino-Matriz').first()
    if probe:
        print(f"\nProbe encontrada: {probe.name}")
        print(f"  Tenant atual: {probe.tenant_id}")
        probe.tenant_id = tenso.id
        print(f"  Novo tenant: {tenso.id} (TENSO)")
    
    # Atualizar servidor
    server = db.query(Server).filter(Server.hostname == 'DESKTOP-P9VGN04').first()
    if server:
        print(f"\nServidor encontrado: {server.hostname}")
        print(f"  Tenant atual: {server.tenant_id}")
        server.tenant_id = tenso.id
        print(f"  Novo tenant: {tenso.id} (TENSO)")
    
    db.commit()
    
    print(f"\n{'='*60}")
    print(f"✅ CORREÇÃO CONCLUÍDA!")
    print(f"{'='*60}\n")
    
    # Verificar
    print("Verificação:")
    print(f"  Probe {probe.name}: Tenant ID {probe.tenant_id}")
    print(f"  Server {server.hostname}: Tenant ID {server.tenant_id}")
    print(f"  Tenant TENSO: ID {tenso.id}")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}\n")
    db.rollback()
finally:
    db.close()
