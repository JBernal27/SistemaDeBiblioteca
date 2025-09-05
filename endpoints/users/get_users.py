from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import User
from database.connection import User as UserDB
from database.connection import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        stmt = select(UserDB).where(UserDB.is_deleted == False).order_by(UserDB.id).offset(skip).limit(limit)
        result = db.execute(stmt)
        users_db = result.scalars().all()

        users = [
            User(
                id=u.id,
                username=u.username,
                email=u.email,
                full_name=u.full_name,
                rol=u.rol,
                created_at=u.created_at,
                is_deleted=u.is_deleted
            )
            for u in users_db
        ]

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
    try:
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_deleted == False)
        result = db.execute(stmt)
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        return User(
            id=user_db.id,
            username=user_db.username,
            email=user_db.email,
            full_name=user_db.full_name,
            rol=user_db.rol,
            created_at=user_db.created_at,
            is_deleted=user_db.is_deleted
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )