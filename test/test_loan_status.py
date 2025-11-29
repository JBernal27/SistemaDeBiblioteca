import pytest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4
from fastapi import status, HTTPException
from models.schemas import LoanStatusCreate, LoanStatusUpdate, LoanStatus, TokenData
from endpoints.loan_status.delete_loan_status import delete_loan_status
from endpoints.loan_status.get_loan_status import get_loan_status, get_loan_status_by_id
from endpoints.loan_status.post_loan_status import create_loan_status
from endpoints.loan_status.put_loan_status import update_loan_status


@patch('endpoints.loan_status.get_loan_status.LoanStatus')
@pytest.mark.asyncio
async def test_get_loan_status_success(
    MockLoanStatus,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de una lista de estados de préstamo."""
    
    mock_status_db_1 = Mock(name="LoanStatusDB1")
    mock_status_db_2 = Mock(name="LoanStatusDB2")
    status_db = [mock_status_db_1, mock_status_db_2]
    
    mock_status_1 = Mock(name="LoanStatus1")
    mock_status_2 = Mock(name="LoanStatus2")
    
    MockLoanStatus.model_validate.side_effect = [mock_status_1, mock_status_2]
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = status_db
    mock_db_session.execute.return_value = mock_result

    result = await get_loan_status(
        skip=0,
        limit=10,
        db=mock_db_session
    )

    mock_db_session.execute.assert_called_once()
    assert len(result) == 2
    assert result == [mock_status_1, mock_status_2]


@pytest.mark.asyncio
async def test_get_loan_status_empty(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de una lista vacía de estados de préstamo."""
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result

    result = await get_loan_status(
        skip=0,
        limit=10,
        db=mock_db_session
    )

    assert result == []


@pytest.mark.asyncio
async def test_get_loan_status_internal_error(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un error interno en la DB levanta HTTPException 500."""
    
    mock_db_session.execute.side_effect = Exception("DB connection failed")

    with pytest.raises(HTTPException) as exc_info:
        await get_loan_status(
            skip=0,
            limit=10,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error interno del servidor" in exc_info.value.detail


@patch('endpoints.loan_status.get_loan_status.LoanStatus')
@pytest.mark.asyncio
async def test_get_loan_status_by_id_success(
    MockLoanStatus,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de un estado de préstamo por ID."""
    
    status_id = uuid4()
    
    mock_status_db = Mock(name="LoanStatusDB")
    mock_status_db.id = status_id
    mock_status = Mock(name="LoanStatus")
    
    MockLoanStatus.model_validate.return_value = mock_status
    
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_status_db
    mock_db_session.execute.return_value = mock_result

    result = await get_loan_status_by_id(
        loan_status_id=str(status_id),
        db=mock_db_session,
        current_user=mock_token_data
    )

    assert result == mock_status


@pytest.mark.asyncio
async def test_get_loan_status_by_id_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que buscar un estado de préstamo inexistente devuelve error 404."""
    
    status_id = uuid4()
    
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await get_loan_status_by_id(
            loan_status_id=str(status_id),
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Estado de préstamo no encontrado" in exc_info.value.detail


# Fixtures para loan_status (agregar a conftest.py)
@pytest.fixture
def loan_status_create_payload():
    return LoanStatusCreate(
        name="Prestado"
    )

@pytest.fixture
def loan_status_update_payload():
    return LoanStatusUpdate(
        name="Devuelto"
    )


@patch('endpoints.loan_status.post_loan_status.uuid4')
@pytest.mark.asyncio
async def test_create_loan_status_success(
    mock_uuid4,
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_status_create_payload: LoanStatusCreate
):
    """
    Verifica que la creación de un estado de préstamo exitosa:
    1. Verifica que no existe un estado con el mismo nombre.
    2. Crea una nueva instancia con los datos correctos.
    3. Llama a db.add, db.commit y db.refresh.
    """
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    status_id = uuid4()
    mock_uuid4.return_value = status_id
    
    with patch('endpoints.loan_status.post_loan_status.LoanStatusDB') as MockLoanStatusDB:
        mock_status_instance = MockLoanStatusDB.return_value
        mock_status_instance.id = status_id
        
        with patch('endpoints.loan_status.post_loan_status.LoanStatus') as MockLoanStatus:
            MockLoanStatus.model_validate.return_value = Mock(id=status_id)

            result = await create_loan_status(
                loan_status=loan_status_create_payload,
                db=mock_db_session,
                current_user=mock_token_data
            )
        
        mock_db_session.query.assert_called()
        MockLoanStatusDB.assert_called_once_with(
            id=status_id,
            name=loan_status_create_payload.name,
            created_by=mock_token_data.id,
            updated_by=mock_token_data.id
        )
        
        mock_db_session.add.assert_called_once_with(mock_status_instance)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_status_instance)
        
        assert result is not None


@pytest.mark.asyncio
async def test_create_loan_status_duplicate_name(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_status_create_payload: LoanStatusCreate
):
    """Verifica que crear un estado de préstamo con nombre duplicado devuelve error 400."""
    
    mock_existing_status = Mock()
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_existing_status
    
    with pytest.raises(HTTPException) as exc_info:
        await create_loan_status(
            loan_status=loan_status_create_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe un estado de préstamo con ese nombre" in exc_info.value.detail
    
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


@patch('endpoints.loan_status.put_loan_status.LoanStatus')
@pytest.mark.asyncio
async def test_update_loan_status_success(
    MockLoanStatus,
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_status_update_payload: LoanStatusUpdate
):
    """
    Verifica que la actualización de un estado de préstamo:
    1. Encuentra el estado por ID.
    2. Verifica que el nuevo nombre no existe (si se cambió).
    3. Actualiza los campos correctos.
    """
    
    status_id = uuid4()
    
    mock_status = Mock()
    mock_status.id = status_id
    mock_status.name = "Prestado"
    mock_status.updated_by = None
    
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_status,  # Estado encontrado
        None         # No existe estado con nuevo nombre
    ]

    MockLoanStatus.model_validate.return_value = Mock(id=status_id)
        
    result = await update_loan_status(
        loan_status_id=status_id,
        loan_status_update=loan_status_update_payload,
        db=mock_db_session,
        current_user=mock_token_data
    )
    
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_status)
    
    assert mock_status.name == loan_status_update_payload.name
    assert mock_status.updated_by == mock_token_data.id
    assert result is not None


@pytest.mark.asyncio
async def test_update_loan_status_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_status_update_payload: LoanStatusUpdate
):
    """Verifica que actualizar un estado de préstamo inexistente devuelve error 404."""
    
    status_id = uuid4()
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await update_loan_status(
            loan_status_id=status_id,
            loan_status_update=loan_status_update_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Estado de préstamo no encontrado" in exc_info.value.detail
    
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_loan_status_duplicate_name(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    loan_status_update_payload: LoanStatusUpdate
):
    """Verifica que actualizar con nombre duplicado devuelve error 400."""
    
    status_id = uuid4()
    
    mock_status = Mock()
    mock_status.id = status_id
    mock_status.name = "Prestado"
    
    mock_existing_status = Mock()  # Estado con el nombre que queremos usar
    
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_status,        # Estado encontrado
        mock_existing_status  # Ya existe estado con ese nombre
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        await update_loan_status(
            loan_status_id=status_id,
            loan_status_update=loan_status_update_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe un estado de préstamo con ese nombre" in exc_info.value.detail
    
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_loan_status_success(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que eliminar un estado de préstamo sin préstamos asociados funciona."""
    
    status_id = uuid4()
    
    mock_status = Mock()
    mock_status.id = status_id
    
    # Mock para encontrar el estado
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_status
    # Mock para contar préstamos (0 préstamos)
    mock_db_session.query.return_value.filter.return_value.count.return_value = 0
    
    result = await delete_loan_status(
        loan_status_id=status_id,
        db=mock_db_session,
        current_user=mock_token_data
    )
    
    mock_db_session.delete.assert_called_once_with(mock_status)
    mock_db_session.commit.assert_called_once()
    
    assert result["message"] == "Estado de préstamo eliminado correctamente"


@pytest.mark.asyncio
async def test_delete_loan_status_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que eliminar un estado de préstamo inexistente devuelve error 404."""
    
    status_id = uuid4()
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await delete_loan_status(
            loan_status_id=status_id,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Estado de préstamo no encontrado" in exc_info.value.detail
    
    mock_db_session.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_loan_status_with_loans(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que eliminar un estado de préstamo con préstamos asociados devuelve error 400."""
    
    status_id = uuid4()
    
    mock_status = Mock()
    mock_status.id = status_id
    
    # Mock para encontrar el estado
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_status
    # Mock para contar préstamos (3 préstamos)
    mock_db_session.query.return_value.filter.return_value.count.return_value = 3
    
    with pytest.raises(HTTPException) as exc_info:
        await delete_loan_status(
            loan_status_id=status_id,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "3 préstamo(s) asociado(s)" in exc_info.value.detail
    
    mock_db_session.delete.assert_not_called()