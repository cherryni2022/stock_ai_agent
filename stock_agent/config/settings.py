"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置 — 所有值通过环境变量注入."""

    # ---- LLM Provider ----
    LLM_PROVIDER: str = "openai"  # openai | gemini | zhipu
    LLM_BASE_URL: str | None = None
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4096

    # ---- Embedding Provider ----
    EMBEDDING_PROVIDER: str = "openai"  # openai | gemini | zhipu
    EMBEDDING_BASE_URL: str | None = None
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # ---- Supabase / PostgreSQL ----
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_DB_URL: str = ""  # postgresql+asyncpg://...

    # ---- Application ----
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    MAX_RETRIES: int = 3
    TOOL_TIMEOUT_SECONDS: int = 30
    MAX_SUB_TASKS: int = 10
    RAG_TOP_K: int = 10
    SQL_MAX_ROWS: int = 500

    # ---- MVP Stock Universe ----
    MVP_STOCK_UNIVERSE: dict[str, list[str]] = {
        "US": ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META", "TSLA"],
        "HK": ["9988.HK", "0700.HK", "1024.HK"],
        "CN": ["601127", "688981"],
    }

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
