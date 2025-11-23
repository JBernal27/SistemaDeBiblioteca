import pytest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4
from fastapi import status, HTTPException
from datetime import date
from models.schemas import AuthorCreate, AuthorUpdate, TokenData
from endpoints.authors.get_authors import get_authors, get_author
from endpoints.authors.post_author import create_author
from endpoints.authors.put_author import update_author
from endpoints.authors.delete_author import delete_author


@pytest.mark.asyncio
@patch('endpoints.authors.get_authors.Author')
async def test_get_authors_success(
    MockAuthorPydantic,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de una lista de autores con paginación."""
    
    mock_author_db_1 = Mock(name="AuthorDB1")
    mock_author_db_2 = Mock(name="AuthorDB2")
    authors_db = [mock_author_db_1, mock_author_db_2]
    
    mock_author_pydantic_1 = Mock(name="AuthorPydantic1")
    mock_author_pydantic_2 = Mock(name="AuthorPydantic2")
    
    MockAuthorPydantic.model_validate.side_effect = [
        mock_author_pydantic_1,
        mock_author_pydantic_2
    ]
    
    mock_result = Mock()
    mock_result.scalars.return_value.unique.return_value.all.return_value = authors_db
    mock_db_session.execute.return_value = mock_result

    result = await get_authors(
        _=mock_token_data, # Corregido
        skip=10,
        limit=50,
        db=mock_db_session
    )

    mock_db_session.execute.assert_called_once()
    assert len(result) == 2
    assert result == [mock_author_pydantic_1, mock_author_pydantic_2]
    
@pytest.mark.asyncio
async def test_get_authors_empty(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica la obtención exitosa de una lista vacía de autores."""
    
    mock_result = Mock()
    mock_result.scalars.return_value.unique.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result

    result = await get_authors(
        _=mock_token_data, # Corregido
        skip=0,
        limit=10,
        db=mock_db_session
    )

    assert result == []
    
@pytest.mark.asyncio
async def test_get_authors_internal_error(
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """Verifica que un error interno en la DB levanta HTTPException 500."""
    
    mock_db_session.execute.side_effect = Exception("DB connection failed")

    with pytest.raises(HTTPException) as exc_info:
        await get_authors(
            _=mock_token_data, # Corregido
            skip=0,
            limit=10,
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error interno del servidor" in exc_info.value.detail


@pytest.mark.asyncio
@patch('endpoints.authors.get_authors.Author')
async def test_get_author_success(
    MockAuthorPydantic,
    mock_db_session: Mock,
):
    """Verifica la obtención exitosa de un autor por ID."""
    
    author_id = uuid4()
    
    mock_author_db = Mock(name="AuthorDB")
    mock_author_db.id = author_id
    mock_author_pydantic = Mock(name="AuthorPydantic")
    
    MockAuthorPydantic.model_validate.return_value = mock_author_pydantic
    
    mock_result = Mock()
    mock_result.scalars.return_value.unique.return_value.one_or_none.return_value = mock_author_db
    mock_db_session.execute.return_value = mock_result

    result = await get_author(
        author_id=str(author_id),
        db=mock_db_session
    )

    assert result == mock_author_pydantic

@pytest.mark.asyncio
async def test_get_author_not_found(
    mock_db_session: Mock,
):
    """Verifica que buscar un autor inexistente devuelve error 404."""
    
    author_id = uuid4()
    
    mock_result = Mock()
    mock_result.scalars.return_value.unique.return_value.one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await get_author(
            author_id=str(author_id),
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Autor no encontrado" in exc_info.value.detail
    
@pytest.mark.asyncio
async def test_get_author_internal_error(
    mock_db_session: Mock,
):
    """Verifica que un error interno en la DB al buscar autor levanta HTTPException 500."""
    
    author_id = uuid4()
    
    mock_db_session.execute.side_effect = Exception("DB lookup failed")

    with pytest.raises(HTTPException) as exc_info:
        await get_author(
            author_id=str(author_id),
            db=mock_db_session
        )
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error interno del servidor" in exc_info.value.detail


@pytest.mark.asyncio
@patch('endpoints.authors.post_author.AuthorDB')
@patch('endpoints.authors.post_author.uuid4')
async def test_create_author_success(
    mock_uuid4,
    MockAuthorDB,
    mock_db_session: Mock,
    mock_token_data: TokenData,
    author_create_payload: AuthorCreate
):
    """
    Verifica que la creación de un autor exitosa:
    1. Verifica que no existe un autor con el mismo nombre.
    2. Crea una nueva instancia de AuthorDB con los datos correctos.
    3. Llama a db.add, db.commit y db.refresh.
    4. Devuelve un modelo Author validado.
    """
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    author_id = uuid4()
    mock_uuid4.return_value = author_id
    
    mock_author_instance = MockAuthorDB.return_value
    mock_author_instance.id = author_id
    
    with patch('endpoints.authors.post_author.Author') as MockAuthorPydantic:
        MockAuthorPydantic.model_validate.return_value = Mock(id=author_id)

        result = await create_author(
            author=author_create_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
        mock_db_session.query.assert_called()
        
        mock_db_session.add.assert_called_once_with(mock_author_instance)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_author_instance)
        
        assert result is not None
        assert result.id == author_id

@pytest.mark.asyncio
@patch('endpoints.authors.post_author.AuthorDB')
async def test_create_author_duplicate_name(
    MockAuthorDB,
    mock_db_session: Mock,
    mock_token_data: TokenData,
    author_create_payload: AuthorCreate
):
    """
    Verifica que crear un autor con nombre duplicado devuelve error 400.
    """
    
    mock_existing_author = Mock()
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_existing_author
    
    with pytest.raises(HTTPException) as exc_info:
        await create_author(
            author=author_create_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe un autor con ese nombre" in exc_info.value.detail
    
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
@patch('endpoints.authors.put_author.AuthorDB')
async def test_update_author_success(
    MockAuthorDB,
    mock_db_session: Mock,
    mock_token_data: TokenData,
    author_update_payload: AuthorUpdate
):
    """
    Verifica que la actualización de un autor:
    1. Encuentra el autor por ID.
    2. Verifica que el nuevo nombre no existe (si se cambió).
    3. Actualiza los campos correctos.
    4. Llama a db.commit y db.refresh.
    """
    
    author_id = uuid4()
    
    mock_author = Mock()
    mock_author.id = author_id
    mock_author.name = "Nombre Antiguo"
    mock_author.nationality = "Colombiano"
    mock_author.biography = "Escritor y periodista"
    mock_author.updated_by = None
    
    mock_query_result = Mock()
    mock_query_result.filter.return_value.first.side_effect = [
        mock_author,
        None
    ]
    
    mock_db_session.query.return_value = mock_query_result

    with patch('endpoints.authors.put_author.Author') as MockAuthorPydantic:
        MockAuthorPydantic.model_validate.return_value = Mock(id=author_id)
        
        result = await update_author(
            author_id=author_id,
            author_update=author_update_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_author)
        
        assert mock_author.name == author_update_payload.name
        assert mock_author.updated_by == mock_token_data.id
        assert result is not None


@pytest.mark.asyncio
@patch('endpoints.authors.put_author.AuthorDB')
async def test_update_author_not_found(
    MockAuthorDB,
    mock_db_session: Mock,
    mock_token_data: TokenData,
    author_update_payload: AuthorUpdate
):
    """
    Verifica que actualizar un autor inexistente devuelve error 404.
    """
    
    author_id = uuid4()
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await update_author(
            author_id=author_id,
            author_update=author_update_payload,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Autor no encontrado" in exc_info.value.detail
    
    mock_db_session.commit.assert_not_called()


@pytest.mark.asyncio
@patch('endpoints.authors.delete_author.MaterialDB')
@patch('endpoints.authors.delete_author.AuthorDB')
async def test_delete_author_success(
    MockAuthorDB,
    MockMaterialDB,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """
    Verifica que eliminar un autor sin materiales asociados.
    """
    
    author_id = uuid4()
    
    mock_author = Mock()
    mock_author.id = author_id
    mock_author.name = "Autor Test"
    
    def mock_query_returner(model):
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        
        if model == MockAuthorDB:
            mock_filter.first.return_value = mock_author
            return mock_query
        elif model == MockMaterialDB:
            mock_filter.count.return_value = 0
            mock_filter.first.return_value = None 
            return mock_query
        return Mock()

    mock_db_session.query.side_effect = mock_query_returner
    
    result = await delete_author(
        author_id=author_id,
        db=mock_db_session,
        current_user=mock_token_data
    )
    
    mock_db_session.delete.assert_called_once_with(mock_author)
    mock_db_session.commit.assert_called_once()
    
    assert result["message"] == "Autor eliminado correctamente"


@pytest.mark.asyncio
@patch('endpoints.authors.delete_author.MaterialDB')
@patch('endpoints.authors.delete_author.AuthorDB')
async def test_delete_author_with_materials(
    MockAuthorDB,
    MockMaterialDB,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """
    Verifica que eliminar un autor con materiales asociados devuelve error 400.
    """
    
    author_id = uuid4()
    
    mock_author = Mock()
    mock_author.id = author_id
    
    def mock_query_returner(model):
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        
        if model == MockAuthorDB:
            mock_filter.first.return_value = mock_author
            return mock_query
        elif model == MockMaterialDB:
            mock_filter.count.return_value = 3
            return mock_query
        return Mock()

    mock_db_session.query.side_effect = mock_query_returner
    
    with pytest.raises(HTTPException) as exc_info:
        await delete_author(
            author_id=author_id,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "3 material(es) asociado(s)" in exc_info.value.detail
    
    mock_db_session.delete.assert_not_called()


@pytest.mark.asyncio
@patch('endpoints.authors.delete_author.AuthorDB')
async def test_delete_author_not_found(
    MockAuthorDB,
    mock_db_session: Mock,
    mock_token_data: TokenData
):
    """
    Verifica que eliminar un autor inexistente devuelve error 404.
    """
    
    author_id = uuid4()
    
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await delete_author(
            author_id=author_id,
            db=mock_db_session,
            current_user=mock_token_data
        )
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Autor no encontrado" in exc_info.value.detail
    
    mock_db_session.delete.assert_not_called()