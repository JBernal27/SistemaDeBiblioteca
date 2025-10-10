from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.schemas import AuthorUpdate, Author, TokenData
from database.connection import Author as AuthorDB, get_db
from common.middleware import require_admin
from uuid import UUID

router = APIRouter(prefix="/authors", tags=["authors"])


@router.put("/{author_id}", response_model=Author)
async def update_author(
    author_id: UUID,
    author_update: AuthorUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Actualiza un autor existente en el sistema.
    Solo accesible para administradores.

    Args:
        author_id: UUID - Identificador único del autor
        author_update: AuthorUpdate - Datos a actualizar
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        Author - El autor actualizado

    Raises:
        HTTPException(400) - Error de validación
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Autor no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        # Buscar el autor existente
        db_author = db.query(AuthorDB).filter(AuthorDB.id == author_id).first()
        if not db_author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Autor no encontrado"
            )

        # Verificar si el nuevo nombre ya existe (si se está cambiando)
        if author_update.name and author_update.name != db_author.name:
            existing_author = db.query(AuthorDB).filter(
                AuthorDB.name == author_update.name,
                AuthorDB.id != author_id
            ).first()
            if existing_author:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un autor con ese nombre"
                )

        # Actualizar campos
        update_data = author_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "updated_by":
                setattr(db_author, field, value)

        # Actualizar campos de auditoría
        db_author.updated_by = current_user.id

        db.commit()
        db.refresh(db_author)

        return Author.model_validate(db_author, from_attributes=True)

    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
