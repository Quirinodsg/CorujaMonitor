"""
TimescaleDB Migration Router
Endpoints para verificar e aplicar a migração para TimescaleDB
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pathlib import Path

from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/v1/timescale", tags=["TimescaleDB Migration"])

SQL_FILE = Path(__file__).parent.parent / "migrations" / "timescaledb_setup.sql"


@router.get("/status")
def timescale_status(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Verifica se TimescaleDB está instalado e configurado"""
    try:
        result = db.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'"))
        row = result.fetchone()
        if not row:
            return {"installed": False, "message": "TimescaleDB não instalado"}

        ht = db.execute(text(
            "SELECT hypertable_name FROM timescaledb_information.hypertables "
            "WHERE hypertable_name = 'sensor_metrics'"
        )).fetchone()

        return {
            "installed": True,
            "version": row[0],
            "sensor_metrics_hypertable": ht is not None,
        }
    except Exception as e:
        return {"installed": False, "error": str(e)}


@router.post("/apply")
def apply_migration(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Aplica o script de migração TimescaleDB"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem aplicar migrações")

    if not SQL_FILE.exists():
        raise HTTPException(status_code=404, detail="Script SQL não encontrado")

    sql = SQL_FILE.read_text()
    errors = []

    for statement in sql.split(";"):
        stmt = statement.strip()
        if not stmt or stmt.startswith("--"):
            continue
        try:
            db.execute(text(stmt))
            db.commit()
        except Exception as e:
            errors.append(str(e))
            db.rollback()

    if errors:
        return {"status": "partial", "errors": errors}
    return {"status": "ok", "message": "Migração TimescaleDB aplicada com sucesso"}


@router.get("/chunks")
def list_chunks(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Lista chunks da hypertable sensor_metrics"""
    try:
        result = db.execute(text(
            "SELECT chunk_name, range_start, range_end, is_compressed "
            "FROM timescaledb_information.chunks "
            "WHERE hypertable_name = 'sensor_metrics' "
            "ORDER BY range_start DESC LIMIT 30"
        ))
        rows = result.fetchall()
        return {"chunks": [dict(r._mapping) for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
