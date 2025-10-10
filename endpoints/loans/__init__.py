from .get_loan import router as get_loan_router
from .post_loan import router as post_loan_router
from .put_loan import router as put_loan_router

__all__ = [
    "get_loan_router",
    "post_loan_router", 
    "put_loan_router"
]