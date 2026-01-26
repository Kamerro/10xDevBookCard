from __future__ import annotations

import os


class Settings:
    def __init__(self) -> None:
        self.database_url = os.environ.get(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/bookcards",
        )

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
