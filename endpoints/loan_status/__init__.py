from .get_loan_status import router as get_loan_status_router
from .post_loan_status import router as post_loan_status_router
from .put_loan_status import router as put_loan_status_router
from .delete_loan_status import router as delete_loan_status_router

__all__ = [
    "get_loan_status_router",
    "post_loan_status_router",
    "put_loan_status_router",
    "delete_loan_status_router"
]
