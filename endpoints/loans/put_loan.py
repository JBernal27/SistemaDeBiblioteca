from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone

from database.connection import get_db
from database.connection import Loan as LoanDB, LoanStatus as LoanStatusDB
from models.schemas import LoanResponse, TokenData
from common.middleware import require_admin

router = APIRouter(prefix="/loans", tags=["loans"])


@router.put("/{loan_id}/return", response_model=LoanResponse)
async def return_loan(
    loan_id: UUID,
    current_user: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Marca un préstamo como devuelto (actualiza status_id y actual_return_date).
    """
    try:
        stmt = select(LoanDB).where(LoanDB.id == loan_id)
        db_loan = db.execute(stmt).scalar_one_or_none()

        if not db_loan:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")

        if db_loan.actual_return_date is not None:
            raise HTTPException(status_code=400, detail="El préstamo ya fue devuelto")

        # 🔹 Obtener el estado "returned"
        returned_status = db.execute(
            select(LoanStatusDB).where(LoanStatusDB.name.ilike("returned"))
        ).scalar_one_or_none()

        if not returned_status:
            raise HTTPException(
                status_code=500,
                detail="No se encontró el estado 'returned' en la base de datos",
            )

        # 🔹 Actualizar los campos
        now_utc = datetime.now(timezone.utc)
        db_loan.actual_return_date = now_utc
        db_loan.status_id = returned_status.id
        db_loan.updated_by = current_user.id
        db_loan.updated_at = now_utc

        db.commit()
        db.refresh(db_loan)

        return LoanResponse.model_validate(db_loan, from_attributes=True)

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad en la base de datos")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


@router.put("/{loan_id}/overdue", response_model=LoanResponse)
async def mark_loan_as_overdue(
    loan_id: UUID,
    current_user: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Marca un préstamo como vencido (Overdue) si ya pasó su fecha esperada de devolución.
    """
    try:
        stmt = select(LoanDB).where(LoanDB.id == loan_id)
        loan = db.execute(stmt).scalar_one_or_none()

        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")

        if loan.actual_return_date:
            raise HTTPException(status_code=400, detail="This loan has already been returned")

        now_utc = datetime.now(timezone.utc)

        # 👇 Asegura que expected_return_date tenga zona horaria antes de comparar
        expected_return_date = (
            loan.expected_return_date.replace(tzinfo=timezone.utc)
            if loan.expected_return_date.tzinfo is None
            else loan.expected_return_date
        )

        if expected_return_date >= now_utc:
            raise HTTPException(status_code=400, detail="This loan is not overdue yet")

        overdue_status = db.execute(
            select(LoanStatusDB).where(LoanStatusDB.name.ilike("overdue"))
        ).scalar_one_or_none()

        if not overdue_status:
            raise HTTPException(status_code=404, detail="Loan status 'Overdue' not found")

        loan.status_id = overdue_status.id
        loan.updated_by = current_user.id
        loan.updated_at = now_utc

        db.commit()
        db.refresh(loan)

        return LoanResponse.model_validate(loan, from_attributes=True)

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad en la base de datos")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
