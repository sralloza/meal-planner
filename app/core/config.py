"""Config module."""

import json
from typing import Any, Dict, List, Optional

from pydantic import UUID4, BaseSettings, validator


def list_parse_fallback(v):
    try:
        return json.loads(v)
    except json.JSONDecodeError:
        return v.split(",")


class Settings(BaseSettings):
    # Server
    API_TOKEN: str
    ENABLE_PROMETHEUS: bool = False
    PRODUCTION: bool = False

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_BUCKET_NAME: str
    S3_FILE_NAME: str = "meals.json"

    # Notion
    NOTION_ADD_DAY_AFTER_TOMORROW: bool = True
    NOTION_BLOCK_ID: UUID4
    NOTION_KEY: str

    # Todoist
    TODOIST_PROJECT_ID: int
    TODOIST_TOKEN: str

    # Database
    MYSQL_DATABASE: str
    MYSQL_HOST: str
    MYSQL_PASSWORD: str
    MYSQL_PORT: str
    MYSQL_USER: str

    # Defined dinamically
    DATABASE_URI: str = ""

    # Other
    LOCALE_WEEKDAY_NAMES: Optional[List[str]]

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            if v != "":
                return v
        return (
            f"mysql+pymysql://{values.get('MYSQL_USER')}:{values.get('MYSQL_PASSWORD')}@{values.get('MYSQL_HOST')}:"
            f"{values.get('MYSQL_PORT')}/{values.get('MYSQL_DATABASE')}"
        )

    @validator("LOCALE_WEEKDAY_NAMES")
    def check_locale_names(cls, v):
        if isinstance(v, list):
            if len(v) != 7:
                raise ValueError("must have 7 elements (one for each week day)")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"
        json_loads = list_parse_fallback


settings = Settings()
