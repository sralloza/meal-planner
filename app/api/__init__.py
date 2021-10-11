from fastapi.routing import APIRouter

from .meals import router as meals_router
from .utils import router as utils_router

router = APIRouter()
router.include_router(meals_router, prefix="/meals")
router.include_router(utils_router)
