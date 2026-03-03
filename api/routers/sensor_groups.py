from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from auth import get_current_active_user
from models import User

router = APIRouter()

class SensorGroupCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    icon: str = '📁'
    color: Optional[str] = None

class SensorGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class SensorGroupMove(BaseModel):
    new_parent_id: Optional[int] = None

@router.post("/")
async def create_group(
    group: SensorGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Criar novo grupo de sensores"""
    result = db.execute(text("""
        INSERT INTO sensor_groups (tenant_id, name, parent_id, description, icon, color)
        VALUES (:tenant_id, :name, :parent_id, :description, :icon, :color)
        RETURNING id, name, parent_id, description, icon, color, created_at
    """), {
        "tenant_id": current_user.tenant_id,
        "name": group.name,
        "parent_id": group.parent_id,
        "description": group.description,
        "icon": group.icon,
        "color": group.color
    })
    db.commit()
    
    row = result.fetchone()
    return {
        "id": row[0],
        "name": row[1],
        "parent_id": row[2],
        "description": row[3],
        "icon": row[4],
        "color": row[5],
        "created_at": row[6]
    }

@router.get("/")
async def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Listar todos os grupos em estrutura hierárquica"""
    result = db.execute(text("""
        WITH RECURSIVE group_tree AS (
            -- Grupos raiz
            SELECT 
                id, tenant_id, name, parent_id, description, icon, color,
                created_at, 0 as level, ARRAY[id] as path
            FROM sensor_groups
            WHERE tenant_id = :tenant_id AND parent_id IS NULL
            
            UNION ALL
            
            -- Subgrupos
            SELECT 
                sg.id, sg.tenant_id, sg.name, sg.parent_id, sg.description, 
                sg.icon, sg.color, sg.created_at, gt.level + 1, gt.path || sg.id
            FROM sensor_groups sg
            INNER JOIN group_tree gt ON sg.parent_id = gt.id
            WHERE sg.tenant_id = :tenant_id
        )
        SELECT 
            gt.*,
            COUNT(s.id) as sensor_count
        FROM group_tree gt
        LEFT JOIN sensors s ON s.group_id = gt.id
        GROUP BY gt.id, gt.tenant_id, gt.name, gt.parent_id, gt.description, 
                 gt.icon, gt.color, gt.created_at, gt.level, gt.path
        ORDER BY gt.path
    """), {"tenant_id": current_user.tenant_id})
    
    groups = []
    for row in result:
        groups.append({
            "id": row[0],
            "name": row[2],
            "parent_id": row[3],
            "description": row[4],
            "icon": row[5],
            "color": row[6],
            "created_at": row[7],
            "level": row[8],
            "sensor_count": row[10]
        })
    
    return groups

@router.get("/{group_id}")
async def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obter detalhes de um grupo"""
    result = db.execute(text("""
        SELECT 
            sg.id, sg.name, sg.parent_id, sg.description, sg.icon, sg.color,
            sg.created_at, COUNT(s.id) as sensor_count
        FROM sensor_groups sg
        LEFT JOIN sensors s ON s.group_id = sg.id
        WHERE sg.id = :group_id AND sg.tenant_id = :tenant_id
        GROUP BY sg.id, sg.name, sg.parent_id, sg.description, sg.icon, 
                 sg.color, sg.created_at
    """), {"group_id": group_id, "tenant_id": current_user.tenant_id})
    
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    
    return {
        "id": row[0],
        "name": row[1],
        "parent_id": row[2],
        "description": row[3],
        "icon": row[4],
        "color": row[5],
        "created_at": row[6],
        "sensor_count": row[7]
    }

@router.put("/{group_id}")
async def update_group(
    group_id: int,
    group: SensorGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualizar grupo"""
    updates = []
    params = {"group_id": group_id, "tenant_id": current_user.tenant_id}
    
    if group.name is not None:
        updates.append("name = :name")
        params["name"] = group.name
    if group.description is not None:
        updates.append("description = :description")
        params["description"] = group.description
    if group.icon is not None:
        updates.append("icon = :icon")
        params["icon"] = group.icon
    if group.color is not None:
        updates.append("color = :color")
        params["color"] = group.color
    
    if not updates:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    updates.append("updated_at = NOW()")
    
    db.execute(text(f"""
        UPDATE sensor_groups 
        SET {', '.join(updates)}
        WHERE id = :group_id AND tenant_id = :tenant_id
    """), params)
    db.commit()
    
    return {"message": "Grupo atualizado com sucesso"}

@router.post("/{group_id}/move")
async def move_group(
    group_id: int,
    move: SensorGroupMove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mover grupo para outro pai"""
    # Verificar se não está tentando mover para si mesmo ou descendente
    if move.new_parent_id == group_id:
        raise HTTPException(status_code=400, detail="Não pode mover grupo para si mesmo")
    
    db.execute(text("""
        UPDATE sensor_groups 
        SET parent_id = :new_parent_id, updated_at = NOW()
        WHERE id = :group_id AND tenant_id = :tenant_id
    """), {
        "group_id": group_id,
        "new_parent_id": move.new_parent_id,
        "tenant_id": current_user.tenant_id
    })
    db.commit()
    
    return {"message": "Grupo movido com sucesso"}

@router.delete("/{group_id}")
async def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Excluir grupo (sensores ficam sem grupo)"""
    # Verificar se grupo existe
    result = db.execute(text("""
        SELECT id FROM sensor_groups 
        WHERE id = :group_id AND tenant_id = :tenant_id
    """), {"group_id": group_id, "tenant_id": current_user.tenant_id})
    
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    
    # Remover referências de sensores
    db.execute(text("""
        UPDATE sensors 
        SET group_id = NULL 
        WHERE group_id = :group_id
    """), {"group_id": group_id})
    
    # Mover subgrupos para o pai do grupo sendo excluído
    db.execute(text("""
        UPDATE sensor_groups 
        SET parent_id = (
            SELECT parent_id FROM sensor_groups WHERE id = :group_id
        )
        WHERE parent_id = :group_id
    """), {"group_id": group_id})
    
    # Excluir grupo
    db.execute(text("""
        DELETE FROM sensor_groups 
        WHERE id = :group_id AND tenant_id = :tenant_id
    """), {"group_id": group_id, "tenant_id": current_user.tenant_id})
    
    db.commit()
    
    return {"message": "Grupo excluído com sucesso"}
