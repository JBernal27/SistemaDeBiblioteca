from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import Author, TokenData
from database.connection import Author as AuthorDB, get_db
from common.middleware import require_admin

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=List[Author], status_code=status.HTTP_200_OK)
async def get_authors(
    _: TokenData = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Obtiene una lista paginada de todos los autores del sistema.
    Solo accesible para administradores.

    Args:
        _: TokenData - Token del administrador 
        skip: int - Número de registros a saltar (para paginación)
        limit: int - Número máximo de registros a retornar (10-100)
        db: Session - Sesión de la base de datos 

    Returns:
        List[Author] - Lista de autores del sistema

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = (
            select(AuthorDB)
            .order_by(AuthorDB.name)
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        authors_db = result.scalars().all()

        authors = [Author.model_validate(a, from_attributes=True) for a in authors_db]

        return authors

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/{author_id}", response_model=Author)
async def get_author(
    author_id: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Obtiene los detalles de un autor específico.
    Solo accesible para administradores.

    Args:
        author_id: str - Identificador único del autor
        db: Session - Sesión de la base de datos 
        current_user: TokenData - Token del administrador 

    Returns:
        Author - Detalles del autor solicitado

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Autor no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = select(AuthorDB).where(AuthorDB.id == author_id)
        result = db.execute(stmt)
        author_db = result.scalar_one_or_none()

        if not author_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Autor no encontrado"
            )

        return Author.model_validate(author_db, from_attributes=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
