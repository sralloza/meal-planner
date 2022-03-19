"""Cron core."""

from enum import Enum

from ..cron import (
    backup_database,
    check_frozen_meals,
    check_variable_meals,
    update_notion_meals,
)


class ValidCron(Enum):
    """Defined crons that can be launched from the API."""

    BACKUP_DATABASE = "backup-database"
    CHECK_FROZEN_MEALS = "check-frozen-meals"
    CHECK_VARIABLE_MEALS = "check-variable-meals"
    UPDATE_NOTION_MEALS = "update-notion-meals"


CRON_MAP = {
    ValidCron.BACKUP_DATABASE: backup_database,
    ValidCron.CHECK_FROZEN_MEALS: check_frozen_meals,
    ValidCron.CHECK_VARIABLE_MEALS: check_variable_meals,
    ValidCron.UPDATE_NOTION_MEALS: update_notion_meals,
}
