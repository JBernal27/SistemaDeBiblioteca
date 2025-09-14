from fastapi import APIRouter, HTTPException, status, Depends , Query
from models.schemas import Material, MaterialCreate
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from sqlalchemy import select, func
from typing import List
from uuid import UUID


router = APIRouter(prefix="/materials", tags=["materials"])

@router.get("/{material_id}", response_model=Material)
async def get_material(material_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene un material por su ID
    """
    try:
        material = db.get(MaterialDB, material_id)
        if not material or material.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material no encontrado"
            )
        return Material(
            id=material.id,
            title=material.title,
            author=material.author,
            type=material.type,
            date_added=material.date_added,
            is_deleted=material.is_deleted,
            created_by=material.created_by,
            updated_by=material.updated_by
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/", response_model=list[Material])
async def get_all_materials(db: Session = Depends(get_db)):
    """
    Obtiene todos los materiales no eliminados
    """
    try:
        stmt = select(MaterialDB).where(MaterialDB.is_deleted == False)
        result = db.execute(stmt).scalars().all()
        return [
            Material(
                id=m.id,
                title=m.title,
                author=m.author,
                type=m.type,
                date_added=m.date_added,
                is_deleted=m.is_deleted,
                created_by=m.created_by,
                updated_by=m.updated_by
            )
            for m in result
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
    
@router.get("/by-author/{author}", response_model=List[Material])
def search_by_author(author: str, db: Session = Depends(get_db)):
    """
    Buscar materiales por autor
    """
    stmt = select(MaterialDB).where(MaterialDB.author.ilike(f"%{author}%"))
    result = db.execute(stmt).scalars().all()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron materiales con ese autor")

    return [
        Material(
            id=m.id,
            title=m.title,
            author=m.author,
            type=m.type,
            date_added=m.date_added,
            is_deleted=m.is_deleted,
            created_by=m.created_by,
            updated_by=m.updated_by
        )
        for m in result
    ]