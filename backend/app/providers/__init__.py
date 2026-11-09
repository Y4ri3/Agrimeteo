"""Fournisseurs de données météo, choisis par WEATHER_PROVIDER ou par le paramètre `source`.

Le lot 1 enregistre ici `open_meteo` et `csv` ; seule la fixture existe pour l'instant.
"""

from __future__ import annotations

from app.core import config
from app.core.errors import AppError
from app.providers.base import WeatherProvider
from app.providers.cache import CachedProvider
from app.providers.fixture import FixtureProvider

REGISTRY: dict[str, WeatherProvider] = {"fixture": FixtureProvider()}


def resolve(source: str | None) -> WeatherProvider:
    name = source or config.WEATHER_PROVIDER
    provider = REGISTRY.get(name)
    if provider is None:
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "Source de données inconnue.",
            [{"field": "source", "available": sorted(REGISTRY)}],
        )
    return CachedProvider(provider)
