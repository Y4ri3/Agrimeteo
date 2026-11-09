"""Configuration lue dans les variables d'environnement (voir .env.example)."""

import os


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


APP_ENV = os.environ.get("APP_ENV", "dev")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
WEATHER_PROVIDER = os.environ.get("WEATHER_PROVIDER", "fixture")
MAX_PERIOD_DAYS = _int("MAX_PERIOD_DAYS", 366)
CACHE_TTL_HOURS = _int("CACHE_TTL_HOURS", 24)
CACHE_DIR = os.environ.get("CACHE_DIR", "/var/cache/agrimeteo")
# Sous ce taux de complétude (en %), une variable est jugée insuffisante : résultat « indéterminé » (D-04).
MIN_COMPLETENESS_PCT = _int("MIN_COMPLETENESS_PCT", 80)
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
