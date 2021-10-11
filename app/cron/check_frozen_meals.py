from .. import crud
from ..core.todoist import add_task
from ..deps.database import manual_db
from ..schemas.meal import Meal
from .base import scheduler


# Should fire everyday at 16:00
@scheduler.scheduled_job("cron", id="check-frozen-meals", hour="16", minute="0")
def check_frozen_meals():
    with manual_db() as db:
        meal_db = crud.meal.get_tomorrow(db)

    if not meal_db:
        return

    meal = Meal.from_orm(meal_db)

    if not meal.frozen:
        return

    text = f"Descongelar: {', '.join(meal.frozen)}"
    add_task(text, due="today 20:30", priority=4)
