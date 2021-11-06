"""Util related API endpoints."""

from fastapi import APIRouter

from ..utils.misc import get_version
from ..utils.responses import Version

router = APIRouter(tags=["Utilities"])


@router.get("/version", response_model=Version, summary="Get version")
def get_version_endpoint():
    """Returns the current backend version."""
    return Version(version=get_version())
