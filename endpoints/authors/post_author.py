from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.schemas import AuthorCreate, Author, TokenData
from database.connection import Author as AuthorDB, get_db
from common.middleware import require_admin
from uuid import uuid4

router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("/", response_model=Author, status_code=status.HTTP_201_CREATED)
async def create_author(
    author: AuthorCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    """
    Crea un nuevo autor en el sistema.
    Solo accesible para administradores.

    Args:
        author: AuthorCreate - Datos del nuevo autor
        db: Session - Sesión de la base de datos
        current_user: TokenData - Token del administrador

    Returns:
        Author - El autor creado

    Raises:
        HTTPException(400) - Error de validación o autor duplicado
        HTTPException(403) - Usuario no autorizado
        HTTPException(500) - Error interno del servidor
    """
    try:
        # Verificar si el autor ya existe
        existing_author = db.query(AuthorDB).filter(AuthorDB.name == author.name).first()
        if existing_author:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un autor con ese nombre"
            )

        db_author = AuthorDB(
            id=uuid4(),
            name=author.name,
            nationality=author.nationality,
            birth_date=author.birth_date,
            death_date=author.death_date,
            biography=author.biography,
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(db_author)
        db.commit()
        db.refresh(db_author)

        return Author.model_validate(db_author, from_attributes=True)

    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad en la base de datos"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
