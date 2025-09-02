from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# -----------------------------
# Pydantic models para la API
# -----------------------------
# -----------------------------
# User Model and DTOs
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
    is_deleted: bool = True

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    message: str
    user: Optional[User] = None
    error: Optional[str] = None

# -----------------------------
# Material Model and DTOs
# -----------------------------

class MaterialBase(BaseModel):
    title: str = Field(..., max_length=200, description="Título del material")
    author: str = Field(..., max_length=100, description="Autor del material")
    type: str = Field(..., max_length=50, description="Tipo de material (ej. libro, video, artículo)")

class MaterialCreate(MaterialBase):
    pass
class MaterialUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=50)
class Material(MaterialBase):
    id: int
    date_added: datetime
    is_deleted: bool = Field(False, description="Indica si el material está marcado como eliminado")

    class Config:
        from_attributes = True

class MaterialResponse(BaseModel):
    message: str
    material: Optional[Material] = None
    error: Optional[str] = None

    