from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import Material, MaterialCreate
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from sqlalchemy import select

router = APIRouter(prefix="/materials", tags=["materials"])

@router.get("/{material_id}", response_model=Material)
async def get_material(material_id: int, db: Session = Depends(get_db)):
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
        return material

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
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )