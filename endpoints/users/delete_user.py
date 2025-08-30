from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import UserResponse, UserDB
from database.connection import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario (soft delete - marca como inactivo)
    """
    try:
        # Verificar si el usuario existe
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_active == True)
        result = db.execute(stmt)
        user_db = result.scalar_one_or_none()
        
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Soft delete - marcar como inactivo
        user_db.is_active = False
        db.commit()
        
        return UserResponse(
            message=f"Usuario '{user_db.username}' eliminado exitosamente"
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.delete("/{user_id}/hard", response_model=UserResponse)
async def hard_delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina permanentemente un usuario de la base de datos
    """
    try:
        # Verificar si el usuario existe
        stmt = select(UserDB).where(UserDB.id == user_id)
        result = db.execute(stmt)
        user_db = result.scalar_one_or_none()
        
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Hard delete - eliminar completamente
        db.delete(user_db)
        db.commit()
        
        return UserResponse(
            message=f"Usuario '{user_db.username}' eliminado permanentemente"
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
