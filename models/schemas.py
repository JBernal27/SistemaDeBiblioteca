from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from common import MaterialType, RolEnum

# -----------------------------
# Pydantic models para la API
# -----------------------------
# -----------------------------
# User Model and DTOs
# -----------------------------
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    full_name: Optional[str] = Field(None, max_length=100, description="Nombre completo")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=255, description="Contraseña del usuario")
    rol: RolEnum = Field(default=RolEnum.cliente, description="Rol del usuario")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6)
    rol: Optional[RolEnum] = None

class User(UserBase):
    id: int
    rol: RolEnum
    created_at: datetime
    is_deleted: bool = Field(default=False)

    class Config:
        orm_mode = True

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
    type: MaterialType = Field(..., description="Tipo de material (book, newspaper, magazine)")


class MaterialCreate(MaterialBase):
    """DTO para crear material"""
    pass


class MaterialUpdate(BaseModel):
    """DTO para actualizar material (parcial)"""
    title: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=100)
    type: Optional[MaterialType] = Field(None, description="Nuevo tipo de material")


class Material(MaterialBase):
    """DTO de respuesta del material"""
    id: int
    date_added: datetime
    is_deleted: bool = Field(False, description="Indica si el material está marcado como eliminado")

    class Config:
        from_attributes = True  # ✅ permite mapear desde ORM


class MaterialResponse(BaseModel):
    """Respuesta estándar de la API para materiales"""
    message: str
    material: Optional[Material] = None
    error: Optional[str] = None

    
# -----------------------------
# Load Model and DTOs
# -----------------------------

class LoanBase(BaseModel):
    material_id: int
    user_id: int
    expected_return_date: datetime

class LoanCreate(LoanBase):
    pass

class LoanUpdate(BaseModel):
    expected_return_date: Optional[datetime] = None
    actual_return_date: Optional[datetime] = None
    is_returned: Optional[bool] = None
class LoanResponse(LoanBase):
    id: int
    loan_date: datetime
    actual_return_date: Optional[datetime]
    is_returned: bool

    class Config:
        orm_mode = True