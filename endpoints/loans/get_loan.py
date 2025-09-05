from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import LoanResponse
from database.connection import Loan as LoanDB
from typing import List

router = APIRouter(prefix="/loans", tags=["loans"])

@router.get("/", response_model=List[LoanResponse])
def get_loans(db: Session = Depends(get_db)):
    try:
        return db.query(LoanDB).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar préstamos: {str(e)}")

@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        loan = db.query(LoanDB).filter(LoanDB.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        return loan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener préstamo: {str(e)}")


