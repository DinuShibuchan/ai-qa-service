import json
from typing import Any, List, Union
from pydantic import BeforeValidator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

def parse_cors_origins(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, str):
        if v.startswith("[") and v.endswith("]"):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                pass
        return [item.strip() for item in v.split(",") if item.strip()]
    return v

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore"
    )
    
    API_V1_STR: str = "/api/v1"
    APP_NAME: str = "AI QA Service"
    APP_ENV: str = "development"
    
    # Database configuration (should be standard Postgres connection URL, e.g. postgresql+asyncpg://...)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_qa_db"
    
    # CORS Origins
    CORS_ORIGINS: Annotated[List[str], BeforeValidator(parse_cors_origins)] = []
    
    PROJECT_SECRET_KEY: str = "super-secret-key-for-development"

    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"


settings = Settings()
