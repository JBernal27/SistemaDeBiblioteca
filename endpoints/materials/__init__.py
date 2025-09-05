from .get_material import router as get_materials_router
from .post_material import router as post_material_router
from .put_material import router as put_material_router
from .delete_material import router as delete_material_router

__all__ = [
    "get_materials_router",
    "post_material_router", 
    "put_material_router",
    "delete_material_router"
]