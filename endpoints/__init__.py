from .users import (
    get_users_router,
    post_user_router,
    put_user_router,
    delete_user_router
)

from .materials import (
    get_materials_router,
    post_material_router,
    put_material_router,
    delete_material_router
)

__all__ = [
    "get_users_router",
    "post_user_router", 
    "put_user_router",
    "delete_user_router",
    "get_materials_router",
    "post_material_router", 
    "put_material_router",
    "delete_material_router"
]