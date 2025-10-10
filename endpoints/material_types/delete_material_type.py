from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.schemas import TokenData
from database.connection import MaterialType as MaterialTypeDB, Material as MaterialDB, get_db
from common.middleware import require_admin
from uuid import UUID

router = APIRouter(prefix="/material-types", tags=["material-types"])


@router.delete("/{material_type_id}", status_code=status.HTTP_200_OK)
async def delete_material_type(
    material_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Elimina un tipo de material del sistema.
    Solo accesible para administradores.
    No se puede eliminar un tipo de material que tenga materiales asociados.

    Args:
        material_type_id: UUID - Identificador único del tipo de material
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        dict - Mensaje de confirmación

    Raises:
        HTTPException(400) - Tipo de material en uso, no se puede eliminar
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Tipo de material no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        # Buscar el tipo de material existente
        db_material_type = db.query(MaterialTypeDB).filter(
            MaterialTypeDB.id == material_type_id
        ).first()
        if not db_material_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de material no encontrado"
            )

        # Verificar si el tipo de material tiene materiales asociados
        materials_count = db.query(MaterialDB).filter(
            MaterialDB.type_id == material_type_id,
            MaterialDB.is_deleted == False
        ).count()
        
        if materials_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el tipo de material porque tiene {materials_count} material(es) asociado(s)"
            )

        # Eliminar el tipo de material
        db.delete(db_material_type)
        db.commit()

        return {"message": "Tipo de material eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
