from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.connection import get_db
from models.schemas import LoanCreate, LoanResponse
from database.connection import Loan as LoanDB, Material as MaterialDB, User as UserDB
from sqlalchemy import select
from uuid import UUID

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo préstamo
    """
    try:
        stmt_material = select(MaterialDB).where(MaterialDB.id == loan.material_id)
        db_material = db.execute(stmt_material).scalar_one_or_none()
        if not db_material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="El material no existe"
            )

        stmt_user = select(UserDB).where(UserDB.id == loan.user_id)
        db_user = db.execute(stmt_user).scalar_one_or_none()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe"
            )

        stmt_loan = select(LoanDB).where(
            LoanDB.material_id == loan.material_id, LoanDB.is_returned == False
        )
        existing_loan = db.execute(stmt_loan).scalar_one_or_none()
        if existing_loan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El material ya está prestado",
            )

        db_loan = LoanDB(
            material_id=loan.material_id,
            user_id=loan.user_id,
            expected_return_date=loan.expected_return_date,
            created_by=loan.user_id,  # ? Temporal hasta implemtentar JWT
            updated_by=loan.user_id,  # ? Temporal hasta implemtentar JWT
        )

        db.add(db_loan)
        db.flush()
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
