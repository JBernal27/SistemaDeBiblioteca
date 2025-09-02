from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# -----------------------------
# Pydantic models para la API
# -----------------------------

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: str = Field(..., description="Email del usuario")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None)
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6)


class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True   # ⚡Ojo: en tu modelo SQLAlchemy usas "is_deleted", aquí "is_active"

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    message: str
    user: Optional[User] = None
    error: Optional[str] = None
