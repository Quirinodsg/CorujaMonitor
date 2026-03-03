"""
Teste direto do endpoint de falhas simuladas
"""
from database import SessionLocal
from models import Incident, Sensor, Server

db = SessionLocal()

try:
    # Buscar todos os incidentes ativos
    incidents = db.query(Incident).join(Sensor).join(Server).filter(
        Incident.resolved_at.is_(None)
    ).all()
    
    print(f"\n{'='*60}")
    print(f"TESTE: Endpoint de Falhas Simuladas")
    print(f"{'='*60}\n")
    
    print(f"Total de incidentes ativos: {len(incidents)}\n")
    
    result = []
    for incident in incidents:
        print(f"Incidente ID: {incident.id}")
        print(f"  Title: {incident.title}")
        print(f"  ai_analysis type: {type(incident.ai_analysis)}")
        print(f"  ai_analysis value: {incident.ai_analysis}")
        
        # Verificar se é simulado
        if incident.ai_analysis:
            print(f"  É dict? {isinstance(incident.ai_analysis, dict)}")
            if isinstance(incident.ai_analysis, dict):
                print(f"  Tem 'simulated'? {incident.ai_analysis.get('simulated')}")
                
                if incident.ai_analysis.get('simulated'):
                    print(f"  ✅ SIMULADO - Será incluído na lista")
                    result.append({
                        'id': incident.id,
                        'sensor_id': incident.sensor_id,
                        'sensor_name': incident.sensor.name,
                        'server_name': incident.sensor.server.hostname,
                        'severity': incident.severity,
                        'title': incident.title,
                        'created_at': incident.created_at.isoformat(),
                        'duration_minutes': incident.ai_analysis.get('duration_minutes', 5)
                    })
                else:
                    print(f"  ❌ NÃO SIMULADO")
        else:
            print(f"  ❌ ai_analysis é None")
        
        print()
    
    print(f"{'='*60}")
    print(f"RESULTADO FINAL")
    print(f"{'='*60}\n")
    print(f"Total de falhas simuladas: {len(result)}\n")
    
    if result:
        print("Falhas encontradas:")
        for failure in result:
            print(f"  - {failure['server_name']} / {failure['sensor_name']}")
            print(f"    Severity: {failure['severity']}")
            print(f"    Duração: {failure['duration_minutes']} minutos")
            print()
    else:
        print("❌ Nenhuma falha simulada encontrada!")
    
finally:
    db.close()
