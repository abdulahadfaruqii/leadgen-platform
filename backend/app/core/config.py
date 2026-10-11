"""
Core configuration module using Pydantic Settings.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "LeadGen AI"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me"
    API_V1_PREFIX: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # Database - PostgreSQL / SQLite
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "leadgen"
    POSTGRES_PASSWORD: str = "leadgen"
    POSTGRES_DB: str = "leadgen"
    # Set to sqlite+aiosqlite for local runs without PostgreSQL
    DATABASE_URL_OVERRIDE: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Database - MongoDB
    MONGO_SERVER: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_USER: str = "leadgen"
    MONGO_PASS: str = "mongo"
    MONGO_DB: str = "leadgen_analytics"
    MONGO_URL_OVERRIDE: Optional[str] = None
    MONGO_ENABLED: bool = True

    @property
    def MONGO_URL(self) -> str:
        if self.MONGO_URL_OVERRIDE:
            return self.MONGO_URL_OVERRIDE
        if self.MONGO_USER and self.MONGO_PASS:
            return (
                f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}"
                f"@{self.MONGO_SERVER}:{self.MONGO_PORT}/{self.MONGO_DB}?authSource=admin"
            )
        return f"mongodb://{self.MONGO_SERVER}:{self.MONGO_PORT}/{self.MONGO_DB}"

    # Redis
    REDIS_SERVER: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION: str = "leadgen_memory"

    # AI
    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_AI_MODEL: str = "gpt-4o"
    FALLBACK_AI_PROVIDER: str = "anthropic"
    FALLBACK_AI_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    KIMI_API_KEY: Optional[str] = None

    # Scraping
    PLAYWRIGHT_HEADLESS: bool = True
    PROXY_ROTATION_ENABLED: bool = False
    PROXY_LIST: Optional[str] = None
    SCRAPING_DELAY_MS: int = 1500
    MAX_RETRIES: int = 3
    RATE_LIMIT_RPS: int = 2

    # Search APIs
    SERPAPI_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    BING_SEARCH_API_KEY: Optional[str] = None

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    MICROSOFT_CLIENT_ID: Optional[str] = None
    MICROSOFT_CLIENT_SECRET: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    @property
    def PROXIES(self) -> List[str]:
        if self.PROXY_LIST:
            return [p.strip() for p in self.PROXY_LIST.split(",") if p.strip()]
        return []


@lru_cache
def get_settings() -> Settings:
    return Settings()
