"""Util related API endpoints."""

from fastapi import APIRouter

from ..core.config import Settings, settings
from ..utils.misc import get_version
from ..utils.responses import Version

router = APIRouter(tags=["Utilities"])


@router.get("/version", response_model=Version, summary="Get version")
def get_version_endpoint():
    """Returns the current backend version."""
    return Version(version=get_version())


@router.get("/settings", response_model=Settings, summary="Get settings")
def get_settings():
    """Returns the backend settings."""
    return settings
