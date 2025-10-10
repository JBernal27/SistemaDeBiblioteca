from .users import (
    get_users_router,
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

from .auth import (
    login_router,
    register_router
)

from .roles import (
    get_roles_router,
    post_role_router,
    put_role_router,
    delete_role_router
)

from .authors import (
    get_authors_router,
    post_author_router,
    put_author_router,
    delete_author_router
)

from .material_types import (
    get_material_types_router,
    post_material_type_router,
    put_material_type_router,
    delete_material_type_router
)

from .loan_status import (
    get_loan_status_router,
    post_loan_status_router,
    put_loan_status_router,
    delete_loan_status_router
)

__all__ = [
    "get_users_router",
    "put_user_router",
    "delete_user_router",
    "get_materials_router",
    "post_material_router", 
    "put_material_router",
    "delete_material_router",
    "get_loan_router",
    "post_loan_router",
    "put_loan_router",
    "login_router",
    "register_router",
    "get_roles_router",
    "post_role_router",
    "put_role_router",
    "delete_role_router",
    "get_authors_router",
    "post_author_router",
    "put_author_router",
    "delete_author_router",
    "get_material_types_router",
    "post_material_type_router",
    "put_material_type_router",
    "delete_material_type_router",
    "get_loan_status_router",
    "post_loan_status_router",
    "put_loan_status_router",
    "delete_loan_status_router"
]