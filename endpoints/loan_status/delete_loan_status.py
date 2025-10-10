from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from models.schemas import TokenData
from database.connection import LoanStatus as LoanStatusDB, Loan as LoanDB, get_db
from common.middleware import require_admin
from uuid import UUID

router = APIRouter(prefix="/loan-status", tags=["loan-status"])


@router.delete("/{loan_status_id}", status_code=status.HTTP_200_OK)
async def delete_loan_status(
    loan_status_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Elimina un estado de préstamo del sistema.
    Solo accesible para administradores.
    No se puede eliminar un estado de préstamo que tenga préstamos asociados.

    Args:
        loan_status_id: UUID - Identificador único del estado de préstamo
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        dict - Mensaje de confirmación

    Raises:
        HTTPException(400) - Estado de préstamo en uso, no se puede eliminar
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

        # Verificar si el estado de préstamo tiene préstamos asociados
        loans_count = db.query(LoanDB).filter(
            LoanDB.status_id == loan_status_id
        ).count()
        
        if loans_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el estado de préstamo porque tiene {loans_count} préstamo(s) asociado(s)"
            )

        # Eliminar el estado de préstamo
        db.delete(db_loan_status)
        db.commit()

        return {"message": "Estado de préstamo eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
