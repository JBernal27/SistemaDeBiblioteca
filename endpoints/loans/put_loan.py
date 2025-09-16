# endpoints/loans/put_loan.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.connection import get_db
from models.schemas import LoanUpdate, LoanResponse
from database.connection import Loan as LoanDB
from datetime import datetime, timezone
from sqlalchemy import select
from uuid import UUID

router = APIRouter(prefix="/loans", tags=["loans"])


@router.put("/{loan_id}/return", response_model=LoanResponse)
async def return_loan(loan_id: UUID, db: Session = Depends(get_db)):
    """
    Marca un préstamo como devuelto
    """
    try:
        stmt = select(LoanDB).where(LoanDB.id == loan_id)
        db_loan = db.execute(stmt).scalar_one_or_none()
        if not db_loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado"
            )

        if bool(db_loan.is_returned):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El préstamo ya fue devuelto",
            )

        db_loan = LoanDB(
            updated_by=db_loan.updated_by,
            is_returned=True,
            actual_return_date=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.commit()
        db.refresh(db_loan)

        return LoanResponse.model_validate(db_loan, from_attributes=True)

    except HTTPException:
        db.rollback()
        raise
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
