from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.connection import get_db
from models.schemas import LoanCreate, LoanResponse
from database.connection import Loan as LoanDB, Material as MaterialDB, User as UserDB
from sqlalchemy import select

router = APIRouter(prefix="/loans", tags=["loans"])

@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    loan: LoanCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo préstamo
    """
    try:
        # Verificar que el material exista
        stmt_material = select(MaterialDB).where(MaterialDB.id == loan.material_id)
        db_material = db.execute(stmt_material).scalar_one_or_none()
        if not db_material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El material no existe"
            )

        # Verificar que el usuario exista
        stmt_user = select(UserDB).where(UserDB.id == loan.user_id)
        db_user = db.execute(stmt_user).scalar_one_or_none()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El usuario no existe"
            )

        # Verificar que el material no esté ya prestado
        stmt_loan = select(LoanDB).where(
            LoanDB.material_id == loan.material_id,
            LoanDB.is_returned == False
        )
        existing_loan = db.execute(stmt_loan).scalar_one_or_none()
        if existing_loan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El material ya está prestado"
            )

        # Crear préstamo
        db_loan = LoanDB(
            material_id=loan.material_id,
            user_id=loan.user_id,
            expected_return_date=loan.expected_return_date,
        )

        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)

        return db_loan  # FastAPI lo convierte a LoanResponse por orm_mode

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
