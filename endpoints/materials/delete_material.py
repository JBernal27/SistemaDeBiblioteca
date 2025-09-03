from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import Material, MaterialCreate
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/materials", tags=["materials"])

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(material_id: int, db: Session = Depends(get_db)):
    """
    Elimina (soft delete) un material por su ID
    """
    try:
        material = db.get(MaterialDB, material_id)
        if not material or material.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material no encontrado"
            )

        material.is_deleted = True
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )