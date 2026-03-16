"""
Metrics Batch Router — ingestão em lote de métricas do pipeline de streaming.

POST /api/v1/metrics/batch  — recebe até 1000 métricas por request
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics Batch"])

MAX_BATCH_SIZE = 1000


class MetricItem(BaseModel):
    sensor_id: int
    server_id: int
    sensor_type: str
    value: float
    unit: str = ""
    status: str = "ok"
    timestamp: Optional[float] = None


@router.post("/batch")
def ingest_batch(
    items: List[MetricItem],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Ingere lote de métricas.
    Aceita até 1000 itens por request.
    """
    if len(items) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Lote muito grande: máximo {MAX_BATCH_SIZE} itens"
        )

    inserted = 0
    errors = 0

    for item in items:
        try:
            ts = datetime.fromtimestamp(item.timestamp, tz=timezone.utc) if item.timestamp else datetime.now(timezone.utc)

            db.execute(
                """
                INSERT INTO sensor_metrics (sensor_id, server_id, sensor_type, value, unit, status, timestamp)
                VALUES (:sensor_id, :server_id, :sensor_type, :value, :unit, :status, :timestamp)
                ON CONFLICT DO NOTHING
                """,
                {
                    "sensor_id": item.sensor_id,
                    "server_id": item.server_id,
                    "sensor_type": item.sensor_type,
                    "value": item.value,
                    "unit": item.unit,
                    "status": item.status,
                    "timestamp": ts,
                }
            )
            inserted += 1
        except Exception as e:
            logger.warning(f"Erro ao inserir métrica sensor_id={item.sensor_id}: {e}")
            errors += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao commitar lote: {e}")
        raise HTTPException(status_code=500, detail="Erro ao persistir métricas")

    return {
        "inserted": inserted,
        "errors": errors,
        "total": len(items),
    }
