from typing import Optional

from fastapi import Header, HTTPException

from ..core.config import settings


def token_middleware(x_token: Optional[str] = Header(None)):
    if x_token is None:
        raise HTTPException(401, "Missing API token")
    if x_token != settings.API_TOKEN:
        raise HTTPException(403, "Invalid API token")
