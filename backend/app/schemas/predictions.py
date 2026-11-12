from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from .common import Location
from .indicators import Indicators
from .weather import Quality, Source

Level = Literal["favorable", "favorable_sous_reserve", "peu_favorable", "indetermine"]
CriterionStatus = Literal["ok", "vigilance", "defavorable", "non_evaluable"]


class LocationIn(Location):
    label: str | None = None


class PredictionRequest(BaseModel):
    location: LocationIn
    crop_id: str
    reference_date: date | None = None
    window_days: int = Field(default=30, ge=7, le=90)
    source: str | None = None


class AnalysisWindow(BaseModel):
    start_date: date
    end_date: date
    days: int


class Crop(BaseModel):
    id: str
    label: str
    rule_profile_version: str
    rule_status: Literal["a_valider", "valide_par_source"]


class CropsResponse(BaseModel):
    crops: list[Crop]


class CriterionResult(BaseModel):
    """Un critère du profil : son verdict, sa phrase explicative et de quoi dessiner une jauge."""

    id: str
    label: str | None = None
    status: CriterionStatus
    explanation: str
    blocking: bool = False
    direction: Literal["lower_is_worse", "higher_is_worse"] | None = None
    unit: str | None = None
    window_days: int | None = None
    value: float | None = None
    vigilance: float | None = None
    unfavorable: float | None = None


class MeteoFavorability(BaseModel):
    level: Level
    summary: str
    criteria: list[CriterionResult]


class SoilMoisture(BaseModel):
    kind: Literal["modelled_indicator"] = "modelled_indicator"
    available: bool
    note: str


class AgronomicCultivability(BaseModel):
    status: Literal["non_evaluee"] = "non_evaluee"
    reason: str


class Confidence(BaseModel):
    level: Literal["faible", "moyenne", "elevee"]
    basis: str


class PredictionResponse(BaseModel):
    request_id: str
    analysis_window: AnalysisWindow
    crop: Crop
    meteorological_favorability: MeteoFavorability
    soil_moisture: SoilMoisture
    agronomic_cultivability: AgronomicCultivability
    indicators: Indicators
    data_quality: Quality
    source: Source
    confidence: Confidence
    limits: list[str]
    attribution: str | None = None
