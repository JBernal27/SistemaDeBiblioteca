from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.schemas import Material, MaterialCreate
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from sqlalchemy import select, func
from typing import List
from uuid import UUID


router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/{material_id}", response_model=Material)
async def get_material(material_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un material específico por su ID.
    Accesible para todos los usuarios.

    Args:
        material_id: UUID - Identificador único del material
        db: Session - Sesión de la base de datos 

    Returns:
        Material - Detalles del material solicitado

    Raises:
        HTTPException(404) - Material no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = select(MaterialDB).where(MaterialDB.id == material_id, MaterialDB.is_deleted == False)
        result = db.execute(stmt)
        material = result.scalar_one_or_none()

        if not material:
            raise HTTPException(status_code=404, detail="Material no encontrado")

        return Material.model_validate(material, from_attributes=True)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/", response_model=list[Material])
async def get_all_materials(db: Session = Depends(get_db)):
    """
    Obtiene la lista de todos los materiales disponibles en el sistema.
    Accesible para todos los usuarios.

    Args:
        db: Session - Sesión de la base de datos 

    Returns:
        list[Material] - Lista de materiales disponibles

    Raises:
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = select(MaterialDB).where(MaterialDB.is_deleted == False)
        result = db.execute(stmt).scalars().all()
        return [Material.model_validate(m, from_attributes=True) for m in result]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/by-author/{author}", response_model=List[Material])
def search_by_author(author: str, db: Session = Depends(get_db)):
    """
    Busca materiales por el nombre del autor.
    Realiza una búsqueda parcial ignorando mayúsculas/minúsculas.
    Accesible para todos los usuarios.

    Args:
        author: str - Nombre o parte del nombre del autor a buscar
        db: Session - Sesión de la base de datos 

    Returns:
        List[Material] - Lista de materiales que coinciden con el autor buscado

    Raises:
        HTTPException(404) - No se encontraron materiales para ese autor
        HTTPException(500) - Error interno del servidor
    """
    stmt = select(MaterialDB).where(MaterialDB.author.ilike(f"%{author}%"))
    result = db.execute(stmt).scalars().all()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron materiales con ese autor",
        )

    return [Material.model_validate(m, from_attributes=True) for m in result]
