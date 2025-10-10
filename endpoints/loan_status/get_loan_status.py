from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.schemas import LoanStatus, TokenData
from database.connection import LoanStatus as LoanStatusDB, get_db
from common.middleware import require_admin

router = APIRouter(prefix="/loan-status", tags=["loan-status"])


@router.get("/", response_model=List[LoanStatus], status_code=status.HTTP_200_OK)
async def get_loan_status(
    _: TokenData = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Obtiene una lista paginada de todos los estados de préstamo del sistema.
    Solo accesible para administradores.

    Args:
        _: TokenData - Token del administrador 
        skip: int - Número de registros a saltar (para paginación)
        limit: int - Número máximo de registros a retornar (10-100)
        db: Session - Sesión de la base de datos 

    Returns:
        List[LoanStatus] - Lista de estados de préstamo del sistema

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = (
            select(LoanStatusDB)
            .order_by(LoanStatusDB.name)
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(stmt)
        loan_status_db = result.scalars().all()

        loan_status = [LoanStatus.model_validate(ls, from_attributes=True) for ls in loan_status_db]

        return loan_status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )


@router.get("/{loan_status_id}", response_model=LoanStatus)
async def get_loan_status_by_id(
    loan_status_id: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Obtiene los detalles de un estado de préstamo específico.
    Solo accesible para administradores.

    Args:
        loan_status_id: str - Identificador único del estado de préstamo
        db: Session - Sesión de la base de datos 
        current_user: TokenData - Token del administrador 

    Returns:
        LoanStatus - Detalles del estado de préstamo solicitado

    Raises:
        HTTPException(403) - Usuario no autorizado
        HTTPException(404) - Estado de préstamo no encontrado
        HTTPException(500) - Error interno del servidor
    """
    try:
        stmt = select(LoanStatusDB).where(LoanStatusDB.id == loan_status_id)
        result = db.execute(stmt)
        loan_status_db = result.scalar_one_or_none()

        if not loan_status_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Estado de préstamo no encontrado"
            )

        return LoanStatus.model_validate(loan_status_db, from_attributes=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}",
        )
