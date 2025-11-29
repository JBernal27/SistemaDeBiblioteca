from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import List
from database.connection import get_db
from database.connection import Loan as LoanDB
from models.schemas import LoansByDate, TokenData
from common.middleware import require_admin


router = APIRouter(prefix="/graphics", tags=["graphics"])


@router.get("/loans-by-date", response_model=List[LoansByDate])
def loans_by_date(
    _: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
    days: int = 30,
):
    """
    Devuelve el número de préstamos agrupados por fecha (loan_date) en los últimos `days` días.
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Agrupar por fecha (solo la parte de fecha) y contar préstamos
        results = (
            db.query(
                func.date(LoanDB.loan_date).label("date"),
                func.count(LoanDB.id).label("count"),
            )
            .filter(LoanDB.loan_date >= start_date)
            .group_by(func.date(LoanDB.loan_date))
            .order_by(func.date(LoanDB.loan_date))
            .all()
        )
        
        return [LoansByDate(date=r[0], count=int(r[1])) for r in results]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error obteniendo préstamos agrupados: {e}"
        )
