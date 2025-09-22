from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from common import MaterialType, RolEnum
from uuid import UUID


# -----------------------------
# Pydantic models para la API
# -----------------------------
# -----------------------------
# User Model and DTOs
# -----------------------------
class UserBase(BaseModel):
    email: EmailStr = Field(
        ..., description="Email del usuario", examples=["admin@ejemplo.com"]
    )
    full_name: Optional[str] = Field(
        None, max_length=100, description="Nombre completo", examples=["Admin"]
    )


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None, max_length=100, description="Nombre completo"
    )
    password: Optional[str] = Field(
        None, min_length=6, max_length=255, description="Contraseña del usuario"
    )
    rol: Optional[RolEnum] = None
    updated_by: Optional[UUID] = None


class User(UserBase):
    id: UUID
    rol: RolEnum
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool = Field(default=False)

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
    type: MaterialType = Field(
        ..., description="Tipo de material (book, newspaper, magazine)"
    )


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    title: Optional[str] = Field(
        None, max_length=200, description="Título del material"
    )
    author: Optional[str] = Field(
        None, max_length=100, description="Autor del material"
    )
    type: Optional[MaterialType] = Field(
        None, description="Tipo de material (book, newspaper, magazine)"
    )
    updated_by: Optional[UUID] = None


class Material(MaterialBase):
    id: UUID
    is_deleted: bool = Field(default=False)
    date_added: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class MaterialResponse(BaseModel):
    """Respuesta estándar de la API para materiales"""

    message: str
    material: Optional[Material] = None
    error: Optional[str] = None


# -----------------------------
# Load Model and DTOs
# -----------------------------


class LoanBase(BaseModel):
    material_id: UUID
    user_id: UUID
    expected_return_date: datetime


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    expected_return_date: Optional[datetime] = None
    actual_return_date: Optional[datetime] = None
    is_returned: Optional[bool] = None
    updated_by: Optional[UUID] = None


class Loan(LoanBase):
    id: UUID
    loan_date: datetime
    actual_return_date: Optional[datetime] = None
    is_returned: bool = Field(default=False)
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        orm_mode = True


class LoanResponse(LoanBase):
    id: UUID
    loan_date: datetime
    actual_return_date: Optional[datetime]
    is_returned: bool
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# Auth DTOs
# -----------------------------


class TokenData(BaseModel):
    id: Optional[UUID] = None
    email: Optional[str] = None
    rol: Optional[RolEnum] = None


class LoginDTO(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str
    token: Optional[str] = None
    error: Optional[str] = None


class RegisterDTO(UserBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=255,
        description="Contraseña del usuario",
        examples=["admin1234"],
    )
    rol: RolEnum = Field(
        default=RolEnum.cliente,
        description="Rol del usuario",
        examples=["admin", "cliente"],
    )

class RegisterResponse(BaseModel):
    message: str
    user: Optional[User] = None
    error: Optional[str] = None
    token: Optional[str] = None
