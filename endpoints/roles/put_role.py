from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.schemas import RoleUpdate, Role, TokenData
from database.connection import Role as RoleDB, get_db
from common.middleware import require_admin
from uuid import UUID

router = APIRouter(prefix="/roles", tags=["roles"])


@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Actualiza un rol existente en el sistema.
    Solo accesible para administradores.

    Args:
        role_id: UUID - Identificador único del rol
        role_update: RoleUpdate - Datos a actualizar
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        Role - El rol actualizado

    Raises:
        HTTPException(400) - Error de validación
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Rol no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        # Buscar el rol existente
        db_role = db.query(RoleDB).filter(RoleDB.id == role_id).first()
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol no encontrado"
            )

        # Verificar si el nuevo nombre ya existe (si se está cambiando)
        if role_update.name and role_update.name != db_role.name:
            existing_role = db.query(RoleDB).filter(
                RoleDB.name == role_update.name,
                RoleDB.id != role_id
            ).first()
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un rol con ese nombre"
                )

        # Actualizar campos
        update_data = role_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "updated_by":
                setattr(db_role, field, value)

        # Actualizar campos de auditoría
        db_role.updated_by = current_user.id

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
