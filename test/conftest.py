import pytest
from unittest.mock import Mock
from models.schemas import TokenData, AuthorCreate, AuthorUpdate
from uuid import uuid4

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
        biography="Premio Nobel de Literatura"
    )

@pytest.fixture
def author_update_payload():
    return AuthorUpdate(
        name="Gabriel Garcia Marquez Updated",
        nationality="Colombiano",
        biography="Premio Nobel de Literatura Updated"
    )
