from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import Material, MaterialCreate, TokenData
from common import MaterialType
from sqlalchemy.orm import Session
from database.connection import get_db, Material as MaterialDB
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from common.middleware import require_admin

router = APIRouter(prefix="/materials", tags=["materials"])


@router.post("/", response_model=Material, status_code=status.HTTP_201_CREATED)
async def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Crea un nuevo material en el sistema.
    Solo accesible para administradores.

    Args:
        material: MaterialCreate - Datos del material a crear
        db: Session - Sesión de la base de datos 
        current_user: TokenData - Token del administrador 

    Returns:
        Material - Detalles del material creado

    Raises:
        HTTPException(400) - Tipo de material inválido o material duplicado
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        valid_types = [t.value for t in MaterialType]
        if material.type.value not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo inválido. Debe ser uno de: {valid_types}",
            )

        exists = (
            db.query(MaterialDB)
            .filter(
                MaterialDB.title == material.title, MaterialDB.is_deleted == False
            )
            .first()
            is not None
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="El material ya existe"
            )

        db_material = MaterialDB(
            title=material.title, author=material.author, type=material.type.value
        )

        db.add(db_material)
        db.flush()

        setattr(
            db_material, "created_by", str(current_user.id)
        )
        setattr(
            db_material, "updated_by", str(current_user.id)
        )

        db.commit()
        db.refresh(db_material)

        created_material = Material.model_validate(db_material, from_attributes=True)

        return created_material

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
