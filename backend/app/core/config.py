from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = "postgresql+asyncpg://optiflow:optiflow@localhost:5432/optiflow"
    database_url_sync: str = "postgresql+psycopg2://optiflow:optiflow@localhost:5432/optiflow"
    secret_key: str = "change-this-to-a-random-secret-key"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    redis_url: str = "redis://localhost:6379/0"
    docker_host: str = "unix:///var/run/docker.sock"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    project_name: str = "OptiFlow"
    project_root: Path = Path(__file__).parent.parent.parent
    access_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"


settings = Settings()
