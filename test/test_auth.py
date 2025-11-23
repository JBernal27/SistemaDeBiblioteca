import pytest
from unittest.mock import Mock, patch
from endpoints.auth.register import create_user 
from endpoints.auth.login import login
from models.schemas import RegisterDTO, LoginResponse, LoginDTO 

@pytest.fixture
def mock_db_session():
    """Mock de la sesión de base de datos."""
    return Mock()

@pytest.fixture
def register_payload():
    """Payload de registro DTO simulado."""
    return RegisterDTO(
        email="new@user.com", 
        full_name="New User", 
        password="password123"
    )

@pytest.mark.asyncio
@patch('endpoints.auth.register.login')
@patch('endpoints.auth.register.select')
@patch('endpoints.auth.register.RoleDB')
@patch('endpoints.auth.register.UserDB')
async def test_register_user_success(
    MockUserDB, 
    MockRoleDB, 
    MockSelect, 
    mock_login, 
    mock_db_session: Mock, 
    register_payload: RegisterDTO
):
    """
    Verifica que el registro exitoso:
    1. No encuentra un usuario duplicado.
    2. Encuentra el rol 'cliente'.
    3. Llama correctamente a db.add, db.commit, y db.refresh.
    4. Reutiliza la función login para el token final.
    """
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    mock_role_instance = Mock()
    mock_role_instance.id = 1
    mock_role_instance.name = "cliente"
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_role_instance
    
    mock_db_instance = MockUserDB.return_value
    mock_db_instance.id = 100
    
    mock_login.return_value = LoginResponse(
        message="Login correcto", 
        token="MOCK_JWT_TOKEN", 
        error=None
    )
    
    response: LoginResponse = await create_user(
        user=register_payload, 
        db=mock_db_session
    )
    
    mock_db_session.execute.assert_called_once()
    
    mock_db_session.query.assert_called_once() 
    
    MockUserDB.assert_called_once()
    
    assert mock_db_session.add.call_count == 2
    assert mock_db_session.commit.call_count == 3
    assert mock_db_session.refresh.call_count == 2
    
    mock_login.assert_called_once()
    
    login_dto_passed = mock_login.call_args[1]['data']
    
    assert isinstance(login_dto_passed, LoginDTO) 
    assert login_dto_passed.email == register_payload.email
    assert login_dto_passed.password == register_payload.password
    assert mock_login.call_args[1]['db'] == mock_db_session
    
    assert response.token == "MOCK_JWT_TOKEN"
    assert response.message == "Login correcto"
    assert response.error is None

@pytest.mark.asyncio
@patch('endpoints.auth.register.select')
async def test_register_user_duplicate_email(
    MockSelect, 
    mock_db_session: Mock, 
    register_payload: RegisterDTO
):
    """
    Verifica que el registro devuelve el mensaje de error cuando el email ya existe.
    """
    
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = Mock() 
    
    response: LoginResponse = await create_user(
        user=register_payload, 
        db=mock_db_session
    )
    
    mock_db_session.execute.assert_called_once()
    
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()
    mock_db_session.query.assert_not_called()
    
    assert response.message == "El correo ya está registrado"
    assert response.error == "400 Bad Request"
    assert response.token is None