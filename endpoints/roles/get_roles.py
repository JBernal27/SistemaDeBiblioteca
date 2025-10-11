from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import Role, TokenData
from database.connection import Role as RoleDB, get_db
from common.middleware import require_admin

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[Role], status_code=status.HTTP_200_OK)
async def get_roles(
    _: TokenData = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Obtiene una lista paginada de todos los roles del sistema.
    Solo accesible para administradores.

    Args:
        _: TokenData - Token del administrador 
        skip: int - Número de registros a saltar (para paginación)
        limit: int - Número máximo de registros a retornar (10-100)
        db: Session - Sesión de la base de datos 

    Returns:
        List[Role] - Lista de roles del sistema

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = (
            select(RoleDB)
            .order_by(RoleDB.name)
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        roles_db = result.scalars().all()

        roles = [Role.model_validate(r, from_attributes=True) for r in roles_db]

        return roles

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/{role_id}", response_model=Role)
async def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Obtiene los detalles de un rol específico.
    Solo accesible para administradores.

    Args:
        role_id: str - Identificador único del rol
        db: Session - Sesión de la base de datos 
        current_user: TokenData - Token del administrador 

    Returns:
        Role - Detalles del rol solicitado

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Rol no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = select(RoleDB).where(RoleDB.id == role_id)
        result = db.execute(stmt)
        role_db = result.scalar_one_or_none()

        if not role_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado"
            )

        return Role.model_validate(role_db, from_attributes=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
