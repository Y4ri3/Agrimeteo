"""Routes de l'API v1 : validation des entrées, fournisseur, qualité, indicateurs, moteur."""

from __future__ import annotations

import logging
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Request

from app import providers
from app.core.errors import AppError
from app.schemas.common import ErrorResponse, Location
from app.schemas.indicators import IndicatorsResponse
from app.schemas.predictions import (
    AgronomicCultivability,
    AnalysisWindow,
    CropsResponse,
    PredictionRequest,
    PredictionResponse,
    SoilMoisture,
)
from app.schemas.weather import GeocodeResponse, Period, WeatherResponse
from app.services import crops, engine, quality, validation
from app.services import indicators as indicator_service

log = logging.getLogger("agrimeteo.api")
router = APIRouter(prefix="/api/v1")
ERRORS = {
    # Libellé explicite : celui par défaut vient de http.HTTPStatus et change selon la version de Python.
    422: {"model": ErrorResponse, "description": "Données invalides"},
    502: {"model": ErrorResponse},
    503: {"model": ErrorResponse},
    504: {"model": ErrorResponse},
}

Lat = Annotated[float, Query(ge=-90, le=90)]
Lon = Annotated[float, Query(ge=-180, le=180)]


def rid(request: Request) -> str:
    return request.state.request_id


def _log(request: Request, what: str, lat: float, lon: float) -> None:
    # Les coordonnées sont arrondies dans les journaux (cahier, 9.9).
    log.info("%s lat=%.1f lon=%.1f request_id=%s", what, lat, lon, rid(request))


@router.get("/geocode", response_model=GeocodeResponse, responses=ERRORS, tags=["geocode"])
def geocode(
    q: Annotated[str, Query(min_length=2, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=10)] = 5,
    language: str = "fr",
    source: str | None = None,
):
    return GeocodeResponse(results=providers.resolve(source).geocode(q, limit, language))


@router.get("/weather", response_model=WeatherResponse, responses=ERRORS, tags=["weather"])
def weather(
    request: Request,
    latitude: Lat,
    longitude: Lon,
    start_date: date,
    end_date: date,
    source: str | None = None,
):
    validation.check_period(start_date, end_date)
    provider = providers.resolve(source)
    _log(request, "weather", latitude, longitude)
    series, report = quality.check(
        provider.daily(latitude, longitude, start_date, end_date), start_date, end_date
    )
    return WeatherResponse(
        request_id=rid(request),
        location=Location(latitude=latitude, longitude=longitude),
        source=provider.source,
        period=Period(start_date=start_date, end_date=end_date),
        units={"precipitation": "mm", "temperature": "°C", "relative_humidity": "%", "et0": "mm"},
        daily=series,
        quality=report,
    )


@router.get("/indicators", response_model=IndicatorsResponse, responses=ERRORS, tags=["indicators"])
def indicators(
    request: Request,
    latitude: Lat,
    longitude: Lon,
    reference_date: date | None = None,
    window_days: Annotated[int, Query(ge=7, le=90)] = 30,
    source: str | None = None,
):
    ref = reference_date or validation.default_reference_date()
    start, end = indicator_service.window(ref, window_days)
    validation.check_period(start, end)
    provider = providers.resolve(source)
    _log(request, "indicators", latitude, longitude)
    ind, report, src = indicator_service.analyse(provider, latitude, longitude, start, end, window_days)
    return IndicatorsResponse(
        request_id=rid(request),
        location=Location(latitude=latitude, longitude=longitude),
        window_days=window_days,
        source=src,
        indicators=ind,
        quality=report,
    )


@router.get("/crops", response_model=CropsResponse, responses={500: {"model": ErrorResponse}}, tags=["crops"])
def list_crops():
    return CropsResponse(crops=crops.all_crops())


@router.post(
    "/predictions",
    response_model=PredictionResponse,
    responses={404: {"model": ErrorResponse}, **ERRORS},
    tags=["predictions"],
)
def predictions(request: Request, body: PredictionRequest):
    crop = crops.find(body.crop_id)
    if crop is None:
        raise AppError(404, "CROP_NOT_FOUND", "Cette culture n'existe pas.", [{"field": "crop_id"}])
    ref = body.reference_date or validation.default_reference_date()
    start, end = indicator_service.window(ref, body.window_days)
    validation.check_period(start, end)
    provider = providers.resolve(body.source)
    lat, lon = body.location.latitude, body.location.longitude
    _log(request, "predictions", lat, lon)
    ind, report, src = indicator_service.analyse(provider, lat, lon, start, end, body.window_days)
    favorability, confidence, limits = engine.evaluate_crop(crop.id, ind, report, src)
    return PredictionResponse(
        request_id=rid(request),
        analysis_window=AnalysisWindow(start_date=start, end_date=end, days=body.window_days),
        crop=crop,
        meteorological_favorability=favorability,
        soil_moisture=SoilMoisture(
            available=False, note="Estimation de modèle, non mesurée sur la parcelle (non branchée)."
        ),
        agronomic_cultivability=AgronomicCultivability(
            reason="Aucune donnée de sol fiable ni observation de parcelle."
        ),
        indicators=ind,
        data_quality=report,
        source=src,
        confidence=confidence,
        limits=limits,
        attribution=src.attribution,
    )
