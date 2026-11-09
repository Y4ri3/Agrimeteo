"""Indicateurs calculés côté serveur : le frontend affiche, il ne calcule jamais (A-08, I-05).

PROVISOIRE : le module `ml` (lot 2) portera ces calculs ; la signature restera la même.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.providers.base import WeatherProvider
from app.schemas.indicators import Indicators
from app.schemas.weather import DailyRecord, Quality, Source
from app.services import quality as quality_service

FROST_THRESHOLD_C = 0.0  # seuil de gel générique ; celui du profil de culture est « à valider » (lot 2)


def _rain_sum(daily: list[DailyRecord], days: int) -> float | None:
    values = [r.precipitation_mm for r in daily[-days:] if r.precipitation_mm is not None]
    return round(sum(values), 1) if values else None


def compute(daily: list[DailyRecord], window_days: int) -> Indicators:
    rain_window = _rain_sum(daily, window_days)
    et0 = [r.et0_mm for r in daily]
    # Bilan pluie - ET0 : calculé seulement si ET0 est complète ; un trou n'est jamais compté pour 0.
    balance = None
    if rain_window is not None and all(v is not None for v in et0):
        balance = round(rain_window - sum(et0), 1)
    return Indicators(
        rain_sum_mm={"7d": _rain_sum(daily, 7), f"{window_days}d": rain_window},
        frost_days=sum(1 for r in daily if r.tmin_c is not None and r.tmin_c <= FROST_THRESHOLD_C),
        water_balance_mm=balance,
    )


def window(reference_date: date, window_days: int) -> tuple[date, date]:
    return reference_date - timedelta(days=window_days - 1), reference_date


def analyse(
    provider: WeatherProvider, latitude: float, longitude: float, start: date, end: date, window_days: int
) -> tuple[Indicators, Quality, Source]:
    raw = provider.daily(latitude, longitude, start, end)
    series, quality = quality_service.check(raw, start, end)
    return compute(series, window_days), quality, provider.source
