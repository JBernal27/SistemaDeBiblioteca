from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import Material, MaterialCreate, TokenData
from sqlalchemy.orm import Session
from database.connection import get_db, Material as MaterialDB, MaterialType as MaterialTypeDB
from sqlalchemy.exc import IntegrityError
from common.middleware import require_admin
from uuid import uuid4
from datetime import datetime, timezone

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
        # Verificar si el tipo de material existe
        material_type = db.query(MaterialTypeDB).filter(MaterialTypeDB.id == material.type_id).first()
        if not material_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tipo de material especificado no existe.",
            )

        # Verificar si ya existe un material con el mismo título
        exists = (
            db.query(MaterialDB)
            .filter(MaterialDB.title == material.title, MaterialDB.is_deleted == False)
            .first()
            is not None
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un material con este título.",
            )

        # Crear el nuevo material
        db_material = MaterialDB(
            id=uuid4(),
            title=material.title,
            author_id=material.author_id,
            type_id=material.type_id,
            img=material.img,
            created_by=current_user.id,
            updated_by=current_user.id,
            date_added=datetime.now(timezone.utc),
        )

        db.add(db_material)
        db.commit()
        db.refresh(db_material)

        # Convertir a modelo Pydantic
        created_material = Material.model_validate(db_material, from_attributes=True)
        return created_material

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos (verifique los IDs referenciados).",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
