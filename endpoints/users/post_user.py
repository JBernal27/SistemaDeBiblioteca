from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
# Pydantic
from models.schemas import User, UserCreate
# SQLAlchemy
from database.connection import User as UserDB
from database.connection import get_db
import hashlib

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
        # Verificar si el username ya existe
        stmt = select(UserDB).where(UserDB.username == user.username)
        result = db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe"
            )
        
        # Verificar si el email ya existe
        stmt = select(UserDB).where(UserDB.email == user.email)
        result = db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Encriptar la contraseña (en producción usar bcrypt)
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        
        # Crear el nuevo usuario
        db_user = UserDB(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Convertir a Pydantic model para la respuesta
        created_user = User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            created_at=db_user.created_at,
            is_active=db_user.is_active
        )
        
        return created_user
        
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