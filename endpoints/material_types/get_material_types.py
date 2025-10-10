from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import MaterialType, TokenData
from database.connection import MaterialType as MaterialTypeDB, get_db
from common.middleware import require_admin

router = APIRouter(prefix="/material-types", tags=["material-types"])


@router.get("/", response_model=List[MaterialType], status_code=status.HTTP_200_OK)
async def get_material_types(
    _: TokenData = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Obtiene una lista paginada de todos los tipos de material del sistema.
    Solo accesible para administradores.

    Args:
        _: TokenData - Token del administrador 
        skip: int - Número de registros a saltar (para paginación)
        limit: int - Número máximo de registros a retornar (10-100)
        db: Session - Sesión de la base de datos 

    Returns:
        List[MaterialType] - Lista de tipos de material del sistema

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = (
            select(MaterialTypeDB)
            .order_by(MaterialTypeDB.name)
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        material_types_db = result.scalars().all()

        material_types = [MaterialType.model_validate(mt, from_attributes=True) for mt in material_types_db]

        return material_types

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/{material_type_id}", response_model=MaterialType)
async def get_material_type(
    material_type_id: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Obtiene los detalles de un tipo de material específico.
    Solo accesible para administradores.

    Args:
        material_type_id: str - Identificador único del tipo de material
        db: Session - Sesión de la base de datos 
        current_user: TokenData - Token del administrador 

    Returns:
        MaterialType - Detalles del tipo de material solicitado

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Tipo de material no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = select(MaterialTypeDB).where(MaterialTypeDB.id == material_type_id)
        result = db.execute(stmt)
        material_type_db = result.scalar_one_or_none()

        if not material_type_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de material no encontrado"
            )

        return MaterialType.model_validate(material_type_db, from_attributes=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
