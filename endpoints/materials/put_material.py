from fastapi import APIRouter, HTTPException, status, Depends
from models.schemas import Material, MaterialUpdate
from common import MaterialType
from sqlalchemy.orm import Session
from database.connection import Material as MaterialDB
from database.connection import get_db
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter(prefix="/materials", tags=["materials"])


@router.put("/{material_id}", response_model=Material)
async def update_material(
    material_id: UUID, updated_data: MaterialUpdate, db: Session = Depends(get_db)
):
    try:
        material = db.get(MaterialDB, material_id)
        if material is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
            )
        if bool(db.query(MaterialDB.is_deleted).filter(MaterialDB.id == material_id).scalar()):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Material no encontrado"
            )

        update_data_dict = updated_data.model_dump(exclude_unset=True)
        
        if "type" in update_data_dict and isinstance(update_data_dict["type"], MaterialType):
            update_data_dict["type"] = update_data_dict["type"].value
        
        update_data_dict.update({
            'updated_by': str(material.created_by),
            'updated_at': datetime.now(timezone.utc)
        })

        for key, value in update_data_dict.items():
            setattr(material, key, value)

        db.add(material)
        
        db.commit()
        
        material = db.get(MaterialDB, material_id)
        
        return Material.model_validate(material, from_attributes=True)

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
