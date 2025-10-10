from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.schemas import LoanStatusCreate, LoanStatus, TokenData
from database.connection import LoanStatus as LoanStatusDB, get_db
from common.middleware import require_admin
from uuid import uuid4

router = APIRouter(prefix="/loan-status", tags=["loan-status"])


@router.post("/", response_model=LoanStatus, status_code=status.HTTP_201_CREATED)
async def create_loan_status(
    loan_status: LoanStatusCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Crea un nuevo estado de préstamo en el sistema.
    Solo accesible para administradores.

    Args:
        loan_status: LoanStatusCreate - Datos del nuevo estado de préstamo
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        LoanStatus - El estado de préstamo creado

    Raises:
        HTTPException(400) - Error de validación o estado duplicado
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        # Verificar si el estado de préstamo ya existe
        existing_loan_status = db.query(LoanStatusDB).filter(
            LoanStatusDB.name == loan_status.name
        ).first()
        if existing_loan_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un estado de préstamo con ese nombre"
            )

        db_loan_status = LoanStatusDB(
            id=uuid4(),
            name=loan_status.name,
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(db_loan_status)
        db.commit()
        db.refresh(db_loan_status)

        return LoanStatus.model_validate(db_loan_status, from_attributes=True)

    except HTTPException:
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
