from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
# Pydantic
from models.schemas import User, UserUpdate  
# SQLAlchemy
from database.connection import User as UserDB  
from database.connection import get_db
import hashlib

router = APIRouter(prefix="/users", tags=["users"])

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un usuario existente
    """
    try:
        # Verificar si el usuario existe
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_deleted == True)
        result = db.execute(stmt)
        user_db = result.scalar_one_or_none()
        
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar si el nuevo username ya existe (si se está actualizando)
        if user_update.username and user_update.username != user_db.username:
            stmt = select(UserDB).where(UserDB.username == user_update.username, UserDB.id != user_id)
            result = db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya existe"
                )
        
        # Verificar si el nuevo email ya existe (si se está actualizando)
        if user_update.email and user_update.email != user_db.email:
            stmt = select(UserDB).where(UserDB.email == user_update.email, UserDB.id != user_id)
            result = db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )
        
        # Actualizar los campos proporcionados
        if user_update.username is not None:
            user_db.username = user_update.username
        
        if user_update.email is not None:
            user_db.email = user_update.email
        
        if user_update.full_name is not None:
            user_db.full_name = user_update.full_name
        
        if user_update.password is not None:
            hashed_password = hashlib.sha256(user_update.password.encode()).hexdigest()
            user_db.password = hashed_password
        
        db.commit()
        db.refresh(user_db)
        
        # Convertir a Pydantic model para la respuesta
        updated_user = User(
            id=user_db.id,
            username=user_db.username,
            email=user_db.email,
            full_name=user_db.full_name,
            created_at=user_db.created_at,
            is_deleted=user_db.is_deleted
        )
        
        return updated_user
        
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
