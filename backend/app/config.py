"""
Centralized app configuration.

Everything here is read from environment variables (or a local .env file
during development). Never hardcode secrets -- that's the whole point of
this file existing.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Open Source Issue Recommender"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://osir_user:osir_pass@localhost:5432/osir_db"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- GitHub OAuth ---
    GITHUB_CLIENT_ID: str = "REPLACE_ME"
    GITHUB_CLIENT_SECRET: str = "REPLACE_ME"
    GITHUB_CALLBACK_URL: str = "http://localhost:8000/auth/github/callback"

    # --- JWT (our own session tokens, issued after GitHub login) ---
    JWT_SECRET: str = "change-this-to-a-random-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- GitHub API ---
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
