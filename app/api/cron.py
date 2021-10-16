from enum import Enum

from fastapi import APIRouter, BackgroundTasks, Depends

from ..cron import backup_database, check_frozen_meals, update_notion_meals
from ..deps.security import token_middleware
from ..utils.responses import gen_responses

router = APIRouter(
    tags=["Cron"],
    dependencies=[Depends(token_middleware)],
    **gen_responses({401: "Missing Token", 403: "Invalid token"}),
)


class ValidCron(Enum):
    backup_database = "backup-database"
    check_frozen_meals = "check-frozen-meals"
    update_notion_meals = "update-notion-meals"


CRON_MAP = {
    ValidCron.backup_database: backup_database,
    ValidCron.check_frozen_meals: check_frozen_meals,
    ValidCron.update_notion_meals: update_notion_meals,
}


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
