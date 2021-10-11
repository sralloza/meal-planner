from datetime import datetime
from pathlib import Path

from toml import loads


def get_version():
    data = loads(Path(__file__).parent.parent.with_name("pyproject.toml").read_text())
    return data["tool"]["poetry"]["version"]


def get_current_week():
    return datetime.now().isocalendar()[1]
