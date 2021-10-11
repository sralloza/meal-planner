from todoist.api import TodoistAPI

from .config import settings


def add_task(msg: str, due: str = "today", priority: int = 1):
    api = TodoistAPI(settings.TODOIST_TOKEN)
    api.items.add(
        msg,
        project_id=settings.TODOIST_PROJECT_ID,
        due={"string": due},
        priority=priority,
    )
    api.commit()
