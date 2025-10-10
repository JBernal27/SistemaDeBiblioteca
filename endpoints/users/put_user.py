from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.schemas import User, UserUpdate
from database.connection import User as UserDB
from database.connection import get_db
import hashlib
from uuid import UUID
from common.middleware import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.put("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        stmt = select(UserDB).where(UserDB.id == user_id, UserDB.is_deleted == False)
        user_db = db.execute(stmt).scalar_one_or_none()

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        
        if current_user.rol != "admin" and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para actualizar este usuario",
            )

        update_data = user_update.model_dump(exclude_unset=True)
        update_data["updated_by"] = str(current_user.id)

        if "rol" in update_data and current_user.rol != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden cambiar roles de usuario"
            )

        if "email" in update_data and update_data["email"] != user_db.email:
            stmt = select(UserDB).where(
                UserDB.email == update_data["email"], UserDB.id != user_id
            )
            if db.execute(stmt).scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado",
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
            detail="Error de integridad en la base de datos",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
