"""Cron related API endpoints."""

from fastapi import APIRouter, BackgroundTasks, Depends

from ..core.cron import CRON_MAP, ValidCron
from ..deps.security import token_middleware
from ..utils.responses import gen_responses

router = APIRouter(
    tags=["Cron"],
    dependencies=[Depends(token_middleware)],
    **gen_responses({401: "Missing Token", 403: "Invalid token"}),
)


@router.post(
    "/{cron}",
    response_model_exclude_unset=True,
    response_model=ValidCron,
    status_code=201,
    summary="Launch Cron",
)
def get_meals(cron: ValidCron, background_tasks: BackgroundTasks):
    """Launches a cronjob in the background."""
    background_tasks.add_task(CRON_MAP[cron])
    return cron
