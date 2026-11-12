"""Adaptateur vers le moteur de règles du module ml : traduit son résultat en schémas de l'API."""

from __future__ import annotations

from agrimeteo_ml import evaluate

from app.core import config
from app.schemas.predictions import Confidence, CriterionResult, MeteoFavorability
from app.schemas.weather import DailyRecord, Quality, Source
from app.services import crops


def evaluate_crop(
    crop_id: str, series: list[DailyRecord], quality: Quality, source: Source
) -> tuple[MeteoFavorability, Confidence, list[str]]:
    result = evaluate(
        crops.profile(crop_id),
        series,
        quality.completeness_pct,
        min_completeness=config.MIN_COMPLETENESS_PCT,
        fine_resolution=False,  # les jeux de données utilisés ont une maille de plusieurs dizaines de km
    )
    limits = list(result.limits)
    if source.id == "fixture":
        limits.insert(0, "Données factices de démonstration : aucune valeur réelle.")
    return (
        MeteoFavorability(
            level=result.level,
            summary=result.summary,
            criteria=[
                CriterionResult(
                    id=c.id,
                    label=c.label,
                    status=c.status,
                    explanation=c.explanation,
                    blocking=c.blocking,
                    direction=c.direction,
                    unit=c.unit,
                    window_days=c.window_days,
                    value=c.value,
                    vigilance=c.vigilance,
                    unfavorable=c.unfavorable,
                )
                for c in result.criteria
            ],
        ),
        Confidence(level=result.confidence_level, basis=result.confidence_basis),
        limits,
    )
