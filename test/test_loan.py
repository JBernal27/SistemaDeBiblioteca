import pytest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4
from fastapi import status, HTTPException
from datetime import datetime, timezone
from models.schemas import LoanCreate, LoanUpdate, LoanResponse, TokenData
from endpoints.loans.get_loan import get_loans, get_user_loans, get_loan
from endpoints.loans.post_loan import create_loan
from endpoints.loans.put_loan import return_loan


# Tests para funciones SÍNCRONAS (get_loans, get_user_loans, get_loan)

@patch('endpoints.loans.get_loan.LoanResponse')
def test_get_loans_success(
    MockLoanResponse,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de una lista de todos los préstamos."""
    
    mock_loan_db_1 = Mock(name="LoanDB1")
    mock_loan_db_2 = Mock(name="LoanDB2")
    loans_db = [mock_loan_db_1, mock_loan_db_2]
    
    mock_loan_response_1 = Mock(name="LoanResponse1")
    mock_loan_response_2 = Mock(name="LoanResponse2")
    
    MockLoanResponse.model_validate.side_effect = [
        mock_loan_response_1,
        mock_loan_response_2
    ]
    
    mock_db_session.query.return_value.all.return_value = loans_db

    result = get_loans(
        _=mock_token_data,
        db=mock_db_session
    )

    mock_db_session.query.assert_called_once()
    assert len(result) == 2
    assert result == [mock_loan_response_1, mock_loan_response_2]


def test_get_loans_empty(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de una lista vacía de préstamos."""
    
    mock_db_session.query.return_value.all.return_value = []

    result = get_loans(
        _=mock_token_data,
        db=mock_db_session
    )

    assert result == []


def test_get_loans_internal_error(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un error interno en la DB levanta HTTPException 500."""
    
    mock_db_session.query.side_effect = Exception("DB connection failed")

    with pytest.raises(HTTPException) as exc_info:
        get_loans(
            _=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error al listar préstamos" in exc_info.value.detail


@patch('endpoints.loans.get_loan.LoanResponse')
def test_get_user_loans_success_admin(
    MockLoanResponse,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un admin puede obtener préstamos de cualquier usuario."""
    
    user_id = uuid4()
    mock_token_data.role_name = "admin"
    mock_token_data.id = uuid4()  # Diferente ID del usuario consultado
    
    mock_loan_db_1 = Mock(name="LoanDB1")
    mock_loan_db_2 = Mock(name="LoanDB2")
    loans_db = [mock_loan_db_1, mock_loan_db_2]
    
    mock_loan_response_1 = Mock(name="LoanResponse1")
    mock_loan_response_2 = Mock(name="LoanResponse2")
    
    MockLoanResponse.model_validate.side_effect = [
        mock_loan_response_1,
        mock_loan_response_2
    ]
    
    mock_filter = Mock()
    mock_filter.all.return_value = loans_db
    mock_db_session.query.return_value.filter.return_value = mock_filter

    result = get_user_loans(
        user_id=user_id,
        current_user=mock_token_data,
        db=mock_db_session
    )

    mock_db_session.query.assert_called_once()
    assert len(result) == 2
    assert result == [mock_loan_response_1, mock_loan_response_2]


@patch('endpoints.loans.get_loan.LoanResponse')
def test_get_user_loans_success_own_user(
    MockLoanResponse,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un usuario puede obtener sus propios préstamos."""
    
    user_id = uuid4()
    mock_token_data.role_name = "user"
    mock_token_data.id = user_id  # Mismo ID del usuario consultado
    
    mock_loan_db = Mock(name="LoanDB")
    loans_db = [mock_loan_db]
    
    mock_loan_response = Mock(name="LoanResponse")
    MockLoanResponse.model_validate.return_value = mock_loan_response
    
    mock_filter = Mock()
    mock_filter.all.return_value = loans_db
    mock_db_session.query.return_value.filter.return_value = mock_filter

    result = get_user_loans(
        user_id=user_id,
        current_user=mock_token_data,
        db=mock_db_session
    )

    assert len(result) == 1
    assert result == [mock_loan_response]


def test_get_user_loans_unauthorized(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un usuario no puede ver préstamos de otro usuario."""
    
    user_id = uuid4()
    mock_token_data.role_name = "user"
    mock_token_data.id = uuid4()  # Diferente ID del usuario consultado

    with pytest.raises(HTTPException) as exc_info:
        get_user_loans(
            user_id=user_id,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "No tienes permiso" in exc_info.value.detail


def test_get_user_loans_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que se devuelve error 404 cuando no hay préstamos para el usuario."""
    
    user_id = uuid4()
    mock_token_data.role_name = "admin"
    
    mock_filter = Mock()
    mock_filter.all.return_value = []
    mock_db_session.query.return_value.filter.return_value = mock_filter

    with pytest.raises(HTTPException) as exc_info:
        get_user_loans(
            user_id=user_id,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "No se encontraron préstamos" in exc_info.value.detail


@patch('endpoints.loans.get_loan.LoanResponse')
def test_get_loan_success_admin(
    MockLoanResponse,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un admin puede obtener cualquier préstamo."""
    
    loan_id = uuid4()
    mock_token_data.role_name = "admin"
    
    mock_loan_db = Mock()
    mock_loan_db.id = loan_id
    mock_loan_db.user_id = str(uuid4())  # Diferente usuario
    
    mock_loan_response = Mock()
    MockLoanResponse.model_validate.return_value = mock_loan_response
    
    mock_filter = Mock()
    mock_filter.first.return_value = mock_loan_db
    mock_db_session.query.return_value.filter.return_value = mock_filter

    result = get_loan(
        loan_id=loan_id,
        current_user=mock_token_data,
        db=mock_db_session
    )

    assert result == mock_loan_response


@patch('endpoints.loans.get_loan.LoanResponse')
def test_get_loan_success_own_loan(
    MockLoanResponse,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un usuario puede obtener su propio préstamo."""
    
    loan_id = uuid4()
    user_id = uuid4()
    mock_token_data.role_name = "user"
    mock_token_data.id = user_id
    
    mock_loan_db = Mock()
    mock_loan_db.id = loan_id
    mock_loan_db.user_id = str(user_id)  # Mismo usuario
    
    mock_loan_response = Mock()
    MockLoanResponse.model_validate.return_value = mock_loan_response
    
    mock_filter = Mock()
    mock_filter.first.return_value = mock_loan_db
    mock_db_session.query.return_value.filter.return_value = mock_filter

    result = get_loan(
        loan_id=loan_id,
        current_user=mock_token_data,
        db=mock_db_session
    )

    assert result == mock_loan_response


def test_get_loan_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que buscar un préstamo inexistente devuelve error 404."""
    
    loan_id = uuid4()
    mock_token_data.role_name = "admin"
    
    mock_filter = Mock()
    mock_filter.first.return_value = None
    mock_db_session.query.return_value.filter.return_value = mock_filter

    with pytest.raises(HTTPException) as exc_info:
        get_loan(
            loan_id=loan_id,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Préstamo no encontrado" in exc_info.value.detail


def test_get_loan_unauthorized(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un usuario no puede ver préstamos de otros usuarios."""
    
    loan_id = uuid4()
    mock_token_data.role_name = "user"
    mock_token_data.id = uuid4()
    
    mock_loan_db = Mock()
    mock_loan_db.id = loan_id
    mock_loan_db.user_id = str(uuid4())  # Diferente usuario
    
    mock_filter = Mock()
    mock_filter.first.return_value = mock_loan_db
    mock_db_session.query.return_value.filter.return_value = mock_filter

    with pytest.raises(HTTPException) as exc_info:
        get_loan(
            loan_id=loan_id,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "No tienes permiso" in exc_info.value.detail


# Tests para funciones ASÍNCRONAS (create_loan, return_loan)

@pytest.mark.asyncio
async def test_create_loan_success(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_create_payload: LoanCreate
):
    """
    Verifica que la creación de un préstamo exitosa:
    1. Verifica que el material existe.
    2. Verifica que el usuario existe.
    3. Verifica que el material no está prestado.
    4. Crea el préstamo correctamente.
    """
    
    # Mock de material existente
    mock_material = Mock()
    mock_material.id = loan_create_payload.material_id
    
    # Mock de usuario existente
    mock_user = Mock()
    mock_user.id = loan_create_payload.user_id
    
    # Mock de que no hay préstamos activos para el material
    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
        mock_material,  # Para material
        mock_user,      # Para usuario  
        None           # Para préstamo existente
    ]
    
    mock_loan_instance = Mock()
    mock_loan_instance.id = uuid4()
    
    with patch('endpoints.loans.post_loan.LoanDB') as MockLoanDB:
        MockLoanDB.return_value = mock_loan_instance
        
        with patch('endpoints.loans.post_loan.LoanResponse') as MockLoanResponse:
            MockLoanResponse.model_validate.return_value = Mock(id=mock_loan_instance.id)

            result = await create_loan(
                loan=loan_create_payload,
                current_user=mock_token_data,
                db=mock_db_session
            )
        
        mock_db_session.add.assert_called_once_with(mock_loan_instance)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_loan_instance)
        
        assert result is not None


@pytest.mark.asyncio
async def test_create_loan_material_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_create_payload: LoanCreate
):
    """Verifica que crear un préstamo con material inexistente devuelve error 404."""
    
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await create_loan(
            loan=loan_create_payload,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "El material no existe" in exc_info.value.detail
    
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_loan_user_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_create_payload: LoanCreate
):
    """Verifica que crear un préstamo con usuario inexistente devuelve error 404."""
    
    mock_material = Mock()
    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
        mock_material,  # Material existe
        None           # Usuario no existe
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        await create_loan(
            loan=loan_create_payload,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "El usuario no existe" in exc_info.value.detail
    
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_loan_material_already_loaned(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_create_payload: LoanCreate
):
    """Verifica que crear un préstamo con material ya prestado devuelve error 400."""
    
    mock_material = Mock()
    mock_user = Mock()
    mock_existing_loan = Mock()  # Préstamo existente
    
    mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
        mock_material,
        mock_user,
        mock_existing_loan  # Ya existe un préstamo activo
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        await create_loan(
            loan=loan_create_payload,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "El material ya está prestado" in exc_info.value.detail
    
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_return_loan_success(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que la devolución de un préstamo funciona correctamente."""
    
    loan_id = uuid4()
    
    mock_loan_db = Mock()
    mock_loan_db.id = loan_id
    mock_loan_db.is_returned = False  # No devuelto aún
    
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_loan_db

    with patch('endpoints.loans.put_loan.LoanResponse') as MockLoanResponse:
        MockLoanResponse.model_validate.return_value = Mock(id=loan_id)
        
        result = await return_loan(
            loan_id=loan_id,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_loan_db)
    
    # Verifica que se actualizaron los campos correctos
    assert mock_loan_db.is_returned == True
    assert mock_loan_db.updated_by == str(mock_token_data.id)
    assert mock_loan_db.actual_return_date is not None
    assert mock_loan_db.updated_at is not None
    
    assert result is not None


@pytest.mark.asyncio
async def test_return_loan_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que devolver un préstamo inexistente devuelve error 404."""
    
    loan_id = uuid4()
    
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await return_loan(
            loan_id=loan_id,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Préstamo no encontrado" in exc_info.value.detail
    
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_return_loan_already_returned(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que devolver un préstamo ya devuelto devuelve error 400."""
    
    loan_id = uuid4()
    
    mock_loan_db = Mock()
    mock_loan_db.id = loan_id
    mock_loan_db.is_returned = True  # Ya devuelto
    
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_loan_db
    
    with pytest.raises(HTTPException) as exc_info:
        await return_loan(
            loan_id=loan_id,
            current_user=mock_token_data,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "El préstamo ya fue devuelto" in exc_info.value.detail
    
    mock_db_session.commit.assert_not_called()