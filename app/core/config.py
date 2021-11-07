"""Config module."""

from typing import Any, Dict, Optional

from pydantic import UUID4, BaseSettings, validator


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
    FORCE_LOCALE: str = ""

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            if v != "":
                return v
        return (
            f"mysql+pymysql://{values.get('MYSQL_USER')}:{values.get('MYSQL_PASSWORD')}@{values.get('MYSQL_HOST')}:"
            f"{values.get('MYSQL_PORT')}/{values.get('MYSQL_DATABASE')}"
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
