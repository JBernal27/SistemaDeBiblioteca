from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import UserResponse, TokenData
from database.connection import User as UserDB
from database.connection import get_db
from uuid import UUID
from datetime import datetime, timezone
from common.middleware import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Marca un usuario como eliminado (soft delete).
    Solo accesible para administradores o el propio usuario.

    Args:
        user_id: UUID - Identificador único del usuario a eliminar
        db: Session - Sesión de la base de datos 
        current_user: TokenData - Token del usuario actual 

    Returns:
        UserResponse - Respuesta con los detalles del usuario eliminado

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Usuario no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_deleted == False)
        result = db.execute(stmt)
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        if current_user.rol != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar este usuario",
            )

        db.query(UserDB).filter(UserDB.id == user_id).update(
            {
                "is_deleted": True,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": current_user.id,
            },
            synchronize_session="fetch",
        )

        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
