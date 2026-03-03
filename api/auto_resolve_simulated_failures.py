"""
Daemon para auto-resolver falhas simuladas após o tempo configurado
"""
import time
from datetime import datetime, timedelta
import logging
from database import SessionLocal
from models import Incident

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auto_resolve_expired_failures():
    """
    Verifica e resolve falhas simuladas que expiraram
    """
    db = SessionLocal()
    try:
        # Buscar incidentes ativos
        incidents = db.query(Incident).filter(
            Incident.resolved_at.is_(None)
        ).all()
        
        resolved_count = 0
        for incident in incidents:
            # Verificar se é simulado
            if incident.ai_analysis and isinstance(incident.ai_analysis, dict) and incident.ai_analysis.get('simulated'):
                duration_minutes = incident.ai_analysis.get('duration_minutes', 5)
                expiry_time = incident.created_at + timedelta(minutes=duration_minutes)
                
                # Se expirou, resolver
                if datetime.utcnow() >= expiry_time:
                    incident.resolved_at = datetime.utcnow()
                    incident.resolution_notes = f"Auto-resolvido após {duration_minutes} minutos (teste)"
                    resolved_count += 1
                    logger.info(f"Incidente {incident.id} auto-resolvido (expirou após {duration_minutes} min)")
        
        if resolved_count > 0:
            db.commit()
            logger.info(f"Total de {resolved_count} falhas simuladas auto-resolvidas")
        
    except Exception as e:
        logger.error(f"Erro ao auto-resolver falhas: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """
    Loop principal do daemon
    """
    logger.info("Daemon de auto-resolução de falhas simuladas iniciado")
    logger.info("Verificando a cada 30 segundos...")
    
    while True:
        try:
            auto_resolve_expired_failures()
            time.sleep(30)  # Verificar a cada 30 segundos
        except KeyboardInterrupt:
            logger.info("Daemon interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
