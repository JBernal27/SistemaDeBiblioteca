from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.schemas import RoleCreate, Role, TokenData
from database.connection import Role as RoleDB, get_db
from common.middleware import require_admin
from uuid import uuid4

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Crea un nuevo rol en el sistema.
    Solo accesible para administradores.

    Args:
        role: RoleCreate - Datos del nuevo rol
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        Role - El rol creado

    Raises:
        HTTPException(400) - Error de validación o rol duplicado
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        # Verificar si el rol ya existe
        existing_role = db.query(RoleDB).filter(RoleDB.name == role.name).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un rol con ese nombre"
            )

        db_role = RoleDB(
            id=uuid4(),
            name=role.name,
            description=role.description,
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(db_role)
        db.commit()
        db.refresh(db_role)

        return Role.model_validate(db_role, from_attributes=True)

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
