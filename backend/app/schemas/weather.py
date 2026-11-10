from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from .common import Location


class Source(BaseModel):
    id: str
    attribution: str | None = None
    license: str | None = None
    retrieved_at: datetime | None = None
    spatial_resolution_note: str | None = None


class Period(BaseModel):
    start_date: date
    end_date: date


class DailyRecord(BaseModel):
    date: date
    precipitation_mm: float | None = None
    tmax_c: float | None = None
    tmin_c: float | None = None
    rh_mean_pct: float | None = None
    et0_mm: float | None = None


class FlaggedValue(BaseModel):
    date: date
    variable: str
    reason: str


class Quality(BaseModel):
    completeness_pct: dict[str, float]
    missing_days: int
    flagged_values: list[FlaggedValue] = []


class WeatherResponse(BaseModel):
    request_id: str
    location: Location
    source: Source
    period: Period
    units: dict[str, str]
    daily: list[DailyRecord]
    quality: Quality


class GeocodeResult(BaseModel):
    name: str
    country: str
    admin1: str | None = None
    latitude: float
    longitude: float


class GeocodeResponse(BaseModel):
    results: list[GeocodeResult]
