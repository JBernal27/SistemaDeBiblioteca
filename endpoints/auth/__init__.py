from .login import router as login_router
from .login import login
from .register import router as register_router

__all__ = [
    "login_router",
    "register_router",
    "login"
]