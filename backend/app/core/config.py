from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Information
    ORBIT_APP_NAME: str = "ORBIT Geospatial Intelligence"
    ORBIT_ENV: str = "development"
    ORBIT_DEBUG: bool = True
    ORBIT_API_V1_STR: str = "/api/v1"
    ORBIT_LOG_LEVEL: str = "INFO"

    # Server Configuration
    ORBIT_HOST: str = "127.0.0.1"
    ORBIT_PORT: int = 8000

    # CORS Origins (stored as JSON array or comma-separated list)
    ORBIT_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("ORBIT_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v

    # Database Configuration (PostgreSQL + PostGIS)
    POSTGRES_USER: str = "orbit_user"
    POSTGRES_PASSWORD: str = "orbit_password_local_dev"
    POSTGRES_DB: str = "orbit_db"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = (
        "postgresql+asyncpg://orbit_user:orbit_password_local_dev@127.0.0.1:5432/orbit_db"
    )
    DATABASE_URL_SYNC: str = (
        "postgresql://orbit_user:orbit_password_local_dev@127.0.0.1:5432/orbit_db"
    )

    # Redis Configuration
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://127.0.0.1:6379/0"

    # Storage Paths
    ORBIT_ARTIFACTS_DIR: str = "./artifacts"
    ORBIT_CACHE_DIR: str = "./.cache"
    ORBIT_DATA_DIR: str = "./data"

    # Security placeholders
    SECRET_KEY: str = "dev_secret_key_change_in_production_min32bytes"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Earth Observation & STAC Configuration
    STAC_EARTH_SEARCH_URL: str = "https://earth-search.aws.element84.com/v1"
    STAC_COPERNICUS_URL: str = "https://catalogue.dataspace.copernicus.eu/stac"
    STAC_PLANETARY_COMPUTER_URL: str = "https://planetarycomputer.microsoft.com/api/stac/v1"
    STAC_REQUEST_TIMEOUT_SECONDS: int = 15
    STAC_MAX_RETRIES: int = 3
    STAC_CACHE_TTL_SECONDS: int = 3600
    EO_SEARCH_DEFAULT_LIMIT: int = 20



settings = Settings()
