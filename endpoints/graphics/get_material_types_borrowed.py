from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import List
from database.connection import get_db
from database.connection import (
    Loan as LoanDB,
    Material as MaterialDB,
    MaterialType as MaterialTypeDB,
)
from models.schemas import MaterialTypeBorrowed, TokenData
from common.middleware import require_admin


router = APIRouter(prefix="/graphics", tags=["graphics"])

@router.get("/material-types-borrowed", response_model=List[MaterialTypeBorrowed])
def material_types_borrowed(
    _: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
    days: int = 30,
):
    """
    Devuelve el número de préstamos por tipo de material en los últimos `days` días.
    Une Loan -> Material -> MaterialType y cuenta préstamos por tipo.
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Realizar join de Loan -> Material -> MaterialType y agrupar por material_type.name
        results = (
            db.query(
                MaterialTypeDB.name.label("material_type"),
                func.count(LoanDB.id).label("count"),
            )
            .join(MaterialDB, MaterialDB.type_id == MaterialTypeDB.id)
            .join(LoanDB, LoanDB.material_id == MaterialDB.id)
            .filter(LoanDB.loan_date >= start_date)
            .group_by(MaterialTypeDB.name)
            .order_by(func.count(LoanDB.id).desc())
            .all()
        )

        return [
            MaterialTypeBorrowed(material_type=r[0], count=int(r[1])) for r in results
            for r in results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo tipos de material prestados: {e}"
        )