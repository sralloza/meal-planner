from datetime import datetime
from pathlib import Path
from typing import TypeVar

from toml import loads

from ..core.config import settings

T = TypeVar("T")


def get_version():
    data = loads(Path(__file__).parent.parent.with_name("pyproject.toml").read_text())
    return data["tool"]["poetry"]["version"]


def get_current_week():
    return datetime.now().isocalendar()[1]


def lowercase(obj: T) -> T:
    if isinstance(obj, str):
        return obj.lower()
    return obj


def lowercase_equals(str1, str2):
    return lowercase(str1) == lowercase(str2)


def is_variable(obj):
    return lowercase_equals(obj, settings.VARIABLE_STR)
