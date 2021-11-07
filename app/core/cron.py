"""Cron core."""

import locale
from datetime import datetime, timedelta
from enum import Enum

from ..cron import backup_database, check_frozen_meals, update_notion_meals
from .config import settings


class ValidCron(Enum):
    """Defined crons that can be launched from the API."""

    BACKUP_DATABASE = "backup-database"
    CHECK_FROZEN_MEALS = "check-frozen-meals"
    UPDATE_NOTION_MEALS = "update-notion-meals"


CRON_MAP = {
    ValidCron.BACKUP_DATABASE: backup_database,
    ValidCron.CHECK_FROZEN_MEALS: check_frozen_meals,
    ValidCron.UPDATE_NOTION_MEALS: update_notion_meals,
}


def get_weekday(delta_days: int = 0) -> str:
    """Return the weekday in words given a delta in days."""
    if settings.FORCE_LOCALE:
        locale.setlocale(locale.LC_TIME, settings.FORCE_LOCALE)

    date = datetime.now() + timedelta(days=delta_days)
    return date.strftime("%A")
