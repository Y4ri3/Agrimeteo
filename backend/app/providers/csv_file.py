"""Fournisseur CSV : démonstration et tests hors ligne avec de vraies données (extraction du lot 1).

Le fichier (CSV_PATH) suit le format du notebook : une ligne par jour et par localité. La localité la
plus proche (moins de 100 km) répond ; au-delà, aucune donnée : le résultat est « indéterminé ».
"""

from __future__ import annotations

import csv
import math
import unicodedata
from datetime import date
from functools import cached_property
from pathlib import Path

from app.core import config
from app.core.errors import ProviderUnavailable
from app.schemas.weather import DailyRecord, GeocodeResult, Source

MAX_DISTANCE_KM = 100
FIELDS = ["precipitation_mm", "tmin_c", "tmax_c", "tmean_c", "rh_mean_pct", "et0_mm"]


def _norm(text: str) -> str:
    return (
        "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
        .lower()
        .strip()
    )


def _km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (
        math.sin((p2 - p1) / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    )
    return 6371 * 2 * math.asin(math.sqrt(a))


def _num(value: str) -> float | None:
    return float(value) if value.strip() else None


class CsvProvider:
    id = "csv"
    source = Source(
        id="csv",
        attribution="Weather data by Open-Meteo.com",
        license="CC BY 4.0",
        spatial_resolution_note="Extraction Open-Meteo (ERA5) : maille de dizaines de km.",
    )

    def __init__(self, path: str | None = None):
        self._path = path

    @cached_property
    def _places(self) -> dict[str, dict]:
        path = Path(self._path or config.CSV_PATH)
        if not path.is_file():
            raise ProviderUnavailable()
        places: dict[str, dict] = {}
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                place = places.setdefault(
                    row["localite"],
                    {
                        "region": row["region"],
                        "lat": float(row["latitude"]),
                        "lon": float(row["longitude"]),
                        "days": {},
                    },
                )
                place["days"][date.fromisoformat(row["date"])] = DailyRecord(
                    date=row["date"], **{k: _num(row.get(k) or "") for k in FIELDS}
                )
        return places

    def daily(self, latitude: float, longitude: float, start: date, end: date) -> list[DailyRecord]:
        near = min(
            self._places.values(), key=lambda p: _km(latitude, longitude, p["lat"], p["lon"]), default=None
        )
        if near is None or _km(latitude, longitude, near["lat"], near["lon"]) > MAX_DISTANCE_KM:
            return []
        return [rec for day, rec in sorted(near["days"].items()) if start <= day <= end]

    def geocode(self, q: str, limit: int, language: str) -> list[GeocodeResult]:
        needle = _norm(q)
        found = [
            GeocodeResult(
                name=name, country="Sénégal", admin1=p["region"], latitude=p["lat"], longitude=p["lon"]
            )
            for name, p in self._places.items()
            if needle in _norm(name)
        ]
        return found[:limit]
