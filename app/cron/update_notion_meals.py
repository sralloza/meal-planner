from .. import crud
from ..core.notion import create_notion_block, update_notion_text
from ..deps.database import manual_db
from ..schemas.meal import Meal
from .base import scheduler


# Should fire everyday at 05:00
@scheduler.scheduled_job("cron", id="update-notion-meals", hour="5", minute="0")
def update_notion_meals():
    with manual_db() as db:
        today_meal = crud.meal.get_today(db)
        tomorrow_meal = crud.meal.get_tomorrow(db)

    today_meal = Meal.from_orm(today_meal) if today_meal else None
    tomorrow_meal = Meal.from_orm(tomorrow_meal) if tomorrow_meal else None

    blocks = []
    blocks.append(create_notion_block("Hoy\n", bold=True))
    if today_meal:
        blocks.extend(today_meal.to_notion_blocks())

    blocks.append(create_notion_block("\nMañana\n", bold=True))
    if tomorrow_meal:
        blocks.extend(tomorrow_meal.to_notion_blocks())

    if len(blocks) <= 2:
        print("warning: not blocks detected in cron-script update-notion-meals")
        return

    update_notion_text(blocks)
