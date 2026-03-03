"""
Script para resolver todos os incidentes de teste
"""
from database import SessionLocal
from models import Incident
from datetime import datetime

db = SessionLocal()

try:
    # Buscar todos os incidentes ativos
    incidents = db.query(Incident).filter(
        Incident.resolved_at.is_(None)
    ).all()
    
    print(f"\n{'='*60}")
    print(f"RESOLVER INCIDENTES DE TESTE")
    print(f"{'='*60}\n")
    
    print(f"Total de incidentes ativos: {len(incidents)}\n")
    
    resolved_count = 0
    for incident in incidents:
        # Verificar se é teste
        if incident.ai_analysis and isinstance(incident.ai_analysis, dict) and incident.ai_analysis.get('simulated'):
            print(f"✅ Resolvendo incidente {incident.id}: {incident.title}")
            incident.resolved_at = datetime.utcnow()
            incident.resolution_notes = "Resolvido manualmente via script de limpeza"
            resolved_count += 1
        else:
            print(f"⏭️  Pulando incidente {incident.id} (não é teste)")
    
    if resolved_count > 0:
        db.commit()
        print(f"\n{'='*60}")
        print(f"✅ {resolved_count} incidentes de teste resolvidos!")
        print(f"{'='*60}\n")
    else:
        print(f"\n⚠️  Nenhum incidente de teste encontrado\n")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}\n")
    db.rollback()
finally:
    db.close()
