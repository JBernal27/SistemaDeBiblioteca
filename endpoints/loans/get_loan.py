from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import LoanResponse
from database.connection import Loan as LoanDB
from typing import List
from uuid import UUID

router = APIRouter(prefix="/loans", tags=["loans"])

@router.get("/", response_model=List[LoanResponse])
def get_loans(db: Session = Depends(get_db)):
    try:
        loans_db = db.query(LoanDB).all()
        return [
            LoanResponse(
                id=loan.id,
                material_id=loan.material_id,
                user_id=loan.user_id,
                loan_date=loan.loan_date,
                expected_return_date=loan.expected_return_date,
                actual_return_date=loan.actual_return_date,
                is_returned=loan.is_returned,
                created_by=loan.created_by,
                updated_by=loan.updated_by
            ) for loan in loans_db
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar préstamos: {str(e)}")

@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: UUID, db: Session = Depends(get_db)):
    try:
        loan = db.query(LoanDB).filter(LoanDB.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        return LoanResponse(
            id=loan.id,
            material_id=loan.material_id,
            user_id=loan.user_id,
            loan_date=loan.loan_date,
            expected_return_date=loan.expected_return_date,
            actual_return_date=loan.actual_return_date,
            is_returned=loan.is_returned,
            created_by=loan.created_by,
            updated_by=loan.updated_by
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener préstamo: {str(e)}")


