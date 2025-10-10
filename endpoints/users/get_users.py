from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import User, TokenData
from database.connection import User as UserDB
from database.connection import get_db
from uuid import UUID
from common.enums.roles_enum import RolEnum
from common.middleware import require_admin, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User], status_code=status.HTTP_200_OK)
async def get_users(
    _: TokenData = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Obtiene una lista paginada de todos los usuarios del sistema.
    Solo accesible para administradores.

    Args:
        _: TokenData - Token del administrador 
        skip: int - Número de registros a saltar (para paginación)
        limit: int - Número máximo de registros a retornar (10-100)
        db: Session - Sesión de la base de datos 

    Returns:
        List[User] - Lista de usuarios del sistema

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = (
            select(UserDB)
            .where(UserDB.is_deleted == False)
            .order_by(UserDB.id)
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        users_db = result.scalars().all()

        users = [User.model_validate(u, from_attributes=True) for u in users_db]

        return users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Obtiene los detalles de un usuario específico.
    Accesible para administradores o el propio usuario.

    Args:
        user_id: UUID - Identificador único del usuario
        db: Session - Sesión de la base de datos 
        current_user: TokenData - Token del usuario actual 

    Returns:
        User - Detalles del usuario solicitado

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Usuario no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        if current_user.rol != RolEnum.admin and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este recurso",
            )

        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_deleted == False)
        result = db.execute(stmt)
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        return User.model_validate(user_db, from_attributes=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
