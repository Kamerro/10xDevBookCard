from __future__ import annotations

import os


class Settings:
    def __init__(self) -> None:
        db_url = os.environ.get(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/bookcards",
        )
        # Fly.io uses postgres:// but SQLAlchemy 2.0 + psycopg3 needs postgresql+psycopg://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        self.database_url = db_url

        self.jwt_secret_key = os.environ.get("SECRET_KEY", "change-me")
        self.jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
        jwt_exp_raw = os.environ.get("JWT_ACCESS_TOKEN_EXP_MINUTES", "60")
        try:
            self.jwt_access_token_exp_minutes = int(jwt_exp_raw)
        except ValueError:
            self.jwt_access_token_exp_minutes = 60

        self.openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.openrouter_model = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.openrouter_base_url = os.environ.get(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        )

        openrouter_timeout_raw = os.environ.get("OPENROUTER_TIMEOUT_SECONDS", "30")
        try:
            self.openrouter_timeout_seconds = float(openrouter_timeout_raw)
        except ValueError:
            self.openrouter_timeout_seconds = 30.0


settings = Settings()
