from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import User
from database.connection import User as UserDB
from database.connection import get_db
from uuid import UUID

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User], status_code=status.HTTP_200_OK)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
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
async def get_user(user_id: UUID, db: Session = Depends(get_db)):
    try:
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
