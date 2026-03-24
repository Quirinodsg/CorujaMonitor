"""
cleanup_network_incidents.py
Limpa incidentes e alertas inteligentes gerados por sensores network_in/network_out.
Execução: python cleanup_network_incidents.py

Também atualiza alert_mode=metric_only para todos os sensores network_in/network_out existentes.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from sqlalchemy import text

def run():
    db = SessionLocal()
    try:
        # 1. Buscar IDs dos sensores network_in/network_out
        sensor_rows = db.execute(text("""
            SELECT id, name, sensor_type FROM sensors
            WHERE sensor_type IN ('network_in', 'network_out')
        """)).fetchall()

        sensor_ids = [r.id for r in sensor_rows]
        print(f"Sensores network_in/out encontrados: {len(sensor_ids)}")
        for r in sensor_rows:
            print(f"  - ID {r.id}: {r.name} ({r.sensor_type})")

        if not sensor_ids:
            print("Nenhum sensor network_in/out encontrado. Nada a fazer.")
            return

        ids_tuple = tuple(sensor_ids)

        # 2. Contar incidentes a remover
        count_row = db.execute(text(
            "SELECT COUNT(*) FROM incidents WHERE sensor_id = ANY(:ids)"
        ), {"ids": list(ids_tuple)}).scalar()
        print(f"\nIncidentes a remover: {count_row}")

        # 3. Remover remediation_logs vinculados
        db.execute(text("""
            DELETE FROM remediation_logs
            WHERE incident_id IN (
                SELECT id FROM incidents WHERE sensor_id = ANY(:ids)
            )
        """), {"ids": list(ids_tuple)})

        # 4. Remover ai_analysis_logs vinculados (se existir)
        try:
            db.execute(text("""
                DELETE FROM ai_analysis_logs
                WHERE incident_id IN (
                    SELECT id FROM incidents WHERE sensor_id = ANY(:ids)
                )
            """), {"ids": list(ids_tuple)})
        except Exception:
            pass  # tabela pode não existir

        # 5. Remover incidentes
        deleted_incidents = db.execute(text(
            "DELETE FROM incidents WHERE sensor_id = ANY(:ids) RETURNING id"
        ), {"ids": list(ids_tuple)}).fetchall()
        print(f"Incidentes removidos: {len(deleted_incidents)}")

        # 6. Limpar intelligent_alerts com root_cause contendo "Sem topologia"
        try:
            deleted_alerts = db.execute(text("""
                DELETE FROM intelligent_alerts
                WHERE root_cause LIKE '%Sem topologia%'
                   OR root_cause LIKE '%host do evento mais antigo%'
                   OR title LIKE '%network_in%'
                   OR title LIKE '%network_out%'
                   OR title LIKE '%Network IN%'
                   OR title LIKE '%Network OUT%'
                RETURNING id
            """)).fetchall()
            print(f"Alertas inteligentes removidos: {len(deleted_alerts)}")
        except Exception as e:
            print(f"Aviso: não foi possível limpar intelligent_alerts: {e}")

        # 7. Atualizar alert_mode=metric_only para todos os sensores network_in/out
        updated = db.execute(text("""
            UPDATE sensors
            SET alert_mode = 'metric_only'
            WHERE sensor_type IN ('network_in', 'network_out')
              AND (alert_mode IS NULL OR alert_mode != 'metric_only')
            RETURNING id
        """)).fetchall()
        print(f"Sensores atualizados para metric_only: {len(updated)}")

        db.commit()
        print("\n✅ Limpeza concluída com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run()
