"""Update notion meals cron sript."""

from .. import crud
from ..core.config import settings
from ..core.cron import get_weekday
from ..core.notion import create_notion_block, update_notion_text
from ..deps.database import manual_db
from ..schemas.meal import Meal
from .base import scheduler


# Should fire everyday at 05:00
@scheduler.scheduled_job("cron", id="update-notion-meals", hour="5", minute="0")
def update_notion_meals():
    """Update meals in notion page."""
    with manual_db() as db:
        today_meal = crud.meal.get_today(db)
        tomorrow_meal = crud.meal.get_tomorrow(db)
        dat_meal = crud.meal.get_day_after_tomorrow(db)

    today_meal = Meal.from_orm(today_meal) if today_meal else None
    tomorrow_meal = Meal.from_orm(tomorrow_meal) if tomorrow_meal else None
    dat_meal = Meal.from_orm(dat_meal) if dat_meal else None

    blocks = []
    weekday = get_weekday(0)
    blocks.append(create_notion_block(f"Hoy ({weekday})\n", bold=True))
    if today_meal:
        blocks.extend(today_meal.to_notion_blocks())

    weekday = get_weekday(1)
    blocks.append(create_notion_block(f"\nMañana ({weekday})\n", bold=True))
    if tomorrow_meal:
        blocks.extend(tomorrow_meal.to_notion_blocks())

    if settings.NOTION_ADD_DAY_AFTER_TOMORROW:
        weekday = get_weekday(2)
        blocks.append(create_notion_block(f"\nPasado mañana ({weekday})\n", bold=True))
        if dat_meal:
            blocks.extend(dat_meal.to_notion_blocks())

    if len(blocks) <= 3:
        print("warning: not blocks detected in cron-script update-notion-meals")
        return

    update_notion_text(blocks)
