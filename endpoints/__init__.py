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

from .loans import (
    get_loan_router,
    post_loan_router,
    put_loan_router
)

__all__ = [
    "get_users_router",
    "post_user_router", 
    "put_user_router",
    "delete_user_router",
    "get_materials_router",
    "post_material_router", 
    "put_material_router",
    "delete_material_router",
    "get_loan_router",
    "post_loan_router",
    "put_loan_router"
]