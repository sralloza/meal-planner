"""Update notion meals cron sript."""

from datetime import datetime, timedelta

from .. import crud
from ..core.config import settings
from ..core.notion import create_notion_block, update_notion_text
from ..deps.database import manual_db
from ..schemas.meal import Meal
from .base import scheduler


def get_weekday(delta_days: int = 0) -> str:
    """Return the weekday in words given a delta in days."""
    date = datetime.now() + timedelta(days=delta_days)

    if settings.LOCALE_WEEKDAY_NAMES:
        return settings.LOCALE_WEEKDAY_NAMES[int(date.strftime("%w"))]

    return date.strftime("%A")


# Should fire everyday at 05:00
@scheduler.scheduled_job("cron", id="update-notion-meals", hour="5", minute="0")
def update_notion_meals():
    """Update meals in notion page."""
    if not settings.PRODUCTION:
        print("Skipping update-cron-meals (dev)")
        return

    with manual_db() as db:
        today_meal = crud.meal.get_today(db)
        tomorrow_meal = crud.meal.get_tomorrow(db)
        dat_meal = crud.meal.get_day_after_tomorrow(db)

    today_meal = Meal.from_orm(today_meal) if today_meal else None
    tomorrow_meal = Meal.from_orm(tomorrow_meal) if tomorrow_meal else None
    dat_meal = Meal.from_orm(dat_meal) if dat_meal else None

    blocks = []
    weekday = get_weekday(0)
    if today_meal:
        blocks.append(create_notion_block(f"Hoy ({weekday})\n", bold=True))
        blocks.extend(today_meal.to_notion_blocks())

    weekday = get_weekday(1)
    if tomorrow_meal:
        blocks.append(create_notion_block(f"\nMañana ({weekday})\n", bold=True))
        blocks.extend(tomorrow_meal.to_notion_blocks())

    if settings.NOTION_ADD_DAY_AFTER_TOMORROW:
        weekday = get_weekday(2)
        if dat_meal:
            blocks.append(
                create_notion_block(f"\nPasado mañana ({weekday})\n", bold=True)
            )
            blocks.extend(dat_meal.to_notion_blocks())

    if len(blocks) <= 3:
        print("warning: no blocks detected in cron-script update-notion-meals")
        return

    update_notion_text(blocks)
