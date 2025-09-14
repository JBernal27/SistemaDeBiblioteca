from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.schemas import User, UserCreate
from database.connection import User as UserDB
from database.connection import get_db
import hashlib
from uuid import uuid4

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario
    """
    try:
        stmt = select(UserDB).where(UserDB.email == user.email)
        if db.execute(stmt).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

        db_user = UserDB(
            email=user.email,
            full_name=user.full_name,
            password=hashed_password,
            rol=user.rol,
            is_deleted=False
        )

        db.add(db_user)
        db.flush()
        db_user.created_by = db_user.id
        db_user.updated_by = db_user.id
        db.commit()
        db.refresh(db_user)

        return db_user
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