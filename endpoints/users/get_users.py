from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
# Pydantic
from models.schemas import User  
# SQLAlchemy
from database.connection import User as UserDB  
from database.connection import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista paginada de usuarios
    """
    try:
        # Query usando SQLAlchemy CON ORDER BY (requerido por SQL Server)
        stmt = select(UserDB).where(UserDB.is_deleted == True).order_by(UserDB.id).offset(skip).limit(limit)
        result = db.execute(stmt)
        users_db = result.scalars().all()
        
        # Convertir a Pydantic models
        users = []
        for user_db in users_db:
            user = User(
                id=user_db.id,
                username=user_db.username,
                email=user_db.email,
                full_name=user_db.full_name,
                created_at=user_db.created_at,
                is_deleted=user_db.is_deleted
            )
            users.append(user)
        
        return users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un usuario específico por ID
    """
    try:
        # Query usando SQLAlchemy
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_deleted == True)
        result = db.execute(stmt)
        user_db = result.scalar_one_or_none()
        
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Convertir a Pydantic model
        user = User(
            id=user_db.id,
            username=user_db.username,
            email=user_db.email,
            full_name=user_db.full_name,
            created_at=user_db.created_at,
            is_deleted=user_db.is_deleted
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )



