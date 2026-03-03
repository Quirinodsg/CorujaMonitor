#!/usr/bin/env python3
"""
Script para fechar incidentes que já foram resolvidos
"""
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import Incident, Sensor, Metric

def fechar_incidentes_resolvidos():
    """Fecha incidentes cujos sensores voltaram ao normal"""
    db = SessionLocal()
    try:
        # Buscar incidentes abertos ou reconhecidos
        incidentes_ativos = db.query(Incident).filter(
            Incident.status.in_(['open', 'acknowledged'])
        ).all()
        
        print(f"\n📋 Encontrados {len(incidentes_ativos)} incidentes ativos\n")
        
        fechados = 0
        
        for incidente in incidentes_ativos:
            # Buscar última métrica do sensor
            ultima_metrica = db.query(Metric).filter(
                Metric.sensor_id == incidente.sensor_id
            ).order_by(Metric.timestamp.desc()).first()
            
            if not ultima_metrica:
                print(f"⚠️  Incidente {incidente.id}: Sem métricas recentes")
                continue
            
            # Verificar se sensor está OK ou se métrica é muito antiga (mais de 5 minutos)
            # Se métrica tem status None, considerar como problema no banco e fechar
            # Usar timezone aware datetime para comparação
            now = datetime.now(timezone.utc)
            if ultima_metrica.timestamp.tzinfo is None:
                ultima_metrica_ts = ultima_metrica.timestamp.replace(tzinfo=timezone.utc)
            else:
                ultima_metrica_ts = ultima_metrica.timestamp
            
            metrica_antiga = (now - ultima_metrica_ts).total_seconds() > 300
            
            if ultima_metrica.status == 'ok' or ultima_metrica.status is None or metrica_antiga:
                print(f"✅ Fechando incidente {incidente.id}:")
                print(f"   Sensor: {incidente.sensor.name}")
                print(f"   Servidor: {incidente.sensor.server.hostname}")
                print(f"   Status atual: {ultima_metrica.status}")
                print(f"   Valor: {ultima_metrica.value} {ultima_metrica.unit}")
                print(f"   Timestamp: {ultima_metrica.timestamp}")
                
                # Fechar incidente
                incidente.status = "resolved"
                incidente.resolved_at = datetime.utcnow()
                if ultima_metrica.status is None:
                    incidente.resolution_notes = "Auto-resolvido: métrica com status NULL corrigida (script manual)"
                elif metrica_antiga:
                    incidente.resolution_notes = "Auto-resolvido: métrica muito antiga, aguardando atualização (script manual)"
                else:
                    incidente.resolution_notes = "Auto-resolvido: sensor voltou ao normal (script manual)"
                db.commit()
                
                fechados += 1
                print(f"   ✅ Incidente fechado!\n")
            else:
                print(f"⚠️  Incidente {incidente.id} ainda ativo:")
                print(f"   Sensor: {incidente.sensor.name}")
                print(f"   Status: {ultima_metrica.status}")
                print(f"   Valor: {ultima_metrica.value} {ultima_metrica.unit}")
                print(f"   Timestamp: {ultima_metrica.timestamp}\n")
        
        print(f"\n{'='*50}")
        print(f"✅ Fechados: {fechados} incidentes")
        print(f"⚠️  Ainda ativos: {len(incidentes_ativos) - fechados} incidentes")
        print(f"{'='*50}\n")
        
        return fechados
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("  FECHAR INCIDENTES RESOLVIDOS")
    print("=" * 50)
    
    fechados = fechar_incidentes_resolvidos()
    
    if fechados > 0:
        print("\n✅ Operação concluída!")
        print("   Recarregue a página para ver as mudanças")
    else:
        print("\n⚠️  Nenhum incidente foi fechado")
