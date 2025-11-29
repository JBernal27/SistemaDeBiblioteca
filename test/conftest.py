import pytest
from unittest.mock import Mock
from models.schemas import TokenData, AuthorCreate, AuthorUpdate
from uuid import uuid4
from datetime import date
from models.schemas import LoanCreate
from uuid import uuid4
from datetime import datetime

@pytest.fixture
def mock_db_session():
    return Mock()

@pytest.fixture
def mock_token_data():
    return TokenData(email="testuser@example.com", id=uuid4(), role_name="admin")
@pytest.fixture
def author_create_payload():
    return AuthorCreate(
        name="Gabriel Garcia Marquez",
        nationality="Colombiano",
        biography="Premio Nobel de Literatura",
        birth_date= date.fromisoformat("1927-03-06"),
        death_date=None
    )

@pytest.fixture
def author_update_payload():
    return AuthorUpdate(
        name="Gabriel Garcia Marquez Updated",
        nationality="Colombiano",
        biography="Premio Nobel de Literatura Updated",
        birth_date= date.fromisoformat("1927-03-06"),
        death_date=None
    )

@pytest.fixture
def loan_status_create_payload():
    from models.schemas import LoanStatusCreate
    return LoanStatusCreate(name="Prestado")

@pytest.fixture
def loan_status_update_payload():
    from models.schemas import LoanStatusUpdate  
    return LoanStatusUpdate(name="Devuelto")

@pytest.fixture
def loan_create_payload():
    return LoanCreate(
        material_id=uuid4(),
        user_id=uuid4(),
        expected_return_date=datetime.now(),
        status_id=uuid4(),
    )

@pytest.fixture
def material_type_create_payload():
    from models.schemas import MaterialTypeCreate
    return MaterialTypeCreate(
        name="Libro",
        description="Material de lectura"
    )

@pytest.fixture
def material_type_update_payload():
    from models.schemas import MaterialTypeUpdate  
    return MaterialTypeUpdate(
        name="Revista",
        description="Publicación periódica"
    )