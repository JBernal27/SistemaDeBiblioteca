# endpoints/loans/put_loan.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.connection import get_db
from models.schemas import LoanUpdate, LoanResponse
from database.connection import Loan as LoanDB
from datetime import datetime
from sqlalchemy import select

router = APIRouter(prefix="/loans", tags=["loans"])

@router.put("/{loan_id}/return", response_model=LoanResponse)
async def return_loan(
    loan_id: int,
    db: Session = Depends(get_db)
):
    """
    Marca un préstamo como devuelto
    """
    try:
        stmt = select(LoanDB).where(LoanDB.id == loan_id)
        db_loan = db.execute(stmt).scalar_one_or_none()
        if not db_loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Préstamo no encontrado"
            )

        if db_loan.is_returned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El préstamo ya fue devuelto"
            )

        db_loan.is_returned = True
        db_loan.actual_return_date = datetime.utcnow()

        db.commit()
        db.refresh(db_loan)

        return db_loan  # FastAPI lo serializa a LoanResponse

    except HTTPException:
        db.rollback()
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
