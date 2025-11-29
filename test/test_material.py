import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timezone

from main import app
from database.connection import get_db, Material as MaterialDB
from common.middleware.auth_middleware import require_admin
from models.schemas import TokenData, MaterialCreate, MaterialUpdate

# --- Fixtures ---

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def override_get_db(mock_db_session):
    def _get_db():
        yield mock_db_session
    return _get_db

@pytest.fixture
def mock_admin_user():
    return TokenData(id=uuid4(), email="admin@test.com", role_name="admin")

@pytest.fixture
def mock_client(override_get_db, mock_admin_user):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = lambda: mock_admin_user
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def material_data():
    return {
        "title": "Nuevo Libro de Python",
        "author_id": str(uuid4()),
        "type_id": str(uuid4()),
        "img": "http://example.com/image.png"
    }

# --- Tests ---

def test_create_material_success(mock_client, mock_db_session, material_data):
    # Create a mock for MaterialTypeDB that will be returned
    mock_material_type = MagicMock()
    mock_material_type.id = material_data["type_id"]
    
    # Configure query chain for first call (MaterialTypeDB check)
    first_query = MagicMock()
    first_filter = MagicMock()
    first_filter.first.return_value = mock_material_type
    first_query.filter.return_value = first_filter
    
    # Configure query chain for second call (MaterialDB duplicate check)
    second_query = MagicMock()
    second_filter = MagicMock()
    second_filter.first.return_value = None  # No existing material
    second_query.filter.return_value = second_filter
    
    # Make query() return different mocks for each call
    mock_db_session.query.side_effect = [first_query, second_query]
    
    # Mock add, commit, refresh to complete the operation
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    
    # Setup refresh to populate the mock material with required fields
    def setup_material(material_instance):
        material_instance.id = uuid4()
        material_instance.date_added = datetime.now(timezone.utc)
        material_instance.updated_at = datetime.now(timezone.utc)
        material_instance.is_deleted = False
        material_instance.created_by = None
        material_instance.updated_by = None
        material_instance.author = None
        material_instance.material_type = None
    
    mock_db_session.refresh.side_effect = setup_material
    
    response = mock_client.post("/materials/", json=material_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == material_data["title"]
    assert data["author_id"] == material_data["author_id"]
    assert data["type_id"] == material_data["type_id"]

def test_get_materials_success(mock_client, mock_db_session):
    # Mock database response
    mock_material = MaterialDB(
        id=uuid4(),
        title="Libro Test",
        author_id=uuid4(),
        type_id=uuid4(),
        is_deleted=False,
        date_added=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [mock_material]
    
    response = mock_client.get("/materials/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Libro Test"

def test_get_material_by_id_success(mock_client, mock_db_session):
    material_id = uuid4()
    mock_material = MaterialDB(
        id=material_id,
        title="Libro Test",
        author_id=uuid4(),
        type_id=uuid4(),
        is_deleted=False,
        date_added=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_material
    
    response = mock_client.get(f"/materials/{material_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Libro Test"
    assert data["id"] == str(material_id)

def test_get_material_not_found(mock_client, mock_db_session):
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    response = mock_client.get(f"/materials/{uuid4()}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_material_success(mock_client, mock_db_session):
    material_id = uuid4()
    mock_material = MaterialDB(id=material_id, is_deleted=False)
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_material
    
    # Mock update
    mock_db_session.query.return_value.filter.return_value.update.return_value = 1
    
    response = mock_client.delete(f"/materials/{material_id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_db_session.commit.assert_called()
