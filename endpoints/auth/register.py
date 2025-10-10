from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.schemas import RegisterDTO, LoginResponse, LoginDTO
from database.connection import User as UserDB, Role as RoleDB, get_db
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from .login import login

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


@router.post(
    "/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: RegisterDTO, db: Session = Depends(get_db)):
    try:
        stmt = select(UserDB).where(UserDB.email == user.email)
        if db.execute(stmt).scalar_one_or_none():
            return LoginResponse(
                message="El correo ya está registrado", error="400 Bad Request"
            )

        # Buscar el rol de cliente por defecto
        client_role = db.query(RoleDB).filter(RoleDB.name == "cliente").first()
        if not client_role:
            return LoginResponse(
                message="Error: Rol de cliente no encontrado", error="500 Internal Server Error"
            )

        hashed_password = pwd_context.hash(user.password)

        db_user = UserDB(
            email=user.email,
            full_name=user.full_name,
            password=hashed_password,
            role_id=client_role.id,
            is_deleted=False,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        """
        Reutilizar la lógica de login para devolver token/response
        `login` espera un LoginDTO y una sesión (Depends(get_db) proporciona Session)
        """
        return login(
            data=LoginDTO(email=user.email, password=user.password),
            db=db
        )

    except IntegrityError:
        db.rollback()
        return LoginResponse(
            message="Error de integridad en la base de datos", error="400 Bad Request"
        )
    except Exception as e:
        db.rollback()
        return LoginResponse(
            message="Error interno del servidor",
            error=f"500 Internal Server Error: {str(e)}",
        )
