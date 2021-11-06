"""API module. Contains the API router."""

from fastapi.routing import APIRouter

from .cron import router as cron_router
from .meals import router as meals_router
from .utils import router as utils_router

router = APIRouter()

router.include_router(cron_router, prefix="/cron")
router.include_router(meals_router, prefix="/meals")
router.include_router(utils_router)
