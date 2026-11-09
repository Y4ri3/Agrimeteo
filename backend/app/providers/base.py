"""Interface commune des fournisseurs de données (lot 1 : Open-Meteo, CSV ; ici : fixture)."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from app.schemas.weather import DailyRecord, GeocodeResult, Source


class WeatherProvider(Protocol):
    id: str
    source: Source

    def daily(self, latitude: float, longitude: float, start: date, end: date) -> list[DailyRecord]:
        """Série journalière brute. Lève ProviderUnavailable, ProviderRateLimited ou ProviderTimeout."""
        ...

    def geocode(self, q: str, limit: int, language: str) -> list[GeocodeResult]: ...
