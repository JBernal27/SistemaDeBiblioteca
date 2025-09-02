# This file makes the users directory a Python package

# Import all user routers to make them available when importing from endpoints.users
from .get_users import router as get_users_router
from .post_user import router as post_user_router
from .put_user import router as put_user_router
from .delete_user import router as delete_user_router

# Make routers available for import
__all__ = [
    "get_users_router",
    "post_user_router", 
    "put_user_router",
    "delete_user_router"
]