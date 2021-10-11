"""Useful functions for the server."""

from logging import getLogger
from uuid import uuid4

from fastapi import Request
from starlette.responses import JSONResponse

logger = getLogger(__name__)


def catch_errors(request: Request, exc: Exception):
    """Logs an error and returns 500 to the user."""
    error_id = uuid4()
    scope = request.scope
    request_info = (
        f"[{request.client.host}] {scope['scheme'].upper()}/{scope['http_version']} "
        f"{scope['method']} {scope['path']}"
    )

    exc_info = (exc.__class__, exc, exc.__traceback__)
    logger.critical(
        "Unhandled exception [id=%s] in request '%s':",
        error_id,
        request_info,
        exc_info=exc_info,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error, please contact the server administrator.",
            "errorId": str(error_id),
        },
        headers={"X-Error-ID": str(error_id)},
    )
