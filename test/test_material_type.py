import pytest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4
from fastapi import status, HTTPException
from models.schemas import MaterialTypeCreate, MaterialTypeUpdate, MaterialType, TokenData
from endpoints.material_types.delete_material_type import delete_material_type
from endpoints.material_types.get_material_type import get_material_types, get_material_type
from endpoints.material_types.post_material_type import create_material_type
from endpoints.material_types.put_material_type import update_material_type


@patch('endpoints.material_types.get_material_type.MaterialType')
def test_get_material_types_success(
    MockMaterialType,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de una lista de tipos de material."""
    
    mock_type_db_1 = Mock(name="MaterialTypeDB1")
    mock_type_db_2 = Mock(name="MaterialTypeDB2")
    types_db = [mock_type_db_1, mock_type_db_2]
    
    mock_type_1 = Mock(name="MaterialType1")
    mock_type_2 = Mock(name="MaterialType2")
    
    MockMaterialType.model_validate.side_effect = [mock_type_1, mock_type_2]
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = types_db
    mock_db_session.execute.return_value = mock_result

    result = get_material_types(
        _=mock_token_data,
        skip=0,
        limit=10,
        db=mock_db_session
    )

    mock_db_session.execute.assert_called_once()
    assert len(result) == 2
    assert result == [mock_type_1, mock_type_2]


def test_get_material_types_empty(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de una lista vacía de tipos de material."""
    
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result

    result = get_material_types(
        _=mock_token_data,
        skip=0,
        limit=10,
        db=mock_db_session
    )

    assert result == []


def test_get_material_types_internal_error(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un error interno en la DB levanta HTTPException 500."""
    
    mock_db_session.execute.side_effect = Exception("DB connection failed")

    with pytest.raises(HTTPException) as exc_info:
        get_material_types(
            _=mock_token_data,
            skip=0,
            limit=10,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error interno del servidor" in exc_info.value.detail


@patch('endpoints.material_types.get_material_type.MaterialType')
def test_get_material_type_success(
    MockMaterialType,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de un tipo de material por ID."""
    
    type_id = uuid4()
    
    mock_type_db = Mock(name="MaterialTypeDB")
    mock_type_db.id = type_id
    mock_type = Mock(name="MaterialType")
    
    MockMaterialType.model_validate.return_value = mock_type
    
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_type_db
    mock_db_session.execute.return_value = mock_result

    result = get_material_type(
        material_type_id=str(type_id),
        db=mock_db_session,
        current_user=mock_token_data
    )

    assert result == mock_type


def test_get_material_type_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que buscar un tipo de material inexistente devuelve error 404."""
    
    type_id = uuid4()
    
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        get_material_type(
            material_type_id=str(type_id),
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Tipo de material no encontrado" in exc_info.value.detail


# Fixtures para material_types (agregar a conftest.py)
@pytest.fixture
def material_type_create_payload():
    return MaterialTypeCreate(
        name="Libro",
        description="Material de lectura"
    )

@pytest.fixture
def material_type_update_payload():
    return MaterialTypeUpdate(
        name="Revista",
        description="Publicación periódica"
    )


@patch('endpoints.material_types.post_material_type.uuid4')
def test_create_material_type_success(
    mock_uuid4,
    mock_db_session: Mock,
    mock_token_data: TokenData,
    material_type_create_payload: MaterialTypeCreate
):
    """
    Verifica que la creación de un tipo de material exitosa:
    1. Verifica que no existe un tipo con el mismo nombre.
    2. Crea una nueva instancia con los datos correctos.
    3. Llama a db.add, db.commit y db.refresh.
    """
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    type_id = uuid4()
    mock_uuid4.return_value = type_id
    
    with patch('endpoints.material_types.post_material_type.MaterialTypeDB') as MockMaterialTypeDB:
        mock_type_instance = MockMaterialTypeDB.return_value
        mock_type_instance.id = type_id
        
        with patch('endpoints.material_types.post_material_type.MaterialType') as MockMaterialType:
            MockMaterialType.model_validate.return_value = Mock(id=type_id)

            result = create_material_type(
                material_type=material_type_create_payload,
                db=mock_db_session,
                current_user=mock_token_data
            )
        
        mock_db_session.query.assert_called()
        MockMaterialTypeDB.assert_called_once_with(
            id=type_id,
            name=material_type_create_payload.name,
            description=material_type_create_payload.description,
            created_by=mock_token_data.id,
            updated_by=mock_token_data.id
        )
        
        mock_db_session.add.assert_called_once_with(mock_type_instance)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_type_instance)
        
        assert result is not None


def test_create_material_type_duplicate_name(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    material_type_create_payload: MaterialTypeCreate
):
    """Verifica que crear un tipo de material con nombre duplicado devuelve error 400."""
    
    mock_existing_type = Mock()
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_existing_type
    
    with pytest.raises(HTTPException) as exc_info:
        create_material_type(
            material_type=material_type_create_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe un tipo de material con ese nombre" in exc_info.value.detail
    
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


@patch('endpoints.material_types.put_material_type.MaterialType')
def test_update_material_type_success(
    MockMaterialType,
    mock_db_session: Mock,
    mock_token_data: TokenData,
    material_type_update_payload: MaterialTypeUpdate
):
    """
    Verifica que la actualización de un tipo de material:
    1. Encuentra el tipo por ID.
    2. Verifica que el nuevo nombre no existe (si se cambió).
    3. Actualiza los campos correctos.
    """
    
    type_id = uuid4()
    
    mock_type = Mock()
    mock_type.id = type_id
    mock_type.name = "Libro"
    mock_type.description = "Material de lectura"
    mock_type.updated_by = None
    
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_type,  # Tipo encontrado
        None        # No existe tipo con nuevo nombre
    ]

    MockMaterialType.model_validate.return_value = Mock(id=type_id)
        
    result = update_material_type(
        material_type_id=type_id,
        material_type_update=material_type_update_payload,
        db=mock_db_session,
        current_user=mock_token_data
    )
    
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_type)
    
    assert mock_type.name == material_type_update_payload.name
    assert mock_type.description == material_type_update_payload.description
    assert mock_type.updated_by == mock_token_data.id
    assert result is not None


def test_update_material_type_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    material_type_update_payload: MaterialTypeUpdate
):
    """Verifica que actualizar un tipo de material inexistente devuelve error 404."""
    
    type_id = uuid4()
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        update_material_type(
            material_type_id=type_id,
            material_type_update=material_type_update_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Tipo de material no encontrado" in exc_info.value.detail
    
    mock_db_session.commit.assert_not_called()


def test_update_material_type_duplicate_name(
    mock_db_session: Mock,
    mock_token_data: TokenData,
    material_type_update_payload: MaterialTypeUpdate
):
    """Verifica que actualizar con nombre duplicado devuelve error 400."""
    
    type_id = uuid4()
    
    mock_type = Mock()
    mock_type.id = type_id
    mock_type.name = "Libro"
    
    mock_existing_type = Mock()  # Tipo con el nombre que queremos usar
    
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [
        mock_type,        # Tipo encontrado
        mock_existing_type  # Ya existe tipo con ese nombre
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        update_material_type(
            material_type_id=type_id,
            material_type_update=material_type_update_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe un tipo de material con ese nombre" in exc_info.value.detail
    
    mock_db_session.commit.assert_not_called()


def test_delete_material_type_success(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que eliminar un tipo de material sin materiales asociados funciona."""
    
    type_id = uuid4()
    
    mock_type = Mock()
    mock_type.id = type_id
    
    # Mock para encontrar el tipo
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_type
    # Mock para contar materiales (0 materiales)
    mock_db_session.query.return_value.filter.return_value.count.return_value = 0
    
    result = delete_material_type(
        material_type_id=type_id,
        db=mock_db_session,
        current_user=mock_token_data
    )
    
    mock_db_session.delete.assert_called_once_with(mock_type)
    mock_db_session.commit.assert_called_once()
    
    assert result["message"] == "Tipo de material eliminado correctamente"


def test_delete_material_type_not_found(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que eliminar un tipo de material inexistente devuelve error 404."""
    
    type_id = uuid4()
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        delete_material_type(
            material_type_id=type_id,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Tipo de material no encontrado" in exc_info.value.detail
    
    mock_db_session.delete.assert_not_called()


def test_delete_material_type_with_materials(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que eliminar un tipo de material con materiales asociados devuelve error 400."""
    
    type_id = uuid4()
    
    mock_type = Mock()
    mock_type.id = type_id
    
    # Mock para encontrar el tipo
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_type
    # Mock para contar materiales (3 materiales)
    mock_db_session.query.return_value.filter.return_value.count.return_value = 3
    
    with pytest.raises(HTTPException) as exc_info:
        delete_material_type(
            material_type_id=type_id,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "3 material(es) asociado(s)" in exc_info.value.detail
    
    mock_db_session.delete.assert_not_called()