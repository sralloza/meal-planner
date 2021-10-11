from typing import Any, Dict, Optional

from pydantic import UUID4, BaseSettings, validator


class Settings(BaseSettings):
    ENABLE_PROMETHEUS: bool = False

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    API_TOKEN: str
    NOTION_KEY: str
    NOTION_BLOCK_ID: UUID4

    TODOIST_TOKEN: str
    TODOIST_PROJECT_ID: int

    S3_BUCKET_NAME: str
    S3_FILE_NAME: str = "meals.json"

    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: str
    MYSQL_DATABASE: str
    DATABASE_URI: str = ""

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
