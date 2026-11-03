"""Configuration lue dans les variables d'environnement (voir .env.example)."""

import os


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


APP_ENV = os.environ.get("APP_ENV", "dev")
WEATHER_PROVIDER = os.environ.get("WEATHER_PROVIDER", "fixture")
MAX_PERIOD_DAYS = _int("MAX_PERIOD_DAYS", 366)
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
