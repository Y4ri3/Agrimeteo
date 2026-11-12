"""Fournisseur Open-Meteo : archive météo (réanalyse ERA5) et géocodage. Gratuit, sans clé, licence CC BY 4.0.

Variables et paramètres validés par l'extraction du lot 1 (notebook devoir_dev). Une valeur absente
reste `null` : le contrôle qualité s'en charge, rien n'est remplacé par 0.
"""

from __future__ import annotations

from datetime import date

import httpx

from app.core import config
from app.core.errors import ProviderRateLimited, ProviderTimeout, ProviderUnavailable
from app.schemas.weather import DailyRecord, GeocodeResult, Source

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
# Variable Open-Meteo -> champ du schéma commun (ml/src/agrimeteo_ml/schema.py).
DAILY_VARIABLES = {
    "precipitation_sum": "precipitation_mm",
    "temperature_2m_min": "tmin_c",
    "temperature_2m_max": "tmax_c",
    "temperature_2m_mean": "tmean_c",
    "relative_humidity_2m_mean": "rh_mean_pct",
    "et0_fao_evapotranspiration": "et0_mm",
}


class OpenMeteoProvider:
    id = "open_meteo"
    source = Source(
        id="open_meteo",
        attribution="Weather data by Open-Meteo.com",
        license="CC BY 4.0",
        spatial_resolution_note="Réanalyse ERA5 : maille de plusieurs dizaines de km, pas la parcelle.",
    )

    def __init__(self, client: httpx.Client | None = None):
        self._client = client or httpx.Client(timeout=config.OPEN_METEO_TIMEOUT_SECONDS)

    def _get(self, url: str, params: dict) -> dict:
        try:
            response = self._client.get(url, params=params)
        except httpx.TimeoutException as exc:
            raise ProviderTimeout() from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailable() from exc
        if response.status_code == 429:
            raise ProviderRateLimited()
        if response.status_code >= 400:
            raise ProviderUnavailable()
        try:
            return response.json()
        except ValueError as exc:
            raise ProviderUnavailable() from exc

    def daily(self, latitude: float, longitude: float, start: date, end: date) -> list[DailyRecord]:
        data = self._get(
            ARCHIVE_URL,
            {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "daily": ",".join(DAILY_VARIABLES),
                "timezone": "auto",
            },
        )
        daily = data.get("daily")
        if not isinstance(daily, dict) or "time" not in daily:
            raise ProviderUnavailable()
        records = []
        for i, day in enumerate(daily["time"]):
            values = {
                field: (daily.get(var) or [None] * len(daily["time"]))[i]
                for var, field in DAILY_VARIABLES.items()
            }
            records.append(DailyRecord(date=day, **values))
        return records

    def geocode(self, q: str, limit: int, language: str) -> list[GeocodeResult]:
        data = self._get(GEOCODING_URL, {"name": q, "count": limit, "language": language, "format": "json"})
        return [
            GeocodeResult(
                name=r["name"],
                country=r.get("country", ""),
                admin1=r.get("admin1"),
                latitude=r["latitude"],
                longitude=r["longitude"],
            )
            for r in data.get("results") or []
        ]
