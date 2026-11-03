from __future__ import annotations

from pydantic import BaseModel

from .common import Location
from .weather import Quality, Source


class Indicators(BaseModel):
    rain_sum_mm: dict[str, float | None]
    frost_days: int
    water_balance_mm: float | None


class IndicatorsResponse(BaseModel):
    request_id: str
    location: Location
    window_days: int
    source: Source
    indicators: Indicators
    quality: Quality
