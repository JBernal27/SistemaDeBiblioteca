from fastapi import APIRouter, HTTPException, status, Depends, Query
from models.schemas import Material
from sqlalchemy.orm import Session
from database.connection import (
    Material as MaterialDB,
    Author as AuthorDB,
    Loan as LoanDB,
    LoanStatus as LoanStatusDB,
)
from database.connection import get_db
from sqlalchemy import select, func, or_, not_, exists, and_
from typing import List, Optional
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
        stmt = select(MaterialDB).where(
            MaterialDB.id == material_id, MaterialDB.is_deleted == False
        )
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


@router.get("/", response_model=List[Material])
async def get_all_materials(
    db: Session = Depends(get_db),
    type_id: Optional[UUID] = Query(None, description="ID del tipo de material"),
    availability_id: Optional[UUID] = Query(
        None,
        description="ID del estado del préstamo (por ejemplo: disponible / prestado)",
    ),
    query: Optional[str] = Query(
        None, description="Texto parcial para buscar en título o autor"
    ),
):
    """
    Obtiene la lista de materiales con filtros opcionales:
    - type_id: Filtra por tipo de material
    - availability_id: Filtra por disponibilidad según el estado del préstamo
    - query: Búsqueda parcial en título o autor (case-insensitive)
    """
    try:
        stmt = (
            select(MaterialDB)
            .join(AuthorDB, AuthorDB.id == MaterialDB.author_id)
            .where(MaterialDB.is_deleted == False)
        )

        # 🔹 Filtro por tipo de material
        if type_id:
            stmt = stmt.where(MaterialDB.type_id == type_id)

        # 🔹 Filtro por texto parcial (título o autor)
        if query:
            stmt = stmt.where(
                or_(
                    func.lower(MaterialDB.title).like(f"%{query.lower()}%"),
                    func.lower(AuthorDB.name).like(f"%{query.lower()}%"),
                )
            )

        # 🔹 Filtro por disponibilidad
        if availability_id:
            # Subconsulta: préstamos activos (no devueltos)
            active_loans = (
                select(LoanDB.id)
                .join(LoanStatusDB)
                .where(
                    LoanDB.material_id == MaterialDB.id,
                    LoanStatusDB.id == availability_id,
                    LoanDB.actual_return_date.is_(None),
                )
            )

            # Si el estado buscado es “disponible” → materiales que NO tienen préstamo activo
            # Si el estado buscado es “prestado” → materiales que SÍ tienen préstamo activo
            borrowed_status = (
                db.query(LoanStatusDB).filter(LoanStatusDB.name == "Borrowed").first()
            )

            if borrowed_status and availability_id == borrowed_status.id:
                stmt = stmt.where(exists(active_loans))
            else:
                stmt = stmt.where(not_(exists(active_loans)))

        # 🔹 Ejecutar la consulta
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
