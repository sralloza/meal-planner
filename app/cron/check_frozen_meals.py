"""Check frozen meals cron script."""

from .. import crud
from ..core.todoist import add_task
from ..deps.database import manual_db
from ..schemas.meal import Meal
from .base import scheduler


# Should fire everyday at 19:00
@scheduler.scheduled_job("cron", id="check-frozen-meals", hour="19", minute="0")
def check_frozen_meals():
    """Checks if tomorrow something frozen is on the menu."""
    with manual_db() as db:
        meal_db = crud.meal.get_tomorrow(db)

    if not meal_db:
        return

    meal = Meal.from_orm(meal_db)

    if not meal.frozen:
        return

    text = f"Descongelar: {', '.join(meal.frozen)}"
    add_task(text, due="today 21:30", priority=4)
