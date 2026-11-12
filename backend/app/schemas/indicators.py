from __future__ import annotations

from pydantic import BaseModel

from .common import Location
from .weather import Quality, Source


class Indicators(BaseModel):
    """Indicateurs du cahier §7.3, calculés par le module ml. null = non calculable (jamais 0)."""

    rain_sum_mm: dict[str, float | None]
    rain_max_3d_mm: float | None = None
    wet_days: int | None = None
    max_dry_spell_days: int | None = None
    tmean_c: float | None = None
    tmin_min_c: float | None = None
    tmax_max_c: float | None = None
    frost_days: int | None = None
    diurnal_range_c: float | None = None
    et0_sum_mm: float | None = None
    water_balance_mm: float | None
    rh_mean_pct: float | None = None


class IndicatorsResponse(BaseModel):
    request_id: str
    location: Location
    window_days: int
    source: Source
    indicators: Indicators
    quality: Quality
