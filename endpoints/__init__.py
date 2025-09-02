# This file makes the endpoints directory a Python package

# Import all routers to make them available when importing from endpoints
from .users import (
    get_users_router,
    post_user_router,
    put_user_router,
    delete_user_router
)

# Make routers available for import
__all__ = [
    "get_users_router",
    "post_user_router", 
    "put_user_router",
    "delete_user_router"
]