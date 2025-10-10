from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import TokenData
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from uuid import UUID
from datetime import datetime, timezone
from common.middleware import require_admin
from sqlalchemy import select

router = APIRouter(prefix="/materials", tags=["materials"])


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Marca un material como eliminado (soft delete).
    Solo accesible para administradores.

    Args:
        material_id: UUID - Identificador único del material a eliminar
        db: Session - Sesión de la base de datos 
        current_user: TokenData - Token del administrador 

    Returns:
        None - Respuesta 204 No Content si la operación es exitosa

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

        db.query(MaterialDB).filter(MaterialDB.id == material_id).update(
            {
                "is_deleted": True,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": current_user.id,
            },
            synchronize_session="fetch",
        )

        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar el material: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
