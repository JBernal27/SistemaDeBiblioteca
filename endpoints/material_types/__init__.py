from .get_material_types import router as get_material_types_router
from .post_material_type import router as post_material_type_router
from .put_material_type import router as put_material_type_router
from .delete_material_type import router as delete_material_type_router

__all__ = [
    "get_material_types_router",
    "post_material_type_router",
    "put_material_type_router",
    "delete_material_type_router"
]
