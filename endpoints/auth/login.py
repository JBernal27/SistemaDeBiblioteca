from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import LoginDTO, LoginResponse
from database.connection import get_db, User as UserDB
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from typing import cast
from jose import jwt
import os
from dotenv import load_dotenv

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/auth", tags=["auth"])

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(data: LoginDTO, db: Session = Depends(get_db)):
    user = (
        db.query(UserDB)
        .filter(UserDB.email == data.email, UserDB.is_deleted == False)
        .first()
    )
    # user.password may be seen by static checkers as a Column; cast to str for verify
    if not user or not pwd_context.verify(data.password, cast(str, user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = {
        "id": str(user.id),
        "email": user.email,
        "rol": user.rol,
    }

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user.email, "exp": expire, **payload}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return LoginResponse(message="Login correcto", token=token, error=None)
