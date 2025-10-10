from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date
from uuid import UUID


# -----------------------------
# Pydantic models para la API
# -----------------------------

# -----------------------------
# Role Model and DTOs
# -----------------------------
class RoleBase(BaseModel):
    name: str = Field(..., max_length=50, description="Nombre del rol")
    description: Optional[str] = Field(None, max_length=200, description="Descripción del rol")

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description="Nombre del rol")
    description: Optional[str] = Field(None, max_length=200, description="Descripción del rol")
    updated_by: Optional[UUID] = None

class Role(RoleBase):
    id: UUID
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

# -----------------------------
# Author Model and DTOs
# -----------------------------
class AuthorBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nombre del autor")
    nationality: Optional[str] = Field(None, max_length=50, description="Nacionalidad del autor")
    birth_date: Optional[date] = Field(None, description="Fecha de nacimiento")
    death_date: Optional[date] = Field(None, description="Fecha de fallecimiento")
    biography: Optional[str] = Field(None, description="Biografía del autor")

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Nombre del autor")
    nationality: Optional[str] = Field(None, max_length=50, description="Nacionalidad del autor")
    birth_date: Optional[date] = Field(None, description="Fecha de nacimiento")
    death_date: Optional[date] = Field(None, description="Fecha de fallecimiento")
    biography: Optional[str] = Field(None, description="Biografía del autor")
    updated_by: Optional[UUID] = None

class Author(AuthorBase):
    id: UUID
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

# -----------------------------
# MaterialType Model and DTOs
# -----------------------------
class MaterialTypeBase(BaseModel):
    name: str = Field(..., max_length=50, description="Nombre del tipo de material")
    description: Optional[str] = Field(None, max_length=200, description="Descripción del tipo")

class MaterialTypeCreate(MaterialTypeBase):
    pass

class MaterialTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description="Nombre del tipo de material")
    description: Optional[str] = Field(None, max_length=200, description="Descripción del tipo")
    updated_by: Optional[UUID] = None

class MaterialType(MaterialTypeBase):
    id: UUID
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

# -----------------------------
# LoanStatus Model and DTOs
# -----------------------------
class LoanStatusBase(BaseModel):
    name: str = Field(..., max_length=50, description="Nombre del estado")

class LoanStatusCreate(LoanStatusBase):
    pass

class LoanStatusUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description="Nombre del estado")
    updated_by: Optional[UUID] = None

class LoanStatus(LoanStatusBase):
    id: UUID
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

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
    role_id: Optional[UUID] = Field(None, description="ID del rol del usuario")
    updated_by: Optional[UUID] = None

class User(UserBase):
    id: UUID
    role_id: UUID
    created_at: datetime
    created_by: Optional[UUID] = None
    updated_at: datetime
    updated_by: Optional[UUID] = None
    is_deleted: bool = Field(default=False)
    
    # Relaciones
    role: Optional[Role] = None

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
    author_id: UUID = Field(..., description="ID del autor del material")
    type_id: UUID = Field(..., description="ID del tipo de material")

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    title: Optional[str] = Field(
        None, max_length=200, description="Título del material"
    )
    author_id: Optional[UUID] = Field(None, description="ID del autor del material")
    type_id: Optional[UUID] = Field(None, description="ID del tipo de material")
    updated_by: Optional[UUID] = None

class Material(MaterialBase):
    id: UUID
    is_deleted: bool = Field(default=False)
    date_added: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime
    
    # Relaciones
    author: Optional[Author] = None
    material_type: Optional[MaterialType] = None

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
    status_id: UUID = Field(..., description="ID del estado del préstamo")

class LoanCreate(LoanBase):
    pass

class LoanUpdate(BaseModel):
    expected_return_date: Optional[datetime] = None
    actual_return_date: Optional[datetime] = None
    status_id: Optional[UUID] = Field(None, description="ID del estado del préstamo")
    updated_by: Optional[UUID] = None

class Loan(LoanBase):
    id: UUID
    loan_date: datetime
    actual_return_date: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime
    
    # Relaciones
    material: Optional[Material] = None
    user: Optional[User] = None
    status: Optional[LoanStatus] = None

    class Config:
        from_attributes = True

class LoanResponse(LoanBase):
    id: UUID
    loan_date: datetime
    actual_return_date: Optional[datetime]
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    updated_at: datetime
    
    # Relaciones
    material: Optional[Material] = None
    user: Optional[User] = None
    status: Optional[LoanStatus] = None

    class Config:
        from_attributes = True


# -----------------------------
# Auth DTOs
# -----------------------------


class TokenData(BaseModel):
    id: Optional[UUID] = None
    email: Optional[str] = None
    role_name: Optional[str] = None


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

class RegisterResponse(BaseModel):
    message: str
    user: Optional[User] = None
    error: Optional[str] = None
    token: Optional[str] = None
