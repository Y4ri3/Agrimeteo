"""Indicateurs d'une fenêtre : le calcul est dans le module ml ; ici, collecte et contrôle qualité."""

from __future__ import annotations

from datetime import date, timedelta

from agrimeteo_ml import compute

from app.providers.base import WeatherProvider
from app.schemas.indicators import Indicators
from app.schemas.weather import DailyRecord, Quality, Source
from app.services import quality as quality_service


def window(reference_date: date, window_days: int) -> tuple[date, date]:
    return reference_date - timedelta(days=window_days - 1), reference_date


def analyse(
    provider: WeatherProvider, latitude: float, longitude: float, start: date, end: date, window_days: int
) -> tuple[Indicators, Quality, Source, list[DailyRecord]]:
    raw = provider.daily(latitude, longitude, start, end)
    series, quality = quality_service.check(raw, start, end)
    return Indicators(**compute(series, window_days)), quality, provider.source, series
