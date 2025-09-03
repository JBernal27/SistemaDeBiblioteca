from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import Material, MaterialCreate
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/materials", tags=["materials"])

@router.post("/", response_model=Material, status_code=status.HTTP_201_CREATED)
async def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo material
    """
    try:
        stmt = select(MaterialDB).where(MaterialDB.title == material.title)
        result = db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El material ya existe"
            )
        
        db_material = MaterialDB(
            title=material.title,
            author=material.author,
            type=material.type)

        db.add(db_material)
        db.commit()
        db.refresh(db_material)

        created_material = Material(
            id=db_material.id,
            title=db_material.title,
            author=db_material.author,
            type=db_material.type,
            date_added=db_material.date_added,
            is_deleted=db_material.is_deleted
        )

        return created_material

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
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
