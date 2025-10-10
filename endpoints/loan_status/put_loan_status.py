from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.schemas import LoanStatusUpdate, LoanStatus, TokenData
from database.connection import LoanStatus as LoanStatusDB, get_db
from common.middleware import require_admin
from uuid import UUID

router = APIRouter(prefix="/loan-status", tags=["loan-status"])


@router.put("/{loan_status_id}", response_model=LoanStatus)
async def update_loan_status(
    loan_status_id: UUID,
    loan_status_update: LoanStatusUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Actualiza un estado de préstamo existente en el sistema.
    Solo accesible para administradores.

    Args:
        loan_status_id: UUID - Identificador único del estado de préstamo
        loan_status_update: LoanStatusUpdate - Datos a actualizar
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        LoanStatus - El estado de préstamo actualizado

    Raises:
        HTTPException(400) - Error de validación
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Estado de préstamo no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        # Buscar el estado de préstamo existente
        db_loan_status = db.query(LoanStatusDB).filter(
            LoanStatusDB.id == loan_status_id
        ).first()
        if not db_loan_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estado de préstamo no encontrado"
            )

        # Verificar si el nuevo nombre ya existe (si se está cambiando)
        if loan_status_update.name and loan_status_update.name != db_loan_status.name:
            existing_loan_status = db.query(LoanStatusDB).filter(
                LoanStatusDB.name == loan_status_update.name,
                LoanStatusDB.id != loan_status_id
            ).first()
            if existing_loan_status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un estado de préstamo con ese nombre"
                )

        # Actualizar campos
        update_data = loan_status_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "updated_by":
                setattr(db_loan_status, field, value)

        # Actualizar campos de auditoría
        db_loan_status.updated_by = current_user.id

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
