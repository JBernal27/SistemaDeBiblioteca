from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.schemas import TokenData
from database.connection import Author as AuthorDB, Material as MaterialDB, get_db
from common.middleware import require_admin
from uuid import UUID

router = APIRouter(prefix="/authors", tags=["authors"])


@router.delete("/{author_id}", status_code=status.HTTP_200_OK)
async def delete_author(
    author_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Elimina un autor del sistema.
    Solo accesible para administradores.
    No se puede eliminar un autor que tenga materiales asociados.

    Args:
        author_id: UUID - Identificador único del autor
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        dict - Mensaje de confirmación

    Raises:
        HTTPException(400) - Autor en uso, no se puede eliminar
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

        # Verificar si el autor tiene materiales asociados
        materials_count = db.query(MaterialDB).filter(
            MaterialDB.author_id == author_id,
            MaterialDB.is_deleted == False
        ).count()
        
        if materials_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el autor porque tiene {materials_count} material(es) asociado(s)"
            )

        # Eliminar el autor
        db.delete(db_author)
        db.commit()

        return {"message": "Autor eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
