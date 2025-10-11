from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.schemas import TokenData
from database.connection import Role as RoleDB, User as UserDB, get_db
from common.middleware import require_admin
from uuid import UUID

router = APIRouter(prefix="/roles", tags=["roles"])


@router.delete("/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Elimina un rol del sistema.
    Solo accesible para administradores.
    No se puede eliminar un rol que esté siendo usado por usuarios.

    Args:
        role_id: UUID - Identificador único del rol
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        dict - Mensaje de confirmación

    Raises:
        HTTPException(400) - Rol en uso, no se puede eliminar
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

        # Verificar si el rol está siendo usado por usuarios
        users_with_role = db.query(UserDB).filter(UserDB.role_id == role_id).count()
        if users_with_role > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el rol porque está siendo usado por {users_with_role} usuario(s)"
            )

        # Eliminar el rol
        db.delete(db_role)
        db.commit()

        return {"message": "Rol eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
