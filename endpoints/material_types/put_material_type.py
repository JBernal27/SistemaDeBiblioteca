from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.schemas import MaterialTypeUpdate, MaterialType, TokenData
from database.connection import MaterialType as MaterialTypeDB, get_db
from common.middleware import require_admin
from uuid import UUID

router = APIRouter(prefix="/material-types", tags=["material-types"])


@router.put("/{material_type_id}", response_model=MaterialType)
async def update_material_type(
    material_type_id: UUID,
    material_type_update: MaterialTypeUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Actualiza un tipo de material existente en el sistema.
    Solo accesible para administradores.

    Args:
        material_type_id: UUID - Identificador único del tipo de material
        material_type_update: MaterialTypeUpdate - Datos a actualizar
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        MaterialType - El tipo de material actualizado

    Raises:
        HTTPException(400) - Error de validación
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

        # Verificar si el nuevo nombre ya existe (si se está cambiando)
        if material_type_update.name and material_type_update.name != db_material_type.name:
            existing_material_type = db.query(MaterialTypeDB).filter(
                MaterialTypeDB.name == material_type_update.name,
                MaterialTypeDB.id != material_type_id
            ).first()
            if existing_material_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un tipo de material con ese nombre"
                )

        # Actualizar campos
        update_data = material_type_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "updated_by":
                setattr(db_material_type, field, value)

        # Actualizar campos de auditoría
        db_material_type.updated_by = current_user.id

        db.commit()
        db.refresh(db_material_type)

        return MaterialType.model_validate(db_material_type, from_attributes=True)

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
