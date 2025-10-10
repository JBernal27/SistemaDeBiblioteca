from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import Material, MaterialUpdate, TokenData
from common import MaterialType
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, select
from uuid import UUID
from datetime import datetime, timezone
from common.middleware import require_admin

router = APIRouter(prefix="/materials", tags=["materials"])


@router.put("/{material_id}", response_model=Material)
async def update_material(
    material_id: UUID,
    updated_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    try:
        stmt = select(MaterialDB).where(MaterialDB.id == material_id)
        material = db.execute(stmt).scalar_one_or_none()
        if material is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
            )
        if bool(material.is_deleted):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
            )

        update_data_dict = updated_data.model_dump(exclude_unset=True)

        if "type" in update_data_dict and isinstance(update_data_dict["type"], MaterialType):
            update_data_dict["type"] = update_data_dict["type"].value

        update_data_dict.update(
            {
                "updated_by": str(current_user.id),
                "updated_at": datetime.now(timezone.utc),
            }
        )

        stmt = (
            update(MaterialDB)
            .where(MaterialDB.id == material_id)
            .values(**update_data_dict)
            .returning(MaterialDB)
        )
        result = db.execute(stmt)
        db.commit()

        updated_material = result.scalar_one_or_none()
        if not updated_material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
            )

        return Material.model_validate(updated_material, from_attributes=True)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
