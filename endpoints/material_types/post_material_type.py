from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.schemas import MaterialTypeCreate, MaterialType, TokenData
from database.connection import MaterialType as MaterialTypeDB, get_db
from common.middleware import require_admin
from uuid import uuid4

router = APIRouter(prefix="/material-types", tags=["material-types"])


@router.post("/", response_model=MaterialType, status_code=status.HTTP_201_CREATED)
async def create_material_type(
    material_type: MaterialTypeCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Crea un nuevo tipo de material en el sistema.
    Solo accesible para administradores.

    Args:
        material_type: MaterialTypeCreate - Datos del nuevo tipo de material
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        MaterialType - El tipo de material creado

    Raises:
        HTTPException(400) - Error de validación o tipo duplicado
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        # Verificar si el tipo de material ya existe
        existing_material_type = db.query(MaterialTypeDB).filter(
            MaterialTypeDB.name == material_type.name
        ).first()
        if existing_material_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un tipo de material con ese nombre"
            )

        db_material_type = MaterialTypeDB(
            id=uuid4(),
            name=material_type.name,
            description=material_type.description,
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(db_material_type)
        db.commit()
        db.refresh(db_material_type)

        return MaterialType.model_validate(db_material_type, from_attributes=True)

    except HTTPException:
        raise
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
