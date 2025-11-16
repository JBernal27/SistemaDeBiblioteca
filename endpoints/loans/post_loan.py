from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.connection import get_db
from models.schemas import LoanCreate, LoanResponse, TokenData
from database.connection import Loan as LoanDB, Material as MaterialDB, User as UserDB, LoanStatus as LoanStatusDB
from sqlalchemy import select, and_
from uuid import UUID
from common.middleware import require_admin
from datetime import datetime, timezone

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    loan: LoanCreate,
    current_user: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo préstamo (solo si el material no está prestado actualmente).
    """

    try:
        # 🔹 Verificar material
        stmt_material = select(MaterialDB).where(MaterialDB.id == loan.material_id)
        db_material = db.execute(stmt_material).scalar_one_or_none()
        if not db_material:
            raise HTTPException(status_code=404, detail="El material no existe")

        # 🔹 Verificar usuario
        stmt_user = select(UserDB).where(UserDB.id == loan.user_id)
        db_user = db.execute(stmt_user).scalar_one_or_none()
        if not db_user:
            raise HTTPException(status_code=404, detail="El usuario no existe")

        # 🔹 Verificar si el material ya tiene un préstamo activo (sin devolución)
        stmt_active_loan = select(LoanDB).where(
            and_(
                LoanDB.material_id == loan.material_id,
                LoanDB.actual_return_date.is_(None),
            )
        )
        existing_loan = db.execute(stmt_active_loan).scalar_one_or_none()
        if existing_loan:
            raise HTTPException(
                status_code=400,
                detail="El material ya está prestado actualmente",
            )

        # 🔹 Buscar el estado "borrowed" para asignarlo al nuevo préstamo
        borrowed_status = db.execute(
            select(LoanStatusDB).where(LoanStatusDB.name == "borrowed")
        ).scalar_one_or_none()

        if not borrowed_status:
            raise HTTPException(
                status_code=500,
                detail="No se encontró el estado 'borrowed' en la base de datos",
            )

        # 🔹 Crear el préstamo
        db_loan = LoanDB(
            material_id=loan.material_id,
            user_id=loan.user_id,
            expected_return_date=loan.expected_return_date,
            status_id=borrowed_status.id,
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(db_loan)
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
