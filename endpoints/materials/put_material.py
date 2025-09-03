from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import Material, MaterialCreate
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/materials", tags=["materials"])

@router.put("/{material_id}", response_model=Material)
async def update_material(material_id: int, updated_data: MaterialCreate, db: Session = Depends(get_db)):
    """
    Actualiza un material existente
    """
    try:
        material = db.get(MaterialDB, material_id)
        if not material or material.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material no encontrado"
            )

        material.title = updated_data.title
        material.author = updated_data.author
        material.type = updated_data.type

        db.commit()
        db.refresh(material)

        return material

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )