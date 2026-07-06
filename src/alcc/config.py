from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Automatic Logistics Command Center"
    app_env: str = "development"
    debug: bool = True
    testing: bool = False
    secret_key: str = "dev-secret-key"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://alcc:alcc_secret@localhost:5432/alcc_db"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    jwt_secret_key: str = "dev-jwt-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    simulator_vehicle_count: int = 1000
    simulator_tick_interval_seconds: float = 1.0
    simulator_incident_rate: float = 0.001
    simulator_fuel_consumption_rate: float = 0.05

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8081",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
