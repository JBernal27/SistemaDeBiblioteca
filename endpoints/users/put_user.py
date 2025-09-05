from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.schemas import User, UserUpdate
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
    try:
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_deleted == False)
        user_db = db.execute(stmt).scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        update_data = user_update.dict(exclude_unset=True)

        if "email" in update_data and update_data["email"] != user_db.email:
            stmt = select(UserDB).where(UserDB.email == update_data["email"], UserDB.id != user_id)
            if db.execute(stmt).scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )

        for key, value in update_data.items():
            if key == "password":
                value = hashlib.sha256(value.encode()).hexdigest()
            setattr(user_db, key, value)

        db.commit()
        db.refresh(user_db)

        return user_db

    except HTTPException:
        db.rollback()
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