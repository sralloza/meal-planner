from .. import crud
from ..core.notion import update_notion_text
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
    if today_meal:
        blocks.append(
            {
                "type": "text",
                "text": {"content": "Hoy\n"},
                "annotations": {"bold": True},
            }
        )
        blocks.append(
            {"type": "text", "text": {"content": today_meal.describe(indent=2)}}
        )
    if tomorrow_meal:
        title = "\n" * bool(blocks) + "Mañana"
        blocks.append(
            {
                "type": "text",
                "text": {"content": f"{title}\n"},
                "annotations": {"bold": True},
            }
        )
        blocks.append(
            {"type": "text", "text": {"content": tomorrow_meal.describe(indent=2)}}
        )

    update_notion_text(blocks)
