"""Check frozen meals cron script."""

from .. import crud, models
from ..core.todoist import add_task
from ..deps.database import manual_db
from ..schemas.meal import Meal
from .base import scheduler


# Should fire everyday at 16:00
@scheduler.scheduled_job("cron", id="check-variable-meals", hour="16", minute="0")
def check_variable_meals():
    """Checks if tomorrow or the day after tomorrow a variable meal is on the menu."""
    with manual_db() as db:
        tomorrow_meal_db = crud.meal.get_tomorrow(db)
        dat_meal_db = crud.meal.get_by_date_delta(db, delta_days=2)

    if tomorrow_meal_db:
        add_task_if_variable(db, tomorrow_meal_db, True)
    if dat_meal_db:
        add_task_if_variable(db, dat_meal_db, False)


def add_task_if_variable(db, meal_db: models.Meal, urgent: bool):
    """Adds a task to define variable meal fields if meal_db has variable meal fields.

    If urgent is True, the added task will be due today 18:00 (frozen check run as 19:00).
    Otherwise the added task will be due today at 21:00.

    Args:
        db (Session): database session.
        meal_db (models.Meal): meal from database.
        urgent (bool): True if it's tomorrow meal, False otherwise.
    """
    meal = Meal.from_orm(meal_db)

    if variable := meal.variable:
        text = "Define variable meal"
        if len(variable) > 1:
            text += "s"
        text += f"[{meal.id}]: {', '.join(variable)}"

        if urgent:
            add_task(text, due="today 18:00", priority=4)
        else:
            add_task(text, due="today 21:00", priority=4)
