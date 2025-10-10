from .get_roles import router as get_roles_router
from .post_role import router as post_role_router
from .put_role import router as put_role_router
from .delete_role import router as delete_role_router

__all__ = [
    "get_roles_router",
    "post_role_router",
    "put_role_router",
    "delete_role_router"
]
