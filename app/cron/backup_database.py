"""Backup database cron script."""

from typing import List

from pydantic import parse_obj_as

from .. import crud
from ..core.aws import save_meals
from ..deps.database import manual_db
from ..schemas.meal import Meal
from .base import scheduler


# Should fire everyday at 02:08
@scheduler.scheduled_job("cron", id="backup-database", hour="2", minute="08")
def backup_database():
    """Backup database to AWS."""
    with manual_db() as db:
        meals = crud.meal.get_multi(db, limit=1000)

    meals = parse_obj_as(List[Meal], meals)
    save_meals(meals)
