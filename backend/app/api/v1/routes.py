"""Routes de l'API v1. SQUELETTE : les réponses viennent de app/services/stub.py (lot 3 à brancher)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.core import config
from app.core.errors import AppError
from app.schemas.common import ErrorResponse, Location
from app.schemas.indicators import IndicatorsResponse
from app.schemas.predictions import (
    AgronomicCultivability,
    AnalysisWindow,
    Confidence,
    CriterionResult,
    CropsResponse,
    MeteoFavorability,
    PredictionRequest,
    PredictionResponse,
    SoilMoisture,
)
from app.schemas.weather import GeocodeResponse, Period, WeatherResponse
from app.services import stub

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


@router.get("/geocode", response_model=GeocodeResponse, responses=ERRORS, tags=["geocode"])
def geocode(
    q: Annotated[str, Query(min_length=2, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=10)] = 5,
    language: str = "fr",
):
    return GeocodeResponse(results=stub.search_places(q, limit))


@router.get("/weather", response_model=WeatherResponse, responses=ERRORS, tags=["weather"])
def weather(
    request: Request,
    latitude: Lat,
    longitude: Lon,
    start_date: date,
    end_date: date,
    source: str | None = None,
):
    if start_date > end_date:
        raise AppError(
            422,
            "VALIDATION_ERROR",
            "La date de début doit précéder la date de fin.",
            [{"field": "start_date"}],
        )
    if (end_date - start_date).days + 1 > config.MAX_PERIOD_DAYS:
        raise AppError(
            422,
            "PERIOD_TOO_LONG",
            "La période demandée dépasse la durée maximale autorisée.",
            [{"field": "end_date", "max_period_days": config.MAX_PERIOD_DAYS}],
        )
    daily = stub.daily_series(start_date, end_date)
    return WeatherResponse(
        request_id=rid(request),
        location=Location(latitude=latitude, longitude=longitude),
        source=stub.STUB_SOURCE,
        period=Period(start_date=start_date, end_date=end_date),
        units={"precipitation": "mm", "temperature": "°C", "relative_humidity": "%", "et0": "mm"},
        daily=daily,
        quality=stub.quality_of(daily),
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
    ref = reference_date or stub.default_reference_date()
    ind, quality = stub.compute_indicators(ref, window_days)
    return IndicatorsResponse(
        request_id=rid(request),
        location=Location(latitude=latitude, longitude=longitude),
        window_days=window_days,
        source=stub.STUB_SOURCE,
        indicators=ind,
        quality=quality,
    )


@router.get("/crops", response_model=CropsResponse, responses={500: {"model": ErrorResponse}}, tags=["crops"])
def crops():
    return CropsResponse(crops=stub.CROPS)


@router.post(
    "/predictions",
    response_model=PredictionResponse,
    responses={404: {"model": ErrorResponse}, **ERRORS},
    tags=["predictions"],
)
def predictions(request: Request, body: PredictionRequest):
    crop = next((c for c in stub.CROPS if c.id == body.crop_id), None)
    if crop is None:
        raise AppError(404, "CROP_NOT_FOUND", "Ce profil de culture n'existe pas.", [{"field": "crop_id"}])
    ref = body.reference_date or stub.default_reference_date()
    ind, quality = stub.compute_indicators(ref, body.window_days)
    return PredictionResponse(
        request_id=rid(request),
        analysis_window=AnalysisWindow(
            start_date=ref - timedelta(days=body.window_days - 1), end_date=ref, days=body.window_days
        ),
        crop=crop,
        meteorological_favorability=MeteoFavorability(
            level="indetermine",
            summary="Moteur de règles non branché : réponse factice du squelette.",
            criteria=[
                CriterionResult(
                    id="gel", status="non_evaluable", explanation="Moteur non branché (squelette)."
                )
            ],
        ),
        soil_moisture=SoilMoisture(
            available=False, note="Estimation de modèle non disponible dans le squelette."
        ),
        agronomic_cultivability=AgronomicCultivability(
            reason="Aucune donnée de sol fiable ni observation de parcelle."
        ),
        indicators=ind,
        data_quality=quality,
        source=stub.STUB_SOURCE,
        confidence=Confidence(
            level="faible", basis="Squelette : aucune donnée réelle. Ce n'est pas une probabilité."
        ),
        limits=["Réponse factice du squelette.", "Seuils du profil à valider."],
        attribution=stub.STUB_SOURCE.attribution,
    )
