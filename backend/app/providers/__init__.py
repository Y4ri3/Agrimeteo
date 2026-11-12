"""Fournisseurs de données météo, choisis par WEATHER_PROVIDER ou par le paramètre `source`.

`fixture` (hors ligne, factice), `open_meteo` (réel) et `csv` (extraction réelle, hors ligne).
"""

from __future__ import annotations

from app.core import config
from app.core.errors import AppError
from app.providers.base import WeatherProvider
from app.providers.cache import CachedProvider
from app.providers.csv_file import CsvProvider
from app.providers.fixture import FixtureProvider
from app.providers.open_meteo import OpenMeteoProvider

REGISTRY: dict[str, WeatherProvider] = {
    "fixture": FixtureProvider(),
    "open_meteo": OpenMeteoProvider(),
    "csv": CsvProvider(),
}


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
