from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import UserResponse, User
from database.connection import User as UserDB
from database.connection import get_db
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter(prefix="/users", tags=["users"])


@router.delete("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    try:
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_deleted == False)
        result = db.execute(stmt)
        user_db = result.scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        db.query(UserDB).filter(UserDB.id == user_id).update({
            'is_deleted': True,
            'updated_at': datetime.now(timezone.utc),
            'updated_by': str(user_id)  # UUID a str
        }, synchronize_session='fetch')
        
        db.commit()
        user_db = db.get(UserDB, user_id)  

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
