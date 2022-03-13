from datetime import datetime
from pathlib import Path
from typing import TypeVar

from toml import loads

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
