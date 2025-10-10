from .get_authors import router as get_authors_router
from .post_author import router as post_author_router
from .put_author import router as put_author_router
from .delete_author import router as delete_author_router

__all__ = [
    "get_authors_router",
    "post_author_router",
    "put_author_router",
    "delete_author_router"
]
