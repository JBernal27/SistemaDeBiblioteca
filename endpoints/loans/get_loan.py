from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import LoanResponse, TokenData
from database.connection import Loan as LoanDB
from typing import List
from uuid import UUID
from common.middleware import require_admin, get_current_user
from common.enums.roles_enum import RolEnum

router = APIRouter(prefix="/loans", tags=["loans"])

@router.get("/", response_model=List[LoanResponse])
def get_loans(
    _: TokenData = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Obtiene la lista de todos los préstamos en el sistema.
    Solo accesible para administradores.

    Args:
        _: TokenData - Token del administrador 
        db: Session - Sesión de la base de datos 

    Returns:
        List[LoanResponse] - Lista de préstamos

    Raises:
        HTTPException(500) - Error interno del servidor
    """
    try:
        loans_db = db.query(LoanDB).all()
        return [
            LoanResponse.model_validate(loan, from_attributes=True) for loan in loans_db
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al listar préstamos: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[LoanResponse])
def get_user_loans(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene la lista de préstamos de un usuario específico.
    Solo accesible para administradores o el propio usuario.

    Args:
        user_id: UUID - Identificador único del usuario
        current_user: TokenData - Token del usuario actual 
        db: Session - Sesión de la base de datos 

    Returns:
        List[LoanResponse] - Lista de préstamos del usuario

    Raises:
        HTTPException(403) - Acceso no autorizado
        HTTPException(404) - No se encontraron préstamos
        HTTPException(500) - Error interno del servidor
    """
    try:
        if current_user.rol != "admin" or current_user.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para acceder a los préstamos de este usuario",
            )

        loans_db = db.query(LoanDB).filter(LoanDB.user_id == user_id).all()
        if not loans_db:
            raise HTTPException(
                status_code=404, detail="No se encontraron préstamos para este usuario"
            )
        return [
            LoanResponse.model_validate(loan, from_attributes=True) for loan in loans_db
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener préstamos del usuario: {str(e)}"
        )


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(
    loan_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene los detalles de un préstamo específico por su ID.
    Solo accesible para administradores o el usuario propietario del préstamo.
    """
    try:
        loan = db.query(LoanDB).filter(LoanDB.id == str(loan_id)).first()

        if not loan:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")

        if current_user.rol != RolEnum.admin and str(current_user.id) != loan.user_id:
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para acceder a este préstamo",
            )

        return LoanResponse.model_validate(loan, from_attributes=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener préstamo: {str(e)}"
        )